"""
emotions-mcp: Queryable user expressive state for LLMs.

An MCP server that continuously captures microphone audio, extracts
prosodic features (pitch, energy, speech rate), and exposes a
query_user_state() tool that returns natural language descriptions
of the user's communicative state.
"""

import threading
import time
import collections

import numpy as np
import sounddevice as sd
import parselmouth
from parselmouth.praat import call
from mcp.server.fastmcp import FastMCP

# --- Audio capture config ---
SAMPLE_RATE = 16000  # 16kHz mono, good enough for prosody
CHANNELS = 1
BUFFER_SECONDS = 30  # rolling buffer of last 30 seconds
CHUNK_SECONDS = 0.5  # capture in 500ms chunks

# --- Rolling audio buffer ---
# Thread-safe deque of numpy arrays. Each element is one chunk.
_audio_chunks = collections.deque(
    maxlen=int(BUFFER_SECONDS / CHUNK_SECONDS)
)
_capture_active = False
_capture_thread = None


def _audio_callback(indata, frames, time_info, status):
    """Called by sounddevice for each audio chunk."""
    _audio_chunks.append(indata[:, 0].copy())


def start_capture():
    """Start continuous mic capture in background."""
    global _capture_active, _capture_thread

    if _capture_active:
        return

    _capture_active = True
    stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        blocksize=int(SAMPLE_RATE * CHUNK_SECONDS),
        callback=_audio_callback,
    )
    stream.start()

    def _keep_alive():
        while _capture_active:
            time.sleep(0.1)
        stream.stop()
        stream.close()

    _capture_thread = threading.Thread(target=_keep_alive, daemon=True)
    _capture_thread.start()


def get_recent_audio(seconds: float = 10.0) -> np.ndarray | None:
    """Get the last N seconds of captured audio."""
    if not _audio_chunks:
        return None

    chunks_needed = int(seconds / CHUNK_SECONDS)
    recent = list(_audio_chunks)[-chunks_needed:]
    if not recent:
        return None

    audio = np.concatenate(recent)
    return audio


# --- Prosody extraction ---

def extract_prosody(audio: np.ndarray) -> dict:
    """Extract prosodic features from audio using Parselmouth/Praat."""
    snd = parselmouth.Sound(audio, sampling_frequency=SAMPLE_RATE)
    duration = snd.get_total_duration()

    if duration < 0.1:
        return {"error": "Audio too short for analysis"}

    result = {}

    # Pitch analysis
    pitch = call(snd, "To Pitch", 0.0, 75, 600)
    pitch_values = pitch.selected_array["frequency"]
    voiced = pitch_values[pitch_values > 0]

    if len(voiced) > 0:
        result["pitch_mean"] = float(np.mean(voiced))
        result["pitch_std"] = float(np.std(voiced))
        result["pitch_min"] = float(np.min(voiced))
        result["pitch_max"] = float(np.max(voiced))
        result["pitch_range"] = float(np.max(voiced) - np.min(voiced))

        # Pitch contour direction (rising, falling, flat)
        if len(voiced) >= 4:
            quarter = len(voiced) // 4
            first_q = np.mean(voiced[:quarter])
            last_q = np.mean(voiced[-quarter:])
            diff = last_q - first_q
            if diff > 10:
                result["pitch_contour"] = "rising"
            elif diff < -10:
                result["pitch_contour"] = "falling"
            else:
                result["pitch_contour"] = "flat"
    else:
        result["pitch_mean"] = None
        result["pitch_contour"] = "no voiced speech detected"

    # Intensity (energy)
    intensity = call(snd, "To Intensity", 100, 0.0)
    result["intensity_mean"] = call(intensity, "Get mean", 0, 0, "dB")
    result["intensity_std"] = call(intensity, "Get standard deviation", 0, 0)

    # Speech rate proxy: count voiced segments (syllable-like units)
    # Using intensity peaks as rough syllable proxy
    intensity_values = intensity.values[0]
    if len(intensity_values) > 2:
        mean_int = np.mean(intensity_values)
        above_mean = intensity_values > mean_int
        transitions = np.diff(above_mean.astype(int))
        syllable_proxy = np.sum(transitions == 1)
        result["syllable_proxy"] = int(syllable_proxy)
        result["speech_rate_proxy"] = round(syllable_proxy / duration, 1)
    else:
        result["syllable_proxy"] = 0
        result["speech_rate_proxy"] = 0.0

    # Pause analysis
    silence_threshold = 50  # dB
    is_silent = intensity_values < silence_threshold
    if len(is_silent) > 1:
        silent_transitions = np.diff(is_silent.astype(int))
        pause_count = np.sum(silent_transitions == 1)
        silent_fraction = np.mean(is_silent)
        result["pause_count"] = int(pause_count)
        result["silence_fraction"] = round(float(silent_fraction), 2)
    else:
        result["pause_count"] = 0
        result["silence_fraction"] = 0.0

    result["duration"] = round(duration, 2)

    return result


