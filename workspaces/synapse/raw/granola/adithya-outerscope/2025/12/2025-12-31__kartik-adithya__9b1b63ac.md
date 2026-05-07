---
source: granola
workspace: synapse
ingested_at: '2026-05-07T04:23:57.244510Z'
ingest_version: 1
content_hash: blake3:fc6261bc91d6a8dae3047d113f73cf72dae32e533a51c95c87028ef9df79dc9f
provider_modified_at: '2025-12-31T19:10:04.774Z'
account: adithya@outerscope.xyz
account_slug: adithya-outerscope
document_id: 9b1b63ac-9c24-4861-be82-c4e5bf40a5a8
document_id_short: 9b1b63ac
title: Kartik <> Adithya
created_at: '2025-12-31T18:30:53.500Z'
updated_at: '2025-12-31T19:10:04.774Z'
folders:
- id: 91a78f08-eb95-45f7-ac10-8cb0ec3c45b4
  title: MOSAIC
- id: 2ace9cb8-854d-4638-9adb-ba6455b0eeb5
  title: SYNAPSE
creator:
  name: Adithya
  email: adithya@outerscope.xyz
attendees:
- name: Kartik Bhat
  email: kartik@seinetwork.io
calendar_event:
  title: Kartik <> Adithya
  start: '2025-12-31T12:30:00-06:00'
  end: '2025-12-31T12:45:00-06:00'
  url: https://www.google.com/calendar/event?eid=YmQ1OWRmODIzOGU0NDAzZGEzZDk5MGEyNTBhNGJlOGIgYWRpdGh5YUBzZWluZXR3b3JrLmlv
  conferencing_url: https://meet.google.com/ztq-desw-igk
  conferencing_type: Google Meet
transcript_segment_count: 115
duration_ms: 2337259
valid_meeting: true
was_trashed: null
routed_by:
- workspace: synapse
  rule: folder:SYNAPSE
---

# Kartik <> Adithya

> 2025-12-31T18:30:53.500Z · duration 38m 57s · 2 attendees

## Attendees

- **Adithya** (creator) <adithya@outerscope.xyz>
- Kartik Bhat <kartik@seinetwork.io>

## Calendar Event

- Title: Kartik <> Adithya
- Start: 2025-12-31T12:30:00-06:00
- End: 2025-12-31T12:45:00-06:00
- URL: https://www.google.com/calendar/event?eid=YmQ1OWRmODIzOGU0NDAzZGEzZDk5MGEyNTBhNGJlOGIgYWRpdGh5YUBzZWluZXR3b3JrLmlv
- Conferencing: Google Meet https://meet.google.com/ztq-desw-igk

## AI Notes

### Adithya’s Eval Product Concept

- Identified two key pain points in ML eval pipeline:

    - Manual eval processes (extremely time-intensive)
    - Expensive, difficult ground truth data procurement
    - Data provider mismanagement issues
- Proposed addressing both eval completion and retraining data collection

    - Ground truth data sourcing
    - Data needed for model retraining after identifying issues

### Kartik’s Market Reality Check

- Eval market consolidating into inference providers:

    - AWS Bedrock, Together AI bundling evals with inference
    - OpenAI has dedicated eval APIs
    - Vellum packaging end-to-end eval suites
- Standalone eval companies struggling:

    - Patronus (Rebecca + Anand from UChicago) raised Series A but facing challenges
    - Hazelabs failed in similar direction
    - Top-heavy market with limited standardization need
- Data collection happening at inference layer where responses live

### Current Enterprise Reality

- Most companies not using custom data yet:

    - Drada, Vanta using basic prompting over complex eval pipelines
    - Next-gen models + prompting solving issues without heavy data investment
- Only top agentic companies (Harvey AI, Cognition) need robust eval pipelines

    - These already being addressed by specialized solutions
- Putting “cart before horse” for most potential customers

### MLOps Pipeline Overview

- Model deployment & serving:

    - Checkpointing for weight snapshots
    - Load balancing and batching
    - Error checking and guardrails
- Data collection & analytics:

    - Sentry-style AI monitoring
    - Automated conversation quality assessment
    - Customer satisfaction analytics
- Content policy enforcement and inappropriate output detection

