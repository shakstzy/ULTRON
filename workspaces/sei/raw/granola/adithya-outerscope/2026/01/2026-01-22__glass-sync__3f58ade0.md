---
source: granola
workspace: sei
ingested_at: '2026-05-07T04:23:57.244510Z'
ingest_version: 1
content_hash: blake3:93fb30a6bf267f52b6de8b591f1f6bc59e2c077d1de731ab2eae81dafff045c9
provider_modified_at: '2026-01-22T18:21:31.390Z'
account: adithya@outerscope.xyz
account_slug: adithya-outerscope
document_id: 3f58ade0-9d38-47d0-aedd-102a93922b56
document_id_short: 3f58ade0
title: Glass Sync
created_at: '2026-01-22T18:13:04.801Z'
updated_at: '2026-01-22T18:21:31.390Z'
folders:
- id: 3ca3cb55-d6e1-49ef-961a-8ba2469731a5
  title: SEI
creator:
  name: Adithya
  email: adithya@outerscope.xyz
attendees:
- name: null
  email: chetan@seinetwork.io
- name: null
  email: jay@seinetwork.io
- name: null
  email: cody@seifdn.org
- name: null
  email: paulg@seinetwork.io
- name: null
  email: cody@seinetwork.io
- name: null
  email: campbell@seinetwork.io
- name: null
  email: jeff@sierrawood.io
calendar_event:
  title: Glass Sync
  start: '2026-01-22T12:00:00-06:00'
  end: '2026-01-22T12:30:00-06:00'
  url: https://www.google.com/calendar/event?eid=YW90MTl2dnN1bWM1cnZ0cm04ZXUxNHUzcHJfMjAyNjAxMjJUMTgwMDAwWiBhZGl0aHlhQHNlaW5ldHdvcmsuaW8
  conferencing_url: https://meet.google.com/teo-dbhh-nhb
  conferencing_type: Google Meet
transcript_segment_count: 55
duration_ms: 498240
valid_meeting: true
was_trashed: null
routed_by:
- workspace: sei
  rule: folder:SEI
---

# Glass Sync

> 2026-01-22T18:13:04.801Z · duration 8m 18s · 8 attendees

## Attendees

- **Adithya** (creator) <adithya@outerscope.xyz>
- <chetan@seinetwork.io>
- <jay@seinetwork.io>
- <cody@seifdn.org>
- <paulg@seinetwork.io>
- <cody@seinetwork.io>
- <campbell@seinetwork.io>
- <jeff@sierrawood.io>

## Calendar Event

- Title: Glass Sync
- Start: 2026-01-22T12:00:00-06:00
- End: 2026-01-22T12:30:00-06:00
- URL: https://www.google.com/calendar/event?eid=YW90MTl2dnN1bWM1cnZ0cm04ZXUxNHUzcHJfMjAyNjAxMjJUMTgwMDAwWiBhZGl0aHlhQHNlaW5ldHdvcmsuaW8
- Conferencing: Google Meet https://meet.google.com/teo-dbhh-nhb

## AI Notes

### Databricks Meeting Follow-up

- Customer focus on model troubleshooting in production

    - Data scientists spend significant time determining if model misbehavior stems from training data issues
    - Similar challenges identified at Pinterest and Adobe
    - Need clearer product definition for addressing this use case
- RAG vs fine-tuning discussion

    - Strong industry trend toward RAG over fine-tuning for future applications
    - Opportunity to add unique value through verifiability features
    - Need to iterate on interactive vector DB approach

### Industry Trends & Market Shifts

- Purpose-built models gaining traction

    - Anthropic and OpenAI questioning generic model approach
    - Models trained only on relevant data for specific use cases
    - Eliminates unnecessary training on irrelevant internet corpus
- Implications for specialized model architectures

### Product Development Priorities

- RAG story refinement

    - Action: Paul and team to develop credible value proposition
    - Focus on verifiable, interactive approaches
- Data lineage product definition

    - Concept: Overlay sitting on graph DB for data-level lineage
    - Differentiator from application-level solutions like Weights & Biases
    - Currently undefined scope and technical approach

### Fundraising Preparation

- Key deliverables needed:

    1. Updated white paper
    2. Light paper pitch deck revision
    3. V1 pitch deck completion
- Strategic decision on data lineage inclusion

    - Risk: 50% defined features may generate open-ended investor questions
    - Alternative: Focus solely on managed TEs, expand vision later
    - Team preference: Attempt full definition to differentiate from neo-cloud competitors

### Next Steps

- Paul and Chetan: Define RAG value proposition (Friday/weekend)
- Paul and Chetan: Scope data lineage product definition for fundraising materials
- Team: Complete pitch deck V1 and customer outreach preparation

---

