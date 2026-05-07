---
source: granola
workspace: seedbox
ingested_at: '2026-05-07T04:23:57.244510Z'
ingest_version: 1
content_hash: blake3:9f85dad56b7659573d61751901726c57ce71b0f71da46055c3d7ef9573c7559f
provider_modified_at: '2026-04-20T16:55:22.802Z'
account: adithya@outerscope.xyz
account_slug: adithya-outerscope
document_id: bb74e44d-822e-41a1-9124-6b00512ec58c
document_id_short: bb74e44d
title: Avery, Lara, Adithya // SaaS Tools Meeting
created_at: '2026-04-20T16:29:19.562Z'
updated_at: '2026-04-20T16:55:22.802Z'
folders:
- id: d96f8706-87cb-455e-ab44-ffb8fb48f61e
  title: SEEDBOX
creator:
  name: Adithya
  email: adithya@outerscope.xyz
attendees:
- name: null
  email: lara@seedboxlabs.co
- name: null
  email: adithya@seedboxlabs.co
- name: null
  email: avery@seedboxlabs.co
calendar_event:
  title: Avery, Lara, Adithya // SaaS Tools Meeting
  start: '2026-04-20T09:30:00-07:00'
  end: '2026-04-20T10:00:00-07:00'
  url: https://www.google.com/calendar/event?eid=M2lkc2VwMm12bGJpcjk4OWM5MTVsYmFubmcgYWRpdGh5YUBvdXRlcnNjb3BlLnh5eg
  conferencing_url: https://meet.google.com/gfv-fsma-jdo
  conferencing_type: Google Meet
transcript_segment_count: 302
duration_ms: 1508298
valid_meeting: true
was_trashed: null
routed_by:
- workspace: seedbox
  rule: folder:SEEDBOX
---

# Avery, Lara, Adithya // SaaS Tools Meeting

> 2026-04-20T16:29:19.562Z · duration 25m 8s · 4 attendees

## Attendees

- **Adithya** (creator) <adithya@outerscope.xyz>
- <lara@seedboxlabs.co>
- <adithya@seedboxlabs.co>
- <avery@seedboxlabs.co>

## Calendar Event

- Title: Avery, Lara, Adithya // SaaS Tools Meeting
- Start: 2026-04-20T09:30:00-07:00
- End: 2026-04-20T10:00:00-07:00
- URL: https://www.google.com/calendar/event?eid=M2lkc2VwMm12bGJpcjk4OWM5MTVsYmFubmcgYWRpdGh5YUBvdXRlcnNjb3BlLnh5eg
- Conferencing: Google Meet https://meet.google.com/gfv-fsma-jdo

## AI Notes

### Hardware & Architecture Discussion

- DGX Spark and MacBook delivered, agentic setup research completed
- Built folder architecture system for sub-agents with LLM wiki integration

    - Provides persistence and “second brain” functionality
    - Auto-ingests from Slack, emails, Granola notes
    - Addresses context management for long-running business processes
- Hardware debate: Local vs cloud models

    - Preview/No Trade team argues cloud-only approach sufficient
    - Current hardware ($5K) vs $1K/month cloud costs = 5-month payback
    - Adithya advocates for local due to future-proofing and token costs
    - Need 4-way call with Lara to resolve architecture decisions

### Agent Development & Prioritization

- Avery’s agent specification requires significant resources:

    - 2x DeepSeek instances (300GB RAM each)
    - Current cluster under 300GB total capacity
    - Multiple parallel agents may be unnecessary initially
- Wednesday planning session scheduled (Avery + Lara in-person)

    - Finalize which agents actually needed
    - Refine requirements and send to cloud team
    - Determine hardware needs based on actual business processes
- Token usage estimates need clarification

    - Adithya estimates 25M tokens/day for full agent suite
    - Cloud team disputes this calculation
    - Requires concrete agent list to validate projections

### Contract Terms & Next Steps

- Adithya’s proposal: $15-20K/month contractor rate (30-40 hours/week)

    - Currently has minimal other commitments except travel weeks
    - Open to equity vs cash compensation alternatives
- Lara’s concerns: Cost justification for early-stage company

    - Need clear scope and deliverable expectations
    - Timeline-based milestones with 6-hour task estimates
- Immediate deliverables needed:

    1. Triaged agent list by Tuesday night
    2. Business value assessment for each agent
    3. Architecture feasibility rankings