### Kartik’s Recommendations

- Focus areas with potential:

    1. RL fine-tuning tooling and gym creation

          - Referenced OpenAI alumni company (Fact Compute) doing enterprise RL FDE
          - Growing demand in this space
    2. AI observability (study Braintrust.dev)

          - Traces model outputs and performance
          - Growing need as models scale
- Avoid crypto integration unless specifically necessary
- Study failed eval companies for lessons learned

## Transcript

**Me:** I still feel like a failure, though. Nigga, how is that possible? Banger.

**Other:** Me. 19. And. So we made it. For you.

**Me:** Through v. Cooker.

**Other:** To create RL environments and RL gyms for any task.

**Me:** Got you.

**Other:** So take a look at that. It's called the Environments Hub. And let's say, Adithya, I wanted to create an RL environment for being really good at Rust. So you can create an environment for that and then people can use that to basically do an RL fine tuning or like eval their models on that. Right. It's like an open source. It's unverifiable, but it's like an open source layer for just aggregating these RL gems. It kind of makes me feel it's a little bit similar to what you're talking about there. Right? Yeah, I think verifiability.

**Me:** Yeah.

**Other:** Is your point? More that nobody knows how to verify a model. Really? Like the benchmarks, you can't trust it.

**Me:** So, like, verticals, like judge, like AI always evaluates AI at this point. Right. So verticalized judge models always have inherent biases in them. Right. Type thing. And, like, in order to determine that, it's very difficult. And also, automating evaluations is extremely, extremely tough. I had a couple calls, like, last week. With, like, a couple CTOs that are doing model evaluates right now. And they're like, all of them are like, bro, like, I was thinking about this a while back, but the issue is automating. This is extremely tough. Like, that's near impossible. Through my research that I found, like, you need extremely product. Specific or extremely vertical specific. Like judge models, which the only way you can create that is just by, like, sort of like collecting data, right? What's also extremely tough for people to do is collecting ground truth, right? Like, data as well. Like, actually evaluating. Like, okay, what is the model like? You. You know what your entry is. Bro. Essentially like how do you collect the data for ground truth in like a non costly manner? And then also how do you like create like super specific, like specialized sort of like data labeling as well, right? Like super high touch point, like data label.

**Other:** Specialize. You see, like, okay, is it like per enterprise, like specific vertical? Like if I'm trying to do a healthcare. If you're trying to, yeah. I mean, I think that makes sense. I think that's like kind of similar to what I think the parallel here is that again, everyone's trying to. Do RL fine tuning and build their evals. Like, again, evals is just one part of the pipeline, I think the biggest source. Like, you could. You could see that what I sent to you, like Hazelabs, you know, is this other company that's kind of failed in this direction, but they were building evals. For every company.

**Me:** Exactly.

**Other:** I think a lot of the focus for the Frontier Labs is like, OK, we're going to have FT's that go to these companies and build evals so that rl fine tune on their task like a finance guy or like a Excel spreadsheet, whatever that is.

**Me:** Yeah.

**Other:** I do tend to think that, like. It doesn't seem. I think a lot of those eval companies have sort of failed a little bit like they have. They've struggled because it's incredibly top heavy right now. Right? And it's like, I don't know if you need an extra verifiable layer. So, like, can you. Can you, like, give me, like, a comp, like a web2comp, potentially that, like. Yeah.

**Me:** Y. Eah, 100%. Okay, so let's take like a. Like a voice AI the company, for example, right?

**Other:** Sure, sure, sure.

**Me:** Like a Cartesia, right? Like, they're building, like, SSM models for, like. Like voice training, all this shit, right? Well, you would need some form of eval, right, to be completed there. Like, you need ground truth, like, sources of data, which is extremely expensive to procure right now. And if you sort of, like, just automated sort of eval again. You're encountering, like, you know, a ton of biases. Right. Type thing. Or like, even, like, just, like, mismanaged data. So now you know. Okay. Like, you have sort of an eval complete. Let's assume, like, you even remove the complete eval stack. Done. Or. Sorry, out of the picture. If you have just the eval rate completed now, you need to know, like, what type of data you even need, right? Type thing. And like, once you've determined the type of data you need, you actually need to go out and collect that data. So the two data, like points you really need. To collect that no one else is addressing, at least from what I've found, is one, like, the actual, like, ground truth data. Right. And then two, the data that you need in order to, like, retrain your model. So retrain. So these two, like, are kind of like untapped sort of markets, as what I found. But maybe I'm wrong here. Like, based on what you're saying.