Chat with meeting transcript: [https://notes.granola.ai/t/31d265a8-3cf8-448d-8a35-8e1abdb1b075](https://notes.granola.ai/t/31d265a8-3cf8-448d-8a35-8e1abdb1b075)

## Transcript

**Other:** For the most part, they quickly try and gravitate towards. What was the input data, what was the training data, what actually happened there? And that's where they spent or. His comment was that that's where the data scientists spent a lot of time kind of thinking through did the model misbehave or was it trained on shitty data? And unfortunately, based on all the conversation was going like, Paul and I didn't really get an opportunity to kind of talk about how we're thinking about that particular problem because that is similar to the challenge that Pinterest talked about and also what Adobe talked about. With respect to just unpacking or troubleshooting why a model is misbehaving in production. A lot of times they need to go back to the input data or the training data, which again. Is something that we have talked about, but we haven't really put a really crisp description of what product we might build that might actually help them in that space. Yeah. But I do wonder about this. I think there is something really interesting though about what he's saying about rag and tool calling. This is also something over a Kartik brought up. And Jay, I think we talked about this with Karthik feels very strongly about fine tuning not being a thing for the future in rag, just being what everyone's going to use. Correct? Yeah, he sort of got a little softer on that recently, saying that he thinks that this, like, continuous reinforcement learning, you might bring it back. But it's like, I do think that this question of. We've known that we need to consider on the private inference side, we need to consider rag. We need to consider how this interactive vector, dps, et cetera. There. But we haven't done much thinking around. Can we provide something unique to that experience? The verifiability piece, something like that could go there. And that seems like something we just need to iterate on today and come up with a pitch and see if it makes any fucking sense today. Go ahead. Yeah, I'M just going to say, literally this morning I came through an article that was talking about. How there's also a very active discussion around purpose Bill models. So if you look at what Anthropic and OpenAI are doing right now, they have the generic models they're trying to use for anything and everything. And they were like, does that even make sense? A model that is going to be only designed for coding, what value is there for that model to actually know about human history or whatever? X, Y and Z. Right. So like the entire corpus of data that is going into pre training and then you're doing post training for just optimizing for a particular use case. That has come to the forefront of people are saying, why are we doing that in the first place? If you have a general model architecture, and if you want to intend to only use it for a specific use case, just train it against the data that is applicable for that particular use case, not the entirety of the Internet. That is not valuable. That's the other trend that is surfacing that will have to be mindful of and see how that kind of plays out. Jay. Yeah. I was just going to say that the databricks context is helpful. I wanted to make sure we're able to get through everything, especially with growth folks on the call as well. So was there anything else you guys wanted to go over the non native brick side or do you primarily want to just. Yeah, I think it's summarizing. The action item is on Paul and my site specifically to kind of think through our rag story. And make sure we, at least first, first and foremost, we were able to kind of think through a credible way of being able to add value to that workflow. Yeah, okay, that makes sense. Okay? Sounds good. So that was databricks. I'm kind of looking through the other work streams. Oh, yeah, so I already touched upon this. We'll have to update the white paper and the light paper pitch deck. Fundraising. Those are the key things on my side. Anything else from anybody. Otherwise, we're just in a crack mode. Right? The V1 of the pitch deck. The customer outreach has. And then obviously on the fundraising side, getting our. The only other thing from my side was the data lineage kind of product definition. That's not going to be ready, presumably by the time the fundraise gets started. No, but there's no reason why we can't write down, like, a few paras to kind of explain our. Our concept and our proposed solution. More, Jay. Like, what Paul and I, we were discussing was like, let's take weights and biases as an example. So they have a lineage capability. For data that they're hosting or they're managing. Right. So if somebody's using weights and biases and they have actually subscribed all the entire the entirety of the training data, weights and biases, they can actually do a pretty good job. Our current thinking is that you want that lineage information to not be at, like, application level, but fundamentally at the data level. Right, so this is where having an overlay that sits on top of some sort of maybe a graph DB or something like that could actually make sense. But exactly what that looks like. We haven't really spent cycles on kind of outlining. That makes sense. I'm trying to think through what's better for the fundraise. Like my intuition is if you don't have something very well scoped out already from the product side, it might be better to only focus on the managed tea part of it and leave the lineage part of it. Kind of like a next step. Versus having something that's like 50% defined that might lead to, like, more open ended questions coming your way. Yeah, let me. Let me take some notes here. So I guess to be more prescriptive there, if you feel like you're not comfortable with the product definition of that, you don't have to include it in the deck. Like it the pitch could primarily be around manage these. No, I think. I think we can make. Paul, what do you think? Can we? Can we spend cycles to come? I think we should try to do it. And then if we decide that we don't like it, we can remove it. But like, I think we should try because it expands, it shows the vision of kind of not like, let's put it this way, if we just say manage Tes. We're basically a comp to a neocloud, I think. But, like, we're up to a neocloud with a. With a smaller market. And that's, I don't think, where we want to end up. I mean, you could also just be saying, we're going to be owning every single part of the stack for, like. I think the terminology used was, like, model deployment. And you could just leave three of them opaque for now. And leave one of them as like. Yeah, we're building a managed solution. Adithya. Anyway, I just wanted to flag that. Don't need to spend too much more time on this call. If you guys want to chat about that later. Yeah. Okay, so that's. One thing that, Paul, you and I, we can spend some cycles on either Friday or maybe sometime over the weekend. Yeah. I mean, I'm thinking butter right now. Behind while doing everything else. So. Yeah. Giving it all today. Okay? Cool. Thank you, guys. All right. Thank you, everybody. Got you guys later. Bye. Thanks, everyone.
