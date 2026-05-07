---
source: granola
workspace: mosaic
ingested_at: '2026-05-07T04:23:57.244510Z'
ingest_version: 1
content_hash: blake3:525c50756b6fd5864d7f69ef67765d13ea1557311e3b169c413e3de10db0a58b
provider_modified_at: '2026-05-05T12:09:07.168Z'
account: adithya@outerscope.xyz
account_slug: adithya-outerscope
document_id: 7040b6d7-eb4b-4cc4-8f64-9513bb29a8a4
document_id_short: 7040b6d7
title: Siddarth Sridhar / Adithya Kumar - 30min Meeting
created_at: '2026-01-06T19:01:14.076Z'
updated_at: '2026-05-05T12:09:07.168Z'
folders:
- id: 91a78f08-eb95-45f7-ac10-8cb0ec3c45b4
  title: MOSAIC
creator:
  name: Adithya
  email: adithya@outerscope.xyz
attendees:
- name: null
  email: sid@bima.money
calendar_event:
  title: Siddarth Sridhar / Adithya Kumar - 30min Meeting
  start: '2026-01-06T13:00:00-06:00'
  end: '2026-01-06T13:30:00-06:00'
  url: https://www.google.com/calendar/event?eid=N2QyMWJmZDQ3ZWY0NDU3MTlmOWMxZWYzMzFhODYxNTIgYWRpdGh5YUBvdXRlcnNjb3BlLnh5eg
  conferencing_url: https://meet.google.com/hbx-afnc-fma
  conferencing_type: Google Meet
transcript_segment_count: 119
duration_ms: 893280
valid_meeting: true
was_trashed: null
routed_by:
- workspace: mosaic
  rule: folder:MOSAIC
---

# Siddarth Sridhar / Adithya Kumar - 30min Meeting

> 2026-01-06T19:01:14.076Z · duration 14m 53s · 2 attendees

## Attendees

- **Adithya** (creator) <adithya@outerscope.xyz>
- <sid@bima.money>

## Calendar Event

- Title: Siddarth Sridhar / Adithya Kumar - 30min Meeting
- Start: 2026-01-06T13:00:00-06:00
- End: 2026-01-06T13:30:00-06:00
- URL: https://www.google.com/calendar/event?eid=N2QyMWJmZDQ3ZWY0NDU3MTlmOWMxZWYzMzFhODYxNTIgYWRpdGh5YUBvdXRlcnNjb3BlLnh5eg
- Conferencing: Google Meet https://meet.google.com/hbx-afnc-fma

## AI Notes

### Product Overview: Domain-Specific LLM Evaluation Platform

- Core problem: Current LLM evaluations are vibe checks using generic models like GPT-4 as judges
- Solution: Verticalized judge models + realistic domain simulations (“gyms”)

    - Deterministic verifiers (compilers, solvers, system checks)
    - Multi-agent debate tribunal for subjective edge cases
    - Human expert escalation for hardest cases only
- Output: Audit-grade evidence + counterexample traces showing exactly why/when/what broke

    - Example: Agent sums 2+3 correctly but puts result in wrong cell

### Target Market & Customer Base

- Primary customers: Companies building LLM agents (excluding Tier 1/2 labs with internal eval budgets)
- Growing market of small language model (SLM) developers

    - SMBs developing fine-tuned models for internal operations
    - IT shops streamlining databases/workflows
    - Finance/healthcare/legal where single mistakes = regulatory liability
- Positioning as essential MLOps component, not optional tooling

### Product Architecture & UX

- SaaS model with online dashboard
- Integration flow:

    1. Customer plugs API endpoint from internal model
    2. Selects verticalized judge (e.g., finance model for XBRL checks)
    3. Pay per API call licensing fee
- Platform feeds various prompts to customer’s LLM, scores outputs via specialized judges
- All testing runs in customer’s environment with API key access

### Business Development Strategy