**Other:** Can you repeat the second one real quick?

**Me:** Yeah. So, like, like the data you would need to retrain the model, right? Like, you now know what's broken. Like, type thing. Like, how do you fix it? Like, what type of data would you even need to fix?

**Other:** Yeah, and I hear you on this. It just seems to me that, like, a lot of this, Is kind of moving to the inference layer. Like, like, sort of like the companies that provide inference, like aws, Bedrock or together, AI is sort of helping with this process. Like, I think part of that was, like, with fine tuning, like, they provided a whole suit of fine tuning, you know, APIs, and then, like, you can collect data on your rollouts, and then you could train on that. So I'm struggling to see where a separate company would come in. Right and help here. So, like, give me. Walk me through the pain point that your friend said. I don't know if it was, like, Mercour or this other CTO that you said. What is a pain point, specifically that they're running it to?

**Me:** Right now. Like, model, like, model evals are highly, highly manual. Right. Type thing for him. Like, it's an extremely process to do. And then also, like, data is extremely tough to procure, like, or not tough necessarily, but extremely expensive to procure. And it also, like, there's like a ton of mismanagement. In that process just because, like, the data provider themselves is out of the loop pretty much.

**Other:** Okay? Sure, sure, sure, sure. Yeah. I get it. It's just that I think there's a reason why it's like that. Because it's moving so fast and it's so top heavy that, like, you could argue that the standardization will come, but it's not really needed right now, and it's like. I think a lot of that standardization is coming from the inference providers, actually themselves. And so that's where I take a look at one. OpenAI has their own eval, sort of API. I would look into that. Obviously, that's existing, but bedrock as well as, you know, inference providers, like together AI are sort of bundling together. Look at Vellum as well. They're bundling together evals along with the inference suite because they realize to end to end deploy, you need to have a really robust eval suite, right?

**Me:** Great, great.

**Other:** So, like, for example, they'll be like, I don't know if this is related to what you're discussing, but it's like, my brother who works on, like, my. My friend and my brother. One of them works at Harvey, and one of them worked in SOC 2, compliance. And Harvey, it's like they, they literally use these guys, these like no code solutions, as well as like these inference writers to create these test beds for themselves that they will just like automatically run eval's on and then like test regressions, etc. Right. And so like it's kind of like a CI CD for, like, model behavior.

**Me:** Exactly. Yeah, dude, like, pretty much for Eval.

**Other:** Exactly. MLP is the way. And I think that, like, a lot of that is coming into the inference provider layer itself.

**Me:** Okay, interesting.

**Other:** It's because, you know. And you could let me just send this to you as well. It's like, because it's all packaged into the model deployment, right? It's like, okay, outside of the weights, When you want to infer the model, you deploy it using together AI, then you get like this, like, you know, URL that you can, like, hit with the curl request. Okay. And then when you actually, you want to save those responses because you want to maybe have some way for a random person to go and say, oh, this was correct. This was incorrect.

**Me:** Yeah, yeah.

**Other:** A lot of that data lives at the inference provider layer, and it kind of feels like it's better packaged there. So, like, that's where I'm saying, like, I don't know, like, it. To me, I struggle to see. Like, I think this could become potentially part of, like, glass or something like that. But, like, as its own. I struggle a little bit there. Right. I wonder what the web three layer is. If there is a web three layer to this.

**Me:** There honestly wouldn't be. I was just thinking like sort of just like just super standalone product type thing.

**Other:** So if it's standalone, like, if this is outside of, say, I'm assuming, just your own personal shit, right?

**Me:** Yeah, I brought it up with Cody a couple times, but, yeah, I don't think there's anything.

