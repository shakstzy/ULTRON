---
source: granola
workspace: sei
ingested_at: '2026-05-07T04:23:57.244510Z'
ingest_version: 1
content_hash: blake3:a34d0c1244c41de7c6f4bde6706a4035800c0d08843f095608c95d9784835dda
provider_modified_at: '2026-03-03T14:25:55.770Z'
account: adithya@outerscope.xyz
account_slug: adithya-outerscope
document_id: a045ecda-fd7f-4b5c-80d3-0d4ac526c517
document_id_short: a045ecda
title: Alec <> Adi
created_at: '2026-01-12T20:02:22.590Z'
updated_at: '2026-03-03T14:25:55.770Z'
folders:
- id: 3ca3cb55-d6e1-49ef-961a-8ba2469731a5
  title: SEI
creator:
  name: Adithya
  email: adithya@outerscope.xyz
attendees:
- name: Alec Shaw
  email: alec@seinetwork.io
calendar_event:
  title: Alec <> Adi
  start: '2026-01-12T14:00:00-06:00'
  end: '2026-01-12T14:30:00-06:00'
  url: https://www.google.com/calendar/event?eid=ODZkNGVjZTA3MzY4NDFkNDljMjgxMjg0NjQ5MzgyNjggYWRpdGh5YUBzZWluZXR3b3JrLmlv
  conferencing_url: https://meet.google.com/nct-zssp-kfz
  conferencing_type: Google Meet
transcript_segment_count: 811
duration_ms: 2585717
valid_meeting: true
was_trashed: null
routed_by:
- workspace: sei
  rule: folder:SEI
---

# Alec <> Adi

> 2026-01-12T20:02:22.590Z · duration 43m 5s · 2 attendees

## Attendees

- **Adithya** (creator) <adithya@outerscope.xyz>
- Alec Shaw <alec@seinetwork.io>

## Calendar Event

- Title: Alec <> Adi
- Start: 2026-01-12T14:00:00-06:00
- End: 2026-01-12T14:30:00-06:00
- URL: https://www.google.com/calendar/event?eid=ODZkNGVjZTA3MzY4NDFkNDljMjgxMjg0NjQ5MzgyNjggYWRpdGh5YUBzZWluZXR3b3JrLmlv
- Conferencing: Google Meet https://meet.google.com/nct-zssp-kfz

## AI Notes

### Problem Analysis - Traditional Trading Solutions

- Current overseas trading landscape presents two poor options:

    - CFDs (Contract for Difference brokerages)

          - Extremely sketchy operations
          - Randomly disappear
          - Block withdrawals when users profit
    - On-chain protocols

          - Poor liquidity depth
          - Security vulnerabilities/exploits
          - Trust issues with decentralization claims

### Proposed Solution Architecture

- Perpetual DEX for majors and indices trading

    - Provides 24/7 execution without heavy oracle reliance
    - Capital efficiency through leverage
    - Reduced infrastructure and counterparty risk
- Three core components required:

    1. Frontend - wallet connection, stablecoin deposits, trading interface
    2. Trading infrastructure - matching engine, margin system (outsource to Monaco preferred)
    3. Liquidity partner - market maker for quote execution

### Trading Model Comparison - Trade XYZ vs Ostium

- Trade XYZ model (preferred):

    - Market makers as direct counterparties
    - Unlimited scalability potential
    - No stablecoin liquidity constraints
    - Deeper liquidity access to global sources
    - Upper bound limited only by market maker capacity (Binance-level)
- Ostium model constraints:

    - Traders trade against on-chain liquidity pools (OLP)
    - Volume/open interest capped by stablecoin vault deposits
    - Requires bootstrapping $20M+ stablecoin liquidity day one
    - If one trader uses full pool ($10M position), protocol unusable for others
    - Maximum ~$100M open interest ceiling

### Regulatory Strategy & Market Listing

- Monaco must create and list markets (not Equity Perps frontend)

    - Maintains arms-length relationship similar to Trade XYZ/Hyperliquid
    - Monaco team pushes code updates for custom market logic
    - Cannot be formal partnership - must appear organic