- Partnership approach: Bundle with existing LLM development tools rather than standalone sale
- Sid offering free engineering support (Naveen) for MVP development
- Core differentiation: Verticalized models vs competitors using generic GPT-4 front-ends
- Two identified competitors, both lacking domain specialization

### Next Steps & Funding Plans

- MVP development with university PhD students (needs salary funding)
- Target February-March fundraising window (markets improving post-election)
- Requirements before serious pitches (2 weeks out):

    1. LOI commitments from potential customers
    2. Tangible partner POCs
    3. CoreWeave CPO as potential advisor
- PRD being prepared by AI head from Story Protocol

## Transcript

**Me:** Yo, what up, Sid? How's it going, bro?

**Other:** Hey, how's it going, Adi?

**Me:** Chilling. Chilling. Man, you back?

**Other:** Good. Yeah, I know, dude. Last month I was traveling a lot and I felt sick. But I wanted to chat with you because I know you wanted to chat about something quickly, so better late than never.

**Me:** Yeah, yeah, yeah. No stress, man. No stress. Ideas developed a ton to sauna series. Good to take some time and ideate on it.

**Other:** Yeah.

**Me:** You're in new jersey or what?

**Other:** Yes.

**Me:** Fire. Fire, fire, man. I'll be up in New York, I think, sometime in March or some shit, so I'll definitely. 100%.

**Other:** Okay, I'll be here. Yes, Tell me what's up. I mean, what is this idea?

**Me:** Yeah, dude. So basically the issue right now. Have you ever done a model eval by any chance?

**Other:** Like. Like Jupiter Notebook or something or what?

**Me:** Yeah, yeah, yeah. Just like anything, like evaluating any model, pretty much.

**Other:** Yeah, yeah, yeah, of course.

**Me:** So. So, like, then you might, like, sort of like, efface this before, right? Where you have sort of like. Have you ever evaluated an LLM?

**Other:** Never an LLM. No.

**Me:** Okay. Okay. So right now, right, like, the issue with sort of evals with LLMs is that there's like, eight. Like, no sort of verticalized judge model. Like, the way LLMs are trained right now is they use AI to train AI, and right now, it's more of a vibe check than anything there's. Nothing where it's, like, concrete about, you know. Okay, this is exactly where it's sort of an LLM went wrong. Right? This is exactly like, sort of why it's breaking in certain cases. Right? Type thing. And so in general, like, as AI agents are moving from chat to taking actions also inside finance, healthcare and legal workflows where, like, a single mistake becomes regulatory, like liability or brand damage. Right? Like, it becomes increasingly important that these, like, models don't hallucinate. Right. But today's evals, like I mentioned, are either, like vibe checks, right? They're basically LLMs at judges. So think, like, using a smaller model like GPT4.0 to train your LLM and sort of evaluate its performance. Right. Or, you know, sort of benchmark contamination as well. Or you also have the records of the world where you have like, expensive human review that really doesn't scale, like to like a massive scale without a shit. Ton of money. And so essentially the idea is as follows, right? You solve this by kind of testing agents in these domain specific gyms, right? So like realistic simulations, essentially, of what the model would do in real life and score them with, like, deterministic verifiers. So these are like compilers, solvers, right? System of record checks pretty much. And, and so let's assume that the agent hallucinates or something is like still wrong in the gym. You then add on a tribunal. Right. Sort of a multi agent debate for subjective calls. Right. So these are non deterministic checks. Right. Where like you only. And, and from these. Subset, Right. Like you only route the hardest cases, the edge cases. That sort of a multi agent debate model can't sort of evaluate properly to a case of experts. Right? So subject matter experts. So the output isn't really just a score, it's like audit grade evidence plus what's known as counterexample. Traces, right? So, for example, if I'm getting a model to add a two and a three and put it in a five, but it puts in a four. Well, a counterexample trace would. Would provide that logs, right? So the system logs and be like, hey, like the agent summed a 2 and. A 3 properly, but misread it in the wrong cell. So it tells you why it broke, when it broke, and what broke specifically. Right? Whereas traditional.

