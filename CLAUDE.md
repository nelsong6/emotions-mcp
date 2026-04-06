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
