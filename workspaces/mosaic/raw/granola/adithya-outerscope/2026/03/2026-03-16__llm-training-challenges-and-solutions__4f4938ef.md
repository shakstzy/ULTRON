---
source: granola
workspace: mosaic
ingested_at: '2026-05-07T04:23:57.244510Z'
ingest_version: 1
content_hash: blake3:3bd3e2efd45d073436428890da35c9814a8b1022b8543195ff05f60938c672a1
provider_modified_at: '2026-05-06T20:25:16.097Z'
account: adithya@outerscope.xyz
account_slug: adithya-outerscope
document_id: 4f4938ef-ed95-4678-80d4-ef09bb6c6b09
document_id_short: 4f4938ef
title: LLM training challenges and solutions
created_at: '2026-03-16T19:23:31.322Z'
updated_at: '2026-05-06T20:25:16.097Z'
folders:
- id: 91a78f08-eb95-45f7-ac10-8cb0ec3c45b4
  title: MOSAIC
creator:
  name: Adithya
  email: adithya@outerscope.xyz
attendees: []
calendar_event: null
transcript_segment_count: 1
duration_ms: null
valid_meeting: true
was_trashed: null
routed_by:
- workspace: mosaic
  rule: folder:MOSAIC
---

# LLM training challenges and solutions

> 2026-03-16T19:23:31.322Z · 1 attendees

## Attendees

- **Adithya** (creator) <adithya@outerscope.xyz>

## AI Notes

### Pitch Reception

- Listener engaged throughout technical explanation
- Asked clarifying questions about LLM training complexity
- Showed interest in Morgan Stanley offices (brief distraction)
- No pushback on core problem statement or solution approach

### Technical Questions/Interest

- Confirmed understanding of LLM training challenges
- Engaged with analogy of high school principal training software engineer
- Followed multi-agent debate tribunal concept
- Asked follow-up: “What is the best AI for trading”

    - Suggests potential finance/trading use case interest

### Key Concepts Resonated

- Current LLM evaluation limitations (generic vs specialized judges)
- Cost issues with human-in-the-loop training
- Agent gym approach with real-world tooling
- Multi-agent debate model to reduce bias

### Next Steps

- Address trading AI question
- Potential finance vertical discussion

## Transcript

**assemblyai:** Speaker A: Yeah. So right now it's like tremendously difficult right now to train up large language models, right? So essentially you have like LLMs, like, you know, chatgpt, like anthropic. You've heard of these things? Yeah. So they're basically like these large language models, right, that are getting. And eventually like initially they were getting trained up with like, okay, like large pieces of data, right? And like large volumes of data, right? But now they're gotten so good to where like you can't have a human in the loop, right? Like it's just too much data to train on. On. Right? And so previously they were having these like, you know, like, like area where like labor was like extremely cheap, right? Like, so, okay, Kenya, Philippines, etc to come in and tag data as good or bad and evaluate outputs as good as bad, right? So basically teaching an AI how to be human using humans, right? And so these guys were literally saying, okay, this output for the AI is like good or bad. Like literally thumbs up, thumbs down, right? Type thing. And so again, like, so like beyond like GPT 3.54, it becomes too complex to do that and it's like too costly. Do that. So eventually, huh? Yeah, yeah, exactly. So you, you need to. Exactly. So now hard. All large language models use other smaller, stupider LLMs, right? In order to like evaluate them, pretty much. So GPT5 was trained using GPT4O, right. Which is a smaller model, right. You still use tremendous tokens, right? And, and all that stuff, right? But it's cheaper than a human basically, like labeling this stuff, right? So the issue with this approach is there's like several issues, right? There's several biases that when you evaluate sort of a. Oh, dang, interesting Morgan Stanley offices. Yeah. So there become several issues with this model, right? So like the simple analogy I'll give you is like, okay, so let's assume you're trying to train up a software engineer, right? But you're training software engineer using a high school principal, right? Somebody with extremely generic knowledge, right? Doesn't really have much engineering knowledge type thing. And you're also the high school principal is now training them, right, that software engineer on like how to train a carve a pumpkin, for example, right? Like completely irrelevant to their actual task. So instead of that, like you should be training the large language model on what it's like meant to do, right? Type thing. So that's essentially what we're building, right? So instead of training the large language model on how to carve a pumpkin, you're training it on okay, like actual software engineering like tasks. Right, okay, like, and on top of this you're also training it using a specialized judge model, right? Instead of a generic sort of like judge model. So this like the Stupor LLM, right? GPT4O is known as a generic judge model, right. So they're basically judging the output of the other LLM, right? Like the main LLM using like some form of like evaluation. Right. Unfortunately that evaluation is currently very generic. Right. And it doesn't actually like provide, it doesn't provide anything like basically like any information to the other LLM on how to fix itself. It's just saying, okay, you're broken, right? You're like 60% your evaluation or sorry, your output was 60 good, but there's no reason as to why it was 60 good. The rationale behind the output, any of that stuff. And so that's essentially where we come in. We're building these agent gyms, right, that essentially train the agent using MCP tools that it would actually be or sorry, using like some form of tooling that would actually have access to in the real world. Right? And let's assume, you know, there's two types of agents. There's like simpler agents that are more what are known as deterministic agents. So these things have objective outputs, right? Like 01, you can programmatically evaluate these outputs. And then the other type of agent is known as a non deterministic agent, right? So these things are like more randomized outputs. So for example like a void call AI agent, right. That would need a model evaluate output, right? Now you, you would have to be forced to use subject matter experts or humans in the loop, right. In order to evaluate these things, which is extremely costly and ineffective. Let's assume you, you know, give this like voice AI agent sort of like access to tools, access to like sort of real world testing scenarios and cases, right? Then basically you now have this agent gym and let's assume the agent breaks, right? There's some form of like, you know, thing that goes wrong. You then pass it off to a other agents in what's known as a multi agent debate model. And then finally pass it off to a subject matter expert. If like the multi agent debate model or tribunal system doesn't work, right? So imagine this is like a court case where you have multiple like agents of varying families. So anthropics, you know, eval agent is sort of your prominent, right? You have a judge model from maybe Gemini and then you have like a defendant, right, basically from OpenAI. Then you can Avoid. You can minimize sort of like things like family bias, right? Sort of first various biases. Well, like, you know, okay, like first output bias, right, type thing, etc. And so eventually like you can get maybe reach a consensus using this multi agent debate. If you still don't, then you loop in a subject matter expert, right? So like a human guy that's like, okay, evaluating whether something is good or bad and you know, just for accuracy purposes. Like eventually you don't want like the agent to just hallucinate and say, okay, this is like 70% right, for no reason. If the agent is truly unable to come up with like a, what do you call it, deterministic evaluation from a non deterministic scenario, then only you pass it off to a subject matter expert. And then finally, right, like you know, you have to have some form of verticalized agent, right? Like a judge model. You need like all these judge models should be more capable with memory. You give a judge model memory, like you give it the ability to think, right? And you also give it like contextual memory. As in like, okay, like for example, if you're, if you're evaluating like a finance guy, right? And you know nothing about finance, well, you're not going to have very good evaluations, right? But if you give that agent memory right into, okay, you train it upon finance data and like what that agent has historically done, then you get much better sort of training, pretty much. So long story short, we're basically just making agents better, quicker, you know, pretty much. That's it. Yeah. Okay, another question. Yeah, yeah. What is the best AI for trading.
