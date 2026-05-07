---
source: granola
workspace: personal
ingested_at: '2026-05-07T04:23:57.244510Z'
ingest_version: 1
content_hash: blake3:80a5bc7fc2669af7b3d9c17ddaa459b95336c486e0a686dce26b0f25e388e96a
provider_modified_at: '2026-04-17T21:47:49.397Z'
account: adithya@outerscope.xyz
account_slug: adithya-outerscope
document_id: 354db6b6-b5f4-47b9-8e33-026c74ae0e1f
document_id_short: 354db6b6
title: a16z Remote Interview Confirmation - Adithya Kumar **Please Confirm**
created_at: '2026-04-17T21:00:56.755Z'
updated_at: '2026-04-17T21:47:49.397Z'
folders:
- id: db8d0de1-40e5-4cfa-943d-65a5f3837095
  title: PERSONAL
- id: 3b7a1171-eafe-4748-a400-d5bb4292d2ce
  title: HIRING
creator:
  name: Adithya
  email: adithya@outerscope.xyz
attendees: []
calendar_event:
  title: a16z Remote Interview Confirmation - Adithya Kumar **Please Confirm**
  start: '2026-04-17T14:00:00-07:00'
  end: '2026-04-17T14:45:00-07:00'
  url: https://www.google.com/calendar/event?eid=bWwwb2hldWE1dDQ3ZDc4NHIgYWRpdGh5YUBvdXRlcnNjb3BlLnh5eg
  conferencing_url: null
  conferencing_type: null
transcript_segment_count: 181
duration_ms: 2740960
valid_meeting: true
was_trashed: null
routed_by:
- workspace: personal
  rule: folder:PERSONAL
---

# a16z Remote Interview Confirmation - Adithya Kumar **Please Confirm**

> 2026-04-17T21:00:56.755Z · duration 45m 40s · 1 attendees

## Attendees

- **Adithya** (creator) <adithya@outerscope.xyz>

## Calendar Event

- Title: a16z Remote Interview Confirmation - Adithya Kumar **Please Confirm**
- Start: 2026-04-17T14:00:00-07:00
- End: 2026-04-17T14:45:00-07:00
- URL: https://www.google.com/calendar/event?eid=bWwwb2hldWE1dDQ3ZDc4NHIgYWRpdGh5YUBvdXRlcnNjb3BlLnh5eg

## AI Notes

### Interview Overview

- Dylan Rhodes, CTO at Andreessen Horowitz
- Panel interview process - notes shared between panel members
- No access to previous conversation with Rusty
- Focus on personal agent/doppelganger thesis

### A16Z Business Understanding

- Involved capital model vs generic funding

    - Opens doors for portfolio companies
    - Differentiated from predatory crypto investment patterns
- Two-pronged approach:

    1. Deal sourcing and due diligence edge
    2. Zero-to-one support for early stage companies
- Role involves implementing agentic processes firm-wide

    - Business process automation
    - Information parsing and decision-making at scale

### Personal Agent Architecture

- Built custom system on OpenClaw foundation

    - Kanban task management with Notion integration
    - 12-13 specialized agents with auto-pruning/merging
    - Fan-in/fan-out debugging model using multiple Sonnet instances