**Other:** Right. There's, like, debugging for LLM development.

**Me:** Exactly, bro. And it's also verticalized debugging as well. Right? So like, think like, sort of like. So if you have a generic model, not only is it more expensive and less effective, but you are training based on latent memory within a company. You're building company specific vertical edge judges and company specific Eval is pretty much.

**Other:** Nice.

**Me:** But yes.

**Other:** Have you been working with SLMs more often?

**Me:** Slm is. What are those, dude? Not familiar.

**Other:** Just like small language models, not large language models. It's basically like a lot of people are kind of like doing it for their own in house development, so they don't need to use ChatGPT.

**Me:** Exactly.

**Other:** It's much more efficient, lightweight, stuff like that. So, like, who's the customer for something like this, right? Like, if they were going to do some of this audit, is it just like. I think SLM developers would love to use something like this. Right? So what's the customer for this? Developers of these language. Models.

**Me:** Yeah, so. So, exactly. Right, so, like, basically, like, if you take an LLM and you're fine tuning it and turning it into some form of agent, right? Like, literally anybody that's building an agent right now would kind of be a. That's, that's not like a major, like, tier, you know, tier. One or tier two lab. Right. That has the budget to do evals internally. They would kind of turn to this. You're essentially getting evals at the cost of software with, like, a human.

**Other:** Interesting. Yeah, I really think that's interesting. Did you, like. Did you build this yet? Is this something that's developed or what's the, like, stage of this?

**Me:** Yeah. So building this with, like, my next door neighbor is actually the head of AI at, like, Story. Dude, he's like a UT PhD, like, advisor. And whatnot. So that, like, works out perfectly. I brought him on.

**Other:** Oh, wow. Story as in story protocol.

**Me:** Yeah, yeah, yeah, yeah.

**Other:** The one. The guy rugged.

**Me:** Yeah. Yeah. They got, like, this guy's background is a pretty killer. Like, so I'm, like, bringing him on as, like, potential.

**Other:** Nice. Yeah. I mean, pedigree is needed in this kind of shift in. That's great. So you're going to develop it with him?

**Me:** Yeah, yeah. So he. He's like recruiting a couple of his students to help build it out. That's like stage right now, dude. Where? In development. But like, I got to pay these guys salaries, so that's why I'm trying to raise. But like, I want to get your thoughts on, like. Okay, like. How do I position this as a better. Obviously, this is kind of like a stream of consciousness pitch. Like, I'll tighten it up, like on.

**Other:** First. 20. Free work. Okay? Yeah, I know, I know. Right? No, I understand this completely, and I really like this. I think if you make the case of, like, why ordinary people are going to get into language model development. Small businesses are going to start developing their own models. And why it's going to be necessary to fine tune those models like all they would need. Like. Like your your basically pitching a necessity to language model developers.

**Me:** Right. It's part of their ML ops. Adithya, like we're automating.

**Other:** Yeah, exactly. Right, right, right, right. It's actually going to be very imperative a part of the mlops. So where would this run? Is this just going to run on their terminal? It's going to run in the Jupyter notebook and a package that they have to install API that they need to query. What is the actual, like, method of like, flow. Like, what's the UX for the developer?

**Me:** Yeah, yeah, yeah, Great question. So essentially, right, it's like a SaaS model, right? You'd basically pay like a subscription fee for access to certain verticalized models. Or if it's a higher touch point service, I'll give you the UX first and pricing second, I guess. So UX like you just have an online dashboard that you log into, you plug in sort of an API endpoint that's exposed from your internal model, right? Then you select one of our vertical as judge model. Let's say like you're like a finance Excel automation platform, right? And we have like sort of a finance model that's like or verticalized judge that's fine tuned for like xrbl, right? Like system of record checks, right. Type thing. Well, then you'd select that and then pay a licensing fee per call, right? Like so per API call to like our verticalized judge. The judge would then evaluate outputs of your LLM. Model by feeding it in like various prompts and then like performing either deterministic or non deterministic checks based on the action taken. So it'd basically be like an online interface that like, you would just like plug your API key into see a variety of outputs and see this variety of outputs scored via our verticalized judge model. Let's assume.