- Market listing framework options:

    1. Consortium approach - Lava, Monaco, market makers coordinate initial 10 markets
    2. Permissionless listing framework (MILF) - $5-10 market creation fee vs Hyperliquid’s $12.5M
- Critical requirement: No KYC implementation

    - KYC requirement = project dead in water
    - Only competitive edge over traditional solutions

### Next Steps

- Alec to draft detailed breakdown:

    - Frontend build requirements
    - Monaco functionality needs
    - Regulatory defense rebuttals for leadership concerns
    - Trade XYZ vs Ostium regulatory analysis
- Document refinement for leadership presentation (Jeff, Gerald)
- Follow-up meeting scheduled for 4:30 PM

---

Chat with meeting transcript: [https://notes.granola.ai/t/79ee8893-6653-401b-bb6b-ba8a2219340a](https://notes.granola.ai/t/79ee8893-6653-401b-bb6b-ba8a2219340a)

## Transcript

**Me:** Regarding Excel classes. What I don't know. Come down. Nothing. Nothing. If I could open this, I'm cutting down.

**Other:** What up, dog?

**Me:** Yo, bro. How's it going?

**Other:** I wish you'd call it even if it Good, man. Good. Yo, check Slack. Cody and I are in another

**Me:** Yeah. Yeah. Just saw your message.

**Other:** Hangout

**Me:** Popping on there.

**Other:** Yeah. No. All good, bro. Just

**Me:** Easy.

**Other:** hop in that.

**Me:** Okay. Catching up.

**Other:** Alright. Bye.

**Me:** Yo. What up, Carrie?

**Other:** Yo. I was just chatting with with Alec, and he said you got

**Me:** Yeah.

**Other:** all. So we were talking about the same thing. Just figured we'd all jam on it a bit.

**Me:** From the sync 30 earlier. Yeah. It makes sense.

**Other:** Cool. And I know we talk at the end of this one.

**Me:** Yeah. Yeah. Yeah. Yeah. This week, I think we're looking to Austium a bit more and then sort of the trade x y z alternatives. I have a couple thoughts on that. Happy to present like, however.

**Other:** Cool.

**Me:** Yeah. And what

**Other:** Yo. Yo. What up? What up? Okay. Let me share my screen here. So, Adithya, by the way, I'm gonna I'm gonna move our one on one back an hour till 04:30 if that works.

**Me:** Yeah.

**Other:** Instead 03:30.

**Me:** 100%. Yeah.

**Other:** Cool. So, Adi, I took the document you gave me. So just context, Cody. After our meeting last week, Adi took the document, created a merge document, I took that again and tried to remerge it a second time. So this is what I hope is short, succinct, distilled. And what I would like to get out of this meeting is, both of you guys base saying, like, what the fuck does that mean, Alec? Like, you need to, like, double click on that, provide more clarity, like, maybe it makes sense to you, but it doesn't make sense to me at all or whatever. Okay? With the objective, we can get this to a point where we can give it to Jeff, Gerald, and, leadership. And they get it. And, we can also identify some potential questions that, you know, they're gonna ask. So with that in mind, let's get started here. So, really, our problem is, twofold. One, a bunch of people overseas have to use these really sketchy brokerages called CFDs. In order to trade stocks. These things are you think DeFi is sketchy? These things are sketchy as fuck. Okay? They disappear randomly. You make money. They just don't let you withdraw. Right? That's your current option. Alternative is you could use on chain protocols, but a lot of them have really shitty liquidity. You don't really trust them. There might be exploits. Right? You get it. So there's two problems with the current market. Either have to use a super sketchy product or you have to use one that's, you know, maybe decentralized, maybe not. You don't really know. Okay. So the solution is a perpetual DEX that lets users trade majors and indices. Right? This will give major institutions and retail traders a novel way to trade the macro landscape with more capital efficiency, I. E, leverage, and less infrastructure and counterparty risk. Okay? Super simple. We're all on board there. Let me pause there for a second. Do you guys like the framing of the problem being twofold? There are CeFi solutions today. Five five solutions, but they're really sketchy. And then the alternative is that the on chain solutions just aren't up to par. Do you think that's a the accurate problem statement?

**Me:** I think, Cody, you muted.

**Other:** Yeah. I was like, yeah. I think I do. Okay. Soon as it passes. The description straightforward. Are the key features. Okay. So we're going right into key features. I scrapped the success metrics for later. Key features are you need a front end, are you going do? You're going to connect your wallet. You're going to deposit stable coins and you're going to trade. Super simple, right? Two, we need trading infrastructure. Okay? This is like the matching, the margin, all that shit. We can outsource that to any cloud I would prefer that we outsource it to Monica. And then third, we need a liquidity partner. This is a market maker. Right? Very simple. It's just executing the quotes. So if we go the Ostium route or if we go the trade XYZ route, both requires market makers. So this is all we need. We need to build the front end. We need to do a business motion with some club. To to list our market. And then we need to find a market maker. To hedge. Do you have any questions on these three core features? Do you think that these are all encompassing too? What p zero needs to be. Core trading engine, margin engine, Oracle and pricing, markets. So so this is the this is the tricky part. This is worth noting. Right? Hyperliquid doesn't allow anyone to create a market. Right? It's it's not it's it's semi permissionless. You have to stay $20,000,000 in order to create a market. We can launch our own cloud. And create our own custom markets or we can build a custom market on top of Monaco. Or some other cloud. I would prefer that we build it on top of Monaco. And Monaco or our team will have to build the logic. Is really just, like, what's the ticker? What's the oracle? And I have I have some of the those that information down there. But, it will require either, Monaco or the or us. To push an update to the Monaco code. Does that make sense? Monaco today, like, you can't can't just launch a market. Like, Monaco's team is gonna have to create a new market for us. The same way that they create a new market for any they will have to create a new market for us. So that's like a legal consideration. But I just want double click on the fact that I had just because you have a club doesn't mean that club is gonna list your markets. So we still have to activate Monaco list our markets. Just in regards to the arms length relationship between Monaco and so Or between them and this brand. Okay. I think we're good here. Ignore p one features. Yes. User journey is normal. You guys understand how traders trade. This is the most important part. Do you guys wanna have a discussion around the liquidity architecture of the two models? Sure. Because everything I just discussed way of describing this. K. So when you trade on hyperliquid, or trade x y z, sorry, market makers are your counterparty. K. There's no HLP. You guys you get that? If I yep. Post an order, someone, a market maker has to come in with their own capital and be the opposite side of that order. When you trade on Assia, OLP becomes the opposite side of your order, not a market maker. K? So what is the role of market makers in Osteo? So say, like, Cody, you go long a $100 on Osteum. That means OLP, the Osteum Vault is short. A $100,000. You guys get that? Okay. Ostium's vault is short. Trader's long. If the trader wins, Ostium loses money. So market makers come in and hedge OLP. They hedge the actual on train walls. And this has pretty significant implications both, legally and how we go this thing to market, But with that, I mean, I I would like to pause there and collect any I don't think you guys are gonna have any because it doesn't sound like it's resonating deeply. But tell me where your mind's at after hearing those two comments about osteum versus trite. So is this different than I guess, a any other perp decks where you have? Like, my thinking, why can't we have a club? Why can't we use stork, chain link, or pits price oracles for stocks? And just put those on the club and go get lava and you know, our partners to market make it. And it just looks and feels like type soul. But instead it's NVIDIA, Tesla, stock stock stock. Mean, 100%, but you said something interesting there, which was like fork a cloud and then add the parameters. We should not build a second roll up. To build our own clock. We should make Monaco add those markets to Monaco. So I do want to do exactly what you said. But instead of building a second club and then doing on trend off chain architecture, for a second cloud. We simply have Monaco add NVIDIA whatever fucking markets we want. And then we're done. It's a Mhmm. Thirty second lift for them, and then we don't have to build our own cloud. Yep. Can do that. If Have you guys looked at best markets? Paul, who's, like, the third option in this category? They're like Osteum. Is it a pool? It's like an AMM model? Okay. None of these are AMMs. None of them are AMS. The the consideration is just who's the counterparty. Is it retail depositors in the vaults? Or is it a market maker directly? The price is always quoted via market maker. It's never quoted according to the liquidity on chain. So if you have good relationships with the market makers, you should always go to trade XYZ route. Long story short, you have complete scalability opportunity. If you have a good relationship with a market maker and you go trade x y z route, if you, go the Ostium route, you are confined by how much stablecoins you have in the pool. So if there's a $100,000,000 of stablecoins in Ostium's vault, it can pass its upper bound of open interest. Where in theory, Hyperliquid can scale indefinitely. As much as liquidity as there is offline.

**Me:** So so just to, like, summarize here, right, like, each each position, like, the trade x y z style plus HIV three model, you get depth. Kinda like execution primitives that are always on. Internal price discovery as well. But you're kinda like the the drawback to that model is, like, you're kinda getting, like, long stake requirements of some kind. Right? And, like, you also have, like, bank broken strings for, like, market makers and whatnot. Whereas, like, like, like, request for quote and, like, on chain liquidity provisioning Right? It's, like, better for, like, block size, like, liquidity stuff. Some forms, like, capital efficiency downtime. Or but, like,

**Other:** I love

**Me:** it's downtime, right, type thing. When, like, oracles are all

**Other:** We just said a lot of things. We just said, like, 10 different things. I'm happy to go through each one of those.

**Me:** So so, like, the the downside with the trade x y z style is, like, you're getting sort of, like, launch date That's, the only downside. Right? Like, kinda

**Other:** This this is my thought. The the the issue with Osteum's is people can only use the protocol as much as stablecoins are in the vaults.

**Me:** Right. So, like, you have to

**Other:** So you have to run a bit. You have to pay for maybe $20,000,000 of stablecoin liquidity day one just to get the to make your system usable.

**Me:** Yeah.

**Other:** Where hyperliquid if you open up a I don't know, Oh, you post a limit order,

**Me:** Yeah.

**Other:** that you want to buy some Bitcoin.

**Me:** A market take the opposite position regardless. Yeah.

**Other:** Can do infinity size on that.

**Me:** Yeah. Right. Right. Right. Right. Right.

**Other:** You're not confined by the stablecoin.

**Me:** Yeah. Right.

**Other:** Deposits. So that's that's if you have a good relationship with

**Me:** Yeah. Yeah.

**Other:** market makers, I would always go that route instead of going the stablecoin route. So that's just kind of like the first comment on the pitfalls or constraints of the Osteum model.

**Me:** Yeah.

**Other:** It is yes, you are confined by the liquidity

**Me:** Right.

**Other:** in OLP.

**Me:** That makes sense.

**Other:** So what other thoughts? I mean, you just said a lot of good stuff, but it was just too fast. I couldn't follow

**Me:** None. Yeah. So so, basically, like, the benefits of Ostium, right, and, like, request for quote pricing is, like, you're getting better block size liquidity and capital efficiency rate in your markets.

**Other:** Why does that why?

**Me:** Like like, if you have, like, sort of a large order size for request for quote, like, you can kinda like, literally, as the name Right? Like, you don't have to take price. You can, like, sort of make price as well. That's kind of the thesis.

**Other:** Well, so in summary, you're saying in the Ostia model, you'll you'll get better quotes?

**Me:** Yeah. Like, theoretically. Like, if you have, like, a large enough order size or if, like, people are, like, to counter your order.

**Other:** Well, I think in in either one, like, the if any I mean, if anything, the hyper liquid one would have much deeper liquidity. Because, like, you you put an order for a million Bitcoin as a limit, Any market maker can come in and do the million. Yeah. I think Osteum would it it has constraints on on size.

**Me:** And, wait, am I misunderstanding RFQ? Like, aren't you able to, like, sort of like, also set price? Like, you can request a price if you have like, a large enough production rate type thing. That, like, folks can come in and then sort of, like, take us well on the opposite side.

**Other:** Yes. But that's exactly what we were just kinda describing as, like, the market maker. Right? Where, like, the in Ostium,

**Me:** Yeah.

**Other:** there's only $20,000,000 of stablecoins, the position can only the counter position can only be 20,000,000.

**Me:** Right.

**Other:** Because that's all that's available for the

**Me:** So even if you

**Other:** the the market maker to use to hedge. They can't they can't use their own books.

**Me:** write the same. Yeah. The like, the liquidity is still, like, gonna get screwed, basically, the stablecoin method unless you boost your app enough liquidity initially. To, like, match that up

**Other:** Yeah. You have to bootstrap all the liquidity. So let's just say you got $10,000,000 of stable coins.

**Me:** Yeah. Sure.

**Other:** Wants to do a $10,000,000 position,

**Me:** Yeah.

**Other:** no one else can trade.

**Me:** Sure. Makes sense.

**Other:** But in hyperliquid, you trade x y z. You do a $10,000,000 position. And then I come in $10,000,000 position. Both market makers can satisfy the other side of that.

**Me:** Right.

**Other:** They don't have to use the on chain capital which is the stablecoins.

**Me:** Right. Right. Makes sense. Makes sense.

**Other:** So that is a very, very important design decision. And I think the takeaway from finding this is that in the event that you have good relationships with market makers, you should always do the trade XYZ route. But then you're running into legal considerations because you're running an illegal exchange. So that's where you need to be on top of a permissionless market. And that's where we're hitting really into the weeds now. But that's where you have to go through a public governance motion.

**Me:** Nice. Makes sense.

**Other:** So, anyways, let yeah. Let's let's back it up again. Where are your thoughts on these two? You had some good questions. Think again, kinda where's your mind at with these And also with Osteum, you can't do twenty four seven markets.

**Me:** Right. Yeah. Like so I've, like, written more thoughts, like, a more thought section, like, on the bottom of the deck or sorry, like, doc. So the the trade x y z style club, like, basically, has, like, you know, sort of a ton of growth, that, like, know, also surged in early twenty twenty six is what research shows. So twenty four seven execution as you just mentioned without, like, heavy Oracle reliance on, like, historic or anything. Could be possible with this model. It also is, like, promising people, like, raise rates, like, the the narrative is, like, ever present.

**Other:** Yes. I

**Me:** And you also have, like, capital efficiency for large trade because you're more

**Other:** chose to be

**Me:** are sort of coming in with deep pockets of liquidity to counter your, trades. Let's see. And then, yeah, like, for depth, basically, and then RFQ for discretion. So, basically, like, if you want, like, sort of private orders or anything, then leak kinda, like, maybe optimize that on, say, using this type of model. And so if you have, like, sort of submillisecond trades on Monaco, right, then, like, that's kind of, going to be like, you can basically rely on that infrastructure for building out, like, your clubs. You don't have to double build Let's see. Trade x y z, for scalability, and then, they also like, sort of traction with RWAs. And then, that's not really, like, sort of a listing point. Honestly, a lot of what you said, dude, like, basically, he's getting deeper liquidity as you mentioned, I guess, sort of with, a market maker trade. Taking the opposite position. For for bootstrapping sort of, liquidity, like, do you see anything tremendously successful or, like, any sort of like like, only things that I saw successful with my research were, like, bullshit points programs that you kinda had to, like, pay to play. Type thing in order to boost your liquidity.

**Other:** Well, you don't have to bootstrap liquidity and the trade x plus z route.

**Me:** But not not not being x y z. I'm saying, like, the the alternative play. Sort of where you have, like, a stable

**Other:** Yeah. Fucking bullshit. Same bullshit as that eight decks.

**Me:** Yeah. Yeah.

**Other:** It's just with stable coin farm.

**Me:** Okay. Makes sense.

**Other:** Alec, you know, went to bootstrap with trade x y z. We bootstrap relationships. I mean, realistically, guys, like, this is the key takeaway. Like, outstanding question has been, like, why do we wanna go Ostium versus trade x y z? And one is a, like, liquidity, like, liquidity def conversation? Mean, the other one is yet on on which makes the most set? I looked at the regulatory side of both, of these, it feels like everybody's just risk off. Like, they geo blocked The US. But I'll tell you exactly why. Is, like, permissionless, decentralized, but they're still making the decision to list even if, like, the ethos is permissionless. And I'll say that They're making they're making the decision to list but they're publishing the logic saying, like, look. Like, we built this perpetual motion machine. It cannot it'll never turn off. It cannot turn off. If you'd like to play in it play with it. Because you're a fucking nerd. This is how you do it. K? You know what I'm saying? Like, it's it's 100% permissionless and non upgradable. So the trader trades against the pool, and then the market maker balances the pool. Right? It's all on chain. I. E, they built an open source protocol. They're not operating anything. They they didn't list a single market. And then you might be asking, well, how is trade XYZ doing? This? It's because they're not operating the club. They listed a market on hyperliquid and paid $12,000,000 just for regulatory safe Does that make sense? Think we lost Cody.

**Me:** Oh, right. Probably did anything. Yeah. So he has post. Well, I mean, dude, then the the choice seems pretty obvious to take the deeper pull of liquidity. Right? Like, what like, why is there so much, like, sort of

**Other:** Because either way, we're doing it's illegal. Like, that's like, we haven't even gotten to the fucking meat of this.

**Me:** Yeah.

**Other:** One second.

**Me:** Let me ping him on Slack, see if he's on there.

**Other:** Welcome. Bye. All these protocols are so fucking illegal. It's hilarious.

**Me:** Yeah, dude. I mean, it's all just, reshuffle marketing bullshit with some sort of legal protection to cover their ass. I think he's computer prose. What'd say?

**Other:** Because you know so this is what Gerald's gonna say to us. She's gonna say, like, sick. You guys built an illegal exchange. Like, fuck yourself. So

**Me:** Right.

**Other:** the question is, like, how did how was Austium legal then? It's because users trade against on chain liquidity pool. K?

**Me:** Yeah.

**Other:** You're not trading you're not trading against market makers.

**Me:** Yeah.

**Other:** You know what I'm saying? You don't need you don't need to see how much market how much liquidity the market maker

**Me:** Right.

**Other:** because you can see

**Me:** Right.

**Other:** you can see the capital on chain. Right? So if I win,

**Me:** Right.

**Other:** my money is sitting right there. They gotta give it to me. So it's there's no there's no boss deciding

**Me:** Right. Right.

**Other:** does I gotta get paid out? Where market makers

**Me:** Are the yeah.

**Other:** in in in trade, they can just not pay you.

**Me:** Yeah. Fact

**Other:** Don't have to.

**Me:** Facts. Yeah. Legally.

**Other:** And and because of that, typically, in order to mitigate that risk, you have to register

**Me:** Right.

**Other:** You have to get regulated. Right?

**Me:** Right.

**Other:** But create XYZ says, no. No. No. We're not actually doing that. We you know, hyperliquid built the market. We're just the front end.

**Me:** Right.

**Other:** So Tony, we lost you then. But I think Yeah. My my computer fully restarted, so I didn't hear any of that last discourse. Sorry. No worries. No worries. We're just trying to narrow down, like, really, what are these questions? What what are the crux of the Osteum versus the trade x y z debate? Like, what are we actually trying to decide on? One is like liquidity depth and structure. One is how, yeah, markets are listed, I guess, may that's what that question is. Yeah. I'll yeah. We'll talk about that right now. So in a perfect world, excluding legality, we would love to, just do the trade x y z route. Okay. And why? That's because you don't we don't need to bootstrap stablecoins. Do you agree with that thesis? We were just talking about liquidity, you have two options. Osteum requires stable coins and trade requires just market makers. Which would you prefer to build? Hypothetically?

**Me:** From liquid

**Other:** Say that again?

**Me:** from a liquidity standpoint, it'd be market makers for debt.

**Other:** Yeah. If you were building a DAX,

**Me:** Right?

**Other:** and you had two options, one which was your volume and open interest is confined by the amount of stablecoins you have in the vaults. Or option b, which is you can do unlimited size you gotta do is no market makers. You'd probably go option B to not have to attract a shitload of stablecoin liquidity. So with that in mind, we would like to go that route. But then why aren't other why why would Osteum have ever done this? It's because of regulatory risk. Okay. How is Austium doing this? It's because traders don't trade against market makers. Okay? Traders trade against an on chain pool of capital. Makes sense? Where on trade XYZ, you're trading directly against a market maker. That arm's length relationship is the legal protection. For Ostia. Okay. So then you might be thinking, why is Trade XYZ Running, You Know, Legal Brokerage Out Of The United States? It's because all they're doing is running a front end. Their market lives on someone else's cloud. Someone else is running the illegal infrastructure. And all trade XYZ of doing is running a front end. Okay? Except no there's no permissionless clob in existence right now. Don't exist. Mhmm. Right? If you want to list on hyperliquid, why would you do that? Just for the regulatory benefit. Saying, look. We're not running the club. Hyperliquid's running the club. That cost you $12,500,000. You know what I'm saying? So, like, that's why they paid that. They paid the 12,500,000.0 because if they did their own CLOB, they're running an illegal ATS. So you can you have two options. You can either do everything on chain and make your traders trade against the liquidity pool or you can have someone else host your markets, which is why we have to host our market on Monaco. Got it. Yeah. No. It makes sense. Then we lean in and do it on market. We lean in and do it on Monaco. And we have to just decide how we want to frame that up. Because I don't want this to look like well, one, if Monaco launches it and operates the front end, it's gonna be a a regulatory headache. And if this equity perps front end launches the market, also illegal. So Monaco has to build the market. And then Equity Perp's front end has to come in organically. As the, front end for that market. Cool. Can you put, like, a couple bullet points around that commentary together? I think that is a key point we're gonna have to defend. Yeah. That's the meat of all this. It's like You're exactly right. Like, So just, like, synthesize it in a takeaway. Yeah, of, like, both points. Like, the market the club has to be Monaco because. Of this yada yada yada. What you just stated. Yep. So So we want the trade XYZ model. So we don't have to attract the stable coin liquidity. But we need to defend the stance that we didn't list the market. Yeah. How's Vess doing it? Just wing it, like, yellowing? Regulation? Yeah. To my understanding, Vest is just running their own oh, excuse me. Osteum vest and Osteum are the same. Vest in osteomer descent and vest Just risk seven million dollars a TBL. Got it. Okay. And and that we can do that. Again, we can launch Like, even with yeah. Look up perp's DeFi Lama. Activity. Like, that's the point of having a CLOB too is it's very cap efficient. Like, even if Vest yeah, trade's definitely dominating this category. But vest is where? It's right here. You can look at my screen too. 34. Yeah. So they have 6 mil in TDL. But they're still doing over a 100 mil a day, it looks like. In volume or, like, 50 to 100 mil, I should say. Yeah. They have 30,000,000 open interest right now. But this is not a quote. What is trade? Mhmm. What is trade open interest? 30 bill in volume over the last thirty days is crazy. Or 11 bill. Yeah. It's not reading open interest because I don't know if DeFi Llama has parsed apart open interest from Hyperliquid. Core versus the, h I p three markets. Got it. Or they're just not showing open interest for some other reason. 300 mil open interest. So you just get deeper liquidity on this model. It doesn't matter. That's the the whole debate here. We're getting into mechanism and nuances, but, like, Osteum is confined by the amount of stablecoins that live on their in their vaults. With the vest. It is impossible to open $300,000,000 worth of positions on Vest today because they are constrained by their stablecoins. Trade XYZ can scale as much as their market makers can inventory positions. So they can go up to 10,000,000,000 However much winter Mute is willing to take the other side of. So what's the upper bound of liquidity? For trade? It's finance. I can get into why, but it's not important right now. But Osteum is capped at maybe a 100 mil. Open interest. And, trade x y z can scale all the way up to the global liquidity sources. Because liquidity is sourced off chain. When you start dealing with when you start matching traders and market makers directly, that's illegal. And you have to register to do that. So we need to have Monaco create that market. Got it. Okay. I see we move forward with this model, yeah, and build on top of Monaco. I I think so too. And then I mean, really, the the biggest barrier here is and the only reason this is possible for us is because we can call up Monaco and say, hypothetically, if you guys were going to build perps for these five markets, we would love to build a front end for it. And then we're done. You know what I'm saying? Mhmm. That that is, like, it has to it can only be done in passing. It can only we it can't be a formal relationship. Just like Trade XYZ and Hyperliquid are independent, We have to have that same relationship with Monaco at a tech level. Mhmm. Was there a question there? No. I'm just making the stance that we so Okay. We need to defend in court that Simran and founder of Equity Perf's front end did not collude. How Hyperliquid is doing that is they created HIP three and it cost $20,000,000 to prove you're not colluding. Mhmm. I have I have mechanisms that I would recommend of how we do that. If I introduce them to Gerald, Gerald's gonna say, just told me that's illegal. Yeah. That could go back to, like, that coalition we talked about of it's Monaco Research. It's the market makers, and it's this front end. Right? And then it's three parties deciding to list something as well. It becomes a bit more decentralized. Yeah. That's a that's an angle. That's 100% an angle. And then for the first 10 markets we list, we just tap the consortium. This, and Monaco. All internal, you know, partnerships, really. And we say, hey. We're gonna list these 10 stocks to start it off. It's not like trades listing a new one every day. They probably picked their initial cohort and then just launched it to the world. Well, funny enough, market makers and the front ends are allowed to talk and negotiate. And Hyperliquid or Monaco has to stay out of the discussion. That's it. Like, on h I p three, the the front end is expected to negotiate with the market makers themselves. So we could do the consortium approach. We can do the and then alternative too is, like, Monica can publish a framework for how you launch markets on Monaco. Mhmm. Which we have to do eventually too because unless we wanna register as an ATS, we have to create a permissionless listing for markets. The market initiation and listing framework. Spell it out. Act act make it an acronym. Is it MILF? Yeah. MILF framework, boys. So but we do We we probably aren't gonna do it. But yeah. No. I get it. I get it. But you're but, like, this would just be the sense of, like, Mhmm. Like, Simran posts a blog and says, look. Hyperliquid, it costs $20,000,000 for you to list on the CLob. I have a new CLob. It only costs $10 to list on us. To create a market. Who wants to create one? Equity perps front end comes in, creates five new markets. We run trade XYZ's whole go to market back on them, but it doesn't cost us $12,500,000. Like, we could build we could build this equity per on top of hyperliquid today, but it would literally cost us 12.5 mil. Let's just run this whole thing back on, say, and only charge front ends 5 or $10 to to do this, to spin up a market. And there you go. You know? Like, hey. We're just like hyper liquid, but it doesn't cost $20,000,000. Mhmm. Okay. Yeah. Let's refine some of these notes a bit. I think we're on the right track. I think we rip the trade model on top of Monaco similar to HL as just a starting point. And then really refine that MVP of just, like, how could we basically vibe code this to existence in two weeks? Obviously, we're not gonna, but, like, just that mental model of what is the bare bones, you know, interface and back end to allow someone to take a leverage position on Tesla or Nvidia. Yeah. Okay. Assuming we go to trade XYZ routes, I can draft up, yeah, basically what I view as. Like you like you mentioned, what we would have to build what Monaco may have to build, what functionality they'd have to unlock for us Mhmm. And then, yeah, the the meat here is though kind of like, how do we protect our butts I'll come up with a couple rebuttals to what I believe Gerald is going to ask. And, also, I'll try to elaborate on, like, how I believe trade XYZ and how I believe Osteum are skirted regulation. Because the only edge here is no KYC, by way. If we have to KYC any of this stuff, we're it's not worth building. FYI. Mhmm. Yeah. If we have the KYC, we're dead in the water. So, like, the only question is, like, how do we build this in, a non KYC way? Yep. Alright. Yeah. Let's refine this a little bit. Feel free to send it over. It's in a good spot later today or tomorrow. I gotta jump now. I'm just getting pinged a couple different ways on stuff, but No. Thanks for talking through this. I know it was just a lot of information. All over the place, but I'll clean it up. This was helpful. Cool. Any idea, I'll talk to you in

**Me:** Okay. Perfect.

**Other:** like, 04:30 or so. Nice. Yeah. See you guys. Thanks. Peace.

**Me:** Sounds like a plan.
