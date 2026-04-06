# emotions-mcp

**Exploring how LLMs could understand what humans actually mean -- not just what they type.**

## The Problem

When humans communicate, the words are only part of the message. Tone of voice, facial expressions, body language, and gestures carry critical information about intent: confidence level, whether someone is thinking aloud or making a decision, what they're emphasizing, whether they're being sarcastic or sincere.

Current LLM interfaces strip all of this away. A text transcript of "we could add caching to the API layer" tells the model nothing about whether the user is proposing a firm plan or floating a half-formed idea. The tone, the shoulder shrug, the rising intonation -- all lost.

This project is an ongoing exploration of that gap: what's lost, what it would take to recover it, and what the right architecture might look like. We don't have the answers yet -- but the questions are getting sharper.

## Where the Exploration Has Gone So Far

### 1. The starting observation

People who think primarily in speech and tones (most people) lose critical signal when communicating with LLMs through text. Existing solutions either ignore this or use a push model that dumps emotion labels ("user is happy", "user is frustrated") into the prompt. That's too crude -- tone carries far more than emotion.

Based on research (particularly the Weizmann Institute's 2025 PNAS work), tone simultaneously carries at least five layers of meaning per utterance: syntactic modality, discourse function, information structure, intentional attitude, and unintentional emotion. Body language and facial expressions carry overlapping signals. They're all expressions of the same underlying communicative state, not separate channels.

### 2. Queryable state, not context dump

Instead of streaming emotional metadata into every prompt (which burns context window and adds noise), what if the LLM could query user expressive state as a tool -- pulling specific information at decision points?

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
     ]
   }
```

This pull model lets the reasoning system decide what's relevant, not the perception system. It also generates data about which dimensions of expression actually matter for LLM decision-making (self-refining).

But this raises a question: what if emotional signal is dense, not sparse? If every clause carries relevant tonal information, a tool-call model breaks down. This led to the idea that the system probably needs multiple operating modes:

- **Ambient**: lightweight per-utterance tags, always present, near-zero token cost
- **Pull**: full structured queries at decision points, on-demand
- **Stream**: continuous deep integration for high-density contexts (therapy, negotiation, teaching)

### 3. An LLM that reasons about emotions

Current emotion AI is classification -- acoustic pattern maps to label. But understanding how someone feels is a reasoning problem: it requires synthesizing signals across modalities, over time, with contextual knowledge. "The user said 'that's fine' but their tone dropped, they shrugged, and fifteen minutes ago they were excited about this feature -- so 'fine' here is resignation, not agreement."

This led to the idea of a dedicated emotional LLM -- not a classifier, but a reasoner whose entire purpose is building deep emotional understanding. It absorbs the full density of expressive signals (tone, face, body, temporal patterns) and the task LLM queries it rather than processing raw signals itself.

### 4. The translation problem (the hard part)

This is where the exploration currently sits, and it's the most important insight so far:

**Emotional expression is a language. Text is a different language. And text is what was losing the information in the first place.**

If we build a brilliant emotional reasoning system and its interface to the task LLM is a text string -- "the user seems uncertain" -- we've recreated the original lossy compression one layer deeper. The emotional LLM doesn't speak code. The task LLM doesn't speak emotions. And text is an inadequate bridge between them.

This suggests several possible architectures, ranging from pragmatic to aspirational:

1. **Text bridge** (buildable now, knowingly lossy) -- The emotional LLM outputs structured text that the task LLM reads. Information is lost, but even crude emotional signal may improve interpretation. Good enough for a prototype.

2. **Shared embedding space** -- The emotional and task LLMs share a sub-linguistic representational layer. Emotional understanding passes as high-dimensional vectors, not compressed text. Closer to how multimodal models handle vision + language internally.

3. **Modulation, not translation** -- The emotional system doesn't *communicate* with the task LLM; it *tunes* it. Emotional state modifies attention weights, sampling parameters, or interpretation of ambiguous tokens. Like a musician who *feels* sad and their playing reflects it, versus a musician told "play sadly."

4. **Single integrated model** -- One model that thinks in both emotions and tasks simultaneously, the way humans do. The eventual right answer, but a training/architecture research problem.

Option 3 is the most interesting conceptually -- emotion as a force that shapes reasoning rather than data that informs it.

## Open Questions

This is an active exploration. Major open threads:

- What does the "language of emotional expression" actually look like as a formal representation?
- Can a text bridge prototype demonstrate enough value to validate the direction?
- What does modulation (option 3) require architecturally? How deep into transformer internals does it need to go?
- How do you evaluate whether emotional understanding actually improves LLM behavior?
- What domains would benefit most? (Coding may be low-signal; therapy/teaching/negotiation may be high-signal)
- Privacy implications of continuous audio/video perception?
- Is the relationship between emotional and analytical reasoning fixed, or dynamic and context-dependent? (Early intuition: dynamic -- people can modulate it, like deep focus during chess)

## Research Foundation

A detailed survey of prior art, existing systems, theoretical frameworks, and the novelty analysis is in [Issue #1](https://github.com/nelsong6/emotions-mcp/issues/1). Key findings:

- **No existing system** exposes user expressive state as a queryable service (all use push models)
- **Tavus Raven-1** is closest but inverts the directionality (perception triggers tool calls, not reasoning triggers perception queries)
- **The Weizmann PNAS work** provides the most rigorous framework for what prosody carries (5 simultaneous layers)
- **No unified cross-modal framework** exists for fusing tone, face, and body into a single communicative state representation
- **~200 discernible prosodic patterns** with linguistic-like structure (vocabulary, semantics, syntax) suggest the "language" of tone is discoverable and codifiable

## Status

Early-stage concept exploration. The ideas here emerged from a single extended conversation and haven't been validated with a prototype yet. The next step is likely an audio-only proof of concept to test whether even crude emotional signal (via text bridge) measurably changes LLM interpretation quality.

## License

MIT
