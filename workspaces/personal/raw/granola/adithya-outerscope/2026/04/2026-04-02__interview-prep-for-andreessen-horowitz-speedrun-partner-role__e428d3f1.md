---
source: granola
workspace: personal
ingested_at: '2026-05-07T04:23:57.244510Z'
ingest_version: 1
content_hash: blake3:519b164fb111f2f360380205a8735a43ccbe2257270346c1ced97828cad1b46f
provider_modified_at: '2026-04-02T21:36:31.508Z'
account: adithya@outerscope.xyz
account_slug: adithya-outerscope
document_id: e428d3f1-e08f-47af-a20f-9f336e0872bb
document_id_short: e428d3f1
title: Interview prep for Andreessen Horowitz speedrun partner role
created_at: '2026-04-02T20:20:11.890Z'
updated_at: '2026-04-02T21:36:31.508Z'
folders:
- id: db8d0de1-40e5-4cfa-943d-65a5f3837095
  title: PERSONAL
creator:
  name: Adithya
  email: adithya@outerscope.xyz
attendees: []
calendar_event: null
transcript_segment_count: 828
duration_ms: 4568080
valid_meeting: true
was_trashed: null
routed_by:
- workspace: personal
  rule: folder:PERSONAL
---

# Interview prep for Andreessen Horowitz speedrun partner role

> 2026-04-02T20:20:11.890Z · duration 76m 8s · 1 attendees

## Attendees

- **Adithya** (creator) <adithya@outerscope.xyz>

## AI Notes

### Context

Interview prep session for Adithya’s upcoming a16z Speedrun partner interview (tomorrow, 1:30 PM). Friend/advisor running mock Q&A and coaching on answers.

### Interview Format & Role

- Role: investment partner at a16z Speedrun (early-stage / pre-seed focus)
- 9-interview process + case study + pitch presentation — all within April
- Interviewer tomorrow: Jonathan (senior director, biz dev / gaming background — non-technical)

    - Expect product/team/culture questions, not deep technical grilling
    - Likely a second technical interviewer in a later round
- Title is “partner” but functions as junior analyst level

### Strong Answers (Keep These)

- AI in personal workflow → Ultra Claw agent: auto-schedules, manages calendar, integrates Apple Health for diet recommendations, self-eval loop that has caught security bugs and upgraded itself
- Technical moat at pre-seed → team + unique market insight + early data flywheel thesis; data flywheel creates defensibility even against LLM providers (Deepgram, Cartesia as examples)
- AI coding agents in 18 months → question is wrong; autonomous founders within 18 months; Claude Mythos (10T parameter) already leaked
- Overrated AI startup category → consumer voice AI agents; B2C increasingly dominated by agentic tool-calling (Anthropic MCP, Amazon Rufus); their domain will be commoditized
- Broken dev tooling → agents don’t autonomously select skills; current solutions (cursor .MDC files) are patchy; fix = dispatcher + skill agent + executor model
- Investment thesis to pitch → agentic memory; mem0 ($25M Series A) validates thesis; super memory has better QMD vector lookup than mem0 and likely to ship auto-recall hooks soon
- Build vs. buy on AI stack → local for deep research / long-running stateful processes (KV cache RAM costs); API for periodic batch jobs within rate limits
- Failed side project → Mosaic evals verticalized judge model; tried training from PyTorch ground-up, too expensive; pivoted to fine-tuning open-source eval models on customer data

### Areas to Tighten

- Answers running too long — target 30–90 seconds per response
- Lead with the problem/bottom line, then add supporting detail
- “What company would you invest in?” → needs a prepared, specific answer with conviction
- Sourcing/deal flow weakness (no prior angel investing) → reframe around X scouting system + conference network + high-bar personal network (“you are the product of the 5 people you spend the most time with”)
- Underrated AI founder question → pivot away from Berkeley names; use X discovery story (find a designer → see who they follow → curated feed of undiscovered builders) applied to AI founders

### Key Coaching Points

- Own the technical superpower — Jonathan is non-technical; being the “technical auditor” in the room is the differentiator
- “Why this role vs. building?” → don’t force a definitive answer; frame as: “I’m a builder — if you don’t hire me, you’ll fund my company later. But VC lets me multiply my skills across many founders at once”
- “Why a16z?” → strategic capital vs. financial capital; a16z has recruiting, marketing, PR arms; Speedrun mirrors venture studio model; matches existing multi-contract working style
- Preserve founder relationships even when rejecting ideas — they may be fundable on idea #2
- Be ready to share screen and demo Ultra Claw unprompted if not asked
- VC is an art, not a science — pattern recognition over metrics; Marc Andreessen himself says VC survives AI because it’s intuitive

### Next Steps

- Adithya: research a16z Speedrun portfolio companies (have a specific one ready to discuss)
- Adithya: prepare a concrete answer for “blank check to one open-source repo/solo dev — who and why”
- Adithya: review VC deal evaluation frameworks (financial vs. strategic capital framing)
- Adithya: have Ultra Claw demo ready to share screen during interview
- Adithya: get sleep, eat, drink before 1:30 PM interview tomorrow

---