- Context management approach:

    - Thoughtful file structure with [index.md](http://index.md) annotations
    - Vector stores using Quadrant + SQLite
    - Gemini embeddings (4096 vector, cents per million tokens)
    - Moved to light RAG system due to mem0 limitations
- Self-improvement capabilities:

    - Session transcript analysis via cron jobs
    - Automated remediation task suggestions
    - False positive/negative feedback loops

### Practical Implementation Examples

- Go-to-market automation for client:

    - Daily context extraction from Slack, GitHub PRs, Granola notes
    - Lead identification via Apollo, Firecrawl, Exa search, X scraping
    - Custom cold email generation (1000/day)
    - Auto-booking with calendar integration
    - Solutions engineering approach with pre-built demos
- Experimental viral content optimization:

    - Using Facebook’s Hive fMRI dataset (700 people, 14k hours)
    - Brain activation pattern analysis for video content
    - Reverse engineering viral triggers through Hedges Field
    - 1000 video/day generation ranked by activation similarity

### Role Vision at A16Z

- Leverage role rather than pure execution
- Map partner/operator time inefficiencies

    - High-value judgment wrapped in low-value tasks
    - Research compilation, memo scaffolding, routing
- Near-term: Compress time around judgment processes
- Long-term: Reusable agent modules across firm

    - Memory, evaluation, permissions, workflow orchestration
    - Regulatory-compliant guardrails

### Mark Andreessen Agent Design

- Simplified v0 approach vs personal experimental setup
- Three core components:

    1. Strong context ingestion of Mark’s processes
    2. High-quality summarization and prioritization
    3. Tightly scoped action layer
- External signal identification for deal flow
- Chief of staff layer vs general chat interface

    - “What matters today” decision support
    - Three key updates vs 40 market noise items
    - Confidence and provenance guardrails
- Reliable decision support system with memory and selective execution

### Current A16Z Priorities (Q2 2026)

- AI DevX theme: Every 700 firm members now engineers
- Vibe Apps platform:

    - Zero-friction internal app building/deployment
    - Authentication concerns for public-facing apps
- Doppelganger project expansion:

    - Personal agents for all firm members
    - Starting with experts, GPs, Mark and Ben
- Success metrics: Meaningful contributions to AI DevX projects
- Context suggestion approach: Progressive discovery, agent-driven, breadth-first

### Next Steps

- Dylan sharing notes with panel
- Feedback expected from Rusty by Monday
- Adithya to share Pi agent research link

---

Chat with meeting transcript: [https://notes.granola.ai/t/6ea5e37d-7b18-4ddc-b10e-e8de8e3b9c85](https://notes.granola.ai/t/6ea5e37d-7b18-4ddc-b10e-e8de8e3b9c85)

## Transcript

**Me:** Hey, Dylan. How's it going?

**Other:** Hey, it's going well. It's going well. How are you doing Aditha?

**Me:** Doing well. Doing well. Sorry. Let me see if I can get this note taker out of here. I know Rusty was telling me.

**Other:** All good.

**Me:** Do you have admin access to this call by any chance? Okay, perfect.

**Other:** Yep.

**Me:** I don't know if it's Sarah's call or whatnot. I know she said that. She.

**Other:** Okay. Here we go. Hopefully maybe Sarah has. This and see if it works.

**Me:** Yeah, me log into my fireflies and see if I can get this out. Too. How you doing? Where you. Where you calling in from today?

**Other:** I'm doing all right. I am here at the SF office. So over on Townsend, just between. The Caltrain station and the ballpark.

**Me:** Nice. Now, I actually was just out there last week, man. Do you know where the human X conference by any chance. Or.

**Other:** Yeah, I actually, I had brunch with a woman, Sam.

**Me:** The most.

**Other:** What is Sam's last name? She's a leading AI. Product transformation, internal stuff for Deloitte. She's fiance of an old friend of mine, my brother. And so we'd actually connected at his wedding a few weeks ago. And then she came out from Denver. And for that conference, and I caught up with her for a few hours the prior Sunday. So I heard a little bit about it. I wasn't there myself. But yeah, I think she had a pretty good time there.

**Me:** No, 100. I think we compared to GTC was definitely more like software focused. You know, GTC was everyone's just pushing chips, you know, on each other. So rebris had their, like, you know, brunches every day type thing, you know, all that stuff. But definitely more software focused. I think a lot of kvcash management projects this time diffusion models being used as, like, token streaming, like a bunch of cool stuff actually coming out right now. But, yeah. Oh, perfect. Thank you. Okay. Right.

**Other:** Cool. All right. Yeah. So super nice to meet you. So Dylan Rhodes, I'm CTO of Anderson Horowitz, and lead engineering here.

**Me:** On.

**Other:** Thank you for taking the time to talk to me. Obviously connected via Rusty, Shan, various folks who are kind of leaning on this one. But I have been fairly heavily involved with the panel discussions to date. So just wanted to let you know, I have taken a look at the materials you submitted beforehand. I do have some idea of the stuff you've been working on. But. Very interested to hear about it from you as well. And also I tend to run these where all the panel members can see the discussions that happened with the earlier panel members. Some other folks who are running this one and it's not squarely in my control. Prefer to keep the notes private for some part. So I actually don't have notes on your conversation with rusty. I apologize in advance if I ask questions that feel like you answered them already. That's why I would have read those if I had access to them.

**Me:** I'm happy to give you maybe a quick two minute overview, you know, maybe for context. That's helpful.

**Other:** But yeah. So I usually like to start, I suspect this will not really be an issue in this case, but you like to start a super general place just to make sure we're on the same page. So first question actually, how do you prefer to be addressed is did you correct? Is for Shakti, I saw your GitHub username. Like obviously totally, but yeah.

**Me:** Yeah, no, that's just like the developer username, but I know it's just Adithya is all good.

**Other:** Okay. Okay, perfect, perfect. All right Adithya, what would you describe or based on your current knowledge, what is your understanding of a 16z business and goals and more specifically what is your understanding of the responsibilities of this role in particular that we're talking about just to make sure we're on the same page.

**Me:** Yeah, totally. Totally. So, I mean, I kind of got, like, the overview from rusty. So do correct me if I'm wrong. You were here. You know, would love to get a better understanding. But, you know, essentially what I've found out, right, like, just from my research and reading, just, you know, from interviewing for this role, right, is a16z is more so not really just, you know, generic capital, but really sort of involved capital early on. Right. And that was kind of like sort of the, the founding thesis of the firm as a whole. Right. It's like, Mark Andreessen was like, okay, like, you know, we can get money from any of these guys, but none of them are really going to open doors for us. Right. And so really, none of these involve, like, none of these VCs right now are really involved either. You know, I come from the world of crypto, you know, initially and transferred into AI. And, you know, a lot of that stuff is just super predatory investment. Right. Where, like, you get into rounds early rate and then you sort of 100x the token, right? And balloon sort of Investments with marketing and then sort of, you know, just dump on retail segs with liquidity. And so that's really not the thesis that I want to subscribe to. Right. And that's kind of like sort of, you know, why I was also sort of kind of interested. Right. When rusty mentioned the role as well. But I think that's kind of my understanding of sort of the thesis of the firm as a whole. And so, you know, it's really stratified into two sort of like, you know, primary kind of goals. Right. One is, okay, like, how do I get sort of the best deals right on the block? How do I sort of get involved in sort of these really sort of like hot sort of companies rate type thing? And how do I really identify these companies and have an edge in identifying this as well? Right. What's my due diligence process? How does that really look? And compared to other firms on the street, et cetera, et cetera. And then there's the other side, which is, okay, how do I really help these early stage companies go from the zero to one process? And I think the fact that these are siloed actually is really, really beneficial, right, to these early stage teams because that is fundamentally two different skill sets, in my opinion. And so I think this role, right, and kind of what rusty was mentioning is it would kind of be enveloping, implementing a gentic process throughout the firm. Right. And so, like, what that looks like is, you know, sort of business processes. Right. What are really agents good for? They're good at sort of parsing a lot of information and sort of making these stratified decisions extremely quickly. Right. And so as, as you can get sort of more independent processes implemented, right, that are really kind of like redundant and sort of rudimentary ray type thing. That's the, the more beneficial to the firm. And that's my current understanding of role. Talk about some of my ideas as well, maybe a bit later on right at first, specific agents that I think we can implement. But is that kind of a good understanding? You know, do correct me if I'm wrong anywhere, please. 100.

**Other:** Yeah, so I think that there are definitely, so definitely great job. I would say that in terms of the differentiated operating thesis that this firm has opposed to kind of your run of those venture capital firm, I would say you're pretty much on the money in terms of the responsibilities of the role. I mean yes. So I would say that there is definitely some latitude to work on, you know, kind of like general agents around the kind of like fine pick win build for business life cycle. I would say that the focus of this role, at least in the immediate term, and this is also something that my team is currently owning and that I'm personally working on and have been for a while is very much oriented towards the personal agent, you know, the sidekick, the doppelganger concept. And this is a thesis that Mark in particular, but I would say for sure, Ben sure a bunch of other of us. Are most interested in right now. It definitely is, you know, kind of the theme of the moment for the time being. And that's really kind of where a lot of our guns are trained right now. So yes, I mean, we've been working on kind of like workflow agents, agents that operate for you, agents that help you identify investment opportunities, agents that help you build companies for quite a while now. I mean over a year basically. And I would say that we do have some pretty good capabilities for that in-house now. I will say that the current frontier is really on this, the doppelganger thesis. And that's something that we're really, really aggressively chasing down right now. And that's something that I anticipate the person filling this role to be providing some like real concrete inputs and assistance on. You.

**Me:** Can I run and go get my other laptop really quick? I built some options.

**Other:** Yeah.

**Me:** Okay, perfect. Okay, give me one second. I've exposed myself. I'm in the pajamas fit.

**Other:** Oh good, all good man. Yeah. You know, I'm doing my best to keep up with everything right now. It is a bit of a crazy time. I did manage to put on jeans this morning, but I will not pretend that that's an everyday.

**Me:** I take all my.

**Other:** Type thing.

**Me:** I work remote just like 24 7, you know, so this is like the default, you know, like the, the upside is formal, but the downside is just pajamas all day. Okay. It's, it's out of power right now. I'm charging it up. But while it is up,

**Other:** Oh, all good. I sense that this is related to my next question. And so I'll just go ahead and pose that in the meantime, which is basically do you have a personal agent set up, you know, and kind of how have you architected that and kind of like what are, well, I guess we'll just start there and then we could talk about functionality and, you know, future improvements in a minute. But do you have a personal setup roughly at a high level like how you architected it?

**Me:** Dude, I'm going to ramble now, so please do pause me at any.

**Other:** Yeah, yeah, go for it. Go for it. Go for it. Yeah.

**Me:** Okay. I'm so excited about this, like, entire space as a whole. Right. Just as, as agents have evolved, you sort of seen anthropic kind of shipping more consumer facing features right open AI kind of going more enterprise. Personally, I think that's a wrong play, but that's a separate conversation. Right. And I think really there's kind of like akin to what Microsoft and Facebook and really all these other companies did in, like, the early 2000s, which is just sort of open source, like, and not really open source, but, like, make their models extremely developer friendly. Their platform's extremely developer friendly and sort of also had these super sexy developer conferences, right? All these awards, and then bang, the instant you get an award, right? Or the instant you achieve some success ship exactly what you shipped and shank you in the back. Right. And that's exactly what I'm thrilled super successfully right now. You saw the open claw nuke, basically, that just happened, right, like on April 4th, right, where agent harnesses can no longer sort of use, you know, I mean, you have to pay API keys. No one's doing that or any type thing. So my thoughts rate. And so before this all happened, I was open claw gung ho, right? Okay. Like, how do you sort of use dot MD files and really, like, context structures and really thoughtfully think about context windows type thing? It's not really like, okay, like the, the naive approach to this is, okay, let's just throw, like, 2000 MCP servers into the context window. Right. All these skills and, like, you know, bloat the context to the point where the agent can't even think gray type thing beyond 50, 60 of context windows, opens is not going to do anything useful. Right. Even though anthropic says, okay, yeah, I can pick above sort of like, you know, 60 tools or whatever. I think it's like sort of the limit upper bound right now for opus, et cetera, et cetera. And throw up a greatly overstays their functionalities, in my opinion. So really, it's about thoughtfully sort of context managing and context switching. Right. So I'll show you actually like a file management structure I'm like kind of following now. And this is like kind of the thesis that I'm subscribing to now. But my previous infrastructure and a way for this thing to boot up. And in the meantime, I'll maybe tell you a bit about it. Right. So essentially the biggest unlock, I think, to actually useful agents, right, is contextual understanding. Right. And how do you give an agent contextual understanding? It's really about memory management systems. Right. And so I was, I've been thinking about this for, like, you know, seven months or so right at this point. And, and back then, right, we had nothing, right? Like, there was no super memory. There was no mem zero. There was no qmd. Right. There was no Gemini embeddings or there's no vector search rate, etc. Etc. Right. And so, like, essentially, like, all these tools kind of came to be. But back then, it was literally just about sort of annotations in a dot MD file and really thoughtfully talking to the agent and really, like, coming up with annotation rules as well. Right type of thing. And so really, like, from there, and that really, like, taught me, like, okay, like, how do you, like, diligently select what is important? Right. Because that's actually very important as well. What does arveni phos rate of perplexity is? He says the guy, like, that's going to win in the next two years is not really the guy with the best model architecture. The guy with the best sort of, like, you know, like, training, etc. Etc. Right. Because everyone kind of is, like, at the same level of playing field at that point. It's really about the best index data. Right. How do you even determine what is good, right? Typically, because that greatly actually, like, you know, changes model behavior and model output. On top of that. Right. I'll also add. Right. Google actually recently released a paper saying that agent harnesses actually matter more than the actual model itself. Right. So how do you actually use the agent? Right type thing. And that actually matters more. So look at Hermes rate, which is news researchers like self-improving agent. Look at, look at some of these things, right? Where, like, for auto research is kind of the cliche thing to mention here, where you have self-improving skills, Hermes has that kind of built in. Right. But I do think that these kind of, like, persistent sort of learnings kind of behaviors will actually, we'll start to see a lot more in 2026 as an architectural pattern. Right, in my opinion. So anyways, talking more about my specific setup, essentially, I incorporated sort of a thoughtfully selected sort of skill set. Right. I really subscribe to cli tools and skills when they subscribe to mtps. What I do, I build out sort of workflows with mcps before. Right. Because, like, that essentially, like, allows you to quicker build, right? Quicker iterate, all that stuff, then you can essentially tell the tool, right, to essentially, because it has the entire context window, build that into a skill. Right type thing. And then every time the skill breaks, you're just continuously self-improving it as a design iteration process, in my opinion. Right. And so that's essentially what I do. And what that does greatly reduces context when no bloat, because all the, all that essentially mcp sort of context gets inducted into the session window every time you start a new cloud code session. Right. And so that's very, very important to kind of, like, thoughtfully manage. Right. Like, you don't want to be sitting at 30 context usage right off the bat, right type thing, essentially. And so that is one thing. The other thing I do is thoughtfully use file folder structures, in my opinion. And so what that allows you to do is I have basically an index dot MD in each one of those. So everyone has a cloud MD, right? That's cool. But in my cloud MD, I actually route to a separate dot MD file called index dot MD, and that actually thoroughly annotates out all this sort of file structures, how the agent is actually storing sort of like everyone's like, okay, doing fancy things where it's like, and I was doing this myself. I was very guilty of this. I built a seven layer structure memory management system, right? Over engineered the out of it when I really didn't need to. Right. Essentially, if you can really thoughtfully prompt the agent and tell it exactly where to sort of store various information and what file format and what structure think about it, almost like a sequel sort of schema, right, that you're providing the agent, but just an MD file, right type thing. That's essentially what I've done. And I'll show you an example of this on my local file here. Why is my computer not booting up, man? This sucks. But.

**Other:** It's all good. It's all good. Yep.

**Me:** Oh, it is. Okay, it is. It is. Never mind. Okay, so essentially what I built, right, is essentially like initially, right there, I subscribe to. Have you heard a paperclip by any chance? It's like a thing that's going by. Okay, so I basically thought, I was, like, thinking of paper clip right before it kind of came out and, like, where there's, like, this kind of, like, CEO, right thing structure. This is going viral on Twitter for a while, right before. And so I kind of built that out, and I thought that that was, like, the best way to do things, right? Because, and this was before I really learned about context float, like context window, like, the importance of really context selection very thoughtfully. But it did work. I mean, so it essentially was a dispatcher agent that had a heartbeat sort of rate to itself, called it Jarvis, because who doesn't? Right. I think that's a generic name, I think. And then let me see if I can boot this up here. Give me one second. And so essentially what that did, right, it had sort of a kanban, like, sort of board structure, linked in with my notion would actually sort of subscribe to when the notion due date was there, if the due date had passed compared to the current time, it would actually auto dispatch sort of skills. If it didn't actually have a skill to complete sort of a task that I dispatched it, it would actually auto suggest skills to create an auto agents to create as well. It had sort of a series of 12 to 13 agents at any given time. It would prune agents if we didn't, like, sort of use an agent for the past week and it would actually create agents, you know, if a thought that it would, like, sort of merge agents as well if it thought that was helpful, et cetera, et cetera. Let me see if I can boot this up really quick. Give me one second. But, yeah, I mean, so it also had, like, each agent had its own, like, sort of tool set, right? Obviously, just for, like, at least I was, like, thoughtful, like, in that way with, like, sort of context float back then. Definitely more thoughtful about it. Now let me see if I can ultra claw. Dang. Okay. Oh, I forgot to have this hosted on an oracle instance, actually. Maybe I could just show you this. My stupid. Okay, never mind. Okay, so maybe I can't show you this. Let me see. Bang. Yeah. Okay, perfect. I might have it hosted already. Okay. Okay. Give me. Or. No, never mind. Give me one second. I think I might have lead the call and come back just to share my screen. Give me one second. Sorry.

**Other:** Yeah, all good. All good.

**Me:** About that.

**Other:** I will, I will still be here. I promise.

**Me:** Okay.

**Other:** You.

**Me:** Okie dokie. Let's see if I can get this working. Allow. Okay. Cloudflare tunnel. It's a bit sketchy. Oh, bang. Okay, we're in. Okay, so this is basically my entire setup, right? So you have this kanban sort of system here, right, that you can kind of view. You can also see, like, remediation tasks. These are basically tasks that the agent has suggested that to fix itself. I have, like, sort of an analyzer agent that analyzes session transcripts at the end of each day using a cron system that essentially analyzes transcripts and evaluates those and sort of scores each thing. So you can see here for, like, past things that have completed properly or have not completed. I haven't run this in, like, ages. That's what you're seeing the 36 days ago and whatnot. But, for example, this is like a task that got completed by Vader, which is, like, one of the sub agents that, like, is a sole use for messaging tasks. You know, it's successfully completed this. There's no errors. Right. So it has a custom prompt that basically, like, you know, goes through, use a fan in fan on sub agent method. Okay, I should also mention this, right? There's, like, stochastic, like, sub agents that you can use for research. Why is that useful? Because each sub agent has sort of a new context window, so it finds new things. Right. And so this is, like, kind of a multi debate tribunal model. I've actually implemented that here in, like, a dashboard agent that I'll show you in a bit. But what I've also implemented here, right, is like, I've used fan in fan out model where, like, you essentially have one orchestrator agent that then goes out to a series of five sub agents, each with their own context window, goes out and debugs tests and actually evaluates each task using an instance of sonus. Sonnet, that's way cheaper from, like, a token context window than just using one instance of opus. It usually catches more bugs, too, and is much more effective. So that's actually the process that's going on behind the scenes here. So context selection, you're actually using context to your favorite, I think is, like, extremely important, in my opinion. But, yeah, so this, this evaluated this. And also, so even if the, even if the thing works, right, what it does as well, it actually dispatches sort of an instance of sonnet more if it doesn't work, less if it does work. The reason why is because, you know, if, even if it does work, if there's a more efficient way to run that skill, it'll actually then auto suggest remediation tasks. And that's what you're actually seeing here for failed tests. This is breaking right now because I haven't run anything recently. But basically for all failed tasks, you would see essentially these evaluations running as well. And then if, if you see an evaluation that's wrong, you can actually then go in and teach the system saying, hey, like, this is actually wrong. The agent did this right and you marked it as wrong or the agent did this wrong and you marked it as rate. So false positive, false negatives, you can kind of manage here as well. And the, the, sorry, analyst agent, right, will actually go back and, you know, sorry, edit it system prompt based on sort of your eval input here as well, pretty much. So that's pretty cool. And then workspace here, right, you essentially have various workspaces with various context windows. Each one of these has sort of their own vector stores. So I ran SQLite basically for, you know, vector or, sorry, vector store was quadrant and then just like database store for like, you know, just task management systems and dispatch systems for SQLite locally. I use Gemini embeddings too just because it's like a 4096 vector store with like literally cents to like million tokens. I'm pretty sure for embedding super, super useful stuff. I eventually like moved on to like a light rag system actually just for like, you know, lower context usage just because like mem zero sucked. I've used mem zero and like other open source solutions before deciding to build my own damn thing because like they all kind of sucked mem zero is not coming back with like some QMD vector search thing for MD files. That's way better than anyone on the market. So might be going back to that, but we'll see. But anyway, so like these are all the sort of these skills and tools that each one has access to. As you can see like this, you know, flag means that it has access to all tools, et cetera, et cetera. These are, so this is my main dispatch agent. This is sort of all the, there's a limited number of session windows that you can use essentially with open claw, at least there were at one point in one version. So just, you know, have like tasks that were dispatched to it. You can actually see anything going on live if I had a dispatch something, you know, it essentially then occupies some agent slots essentially right here. You can see what workspace each agent has access to. The reason why that's important is because then it has access to a different tools and like also just different system problems within each section. You can see one out of two just means sort of one session slot is why is this broken right now? I don't know if this is live.

**Other:** Nice. Ly. Is this the oh my open code sub agent config or I guess this is forked from the open code.

**Me:** Oh no, I just built this from scratch.

**Other:** It looks like it. No. Okay. Okay. Yeah. The, the, the atlas forward nomenclature for what I assume is like the overall orchestrator and then the like task assigner. Is maybe like maybe your agent was reading the docs of that project. It can definitely happen.

**Me:** Yeah, basically just like sort of instantiated like a new tmux sort of instance for each thing in order to instantiate like a new session essentially. And then you can also do like schedule tasks as well. There's like sort of a, this is like an old version. Man. Hold on. This is not correct. Give me one second. There's like a calendar view that I incorporated here. There's definitely something wrong here. Give me one second to see if I can boot this up.

**Other:** Yeah. So, so this is, this is essentially built on open cloud, right? Like this is a fork on top of open claw. And like how, how have you approached like pulling in like new versions from open class? Like let's say like open class ships features that you're trying to take advantage of? Like have you tried like rebasing on them? Is that like a possibility? Is that something that's like been difficult? Is it something that's like been not that difficult? Like how has that been?

**Me:** Yeah. What I would do is honestly, I'd like just use claw to like reverse like engineer like sort of like most features. Honestly. Like what I do is like use grok to basically just prompt, right? Like and see like what people were talking about on X. I find x is like honestly just the best source of information at this point for a lot of stuff. Like it's like the new version stack overflow is kind of grok ray type thing. Like for a gentech engineering. So I basically just like get people's opinions on like sort of what the best features are every like week pretty much use that to basically then reverse engineer those features and then implement it into my local setup.

**Other:** Nice? Yeah, that's, I will say that that's, that's like one of the things I've been asking my open cloud for is just like, you know, the voice voice notes briefing of like everything that's been released in the last 24 hours is definitely. Definitely super helpful.

**Me:** PR merge literally.

**Other:** Yes. Yeah. And yeah, I mean, I guess like natural questions. So I saw some of the skills that you've installed. I mean, it looks like there's like a social skill. Obviously we've got like canvan tasks. Obviously got these self-improvement layer. I'm curious kind of like what are some of the things where you found value in using this? And, you know, are there tasks for which you rely on it in practice or like are you feeling that the ecosystem is still too early for that? Like kind of like where are you on that spectrum right now?

**Me:** Great question I'll maybe like talk about one like like realistic thing that we're actually implementing that's tangibly implementing business value for one of my clients. And then one more like out there thing that I'm influencing that I think is super cool that's still adding value, but it's just like kind of sci fi you know type thing. Okay, so first thing is essentially like you know for go to market stuff right like everyone and their mom's kind of building the like you know vibe go to market thing for yc right now and kind of shipping that and getting funded. But I think it's like it's just shit right like they're not really like understanding sort of business processes like really what the product is a product constantly changes internally right you can't really build like a context stack that understands that unless you're internal or unless you're constantly sort of like reevaluating your contact window like every day, which is like actually exactly what I implemented right type thing internally. So I have sort of a you know I'm sure you've heard of like carpath these like llm wiki right type thing meta so essentially just sort of like an empty store rate that's managed by an llm essentially and it just sort of for our slack messages checks the delta each day of like what you know sort of gotten added use basic sort of sentiment extraction using like a local jama instance. I literally just got my dgx spark and today I'm super hyped on it before I call so I'm like running that basically in order to essentially just do like content or context extraction. And then from that you basically can compress this like large amount of like ingestion from all of our Granola notes right our entire team uses Granola all of our github PRs what's changed on the inside what's changed on the legal ops side and all this essentially gets ingested and stored into this MD file in like a thoughtful manner.

**Other:** Yeah, what I guess you're still setting up the spark. I'm curious kind of like what size gemma model you're working with and whether you're like, am I correct in understanding that you're doing local inference?

**Me:** Yeah yeah gemma kind of like sucks I'm like kind of like I'm using it like right now like I'm like kind of transitioning you know between sort of just sonnet using sonnet honestly to like sort of I'm like playing around between gemma or like honestly I'm thinking about just like sort of using deepsea just like a quantized version or just running an exo cluster honestly between my MacBook and like this thing I need to get like a 10 gig switch for that though very but yeah, I mean like essentially I'm just using essentially for like just context extraction mainly so you know like what is important what is valuable what is a meaningful change to the business that actually impacts the product is essentially the system prompt essentially in the summary. And so from that okay like that's cool and all essentially the AI now understands or sort of the agent I understand sort of the business but what does that actually values that adding rate so then I've actually instantiated sort of a Apollo skill and also just a fire crawl and exa search rate in order to see what sort of the best client's rate would be like top 50 to top 100 clients. I also have sort of a developer account on x right so I can then go and scrape sort of leads there as well. And just all this stuff and then from sort of that then compare that against sort of what the new changes to the product are what the top features of the product are how that would tangibly deliver value to this person and then write a cold email that's custom to that right and actually have the agent figure this out it sends out actually a thousand emails per day for this right and so we actually get a pretty great on that because it's a custom sort of thing right and there's actually like a it's not really like a solutions engineering type thing right it's like a quasi fds agent right that like actually implements a very very like sort of like easy to implement like white label sort of task grade type thing. So it's like in my opinion cost of software engineering is near nothing if you're hopping on a sales call without actually like implementing a solution for like the person or like client you're lazy right type thing. So like the agents actually automatically doing this links sort of the demo to the client and we're getting a pretty good hit rate from that. So it auto books basically just using calendar integration. So that's like realistic okay like we're actually getting stuff done there's tangible business here we've actually closed like a ton of contracts from you know sort of these calls etc etc the more out there thing in my opinion which I think is a lot cooler right? Have you heard of hive by any chance like Facebook's data set or whatever.

**Other:** Five of there's so many things called hive. I don't think I'm familiar with this one, but it's a good question.

**Me:** No it's basically the one where like it's like fmri data that they basically scan from like 700 people right it's like 14,000 hours of this like crazy sort of like detailed fMRI data right and so what I did like this is like honestly some terminator level stuff dude in my opinion right but like essentially what it does it activates sort of like your it detects sort of what like synapses activate and what areas of your brain activate right when you're actually like watching something so they've scanned sort of like you know again like all these people and so when you run a video through the model it tells you exactly sort of you know what like neurons are activating or whatever I don't know like the.

**Other:** I I did see the announcement of this. Yeah, yeah, yeah, yeah. So. So what are you doing? What are you doing with this data set?

**Me:** So what we've done is like we now know the hashtag for what our product represents right like and we're doing a ugc sort of like push right and so you can use higgs field pretty much like build a custom higgs field skill to like use CDP. I don't want to pay for the API rate or whatever so use heat field in order to auto generate these UDC videos right and custom rate these prompts based on what is working in the market how do you determine what's working though right that's hard to determine not with this right so you can actually then go out and like literally scrape using whatever custom hashtags your product is and whatever your niche is right pull the top like 100 viral videos per day go in and actually detect exactly what parts of the brain this is activating literally right typing these videos are activating and then I'm, I don't know whether this works I'm still like in the process testing this out right but like in theory is right okay like once you determine and like I've already determined what portions of the brain these videos are activating now you can actually reverse engineer that by literally just outputting a thousand Higgs field videos per day and ranking those in order of what is closest to that level of activation that pattern of activation right type thing from the previous like stratum essentially and that is literally sick because now you're essentially getting like literally like some level of social engineering right to confirm and validate that like your video is going to go viral and you can now also feed that back into sort of like not really an RL loop, but like a prompt loop in a way type thing in order to actually like trust your prompt based on what's working what's not working right based on this thing so we're kind of implementing that we'll see if it works but you know that's more out there thing that I don't know if it'll you know actually tangibly add value at it that was cool.

**Other:** Yeah, super interesting. I mean, definitely if it works, you know, it's. It's. It feels. Feels a little bit, you know, doctor strange lovey, but. But, yeah, that's, you know, that's. That's kind of. That's kind of the world we're in at this point.

**Me:** Yeah. Yeah right on.

**Other:** Yeah.

**Me:** But I'm talking a couple of the other agents and stuff if that's helpful if you know like more like useful ones but yeah.

**Other:** Yeah, definitely. Definitely helpful to talk about some of the other agents, but honestly, I mean, I think the thing that I'm looking for, you know, I'm curious about at this point most is. Is basically kind of like how are you thinking about this role at Adith? So, like, I know that there's. There's, like, a team you're working with right now. You know, I. Know, I think, like, you're in. You're in the founding position. Right. And I'm curious, basically, like, what is. What is your perspective on, like, this role? Like, what are you looking for from this role? Like, what are you looking to, like, put into this role? Kind of like, where are you on that, on that distribution?

**Me:** Totally totally I mean I think like like to give you a bit of perspective I'm like running a venture studio right now so we have like a bunch of clients have like two co-founders go you know co-running it with me I'm thinking kind of about the role right it's not really like an execution role but really more of like a leverage role in my opinion right I think what really kind of seems unique about the firm and I was talking about this with with rusty earlier right is that it has this unusually sort of large operating platform already right and there's really two surfaces where like really good internal systems matter right and I think this is kind of one of them where it's really helping the investment side kind of move like that much faster I was talking to john right like earlier like and like he was telling me there's 18,000 like speed run applicants every year right so it's like ridiculous amounts right and so that's really where good like internal systems matter and like these large sort of like scale business operations right and I think one is sort of like helping their side move faster with better context right the other side is also helping the platform side scale move faster too right like more the ops side and it kind of gives like these founders level a level of support with that linearly just adding headcount in my opinion you can kind of exponentially grow the amount of value they're delivering to these people so if I kind of were personally stepping into this world I want to like maybe spend the first stretch kind of mapping out where partner and operator time matters most ratings actually kind of getting burned today right at the at the firm and maybe we're places where like people are doing repetitive tasks or like maybe high value judgment kind of wrapped in like a lot of low value retrieval tasks right like synthesis formatting routing follow up work all that stuff can just be automated in my opinion. And so the way I kind of want to contribute is like really being very pragmatic about this right like what is like the biggest sort of ROI right what are the workflows where ROI is super obvious and then the human kind of remains in the loop but success is kind of super easy to measure as well right tangibly right how much impact we actually have me on the firm. So the near term I kind of expect that to maybe look like less like replacing judgment and more like maybe compressing the time around judgment, the process around sort of like due diligence. Right so research compilation like memos scaffolding like all this stuff is boring just tasks that kind of can be automated right and so long term really what gets me excited is maybe like also helping build these like internal agent infrastructure sure but also maybe that becoming reusable across the firm like these kind of agent modules that can like kind of be dispatched across the firm rate type thing like memory like evaluation permissions like workflow orchestration agents etc right like and also maybe like the guardrails that make these systems like accessible and useful to like various you know sort of companies as well for like regulatory concerns all that good stuff does that answer your question I don't know if you were asking like a 30 60 90 day.

**Other:** Yeah, yeah, yeah. No, no, no, no. I think. I think. I think that makes a lot of sense. I mean, if I was. If I was to zero in on, let's say that you were just building one of these agentic systems for mark, let's. Let's just zero in on that one use case.

**Me:** Okay.

**Other:** What is the delta between the system that you've set up for yourself and the system that you would set up as kind of like a v zero or a v1 to, like, test the waters if. If you were specifically targeting mark as your. As your first user.

**Me:** Interesting okay so I'd like probably. Okay maybe I'll talk about this I think the man Delta rate is that for myself I'd probably like optimize pretty aggressively for speed flexibility like my own tolerance for like kind of weirdness right in a way like whereas like maybe someone like mark the bark like the martyr is like much more higher right like about like trust like signal quality right like how seamless it kind of fits into the way he already worked he doesn't want to like go into some like other process right just cuz like okay it's like cool agents right type thing so for my own system I'm kind of comfortable with like a lot of modularity already right like I don't care what I'm working on right experimentation even but like messiness under the hood right that as you can kind of clearly see like with the current implementation rate and so I think a v zero for mark maybe I'd super simplify it kind of like a ton right like essentially probably start with just three things right like probably like one is like you know maybe like super strong context ingestion right I think that super matters first right like that's the primary thing like the agent needs to know a ton about marks processes in order for it to actually be useful right and then two like super like high quality summarization and prioritization like I already mentioned and I've already implemented these processes right but three that I haven't implemented I think would be super useful for mark specifically is like a super tightly scoped action layer right and so like maybe at concretely like more concretely I wanted to understand like not as like his world through like email calendar notes all that stuff right but that's kind of like the boring stuff I think like really like the cool stuff is maybe like also helping him identify deal flow like relevant external signal right and like in a way that like it's it's a boring stuff but it's needs to happen right I'm not saying it doesn't need to happen it needs to happen right but like the external stuff is really where I think the interesting part is where like you know he's already doing these things he's like already going out on X I see his tweets all like you know all day every day right I think and he has high signal he just like I'm I'm trying to almost give him like a tool to like summarize more information at the same time right in a way so that would be super cool right and so not in a way where it tries to do like everything at once but like really the first job would maybe be helping him answer like what matters today right like what what can be changed what needs his judgment personally what can be delegated to other people in the firm right and I think that means the product kind of needs to be somewhat opinionated right in a way less of like a general chat interface more of like a trusted like chief of staff layer right in a way that continuously compresses like all this noise right in the market until like sort of super decision ready context for him specifically so instead of like saying okay like here like 40 updates from like the market or whatever it should say like here are the three things that actually moved right like here's why they matter here's the missing context here's why you care as mark right as as like specifically and then here's like the next action that you can draft like if you actually wanted rate take so the other big delta I think is well compared to like my setup would be evaluation right for me like if the system's wrong and sometimes not useful the spine like whatever I'm just going to go back in and modify it but like for mark I probably want like super tight guardrails around like confidence providence rate like data prominence probably matters a ton to him right and then like failure handling as well right if it's uncertain it should say so does taking an action it should say so it should be reversible it should be human approved right if like surfaces of recommendation it should be like super clear wires grounded in and should have research back like sort of links like you know wiki links so I think the v zero is like less like a broad autonomous agent right like lesser so that I've set up for myself but like more so like a reliable like decision support system right with like memory prioritization select of execution and opinion right like it actually matters you actually do need to rank some of these things based off like what market theoretically think and once that earns trust then I'd expand the action surface from there but it's like a ton of information to throw.

**Other:** Yeah. Yeah. I I will say you may be underestimating Mark's appetite for speed and things breaking. But. But, yeah, that's. That's definitely good to know. I think. I think a lot of those are definitely, you know, ingredients in the working recipe.

**Me:** Okay.

**Other:** And, you know, I mean, a question. A question you'll hear over and over again is, you know, what is the strongest version of this? And usually that. That is actually a pretty useful question to ask yourself when you're thinking about building a system. Like, what is the strongest version from this version of this and maybe start from there and then scale back as needed. But. But, yeah, it. It makes a lot of sense. So, yeah, I mean, we've. We've spoken about a few different things. Spoken about a few different things. But. Yeah. And I'm glad that you spoke with john as well. It's true. We work very closely with the speedrun team. They do a great job with growth marketing in particular. Obviously, Andrew is. Is also quite a, you know, notable growth marketer. But, yeah. Okay. Yeah, we talked a little bit about memory. We talked a little about the setup. I mean, I guess one other question. So. I know that your personal setup is primarily open flaw flavored. I'm curious, like, have you tried out other claw ecosystems setups and kind of, like, were there pros and cons that were noticeable to you or these things that push you in one way or another or, you know, kind of like how. How have you thought about the various trade-offs between, you know, the nano clause, the nemo clause, the hermes, you know, etc. That. That are kind of out there, open sourced in this space.

**Me:** I just honestly go for what's most maintained to be honest right primarily primarily like that's where I technically like not like really gravitate to I do try out other things but like at the end of the day like the folks that are like you know it's an exponential growth curve right like the folks that are going to have like 50 developers working on it versus like five even if the 50 are super shitty at this point everyone's like not really shitty with cloud code in my opinion right so so I think like honestly just more hands on the keyboard and more eyes on the repository just push it farther but I that being said right like I have tried out Hermes actually like completely shifted her over my entire set of hangings but then I found out that honestly I could just build my own self improving skills myself right it's not really that difficult to do and it also adds a lot of context float and I kind of built like a custom agent harness like based off of pie have you heard of that one it's like okay nice yeah okay so like that one's like a lot more.

**Other:** Yeah. Mario sectioner. Yeah. The, like, tear it down self-improving coding agent. Yeah. Yeah.

**Me:** Crazy talk earlier today dude I'll send you a link maybe after a call actually super cool but I think like you know that's like a more like stripped down version right basically of like cc where it's like a lot less opinionated about a lot of these things it's kind of like the my version right almost like you know maybe quote the previous answer right like kind of like the the off-road version right so I think it's a lot more like you know you have a lot more choice around it right but I think really the the drawback there again is like a lot more these like integrations with like things like skills with routines with like cron jobs with you know scheduled tasks a lot of these things actually youy have require a lot of like manual setup right for example you need to have like daemons just like constantly running right just like you know have like watcher tasks for example right for like web hooks etc it's like yeah you can do it but it's going to take me a week to do rather than a day to do with open claw right and it's like all right I don't really mind like the difference in context flowed at that point so I think really like the way I think about trade off right it's like less like which ecosystem is kind of best in the abstract and like more which ones like which each one is optimized for now I would I would argue like right like for specific sort of instances where I want a more autonomous long running agent I would definitely pick hermes right over this thing just because like it's like you know I don't I don't have like as much setup and also if I got my like they you know dot MD file right like the first time like honestly it's a lot lot better and a lot more long running of a process now that being said 4 7 got dropped yesterday and it actually has a lot of inbuilt features where they actually have like implemented things like routines slash routines actually now has a lot more long running features right you can actually use sub agents to actually prompt back actually you can use like the are you familiar with like the session hook stuff basically with like like claw so at the end of the session hook you can actually re inject a prompt right to like basically dispatch sub agents to like you know there's all these workflow things that you can basically do right that are super cool so honestly I do think like at this point right like with the rate of speed of shipping with the rate of adoption cloud code is a clear winner for agentic harness right you just build up sort of your custom agent harness on cloud code as per your business processes in my opinion. I think like for memory management systems like you know like sort of trying to build your own custom processes dead right I think like honestly like having just thought MD files and being like really agnostic from harness and by model is honestly the best structure right like not like super vendor locked to one thing is like really important in my opinion as well do that as like honestly just with like sort of dot md files right so that's kind of my thoughts right I'd love your thoughts on this though because I know there's kind of like an interesting question right and I'm sure you're thinking.

**Other:** Yeah. So I was gonna say, actually. So. Like I said, Adithia, I've been taking notes this whole time. If there's anything we haven't spoken about yet that you think would be helpful for the rest of the panel to know because I'm gonna share my notes with the rest of the panel after this call, now would be a good time to bring it up. But otherwise I'd be happy to answer your questions. And I'm really sorry about this. I do actually have a hard stop at 245. I try to keep these so I have extra time at the end, but they sometimes schedule them. Not great.

**Me:** Yeah. Yeah. Yeah.

**Other:** Yeah.

**Me:** Yeah. But yeah I mean I love your thoughts on this and then like maybe like my two other rapid fire questions at the end you know I'd love your thoughts on maybe what like Q2 looks for the firm right I know you're like sort of like you know leading the ship on sort of the technical side so we'd love sort of your vision and you know for the firm for the next couple months maybe a couple of the interesting you know one or two interesting projects that I think you know might come up internally with the role as well and maybe how you're seeing the role you know what would success look like you know if I were to get the role for potentially?

**Other:** Yeah. So honestly, so a lot of stuff that we've spoken about, and I will say that I share a lot of your opinions in terms of, like, you know, the ideal enterprise architecture for this. I would encourage you to think about it in the mold of, like, what if you are not cost constrained? You know, how would you set this up? That's kind of how we were thinking about it, basically.

**Me:** Yeah.

**Other:** But, yeah, I think in terms of q2, what would success look like? And then interesting projects. I think, you know, I can kind of give an answer that hopefully satisfies all three of those questions in some ways. So some of the most important pieces that we're working on basically fall under the heading of AI devx here. So we're of the opinion that as of this year, basically every single person at the firm, there's about 700 of them is now an engineer. Some of them are very.

**Me:** Nice. Abstracted.

**Other:** New, shall we say? Should we say less, less technical engineers, but, but every, everybody is building now. And so two of the most important projects that we're chasing down right now are so the vibe apps platform, which is basically a very simple, frictionless way to enable people to build applications to at least a reasonable standard of quality and working functionality and then deploy them internally with essentially zero friction. So make it just as easy for somebody to build something locally for themselves. Make it just as easy to build it for their team. Obviously, you know, publicly exposed surfaces are more of an issue. We have, I mean, at this point, we have a lot of practical exposure to people having, you know, Vibe stuff. And currently nobody's implemented authentication correctly. Who doesn't have an engineering background? So it's like, it doesn't really get to talk to the public internet, at least in terms of ingress until somebody else has their eyes on it. But we absolutely are reducing the friction to zero for internal syndication of apps. That is super high priority. Second thing that super high priority is really this, the doppelganger project. And that's a lot about what we talked about. It's like the personal agent, the person always on agent. We really want to enable that for every single person at the firm. And, you know, I would say first the experts come, you know, a few of the people on my team, a few of the general partners, definitely Mark and Ben. But, you know, it's an initiative that we're looking to push. And honestly, I think success for the person who's in this role really looks like making meaningful contributions to those projects and the other projects under the heading of AI dev X. I will say this is the theme. This is the theme of the moment, theme at the time. It's the, it's the theme of the market. Red hot, honestly, maybe even white hot at this point. And so it's really contributions in that space that we think are highest leverage right now.

**Me:** Nice super cool. I know we're outside do we have time for one more all good if you have to go.

**Other:** One more. Yeah, I'll do, I'll do one more and then I really do have to jump because I am, I know somebody else might have.

**Me:** Okay and and so what are your thoughts on context suggestion right I know you've sort of said that you've you built out this personal sort of OS age.

**Other:** Yeah, it has to be, it has to be Progressive, Progressive discovery. That's the only thing that works. So, yeah, you, you basically need a really, really good mechanism for progressive discovery that can go as deep as the agent needs, but it essentially needs to be like breadth first at one layer and then entirely agent driven. You cannot stuff the context window with too much.

**Me:** Nt.

**Other:** Those are my very, very brief abridged thoughts. I think there's a lot of stuff to say on that topic, but I think the real key principle is progressive discovery that is entirely driven by the agent.

**Me:** Absolutely.

**Other:** Yeah.

**Me:** Just good agent routes and honestly just also good agent ingestion right agents need to prompt humans for information and agents also need to understand how to route themselves right for limited windows but cool stuff well I'll let you go but no thank you so much for the.

**Other:** Cool. Super nice to meet you. Thank you so much for talking to me on this really interesting conversation. I've taken notes on the whole thing. I'll be sharing those. I would expect you back from rusty within 24, I guess it's Friday afternoon. Okay. You'll hear back from rusty by Monday, but I'm going to share him the stuff now.

**Me:** Yeah. Okay. I'm going to show you over that news research or sorry pi agent like thing to talk from super interesting definitely check it out.

**Other:** Nice. Cool. All right. Take it easy.

**Me:** Take care.