**Other:** Yeah, yeah. So being very catalog, you know, whatever. This is not, say, related. It's probably better without crypto. Like, I think that, like, there are a lot of, you know, you should study Haze. You should study these companies that start off as evals. I think Braintree is the most successful by far. Or Brain Brain. Trust. Is the most successful by far. I want to send this to you. It's called braintrust.dev it's an observer. They basically call themselves AI observability. And, like, effectively, that includes okay. Like, okay when it, like, fucks up or the actual model screws up, but also that's. Eval is because, like, you collect data on, like, its outputs, like an agent outputting something. And then like, oh, like this was incorrect or not. And then I can run those traces again when I train the model. Right? So I sent a bunch of those companies. I just. A lot of that is being packaged into the inference. Layer. And Then also these MLOps companies are packaging that altogether with like a sort of datadog like system where they like, they, oh, this is incorrect or correct. Right. So I'm noticing that, like, it's, it's struggling to exist as an independent product. But as inference or with mlops, I think it has tended to work, but I could sense a more. Definitely study those and, like, you know, more ideas here. Yeah.

**Me:** Yeah. Total. Ly. You've heard of Patronus, right? Like glider?

**Other:** I know the founder, Rebecca. Yeah, yeah.

**Me:** Oh, I know the other founder, bro. He's a.

**Other:** Oh, he went to Uchicago, right? Indian guy, something Kartikan or something like that.

**Me:** I'm forgetting. Blankie on his name now, bro.

**Other:** Yeah. His name is anand.

**Me:** Yeah, yeah.

**Other:** Yeah. Uchicago Indian guy. So I. I knew Rebecca from New York. I don't know her super well, but, like, she was in, like, the reading group together. Yeah, they're doing okay. I think they raise an A pretty successfully.

**Me:** Yeah, they did. They did. Yeah.

**Other:** Yeah. After that, they're kind of struggling, and so they. They thought about doing things like, oh, we'll train, like an eval model that's better than other. Like, they kind of struggle, and I think they're struggling to figure out what that next step is, but to where they've got it. And it's like. It's impressive, I guess.

**Me:** Yeah. For sure. For sure. So, okay, so like, like, kind of like the. The high level overview. And dude, you honestly know more about the suite than me? And honestly, I'd love to learn. Like, that's my next question for you. Is like, dude, what is like sort of from ground level to like, actual model deployment? What? Does that MLOPS pipeline look like? But before that, right? Like, I think like sort of the high level thought here was like, okay, you have the patronuses of the world. You have like the mercourt world, right?

**Other:** Yes.

**Me:** But no company does both of these in, like, one go. And maybe there's a reason for that. Right? Like, I'm still continuing my research.

**Other:** Oh, I. I hear you. Why is mercourt not so? I.

**Me:** Record does eval actually for, like, super high touchpoint customers, but, like, it's an extremely manual process, which is why I think they avoided for small to medium businesses.

**Other:** That's why I think the thing is. Right. I think the big thing is that candidly, if you look at companies like Drada, which is where my brother works at, or what is it? Vanta Top two company. A lot of them aren't actually. You like, making use of the custom data. So, like, I think there is, like, some sort of, like, prompting thing where it's like, hey, this failed here, so we'll prompt it again. But candidly, a lot of these guys are, like, noticing that, like the next generation of model with just some basic prompting. Solves it over investing a ton of money in, like, a very robust data collection eval pipeline. And so the only players that really need it are the top agentic companies, which are like Carvi, AI, Cognition.

**Me:** Yeah. They're already being addressed.

**Other:** Yeah. And, like, the normal players are not there yet. They'll get there, but, like, they're not there yet. And so it's kind of putting the cart before the horse.

**Me:** Bro. Makes sense. Makes sense. And what is this mlops pipeline look like? I've kind of, like, done some research reading on.