def describe_prosody(features: dict) -> str:
    """Convert prosody features into a natural language description.

    Deliberately approximate and hedged -- not false precision.
    """
    if "error" in features:
        return features["error"]

    if features.get("pitch_mean") is None:
        return "No voiced speech detected in the recent audio. The user may not have been speaking."

    parts = []

    # Pitch description
    pitch_mean = features["pitch_mean"]
    pitch_range = features.get("pitch_range", 0)
    contour = features.get("pitch_contour", "flat")

    if pitch_range > 80:
        parts.append("The user's pitch is varying widely, suggesting animated or emphatic speech")
    elif pitch_range < 30:
        parts.append("The user's pitch is relatively flat, suggesting measured or deliberate delivery")

    if contour == "rising":
        parts.append("Their intonation rises toward the end, which often signals a question, uncertainty, or an invitation for response")
    elif contour == "falling":
        parts.append("Their intonation falls toward the end, which often signals a statement, conclusion, or confidence")

    # Energy
    intensity_std = features.get("intensity_std", 0)
    if intensity_std and intensity_std > 8:
        parts.append("Energy levels are variable -- some parts are emphasized more than others")
    elif intensity_std and intensity_std < 3:
        parts.append("Energy is steady throughout, suggesting even, unhurried delivery")

    # Speech rate
    rate = features.get("speech_rate_proxy", 0)
    if rate > 5:
        parts.append("Speech rate seems relatively fast")
    elif rate < 2 and rate > 0:
        parts.append("Speech rate seems relatively slow or deliberate")

    # Pauses
    silence_fraction = features.get("silence_fraction", 0)
    pause_count = features.get("pause_count", 0)
    if silence_fraction > 0.4:
        parts.append("There are significant pauses, which could indicate thinking, hesitation, or careful word choice")
    elif pause_count > 3 and features.get("duration", 0) < 5:
        parts.append("Multiple short pauses suggest the user may be formulating thoughts as they speak")

    if not parts:
        parts.append("Speech patterns seem neutral -- no strong prosodic signals detected")

    # Always add a caveat
    description = ". ".join(parts) + "."
    description += "\n\nNote: This is approximate analysis of prosodic features only. It suggests tendencies, not certainties. Use it as one input alongside the text content, not as a definitive read of intent."

    return description


# --- MCP Server ---

mcp = FastMCP(
    "emotions-mcp",
    instructions="""You have access to the user's prosodic state through the query_user_state tool.
Call this tool when you are uncertain about the user's communicative intent --
for example, when you're unsure whether they are making a request or thinking aloud,
how confident they are in what they're saying, or when their text is ambiguous in a way
that tone of voice might resolve. Do not call it on every message -- only when it would
genuinely help you interpret what the user means.""",
)


@mcp.tool()
def query_user_state(
    question: str = "How does the user seem to be communicating?",
) -> str:
    """Query the user's current expressive/communicative state based on
    their recent speech prosody (tone, pitch, pace, pauses).

    Call this when you're uncertain about the user's intent -- whether
    they're requesting action or thinking aloud, how confident they are,
    or when ambiguity in their message might be resolved by how they said it.

    Args:
        question: What specifically you want to know about the user's
                  communicative state. Be specific about your uncertainty.
    """
    audio = get_recent_audio(seconds=10.0)

    if audio is None or len(audio) < SAMPLE_RATE:
        return "No recent audio available. The user may not have spoken recently, or the microphone may not be active."

    features = extract_prosody(audio)
    description = describe_prosody(features)

    response = f"Your question: {question}\n\n"
    response += f"Prosodic analysis of the last ~{len(audio) / SAMPLE_RATE:.0f} seconds of speech:\n\n"
    response += description

    return response


# Start audio capture when server starts
start_capture()

if __name__ == "__main__":
    mcp.run(transport="stdio")
