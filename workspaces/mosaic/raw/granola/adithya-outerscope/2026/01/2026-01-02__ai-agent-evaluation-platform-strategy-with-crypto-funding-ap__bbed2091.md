---
source: granola
workspace: mosaic
ingested_at: '2026-05-07T04:23:57.244510Z'
ingest_version: 1
content_hash: blake3:a9170db79d89fd27db9e999178ff09ada95ecada5ebf6fb2688e39067da449c1
provider_modified_at: '2026-01-02T18:53:03.785Z'
account: adithya@outerscope.xyz
account_slug: adithya-outerscope
document_id: bbed2091-73a1-4fc0-8369-cefad7e3f150
document_id_short: bbed2091
title: AI agent evaluation platform strategy with crypto funding approach
created_at: '2026-01-02T18:26:51.715Z'
updated_at: '2026-01-02T18:53:03.785Z'
folders:
- id: 91a78f08-eb95-45f7-ac10-8cb0ec3c45b4
  title: MOSAIC
- id: 2ace9cb8-854d-4638-9adb-ba6455b0eeb5
  title: SYNAPSE
creator:
  name: Adithya
  email: adithya@outerscope.xyz
attendees: []
calendar_event: null
transcript_segment_count: 197
duration_ms: 1550470
valid_meeting: true
was_trashed: null
routed_by:
- workspace: mosaic
  rule: folder:MOSAIC
---

# AI agent evaluation platform strategy with crypto funding approach

> 2026-01-02T18:26:51.715Z · duration 25m 50s · 1 attendees

## Attendees

- **Adithya** (creator) <adithya@outerscope.xyz>

## AI Notes

### AI Agent Evaluation Platform

- Core concept: Verticalized agent gym + evaluation system

    - Replaces current GPT-4-based agent evaluation (inefficient, expensive)
    - Creates agent gym where models practice specific tasks with company data
    - Provides “counterexample traces” - exact breakdown of where agents fail
- Example: Finance agent sums A2+A3 but puts result in A5 instead of A4

    - Current tools show traces (what happened) but not failure points
    - Platform identifies precise error location and cause
- Multi-agent tribunal for subjective evaluations (15-20% more accurate)

    - Advocate agent, critic agent, judge agent iterate to consensus
    - Falls back to subject matter experts only when needed (cost control)
- Verticalized judge models built from training data per industry

    - Creates switching costs and defensible moats
    - Much cheaper than GPT-4 with higher quality outputs

### Go-to-Market Strategy

- Target verticals: Financial services (highest risk, need rigorous evaluation)

    - Design partner prospects: Friend at BlackRock model evals, Anti Metal CTO
    - Neighbor: Head of AI at Story Protocol (Stanford PhD connections)
- Key introductions needed:

    - Surojit (Ema founder, ex-Coinbase/Hash3) - strong investment board
    - Cursor head of growth connection for coding platform partnerships
- Validation progress: Anti Metal CTO initially skeptical, now interested after pivoting to agent gyms

### Funding & Next Steps

- Crypto route recommended over traditional VC

    - 2-3 month timeline vs 6-12 months for traditional raise
    - Target $15-20M to hire top PhD talent afterward
    - Token mechanics: Compensate ground truth contributors, agent marketplace
- Immediate actions:

    1. Create advisor list (all potential connections)
    2. Develop crypto + non-crypto deck versions
    3. Set up shared drive with all materials
    4. Schedule bi-weekly Monday/Thursday check-ins (11am CST/10:30pm India)
