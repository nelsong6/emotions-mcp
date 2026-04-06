# emotions-mcp

**Exploring how LLMs could understand what humans actually mean -- not just what they type.**

## The Problem

LLMs can't distinguish between different communicative intents behind identical text, because the differentiating signal was in the delivery, not the words.

When you say "we could add caching to the API layer," your tone, posture, and facial expression tell a listener whether you're making a decision, floating an idea, or thinking aloud. An LLM gets only the transcript. It responds to your words, not your meaning.

This isn't about emotion detection. It's not about making LLMs empathetic. It's about a specific, testable claim: **communicative intent is richer than text, the missing signal is recoverable from audio and video, and giving an LLM access to that signal would make it a better listener.**

## What Success Looks Like

Record yourself saying the same sentence two ways -- once as a firm decision, once as an exploratory thought. Both transcribe to identical text.

- **Without the system**: the LLM responds identically to both.
- **With the system**: the LLM responds differently, and the difference matches what you actually intended.

That's the test. Everything else follows from whether that works.

## Roadmap

### Step 1: Capture and annotate

Hook up mic and camera. Extract basic features: pitch, energy, pace, facial action units, gesture. Translate these into text annotations injected into the LLM prompt. Crude but functional -- the goal is to have something running, not something perfect.

There's existing research and tooling for codifying emotional expression that we can piggyback off of for the early stages rather than building perception from scratch:

- **Hume AI** -- API access to 48 emotional dimensions from voice, plus facial expression analysis. The most production-ready option for getting emotion scores quickly.
- **FACS (Facial Action Coding System)** -- 44 action units mapping facial muscle movements. Implemented in open-source tools like OpenFace and MediaPipe.
- **Whisper + prosody extraction** -- OpenAI's Whisper for transcription, combined with libraries like Parselmouth/Praat for pitch, energy, and speech rate extraction.
- **Weizmann prosodic framework** -- Academic but the most rigorous model of what tone carries (5 simultaneous layers per utterance).
- **MediaPipe** -- Google's open-source framework for face mesh, pose estimation, and gesture recognition from camera input.

The important design note: these tools output structured scores and classifications (confidence: 0.72, emotion: "determination"). That framing imposes false precision on something that's inherently approximate and contextual. For the prototype, it may be better to translate these signals into natural language descriptions rather than numeric scores -- descriptions that are honest about the approximate, layered nature of emotional expression rather than forcing it into a mathematical frame.

### Step 2: Establish a baseline

Before testing the system, document what "without it" looks like. Record the same instructions delivered different ways (exploratory vs. decisive, confident vs. uncertain, emphasizing different words). Transcribe to identical text. Send plain text to the LLM. Document responses. This is the control group.

### Step 3: A/B test

Same inputs, now with annotations. Does the LLM respond differently? Does the difference match intended meaning? **This is the kill decision.** If annotated prompts don't measurably change LLM interpretation of ambiguous intent, the rest doesn't matter.

### Step 4: Find what matters

Some annotations will change LLM behavior. Some won't. Confidence level might be load-bearing. Gaze direction might be noise. Prune the dimensions that don't pull weight, double down on the ones that do.

### Step 5: Move to pull model

Now that you know which dimensions matter, expose them as an MCP tool the LLM can query on-demand instead of always injecting them. Test whether on-demand querying works as well as always-on annotation with less context noise.

### Step 6: Add temporal context

The state service starts tracking trends -- is confidence rising or falling across the conversation? This goes beyond per-utterance annotation into something that couldn't be done with simple prompt injection.

### Step 7: Real usage

Stop testing with contrived examples. Use it in a normal workflow for a week. Journal where it helps, where it's wrong, where it's irrelevant. That data tells you whether this is a tool or a toy.

## Longer-Term Ideas

The roadmap above is the testable, buildable path. But the exploration surfaced deeper ideas that shouldn't get lost -- they're where this goes if the prototype validates the hypothesis.

### Emotional data as a native message format

The end-state vision isn't text annotations about emotions. It's the LLM receiving actual emotional/expressive data as a first-class part of the message -- structured representations that carry the richness of the original signal rather than compressing it to English descriptions. If the prototype shows that even crude text annotations improve interpretation, the question becomes: what happens when the representation gets richer and moves beyond what text can express?

### A dedicated emotional reasoning LLM

Current emotion AI is classification (acoustic pattern maps to label). But understanding how someone feels is a reasoning problem -- synthesizing signals across modalities, over time, with context. A dedicated LLM whose entire purpose is building deep emotional understanding could absorb the full density of expressive signals and serve as the perception layer that the task LLM queries.

### The translation problem

Emotional expression is a language. Text is a different language. If the interface between an emotional perception system and a task LLM is text, we've recreated the original lossy compression one layer deeper. This suggests several architectural directions:

- **Shared embedding space** -- emotional understanding passes as high-dimensional vectors, not text
- **Modulation, not translation** -- emotional state changes *how* the task LLM processes input (attention weights, confidence thresholds) rather than adding content to the prompt. Neuroscience supports this: the brain doesn't translate emotions into thoughts. Emotional states change the neurochemical environment in which reasoning happens -- neuronal gain, signal-to-noise ratios, precision weighting of prediction errors. Emotion modulates cognition rather than informing it.
- **Single integrated model** -- one model that processes both, the way humans do. The eventual right answer, but a research problem.

### Multi-mode delivery

If the signal turns out to be dense (every clause matters), a tool-call model breaks down. The system may need multiple operating modes:
- **Ambient**: lightweight per-utterance tags, always present, near-zero token cost
- **Pull**: full structured queries at decision points
- **Stream**: continuous deep integration for high-density contexts

### Self-refining framework

The queries the LLM makes (or the annotations that change its behavior) become data about which dimensions of expression actually matter. The framework discovers its own most important features rather than being designed top-down.

## Research Foundation

A detailed survey of prior art, existing systems, theoretical frameworks, and the novelty analysis is in [Issue #1](https://github.com/nelsong6/emotions-mcp/issues/1). Key findings:

- **No existing system** exposes user expressive state as a queryable service (all use push models)
- **Tavus Raven-1** is closest but inverts the directionality (perception triggers tool calls, not reasoning triggers perception queries)
- **The Weizmann PNAS work** provides the most rigorous framework for what prosody carries (5 simultaneous layers per utterance)
- **No unified cross-modal framework** exists for fusing tone, face, and body into a single communicative state representation
- **Neuroscience says emotion and cognition are not separate systems** -- they share infrastructure, and emotional states modulate reasoning through neurochemical environment changes, not information transfer. This supports the modulation architecture over the translation architecture.

## Status

Early-stage. The ideas here emerged from an extended exploration and haven't been validated with a prototype yet. Next step is Step 1: get capture and annotation running.

## License

MIT
