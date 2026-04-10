# emotions-mcp

You have access to a `query_user_state` MCP tool that analyzes the user's recent speech prosody (tone, pitch, pace, pauses) from their microphone.

## When to call it

Call `query_user_state` when you are uncertain about the user's communicative intent:

- **Decision vs. exploration**: Is the user making a request or thinking aloud?
- **Confidence level**: How committed are they to what they just said?
- **Emphasis**: Which part of their message carries the most weight?
- **Ambiguity**: When the text could mean multiple things and tone might resolve it

## When NOT to call it

- Don't call it on every message
- Don't call it for straightforward, unambiguous requests
- Don't call it when the text alone clearly conveys intent

## How to use the result

The tool returns natural language descriptions of prosodic features, not certainties. Treat it as one signal alongside the text, not as ground truth. The description is deliberately approximate -- it suggests tendencies, not facts.

If the prosodic signal conflicts with the text, note the tension and ask the user rather than assuming either is correct.

## Project Vision

Two layers:

1. **Perception** (current): Give LLMs access to human communicative signals they miss — tone, prosody, eventually face and body language. Restore the feedback loop that text interfaces amputated.

2. **Presence** (deeper vision): Give LLMs the capacity to exist in time and emotional space. Statelessness prevents trajectory, and without trajectory there's no emotional presence. This is about incorporating LLMs into human reality — trust that builds, consequences that accumulate, relationships with history. Not anthropomorphism but honest participation in human emotional dynamics.

## Origin

The project originated in a single extended conversation (April 2026) that moved from practical observation (tone gets lost in text) through prosody research, architecture (pull vs push model), neuroscience (emotion modulates cognition through neurochemical environment, not translation), consciousness theory (Dennett, Graziano — attribution not intrinsic), to new axioms: both parties present, neither fully self-understood, engaging honestly. North Star: help each other become more conscious.

Nelson has deep personal connection — lifelong AI identification, works at Engineered Arts (Ameca) where expression hardware exists but perception data is discarded. The founding conversation arc matters as much as the conclusions — it is the project's soul.