- Additional opportunities: TED Talks founder website project (land conservation visualization)

### Action Items

- Lara & Avery: Deliver triaged agent list by Tuesday night
- Adithya: Review and provide architecture assessment before Wednesday meeting
- Schedule 4-way call with Manoj/Preview team (Thursday/Friday)
- Lara: 6pm call today with Manoj about lab requirements

---

Chat with meeting transcript: [https://notes.granola.ai/t/c07995be-3097-478c-a4cc-c1fec53312df](https://notes.granola.ai/t/c07995be-3097-478c-a4cc-c1fec53312df)

## Transcript

**Me:** Yo, money. Bro.

**Other:** Hey, how are you? Thanks for making the meeting.

**Me:** Quest, quest, ghost. You in the office?

**Other:** Now at home. I only have one day here in the city this week and I leave for London tomorrow.

**Me:** Conway. Where's that? Is that like China?

**Other:** London.

**Me:** Oh. Oh, I thought you. Okay. Okay.

**Other:** Yeah.

**Me:** Hong way. What'd you say?

**Other:** I'm going to London tomorrow.

**Me:** Oh, okay. Okay. But you're in China right now, right?

**Other:** Yeah. No, I'm in New York.

**Me:** I'm retarded. Okay. I don't know.

**Other:** Yeah, sorry, sorry. And I was just.

**Me:** These said some Chinese.

**Other:** No, no.

**Me:** Oh. Oh, okay. I thought you went down for something else. Okay. Oh, bro. That's hilarious. Damn. It's Lara coming on.

**Other:** Yeah. You should be.

**Me:** It's a New York. And. Oh, no, she's not New York, right? She's in elsewhere. I don't know. Germany. Some. Guy where she is.

**Other:** Yeah, she's in London. I think she's getting. It anyways.

**Me:** We got a bunch of set up, man. We can leave. I can walk you through everything. That's helpful. I don't know if it is over. Here.

**Other:** All right, sorry. I was responding to Manish. I think Lara's hopping on. She has. Hello.

**Me:** Hey, how's it going?

**Other:** How are you?

**Me:** Doing well. Doing well. How about yourself? You're in London right now. It's what Avery was saying. Here. Nice.

**Other:** Yeah. Avery's coming tomorrow.

**Me:** Yes, indeed. Yes, indeed.

**Other:** Yes. Yeah.

**Me:** Good stuff. Good stuff.

**Other:** You've got new hair, Avery. Huh? Little G. I just got a haircut on Saturday. Yeah. Nice. Yeah. Yeah. I gotta check into my flight to London. But, yeah, I think I leave at 9am tomorrow, so I get there in the evening sometime. Yeah. Nice. Yeah. So. Yeah, cool. Well. Yeah, yeah, it'll be exciting. You'll have to, I guess, figure out how I get in the airbnb since you booked it for me. It's super close to where I. Ll figure that out. Should be fine. Yeah. Okay. Awesome. Okay. Sweet. So, yeah, a few things we can discuss for the next 25 minutes. We can discuss some sass tools and. And things that we should sort of set up a DT. I know you suggested, like, notion and Adyo. So we're using those for, like, crm and project management. And so I forget which other tools we were going to ask about, but we can get into that. And then also kind of on the AI side, like setting up the. The hardware and I guess maybe going through and ideating, like, some agents and. And talking more about all that sort of stuff, what we had talked about before. Do you guys want to discuss as well in terms of, like, execution work and compensation? Just to understand kind of indeed, like, what is your bandwidth? Like, given the kind of advisor situation, like, what are you, like, what just very openly this is German and me? Like, what are you like? What does it mean to you? Like, what are you expecting to kind of, you know, deliver for that? What is kind of the Outsized scope of that that you feel you would prefer or know or need an additional compensation for? And if so, what's the, you know, kind of hourly expectation for individual tasks? So I think I would want. And this is just me personally. Avery, we didn't get to catch up before, but I would just prefer if we have an honest conversation either we move forward with, you know, one, two, three or four of those things or these fine agreement that we can otherwise, you know, find a different solution.

**Me:** Yeah, totally. Okay, so I can start out with maybe discussing updates on my end. So what I've kind of gotten done with the equipment so far and what I have set up and then maybe talk through and get some clarity from y'all on. On sort of, you know, what sort of deep research agent specifically look like just to kind of refine the hardware spec. Right. I want to make sure we're not over engineering anything as well at the same time. But also, like, you know, keeping mindful that, like, we also do need to be future proof as well with hardware, so. And then after that, yeah, like, definitely let's talk, like, yeah, contract commitment, all that good stuff, for sure. So to start out, let me maybe update you guys on my end. So dgx spark has come in. Mac book has come in. Been doing a lot of reading on agentic setup processes and how to be more efficient with setups. So, you know, gemma has, like, quantization, basically. Long story short, pretty much, you know, from all my reading, what I found is we basically just need to be a lot more rigorous with sort of context management, pretty much. And so that's essentially what you're seeing here. It's like I've basically come up with, like, a folder architecture system for sub agents that's, like, super accustomed to, like, what we'd be doing. So what this allows for is, you know, basically an integration of what's known as an llm wiki, which provides sort of these agents with persistence and second brain almost, which actually allows for, like, useful business processes rather than just ephemeral agents that are just.

**Other:** Can you, like, explain that part, like, in layman's terms? We understand. I don't know if Lara knows what a wiki is.

**Me:** Imagine. Yeah. Imagine, like an imagine llm with ad. Imagine a me, literally an llm with, like, ADHD, right? Like, can't remember, right type thing is, like, immediately just talking about, like, you know, just, like, the next immediate process, but doesn't actually have any, like, context into, like, the bigger picture. Right. Like, what the business's goals are architecture are. This becomes extremely important for certain tasks where creativity and, like, you know, sort of critical thinking and long running business processes matter a lot more. And hence what I'm building out is basically a second brain for Seed bugs. Essentially. So it has essentially a bunch of files and repositories and structures where it auto ingests things from our slack auto ingest things from my emails, auto adjust things from our Granola notetaker. Yeah, like everything. Oh, you're using fireflies. I saw I could do that, too. So. Yeah.

**Other:** Yeah.

**Me:** But this requires.

**Other:** I have, like, 8,000 minutes of 8,000 hours or minutes, something of, like, all my meetings that I've done. So a lot of context there. Yeah.

**Me:** That's insane. That's holy. Eight thousand is a little insane. We might need to use a rag system.

**Other:** Yeah. Yeah. I also have. I also have. Let's see. Like 500 pages of one running Google doc 754 pages of one running Google docs of all the notes I've ever taken for every meeting by hand.

**Me:** Jesus Christ.

**Other:** So.

**Me:** Low-key actually, that's probably a really good organizational structure now that I think about it. As much as I think that that, like, might get cluttered, like, it's actually, like, pretty good that that's in one file already. We can consolidate that pretty easily. But, yeah. So, like, that all being said, right? Like, I have the, the exo cluster set up. We can run local models now. Everything is chill. But I also want to make sure that, like, it makes sense to, like, actually, like, do all this stuff, right? Like, type thing. Like, what are the actual business processes that we're trying to solve? Because, like, we kind of hopped on a call with, like, preview and no trade, right? And these guys are like, dude, like, this is literally a super computer you're building. There's no need for all this, right? So I'm like, I kind of want to, like, balance both sides of it where it's like, I do understand that we need to be, like, you know, more future proof, right, for, like, more complex, you know, sort of models that we need to run locally in the future. But also the question now becomes, do we even need to run models locally in the first place? Right? Like, what are, what are we actually trying to accomplish here and why? I'd love maybe Clarity on that.

**Other:** If we don't do that, then do we even need Hardware?

**Me:** If we don't need local, if we don't need local models, that's the only reason we bought the hardware is for, like, local, like, long running processes and. Right. So for, like, deep research agents processing a massive number of tokens as context windows becomes costly with apis. But if we're not doing this at a massive scale, right, like, where it's like, we're ingesting, like, hundreds of research papers a day, it doesn't make sense, actually. Like, now that I think about it. Yeah. If we, if we just super rigorously manage context and just like, of course this will require several cloud Max subscriptions in tandem, but we can get it done, I think.

**Other:** Isn't that more expensive, though? If again, individual pldmax costs 100, you know, like a hundred dollars or something, several of them.

**Me:** 200. Yeah. Absolutely. We'd be looking it around, like, you know, probably a thousand bucks a month in clawed costs. Ish.

**Other:** Like within five months, the hardware that we bought, which was like five grand. Is that true?

**Me:** That's. This is my argument, too, dude. But, like, this is literally, like, what I brought up to them, too, but they were just like, bro. Like, I mean, if you efficiently do it, like, technically, like, you know, it would take you 10 month repayment period to even pay back, like, what we've already bought. Right. So it's like, is there really a cost benefit analysis trade-off there is kind of their question.

**Other:** Isn't like that at all, to be honest, like, for the rep.

**Me:** That's what I said.

**Other:** Lay.

**Me:** That's what I said, too, but. Okay, whatever. It's true.

**Other:** I mean, personal. I'm not the expert, but I just think in general, yes, there's. There's always advantage of having flexibility and costs. To, like, not, you know, Deflate too much. But I think if it's running costs that are just going to be very, very high and there's no way of migrating it.

**Me:** What we need to do is hop on, like, a four-way call with you on the call as well. I think Lara, like, with these guys.

**Other:** To manage the boys. I'm kidding.

**Me:** Yeah. No, literally just, like, crack the whip, bro. Crack the whip. Make them Defender. Make them defend their position. Like, they're literally just saying these statements.

**Other:** When was these technological. Knowledge? Like, I'm like the one who has, like, this, like, I'm like the, I'm the, like, what's it called? Like the least knowledgeable AI person with the biggest opinion.

**Me:** No, no, but, but, like, you're who we're building for. Right? Like, I feel like you're who they should talk to, too, because, like, I'm trying to convey your requirements to them, and they're just like, dude, you're being a idiot. Like, this is like, that this doesn't make sense. Like that. And I feel like I'm not conveying what you're saying properly, right? Like type thing. Like, because I, like, I'm like, I'm just talking about, okay, like, you know, XYZ business process, but I don't have the boarding knowledge that you do on, like, what exactly you want to see in ray type things. So I think if we convey that directly and maybe get you on a call with them directly, we can, like, iron out sort of what we want built out. And then that, like, then also informs directly our hardware decisions and architectural decisions moving forward.

**Other:** I thought you were just saying that, like, it's too overpowered. Like, we're going to use 1% of that power. If we stack all those hardware things together. Not that, like, we needed to do it on in the cloud or something.

**Me:** The argument is the cloud, bro. They're basically saying we need to, like, transfer everything up to, like, sonnet agents or some for, like, you know, research sub agents. You can't run sonnet locally. It's like a cloud. It's like a proprietary model. Right. That's what previews mentioned. Literally is mentioning so on it, like coding that exactly. And now, actually, after doing more reading, it's not like I disagree with them, actually. You know, like, if you use a series of sub agents, like, around, like, eight sub agents, then you're, that have adversarial sort of, like, tasks given to each one of them. You're actually getting similar level of performance as a flagship model for, like, half the token usage. So I don't know, dude, like, there's, there's definitely these hacky ways that we can get around it. But, like, I also want to be mindful that, like, bro, like, if we do ever want to go back to pivoting back to, like, local. You know, we should just be mindful of, like, increasing RAM costs, all that good stuff. So, yeah. Anyways, like, that all being said, I think, like, the current Hardware system works that we have right now. Like, I don't think we need to, like, you know, scale up super crazy.

**Other:** Okay. What are the, I mean, we had a list of agents that we were discussing that we wanted to launch first was the status on those. Maybe we could just run through and see if they still have and hold priority. Ones that we can now get started as well.

**Me:** Yeah. So, I mean. Like, I know, Avery, you'd put together, like, a thorough list, right? Or something of, like.

**Other:** Yeah. Here.

**Me:** Maybe if we can go through and. Yeah, if we can go through triage.

**Other:** I'll put it in the chat. What is the, we had a document as well, another one that you set up, Aditha?

**Me:** Yeah, I, I think he kind of merged that one. And wait, you, dude, you use that one right as context when you're building this. Avery.

**Other:** Yeah, that Lara sent you.

**Me:** The PDF that we were going back and forth on, like, email. I believe so. I'm pretty sure. Pretty sure it's the same document, but. Yeah. Okay, cool, cool, cool. Yeah, dude. Yeah. I mean, even in your spec right here, it says local model allocation. You have, like, 2x instances of deep seek 1x instance of quad, 1x instance of gemma 4, 2x Max subscriptions. Right? Like, and this is like base level, right? It's like what we're talking about, like, for. Like, agents. And if you're looking at deep seek itself, like one instance of deep seek 300 gigs of ram, we're not even at 300 even in our current cluster. Like, everything put together. And it's asking for two instances of this. So I'm just like, dude, like, I'm. I honestly, like.

**Other:** There is like, there's a high level. I'm just looking at this through because I haven't actually seen this before. There's a high level of engines as well that I'm not sure if we need all of them at the same time.

**Me:** Fair. Yeah. If you don't need a paralyzed task, you don't need to do all that. Yet.

**Other:** No, I mean, I would suggest the phones. Avery and I are sitting. We're sitting down from Wednesday onward in person. How about we sit down, Abe, and just go through the agents, decide, like, which we actually need, refeed that to cloud and see what comes back. And then we decide, you know, like what the. You know, what structure we need. And then based on that, we can, I mean, maybe you want to give us some incentives for the, you know, for the adverse or shares, like, what were you thinking when you initially said, hey, let's do this. Because that would be step one to understand for me. And then secondly, you know, then understanding once we send you the agents that we're thinking of building to understand, okay, what's the time invest on your side? And, you know, what are you thinking in terms of compensation as well as timeline?

**Me:** Yeah. So great question. All this stuff. I was honestly just thinking about it as being, like, more full-time role currently. Like, you know, I have, like, one other engagement that's, like, not really taking up too much of my time anyway. So I was kind of thinking of it being sort of more a full-time position. You know, maybe contract to start out just like as a work trial to see how we work, ray tape thing. Comp wise, I told Avery, like, typically sort of contracts. I, like, take her, like, roughly in the 15 or, like, 20-ish sort of like K per month range. So if that works, like, that works. If not, then I was definitely open to, like, more sort of equity splits versus sort of like cash.

**Other:** I didn't get that. That was so fast. You talked to.

**Me:** Sorry. 15, 000 to 20, 000 is just, like, typically my contract size. So it's like 180 ish, like, upwards. Pretty much just TC per year.

**Other:** Yeah. Contractor basis.

**Me:** Sorry.

**Other:** That's an employee that that's on a contractor basis or a full-time employment basis.

**Me:** That's like contractor position, like, pretty much is like, like my current role right now is like 200, like a contractor type setup. Again, open to, open to different.

**Other:** Yeah. What does that mean in terms of, like, weekly hours or how is that or what's the, like the scope, just the understand.

**Me:** Yeah. Yeah. Great, great question. Yeah, it's like 30 to 40 ish hours per week would kind of be like the contract commitment, essentially. Yeah.

**Other:** So you have one full-time position running already. So how much time would you have to do a second role next to that without, like, getting to a point where you're, like, burnt out or, you know, not able to actually deliver on that stuff as well?

**Me:** Great question. So it's actually a contractor position. It isn't a full-time.

**Other:** I mean, all these questions are good.

**Me:** Yeah, yeah. No, no. So it's the other one's actually like a, it's a contractor commitment. It's not a full-time commitment. So the only time it actually really gets hairy with that one is just during travel weeks. Other than that, like, I literally work like maybe a couple hours per week for that. So it's super chill. Like, typically it's just travel weeks, as I mentioned, Avery will definitely get a bit hairy. So that's the one thing I want to caveat that with. Yeah.

**Other:** Yeah. Yeah. Got it.

**Me:** Yeah.

**Other:** Okay, let's discuss. I mean, the reality is, and this is like me being truthfulness, it's like me not having spoken to Avery about this. It's like we're still very much, like, ramp up phases. So I'm not sure, you know, how we're able to afford spending 200K a year. On hiring someone where I completely even more. You know, I completely understand that that's your going salary and that's what you're looking for. But the reality is I genuinely don't know.

**Me:** 100. Yeah.

**Other:** If that's feasible from, like, you know, even towards investors as well. Because if I were in a bachelor, the first thing I would ask is like, okay, like, what's the, like, how do you justify this cost? It is a really necessary to spend that money. So maybe we can find, like, an in between solution as well. Given, you know, once we know kind of what the scope is as well, we end up week.

**Me:** Cool. Yeah. Perfect. Perfect.

**Other:** Cool. And then, I mean, this is from me. The only thing that's important is, like, having clear expectations in terms of how long things need. If there's a lot, they take longer there.

**Me:** Yeah.

**Other:** To really understand, you know, given the scope and the timing that we agree, like, what are the results that we're looking for within that time frame?

**Me:** Totally. Yeah.

**Other:** Make sure that there's, like, a justification as well for any null cost. S.

**Me:** Yes. Yeah. And that's helped tremendously helpful from my end, too, to, to have, like, time-based deadlines as well. Right. I think give me, like, a sense of direction. I'm happy to set some of these for myself. Right. Etc. Etc. Yeah. 100.

**Other:** Yeah, I'll be in back and forth. Like, if, you know, we're deciding what agent and you say, hey, it's going to take you whatever, six hours, then the expectation is that after six hours, you know, it's done.

**Me:** Absolutely. Yeah. Yeah. Right.

**Other:** And you say, hey, listen, I've come across XYZ in terms of problem, you know, happy to discuss if, like, the timeline needs to be pushed back. But also that there's Clarity in terms of, you know, speed and deliverables.

**Me:** Easy. Perfect. Okay, so what would be tremendously valuable at this point for me, from you guys is basically just a clear list of sort of, like, agents and expectations. I think where I can sort of help with this document is more so on the architecture side with the actual Enge decisions. How do we actually build this out? Is it feasible? Right. Ranking by feasibility. But where I have less visibility and where I think I'd love your guys'Insight on is, like, the actual business operations part of it. Right? Like, how does this add value to Seedbox tangibly? Right. Triaging it from that perspective would be tremendously valuable for me.

**Other:** Yeah, we'll get that done for store. I think, you know, like, one of the biggest holdbacks right now is just to get the boys working. And get the work done, and then everything else is going to fall into place.

**Me:** 100. Yeah. 100.

**Other:** So. Yeah, no fair.

**Me:** It's a cold start machine problem, dude. Literally, we just, like, once the machine gets started, we'll crank. I know for a fact. Yeah.

**Other:** It's like, it's this, like, waiting period where, you know, like, it depends on, like, how when, once they get going, there's, like, the kickoff of the timeline to kind of, you know, then start, you know, measuring against whatever deadline we have, but until we don't know when they start. Everything's kind of like in limbo because when do you do start socials? If we know that's going to be a year from now, maybe now is too soon. Who knows? You know, that. S.

**Me:** You guys heard the decision making phase. That makes sense. It's always good to. To plan. Right type thing, I think, before executing. 100.

**Other:** Because you're not running in the folder, like, in the wrong direction and stuff as well. So cool. Yeah, that's all from my side. We'll get back to you. I'll schedule something for us for Wednesday, so we'll get back to the end of day Wednesday with an overview of the so that we can get this done by end of week.

**Me:** Okay, cool. Okay. Yeah. So if there's just a triage version of that, if you guys have a version, like the triage version, maybe by tomorrow, that way I can also, like, maybe put together a version, take a pass, you know, myself before a Wednesday meeting.

**Other:** He's on the plane tomorrow, so probably Wednesday morning, which is then your Wednesday. Like, it's your give your Tuesday night, probably when I'll schedule for us for the morning. So you just have it by Tuesday night.

**Me:** Okay. Okay. Solid. Okay, perfect. Cool, guys. Okay, sounds like a plan. And then, yo, Avery, dude, can we get a meeting, like, maybe scheduled with, like, manoj for being Lara, too? I think that'd be tremendously helpful just to get those guns because, like, it's. It's like I'm trying to communicate, like, sort of like what she's trying to say, right, to these guys, but they're not understanding it. I feel like, you know, or maybe I'm not understanding what they're saying. Either way, there's some miscommunication going on. I just want to make sure everything's resolved. You know?

**Other:** Well, they looked at it and basically said, you need, like, less than a 10th of all of this computational power to. To do this.

**Me:** Facts.

**Other:** Do you disagree?

**Me:** Like, I don't disagree. We can take it to the.

**Other:** So then why, why.

**Me:** We can take it to the cloud. However, my argument is that the payoff period of the hardware is going to be a lot sooner than what they think.

**Other:** Yeah.

**Me:** That's. That's my. That's my argument. In fact, I think it's actually going to be in two months, according to my calculations. But we need to iron out business processes first in order for me to justify that cost. Right. I can't be, like, blindly, like, you know, because, like, this is what happened, right? When I told him, I'm like, yo, man, like, our cost is going to be 25 million, like, you know, per day, like, tokens per day. And they're like, no, it isn't. Right? Like, it's like we. We only have one, like, sort of deep research agent, right? That's, like, maybe scraping I for leads. Yeah. Like, obviously it's not going to be like 25 mil if it's just that. But if you have, like, 20 different business processes happening, like in tandem, right? Okay. Social media agent that scrapes the internet for.

**Other:** If you, if you run, if you run this document through cloud and say how many tokens a day will this burn to do this plan, what does it doesn't say 25 million, though? That's what they did. That's part of what they did as their research.

**Me:** Like. So what, what business?

**Other:** You saying it does?

**Me:** It depends. This is why.

**Other:** What I just put in the chat, all of those agents.

**Me:** This is why, this is why, like, if I have Clarity on sort of what agents, like, we're actually going to build out, dude. Like, I I honestly do think, like, it's going to be way more than, I think 25 mil is a conservative estimate, in my opinion, based off of the doc you sent me. So I don't know where the hell they're getting that numbers for them, but, like, let's iron out the dock first, because then that gives me justification to be like, yeah, this is, like, literally a hardware requirements or this is our payoff period. This is like XYZ without numbers. I can't cite anything. It's just BS, right? It's just made up numbers. But, like, with these numbers, with the number of agents that, like, and, like, an agent like structure, right, then I can be like, okay, this is like a running, you know, processes. Anyways. Yeah, I think that would be tremendously helpful. And then we can, like, schedule a meeting Thursday or Friday with those guys.

**Other:** Yeah, sounds perfect. Yeah, we'll do. Thank you.

**Me:** Perfect, guys. Cool.

**Other:** Okay. And the interest of time on potentially returning it, though, how soon should we speak with managers? Like, should we do it, Lara? Should we try and do it today or what do you tomorrow. Or. I mean, you want to. I'm going to schedule a call now for 6 p.m. to talk to manuja anyways for the. For the lab that he was requesting on WhatsApp. So we can just ask him as well to, like, have a thought about, like, what kind of, you know, like maybe things they would require or that, you know, would be helpful for them and see if we can add that in as well. Yeah. Okay. All right. Sounds good. Can you invite me to that? Yeah. Okay. Awesome. Yeah.

**Me:** Anything else? Top of mind?

**Other:** Okay. I just met the founder of ted talks this morning, and she wants help building, like, a website if you want to. That could be. Yeah. She's trying to build a new project that can.

**Me:** Dude, what? Founder of ted talks? That's insane.

**Other:** Yeah. Sitting next to her at a breakfast today.

**Me:** That's insane, bro. My mom ran, like, 10x and Austin or some, actually, for a bit.

**Other:** Yeah. Yeah, yeah, yeah. Oh, really? Nice.

**Me:** Yeah. She was like, hella plugged into the ecosystem. That's insane. The founder is insane, dude. That's crazy.

**Other:** Yeah. So she's trying to do. I can.

**Me:** Wait, what does he want? What does she want to say? Yeah. What are you saying?

**Other:** She needs to use AI to build a website that ingests a bunch of data and shows a visualization of, like, areas in the world where land needs to be conserved and then where people can go and donate money. To put those acres of land in a trust. And I think I asked her about the data. Yeah, the data is all publicly available. You could probably vibe code it really quickly.

**Me:** That's solid. Oh, that's pretty sick. Yeah.

**Other:** So. And then there was this other guy who's, like, was the first designer at ramp. Which is now a $30 billion company. In new york. And he would help her with design. Yeah. So if you want to maybe work with him a little bit on that.

**Me:** According to ramp, bro. Of course I don't rip, bro.

**Other:** But we can talk about that when I get back from London. Yeah.

**Me:** Holy. Dude, that's actually crazy. Anyways. Yeah, I'll hit you. I'll hit you on, like, a FaceTime or something for sure. Yeah, we'll talk through. It.

**Other:** Okay.

**Me:** Okay.

**Other:** Yeah, I think. I think that's it. So we'll, we'll pick this up in a couple days.

**Me:** Cool, cool, cool. All righty. Appreciate the time, Lara.

**Other:** All right.

**Me:** Good to see you. All righty. Peace. Peace. See you guys.

**Other:** All right. Bye.

**Me:** Peace.