Chat with meeting transcript: [https://notes.granola.ai/t/700ce964-dd24-404c-b4d7-8fea7073730e](https://notes.granola.ai/t/700ce964-dd24-404c-b4d7-8fea7073730e)

## Transcript

**Me:** Our loading. I'm browsing access for 45 seconds at a time. And I stay at the cutting edge of what's happening in AI. So you don't have to. Really explain how you're doing it because maybe you are, maybe you aren't able to see what you think. Okay. But all you got to do is just say that. Don't believe you. They're like, okay, this young kid, like, knows how to use acts, right? And. Then you should be sort of familiar with the portfolio and, and the alumni and the post that he just made on LinkedIn that you sent me. Got you. Okay. Alumni meeting. No. The, the company that. The. Companies that. Jonathan tag. Ged in his LinkedIn. Post. Oh, got it. Okay. Be fun. Okay, got it. Yeah. Facts. Perfect. Okay, facts. Yeah, dude. Okay. So then. Let me give you some. Questions. Let's run. It. Okay. Okay. This. Shot requires a link. To a product. Or terminal session. You're proud of. Can you please walk me through? What you. Built? How you integrated. AI. Into workflow to build it? And how you. Do optimize your coding engine. So just tell me what you would do if you asked you that question. Yeah. So for one of my contracts with eclipse right now, they, they pivoted from a, you know, crypto facing layer two solution to a human API product that allows, you know, just agents to call upon humans. So for, you know, to complete various tasks, essentially acting as a data broker. So for this, we required a ton of outbound go to market initially, which ended up being a very tedious and manual process, you know, to set up in order to hire folks for these tasks as well. We decided to kind of hackily use fiber and upwork in order to post tasks while we were sort of building up our corpus individuals. So in order to prevent this from being extremely manual and in order to kind of hackily get around API limitations on fiber and upwork, I implemented a custom open claw implementation to constantly scrape our internal slack and Google Drive to update its, you know, daily memory of and working memory of our product, then go out and use fire call, exercise and a number of other tools to pull, etc. Etc. To pull the top 200 leads every day that we hadn't reached out to and automatically email those folks and send a LinkedIn DM using LinkedIn sales Navigator. So this greatly increased calls booked, you know, for us and actually landed and closed several, you know, deals for us as well initially while we were coming up as a data broker with, you know, very limited sort of reputation, which is extremely important in that space. The other thing is we, we also built up our contributor network significantly using the custom open cloud implementation that we had built for relaying tasks from the API directly to Fiverr and upwork. Many of those contributors actually ended up not only staying on, but ended up being sticky users on our platform. So that was kind of a patchy way that we also had used AI to bolster the product. Okay. Very engineering heavy, I think, bro. Right. No, no, no. It's good. So Claude says this is actually good. So it says you should pick. The one with the most technical, technical depth and observable user impact, which I think you did both and lead with the problem, not. The tech. Thank you. Okay. Okay. Is that Laura? Okay. All right. Sounds good. Yeah. That was Laura. Nice. So. It says. Lead with the problem. Not the tech, but you also did. And then it says for some reason, end with what you would do differently. Right. I don't. Know exactly. Why you need to do that. Yeah. I don't know either. But, yeah. Okay. Let's just go through some more questions. Okay. Okay. I think that looks pretty good. I think. That was pretty good. I would, I would say it's a good point to go with something with very hard technical. Depth. It doesn't seem like. That had good user impact. I, I would say that would be an okay thing to answer. But if there's another way. Don't. Want to talk much longer than that, but maybe add on. There's a, there's another thing and then, like, impress them with how insane. Like, I could also be like, yeah, like some of our go-to-market like a b testing post for our user generated content. I ran through Facebook's new hive model to test out what neurons it was essentially activating. Right. It's imp like that. Right. That one is really. Interesting. Yeah. You can sell that really well. Hell, yeah. I wrote that in. Because you're like, you're like simultaneously answering these questions, but then you have to think, like, how it's being perceived by the user. Likes what I'm not. Saying. Allows, you know. Whatever, like you to see how. And then that demonstrates that I'm on X and too. Yeah, valid. Yeah. Oh. That. That's what. That gave me a very impressive answer. Okay. So, okay, let me just give you some more questions so we can practice, right? When are you, when you were working with an AI founder at the absolute zero to one stage, what's the most common mistake you see to make regarding the GTM strategy or their fundraising pitch? And how do you correct it? They often assume that their moat is in the technical product itself rather than the go to market. Honestly, any sort of product right now will be replaced by an agent within the next six months, and people have to realize that and be conscious of that as Founders and recognize that as a result. I think a large result of many investments and even a16z investment and clearly significant. Of this. Right. It's more respective. Of good market and actual volume. And ability. As a product. And it's really more about human attention these days. The ability to capture attention in a product rather than the product itself, because products are commodity. Software engineering is a commodity that we see this increasing board employee sales engineers as well. Right. It's disrespectful, frankly, not a lot on sales call, not a network, right? Just because of the cost of, don't, don't we step into the point? So what? What, what do you mean? So one place, what were you saying? Is the most common mistake. Assuming. Product, like, is a mode rather than go to market is a. Mode. Like, I think modes for, like, most, like, AI products these days are, like, a teaser base. That's all. I should have just. Fine. Yeah. You. Need to be deeply embedded. In the network. Where you. Find it as far as. Buildings right. Now. And who. Is an underrated. AI founder? You've recently interacted with. I'm working with Jeff from, say, he's one of the co-founders to build, like, a Berkeley version of Harvard's broad program. He's, you know, also, like, kind of trying to build up his own venture or not family office, you know, pretty much. So. I'm finding Builders all across sort of the, the Berkeley ecosystem right now. There's several sort of clubs there that I was natively ingrained with during my time there as well, given the fact that I'm a GSB right now. I can also interact natively with sort of Builders there. I know coon and Gil from the blockchain accelerator. They're very well for a number of years. And so both of those are, you know, very good corpuses of Builders, respectively. There's also. I, I would talk about. Like, X, to be honest. Or something like that. Yeah, right. That's a good correction facts. I would say, look, I, I. M, I'm very captain on X, and I'm constantly looking for, like, for example, I met this chapter recently in New York was like, I find all the best designers because I will find a designer and then see who he follows and follows them. And then my gold news feed is just cracked undiscovered design engineers. You should basically say yours is like that for AI Builders. Yeah. Because if you're a VC, you're. Hiring these people as founders to invest in sort of. Yeah. Right. So I would recommend. You less about Berkeley, especially if, like, our Stanford will be dispossibly. Jefferson. Really? You're gonna. Say he's an. AI actor. He's not. No, no, no, no, no. I'm, like, building, like, this program with him. Or whatever. The. Says. An underrated AI. Underrated AI founder. Me. Wasn't. Underrated. Me, myself and I. M. Gonna. See. So again. I think. Your weakest part. Of a lot of the categ. Ories is. Probably around invest. Ing because you haven't been an angel. Investor. Before. So you're gonna need to, I told them I, I tapped. I told them that I angel invested in a couple, like, things. I need to, like, figure out. You should tap it. You should have an answer ready for this, because, again, let me tell you. If there's. Another Berkeley. Kid who's just. As good an AI. But he knows slightly more on sourcing deals. Yeah. Well, you're. Not thinking. But you just want to address this potential weakness. How do I do that? I mean. Look, I can send. You. This. Question. And you can just put some thought into it. Yo, my boys rose it. You check out this thing I bought my brother. She's acting. Dude, but it's like some LED thing, like, displays the price of some stuff. I I know someone that has a so overpriced ever. She's 100 bucks for this tiny ass. Look, he looks legit, though. This guy with a. 35 000 apartment in tribeca in the bargain. He runs the New York City fires club. With the. Bitcoin price on it. In his. Department. Yeah, that's me, actually. No, this. You can set this up for bitcoin, too. Yeah. You said it, like, tracks it live online and. Dude, that's your negative, bro. 35k. When he. Runs an AI. Benchmark. That's why he's building an. AI engine. Dude, can we, like, talk to his name? Can you, like, let me, like, talk to this thing? Like, I'll figure it out. Trust. Yeah. And then I have. Another friend. From stanford as. A mention. But. You got to be a very. Serious person. If you want to talk to them. No, for sure. Like, I like. I like chink. I like chink on the phone. If. You're very experienced. Okay, let's wait. So sorry. Just so I understand the limitation here, right? Like, I I need to. The limitation of my profile right now is that I haven't sourced previously. Like, I don't actually, like, have any, like, direct proofs that I could Source. Right type. You need to. Be able. To answer the. Question of. Do. My next question is. What company? Would you. Would you recommend. Me? Invest? Ment? So number one. Calm. Prepared. Okay. Answer to. That question. Right now. Okay. Yeah. So. That's me. You have to admit. Your customer before. You need to. Pass. In these stuff. Number one, they're looking for. Two things. For one. Jude, you literally. Coming the door? With. The old float. Is so. Holy. Number two. Okay. As. A system. What is your system? As a potential. Venture capitalist for increase? What's the system at which you. Re gonna find the. Continuing uncover. Ed new flow? Is it X? Is. It group chat? Is it new way outside of Stanford? Wall engineering center after the AI class ends and you talk to the other. What is your system or. I mean, I'm just like, yeah, the Berkeley, you know, they're trying to understand what is their system by which you come up with ideas for you close and can you literally reveal flow and on day one? Not necessarily Adaptive or like, at least for the. Educ. Ation. You might have to city source. Deals. But once the system for. Which you are. Getting new deals across your newsfeed or your monitor, whatever. Right? So I I like. Okay. Yeah, it's facts. Okay, so I'll just be like, I Source Builders on X, like, using that exact thing, like, lip launcher, homie said, I'll be like, I I constantly travel. I go to all the AI conferences, like, literally 500. Literally, like, I always connect with accelerators, Venture, like, you know, other venture abilities. Like, I keep the quality of my network. And you'll learn how to do this, especially if you work in a Jason. But I keep the quality of the people that I surround. Like, what I personally say a lot of the time, and it's kind of true. Like, You are the product of. The five people you, you spend the most time with. So therefore, if you prune your network and only hang out at a very high level people all the time. You're going to only be, you're going to be. Operating. At this higher level. And so you're only going to be around other people. So it is true you go into these conferences, but also it's good if you just throw that sentence in there. Of, like, I, I hang out. I only associate with very high level Builders, and then I am able to get into group chats. They introduce other Builders. I get invited to things, and I'm constantly meeting people at the highest levels. From tier and AI. Like, I would explain. And then they're like, okay, like, he has the high bar for this. I can just say that. I need to prove it. Right? No, for the interview, you're gonna need to say it. But to prove that they might, the last question here is, like, looking at our current recent alumni, like run where hedra next to AI, what is a brand new frontier AI thesis you would shoe up through our new fund. So they will ask you, like, what category do you like? So I like memory. I like memory. The limitation between AGI and current systems is context windows and agent harnesses. You've seen prior work in this, both these spaces. The recent 25 million dollar series. A. For mem zero proves this thesis out as well. And you can also see increased consumer demand for autonomous agents with consumer tools seen by the recent Resurgence of open claw as well, right towards the end of last year. You've only seen more self-improving agents and longer running agents with the news research agent and carpathy's auto research going viral on Twitter and X. I'm sorry, Twitter and GitHub, right? Like last week. So what you can see from both of these Trends is memory is really the limiting factor at this point. Tools and auto calling tools has been pioneered by anthropic using the mcp protocol. You already have autonomous sort of agents that can constantly self learn. Now the limiting, the third part of the piece, right, of the puzzle, right autonomous and truly helpful agent and stateful agents is memory. Mem zeros already taken off. The other startup that I would pitch to the fund would be super memory. They have better qmd lookup on a vector database. So if you're running both on quadrant or a local SQ light database, you're actually going to get better performance with super memory than mem zero. While mem zero has auto recall, you can actually write custom hooks to get the exact same behavior out of super memory. And I suspect largely that they will update their product to do this. So Builders will natively be able to integrate this with open claw. And as a result, you'll have a way crazier Resurgence. And this is a very. Opportunistic time to pick them up because I suspect that they'll probably be shipping out a new version with this hook capabilities automatically baked in. Right. And once open Cloud Builders actually realize that the auto recall feature is now, you know, available on super memory. And they actually realized the performance is much better for lookup, memory lookup than what do you call it mem zero. They're all going to switch over to that and they're going to have an insane amount of recurring Revenue from open cloud Builders. And as a result, I think that that's what pushed their valuation. Way higher. So I think we should look into that. But you're. Going to want to keep your answer slightly shorter. That was a little bit too long. Yeah. Facts, dude. I'm a. Content was all good. But if you can try and get the most emphasis, emphatic points off in 30, 60, 90 seconds, that'll help the strength of the answer. Just like it's a presentation thing. Okay, let me give you a couple of other good ones. This one's a juicy one. So I just want to see how, how hard you can knock this out of the park. Ready? Okay. How have you actually embedded AI in your own workflow, not just your products? My, my custom agent Ultra clock. Scrapes all my sort of contract work individually has a separate database in order to prevent any conflict of interest between sort of contracts. Auto schedules meetings for me. Auto manage my calendar every day. Auto compacts memory. There's. It basically has, it's a stateful agent that autonomously takes decisions for my life and auto recommends things for me. I'll give you a very simple example. I've integrated my open claw into my Apple health. So it actually autonomously, it knows that I'm South Indian, knows that I'm genetically predisposed for diabetes. And autonomously recommends like a food plan for me every day because I hate cooking. I, I hate planning for cooking and I hate shopping. So I've integrated that into my life on a daily basis. Very simple example, but a similarly, you know, there's also more complex workflows, obviously, like sending, you know, generating research reports autonomously based on Granola, you know, AI meeting notes and then sending those autonomously into slacks, et cetera, et cetera. Right. Okay. Really good. I, I would almost laugh my ass. I'm gonna definitely say I'm South Indian, so knows I'm genetically inferior. Once broken. Okay. Where do you think. AI. Coding agents will be in 18 months and what does that mean for Founders should build today? Agents will be asked of whether you're, this is a test of whether you're a clear thinker on the trajectory of AI agents. Agents will answer that in 18 months from now, agents will be Founders themselves will completely go from end to end customer UX research will autonomously parse things like Reddit, a scrape online threads to understand where holes in the market lie. There will be no more developers, I think, in 18 months. The question itself, I think, is wrong. I think from, from a thesis standpoint, you already look at Claude Mythos, which has just gotten leaked with this a 10 trillion parameter model that they're only releasing to select few individuals and has already been proven to be the best hacker in the world, better than any human engineer could ever be. We already have this, right? Claude claimed that it was already, quote unquote, sentient, although I suspect that that's just a go-to-market play by anthropic to just achieve virality. But honestly, I do suspect that a 10 trillion parameter could easily achieve sentience. And at that point, you're really looking at autonomous Founders, autonomous thinkers that really don't need humans in the loop. So honestly, I think the question itself is wrong. I think we'll have autonomous Founders itself in 18 months. Nice. Okay. That's. Good. What's broken about. The current. AI dev tooling that you fix? There could be a much better agent harnesses, in my opinion. And autonomous agent harnesses that autocall tools. It's very annoying to have to even, you know, using every, everything clogged code skills, which I think arguably is one of the best agent harnesses right now. Ford's claude CLI, you're constantly having to use slash commands autonomously. And while I've, I've actually tried to code a dot MDC file to autonomously, it's like basically a daemon file that is a watcher and triggers upon, you know, stateful hook events in cursor to pull in skills based on prompt processing. And autonomously use and choose whatever skills it needs. But this is not an autonomous task. This is kind of just a patchy solution, right, to a larger problem, which is that agents actually don't autonomously pick skills. Rather, it's just an auto suggestion in their dot MD file. So there should be a harder enforcement, programmatic enforcement, I believe, for agents to select skills based on a prompt processor. I think a way to do this is using a agent of agents model using a dispatcher model and then a dedicated skill agent that then auto injects that into another larger combined prompt to a third agent that then gets the combined prompt from both of those and then executes, including whatever skills are needed. Retarded answer, bro. I'm sorry. It's so autistic. No, it's. Okay. Okay. Maybe almost slightly too long. Yeah. Because you want to probably impress him as long as possible for 30 minutes, but, like, if you do two and a half minute answers, that'll maybe limit the number of questions. Yeah. Okay. So. Okay. Ready? Investor questions. So what's it, what's a space you push speedrun to be investing in that they're probably not yet agentic memory. Like I said, I think that's the biggest hole in the market right now for AI. Everything else is just wrappers. A genetic memory is the only thing that achieves any stateful context and actually causes vendor lock in as well. And I think that that causes recurring revenue. Okay. If you were evaluating a pre-seed AI startup today, what's the first thing you pressure test? The founders themselves, that's like the first, you know, like art of VC literally states that, you know, if the founders have signs of Excellence historically and also have, like, extremely solid theses that this is a dude, how would you, how would you answer? Can you, how would you respond to this? Yeah. So client says. Investment partners, quote, think critically about new technologies and market trends. Aditha is being evaluated as a future partner, not an analyst. You should answer like someone who has seen startups succeed and fail because he has ideally references a real pattern he's noticed. Which could be the quality of the founders. But you, but I might ask a follow-up which I'm gonna, I had to follow it myself to that, which is like, well, tell me what specifically you're looking at in the founders. Signs. Excellent. Like us in, like, past associations with, like, good research labs, Elite, like, placements at jobs, right? Like desirable, like Frontier research labs. They should have a reason for quitting and actually working on this. Right. It shouldn't just be because they're jobless. That's a, that's a good neck in my. All right. So what's, what, what's a company in the speedrun portfolio you find interesting and why? I gotta do some research. Okay. All right. Why this rollover building company? Huh? Huh? Are you interested in joining and treating the horror with Steve and over building your own company full time as a, as a founder? That's an excellent question that I do not answer. How do I do that? Because I literally applied for speed run, and I'm literally, I have another interview for speedrun, like second round, so I don't know what the to say. As a, as a founder. Yeah. Mosaic evals. I told you verticalized judge model, bro. I'm in the, I'm in the late stage speedrun thing, too, bro. It's like low-key W's all around, bro. Wait, how are they inter. Viewing you for both? That's what I'm saying. I literally don't know, dude. I didn't even apply for this position. I applied for speedrun, and they literally, like, like. Headhunted me for the position or some, or, like, they're just like, all right, it just, like, also apply for this. So get go to serious opportunities, man. Partner in 23 at andreachen, bro. Dude, the next closest guy is 32. He's told a company to lift. He was, he's been a ban capital Ventures. By the way. I'll have to coach. You on this if you get the role. But, like. The partner. Title means think they're jackally make money and partners who are basically Junior Associates, bro. Yeah. They're all partners. So once you're there, you're gonna have to figure out how to navigate and actually be good if you want to move up. But anyways. Okay, so I think, yo, how much, how much money do you think this is, bro? Realistically. Like 200k. But, like, you could parlay it into a lot of things. It's not a bad job to take. There's a lot of optionality. And if you do a good job and you stay at the firm, if you stay there for five or ten years and actually move up. Then you can make a lot of money. Okay, so look, to answer that question, why this role, especially if you're interviewing for both, I would basically just say, all you have to say is. Like, I love building on the builder, first of all. First of all, I'm a builder. Okay. Yeah. Like, even if I join as an investor, I'm actually a builder. But I'm really interested as, as a builder and founder. Like, I'm interested in multiplying and an AI Builder. Like, I'm just, I'm very interested in multiplying my efforts across. That's exactly with different Founders, especially going deep and helping them with AI. I think it's an interesting opportunity for me to be able to my skills into the world and help lots of people with different goals, something like that, probably facts. Because, like, yeah, it's like. But, like, with that, like, kind of signify that I'm, like, not in depth into any one thing. Like, but it would, it would just actually, it would signify the exact opposite. It would signify that I'm a very involved VC, right? Theoretically. Look, I think you, I think the answer is you don't even, you don't have to, like, act like you know for sure that this is the right thing for you rather than building a company. And I noticed I didn't really say, like, for sure. The reason I didn't really say, like, oh, I'm a way better fit to be a DC than an entrepreneur. I said, I'm a builder, so I'm actually saying I'm not, not a founder. Like, if you don't want me for this job, you'll end up funding my company later. It's basically like the attitude. It's like, but, but. A VC who can help a bunch of different companies potentially can make more money and impact than a founder doing one company. And so I would frame it as, like, I'm interested in doing this just as I'm interested in being a founder, kind of, because, like, but it's kind of maybe like being a founder with more than one company. Why Ad over other funds? And I can also kind of point to the venture studio thingy. It could be like, bro, I've been working in multiple contracts. This is naturally what I do. Like, literally. Yes. Yes. That's a great answer. Yeah. I'm actually used to getting involved Hands-On in early stage companies, and I'm currently doing that. So that's a great, that's a great answer because this is different than, you know, joining one board a year as a VC partner and have some other firm, you know? Right. Okay. And so why Andreeson over like Sequoia over someone else? I would, I would tailor it to the speed run program and say, look, I'm really interested in working with a batch of new companies every quarter. Right now, I'm actually basically doing, I'm a perfect fit for this job because I already am working with a bunch of founders and I split my time among a bunch of different companies and find that to be a good way for me to apply my skills. And so I think this, I would answer it and say it's not only why Andreessen, why Andreessen is partially because of the speedrun program, right? Yeah. So I would say. Because of what you said, like your Venture Studio experience, essentially speedrun is like a venture studio where they're incubating companies that if they said, why not Sequoia are, which is the same thing as Andy. Right, right. I don't really. Okay, so why I, I think probably the opportunity to build, to work alongside such knowledgeable investors with, with alongside a sequoia is an investors, too, right? Well, I don't. Know that they're going to ask you why not Sequoia. That's kind of a, that's kind of a question. Yeah. It's like, dude, because they didn't call me for interview. Yeah. Like, any other Venture firm that's easier to answer, but if they're like, why, why not? I would honestly be like, dude, sequoia is better now. Just like, yeah, dude. Hey, man, put out a good word for me, bro. Like, literally, I need a referral dog. Yeah, literally. Okay, cool. Nice. Okay, so builder first, and then, like, this thing. Okay. And then, like, I'll get involved. Okay, fire. So, yeah, so Gemini says own the technical superpower. I very much agree. I know how to evaporate. That's another good thing you could say. I know how to evaluate these companies from a technical standpoint. Because I know how they're built. Yeah. Yeah. Dude. Dude, I'm gonna say I'm your CTO, bro. You mean I say I'm your CTO? If you want. Yeah, low-key low-key on the low. You're gonna be like, yeah, dude, I'm a CTO. This. This company here. Nice and technical. And hold on. It's fire. I don't know if. Is that good Optics? I guess like low-key I don't know. I mean. Aren't you gonna say you're helping a bunch of different companies? Yeah, low-key yeah, look. If I'm like, yeah, dude, I'm gonna say. You could say, like, I'm, like, interim CTO for, like, very dang. Yeah. Easy. I'm at the level of, like, a CTO when I'm helping these companies get off the ground. You should actually say something like that because the speedrun is like a zero to, like, one, right? Like, bro, this is. I'm built for this, bro. I'm literally telling you, bro. I literally, like, I only worked in, actually, you could do a good job. If you're not lazy. When you get the job, dude. I would, like, actually go actually, like, cut everything out, like, type all the. Hang on. I'm just reading this last thing. So. Okay. The zero to one empathy is made up. The post highlights founder and the BS cultural value because they need people who built from the ground up. Here's the play. Aditha needs to share war stories. He should talk about the pain of being a model, the frustration of optimizing coding agents or the late night shipping aside project. He can say, quote, I can Mentor Founders say this. I can Mentor Founders through the zero to one phase because I'm in the trenches doing it myself right now. I'm just taking notes. Yeah. This is also a good point. You should actually be prepared not only to expl. Ain a side project, but to share your screen. Have it ready. To share your screen for the project that's hardcore that you're most proud of. Yo, I'm gonna show them Ultra claw. I'm literally gonna show them Ultra claw, bro, on the thing. Yes. I'm gonna, like, be like, I'm gonna be like, check this out, bro. If they don't ask you, you should ask if you could show them. I did. I. That's what I did, bro. I went full autism on the. General. You were driving to the general. Yeah, that guy's a hoe, bro. Dude, you know what they said? By the way? Yeah. This how you talk to is a product guy. Yeah. Kind of a. Glory. Yeah. She's probably even less technical than the average engineer at a company. So don't be surprised if his questions are geared towards products. Team, things like that. And then you would talk to someone else after who's like, okay, this is their AI knowledgeable person. Don't be surprised if that happens, okay? Because he's on. This guy is only going to ask questions about that, like, he actually can understand what. What a good answer is. You know what I mean? Like, that's my guess is you would have another interview after this. Dog. Yeah. You know, they said it was. It was nine interviews, bro. And then I also have to do, like, a case study, and. And then I have to go and pricing and pitch a presentation, bro. It's, like, bro. Like, really? It's like low-key intense. But they said they would get done in a month. So, like, I know within April. I know a lot of work. Yeah, it. Dude, it's a lot of money, too, bro. I'm pretty sure it's like, yeah. Yeah, it's a good role, dude. Like, if you get a job there, you could probably stay there for, like, I'm, like, literally a VC is what I realized, like, actually, at, like, the end of the day, I'm just an ADHD ass. Like, I I don't want to, like, stay at one project, you know, type thing. Dude, I'll introduce you to the Stanford people I know. Like, look, I. Once you get there, I know Eric, and you can become friends with them. Like, Eric Tornberg, Katie kirschu. This girl's dad invented the computer mouse. They're so rich. He has the patent on it. That's retarded. That's true. She's from Palo Alto, bro. Dude, dude, this would actually be, like, a jump in, like, life, bro, if I get this, bro. Like, actually, life trajectory lead, bro. This girl's dad copsy are the one I was showing you. Her dad was, like, the mayor of La and, like, ran La, like, type. Are you serious, dude? That explains a lot. What the hell, dude? Yeah, she's a marketing hoe, bro. There's no way. I know. Yeah. She said he the easiest manager at Stanford. Dude, which one you say called science, technology and society. We used to hang out at para VC. Dude. Yeah, no, that's what. No, this pair VC retarded, bro. Like, they low-key, like, are investing in a couple. Like, dude, you're about front desk. It's my boy's startup. It's like a. I don't know. Is pair VC legit? Yeah. They are now. Yeah. They're pretty legit. Really? Okay. Yeah. I should look at their other investment. Spray. Dude, the guy was like, he invested in Dropbox out of YC and made, like, a billion dollars. That's. Damn. Okay, never mind. And then they've made tons of good investment. So basically, one of the guys is, like, a high school graduate from Iran who was a rug dealer and then hustled his way to YC demo day named page Von. And he hustled his way into yc demo day and funded Drew house through Houston. Right. And then his partner, mar. That's why it's called pige hair. P a page on bar. P e a r. Mar is a PhD in electrical engineering from Stanford. The other co-founder of the farm. Oh, my God, dude. Yeah. Yeah. And then they always just get Sanford grads to work with them for, like, two years, and they turn them and burn them and then hire new people, basically. Bro. I thought this was like a, like, dorm room fun, bro. What the hell? No, no, it used to be like that, but now it's legit. Damn. Crazy. Okay, okay. I got a couple more questions. Once a hot AI startup, everyone is excited about right now that you think is overrated and why. Damn, that's a hell of a good question, bro. I think most of the customer voice agent, like, startups are going to die out. The reason I think for sure, the reason I think so they've invested in one, I think. Oh, no, I'll tell them to straight up to their face, dude. Like, the reason I think so is because, like, the way. Commerce will occur is all through agents in the near future, as in, like, all through, like, GPT clawed. You already see, like, quad having, like, consumer dominance over GPT. Like, it's like the stats are ridiculous now. Like, literally, right? Like, claud has a vast hold on the consumer Market while gpt has a basketball Enterprise, but no one really cares about Enterprise anymore, for at least personal AI. Personal AI is where majority of spend is occurring as well. No one actually gives a about Enterprise AI right now. It's more of just a trinket solution, right? So it's just like. So for consumer AI, which is actually where, like, a majority of customer voice agents would even, like, also, like, interface with. It's, it's, it's, it's all B2C sales is what, like, sort of customer voice agents are targeting. I believe that because claude will become more autonomous and have a, like, more tool integration and more MCP capabilities autonomously and be able to think autonomously. You even see this with Amazon Rufus and Amazon shopping. Bro. You're right, but it's a good answer. How much, bro? I, like, just be rambling, bro. I don't know how to solve this problem, bro. Okay, you need to just think about, like, what's the main bottom line? And then as you get to the point, like, you can add in details, but make sure they're very important such that you keep his attention the whole time. If you're just saying the important, juicy, it'll keep his attention. And that's the perfect way to do it. But if you go on for two minutes, I'm not saying anything won't be necessary. You don't have to agree. I don't want to make, I don't want to born a duty, dog. Like, okay, so, like, how would you, how would you, like, responded to that? Like, like, with my response, but, like, in, like, you know, concise. Things and, and fewer words, it's, it's a sign that you have a very strong thesis and a very strong conviction. Because you're just like this industry. And here's why rather than explain it too much. Right? Yeah, exactly. Yeah. You look, like, talking longer, lowkey. Actually. You're not that bad because some people just put in fluff and you're just elaborating on your thought process. But if you can pare it down a little bit, it's probably good. Yeah, dude, okay, how would you have said that? Like, like in a concise way. Like my, my response, but, like, concisely. I mean, do you want to just try it again? Yeah, I guess I'll go to another shot. Okay. I think, I think an industry startup everyone is excited about right now that you think is overrated and why. I think consumer voice AI agents because of the following rationale. Consumer voice AI agents are primarily focused on B2C, and B2C is increasingly being dominated by a genetic tools, a tool calling services like anthropic. You also see a lot of this trend with tools like Amazon rufus, right, which is an agentic shopping experience, even on, like, you know, probably the flagship sort of online shopping experience. Right. Amazon. So as a result, I think consumer voicents will die out because their domain will die out as tool call agents will get better. Okay, good. You got, you said everything you need to do. I think that was good. See, but the thing is, dude, like, it, like, it, like, it required, like, one iteration. Like, of me to just get my thoughts out in order for me to present it well. So how the do I do that first time? Like, that's my thing. I think the more you practice, probably the better, I would guess. Here, let me go. Hang on. Let me look at these questions and think what will Jonathan actually. Because he is a product. Let me check his link down one more time. Senior director of business development gaming product. Yeah. So he's a non-technical. Bro. Do pair. Pear literally back door Dash, bro. That's actually ridiculous. Yeah, I thought these guys were niggs, bro. That's actually crazy. Okay. How would you tell a founder their idea is bad without losing their relationship? If the founder is a good founder, they wouldn't care. You. That's my response. Concise. Are you serious? Yes. I don't know if that's a. Good. That's a. Okay, fine, fine. Okay. Legit response. I'm not sure if that's a good answer. You want to know the right answer? Yeah. No interest your capital. This is the right answer. Okay. I would seek to be constructive with the founder, understanding that people can grow and learn over time. And I'd want to help him on his path of entrepreneurship, because in the future, he might be. He might be someone that we want to back on his next idea. So I would definitely seek to preserve the relationship. But I would also be straightforward and honest with my criticism, but help and make sure it's constructive. That's the perfect answer. Yeah. Yeah. Okay. Makes sense, though. Why? Very PC facts. No, it's not just PC, but that guy may come up with another idea on the second time, and then Andreason wants to back him. So you don't want to lose any relationships in venture. You want to, like. And they also actually be looking for you. Can you hang? Can you really be. Can you. Are you like, could we take you to the mark Andreessen's house? For the offsite with all the employees? And you would be friends with everyone. Like, they might actually be looking for that because you do have to be friends with all these Founders. Yeah. And, like, dude, if they're. If you're at a networking event and you're representing Anderson or you're at a conference and there's a founder on stage, and then you're backstage in the VIP room, you need to win the deal flow. So, like, it is also, like, important that they feel. So just. Just a side thing. I don't know if that's the number one thing they're going to be looking for, but that definitely is a real thing. They feel so, bro. I, like, literally. Yeah, dude, in person, like, literally. Okay. Anyways, fire. How do you think about evaluating technical mode for an AI startup at the pre-seed stage when there's barely any product yet? Almost always association with Academia. If there's any significant technical moat and there's no product, the only way you can back that is with significant previous research experience or some form of IP mode. That's the only way. Is that a good answer? I don't know. So the claw says critical question for this rule. At pre-seed moat is mostly team plus insight plus early data flywheel thesis. You should be able to articulate what signals suggest durable differentiation. Versus a wrapper that gets commoditized in six months. Wait, what was it? What was it? Sorry. The mode is mostly team Insight and early data flywheel thesis. You should be able to articulate what signal suggests durable differentiation versus just a wrapper that will get commoditized in six months. How would you answer that? That's like a response. Yeah, I think. I think it's. I don't know that you want to pigeonhole it into academic background. I would. I would. I would not say that. Because, dude, yeah, be careful saying that. How do you evaluate the technical? Okay, I think probably you would want to say something like. The. I don't pre see the moat is mostly team, but it's also the market Insight. The unique market insight. This is literally true, by the way, for venture. Right? For angel investing. Like, seriously, for early stage investing, this is true. The team is the most important thing. I knew Alexander way when he started scale. What can I tell you? He pivoted. They were doing something different than scale. What does that tell me? Team over everything else because he figured out how to do it despite having originally applied to YC with a totally different idea. So number one, what I would say is this. At the precede moat is mostly T plus insight. Plus early data flywheel thesis. And I would seek to understand if I thought they had a strong team, a unique Insight about the market that would allow them to develop the flywheel for data. Because if they can collect enough data, it will be hard for even the large language model companies to commoditize what they're doing if they built a flywheel to capture the data. So actually, the technical strength isn't the only thing that matters. It's also like data. Yeah. For the product. Yeah. And, and then make the, if they understand that you realize it's more than just. Yeah, I don't know. It's a tough. I'm not 100. No, no, no, no. That's a golden response. I'm just a retard. Like, I would talk about deep, deep gram, actually. Deepgram has a data flywheel where all their customers actually feed back into the, the large model. So Granola, vapi, all these models actually use deep grams foundational research models. Same thing with cartesia with solid state models. All their customers actually feed all their data back to the model provider so that the model continues to improve for cheaper API rates. So things like that can definitely mention. I'm an artist. I think look, you got this in the bag, I think. Dude, I just need to go full autist on this. I just need to be like a sociable autist. You know? Yeah. Okay, what else? What else? Yeah, yeah. They need to confidently explain how they evaluate a tech stack, bro. Yo, are there any standard BC frameworks? Yo, are there any standard. Sorry, sorry. Are there any standard VC Frameworks that you can, like, sorry, my phone's about to die, bro. I'm gonna call you back for. My. Yo. What's good, bro? Sorry. My phone died. Dude, can you hear me?

**Other:** Yeah.

**Me:** Sorry. Wait, so you were saying. You were saying something, and then the chick got cut. We were talking about, like, the. The data feedback loops and. Oh, I was asking about VC Frameworks. VC framework. What should I mention?

**Other:** I don't know exactly what that means.

**Me:** Like. Like these guys are all, like, ex-bankers, bro, right? So, like, my boys were like, oh, you should study DCF, like the three, like, you know, balance sheets, all that.

**Other:** Probably literally around.

**Me:** Like, how would you value, like, okay, they ask you that. Okay, I'm.

**Other:** Okay, the answer is. Okay, I think I get what you're saying. And it actually kind of feeds back to what we were just talking about, that maybe that's how you thought of this.

**Me:** Comps.

**Other:** But what do you look for with an early stage startup? If they said, like, what are the three main things you look for? Like, number one. Is team. And I just explained why I gave you a real life example in my own life. I knew Olesander wang. He's such a strong founder. He pivoted into doing what with Lucy grow and lucy. They pivoted into doing scale AI from another idea, but they. He was such a. Genius, right? And. And perseverant person that he figured it out. So if you just bet on smart people, odds are they figure out how to make it work, whether it's a pivot or whether it's running through walls.

**Me:** Smart. How do you define smart? What heuristics could I mention on the call?

**Other:** So. I I didn't say. Well, I didn't. I mean.

**Me:** Like, you're claiming he's capable. What. What signified that he was capable is my collection.

**Other:** Oh, I'm not saying I knew he was going to build that big of a company, but all I'm saying is if you. At the seed stage, the point is this, like, Adyen stage or pre-seed stage. It's hard to judge just based on the idea because it's so early. So you also have to take into account just how good the founders are.

**Me:** Dude, but I'm saying, like, I get. Now I get that. I'm saying, but, like, what? Like. Like, what actual metrics are you looking at to signify Founders? Good?

**Other:** Venture capital at the early stages in art and not a science. So it's not just metrics.

**Me:** Response?

**Other:** No, that's 100 true. I'm telling you that.

**Me:** No way. You see, you're saying, okay, it's like. It's like your intuition.

**Other:** It is an art. It's dude. Private equity and stuff is a science, but that's why they go in with spreadsheets and, like, cut cost. Venture is an art where the valuations are made up and people are making guesses. They're making bets on lots of people, and then they're trying to figure out how to be good at it, which is why it's an art and not a science. If it were a science, then a robot could do venture capital. But even Mark Andreessen himself, dude said he thinks venture capital is, like, going to be one of the only jobs after AI takes over because it's not a scientific thing. It's literally like maybe art is the wrong word, but it is like an intuitive.

**Me:** Yeah.

**Other:** Like. If you have to, you have to have a feel for, like.

**Me:** Process. Yet.

**Other:** Yeah, like, if this, like, dude. Yeah.

**Me:** Though, dude. Like, in an interview, like, what the am I gonna say? Yeah, bro. Like, because I know good.

**Other:** I. Don't.

**Me:** Like. Like, that's what I'm trying to think. Like, because, like, you know, in, like, interviews, like, dude, maybe I'm just overthinking it, you know, type thing. I feel like there's going to be a chill ass conversation.

**Other:** Actually what will realistically, they're not trying to figure this out in one phone call. But if you got the job and you started doing this job for a year, they would watch to see if you start learning from seeing Founders. If you can develop pattern recognition of what a good founder, what a winning founder looks like versus a not winning founder. And then when the winning founder comes in the room, you cut them the term sheet. That is what they would be trying to figure out is if you can develop that sense as a VC of who is it looks like a good founder and then bet on that founder.

**Me:** Yeah.

**Other:** So that's ideally what you'd figure out how to do.

**Me:** Yeah. Facts.

**Other:** So. Yeah.

**Me:** Yeah.

**Other:** Do you want me to ask more questions or what do you think? Okay. How do you think about the build versus buy decision when advising a founder on their AI stack?

**Me:** The build versus buy. What are you saying?

**Other:** How do you think about the build versus buy decision when advising a founder on their AI stack?

**Me:** Oh, my gosh. Literally exactly what I'm talking about, bro. Okay.

**Other:** Yeah.

**Me:** Basically, if there's deep research context that's needed, then kv caches need a ton of Ram costs. This eats into API cost because it's their large token windows. So for any deep research context windows, I'd say go local for any long running contextual processes or any stateful memory processes at, say, go local for anything else where it's like just periodic batch training or batch jobs that can fit within sort of rate limits for cloud Max. I just say go API cost. But if it's a recurring process, then Hardware will most often pay itself off, although in recent months we've seen a massive Rams price spike. So remains to be seen.

**Other:** Okay, that's good. What's the most interesting thing you built with an llm that surprised you? Where it performed better or worse than expected?

**Me:** In my ultra claw instance. I built in a self-learning loop where it's a self eval self eval agent that basically evaluates the performance of every transcript. So it reviews every transcript from every agent session and then determines what went wrong, what went right. The reason why I think it performs better than I expected is it's actually improved upon itself. It's. Oh, it reviews its own agent transcripts and it tangibly has dispatched jobs that have actually not only caught security bugs that could have released api keys, but also has upgraded open claw itself. And is improved itself to actually be more of a more capable reviewer. That's a terrible response. I'll tighten that up. That's some low-key. Wait. Said that, bro, low key. What would you have said?

**Other:** Okay. I think it's fine. I think that.

**Me:** Okay.

**Other:** We see hundreds of AI pitches per week as a technical partner tasked with thinking critically about new technologies. How do you quickly differentiate between a startup that has a defensible technical mode and one that is a thin wrapper around an open AI API?

**Me:** So one is if it has a tangible Improvement on a flagship Benchmark compared to a flagship model, we saw this with willow most recently. I'm comparing itself to a live and Labs, more Flagship models and having nearly double the performance for speech to text. That's a solid technical mode. Otherwise, if it has a large corpus of data that can collect this proprietary, we saw this and then it can monetize on. We saw this with niantic monetizing their data.

**Other:** Yeah, that's good.

**Me:** Or if there's a way to acquire large customer base that wants to spend recurring Revenue and you learn and achieve a data flywheel approach based off that customer, we achieved that with friend.com, which is a mark for trinket solution. We'll learn from its users in order to generate a genuinely massive corpus of human like data.

**Other:** Okay. Yeah, that was good. So it, it said how to answer. You should outline the exact technical heuristic, what architecture choices do you look for? Do you look for proprietary data loops, custom fine tuning or novel agentic infrastructure? They need to sound like a technical auditor here. Yeah. So I think you got that one. Okay. As an investor.

**Me:** I think I should have gone more technical. It said.

**Other:** Okay. Yeah, yeah, yeah. Yeah. So that's how you should answer that, by the way. So. Okay. As an investor, you aren't writing the code yourself anymore. You're helping Founders make progress across product and Technology. Tell me about a time you had to guide another engineer or team through a complex technical blocker without just doing the work for them.

**Me:** When I was running go to market at a company layer. We had a massive deal on the table with a company called ether five. They had 6.5 billion dollars in non-unique stake that they were bought deposited in TVL into our brief staking protocol. In order to do that, though, they wanted to see a proof of concept developed. And they were also hesitant about the deal. And so I'd done some thinking from a product lens, and I determined that they had massive issues after speaking with a couple of their internal Engineers at multiple conferences. I had come to the conclusion that they had massive issues with rewards calculations. For their restaking platform. So I expect out a very detailed sort of rewards calculator. And given that to the engineers to, to sort of manage and deploy, the first iteration was kind of garbage. Honestly, not gonna lie. And then we just achieved sort of a product engineering feedback loop internally, and we ended up shipping a product that they still use to this day for rewards calculation and also ended up closing the deal. That deal ended up in two more. Deals closing with figment and renzo and kelp, actually three more deals. Which ended up placing us at the second largest restaking platform by tbl in the world at nine billion dollars in TV. O.

**Other:** Okay. Speedrun is focused on first money and investing at the frontier. If you had a blank check to write right now to one open source project. Github repo or solo Dev, you've interacted with online. Who gets it and why? Yeah. This proves if you're really in the Builder community.

**Me:** That's a question, bro.

**Other:** So. What the.

**Me:** That's a crazy ass question, bro. No way, bro. I'm. I don't know. I can't see on this. Let me think. I got a. Hold on. I got a. Come on.

**Other:** Or just fine figurine later.

**Me:** Yeah. I gotta do some reading, man.

**Other:** But if you just, like, made up a name. But, like, set it with a lot of conviction.

**Me:** It's sort of like pushing this hard, bro. Like, literally. Oh, yeah, I could. I could actually, like, say something legit. Okay, so one of my boys is building a product called. It's a called, bro. It's a made up name, but I just come up with some right now. Dude, what the is it called, bro? Synthify. And so it's basically that literally does sound made up low-key but, like, they're basically forecasting time series data using multimodal heuristics. And a reason I think that's extremely important right now is because we increasingly are quantizing sort of moments in history with, with things like poly market call sheet, Etc. We're getting moments in history and points of human opinion where we can also start tracking deltas, things like mirror fish that went viral recently have proven out that, like, using multi-agent sort of debate models, we can actually achieve some level of future forecasting. And I think we could really be cool because we had, like, almost like a AI that could or AI Oracle that could almost predict the future using, you know, these probabilistic simulations simulation models. So I think for that reason, I'd fund that. What did I even say? What was my.

**Other:** Okay.

**Me:** Who is the guy?

**Other:** I have no idea.

**Me:** Dude, I literally forgot who I said I'd find. Like, that's how ADHD I am. What the. What did I say? What was my argument? Miro fish. And then why mirror fish? Why do we get to mirror fish? Dude, I would note take her on. Hold on. I'm, like, actually tripping right now. What the. Synthesize. Yeah. Time series. Okay. Yeah. All right.

**Other:** Okay. Okay. Ready?

**Me:** Yeah. So I need, I need to read up on developers.

**Other:** So. Yes, you should have an answer for that, for sure. We love people with a side project or multiple side projects currently going on. Okay, let me give you a hint for this question, and then I'll ask you the question. Okay. Vulnerability is key here. VCs know that zero to one building is messy. You should be able to get technical in the answer about why it failed. For example, latency issues, context window limits, bad data formatting. And what that taught you about evaluating future startups? So here's the question. We love people with a side project or multiple currently active. Tell me about a side project you built that completely failed or hit a massive technical wall. What was the wall and what did you learn?

**Me:** Okay, we're building verticalized judge models for Mosaic evals. And initially what we thought we could do is just build a complete sort of, like, from the ground up eval structure where it would be a completely new type of model architecture for verticalized judges. And so this would be like foundationally trained from pytorch, right from the ground up based off of customer data. Well, we quickly realized this with a large corpus of customer data, this becomes quickly, quickly very, very expensive to do. So as a result, you have to use a foundational model and fine tune it based off customer data in order to run eval. And so what we're doing now is basically using open source eval model structures and then sort of cultivating, you know, massive context windows. And based off of Google's research paper, this is actually a more effective approach because agent harnesses matter more than the agents themselves.

**Other:** Okay.

**Me:** Now buy them. I'm prepped, bro. I'm locked, bro. Come on, bro. You heard that.

**Other:** All right. Ready?

**Me:** In your pants for your partner a16 z, bro. You'd be like, we need to pay this seven figures, bro. We need this Indian, bro. He's smarter than me, bro. I need to get this kid as a partner a16z. Literally, you wouldn't say that. That's a go to respond for a goden. Okay, what's next? I've been giving him. I would have been given hits. I just need to, like, I need to, like, I need to, like, read up more on, like, BC Frameworks and probably, like, how do you actually evaluate a deal? I look, you need to ask you, dude, like, how do you, like, you were at park Avenue? How did you evaluate deals? What was the deal flow structure? What does a16z maybe look like when evaluating, like, a thing? Like, what is a firm structure look like? Right? Like, I'm coming in as a analyst. Like, I understand that. Like, it's not. It's partner, but it says partner is not a partner. It's like a junior analyst. How do I. Like, fall into place? Like, what does, like, my job look like? What do I need to be good at? What skill sets do I demonstrate? On the call to, like, you know, be like, all right, it's this thing. Obviously, I can't give them a reason to say no, bro.

**Other:** All of these questions are, like, very relevant to getting an understanding of you. And if you have the skill sets. So VC, and if you have the skill sets to be able to figure it out on the job, VC is something you have to learn on the job. And you literally actually learn by number one, making investments and seeing how they go. And then also meeting Founders and seeing their journey unfold and being like, okay, that guy had the dog in them. We should have backed him or like blah, blah, blah. So you literally just learn over time doing the job. The best thing that I can say makes you a practically good VC is having been a founder and Builder yourself, because then you'll be able to pattern match with yourself and be like, oh, I had that dog in me. I built this company. That guy also has the dog in it. I should back this guy. Right. So having actually been in the founder's shoes can help a lot. Having actually built AI is probably helpful to evaluating AI startups. But it is a bit, it is a bit of an art and it is a bit of a picking people person business. So. Let me see.

**Me:** Yeah.

**Other:** What's your, what's your view on where AI sits and the create fits in the creative workflow tool collaborator or replacement?

**Me:** Which one?

**Other:** What's your view on where AI fits and create in a creative workflow? Is it a tool collaborator or a replacement?

**Me:** Quickly become a replays mat? It already has several open funds and says, in fact, I have a local sort of open client stance that's running ugc for eclipse right now. Which is one of my contracts and it auto scans sort of for certain hashtags and pulls certain things from YouTube using a dlp API. All that means is basically just pulls multiple metrics based on product context windows and auto creates posts using higgs field, which is a video generation service. This is being done, like, today. Right. And I think in the near future, we'll actually see this be a complete replacement where agents are just going to be able to autonomously operate. Yeah, that's all.

**Other:** Okay, what creative category do you think AI unlocks that literally could not exist before? Not just faster. But fundamentally new.

**Me:** Dude, you're actually hitting some crazy questions right now, bro.

**Other:** These are some of his theses because he does creative gaming. So.

**Me:** Oh, dude, you actually.

**Other:** Jonathan published an article AI learned to talk. Now it's learning to build reality. He thinks about AI enabling entirely new creative formats. Adithia should have a genuine specific answer, not AI music or AI art. Think interactive narrative personalized simulation real, real time world building.

**Me:** Okay. Okay. I think.

**Other:** What creative category do you think AI unlocks that literally could not exist before and is fundamentally new?

**Me:** Okay, this is super futuristic and kind of dystopian, but I think in 20 years, we already see sort of, you know, people addicted to their phones. Right. This is a 2D medium. It's like a flat screen. Right. I genuinely think, right, that, like, people are already picking their phones over family members, like, etc. It's like a very addiction. No, genuinely. Right. Like, it's like, it's a very addicting medium, right? The consuming content is like a new meta. I think entertainment will be like a huge part of our life as agents get more autonomous. And I think the future of entertainment is literally like entire new world personalized simulations per each individual. And what I mean by this is we already, we've already digitized the fruit fly's Consciousness by mapping its individual synapses and putting it into a neural network and not training the network at all. And the neural network behaves exactly like a fruit fly. We've done this with a mouse brain. It's only a matter of time before we do this. We have the ability to do this with a human brain. You know, it's only a matter of time also before people, you know, want to escape this reality in a well, in a way as well. Right. Very dystopian statement, honestly, in my opinion. But, like, I think it would become a reality in 20 years, right, where folks are, instead of choosing sort of real life, they're already choosing their phones instead of choosing real life. They're going to actually do simulation, right, where they can actually do whatever the hell they want to. So I think that's potentially, you know, really crazy new unlock that we're going to find with, like, you know, I think near short-term research. It might honestly be commercially viable already, and we just don't know about it. Some.

**Other:** Nice.

**Me:** I don't know if that's some crazy to say, bro, but honestly, it's facts. I do be thinking that. Well, how do you respond? How would you respond in, like, a more tame response to that?

**Other:** Okay. No, I think it's good. It's good. I'm trying to think. I'm getting tired, so I'll probably have to go in a little bit, but we could do a couple more questions.

**Me:** Of course. Of course.

**Other:** When you're evaluating a startup, how much weight you put on the market versus the team and how does your view changed over time?

**Me:** Oh, God. The market is important, but the team can figure out another Market as well if they're capable. So the team is probably the most capable thing that I would evaluate. Or the strongest heuristic that I would use to evaluate. Success or early stage.

**Other:** But how do you weight them relative to each other?

**Me:** Team 80 Market 20 early stage. If it's a series a company, that weight differs tremendously. It'd be 50 50. Anything beyond that market.

**Other:** Okay, nice. Okay, got it.

**Me:** Takes prior. Ity.

**Other:** How do you think a16g speedrun creates unfair advantages for its portfolio beyond the check?

**Me:** I don't. Y'all are. I don't know, dude. Like the brand name definitely is helps teams open. Not as a response. What do you think? What do you should I say? I should be like,

**Other:** The network, the brand and the founder community?

**Me:** That's, bro. What else can I say, you think?

**Other:** No, it's not.

**Me:** But, like, network, like, anyone can say that. Like, found a community. Anyone can say that. How does a16z create an unfair Advantage? Oh, brand name.

**Other:** Okay, well, if you get that question, that's probably what you should say.

**Me:** You're right. You're right. But, like, is there, like, is there another response I could say, like an intangible, do you think? Like, I agree with you. Like, that's definitely the response, I should say. But, like, I'm wondering if there's, like, a better response.

**Other:** So. You're gonna have to say something that illustrates that you understand that they are.

**Me:** Than.

**Other:** The diff, the difference between financial capital and strategic capital. Right.

**Me:** I guess. That's a very, dude. See, this is the, this is the type of the terminology, bro. I need you to educate me on the terminology.

**Other:** So it's. Up.

**Me:** What did you just think? Can you repeat that? Financial capital versus.

**Other:** Basically.

**Me:** Capital? Bam. I'm going to use that.

**Other:** Yeah.

**Me:** Okay. What else? What else? Like, okay. And how do I, and how do I be like, okay, you guys are strategic capital because you guys offer introductions to other, like, like Founders. Right. The founder community is.

**Other:** Okay. Okay. Okay. So I don't know if you know this, but. And they're very different than other firms. Because. They. Really pride themselves on being strategic capital. Right. Mark Andreessen talks about the reason he started injuries and poor witz because he wanted to build a better venture capital product for founders because he thought it was just basically money and nothing else when he was raising money. So if you can. So I would basically, I mean, they don't know that this is that important of a question to ask you. Like, there are probably better questions, but basically you'd say, look, I think the talent density and the founder community that speedrun has built, you know, makes it valuable for people to participate. And I think the network and the brand. I don't know. I mean. Like, do you know much about Andreessen?

**Me:** Now, dude. Is there anything else? I should definitely meet up on this? One?

**Other:** They try to plug. Dude, they, they, if you get an investment from andreeson that you can, like, Outsource your whole team to them. Like, they have a recruiting arm. They have a marketing arm. They have a PR arm, and they'll help your company do all these things. So they have a very value added system.

**Me:** Got you. I got it. They get involved in there. Okay. They get involved in their Investments. Okay. And speed run needs to kind of mirror that. But, like, there's already, like, teams like that. Actually, it's kind of what the HR guy was kind of telling, telling me to. Okay, interesting. Okay, nice. So why 16z over anyone else? Because I like to take an involved approach in early stage companies that I involve myself in, and I, I see the same approach that you guys mirror. And as such, I think this would be a perfect fit for me. Okay, bang. Very nice. Dude. What are some of the intangibles, right, that you kind of learned about, like, by just working at a VC? Right? Like, I can't just, like, you know.

**Other:** What do you mean?

**Me:** Like, as in, like, like, what are, like, what are some of, like, the intangibles that you've, like, learned by working at Park Avenue? Right? Like, like, just, like, on the Block. Like, you're just like, bro, like, you can't learn this by just, like, looking the up online about.

**Other:** Okay, you, you, you did. If you wanted to be like the best VC in the world and you wanted to, like, make a shitload of money, all what you would really need to do and what a lot of the good VCs do, like, especially the ones who don't miss. Like, if, like, by the time a good company has come through the valley and started pitching all the funds and got to see it in series a, the ones that don't miss, they have their ear to the ground and hear about everything because they have other friends who have their ears to the ground and those friends report back to them. And so they're just constantly in communication and, like, plugged in hardcore. So, like, being a VC who. Has sources and, and other people and a network of people who will share deal flow with you, it, like, you actually can Outsource your thinking entirely if you have enough smart people giving you advice on what to invest in. Which is kind of, it's a herd mentality in too many VCs do this and then add no value versus, like, Peter teal, who thinks for himself. So it's a different way to do it. But, like, it's very valuable to have. Yeah.

**Me:** Okay, that's matt. That's mad fact. So you're basically like, dude, I need to have, like, I have home. Like, that's what I need to emphasize.

**Other:** You know.

**Me:** It's like, I have homies on the ground that, like, know who's good, right type thing. And they can also, like, like, refer me to them type thing and get me into deals that, like, are good type thing. Like, my boy, like, my boy invested into, like, applied compute, like, like, major things. Applied computes co. I carpooled with the like, should I mention things like this?

**Other:** Maybe.

**Me:** Would it be worth it because to a GP, bro, why the would he care? Like, how should I approach this specific conversation with a gp man is my question. Like, the, the, like, pop, bro. Like, he's got it. Like, so what the do I like? What value do I offer and, like, type things? Like, you know, like, they already have a network. They already know how to source. So what value do I add? Like, what do I emphasize, I guess.

**Other:** The last part. Sorry.

**Me:** No, no, I'm just saying, like, how do I, like, demonstrate value to this guy? Like, who's a GP that's already popping that, like, has, like, you know, sourcing already complete?

**Other:** Here's what you say. For him, it's going to be less that you need to build out of that network of seed and series a deals. Right. But.

**Me:** Yeah.

**Other:** The same skill of building that network of people sharing information and really you being in the know and influenced by the people you're around the most, as I was saying earlier, keeping your network level very high. So when high level people enter out of nowhere, you hear about the cracked Builder, and then you're like, hey, apply to a16z speed run, and then you found them. Right, right. What you need to show is that you can apply that same type of thinking in network building to pre pre seed scouting. For what he's doing. Like, that's why getting off of Twitter and conferences is really valuable because it's a different stage of company. Does that make sense?

**Me:** I agree.

**Other:** Makes sense, kind of.

**Me:** I agree. This makes sense. And, like,

**Other:** That would make you also the perfect partner for speedrun if you're able to do that.

**Me:** It's facts, dude. All I do is travel. I need to tell him that. All I do is travel, and all I do is, like, scroll on Twitter on the rally. Fire.

**Other:** Well, you don't want to say that's all you do. But. Yeah.

**Me:** Okay.

**Other:** Right. But, okay.

**Me:** That's why I don't want to take up too much. Yeah, I know you're probably exhausted, dude. Now, thank you for the.

**Other:** I'm exhausted. No worries. I need, I need some 2C, bro.

**Me:** Team. Yeah, dude, some toot, bro. Some K2.

**Other:** Some tooth. Oh, that sounds good.

**Me:** Makes.

**Other:** Oh.

**Me:** Dude, if I get.

**Other:** All right. Wait, when.

**Me:** If I get this job, Avery, I'm buying you a Grand.

**Other:** Is. Okay, sounds good.

**Me:** Easily. I actually easily work. I'll fly to New York, literally.

**Other:** All right. Yeah, maybe announce. At least, at least three or five grand, please. So when is the interview?

**Me:** Tomorrow, dude. Literally.

**Other:** What time?

**Me:** Like 1 30. I'll, like, keep. I'll keep you posted.

**Other:** All right, make sure you get some sleep and, like, eat and drink and. Okay.

**Me:** Dude, yeah, facts.

**Other:** All right. All right. Well, I'll let me know how it goes. Okay.

**Me:** Yes, sir. Dude, appreciate you, man.

**Other:** All right, bro. Catch you later. All right. Good luck. You got this.

**Me:** Thank you. Thank you.

**Other:** Bye.

**Me:** Nothing.
