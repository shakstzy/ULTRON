---
source: granola
workspace: sei
ingested_at: '2026-05-07T04:23:57.244510Z'
ingest_version: 1
content_hash: blake3:e6b844dcc171d43982252944613b14d9990b1cf0a31fc34630334dd53d75b69e
provider_modified_at: '2026-05-06T20:37:36.880Z'
account: adithya@outerscope.xyz
account_slug: adithya-outerscope
document_id: 5c200b21-e515-4b71-8b04-52b80bae072d
document_id_short: 5c200b21
title: Austin V / Adithya Kumar - 30min Meeting
created_at: '2026-01-14T21:30:08.718Z'
updated_at: '2026-05-06T20:37:36.880Z'
folders:
- id: 3ca3cb55-d6e1-49ef-961a-8ba2469731a5
  title: SEI
creator:
  name: Adithya
  email: adithya@outerscope.xyz
attendees:
- name: null
  email: austin@gensyn.ai
- name: Chetan Kapoor
  email: chetan@seinetwork.io
calendar_event:
  title: Austin V / Adithya Kumar - 30min Meeting
  start: '2026-01-14T15:30:00-06:00'
  end: '2026-01-14T16:00:00-06:00'
  url: https://www.google.com/calendar/event?eid=ZDkwM2UwYWI3MGY3NGE0YTk4MzhiZmY4OTkxM2FmM2QgYWRpdGh5YUBvdXRlcnNjb3BlLnh5eg
  conferencing_url: https://meet.google.com/gig-bezk-kxw
  conferencing_type: Google Meet
transcript_segment_count: 172
duration_ms: 1820254
valid_meeting: true
was_trashed: null
routed_by:
- workspace: sei
  rule: folder:SEI
---

# Austin V / Adithya Kumar - 30min Meeting

> 2026-01-14T21:30:08.718Z · duration 30m 20s · 3 attendees

## Attendees

- **Adithya** (creator) <adithya@outerscope.xyz>
- <austin@gensyn.ai>
- Chetan Kapoor <chetan@seinetwork.io>

## Calendar Event

- Title: Austin V / Adithya Kumar - 30min Meeting
- Start: 2026-01-14T15:30:00-06:00
- End: 2026-01-14T16:00:00-06:00
- URL: https://www.google.com/calendar/event?eid=ZDkwM2UwYWI3MGY3NGE0YTk4MzhiZmY4OTkxM2FmM2QgYWRpdGh5YUBvdXRlcnNjb3BlLnh5eg
- Conferencing: Google Meet https://meet.google.com/gig-bezk-kxw

## AI Notes

### Gensyn Company Overview

- Marketing, community, grants function head at Gensyn (Austin, 8 months)
- Previously: 9th hire at Solana (go-to-market), global expansion at Aptos
- Company: 5 years old, 4 years research phase, ~55-60 team (mostly PhD researchers, ML/RL engineers)
- Just completed token sale, approaching mainnet launch
- Core protocol for machine learning focused on signal, scale, eval concepts

### Current Products & Technology

- RL Swarm: Core product, distributed reinforcement learning
- Block Assist: AI agent learns user behaviors without prompts (proves “signal”)
- Code Assist: Similar to Block Assist but for coding environments (proves “scale”)
- Delphi: Live prediction market for model benchmarks

    - First live betting platform on AI model performance
    - Currently running lightweight reasoning benchmarks
    - Revenue via fee switches on trading volume
    - Polymarket does ~$1B daily volume, FanDuel $50B in 2024
- Recent grant with Quok: tested 800 participants across different hardware setups

    - Some optimized CPU setups outperformed GPUs for data quality

### Integration Opportunities with Outerscope

- Outerscope building trust/governance layer for AI systems across cloud/on-prem/decentralized
- Key integration areas:

    1. Trusted execution environments (TEEs) for sensitive workloads

          - Cryptographic identities for models/data/agents
          - Runtime policy enforcement
          - Tamper-evident logs for provenance
    2. Verified work economics for Gensyn’s network

          - Strong guarantees jobs completed correctly
          - Enhanced verification processes for SLAs/rewards/slashing
    3. Policy-aware scheduling for enterprise clients

          - Route jobs to nodes meeting jurisdiction/hardware/compliance constraints
          - Makes network consumable by regulated verticals
    4. Enhanced model discovery via Delphi

          - Tie eval results to specific model versions/training runs
          - More trustworthy, auditable results