**Other:** A little volume and like, so definitely take a look at volume. Like, they're not. I don't know that they're even the top in MLAPs, but, like, take a look at there. I think ML Ops goes from everywhere of like, one, you know, again, Frontier Labs do this more, but, like, you train the model and so you have, like, a checkpointing layer for, like. Being able to take snapshots of your model weights and deploy them really easily. Ok, so you have deployment. You're monitoring of, like, deployment and whatnot and like, literally load balancing on, like, the serving layer of like, oh, like this goes to a specific instance and how do you serve it? Okay, so serving is a part of that, then you have, like. You have, like, error checking, etc. On that serving. Batching of that serving. Like, there's all these, like, things. And then I think where it gets more interesting is, like, what you're mentioning, where you have, like, a sentry for AI, where, you know, it's literally like, oh, like, we have guardrails. Like, so there's guardrails, right? Where you're like, oh, this, this produced content that's inappropriate or produced content that's, like, against our policies. And you have collection of data where it's like, immediately, no matter what it, it will flow directly into a database that, like, your engineers can easily pull and, like, view and then analytics. Right. Which is like, okay, like, what percentage of these, like, solve the customer needs or not? So it's like that whole ops pipeline, I think, is getting built. Like, I think the analytics layer is also interesting. Like, there are companies that. Are, like, you know, like, okay, like, we'll. We'll feed. If you have, like, an agent that gets deployed, or, like, a customer service bot will feed that directly into, like, this, like, database that gets populated. And then you can. You know, they're like pre. There are other lms that they're run. To say, was this conversation good or not? And then you analytics on saying, like, okay, like, what percentage of customers, like, were satisfied with their results and whatnot? Right? So I think it's like the model serving the model distribution, you know, the sort of, like, collection of data and, like, potential, like, analytics around that. That I think, is ML Ops layer. Not necessarily, like, the fine grain on like. Like data handling, because that's only something that customers really do, right?

**Me:** Facts, bro. Facts, dude.

**Other:** Is this is helpful for you.

**Me:** Super valuable. What's that? Absolutely, bro. This is extreme. Yeah. Valuable. No. 100%. Like, I'm trying to do as many, like, calls like this as possible to just, like, kind of, like, validate or devalidate the product, and it's not 100% extremely useful. Where do you think they're like? Are there, like, any. Holes that you think there are and like, sort of the eval pipeline or even like MLOps pipeline that are unaddressed.

**Other:** Okay? I. I think the biggest hole, the most exciting thing for me is that. Okay, I candidly think fine tuning is a meme originally. Because it takes three months to be able to really get. Or like a month or two to really get a good fine tune. And by that time, Your companies can already see a new model that comes out and you just prompted. So I think what potentially could change one avenue that's interesting is rl Fine tuning is definitely interesting. Like learning fine tuning. I think the tooling and stuff around that, like building a gym, building in a hub for every company is where companies have. Like, there's these three OpenAI kids who started their new company. I forget what it's called, but, like.

**Me:** Fact. Compute, bro. One of the guys I used to carpool with, he went to my high school, actually.

**Other:** No, bro. Literally. Those motherfuckers are literally just doing, like, FDE for RL for enterprises, right? Like, that's like, their whole business. And so with that, when I hear that, I'm like, okay. You know, if you have FDEs being deployed. It's going to slowly also start getting automated, like that pipeline. So I would take a look at that, like RL fine tuning and like, where in that cycle you could sort of automate.

**Me:** Yeah.

**Other:** And like, candidly, this is separate from an incubations from, say. Right. Is it just your own, like, side project or are you.

**Me:** Yeah. Yeah. I'm just, like, trying to see if there's, like, any interesting or, like, worth pursuing, but, yeah.

**Other:** Yeah, yeah, yeah. So I. I would say, like, yeah, you know, again, throw crypto where it's necessary, not where, like, for no need, right?

**Me:** Y. Eah. Yeah. I don't think it's. Yeah, it's all relevant. Yeah. For. For this shit.

**Other:** I'll send you some stuff around Rl520. I mean, the OpenAI basic doc is there, but like there's so many more companies and it's like it's still a little early. The point is that, like, you know, people are doing FE style stuff for that, so there's a lot of demand. I think the other thing is look at brain trust on the observability. So observability and RL fine tuning are two places where I'd be like, oh, take a look at and they'll give you a good picture of like where people's pain points are, etc.

**Me:** Nice, bro. Okay? Right on, right on.

**Other:** Awesome. I got a hot man, but, like.

**Me:** Yeah. No, dude, I appreciate you, bro. This has been, like, one of the most helpful conversations for this idea. So appreciate you, man. 100. Cool.

**Other:** Whatever.

**Me:** Man. Peace out. See you.
