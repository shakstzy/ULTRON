---
source: granola
workspace: sei
ingested_at: '2026-05-07T04:23:57.244510Z'
ingest_version: 1
content_hash: blake3:df0d6157d9c9725b7e6b57424e6a13837d1607438e3b5655e46ab0e963b39486
provider_modified_at: '2026-03-03T10:37:28.695Z'
account: adithya@outerscope.xyz
account_slug: adithya-outerscope
document_id: 042e7474-882c-487a-ad8f-cc81a21d2660
document_id_short: 042e7474
title: Kurt Larsen / Adithya Kumar - 30min Meeting
created_at: '2026-01-07T16:02:35.858Z'
updated_at: '2026-03-03T10:37:28.695Z'
folders:
- id: 3ca3cb55-d6e1-49ef-961a-8ba2469731a5
  title: SEI
creator:
  name: Adithya
  email: adithya@outerscope.xyz
attendees:
- name: null
  email: kurt@rhinestone.wtf
- name: Chetan Kapoor
  email: chetan@seinetwork.io
calendar_event:
  title: Kurt Larsen / Adithya Kumar - 30min Meeting
  start: '2026-01-07T10:00:00-06:00'
  end: '2026-01-07T10:30:00-06:00'
  url: https://www.google.com/calendar/event?eid=NzNkMDM5YjQ1MGQ0NDNjMzg3MTVjNTBmOTI4YjQwNTAgYWRpdGh5YUBvdXRlcnNjb3BlLnh5eg
  conferencing_url: https://meet.google.com/zpk-qwte-swd
  conferencing_type: Google Meet
transcript_segment_count: 98
duration_ms: 1219760
valid_meeting: true
was_trashed: null
routed_by:
- workspace: sei
  rule: folder:SEI
---

# Kurt Larsen / Adithya Kumar - 30min Meeting

> 2026-01-07T16:02:35.858Z · duration 20m 19s · 3 attendees

## Attendees

- **Adithya** (creator) <adithya@outerscope.xyz>
- <kurt@rhinestone.wtf>
- Chetan Kapoor <chetan@seinetwork.io>

## Calendar Event

- Title: Kurt Larsen / Adithya Kumar - 30min Meeting
- Start: 2026-01-07T10:00:00-06:00
- End: 2026-01-07T10:30:00-06:00
- URL: https://www.google.com/calendar/event?eid=NzNkMDM5YjQ1MGQ0NDNjMzg3MTVjNTBmOTI4YjQwNTAgYWRpdGh5YUBvdXRlcnNjb3BlLnh5eg
- Conferencing: Google Meet https://meet.google.com/zpk-qwte-swd

## AI Notes

### Company Introductions & Background

- **Rhinestone** (Kurt Larsen, founder)

    - Account abstraction specialists since early 2023
    - Built first modular smart account (ERC 4337 native)
    - Created ERC7579 standard adopted by major wallets: Safe, Biconomy, 0xDev, 3rd Web, OpenZeppelin, OKX, Trust Wallet, Gemini
    - Offers account vendor-agnostic SDK and tooling for smart account development
- **Glass** (Chetan Kapoor, founding CEO, ex-CoreWeave CPO)

    - Privacy-first AI inference platform
    - Uses FHE + TEE for private, verifiable execution
    - 90-95% native speed inference
    - Protects user data and model IP

### Rhinestone’s AI Agent Infrastructure

- Session keys enable agents to transact on users’ behalf with authorized permissions
- Chain abstraction infrastructure for multichain transactions

    - Agents can hold balance on any chain, transact on another
    - Gasless transactions with stablecoin-only accounts
- Example client: **Sci Fi** - cross-chain rebalancing agent for DeFi vaults

    - Agent hits Rhinestone API for any chain transaction
    - Rhinestone constructs call data, agent signs with session key
- Other AI builders: Magic Labs (Newton product), Geezer, Ask Gina

### Potential Collaboration Areas

- **Private agent actions with verifiable permissions**

    - Rhinestone: modular wallet logic, agent identity/permissions
    - Glass: private inference for agent decision-making