- Focus: Solve for capital first, avoid over-engineering

    - V1 should be manual/human-powered like early [Otter.ai](http://Otter.ai)
    - Build narrative for fundraising, hire technical talent after raise

---

Chat with meeting transcript: [https://notes.granola.ai/t/f8f13af7-8f12-4827-8221-a7de563e7250](https://notes.granola.ai/t/f8f13af7-8f12-4827-8221-a7de563e7250)

## Transcript

**Other:** Yad. Go ahead. Also my daughter is sitting next to me so we need non nsf to nsfw language.

**Me:** So basically, what you need to build, right, is essentially something that improves agent velocity and time to shipping speed. Right. So how do you do this? You build the tools and pickaxes in an agent gold mine rush, right? And so what this looks like in a defensible claim after doing a ton of competitor research and product research, is two things. One is a verticalized agent gym, essentially an area where you can get an agent to leverage tools to reproduce certain actions, right type thing. The issue with current evaluation tools is basically, you're building verticalized judge models to also evaluate products. So right now, the process for training an agent is an AI agent will review the output of another agent. Right. Type thing. So you're using GPT4.0 to classify and vibe check the output of an LLM right? And check whether an LLM is hallucinating by kind of like testing it with various prompts and then using GPT4 in order to evaluate the prompt output from the model. This is a very foolish process because again, you're not understanding properly where an agent is necessarily breaking. You can replay that exact sort of issue. And so how can you build a system to do this? You can build what's known as an agent gym. There exist open source tools that will allow us to actually feasibly build this. I'm like, also ensuring that all this is technically feasible. Namely, databricks actually has like a tool set that where you can actually build sort of agent gyms yourself. So then you might ask, okay, where's the mode? What are you doing new? What we're doing is actually integrating sort of a company's native data into sort of this agent gym that allows the agent to actually reproduce sort of vulnerabilities. With the large language model specific to that sort of vendor or customer or whatever you're partnering with. I'll give you a very specific example, right? Like, let's assume you're, like, partnering with a company that's automating Excel tasks, for example. So the agent gem for that would look very specific, right? Like, okay, it's like a finance agent gym. You have very concrete sort of tests that you'd want the agent to output. For example, if you're like wanting to edit, okay, the agent needs to some sells a 2 and a 3 and then place it in a 4. But the. Agent sums a 2 and a 3, but place it in a 5, right? Then you exactly know what went wrong. Now, current tools actually are unable to do what is known as. They're able to do what's known as traces, essentially logs where they know what the agent's doing step by step, but they're unable to determine where the agent breaks. Right. So what we're going to provide, step beyond that, is known as a counterexample trace. Right. This is what I'm calling it. Basically sort of an example where you're able to not only say, hey, the agent wrote. The agent broke because it wrote. And sell A five. But the agent's exact step right? So was found correct, but the agent broke because it wrote in cell A5 rather than A4. So having that level of intelligence not only allows you to train an RL model much more efficiently at much lower costs, but also having a specialized model is much better because it allows you to provide these counterexample traces. The only way to do this is by actually partnering with the company directly. And eventually we'll also create verticalized judge models based off of all the previous training data that we have. So we're continuously developing a mode, we're developing switching costs for vendors so that people have to stay with us as a product. And that's our defensible mode as well. And so once we have enough finance companies, for example, that we partner with, we can create a finance specific vertical judge mode or judge. Right? And essentially that is much, not only much cheaper than GPT. 4. It provides much more quality sort of training data and retraining data. The other thing is, we'll also partner with these companies in order to allow for them to collect ground truth with subject matter experts in our network. So we'll basically partner, at least initially for the first zero to six months. We'll partner with the next journal company in order to collect some of this ground truth. But once we have enough funding ourselves, we can then hire subject matter experts. And what I mean by ground truth is what will an agent perform in an idealistic scenario? And so in this case, the ground truth would be. Hey, you have a manual guide, like a subject matter expert, a business analyst, go in and manually perform the actions, right? So some a2 and a3 and put it in a5. That's an example of a ground truth, right? It's an idealistic sort of output, and it's the golden output, right, that you'd want an agent to do. This is a very simplified example, but you can see how this would extrapolate to other examples. And so that's essentially the idea in a nutshell. So after you have sort of the agent gyms and whatnot, where the agent can continuously train itself, you then want to evaluate it. Right. So model evaluations are also very manual and tedious to do right now. I've talked to a couple CTOs at, like, a couple model companies such as Anti Metal and a couple others in New York, and all of them have said the same thing. It's like, it's very tough to find what an evaluation would look like, but it's extremely product specific, so the company does need to do that. The part the company doesn't need to do is collect data and actually manually even retrain and perform like RL learning on some of these models. So what does that look like from our end and what does the product look like? Essentially, you now have access to the complete log set for what the agent has done in this sort of agent gym. Right. Then you pass that off to a multi agent tribunal model. This has proven historically to have on average 15 to 20% more evaluation for accuracy for non deterministic tasks. The task I gave you is deterministic, but let's say it's a voice AI, for example, and you need sort of ranking. I'm like, oh, how well did this chat agent perform? Right? That's a very subjective matter. You can't really perform a deterministic check or code a deterministic check to do that. So then you have a series of agents, and this is proven literally by research papers. Right? So one agent actually advocates for the model, one agent is a criticizer model, and one agent also accessed the final judge model. Right. And so these guys go in a series of n number of steps. Until they either come up with sort of an objective metric that you can evaluate the agent using. So let's say it's like, okay, 80% for this chat agent, 80% on helpfulness, 75% on accuracy. Like company level accuracy. Like, unlike what information provided. You get my point, right? So it's Basically, you're taking non deterministic actions and creating deterministic metrics based on that. And so then let's assume after n number of steps, these agents still can't come to a consensus on what to actually rank, what metrics to rank and how to rank them, what percentage the agent actually fulfilled. Only then will we tap on our subject matter experts. Why is this? Because subject matter experts are extremely expensive. And that's what Mercourt is like doing right now. Right? They're just burning cash Left and right. $2 million a day they're paying out. Just a subject matter experts. That's extremely. Foolish. Right. Because in the case of model evaluation, you want to lower the cost ultimately, if a model company. And so that's essentially what we're providing. We're providing high touch points, sort of manual auditing and evaluation, but a fraction of the cost at a cost of just automated software. We can't. Evaluate the entire process for evaluations. Because that's foolish. Like, you're not going to get quality outputs. Right. And that's foolish to think. But what we can do is minimize the human level of intervention needed to train models using this process. So first you go from the gym, then you go to the tribunal. Model. And then only if you can't come to a consensus there, would you go and tap on a subject matter expert and be like, hey, rank this right? So, for example, this object matter and this chat example would be like, okay, a customer call agent, that is 10 years of experience with customer calls. OK? They go in. And then manually rank on these metrics type thing that will then inform our verticalized judge and our verticalized gym for chat agents, for example. And our verticalized judge would get retrained on the subject matter expert. So the ultimate goal here is subject matter experts, like evaluation of the model. So the ultimate goal here is to completely cut out the subject matter expert at the end and create a verticalized judge for that vertical. A judge model that is accurate enough to actually rank subjective sort of metrics as well on that. That's. Sorry, that's a very ranky pitch. I'm, like, trying to tighten it up, but. I just want to give you the thorough thoughts, everything. That's about it. Any questions I can help. I know that's, like, a ton of information to throw at you in once.

**Other:** Got it. Sounds interesting. After multiple verticals, or should we just pick one vertical?

**Me:** So after this call with you. Actually, I have, like, a call scheduled with this guy I'm working with. It say he used to be the CPO of Core Group, which is a big, big sort of AI company. This guy has connections left and right, so I'm just going to ask him transparently. It's like, bro, I'm kind of cooking up this idea on the side. I'd love for you to come on as an advisor and help us with our go to market motion. Initially based off of numbal group, we only have crypto type thing. That's the issue. So I've already talked to Aurora Network.

**Other:** One thing.

**Me:** Oh, shit. You're breaking up, uncle actually.

**Other:** Have you heard of code bins and Kaggle in these guys where programmers go against each other?

**Me:** It could be so.

**Other:** Kaggle is one where all these data engineers complete each of the KGL.

**Me:** Okay?

**Other:** One. And then there are these other platforms where programmers start. I'm wondering if this grammar is to sort of evaluate output for generic programming tasks on wipe coding platforms.

**Me:** Yeah.

**Other:** So let's say somebody building.

**Me:** Right? No, exactly. This is like, essentially what we do, right? It's like not only source the ground.

**Other:** So that's beyond crypto. That's beyond crypto admin. If you look at when you go to a gtm, beyond just crypto. From market perspective, incentivize using crypto. We might need to find one gtm that is should speak to surajit, the ema guy. And get a starts as well.

**Me:** Adiya. Who's that?

**Other:** This is the founders Ema. He is the co founder of hash3, the pharmacy PPF, Coinbase. He now has a startup called ema.

**Me:** Ema.

**Other:** Eme.

**Me:** And then what is it?

**Other:** Just type in ema space roji. That's urugat.

**Me:** So r I j t.

**Other:** S u r o g I t.

**Me:** Oh, sorry. Got it. Ema. Okay. Interesting. What is this guy doing? Also mit sloan. Nice. GDP when transforming every business with universal AI employees. Interesting. Yeah. I mean, this would be a great partner, dude. It's basically, wow, he has an insane investment board, bro. Oh, my God.

**Other:** So he's the guy who set up Hashtree with me.

**Me:** Oh, nice. Yeah, dude, I'd love to chat with him. Man, this would be an insane intro. Yeah.

**Other:** Exactly. So that's. That's the thing. So we need some partner to wed this with. My because my sense is a lot of these models is probably spending a lot of time. Like if you look at the Goldman's of the world. It is. A vendor saw the models. They're both trying to come with the same problem.

**Me:** Yeah.

**Other:** So how do we sort of be complementary to that rather than just go head on that? That's what I'm thinking.

**Me:** So even enough money, like, they're basically training one sort of universal model to automate mundane tasks, right? But what we're doing is, like, slightly different in that, like, we would be, like, they would be one of our golden partners, you know, like, the idea would be we're evaluating their model for them, right? And we're providing an agent gym in which they could, like, simulate sort of models and model outputs. But, yeah, you get it. You get it, But, I mean, yeah. Model outputs like before. Sort of like, you know, evaluating shit in the real world. Right. It's the idea.

**Other:** Understood? Understood. So who your fight dream? PTM partners.

**Me:** So. That's a really good question, man. I mean, I think I first have to pick the wedge, right? So I'm thinking, like, we'd probably want, like, high touch point, like legacy services. So I was thinking financial services, because that's probably where a bulk of our, like, connections would also be, right? Type thing. So for fintech.

**Other:** Right, right, right.

**Me:** My friend works on a lot and model evals at Blackrock. That would be an insane design partner. Right? So I've told him, like, I'll give him a, you know, a bit of equity if he closes them for us. He's like, talking to us, like, head of product type thing right now to. See if we can get a call with him then. I'm also working on Anti Metal. It's like an AWS deployment service. So I chatted with the cto and I'm, like, trying to design partner too. He's been, like, helping me, like, sort of refine the idea quite a bit. My next door neighbor here is actually the head of AI at Story Protocol. He's like a Stanford PhD advisor, so I'm sure he has, like, a bunch of kids that would be, like, down to maybe help build the idea itself. But design partners, like it's probably in the financial land, right? Because that's probably like the highest risk, right? Folks that want a general model evaluations for a fraction of the cost because they need to like, you know, evaluate a pretty rigorously. That's the idea.

**Other:** Okay? Okay?

**Me:** Yeah. So it's a. It's like kind of a skew of the initial idea. Initial idea was like, honestly, I think it's still defensible, dude, and we could probably do a token play on it. Honestly, like, if I. If I was really thinking about it, you'll probably still do a. Token play on it because data labeling is still a large problem. I'm just thinking there's a much more defensible claim to fame.

**Other:** Yeah.

**Me:** I think so. I'd love to. I'm like, you know, I think.

**Other:** Yeah. I think. There's a bit of lag. Please continue.

**Me:** Hilala. Sorry. Sorry. What were you about to say? I wasn't about to say anything else.

**Other:** Then we'll continue.

**Me:** Okay, okay. I'd love to talk with, you know, Sergeith, I guess, like, I mean, I think, you know, the more people I talk to, the more the problem is validated. So that's like kind of like what I'm going off of this guy, what do you call it, this thing, his name is Sai, he's. The CTO of Anti Metal. It's basically like an automated deployment to aws. He's currently working on model evaluations for his product, which is, like, perfect sort of stage for us to also join him. At. And he shitted on the idea. Like, dude, initially, like, it was like, he was like, bro, this is not really, like, the initial ideas I'm going to get, like. And he was like, bro, like, this is not defensible like, this and that. And then, like, I finally, like, eventually went to model evaluations. And then this thing. And finally, like, yesterday, I had a call with him where I was like, okay, like, verticalized judges and verticalized agent gyms where you can sort of replay agents actions. Sounds interesting. So hopefully that's, like, assigned to proceed with further. Like, I just want to do as much product validation and, like, customer discovery calls as possible initially. So if you have folks like this in your network, that'd be killer intros, I want to say. Uncle.

**Other:** So one thing you need to figure out is. Listen. I mean, it's all great. We can do old fashioned vc, but what we know very well is how to play the crypto game.

**Me:** Yeah.

**Other:** Let's be like xrp, right? I mean, you may or may not have a product, but get the narrative and save the directive. Crypto is the fastest way to raise 15, 20, 30 bucks. So don't. Also, don't shy away from that. Right? So that's also the place that I think we get maximum bang for the buck. So get all these. We get Surogi, we get this Sal, all these guys put up advisory board, get an elective going, get a date from finance and really pump it up. Do an impossible launch, 2, 3, 4 launches. Do a binance race.

**Me:** Yeah. Yeah. Yeah. Yeah.

**Other:** And that the token then trade. And we sort of pump up the narrative with, if you're 1530 in the bank, right? Then there will Runway for two, three years. Then we can do a traditional threes.

**Me:** Yeah.

**Other:** So don't mistake because.

**Me:** And I think, like, honestly,

**Other:** Yeah.

**Me:** Go for it. Go for.

**Other:** Traditional 6 months, 9 months, 12 month project. I mean the traditional VC race is very, very tough path as you've done it, if you've done it before, you'll know there is crypto still a 2 to 3 month race. The fastest way to raise 15, 20 bucks in 2 to 3 months is crypto.

**Me:** Yeah.

**Other:** So I would still say. I mean idealistic. Yes. Revenue. Etc, that's all face to face. One, we need 1520 in the bank. So understand the problem we're solving, right?

**Me:** Facts. Yeah. No, I don't disagree with you at all. I think, like, initially, if we do like a crypto based product, then pivot to something like this, because this is extremely tough to build out. Like, honestly, if you really look at the technical components, It's a non trivial thing to build out. You need, like, experienced guys.

**Other:** Yes.

**Me:** In order to raise for it, you know, type thing.

**Other:** That's what? That's what? Sentient. Right. Sentient. Grade 70, 80 million. Crypto. And then now they figure solving the problem.

**Me:** Yeah, yeah.

**Other:** OT is we pay as much money as we can in the next three, four, five months, and then we hire the best PST AIs in the world.

**Me:** Y. Eah.

**Other:** You use a Berkeley network. We go to mit, we go to Stanford. Right. And then we hire some PhD, sir. And then we spend two, three years building out the problem.

**Me:** Yeah.

**Other:** First solve for capital. So make the narrative as strong as possible. Get all these advices. I mean, depending on the conversation, either you index on crypto or you sort of underplay the crypto angle, right?

**Me:** Yeah.

**Other:** But, yeah, so that's. That's my.

**Me:** No, I agree with you. I don't want to like, you know, sort of think too to idealistically. Right. Type thing. You definitely have to be realistic with, like, where you can raise money and like, both of our networks lie in crypto type thing first. Right. So I'm not against that at all and. I think I can definitely work in a crypto angle to this, right? Where, like, oh, like, you get compensated for ground truth. Like. Or, like, you know, agents that you build will get. Right. Type. We could become a virtual but for, like, agent type thing. So that's. I.

**Other:** Guest. I mean, think about it, right? Let's say. Let's talk. Let's say I'm by coding something like a part of prediction market, right? So right now I go to Claude and say, okay, make me this turbo options market. Imagine. Now, I had on top of that, four other programmers who are advising me. And give me the best shot at what's the best output. Right? That's an ultimate agent gym. Right? That's Agent Plus. So you're bringing back the SME angle to what is our commoditized agent field, which is completely undifferentiated AI Slop. Right. So you are the AI Slop. Okay, maybe two, three years, AI Is going to build me the perfect programming thing. But right now, I need these really good. Programmers, singletons who are wolves, who have the ability to sort of like the shivams of the world, right? Who can take an AI model and get me the last 10% very, very fast. And so if we can think of that could be interesting model. Right? And you could be. So there are ways to do that. The agent gym. We can weave into crypto.

**Me:** Yeah, I think, like. Yeah. Honestly, what I'm describing, it's like the end phase, right? I think in the medium term, like the short term, what we can do, right?

**Other:** It could even be a mechanical turk for the last 10%. Like a mechanical Turk.

**Me:** Is.

**Other:** But I wouldn't call it mechanical Tech sort of implies a dumb down mechanical task. But there's more high end tasks. Where people compete to help you complete the models the last mile.

**Me:** No. Yeah, absolutely, absolutely. Like, basically where, like, you know, sort of you have the Asian gym, and then in order to actually evaluate model output, you still bring in a guy, right? Type thing and sort thing. And then you can pay him with crypto. Because of Crossbow. We can bullshit that dude. That's fine, you know.

**Other:** Yeah.

**Me:** Yeah, dude. I mean, very not against this, honestly, right? It's like. We'd be direct.

**Other:** And then. Yeah, and then if you look at the white coding platforms, we'll look at the tier 3 tier ones and then they would love it because this gives them a leg up. This helps them pull in more clients and also helps them improve the models through proper human agents. Jimming it out. Right.

**Me:** My friend from high school is the head of growth at a cursor, right? So it'd be like a. Like this thing. Like, just tap his shoulder, and then, like, we can get him as a partner, which would be huge. And then you can raise off of that itself.

**Other:** Okay? Amazing, but make a list of every single person that you know that could be tangentially associates and advisor or whatever. That's the first thing I would do. And then let's make a list of QLs and then you get me the deck. I'll lock in Suroghis and Google on some of these guys. And then let's first lock a date with Banan. So March, man, I think Q1 is a cycle.

**Me:** Okay?

**Other:** Right, so. Hello, adi. Hey, sir. Some Internet issue in mind. No, I think we covered most of it. So send me the deck. Let's sync again. Monday, Tuesday, whenever we can. Set up a quick bi weekly or something. A 10 minute touch base wherever you need help, right?

**Me:** Sure, sure.

**Other:** But let's keep cooking. What I want from. Again, just to reiterate, my role is going to be just give the Banan State focus on the race, get to strategic contacts. Right. You're going to own the product and the BD and the whole shebang. Right? Right. And then depending on where you want gtm. We'll get Subham, Bimal, whoever we need. Right. That's all shown for a flight right now, okay?

**Me:** Yeah. Yeah. Yeah. Okay, I'll finalize, like, a crypto version of this, and then I'll send you, like a. I'll send you a deck that's, like, non crypto, and then I'll send you a deck that's crypto, and then.

**Other:** Set up a drive. Set up a drive, throw and everything you have with some context or something. I'll pick it up and give me a blurb. Small verb, large blurb.

**Me:** Perfect.

**Other:** Crypto non crypto deck any other rating material and then list of people just dump on who all we can reach out to angles are also start adding some names there.

**Me:** Yeah. Sure. Sure, uncle. Okay, okay.

**Other:** And then that's based periodically. Maybe once or twice a week or something. Let's keep it cooking.

**Me:** Monday Thursday manco Monday, Thursday india timer.

**Other:** Yeah. Mandate the swing get appalled.

**Me:** Okay, there's like that 10:30am this thing worked for you.

**Other:** Yeah. 10:30aM Right now, 12:20 in India.

**Me:** Oh, okay. Okay, okay. Okay. Panason. We'll do it earlier then 11am would be your what? 11a would be 30pm we could balance manga India time. Good.

**Other:** April time, but right now it would be 11aM Yeah.

**Me:** I'm in CST 1251 number. So you're like 11 hours and 30 minutes ahead of me. So my 11am 3.

**Other:** 10:30pM Perfect. Put a 30 minute stop.

**Me:** Okay, perfect. I'll do that right now.

**Other:** Yeah.

**Me:** Excellent, uncle. Okay, thank you for the time. I'll ID it on this a bit more and then I'll send you, like an updated deck as soon as I can.

**Other:** Perfect. Perfect. Okay?

**Me:** Okay. Proper uncle. Okay.

**Other:** But again, remember this. Don't one part of your brain just process the long term strategy but other part of the brain be reptilian? How do I solve for thirding party?

**Me:** Yeah. I'm over engineering the hell out of the solution, and I need to, like, honestly, like, just make money first, right? Yeah.

**Other:** To look at story, look at sentient.

**Me:** It's just a narrative play, and they raised a shit ton of money behind it, which we can do as well, I think, you know, with the level of contact.

**Other:** But once you have that, you can get the best PST in the version. They'll build it for you.

**Me:** Exactly. Yeah. Like all this research, like heavy driven stuff, like should be a secondary thing. We should just ship a product that people want right first and people. Not even people want, but the VCs want. Yeah, that's the tag.

**Other:** Y. Eah. The first version of. Do you know the first version of Otter? Right. There's a bunch of guys. Who are listening into calls and sending out transcripts.

**Me:** Yeah, yeah, yeah, yeah, exactly. We should be like that. Dude, there's no reason to like, over engineer or anything or like, you know, like a bunch of technical things on a slide.

**Other:** The V1 would be hairless. And you want to wipe. Code. Great, by code. But then give us a code. We'll get your workable product.

**Me:** Exactly. Yeah, exactly. Exactly. Yeah. 100%. Nights, Uncle. Okay, Kandipa, then I'll send you all these materials hopefully by either end of day today or end of day tomorrow. I have like complete context contextual files as well. So I'll send you that as well on the Google Drive. Okay, andy. Banco. Nice. Okay. Bye. Bye.