### Next Steps

- Follow-up meeting in 2 weeks (end of January)

    - Outerscope to share detailed product architecture
    - Gensyn to clarify Delphi mainnet production plans
- Austin to loop in dev relations team member
- Timeline: Integration could be ready in couple months depending on scope
- Austin to add Adithya to LA crypto monthly meetup group

---

Chat with meeting transcript: [https://notes.granola.ai/t/ea31d370-8cb2-409a-a356-a143019dd175](https://notes.granola.ai/t/ea31d370-8cb2-409a-a356-a143019dd175)

## Transcript

**Me:** Hey. Morning.

**Other:** Tell me a bit about Genshin Outerscope.

**Me:** Yeah. Outerscope is just like my handle Chetan actually.

**Other:** Oh, okay. Oh, sorry.

**Me:** Hey, how's it going, Austin? Great to meet.

**Other:** I'm good. How are you guys doing?

**Me:** Doing? Well, where are you calling?

**Other:** It's good to connect. I'm in Los Angeles, so a lot of. Not a lot. But a decent chunk of the team works out of an office in la.

**Me:** Wait. Where are you guys? In la, man. I'm calling you from Granola Hills, if you know where that is.

**Other:** Very cool offices in West Hollywood. I live on the west side, though.

**Me:** Cool. Very cool.

**Other:** Yeah, so we're not too far.

**Me:** Not too. Nice. Right on.

**Other:** Very cool, but it's nice to meet you guys. So fair warning. I've went over the dock. I don't have much contacts outside of that. So whatever would be helpful, context wise to start there that might be the most beneficial and then happy to take that in any direction. I had a couple of questions. But aside from that, would just be really curious to learn more.

**Me:** Before that. We love to hear about Chetan as well. He's the founder of Glass. Chetan. Do you want to maybe give a quick personal background? And I can get started.

**Other:** Yeah. Austin. Nice to meet you. Previous to starting this gig, I was the Chief Product Officer at Corweave. Claudia company and very impressive, by the way. And before that, I was in the AWS computer leadership team. Their AI Cloud business, so, yeah, that's my background. Yeah. One second. I forgot my card. Okay. Go ahead.

**Me:** Perfect. Yeah. No. I'm going to give you a quick sort of insurance to what we're building here, Austin, and then also know quite a bit about you guys as well.

**Other:** Before we get into that. Addy Austin, if you don't mind. Just like a 12 minute overview. I've seen your website. Of course. Yeah. So for myself, Austin. I run essentially all of the marketing community grants function. So think everything from marketing to bd the ecosystem. The whole stretch of gens, and prior to this I spent the bulk of my career two specific companies. One of them was Solana, so I was the ninth hire there and ran go to market. For our initial launch and then global expansion. And then I ran global expansion and go to market for aptos as well. And so a lot of my career has been spent in early stage companies helping them hyperscale phase. So essentially taking startup concept ideation. Go to market and then helping that scale globally. And then I've been with Gensyn for about eight months doing a very similar function for that gen. At its core is essentially a new protocol for machine learning. So we're essentially trying to redefine how reinforcement learning works across distributed systems based on three concepts called signal, scale, eval, and what we're doing is we're currently productizing these concepts one testnet to prove out how each of these concepts can be iterated on and then we're trying to take this to market in Mainnet. We just wrapped up a token sale, which essentially means that the next natural step is going to be a main Net launch. Right now, though, we are just putting the final touches on a bit of pieces. I think like any new tech, the more that we expand out and think we're getting close to finalizing a piece, the more we realize there are 10 other pieces that need some adjustments. But the company itself has been around for about five years. It spent four of those years in the research phase. So the team's about 55, 60 now, with the vast majority of that being doctorate researchers and then engineers working on ML and rl. And so the core product that we were really known for was RL Swarm. And since then, we've released two other products. Technically, three other products. One of them was Code Assist, one of them was Block Assist. Block Assist was essentially an AI agent that dropped into Block Assist with you, no prompts, learned from your actions and behaviors, and assisted you. This was essentially to prove out signal, which is just like what it is. And then scale was code assist, which is very similar to block assist, but in encoding environment where you drop an agent into a coding system with you and not where you prompt Intella what to do. But again, it kind of learns from your behaviors and this was to prove out the scale version of this, that we could implement this technology into something like this that could then be scaled to a much global, broader stage. And so right now, the latest product that we have is Delphi. Essentially, Delphi is competing for models on chain. So it's essentially. Let me send you the link. Right now, a lot of it is done manual, but this is what will be taken to mainnet. Delphi. Essentially the first live prediction market. Based on benchmarks. And so right now we're doing. We just put out a new set. Actually, we're doing our lightweight reasoning benchmark. Prior to this, we were doing our middleweight. But this one's kind of models that you can run locally on your laptop, very small. And what we do is based on evals, you can bet on which one's going to be the best. So it essentially allows you to place bets on technology. So if you look at the Open. And the Claude stuff that's going on. Claude just released Cowork, for example, which is phenomenal. I've been playing around a little bit with it. But this allows you to make bets on technology in sense where you can make a bet on which technology is going to be doing better. And this is proving out signal scale eval all in a singular product at its core. Company is not a product company. We're a tech company. All the productization is just a way to demonstrate the tech. And then from a customer type perspective, Austin, how would you categorize that? Like, who are the. Yes, either. Of the technology side product. You're saying that it's more like a demonstration vehicle for you guys, right? Correct. For the typical clients who work with. Correct. So right now, and this kind of leans more into where we fall into web3 companies. Revenue generation has only recently become a priority. Up to this point, we've been very well funded and the focus has been on just proving out the technology. So we've had more users. We haven't really had what we would see as clients, but I think when we go live. We expect fee switches to be the main way of doing that as you collect fee revenue based off of trades. So right now, Polymarket is doing, on average, about a billion dollars a day in trading volume. Even if they take.005% of that in fees, they're doing very well. For example, I was just reading FanDuel. I did about 50 billion in volume in 2024. And so we're already seeing a massive, massive surge in just activity across these. And we're thinking that the first product will be able to fall into the zeitgeist. Demonstrate the technology, and then from there, we can scale it to much different ways. But at least for Delphi, I've kind of seen more of what I would call the traditional betting market. Participant is probably going to be the very top of the funnel. At the very bottom of the funnel, which is the area that we're actually the most focused on, is folks that want to submit their own evals, for example. So we would see RL ML engineers. Folks that are coming up with these new models that actually want to put them to the testing competition against other models. I would see those as users as well. And so it's kind of everything in between, depending on where in the product they want to fit. But from the models per se and supporting AI, it is mostly providing these platforms for these model providers to submit, at least as part of Delphi. Correct. So almost like you mentioned, I think. What was it similar to Elam arena, but not quite right because. Correct. I would say it's very similar along those lines is that right now we see that as the best demonstration. Of the three components of the technology. The value they bring to market is, like, their evaluation platform is, like, free for users like you and I. And in the back end, what they're trying to do is actually sell to the model providers and say, like, hey, we've got this platform. Where you can upload your models or provide access to us somehow. And we'll let you evaluate these models in real, real world conditions. And they make fees and profit out of that engagement. Do the model providers. Do you guys host these bottles on your network? We're hosting them right now as we kind of refine some of the stuff, I would say. I see that business model is more of like, a B2B model. Where I would say what we're going to be doing is more of like A, B to C, where the individual model providers we're going to be less interested in. It's going to be more the consumers on the other end that are interested in wage earning, which models are going to be the most effective? I see. So it's almost like a betting market. For the models, correct? Yeah. And you guys are adding some platform to enable that, correct? Yeah. As far as we know, it's the first live production ready way that you can actually bet on these models. Got it. Now, outside of running these models and seeing how they perform against specific set of evaluation criteria, Are there other types of usage you see from these hosted models? Because ultimately, you want to see these models deployed in production where somebody is putting them to actual use. Outside of just trying to understand. So is there some notion if you guys wanting to actually tap into that part of the model market also, or is that secondary? I think that would be secondary, at least for right now. We kind of have a few different competing priorities as we make our way to mainnet. I would say we kind of have more of the consumer angle, which I think this covers. And then we have the research angle, which is I dropped a link into our blog post down here, which highlights a few of the pieces. The most recent one that we put out is the LMSR blog post. We kind of have our research angle as well. And so we're currently in the balance of actively contributing consumer products while not letting that muddy the really strong research arm of the company that we have. I see. I would say there's an internal, internal consensus that kind of like the shift of when OpenAI decided to release a chatbot and a lot of the community, the ML space, were not very happy that we were taking this technology that's been around for a really long time and consumerizing it like that. I would say worst striking it very delicate balance with that as well. Interesting we had all these questions was because I was trying to map it to what we are trying to do as a company, right? So essentially it comes down to our belief that all the assets around AI, the models, the way it's the actual data, is going to continue to exponentially increase in value. And then there are going to be categories of customers where it's going to be business critical for them to have a really solid tracking and governance around those assets, where there are different ways and different aspects. From a product capability perspective, we can provide that value. But in your case you guys are taking open source model hosting them on your infrastructure. Maybe you lease Hogwarts from somebody else. And the way you deploy these models in that arena type of setting or the evaluation setting, right? Correct. At least in this demonstration of the tech, I would say that only covers a small fraction of what we are as a company. So at least as part of Delphi, I'm assuming you guys are actually not sensitive about the model itself because it's an open source model, and you guys are probably also not sensitive about the training hardness or the data that is used to exercise those models. Is that I would say yes, for the most part. With the caveat that we do really value the quality of how the data is brought in. So we've recently completed a grant with a company called Quok and what they were instructed to do, and the whole purpose of their grant was to run benchmarking against different models or against different hardware setups to see what was the most effective way of producing quality data on the network. And so they tested, I think, 800 different participants that pulled from our discord that were running a swarm. Which is essentially like any node, they are running GPU, cpus spinning up and then competing against each other for prizes. They essentially ran benchmarks against that to see who was contributing meaningfully to the network. So it wasn't just just because you're running a GPU means your ranked higher. We did have folks that were on some CPU setups that were optimized, and they were producing significantly better data than the GPUs. So we do care to an extent. I think it just depends on what lever of the company we're pulling on. Totally. And some of your end customers, like, from a technology perspective, Because again, Delphi is more demonstration vehicle. And, you know, there might be a situation where, you know, the betting around which model is better kind of translates to, like, some sort of a monetary flow for you guys, of revenue for you guys. From a technology partners perspective, Austin, are there, are there folks or customers where you can actually foresee that, you know what? This particular customer, they might leverage our tech, but at the same time, they're going to either bring their own models or they're going to bring their own data and they're going to be hypersensitive to making sure that they track and the govern access to this. Data, because, again, it might be like a business. I would. I would say yes. Which is, which is one of the things that, like, when I was reviewing through your doc, that I did think was interesting, kind of the, the main question I had around that, at least for the time being, would be production ready versus more theory. Where does that split come from? From what you guys actually have right now. Like what's? Actually production ready, and then what's kind of on the roadmap that you would like to have for the extent of the product? So we're super early in the lifecycle of the company. Right. So, you know, we, we have some internal POCs running that are kind of testing different aspects of the technology that we want to build on, like, for example. You know, one aspect around how we want to secure models is via technology called yet our trusted execution environments. And we have that kind of set up and spun up, and we are like, you know, running evaluations and benchmarks against that to understand how well it works, how clunky it is for customers to use, and if you can build, like, software around a capability like that to make it a whole lot easier for customers to kind of secure their particular models and the association. Right. So we, we have. We have code that is running. You know, I wouldn't call it, like, production ready. I wouldn't want to run like a production. Service on it, but it's like a really good evaluation framework for us. There's the second part that the doc talks about, which is like, data lineage, which is, like, really exciting for some of our enterprise customers that we're talking to. And essentially the use case there is that they want to track. Like, if a model is getting trained, they want to understand everything around it, like, who kicked off that training run. What data is it actually training on? What were some. What hardware was it running on X, Y and Z? Like, features that galore around, like being able to kind of track and govern what's happening on the training side. Right. So to simplify it down, we're calling it Data Lineage. There's. Actually a lot more sophisticated than that. But that's an area where we have seen enterprise customers because they're like, okay, we might be taking an open source model, but once we trained it with our data, it becomes our model. And the data itself is also like internal, proprietary data. So they're sensitive about alternative both the aspects like the model that they have fine tuned and also the data that they're using in order to kind of train it. Right. And they want to make sure they've got really tight controls around how it's used and where it's deployed. Right. Understood. Okay, and then let's say the code and the PoCs that you're currently running are production ready. Where in the stack here do you see decentralization, like, most meaningfully entering the system? Like, where in your ideal world, in this stack does that come in, and where is that the most effective? I think those were the two things I was the most curious. That's a fair question. So decentralization aspect is probably like phase two, maybe even phase three of our go to market plan. The first phase is going to be to validate our ability to set up these really complicated trusted execution environments in a meaningful way across a diverse set of hardware platforms. Right? Like if you have a gpu, let's say that has an Intel CPU tied to it versus an AMD CPU type to it changes if you have a Hopper vs Blackwell environment changes. So there's just a lot of combatorial math and combinations you have to kind of think through. So step one is to build something that actually works across a combination of hardware. And then depending upon where our customers want to take us, like, we have some ideas around setting up marketplaces where it could feature hardware from our own site, it could feature hardware from third parties that we actually bring in. Right. So there are different ways we could potentially go down the path of decentralizing at least the hardware available in a standpoint. But that will come after we've kind of proven the core technology and unigatal solid runtime in running that on our customers own hardware. Right. Because a lot of enterprise customers that we're talking to, they already have, like, contracts with their cloud provider of choice. They're like, okay, well, I have a hundred million dollar contract with aws. And I like what you're building, but I want to use that stack on my hardware. If you use any aws. Right. So let's get that going first. And once we're able to kind of get the service running, then we can go down the path of, like, sourcing either our own hardware, kind of decentralizing from a fleet standpoint. Okay? Does that make sense? That does make sense, yeah. Yeah. I'm coming from the AI world, and I'm learning a lot about the crypto space. There might be a little bit of, like, vice versa. So this is. This is good. It's helpful for me, no? Yeah, it's. There. There's some of the things that takes me a moment to. Click together, but it all does make sense. Okay? As. As far as that timeline, then. And this might be where my information gap lies, is where do you see gents and slotting into this, whether it be on the customer side of things, the integration side of things. I feel like there was a conversation with Ben at some point that I just didn't quite get the full context of. I forget who had it, but this might be where I would be curious to know how we could potentially work together. Yeah, I don't have context on the historical discussion. I not sure if you have.

**Me:** Yeah. Happy to jump in here, right? Just Ben and I just met each other just for a while. Just went through the entrepreneur's first program with gents in the South. I got to know. Him, actually. And just like a couple of deals in the past as well with you guys. But more specifically here, I think sort of what the key points of what you all are building is sort of the RL Swarm, the Block Assist, Code Assist, and Delphi. Given the fact that you all just completed a token sale, now moving toward mainnet launch, I thought it would be kind of the perfect time to reach out for a potential integration. So just to quickly summarize what we're building before sort of how to get the products energies eventually what we're doing, one line is sort of we're building a trust in governance layer for AI systems that kind of sits across environments so cloud on prem potentially decentralized network as well, which is where you guys will slot in. Kind of the core ideas here is that we sort of want binding models, data agents and policies to cryptographic identities. So that's where sort of the on chain component comes in. And we also want runtime policy enforcement over what we can run, where we can run it, under what conditions. So all these policies that we want to enforce.

**Other:** It, okay? Perfect.

**Me:** The other gene, right. That cheapens also brought up is the use of sort of TEES here in order to secure sensitive workloads and data. I think a model IP as well. So not only to verifiable execution piece here, but you're also getting data problems, right? So you've got to tamper evident logs. Of what brand where and sort of what inputs. We use this type thing. So really where the products that are in these slides. I see it and I'd love both y'all's thoughts on this as well. Is trust and decentralized compute for sleep where you guys are kind of bringing it global incentive. Driven ML vertical and also sort of the prediction markets component with Delphi. Right. And you also are kind of bringing we're kind of building a tested sort of policy where execution. And why is that valuable? Right. It's sort of that sensitive models and data can then safely run on untrusted nodes. Right. And so we can also sort of collaborate on verified work and economics here as well, where Gensyn kind of needs strong guarantees that jobs were done correctly. And this just for sake of y'all's SLAs, right? Essentially rewards slashing all that stuff. All provenance and attestation can actually strengthen those verification process. And since I know that's not your square focus. Right. But that is our core focus and that's where I think we could potentially add to your product as well. Where like Yols verification and accounts and layer could actually just kind of be us, right? Type thing. We could also get sort of policy where scheduling for more enterprise clients, right? Where you guys can encode constraints like sort of like jurisdiction, like hardware classes like regulatory compliance, et cetera, et cetera, where you guys can route jobs only to nodes that kind of satisfy those policies, which we can enforce using our tooling. So kind of make your guys network consumable. By more that regulatory user. Sorry, a regulated user. Sort of vertical. Right. And so those are a couple ideas. The last idea here is the one. So if it is kind of like more man, wavy, I think, for lack of a better word. But it's better model discovery and evaluation. We're like kind of Delphi. Can kind of create this live market or go model performance random benchmarks. You could already brought up the point with eval is already being a part of this right or identity provenance. Kind of like help tie sort of evap results back to sort of specific model versions. Training runs and sort of data as well. So it kind of makes Yalls results from Delphi more trustworthy and auditable. So these are just various components of offerings that I think we could kind of slot in and sort of add sort of accurate benefit to what you guys are offering as well.

**Other:** Y. Es. Okay, perfect. That aligns mostly with what I was thinking then when I was reading through everything. The one piece I'm not sure of in this, this might just be a lack of knowledge on my part is where the T slot in and what where they would provide guarantees versus, like, where we would need to rely on like more of a trust based system and how that would potentially work between the two parties.

**Me:** Cool. Just to clarify the questions on sort of the hardware component early TEs themselves and what they're doing. Yeah. So, I mean, it's kind of like guaranteeing execution on the box, right? Like, code and weights can kind of run in this isolated enclave environment.

**Other:** Correct.

**Me:** That's completely off chain and even like the node operator couldn't see your Tampa with them, right? That's kind of the benefit here. So you kind of get a remote attestation from the TE saying, hey, this specific binary or model hash or whatever on this hardware actually ran on it type thing that's what we're offering. So our protocol then kind of looks set on top of that, where it's like, okay, we can still handle incentive design coordination, sort of like higher level verification across many nodes, which is what you guys would probably take care of. And then we could kind of retreat, sort of like a te a test and run as, like. Almost like a higher trust primitive right inside yellowsorville network. So it kind of be like a slot, right, that people could check, being like, hey, we want to use on this node type gene, for example.

**Other:** Understood? Yes. Okay? Got it. Okay, that does make sense. And it's a. It's a bit preemptive, but we have another project that I'm currently working with right now that I think could actually go hand in hand with this.

**Me:** Guys.

**Other:** Quite, quite. Well, I should have more information about tomorrow when I do. If I'm able to share, I'll send over to you guys and see how it could work together. To fit in here, but this could actually work out quite nice. And now I see why Ben wanted us to talk then. Okay? As far as timelines and what would be most beneficial for you guys. In operating with us. Like what? What type of relationship do you think would be the most effective here? We have a grants program. We can do integrations. Like, there's so many different ways we could spin this, but if we wanted to start moving forward, With exploring in, like, a more technical capacity. Around what this would look like. Is there a preference from your side on how that would go?

**Me:** Actually, can I call, let you take this one?

**Other:** Yeah. So, Austin, we are fairly close to getting, like, You know, a solid what I would call as a platform architecture. Down, like again, like I mentioned, we have bits and pieces kind of running. But, you know, we're working on just kind of ironing out, like, what the actual product experience is going to look like and how it's going to work and things like that. So if you guys are interested, you know, in a. In a few weeks from now, we can get together and kind of share, like, additional details with you guys. Like, okay, we've talked about these concepts. We have some POCs kind of working on our side. And, you know, as part of the follow up conversations, we can say like, this is what we're actually planning on building and this is how you would use it. And we can have a much more detailed discussion about how it might integrate into your stack. Right. That sounds great. And by then, I should have a much clearer picture of what Delphi arena will actually look like in productional mainnet. So I think with those two pieces, that'll probably be a pretty productive conversation. Okay? Sounds like a plan. Perfect. So I'll set a reminder just to follow up with you guys and maybe, like, two weeks, so right at the end of the month. If there are any major updates on our end, I'll obviously let you know, but I think this is super interesting. I think this would align very closely with teams and integrations that we want to get involved with us prior to going to mainnet. So timing's perfect. All that as far as actual production. Ready? Do you have a time? Horizon here around when that could be ready. It's going to depend upon, like, what. What component of the stack we end up finding value for for you guys, right? We're scaling right now. Engineers are coding away, so it could be as soon as, like, you know, a couple of months from now. Again, it's going to come down to the details that we'll have to align on Austin. Right. Okay. No problem. That sounds great. I don't want to make a commitment right now because again, we understand you know what that interlock might look like. And what that implies from, like, a product capability standpoint that we need to build out. Understood. I understand that all too well. This was. This was lovely. It was great to meet both of y'all. We have the telegram group. I'm going to loop in Austin on my team who runs dev relations. He kind of helps me keep playing with a lot of other things to make sure all the pieces are. Are moving. I'll start a file for you guys or an internal thing, and I'll just make a note that we'll follow up before the end of the month. And then let's just stay in touch as things continue to move along. But I think there's definitely something here. Okay, sounds good. Well, thank you so much for your time, Austin. We really appreciate it. Yeah, it was super nice to meet both y'all.

**Me:** Appreciate the time, man. Quick question. Are you part of the LA monthly Crypto meetup group chat yet?

**Other:** Is. It is an la thing.

**Me:** I don't know. Rahu from Gauntlet used to run this thing every month. Yeah. I mean, he's now in New York, right? But Gauntlet's still running it, and a couple of my buddies and I actually put him together. Sort of monthly event, so I'll definitely add you to the group.

**Other:** Does he? I'm a big. I'm a big Gauntlet fan, Tarun and folks were part of, like, the early stages of when I got into web3 forever ago, when they were first launching that alongside Solana. So he has a soft spot.

**Me:** Sid. Nice. Do you know Austin Barlow had a foundation?

**Other:** I would love to get included in that.

**Me:** Dude. Yeah.

**Other:** I do know Austin barlow. Yep, I do.

**Me:** That's very cool. Very cool. And mika.

**Other:** Yep. Yeah. When I saw I got looped into the chat, I like was like, oh, yeah, no, Austin I knew Austin quite well.

**Me:** What about me? Code. It used to be a habitat. Actually, before joining the EVML too, I was like a part of.

**Other:** No. So Austin joined probably, like, six months before I left. So the overlap there was minimal. So when I, like when I joined, there was just a couple of us in the office in San Francisco. And then when I left, we were like 150. I do much better in, like smaller scale companies. And then once there's 150 people in 10 orders of reporting and stuff. It just doesn't. I feel too caged. It doesn't work for me. I got a draw from the next call. Thank you so much. It was nice to meet you guys. Have a good.

**Me:** Yeah. Y. Eah. Yeah, it makes sense, dude. So you're probably early octos. Wait. Wow. 100%, bro. 100. Absolute pleasure, guys. Pleasure. Good to meet you.
