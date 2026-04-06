# emotions-mcp

**Queryable user expressive state as a tool for LLMs.**

## The Problem

When humans communicate, the words are only part of the message. Tone of voice, facial expressions, body language, and gestures carry critical information about intent: confidence level, whether someone is thinking aloud or making a decision, what they're emphasizing, whether they're being sarcastic or sincere.

Current LLM interfaces strip all of this away. A text transcript of "we could add caching to the API layer" tells the model nothing about whether the user is proposing a firm plan or floating a half-formed idea. The tone, the shoulder shrug, the rising intonation -- all lost.

Existing approaches to this problem use a **push model**: continuously monitor the user's emotional state and stream it into the LLM as context. This creates noise, burns context window, and forces the perception system to decide what's relevant rather than the reasoning system.

## The Idea

**User expressive state as a queryable service, not a context dump.**

Instead of attaching a full emotional readout to every message, give the LLM a tool it can call at reasoning-time decision points:

```
Model's internal reasoning:
  "User said 'we could try caching.' I'm about to plan
   an implementation. But this might be exploratory."

-> query_user_state("Is the user proposing a decision or thinking aloud?")

<- {
     classification: "exploratory",
     confidence: 0.87,
     evidence: [
       { source: "prosody", signal: "rising intonation on 'caching'" },
       { source: "gesture", signal: "shoulder raise during statement" },
       { source: "gaze", signal: "upward direction — recall/imagination" }
     ],
     recommendation: "Treat as brainstorming. Discuss trade-offs
                       rather than implementing."
   }
```

The model asks what it needs, when it needs it, with the reasoning context of *why* it's asking. The perception system handles the multimodal fusion and returns a targeted answer.

## Key Architectural Principles

### Pull, Not Push

The LLM initiates queries to the state service at its own decision points. The perception system doesn't need to know what's relevant to the model's current reasoning -- it just answers questions.

### Unified Communicative State

Tone, facial expression, and body language aren't separate signal taxonomies. They're multiple sensors reading the same underlying communicative state. A shoulder shrug and a rising intonation and the word "maybe" are all evidence for the same thing: uncertainty. The state service fuses these into a unified representation.

### Queries Carry Context

The model doesn't just ask "what is the user feeling?" It asks questions shaped by its current reasoning: "I'm about to treat this as a firm requirement -- is that consistent with how they expressed it?" This context allows the state service to return maximally relevant answers.

### Self-Refining

The queries themselves become data. Logging what the LLM asks about user state and when reveals which dimensions of expression actually matter for model decision-making. This feeds back into improving the state representation. The framework discovers its own most important features.

## Why This Matters

LLMs are increasingly used as reasoning partners, not just text generators. The quality of that partnership depends on the model understanding not just *what* you said, but *how* you said it and *what you meant by it*. For people who think primarily in speech and expression (most people), the text interface is a lossy compression of their actual communication.

This project explores whether giving LLMs on-demand access to the full expressive signal -- structured, queryable, and multimodal -- changes the quality of human-AI collaboration.

## Architecture (Planned)

```
                                    +-------------------+
                                    |    LLM Runtime    |
                                    |  (Claude, GPT,    |
                                    |   Gemini, etc.)   |
                                    +--------+----------+
                                             |
                                    tool call: query_user_state()
                                             |
                                             v
+------------------+           +----------------------------+
|  Audio Input     |---------->|                            |
|  (microphone)    |           |   Expressive State Service |
+------------------+           |                            |
                               |   - Multimodal fusion      |
+------------------+           |   - Temporal accumulation  |
|  Video Input     |---------->|   - Query interpretation   |
|  (camera)        |           |   - Evidence assembly      |
+------------------+           |                            |
                               +----------------------------+
```

The Expressive State Service:
- Continuously processes audio/video input (perception runs always)
- Maintains a rolling state representation (temporal context)
- Exposes a query API that the LLM calls as a tool
- Returns structured, evidence-backed answers to specific questions
- Logs queries for framework refinement

## What's Novel

Based on a survey of published research, patents, and production systems (as of April 2026):

1. **State as a queryable service** -- All existing affect-aware LLM systems use push architectures (Hume EVI, Empathic Prompting, SocialMind). None expose user state as an API the LLM queries on demand.

2. **LLM-initiated perception** -- The closest system (Tavus Raven-1 "perception tool calling") has perception triggering tool calls, not reasoning triggering perception queries. The directionality is inverted.

3. **Query-as-data for framework refinement** -- No existing system uses the model's own information needs as a signal for which expressive dimensions matter most.

4. **Unified cross-modal communicative state** -- Existing frameworks are modality-specific (FACS for face, ToBI for prosody). No production system fuses these into a single queryable representation of communicative intent.

## Status

Early concept stage. See [Issues](https://github.com/nelsong6/emotions-mcp/issues) for the full research background and development discussion.

## License

MIT