**Other:** So you're. You would import your LLM to the actual software that you would develop, you would get an API key or license, and then you would basically do all your testing in your environment, basically.

**Me:** Exactly. Yeah. Yeah. It's like, exactly, yeah.

**Other:** Nice. Nice. Yeah. This is really. I. I really like the idea. I think it's a really solid idea. I think it's going to be really, really important that people are going to start needing to do this, I think. For your pitch if you just kind of make it. I mean, honestly, the. I understood your stream of consciousness pitch. Like, I understood that in the first, like. Like 12 seconds, right after you kind of described the actual product. I think when you're pitching this, if you could just kind of emphasize how there's a wave of people that are going to build their own language models just to avoid LLMs, just to, you know, fine tune their own data and keep it in their own silos. I think that's the pitch, right? I think people who are going to be like, what do you want to call the SMBs of LLMs, right? Like people who are going to develop their own fine tuned models.

**Me:** Great.

**Other:** For their own day to day work for their own business. Right. Like it could be regular, let's say, you know, like to describe it, like it'd be an IT development shop. That is trying to streamline its own databases and consciousness for internal operations. Or, you know, I would just figure out and kind of do some customer research on what kind of users are there. But, I mean, that's just a pitch deck stuff. That's just semantics. I understand this completely.

**Me:** Yeah. Okay. Fire, dude, fire. Fire. Yeah, dude, what do you think next steps would even look like, right? Like, theoretically. What I'm trying to do is, like, I'm. I have, like, a convo, like a couple convos with, like, a couple of VTs this week, right? Just, like, show them, like, sort of current progress, team traction, all that shit. I got on, like, the CPO of, like, core weave or, like, I'm still trying to sign them on, but, like, I'm working with them directly right now, so I'm trying to, like, see if he'll come on as, like, an advisor, which would greatly help. Like, sort of the sell. Right type. Thing. I'm trying to think, like, do we need, like, some form of, like, MVP to kind of demonstrate in these meetings?

**Other:** Okay? Yeah. I would get an mvp. I can also lease my engineer, like for free. By the way, like my engineer, I'm more than happy to offer his time.

**Me:** Five.

**Other:** To, you know, just help build this. Seems like a very interesting thing that we can at least contribute, at least for the development of the mvp, if you know what to build and how to build it. You know, Naveen, he can help out with this stuff.

**Me:** Y.

**Other:** So.

**Me:** Like, designer guy, right, or some.

**Other:** My engineer. Yeah, yeah, yeah. He can help with this stuff. A lot of the development work that we have right now is very, very streamlined and easy for him. I think this is a very nice project that if you could engage on, I think it can help you out a lot and do you a favor. I think that would be the best way we could get the MVP there. And then I would actually figure out how you would package this. Like, what distributed channel would you sell this through? Right. I think the best way this would work is actually as a bundle. With another product. Right? So, like, hey, you know, what are the top LLM development tools? That exist out there and basically kind of figure out how you can kind of bundle your product with the other product, you know, Instead of like Microsoft360, you know, like a bundle of products. So when you purchase for the LLM development, like, basically like, find what do businesses use to develop their own SLMs and LLMs. And then I would, for, I guess, your sake of bd Try and see if you could get some sort of. Some sort of partnership going with them, you know?

**Me:** Factual, dude. Yeah, factual.

**Other:** That's. I mean, it on the business side, but yeah, I mean, listen, like, once you need help on the mvp, like. I will. Let. Let me know once you need help with that. I'll ping Naveen. I'll tell him to help you out on that. And then, you know, should pump at least something. At least, you know, some. Some MVP out, you know?