- **Enterprise/high-value agent features**

    - Spend limits and role-based access controls
    - Upgradable agent permissions (like Gnosis Zodiac but for agents)
    - Keep strategies, prompts, model IP confidential
- **Agent marketplaces and composability**

    - Define agent capabilities and limitations
    - Swap models through Glass without changing custody/permissions
    - Enable composable agent stacks

### Glass Customer Base & Market Opportunity

- Range from foundational model labs to digital native enterprises
- AI startups moving from hosted APIs to proprietary models

    - Example: Cursor building fine-tuned models to decouple from Anthropic/OpenAI
    - Enterprise customers asking about code lineage, IP protection
- Privacy becoming “extremely pervasive requirement” across Web2/Web3
- Model builders concerned about IP leakage after spending hundreds of millions on development

### Next Steps

- Kurt to share Glass one-pager with AI builder partners
- Potential joint go-to-market for mutual customers needing smart wallet + private AI
- Design partner conversations needed for Glass product development
- Intro opportunities with Sci Fi, Magic Labs, and other Rhinestone AI partners

---

Chat with meeting transcript: [https://notes.granola.ai/t/2d7f09aa-d729-47db-9cad-184e61663702](https://notes.granola.ai/t/2d7f09aa-d729-47db-9cad-184e61663702)

## Transcript

**Me:** It's like breaking up a bit. Yeah. I don't know what's going on. Sure. Yeah, dude. No, man.

**Other:** Hey, Chetan, do we have you?

**Me:** The holiday season. I'm actually going back to LA later today, which is where I'm typically based. LA in New York. It's like trying to slip my time between both.

**Other:** I think so. Can you guys hear me? Okay?

**Me:** Chetan office.

**Other:** Nice. Chetan. We're getting a little bit. Maybe say something again. Testing, testing, one, two.

**Me:** We're good.

**Other:** Okay. Yeah, we've got you. I've got a delay, but I think it's manageable. Okay?

**Me:** Perfect.

**Other:** Nice. Great to meet you.

**Me:** Yeah. So let me provide a bit of context on both sides here. Right. Just real quick. So Kurt's one of the founders of Rhinestone, and Chetan is also sort of the founding CEO of Glass. Chetan has a pretty. Pretty cool background, actually used to be the CPU at Core Weave, if you've heard. Of them.

**Other:** Yep.

**Me:** And I'll also give you maybe sort of three sentence summary. Right. On what we're building here, too. Right. Glasses. Essentially just privacy first. AI inference. Right. And that enables kind of private, verifiable execution of sort of powerful models or small models using trusted hardware and cryptography. So we're using sort of a blend between FHE and TEE for both nonlinear and linear data operations without exposing user data or model ip. So it protects against and provides permissionless near native speed inference. So about 90 to 95% for developers, enterprises and autonomous agents, while also allowing sort of model creators to monetize and specialized models. So that's a bit about glass. Kurt, if you want to maybe give, like, a line or two about Rhinestone, hopefully provide a bit of context for both of us.

**Other:** Nice. Yeah. Yeah, sure. So Rhinestone, like our bread and butter, is a count abstraction. So we originally got started as the team that built the first modular smart account implementation. That was ERC 43 37. Native. That was back in, like, early 2023. We ended up writing the standard on modulus smart accounts. It's called ERC7579 and that's been adopted by pretty much all the like account vendors that matter. So save by economy 0 dev 3rd web open Zeppelin has an implementation okx trust wallet Gemini like at least like just keeps going on and on. And so we've been very fortunate to work very closely with pretty much all those teams on, like, the low level, like, solidity side of, of what they do. And then on the, like, business side, like, what are the products we offer? So we are like, account vendor, agnostic SDK and like, tooling suite for teams that want to build on smart accounts. We bring modules, so features that extend these accounts or components that extend these accounts. And then we also have this, like, chain abstraction infrastructure. So about 12 months ago, we realized that one of the shortcomings of the existing, like, account abstraction, like, transaction infrastructures was that it was single chain. A lot of the clients we were speaking to wanted to be multiple multichain. And so we built a like multichain intent based transaction infrastructure for smart accounts. And so the matter around that was like chain abstraction, the idea that you can have a balance on any chain and then do any kind of transaction on another chain. And so we do work with some teams that are building with AI or building like agent copilots for wallets. Typically, what we find with teams like this is the kind of the wedge or the thing that they're interested in when it comes to smart accounts is session keys. So the ability for the user to authorize a session key for the agent to use on their behalf and transact on their behalf. And then the other thing is is obviously having like this transaction infrastructure and having it be gasless so they can have like stablecoin only accounts where the user and the agent doesn't need to manage gas tokens. But then, like, the agent might be multi chain. So one of the players we're working with does, like multichain rebalancing. Essentially, the agent is like an APY maximizer across all these different vaults on all these different chains. And then no matter what chain, the agent just hits our API and. Says, hey, I want to transact on this chain. And we build, like, the. We, like, construct the call data and build the transactions to make that possible. And then they sign it with a session key and, you know, presto. Like, you kind of get this, I guess this, this cross chain agent with, like, interacting with this simple. API from their perspective, so. Yeah, that's just like, a short overview, I guess. Thank you for that, Kurt. Have you? Like how are you guys leveraging AI and the solution by any chance, if there is any? No. No, no. So we. No, we don't touch it. It's just the teams we work with, they're using AI to build these agents. Got it. So your customers might end up be the ones that are building these agents that benefit from cross chain transactions and commerce. Do I have that right, Kurt? Correct. Yeah. Ok. And then do you have a specific example of a particular customer that could be a good reference point for us to discuss it, like, what kind of agents are they thinking about building? You know, what do we know about, you know, what kind of IP they're kind of building on top of your solution? I think the best example is the one I've already mentioned. They're called Sci Fi, so it's like a cross chain rebalancing agent for defi vaults. I can't talk to the specifics of their AI stack. I only know like the high level and, and kind of my interactions. With them is very much about how they're consuming our products, which makes sense. Got it.

**Me:** Yes. I think the collaboration between Rhinestone and Glossrate, I think where I was thinking three primary points, and both of you guys can correct me if I'm wrong here on either side. Right. But firstly, sort of like you can have private agent actions that have verifiable permissions. Right. Since Rhinestone could. Kind of handle sort of like modular wallet logic, what an agent even is, who an agent is, what it's allowed to do. GLAST would then handle sort of like private inference, right? So basically, how the agent actually decides, like thinking module. And so together, I think agents can now reason oversensitive inputs like strategy. User data treasury management ops in general and so then second also for enterprise or high value agents as well, trading treasury management governance ops as a whole. You guys can enforce spend limits, for example, because none of you guys have done that before for a while. You guys can also have role based access, upgradable agent permissions think almost like Gnosis Zodiac great, but for sort of just agents specifically. And what we could do is also keep these strategies, prompts and model IP kind of confidential as well. So for some of your more large sort of ticket clients that also want to do like inference, privatized inferences becomes a massive sell to them as well. Right. The third area would be agent marketplaces and kind of composability as well. Right. So you guys can kind of define what an agent is allowed to do and what it isn't allowed to do. So think like almost a gentic guardrails. And then we could also kind of. Define how well it does it. Right. Kind of enabling composable agent stacks in a way where developers can swap models through glass. Without sort of changing custody partners, permissions, wallet logic, which often becomes sort of a hassle. But both you guys, correct me if I'm wrong, if I'm, like, making any sort of assumptions here.

**Other:** Yeah, I think my, my question for, for you guys is how, how do you want to work with teams that require some like, element of a wallet to interact on chain? Do you want to offer them an out of the box solution or do you want, do you want like a go to market, like partner where someone like Rhinestone can step in and say, like, hey, here's the SDK, here's the API. This is how you spin up a key. Like, we have had conversations with AI, like, infra providers in the past about how we could kind of team up to. Or they could, like, even wrap our product to offer, like a wallet. And honestly, like, it hasn't. It hasn't really gotten past the expiration phase. And I think that's mainly because the teams we've been chatting to haven't had a lot of traction, but I think that's, like, an angle that we'd be more than happy to explore, obviously. Starting with something that's light touch, where, like, we can just have like, a kind of, you know, a test case, like a beta client in mind where we can partner together.

**Me:** Chetan. Do you want to take this?

**Other:** Yeah. Sorry. Just kind of thinking out loud here, Kurt. It's going to be more on the. It's going to be more on the partnership side. Like, if, you know, there's potential mutual customer partner that wants to, like, leverage your smart wallet kind of technology or cross chain technology. And use that in a secure, verifiable, and private way with, you know, with respect to, like, AI models, then I think there could be, like, a joint go to market, right, where we say you use what Rhinestone is building. You're dealing with really sensitive and private information. You want a platform or solution that gives you the best privacy possible. And that's where the the two solutions can collaborate together. To kind of give a mutual customer, like a one of a kind platform. Yeah, that makes sense. On the, like, who are like, what are the examples of some of the clients that, that you guys are working with? Are they, are they predominantly interacting with, with crypto? Or is it, or is it more general purpose? Just like conversations so far have been, but like, you know, web, two AI companies, Kurt, like, it ranges from the the biggest AI foundational model labs to digital native enterprises. And. And we are starting to have a lot of deep conversation with startups also. Right. And startups in the AI space are moving from some of them. Moving from leveraging just hosted APIs, from Anthropic or OpenAI or the particular cloud provider of choice. To start investing in, like building their own ip, either with fine tuned models or with context engineering and things like that. Where they are in a little bit of a precarious situation in the market right now, where unless and until they innovate above the model layer in a really rapid fashion, there's a risk that they actually get consumed by what the foundational models providers are actually building. Right. So a really good example there would be like Claude code and how it is quickly becoming the default coding agent for people to use and how it's competitive with Cursor and things like that. Right. So now Cursor is going down this path of building their own fine tuned model so that they can actually decouple from having dependencies for either cloud or OpenAI. Right, so, so they are saying, hey, we're going to build a fine tuned knowledge. We've got a massive customer base, we've got insight into how developers, tens, hundreds of thousands of developers are using our product. And instead of all that goodness going back into Entropic, Or OpenAI. We're going to take that, take that data, take that lessons learned into our own fine tuned models, improve our cost structure. Now, one of the things that customers like Cursor is going to run into is, like, as soon as they start penetrating, like, The Enterprise Space Enterprises are going to start asking them questions about, like, where is the code going? What kind of lineage do you have around the code base that has been created here? Autoweb protected. Make sure that the IP that my teams are building doesn't kind of seep into the open space, so that's where there's a lot of interest brewing, interest in this, in this concept around, like, private inference or confidentially executed inference that that customers are excited about. Right. So, and our theory is that this is going to become like an extremely pervasive requirement across Web two and Web three. Right. So anything that is involving agentic transactions or you know, these large scale enterprise deployments, data privacy security is going to, it's going to be top of mind for a lot of these people, right? And we want to make it dead simple these people to actually take advantage of these cutting edge models and agents without creating off the security or the price and performance. Okay. I mean, that makes a ton of sense. Whenever I use any tool for my business, I am thinking, where the fuck is this data going? Exactly. That makes a ton of sense. We're going to have a step by step approach, right? We're going to move very quickly, but first and foremost, you know, one of the data points we're getting from these foundational model builders is like there's tons of IP and capital that is needed to build a foundational models. And the last thing they'll want to do is, like, hosting a provider and somehow the model weights leak. In the ecosystem, right? That's just terrible for them because, you know, again, they spend hundreds of millions of dollars, if not tens of billions of dollars, like in the extreme cases, right? And then you kind of also start tackling the problem of, like, how people are using these models in production and what data is going in, going out, where is it stored, how is it track, who has access to it, who doesn't, right? And that's part of the problem also, we want to take on. Okay, that makes sense. Yeah. I mean, to be honest, like, Mo, when it comes to privacy, like, most of the concerns we hear from our clients is, like, like, on chain privacy. Honestly, haven't run into a lot of teams that have, like, at least disclosed to me. I don't know why they would disclose to me anyway, like, problems, big problems in this. This kind of realm. But if we, like, if you do have a team that is, you know, building some kind of proprietary model or system and they're looking to interact on chain. Then and they have like very strong reasons to maintain self custody then I think like that's where we can be very effective at like essentially you bring them the wallet infrastructure and the abstraction layer to like easily like interact on chain without breaking self custody. Because in a lot of cases, what I have seen so far with AI like coming on chain. Typically, you just give the key to the agent. And, like, if you. If you're a user and you're using one of these agents, you fund the agent, and then the agent has full autonomy to do whatever it wants. In this context, Kurt, like, what is the key? Like, is the key for what? The key is like for the, for the account, like the on chain account, like the key that controls the account. And so with, with our infrastructure, the smart account and the key, the key is separate. So with, with account abstraction, you separate the verification and execution logic. And so this allows you to spin up like ephemeral and scoped keys where the policies and like what is actually authorized is maintained by on chain code. And so even if these keys are leaked, it's not like you're leaking the whole key and expire after either end minutes or hours or days, whatever that is, right? Completely configurable. So. So, yeah, so this is like. Yeah, this is one of the things that, like, the AI builders that we're working with are finding very useful. If it's in this, like, kind of copilot needs to be self custody, I think that's where we can be, like, we can be really helpful. But if it's, it's, if it's a case where, like, the agent is just doing its own thing, so custody is not really a. Problem, then. You know, I think there are probably, to be honest, better partners that can meet those needs. Got it. Okay, cool.

**Me:** Mean, who are maybe some of. Who are the top three builders on Rhinestone right now that are maybe using inference at the moment?

**Other:** So, yeah, Sci Fi is. Is one of the big ones. Another one, which might be worth you talking to, is Magic Labs, who have this new product called Newton. So they use our infrastructure. We've worked very closely with them. There's some smaller startups. Like geezer. As a team we've been speaking with, they have not converted fully to our stack yet. Ask Gina is another one. So there's. There's a handful here.

**Me:** Got you, dude. Yeah. I mean, we love intros to them. Like, essentially, what we're trying to do right now is just like, sort of spin up design partner conversations, pretty much just like, learn from them as we're building, type thing. The product isn't fully built out, and we want to ensure that it's like, you know, sort of tailored to whatever the customer needs. Right. Type thing in terms of all these folks are like, you know, any of these folks would kind of be tremendously helpful for us and from, like, a collaboration perspective on our end. Right. I think once we have convos with these folks, like, we'll also know. Okay, like, this is sort of. I'm also curious, like, how do you guys differ from Nosozodiac dude?

**Other:** Thanks.

**Me:** Have you heard of them by any chance?

**Other:** Yeah, Nosodiac. They do like a. They do this roles based system on safe. Right? That's what you're referring to?

**Me:** Yeah. Yeah. Were we. I think we were chatting about this in, like, Buenos Aires, right? I think last time I chatted with you, I don't know. I don't know if I'd ask.

**Other:** Yeah, yeah. Yeah, the Zodiac team are great. That module is built specifically for safe.

**Me:** Safe, whereas you guys, deployable for wallets.

**Other:** Yeah. For? Like, pretty much, yeah. All account implementations. The other thing, which. Is the devex around? Nosodiac is pretty terrible, to be honest.

**Me:** Yeah. Docs really?

**Other:** It's, like, super complex. And the flexibility is not really there either in terms of, like, the types and policies you can write. So, yeah, I actually don't really know any new teams that use noso Zodiac anymore. It's mostly just a legacy thing when there just wasn't. When session keys weren't a thing. Like, it was like Zodiac roles modules, like, the only thing, so. So, yeah.

**Me:** Yeah. Right. Right. Nice. Okay. No, just curious. Dude. Sick. Okay. Yeah. I mean, would love to plug into some of your partners there on that side. And I appreciate you taking the time here to. To chat with us.

**Other:** Yes. Share some details, like a one pager or something, and I can flick it over to these partners, and if they're interested in chatting, I'll definitely intro you guys.

**Me:** Yeah. Not happy to, dude, absolutely.

**Other:** We've just hired. Sounds good. Thank you so much for hopping on the call, Kurt. Really nice to meet you. Yeah, you too. Good luck with it. Sounds very interesting. All right, great. Thank you. Thanks, guys.

**Me:** Peace out. See you too.