**Me:** Yeah. Okay. Fire, dude, fire. Yeah. I'm like, okay. And, like, how do you, how would you approach fundraising? Right. I'm thinking I probably need not only, like, a couple LOI commits, but, like, also, like, tangible partners that we built out POCs for. Right. Because I've heard, like, multiple people now that, like, the, like, AI sort of fundraising sort of climate has greatly died down, and it's, like, much harder to race now. So I feel like you need something more tangible. But what have you seen, I guess, like, in your networks?

**Other:** Yeah. I mean, I think raising is just going to pick back up after I mean, I think the climate for raising, to be honest with you, is going to start picking back up because Trump captured Maduro. And, like, the markets are doing pretty well. So February is probably your best time to start raising. I, I think it's going to pick up. So I, I wouldn't worry about what it looks like right now. I would worry more about how it's going to look, you know, like the product. So, yeah, I mean, listen, get an loi, an mvp, and you'll be far ahead. And then you'll be able to kind of start scaling this to, you know, heaven, you know?

**Me:** Right.

**Other:** Yeah.

**Me:** Facts. Okay?

**Other:** So I. I think you'll be fine. I think the only thing for, like, AI VCs are they are severely, like, you know, like, burnt out by stuff. Right. Are there any competitors for this product? I. I'm not really in the AI Space, you know, but are there any competitors for this product?

**Me:** Yeah, dude, I've done, like, a pretty thorough competitor landscape, like, competitor landscape research or whatever. And I found like two primary competitors that are also focusing on model evals. The thing is, both of them are not focusing on sort of verticalized models, right? So they're still using generic models like GPT 4.0 and merely just providing like a front end user experience. Better you.

**Other:** Okay, so you're basically doing this for, like, whole development lifecycle, so that's, I think, the way you can differentiate. I really like the product. You know, it makes sense to me as someone who's like, I consume AI on a huge basis on a daily, daily basis. So it makes sense to me. So, yeah, aibc, I think would ape in and this. I just need to, you know, just get your ducks in a row. Right? I think you'll be fine. But what are you kind of looking for? For in terms of investors? Like, I know you're having a few conversations. Here and there.

**Me:** Really? Once, bro, because I just want to get, like, a couple reps in, right? Type thing to, like, tighten up the pitch. All that I'm on, like, the finishing touches of, like, putting together a deck for this that, like, I have to present later today.

**Other:** Right, right, right, right.

**Me:** But yeah, I mean, these are just like reps. Like, I think the serious pitches will probably happen like two weeks from now. Ish. Red type thing. Once there's something more tangible to talk about on, like the go to market front. And like, on this front. Right. Like, type thing, product front. But. Yeah, I mean, I. I think it's pretty obvious next steps. It's just like. I just don't know, like, how to approach the raise, like, especially in, like, sort of. I mean, but if you say, like, I guess you're saying that you think, like, races are going to pick back up in. February.

**Other:** Yeah, I mean, I think especially with just, like, what's going on with, like, Venezuela shit. I actually think that it's actually going to increase and improve the like anytime public markets. Are doing well. There'll be a 60 to 30 to 60 day delay in private markets. So I would absolutely think that February March is going to be a pretty good time for fundraising.

**Me:** Y. Cool, cool, cool, cool. Easy, bro. Okay, dude, Sounds good. I'll. I'll stay in touch. Like, I have, like, a. Like, PRD being put together by Sid. Like, the neighbor guy. So before that to you.

**Other:** Nice. Yeah. Listen, just ping me whenever you need help on building this stuff. I'll get Naveen. You know. You know, just set up with you, and then, you know, whatever you need for development.

**Me:** Yeah, perfect, bro, perfect.

**Other:** Boom, dude. Good luck. I think this is a great idea. Let me know how I can continue to assist.

**Me:** Easy, bro. Easy. All right, man. Appreciate your time.

**Other:** Take care. See you soon. Bye. Bye.

**Me:** Peace out. Stay t. Uned.
