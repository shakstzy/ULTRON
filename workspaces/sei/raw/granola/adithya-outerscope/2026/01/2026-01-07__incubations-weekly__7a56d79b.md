---
source: granola
workspace: sei
ingested_at: '2026-05-07T04:23:57.244510Z'
ingest_version: 1
content_hash: blake3:c551be65eb0275568a4a630dd2c5dacce8127623a3d2009f9c66f1a3bc242013
provider_modified_at: '2026-01-07T20:54:20.650Z'
account: adithya@outerscope.xyz
account_slug: adithya-outerscope
document_id: 7a56d79b-4f26-4217-988c-42dc71af5f3d
document_id_short: 7a56d79b
title: 'Incubations Weekly '
created_at: '2026-01-07T20:00:34.499Z'
updated_at: '2026-01-07T20:54:20.650Z'
folders:
- id: 3ca3cb55-d6e1-49ef-961a-8ba2469731a5
  title: SEI
creator:
  name: Adithya
  email: adithya@outerscope.xyz
attendees:
- name: null
  email: alec@seinetwork.io
- name: null
  email: cody@seinetwork.io
calendar_event:
  title: 'Incubations Weekly '
  start: '2026-01-07T14:00:00-06:00'
  end: '2026-01-07T14:30:00-06:00'
  url: https://www.google.com/calendar/event?eid=MGpqdThpZWdzYjI3c3ZpN2dqbzQxYmtsdGVfMjAyNjAxMDdUMjAwMDAwWiBhZGl0aHlhQHNlaW5ldHdvcmsuaW8
  conferencing_url: https://meet.google.com/gxd-xqmt-jsa
  conferencing_type: Google Meet
transcript_segment_count: 469
duration_ms: 3200811
valid_meeting: true
was_trashed: null
routed_by:
- workspace: sei
  rule: folder:SEI
---

# Incubations Weekly

> 2026-01-07T20:00:34.499Z · duration 53m 20s · 3 attendees

## Attendees

- **Adithya** (creator) <adithya@outerscope.xyz>
- <alec@seinetwork.io>
- <cody@seinetwork.io>

## Calendar Event

- Title: Incubations Weekly 
- Start: 2026-01-07T14:00:00-06:00
- End: 2026-01-07T14:30:00-06:00
- URL: https://www.google.com/calendar/event?eid=MGpqdThpZWdzYjI3c3ZpN2dqbzQxYmtsdGVfMjAyNjAxMDdUMjAwMDAwWiBhZGl0aHlhQHNlaW5ldHdvcmsuaW8
- Conferencing: Google Meet https://meet.google.com/gxd-xqmt-jsa

## AI Notes

### Rhinestone Call Update

- Met with Chathan about Rhinestone partnership

    - Rhinestone handles account-level permissions, smart wallets with Treasury Alps management
    - Strong need for private inference to protect alpha trading patterns
- Chathan’s feedback: not ideal direct partner (too crypto-focused)

    - Better as intro to their existing customers who fit Glass profile perfectly
    - Should have taken call alone, then brought Chathan for higher-value prospects

### Glass Product Evolution

- Chathan joined as C-suite hire from publicly traded company

    - Changed LinkedIn to “stealth” → immediate VC inbound (A16Z, Sequoia, Lightspeed)
    - Featured in A16Z Scout newsletter “stealth report”
    - Could raise $10-20M in Q1 on pedigree alone
- Product pivot: now B2B SaaS play, doesn’t touch Sei yet

    - 6-month research → build → validate cycle learned
    - Future incubations will focus on de-risked, proven concepts rather than novel research

### Equity Perps vs Prediction Markets Debate

- Alec’s case for equity perps:

    - 85% of infrastructure already built via Monaco
    - Just need front end + market maker relationships (social game, not tech competition)
    - Market size: hundreds of billions vs prediction markets’ ~$100M monthly
    - Easier to bootstrap liquidity than long-tail prediction markets
- Adithya’s case for prediction markets:

    - Fastest path to product-market signal
    - Lower liquidity burden, simpler user experience
    - Net new experience unique to Sei (bonding curve mechanism)
    - No real competition except Melee Markets
- Agreed equity perps = 100x larger market, but prediction markets = unique positioning

### Equity Perps Technical Requirements

- Core problems solved:

    - Non-US traders can’t access US equities leverage
    - US traders limited on leverage perpetual contracts
- MVP components:

    1. Trading interface
    2. Oracle stack (multiple sources, Chainlink integration)
    3. Liquidation engine with deterministic rules
    4. Insurance fund mechanism
- Monaco dependency: Perp engine must be built first

    - Could fork Monaco, run parallel testnet until mainnet ready
    - Success metrics: focus on trader count + volume quality (not wash trading)

### Team & Resource Planning

- Engineering team reorg: Brian/Carson → developer experience

    - Uday, Omar, Cam on incubations
    - Hiring 5-7 more engineers in next 3-4 months
    - Need financial engineers (ex-dYdX background)
- Immediate tasks:

    - Consolidate both PRDs into single document
    - Define T0 MVP: “janky front end with liquidations and matching engine”
    - Research Trade XYZ architecture (built on Algorand, not Hyperliquid)

### Next Steps

- **Alec & Adithya**: Consolidate PRDs by Friday afternoon
- **Cody**: Monaco private testnet launch next week

    - 25 trader invites target
    - Coordinate with foundation for amplification
- **Adithya**: Continue Glass customer discovery calls

    - 4-5 calls booked this week/next
    - Support Chathan on initial validation calls
- **Team**: Friday review session for equity perps + killer app updates

---

Chat with meeting transcript: [https://notes.granola.ai/t/d5a27657-029b-49ca-835e-0137354b0314](https://notes.granola.ai/t/d5a27657-029b-49ca-835e-0137354b0314)

## Transcript

**Me:** Hey, cody. How's it going?

**Other:** Hey. I'm doing good. How are you?

**Me:** Doing well. Doing well.

**Other:** Nice.

**Me:** I hopped on with Rhinestone earlier today. With Chathan, I can give you like, the rundown real quick. So the thought process is Rhinestone has account level permissions. They're one of the first to get smart wallets with sort of Treasury Alps management permissions, all this stuff. A lot of these guys as I mentioned, like in a couple previous conversations. Right. They essentially have sort of a very, very large need to do private inference. Right. Just because they naturally don't want to give out alpha on what they're doing, their trade patterns, any of this stuff to external clients.

**Other:** Yeah. Go for it.

**Me:** Yo, what's up, Alec? And so naturally sensitive, like treasury ops management stuff that you'd want to actually do inference on. They kind of be the perfect partner. They themselves are not, like, perfect partner for us. What I was thinking more so it's like, okay, they could actually naturally integrate glass as one of the. AI providers in their suite and whatnot. Right. But they actually have a ton of really, really good actual customers and whatnot already that are actually doing exactly what I described to them on call, is what confirmed. So it's more of like an intro.

**Other:** What did Chaitan think on that one?

**Me:** Chaethan thought it wasn't, like, really too useful just because it's, like, sort of more crypto land. One, right. And then two. Also, they're not exactly, like, the perfect partner for us, but all their customers are, so I honestly should have taken this one just alone, and then I should have brought them on to like the more high topic this thing is or whatever. I'll do that in the future moving forward where it's like a direct customer rather than sort of like a one to many type deal.

**Other:** Cool. That makes sense. Yeah, we just got to keep plugging away at that.

**Me:** Yeah.

**Other:** And Nathan will get in a good spot on that. Alec, we're just dividing and conquering some blast stuff.

**Me:** Yeah. 100.

**Other:** There's a lot of nitty gritty AI Product validation going on with Chapin and Paul on the lab side. And then Adi and I are just helping out with some customer combos.

**Me:** Oh, nice. Yeah.

**Other:** But a little bit of a slog. So we're looking to get into some. Tell me a little bit about chafing, man. How has it been since he's joined? I don't really know much about the guy. How's it all rolling? Yeah. Jay really likes him because of just his pedigree. He was C suite at, like, a publicly traded company. So he's, like, the first, say, hire to have that under the belt. That'll help with a fundraise. Like he changed his LinkedIn to stealth. Yesterday. And got hit up by, like 30 VCS. Like a 16Z Sequoia Lightspeed, like, bullish, tier one. And then he also found that his name got, like, put in this newsletter that, like, this a 16Z Scout puts together of, like, the stealth report of people who change their name. Oh, so he was in there with, like, heavy hitters.

**Me:** What?

**Other:** And so already, like, he changed that, and he's, like, getting inbound. He could probably raise on that pedigree alone. And of course that's helpful. Like the SEI ecosystem. Having somebody like him with like a big 10 to 20 million dollar fundraise in Q1, right, could be huge for us. All that said. We didn't really have a good lens of the product like me, Paul J and Audi before he joined, it was like. Actually Audi joined like the day Chatham did, so he couldn't. Let Chathan cook. And he's ultimately like the tldr. He's cooked like a B2B SaaS play. That doesn't really touch sei yet. And maybe in the future. And so me and Jeff from the BD side and, like, you and, like, foundation are like, okay, what the fuck? And then Jay and Chathan are. And Paul are just kind of fine with it. And I'm fine with it, too. If we just let them cook and have a big fundraise and then figure out what to do. I'll say this is like, definitely a unique incubation. And we're probably, I can say with confidence, we're not going to do it like this. Going forward. Where the big learning was, we've tried to do something novel with class, like built something net new that nobody in the industry has done. Through research. What that means is that takes six months to research, build a thesis, ie eight, then validate which validation is a slog too of talking to dozens and dozens of people in the industry. Be like, hey, you need this. Hey, you want us to build this for you? Hey, how much will you pay if we do build it? That's where we're at with this. And that's realistically, we're realizing it's like a six month motion. Like I think September, like Glass, the idea of Glass was planted at S.E. labs, right. And now it's going to be February. And so realistically, future incubations and I think we talked a little bit about this, but for both you guys. Is going to be things that have been de risked. Like, Jay puts it in kind of a lazy way of like, we're going to copy something. Sure. But we're going to do something that exists. Make a couple key trade offs. Similar to, like, L1s. Like, not every L1 is Ethereum. Ethereum wasn't bitcoin, solana says in Solida. But we are L1s and those have been de risked. Equity perps will be similar. We don't need to do an AMM model and have the exact assets of Osteom, but we can do our own with our own spin. And I think we're going to talk about probably going to build. I was just going to say I think we're going to talk about this today. But that kind of just like I'm on board with Jay, because oftentimes product isn't what really kind of makes you a killer app. It's like distribution and selling. Just because you build something first does not mean you're all of a sudden going to win. Right? So I'm totally fine with this notion of copying. I think the hard part is the distribution and gaining traction for the product. Yes. But I want to be super ruthless with Time today, too, because we have a couple things to discuss. One. Just take a look at this. It's a new incubations wiki. Like this will be our source of truth for anything. We build out new stuff. So this is your document Just as much as it's mine. So, any notes, any build outs? Like, just. This is for everybody at labs to kind of see what we're working on. Feel free to use this going forward. And then, really, I just. Want to kind of in, like, a streamlined way, like, walk through. These two PRDs for the sake of this call, actually. Given. I don't think we'll get through all four. Like doing two each. I want to just do equity perps today. And I guess. I'm curious on your end. A question. Just super high level like to start this for Adi and Alec based on your like digging into equity perps and a prediction list, prediction market. What do you feel is, like, the highest leverage thing to build in Q1? If we could only touch one of these. What would it be and why? Is something I want to hear from like both of you before we dig in. I just have a quick thought on that. I think that the equity perps are being built. Regardless. Monaco is going to build equity parts. Whether or not we incubated or not or whether we called an incubation. The big lift there is building market maker relationships. So when it comes to, like, incubating equity perps, I would argue it's being incubated via Monaco, and we, we can spin up a front end if we would like. If not, we can source a team to find the front end, but I don't think it's going to be any sort of significant tech build out when it comes to, like, margin considerations, asset listings, RWA partnerships. We're outsourcing all that to Monaco. And, Adithya. That's my two cents. I think that it's a. It's a massive opportunity. We're already doing 85% of the lift by incubating Monaco, and we should absolutely pursue the last 15% by just building a front end or, you know, sourcing a team. And finding a way to get exposure to the success of that team. Yeah. That's kind of it. Like, we probably 99% would dog through this on Monaco. It depends on when Monaco goes to Mainnet. Like, if it doesn't go to Mainnet till Q3, we'll want to rip something like this earlier and then maybe put it on Monaco later. The other thing, too, I've talked to, like, a number of equity perps, teams. I feel like you have to at this point. They're all kind of or just like ecosystem teams. They're going to run full victim to Citrix. T Rex. Like whatever this garb. Dragon Swap. He's in our current eco. This is like that verticalization motion of let's build it fully in house with our world class devs. Have us be the owners of it at first, bring it to market and then put a chin run caliber founder rather than like one of these guys inbounding us through the RFPs. And so that's what look and feel like it's probably cooked in house a little bit and then spun out to a strong enough. I totally agree. And just a quick comment on, like Vertex, I think a lot of those teams are gaining traction in the short term, but they'll ultimately be completely like their lunch is going to be eaten by like, anyone who's like a traditional finance individual that can like, understand how to play the market making game. And like, whoever builds the relationship with the market makers are the ones that are going to have the liquidity. And that's not like a, you know, crypto native motion. And it's not a tech competition either. It's totally a social game. It's a social contract. Debate, and I think that we've got some of the best to do it in Simrin, and we're already making progress by having this whole, like, massive ecosystem that's being built. And then meanwhile, it's like the alternative is, like, they have to talk to, like, an osteom or a vertex. Or these like smaller players that are trying to compete and they really don't have much legs because their model fundamentally is like not going to be scalable unless they're building those market maker relationships. So, yeah, I think that's not there. I'm getting, I'm repeating myself now. It makes sense. Adi, how about you? From, like, looking at both of these on your end, which do you feel like more convicted?

**Me:** Yes. Personally. Yeah. Like, I mean, I agree with the go to market motion. Right. That you mentioned. I think permissionless markets first, just because there's like fastest path to like product market signal. Right. Type thing like a credible MVP is not going to take us too long to ship. And on top of that, like there's lower liquidity like burden on us and infra burden, which might not actually be an issue because we can rely again on like Monica's rails there. But like, it is still like a point to note. And, like, it's also going to be, like, maybe significantly more distribution, but also more upside for sale ultimately, I think. Right. Like, if you have, like, some form of virality that you hit with even, like one product, it's already in the meta, it's already in mindshare. You're also kind of like de risking sort of like the trading app learning curve, because it's extremely simple for users to use. Yeah, I mean, I think those are like, a couple reasons why and, like, why not equity perps, right? Like, again, it's capital and liquidity intensive. There's like, more ways and, like, more breaking points almost for it. And again, like, users kind of need to learn the interface, like all this Ray type thing and. Again, like, actually to your point, Alec as well, it's like, very hard to differentiate earlier, in my opinion. Like, because there's Audi, a bunch of folks that are doing. I would actually kind of like, I don't know if I would disagree with your statement, Cody, that, like, all them are like, I know there's a couple of them that are shit, but I think there's a couple folks also shipping like pretty reliable like sort of infrastructure. At least I do agree to your point. There's not many builders right on these tools yet, and I don't know why that is. I need to do it, but I want to research on that, but there's a couple dots.

**Other:** Yeah, that's fair. I would be curious to look into the like net Monthly volume.

**Me:** Yeah.

**Other:** On perps versus prediction markets. Again? I don't know. I'm guessing perps has is doing, like, close to hundreds of billions. If not like trillions a month.

**Me:** Yeah.

**Other:** In volume. And I would say prediction markets are still new, flashy. But what is Polymarket and Cal she's doing. Maybe 100 million a month.

**Me:** Adithya.

**Other:** Maybe a billion. And so equity equity perps feel potentially 100x bigger market right now.

**Me:** Like a bigger. Yeah.

**Other:** And all these like to say. It's like it could go both ways. I'm just kind of giving the argument of maybe why equity perps, in my opinion.

**Me:** Y.

**Other:** Here. The other thing with these permission, is it, it is going to be harder to bootstrap liquidity on some of these. Like, it's much more of a math formula of, okay, a thousand markets are being created.

**Me:** Eah. Y.

**Other:** 998 of them are dead. Most of the liquidity goes into one. And then market makers are, I think, more willing to make. Just perps right now than these long tail parlays of, like, seven different things that combine sports and geopolitics. So candidly, I think it might be easier to plant our flag into equity perps over the next two, three months. And become a winner there.

**Me:** Eah.

**Other:** Opposed to compete with a Poly and Cal sheet. And if they just roll out. Hey. Let's let users launch their own markets.

**Me:** Y. Eah.

**Other:** Then you're kind of cooked, you know, your product first winning a category that is super nascent. Yeah, I do used to have a quick something to consider. I do think it's worth noting the fact that, like, we could get this prediction mark, though there's going to be some complexities around, like, the bonding curve. It is a net new experience that's going to be unique to say. And. We're not really. There's no competition. Like, really. I mean, I guess you have melee markets. But, like, maybe I should. I should finish my research on melee markets. But to my understanding, there aren't many competitors, if any, it's melee, and melee is not fully permissionless. In my understanding, there's no sort of, like, bonding curve mechanism to seed your own new market. It's a net new experience versus being one of the many equity perps platforms and just kind of fighting for attention. I think that to be honest, my take would be like we build the prediction market. Platform. And we continue to shill and advertise that, and then in the same motion, You just kind of, like, do a marketing campaign around equity perps because there's nothing to build until equity per. Commercial agreements are finished. And that's all on Simrin. Right? So, like, I think equity first. We could start the brand and do all that, but there's nothing that we can even, like, bring online for a couple of months. Unless we, I guess we could do testnet. So I don't know. I'm kind of rambling a bit, but I do. I don't want to, like, toss prediction markets to a side. I think one is a platform play that you can build in the shadow as a smart contract and then the equity purpose is a brand play. And like. That's. That's my. That's my thought on it. But the fact that we do have. We do have spot equity. Assets on monaco. Means that we could, I guess, get the Equity Perps foundation up and running sooner than later. I'm thinking about both. We could do a couple things. Given SEI Labs does own Monaco, We could technically fork it. Build out the first iteration because Simaron's going to want to be in testnet for a while, even though mainnet should and can like will be ready. Then you can kind of run two in tandem. Then we could do this announcement. Okay. You know, the equity purpose is now living on Monaco's, like, core, and then it just combines them in the future. Yeah, it's tbd. I think we do explore both. I know we are already just chatting through a lot of this. So for the sake of this call, And maybe next week or even, like, Friday, we can kind of jump back on and talk through some of these other ones, because there's just a big agenda here. We can also do something where we make this, like a 45 minute call. Next week, but I want to just dig into equity perks. So I want you guys to kind of both talk through your initial PRDs. And maybe Alec, you first. Just because yours is linked here and I know you have a really good lent into the defi world. And then we'll save, like two minutes at the end just for, like, higher level updates and stuff like that. Okay, so I will try and keep this nice and succinct. You guys are already familiar with. What equity perks are. So I won't beat a dead horse here. But the big problem is, like. Non U S traders and US Traders. So if you're in the US you already are. You're not really given a ton of access to leverage perpetual contracts you have to go through like traditional finance OTC desks. You can get the exposure, but it's really complicated. So for like the regular retail trader, you don't have access to leverage in the US and if you're overseas, there's almost no hope that you can get access to US equities, let alone leverage on these things. Right. So the. The problems are pretty straightforward. If you're overseas, you just can't get exposure to US EQUITIES. Let alone fucking leverage. Billions of traders want to trade and speculate on US Assets, but they can't. So what's the opportunity? One we can eat all of the. Okay, so just back up Market opportunity. Our perpetuals gaining traction? You bet your ass they are. You know, last year the volume doubled to $60 trillion. And the decentralized perfect exchanges did 1 trillion monthly by the end of last year. So obviously up until the right metrics. And then let's look at, like, the traditional finance space. You're like, okay, is this just a bunch of fucking crypto retards, like, trading nonsense? No. These instruments are also being used in traditional finance, and they do $7 trillion in notional is the current open interest in these rolling derivative products and. These are products that you'd never have to own the spot. All you do is you speculate on with leverage on price action, right? So there's a shitload of interest in tradfi also. So it's like retail and then also tradify. Right. Two people tapping into this market is a huge demand, but right now, the tradfi ones are really blunky, and then if you're outside of tradfi, there's just no hope that you could ever get access to them. Okay, solution. Solution is snipe exchange. It's a 247 equity perpetuals trading platform for non US traders. And it uses a builder code model. So we don't have to worry about liquidity. We don't have to bother with in theory. The broker dealer and ATS licensing that would be required to sell these things. We're simply a front end. We may have to register as an introducing broker, but the key takeaway here is we're just sitting on top and using builder codes. Success metrics not super important right now. Obviously, it's volume and users and them spending money on our exchange and losing a fuckload of money, okay? V. 0.1. You need a trading interface. You need a couple design partners, right? You need like an RWA issuer. That's denari. You need to spot market maker. We already got these guys with Monaco. You need a perk market maker. We already got these with Monaco. Obviously we haven't identified them, but they will be identified shortly. Monaco question. Do we need the spot assets on a club? In order to have perps for it? Or can you just use like pure oracles for something like that? Just pure synthetics. You could, you could use, you could binance a spot rate. The reason you need spot and perp is because like, as the, as the perpetual price deviates from the spot price that sets the funding rate. So like in a perfect world you would like for your spot price to be actually like internal. But you could also argue that, hey, you don't want that to be manipulated. So maybe you use like a weighted average of binance price feeds plus chainlink price fees, whatever. So sorry. That was a long answer to your question. No, you don't need spot. It's a nice to have. It's not a must have. We could absolutely use. Price feeds for the spot. Okay? So then. So I would just say, like, that we could almost just MVP this out without Spot. And then, obviously, to bolster the product, you'd layer that on after the fact. So maybe that could just go. Instead of, like, beating all these partners, we just tap into, say, chain links, like data feeds, which is already integrated to set. Yeah, Right. So, okay, the spot RWA is not needed, but you absolutely need a. Per. Sorry, rwa Per market maker. You don't need a spot market maker for it. And then, yeah, pretty much. That's V.0.1. All you do is you build a trading interface and then you allow for the natural Monaco motion to continue. In parallel. And you build the front end on top, and then it's like a narrative and branding play. And then depending on if we want to, like, register as a broker dealer, we either give it to a new team or we run it in house and take the fees ourselves. Nice. So I think that's pretty much all the relevant aspects of it. Go to market stuff with simple, I mean. Yeah. It's really just basic defi. You know, you run. You run a testnet campaign, you identify your initial assets, all that. Nothing. Nothing sexy there, just very vanilla. Nice. Yeah. What I want to get to the bottom of, and I think you're close here, is just. What is the bare bones? MVP or something like this? Like what could we have the inch team cook up and, you know, a few weeks? Is it like a couple smart contracts, a couple links to, like, pith or. Chain link and then a UI front end. Or does it go much deeper? Do we need to onboard like these spot assets? Of course. A market maker, but yeah, just going maybe a little like slimmed down of even what was up there. What we need. Helpful. Yeah, we just need Monaco. I mean, like, Monaco's, like, perp engine needs to be built. Like, I can give all the details, but, like, if Monaco's perps work, you just use the API. Like you don't build anything. You just build a front end, and then you send the orders through the API. So, Adithya. That's, that's really it. You don't have to build any sort of contracts, but I can absolutely. List that out in this section right here. Cool. Adi, I want to give you some time to just talk through your section. If you want to share your screen.

**Me:** Yeah. Yeah, yeah.

**Other:** And maybe, like any nuance. From Alec. If it's like the exact same thing, we can just, you know, walk through it pretty quickly. But I want to hear how you, like, approached it.

**Me:** Yeah. I mean, pretty similar, dude. Honestly, can you guys see my screen?

**Other:** Yeah.

**Me:** Okay, Right. So essentially the thesis. I agree with your thesis, right. That equity perhaps really kind of like 100x market, but, like, I feel like the product only works if we win on execution quality and index marks and liquidation integrity too. Right. So, like, that requires a ton of infrastructure to be built, especially off hours.

**Other:** What do you mean by some of those, like, index marks?

**Me:** So, like, basically, like, where, like, at what point, like, you'd sort of get some form of, like, liquidation, right? Type thing. Like, where would, where would users kind of get screwed? Where would they not, like, sort of, like, also quality checks for new assets that were, like, coming on or bringing on type thing, ensuring that there's some form of whitelist, just, like, generic, like sort of. Like defi guardrails, I guess, is what that means, but yeah.

**Other:** Yep. Gotcha.

**Me:** Cool, cool, cool. And so, like, trad by equities are massive, as we know, but access is kind of gated. Like, there's a couple problems, right? Like, you have, like, hours, geo concerns, custodian concerns. And so, like crypto, the crypto market already kind of understands perps as a whole. And the trading 247 piece, which is kind of like what you kind of want to highlight, right? In a way. So the missing piece is kind of bringing on this level of equity exposure on chain with, like, almost like a sex grade experience, right? It's like Web2 has, like, sort of experience for them. And so the. The lesson I've learned right from like, like trade XYZ is like the UI is really not the mode here. It's actually like liquidity, right? And like also like tangible risk systems, right? That like where like you're actually providing like super high level infrastructure that you'd find in like sort of traditional. Markets that, like, are also brought on to, like, the traditional dgen crowd of crypto. Right. In a way. And so if you get that right, then users are kind of concentrating into, like, the venue that doesn't really, like, produce unfair liquidations, per se. No one wants to get liquidated. It's kind of the summary here. Right. And so the product in one sentence would kind of be that, like, this is kind of the canonical, say, L2 venue for equities and index proofs, which Monaco doesn't focus on, is kind of the idea. And you're settling everything in, like USDC or whatever other currency you're using a club for, you know, tight spreads and also ensuring that, like, you know, rapid execution and also, like some form of, like, Oracle layer that's pretty robust. This would kind of be an osteom, you know, coming in or. Something, right? Type thing that provides this data for us. This ensures kind of fair liquidations, like, even in off hours, right? And so what we're actually trying to win at here is, like, the product is safe, right? It, like, has, like, sort of, like, reliable sort of usage, right? Liquidations for, like, not, like, you know. Crazy out of the loop type thing. Right. And so the wedge would again, just kind of like ensure that there's also like multi store sort of oracles as well, basically just building sort of a fair user experience as a whole is what I'm trying to harp on you. Right. And so we really should start narrow with the scope initially in my opinion. Right, so like just like five to ten markets, maybe like in day one Right. Type thing. And so like you essentially have one maybe like flagship perp that you launch. Right. And then like maybe like one to two super large equities, right, which is phase one. And you have very conservative leverage to ensure that you can actually, like, get a sense of, like, okay, what users are, how users are using the product, how to liquidate users. Right? This will like, only progress as, like, we get more data on usage data. Right? And so phase two would then also have, like, more tickers on board, right? Like, once you actually have like surveyed and survived like sort of like real volatility, like now you're actually seeing like what's happening in the market and your insurance system or like liquidity, like, sorry, liquidation system is kind of like more full fledged and proven out right in the market. And then you can have like, you know, the ultimate goal here is, like, you have, like, some level of, like, permissionless listings, right? For lack of a better. Like, this is kind of like the Hip three thing that we were talking about last time, where if you have enough liquidity, you can just start your own market type thing, right? Obviously, you'd have, like, some form of, like, templated deployer synthesis, traditional equities. But, yeah, I mean, that's. That's basically that core system architecture, right? Like, what are we actually needing to build here? You need a club of some kind, right? You need. That's like, a bare minimum. But we already have that with Monica, so that's fine. We can just, like, reuse a lot. Of that code. You do need to, like, kind of define, like, I think differently for Monaco. Right. Like what maker taker fees are. Right. Like what the tick size is here, what the minimum order size. Actually, I guess a lot of that would overlap, but some of them would be kind of new. Right. Since it's fundamentally a different asset. Like, how are you going to liquidate users? What does, like, liquidation look like? Things like this, right? And then for the Oracle stack, this is probably like, our most important sort of, like, decision to make is like, where the hell are you actually pulling your data, right? And so, like, you kind of want.

**Other:** Yeah. You scroll up a little bit?

**Me:** Yeah, yeah, sorry.

**Other:** Sorry to interrupt. You scored a little bit past, like, the P0 stuff.

**Me:** Yeah. Oh, sorry. Sorry. Yeah. I mean, like, basically like. Yeah, sorry. So these, like, phase one, it's like, okay, you have your core markets and whatnot. And then face C, you have sort of have like, broader equities, et cetera, et cetera, for oracles. Right. I think you'd probably want to. Like, use multiple oracles, right? Just, like, prevent. It's just good optics. Right. Type thing. And also, like, legitimately good, just to, like, sort of ensure that you have reliability of price feeds. Let's see. What. Oh, let me plug in my computer here. And you also want some form of like, a liquidation engine as a bare minimum, obviously, right? That's, like, kind of needed. You'd want to ensure that liquidations are like, not like a vibe check, rather like very deterministic set of rules, right, that, like, users can actually, like, publicly read about what else? And then, like, some form of, like, an insurance fund maybe, right? Like, I think. And so, like, you kind of want to maybe bootstrap that via, like, okay, trading fees that, like, you can reroute to, like, some form of insurance fund or some of the, like, the capital that you'd raise for the product, although. That I think is a stupid idea. And then that's about it, dude. I think that's like a majority of everything. I mean, like, what success would kind of look like great. Like, like, you also. Kind of. Like, what I've noted here is, like, there's like, also, like a shit ton of wash trading that I noted, like, a lot. Of my research. So volume should not be the metric we track, but, like, we should actually track, like, quality metrics, right? Like, okay, yes, you would need monthly volume, like, as one of your metrics, but you should also ensure that that's not just, like, from Wash, right? Honestly, it might even be a growth tactic initially. If we were to do wash trading ourselves just to kind of inflate these numbers, which a ton of people have done for their go to market motion. So what else you'd want, like, sort of like, okay, tracking your liquidity spreads, like, tracking, like, whether there are any cascading liquidation events because of, like, certain, like, user error or like, you know, sort of like liquidation engineer. And you, you'd also want to like, I think the biggest north parametric for like success here would probably just be like number of traders, right, that like you could actually get on board and like you actually have like tangible off hour activity where like folks are actually coming to us instead of traditional equity markets because they would probably just go there, like, during regular hours for, like, if they're trying to trade, like, Tesla, dude, like, you want, like a deep liquidity or like you have like a massive, like, sort of buy order, you're going to go to a regular market, right? So I think it's kind of the idea. So we're just, like, we're looking to track tangible.

**Other:** Yeah. Pause there for a sec. Yeah, just curious on that success metric. Curious. Alec, your thoughts too? Number of traders versus, like, pure volume. Right? When you think about, like, hyperliquid, I think they have, like, 20,000 users, like, daily actives, maybe. Weekly actives.

**Me:** Yeah.

**Other:** But they're doing like Billy. Hundreds of billions in volume.

**Me:** Yeah.

**Other:** So they focus more on like higher tier, high volume traders. But then you think of, like, Coinbase, right? They might have, like, 200 million traders globally, but it's the folks, like, dcaing, like, you know, a dollar ten bucks a month.

**Me:** Y. Eah.

**Other:** And so I would argue that high value or high volume traders, less of them, but more volume. Is probably a successful trip on something like this.

**Me:** My question there would be how would you like, like, how would you attract folks with like, really big, like, buy orders? Right. Because wouldn't they just go to like, I mean, the only benefit that you're kind of adding with like sort of an equities market is like, you're getting. Okay, sorry. There's two sort of metrics here. And like, the second one or, sorry, two classes here. And the second one actually kind of speaks to your point. Second class is kind of like, okay, folks with just a ton of crypto sitting around, right, that, like, want access to traditional equity things. But, like, the other latter half is like, okay, like, you could just maybe use an off ramp or something if you're getting better liquidity, right? Type thing on, like, a traditional market. You could just, like, off ramp and then, like, purchase through traditional markets. Right? It's kind of the idea. So, like, what would prevent a user from doing that, would it? Just be like, switching costs or, like, you know, some form of, like, off ramp fee that you wouldn't want to incur.

**Other:** 50x leverage.

**Me:** So okay. Okay. So okay. Damn. Yeah, it makes sense. Actually.

**Other:** Spot. A spot? Yeah, but like using that spot position, so. I can be an absolute degenerate elsewhere on chain.

**Me:** Yeah, yeah. Yeah.

**Other:** Is not possible. In dry five.

**Me:** Yeah. Nice.

**Other:** So even if you just want leverage. So it's like margin and leverage.

**Me:** Yeah. Yeah.

**Other:** That's it. Margin on leverage. That's why.

**Me:** Makes sense.

**Other:** Yeah.

**Me:** Was that part of, like, kind of growth mechanic where it was like, dude, they just offered ridiculous. They were. They were offering kind of ridiculous leverage on, like, a lot of, like, they were the first to do it on, like, a lot of, like, whitelisted assets or whitelisted for them.

**Other:** Nice. What was. Which protocol?

**Me:** Hyperliquid. Was that part of their growth Mechanic? It's offering, like, you know, a ton of leverage. It might have been, actually.

**Other:** Yeah. I mean. I mean, hyperliquids, value prop was just decentralized. Perpetuals, like, perps were great because they offered leverage. Except you had to trust Arthur Hayes. Or you had to trust. You had to trust cz, so you just didn't trust those guys. If you didn't trust those guys, hyperliquid was a great alternative.

**Me:** Yeah. Right. Right. Makes sense.

**Other:** Just like Uniswap if you don't trust Coinbase Hyperliquid if you don't trust Bybit.

**Me:** Right. Six. Yeah, I mean, that's majority of the points I had, honestly.

**Other:** And just a quick thought on the just a quick thought on the success metrics. I don't think we're building like a high value ATS, which is going to have like five hedge funds as their clients running 10 billion annually. I think it's like closer to what you were saying, Adi. It's definitely going to be like sheer number of users is going to be critical. But yeah, if they're a bunch of like, I don't know, fucking negative net worth guys, it's irrelevant. So, like, I think it's going to be a nice hybrid of the two. Probably 80% is just sheer, like, volume. And then like, that 80% crowd is going to attract a couple of the big whales that are, like, doing like, 80% of our volume, only being 20% of the users. Right. Like, it's going to be. I don't know. I can't say I know exactly, but I bet it's going to be a blend of the two. Right. There's going to be. A couple big whales that are trying to screw retail, but it's going to be primarily a retail exchange.

**Me:** Now. Yeah, my point there. I think volume is definitely a critical metric to track, but, like, we should definitely ensure that it's not too much wash, at least initially. And they're ways to detect that. But definitely getting harder. But, yeah, 100%.

**Other:** For wash. Trading is expensive, dude. I ran plenty of wash trading bots. It's no fucking. It's not cheap to wash trade.

**Me:** Yeah. Valid. Oh, yeah. You're paying for vanity metrics 100%.

**Other:** Yeah, it's turbo expensive. Yeah, okay. I totally agree. I totally agree with everything here. I think a lot of what you mentioned, dude. At least my two senses. It's outside of my competency. Doing things like doing risk analysis on margin is just outside of my capacity as a human. I would have to outsource that. And I just think that. I don't know. I don't know if our team has the capacity to build that. I think Simrin does, and I think he's doing it. But to be honest, if we were to incubate this thing fresh, I don't think we'd get it to market. With the current engineers know, but we're getting much better engineers in the next quarter. And we could also bring in some folks. So just. Yeah, like a heads up. The ecosystem. Inch team is getting reorged a bit. I think Jay mentioned this a bit on the all hands. Brian and Carson are going just to do, like, developer experience stuff from the chain. And then it's going to be Uday, Omar and Cam for now, on the incubation side. The goal is to hire between five and seven more in the next three to four months. On some of this personally I've flagged to Clint like archetypes like X DY DX guys sit at all. We need some more financial engineers. And so this will bolster just as a next step there. I know we're over to. But as the next step on that specific prd, if you guys can just collaborate, find some time tomorrow or this afternoon and just consolidate both of your PRDs and then slim them down. Even more. Just like what T0 is is, like, the most remedial MVP. Like, it's literally just a janky front end that supports some assets and has liquidations and a matching engine. Right. And you guys are close to that. So just slim it down a bit. Then everything else can be P1 or P2 plus, like, the things we do to scale it. Like, how do we take a scrappy demo almost to, like, a VC and be like, look what we built? This is the team behind Sei Invest. You know, if that was the motion, But, yeah, if you can consolidate that. Ideally by, like, midday or, like, afternoon Friday. We that can be, like, a good enough spot to present up the totem pole and, like, get buy in from Jay and Jeff and the folks there. But, yeah, I think this is something we can lean into. And then I also. Just. While we have a couple more minutes. Yeah, I'm good on time, by the way.

**Me:** Yeah, me too. Yeah. Alec, I put some time on your calendar. If it's more like afternoon, that's good with you.

**Other:** Cool. Yeah, banya.

**Me:** Okay?

**Other:** Dude. Sweet. Does does trade XYZ not run on hyperliquid? I thought they were just kind of like unit, but for. My understanding is they were an hip three play but worth looking into, I think. Like that's another consolidate the PRDs. And then just give, like, a few bullet points on trade xyz. Because look at this. It has xyz. It has XYZ perps in the bottom. But then it has, like, hyperliquid perfs, implying, like, they're different.

**Me:** It's built on the Algon.

**Other:** Buckets. Yeah, no, it's worth looking into if you can get, like, an answer to that. My. My thinking was it was like a builder code split, like they're a Mach 1 on top of. Money. That's what I. That's what I thought, too. But okay. We'll figure code play hip three needs 500,000 hype. Staked to, like, the pool, that at one point. What is it now, like, 10 million? It was 20 million. A couple months ago. It's like 12 million now. And so that's great. That's, like, where that. That's where I want to dig into. That guy behind trade. XYZ in unit, he feels like a Chinese whale who's super close with the Hyper Liquid team. You said it's Jeff. I think it's someone different, but someone who's basically like an advisor. It's like if Justin was running something or something like that. But let's look into trade a little bit. Both the team behind it and, like, yeah. How their product sits either on or adjacent to hyperliquid. Right. Okay? Yeah. And then it's a super high level. Yeah. Outside of, like, these PR. These PRDs thinking about really, like, honing in on what we're going to build. In q1. Next. And how we define a killer app. Those are, like, two motions. Like I said, we don't really have. An end zone on. We're just going to keep kind of trucking away at those over the next couple weeks, and ideally by, like, I guess, end of Jan, have a really good lens into that. Yeah, but. Yeah. Want to just hear, like, what's top of mind for you guys? More broadly, too. Given. Like you put some notes here. Just talking through some of these. Yeah. Do you want to? I mean, I did a little bit more research, and I tried to add a little bit more hard edges to the killer app idea or that that document. Besides, just my updates are like. We're just working on content for next week's rollout of Monaco's private testnet. I'm coordinated with the partners. Everything's good to go. Partners are just looking to add some. A little bit of copy. We're waiting to get an update from Aaron on the teaser. If the teaser is looking good, we'll push it this week. If not, we'll just scrap the teaser and just do the announcement next week. So realistically, it's these PRDs plus the killer app Doc, and then I was just ensuring everything's good to go for next week for the Monaco Private Alpha. Everything's. I'm feeling good about it. Yeah. I'm adding some time Friday afternoon for us. To go through killer app updates and equity perp updates. Because we're already, you know, over time. And I think that would be helpful to really dig into a bit more on both fronts. Cool. So, yeah, I mean, that's. That's what was like the last seven days. And then looking forward, next week, we got the big push for the Monaco Private Alpha. Just crossing tees and I's. Get that rolled out nicely. I have to coordinate still with the foundation to ensure that they're ready to amplify it next week. And then besides that, just reaching out to traders. So I want to get 25 underneath, like, for my invites in next week. Signed up. And that'll be a blend of FOMO traders, plus, just, like, homies of my network. Nice. You should hit up Dip Wheeler. And say, Parkland. Well, we'll be on day one. We need some of that generational bottom. We do. Okay? And, yeah, fomo leader, ship, leaderboard. It's going to be clutch there. And then what else? Yeah. No, this is solid. If you need to get more out of Aaron on design. Feel free to, like, loop me into a call. Or you and him just have a call and talk through it. I think it's easier than just going back and forth over text. If you're like, screen share and be like, this could be improved. This could be improved. He always wants inspiration, so if you've seen any really good ones, just send it to him and be like, hey, you know, take inspiration from this. We like this element of this. So there's tons of different launch and hype videos. Look what Trade XYZ did. Osteom like all these comps. And just. Yeah, talk. Talk through it with them. If it's not giving you what what you want. And if you need any looped in. No, I. I know how to manage this better next time. Simran was like, hey, like we should do this teaser concept. And it was a bit of a last minute. Addition to the strategy next time. I already told Aaron I'd apologize. And I said, hey, I'll give you more lead time. Moving forward. Yeah. So we're good? I teased her for something as small as private. Alpha probably isn't necessary either. Right. Agreed. It's almost like unnecessary attention that we don't particularly want. I want to keep all of our ammo for the trading competition and the public testnet. Yep. Yeah. We'll see conversations with traders, like, all this legwork in the back end, like this is super important over the private Alpha period. Not 100%, so that's going to be my focus. And I've already had some guys up there excited about it, some trader buddies, so, like. You know, dudes like this. He's going to be in it next week. That's your big wick. Nick. It's also just spot. So it's like people like this are going to land on it and be like, where the are my perps? So we really need to, like, manage expectations with some of these guys and be like, hey, it's not done. We need you as, like, a design partner for purpose. We want you to test this out. What do you like? What don't you like? The front end experience and just. It needs to be framed to them. As not even. Like you're getting early access to something that's done. Like you're getting early access to help the team build. And you're going to be reminded of that. So just double down on that with these folks so they don't get, like, funded by kind of a nascent early version of it. I. I hear you. I hear you loud, claire. Yeah, I'll. I'll tread lightly. Cool. Yeah. Adi.

**Me:** Yeah.

**Other:** Give me a quick rundown and then we can jump.

**Me:** 100%. Yeah. Gave you an update on the rhinestone call. Finalized. Sort of like a blurb with Chathan on, like, what we'd start sending out to these folks. I'm roping together a couple more TG groups. Got, like, a couple replies back, so we should have, like, about, like, four or. Five calls booked for later this week and then started next week.

**Other:** Yeah.

**Me:** Apollo. I, like, created, like, a test account and then, like, started creating a sequential workflow for, like, outreach for, like, YC and smaller AI startups as a whole. Because I don't want to, like, pigeonhole ourselves to yc. But, yeah, that's about it. And then for next week, it's just. Like, it just calls on books. Just like my North Star right now that I'm chasing. And then just getting Chen on some of these quality calls. And then, yeah, I need to, like, wrap up my second review of, like, notes for Friday for, like, the killer apps review. Anything else that's, like, top of mind?

**Other:** Nice.

**Me:** Pivoting.

**Other:** No, that's good. Next. Yeah, Friday will be equity perps, and we'll go deep on killer apps.

**Me:** Okay?

**Other:** And then, yeah, the focus is really just supporting Chen with those initial calls as we, like, validate the cell.

**Me:** Yeah.

**Other:** Yeah, Feel free to pass things over to him earlier, too. Like, you can just inbound to somebody, say they come back to you, be like, hey, here's the CEO. He'd love to chat with you. And then you can hand it off, and it's like, on to the next.

**Me:** Okay?

**Other:** Too obviously, if you.

**Me:** I'll get a calendar link.

**Other:** And then I think he added you to a product doc today. He keeps kind of, like, refining the product more and more.

**Me:** Yeah.

**Other:** It's almost like a security play at this point, rather than a privacy.

**Me:** Yeah.

**Other:** So his pitch, his, like, blurb is in that pitch as well.

**Me:** Oh, okay.

**Other:** And so we'll just. Yeah, he added a blurb to that, so just feel free to sync with him. On how he like the elevator pitch or the high level of it. I also told him to, like, refine some of the questions we're asking these folks. But, yeah, just be sure you're staying on top of, like, how fluid that product is right now.

**Me:** 100%.

**Other:** It's really just like a security play for these major labs. And he thinks he can sell into, like, an OpenAI or anthropic, can get them as an early user.

**Me:** Sick. That'd be sick. Yeah. 100 OpenAI has its own TE team, right? Like, why would they need us?

**Other:** Feel free to ask. Like that's a perfect question to drop in project class.

**Me:** Yeah.

**Other:** Like, chat and see what Chet says.

**Me:** Okay?

**Other:** The, the short answer is like they have a TE team, but it's, that's what I mean, it's evolved beyond just like the pure te. It's like that managed services, end to end security of tes. So even if you have your T, it's kind of verifies. That it's accurate in a secure way. Again. It's, like, very nebulous and I don't have a full grasp of the product. That's why Paul and Faith and J and you are kind of like the AI guys that I'm trusting. But that's my understanding of it right now.

**Me:** I didn't click. What's like the differentiation again? Sorry. In your this thing.

**Other:** Just take a look through that product doc that Nathan sent over to us this morning. My thinking is it's like, end to end security and, like, provenance. So it, like, tells you that the model and, like, the different pieces of the te are not getting penetrated by the actors. It shows, like, historically where it's. Come from?

**Me:** I will. I'll take a look here. I'll take. From my understanding.

**Other:** Again. This is like a very remedial.

**Me:** Oh, do you have lots of like, you have logs of, like, what's happening within this. What TE is naturally produce logs, dude, I'm pretty sure, like, at least there are certain libraries that exist that would be like a trivial ad for like an internal developer. Like, if you're a member of technical staff at OpenAI. OpenAI. I, like, highly doubt you can't integrate a library or some shit. Let me ask him. I'll, like, dig deeper into this because I don't know if that's, like, a defensive claim, but, yeah.

**Other:** All right. Take a look at that product, Doc.

**Me:** Yeah.

**Other:** And feel free to, like, ask questions and, like, poke holes in it. Because he's still coming together, and he needs people.

**Me:** Yeah, yeah.

**Other:** Like hitting the door and seeing it. What gives him.

**Me:** Yeah. Y. Eah, okay. Cool, cool. Co. Ol?

**Other:** Cool. Is this something. If this is completely out there, I'm sorry, but, like, I've always, always thought about, like, this idea of, like, selling data. And, like, you just want the insights of the data, right? The advertisers don't want to actually touch the data or ever see the data. They just. Want to know that they're getting good data, right? So they can direct their advertising algorithms. Could we use Glass to allow for like me to upload all my private data to Glass? Advertisers can see and extract insights from it without ever seeing the data. But they get the proof from the te saying. Alec Shaw did in fact upload all this data. It was never with. And here's the output of the data, but they never actually see it, so you basically get the same advertising insights out of it. You pay the person who generated you the data, but the data never goes to the actual advertiser and you don't have to worry about data breaches.

**Me:** That would be more of like a raw, like, data play, I think, like, the re like, what these guys are trying to do and correct me if I'm wrong here, Cody. Right? But, like, it's like, basically fhe plus tee play where it's like, purely for compute standpoint, right? Type thing. They're not really focusing too much on, like, data privacy or security because, like, they'll get their lunch eaten, bro. Like, I think, right. If they do. Because, like, there's already existing tooling. Like, Cisco's been, like, cooking on tees for, like, 20 years, right? Damn near. So it's like they already. Have, like a ton of existing libraries where it's like, you're almost describing, like a ZK proof in a way. Right, but like through a TE in a way, like an attestation data. Yeah, 100%. I mean.

**Other:** Yeah. Yeah. It's possible. Like, down the line, an app could be built on top of glass to do just that. Realistically, like the first clients that it seems like Chen is trying to target now. Our model like labs, like the OpenAI's anthropics. Llama is like on and on perplexity from there. Also like agent builders. So anybody who basically like fine tunes on top of a model or an LLM. There's just going to be net new IP that happens there. And glass, in theory, protects like end to end, from research to training to deployment. Your IP on this is. That's again, like, I have. I understand 50% of, like, where the product's at right now, so take some of this with a grain of salt.

**Me:** For data related. I was just typing this in the chat, but like ZK Pass exists, which has zktls. They're the ones that pioneered it. They're basically like HTTP attestations. So like, honestly, like everything that you typically upload to Google Drive, you could basically do like through a zktls system. The other reason why you'd wouldn't want to trust a TEE with like super sensitive data or whatever like PII data is like. Cause you're actually still like, like all your information is still getting decrypted within the confidential compute environment, so you're actually putting trust into an external. Compute environment. With zk, you don't even have to do that type thing. You could just store it off in like a, like a database that you would custody yourself type thing, and you can just like, sort of.

**Other:** But what? But what is it? What are you trusting today? That. So instead of just trusting the hardware, I'm just trusting Facebook. I'm trusting anyone who's collecting my data in a centralized way, right? I'm just trusting that they're not going. It's infinitely better than that. Right? It's like I'll trust the TE instead of trusting Facebook. 's system.

**Me:** Yeah, yeah, no, no, that. Like, I'm not arguing with that, but, like, my argument is, like, I think zktls would probably be a more secure transmission system, or, like, even, like, storage system, for that matter, too. Like, even, like a database. Like, you know, Supabase. Even, like, something even as simple as a supabase. Like if you were to do like HTTP like get and pull requests from that, or sorry, get and like write requests from that, then like a ZKTL list system is not only lesser compute, but it's also a more trustworthy transmission process. What could actually be interesting, bro, now that I'm like thinking out loud here. Like ZK TLS plus like a TEE enforced database could actually be interesting which would actually be able to built on top of glass. Like essentially if you had like some form of like custom SQL command that you could write to. Like basically like a database that's like stored within his tee. I'D have to look into a the technical feasibility and also the cost of that because, like, storing data within a TE is probably immensely, immensely tough. Like, because RAM is super expensive.

**Other:** Yeah. The use case I'm driving toward is like. Like, I want to create a private data marketplace so advertisers can extract insights from the data without ever having to see it.

**Me:** Oh, you're seeing run like, sorry, dude, I, like, totally misunderstood what you're trying to say. You're not saying, let's store the data somewhere. You're saying, bro, we need to run on the data. I'm actually.

**Other:** No. Yeah. No. No one. No. The advertisers. The advertisers do not want the data.

**Me:** That's a perfect use case. I'm going dead. Yeah, yeah, yeah.

**Other:** So it's like, it's like the. The middleman software connects me with the device and the data collect being collected with the advertiser, but the advertiser just sees where my data moves the knobs. All they do is they see the output of and they can draw in for I'm. Using the wrong keywords. Apologies.

**Me:** Y. Eah. Y.

**Other:** But you know what I'm saying.

**Me:** Eah. Dude, like I thought we were trying to talk about was, like, the process of actually transmitting it, which, like, te is just too compute costly to do that, but, like, the process of actually, like, once it's been stored somewhere, securely running inference on that glass is perfect for that. That's actually like.

**Other:** No, I'm just thinking of the narrative of, like. Personally identifiable. Like you don't like. Like, let's say goodbye to data breaches because the advertiser is never going to have your data to begin with. The middleman is no longer going to have raw data. The middleman is only going to have insights, saying like I. And I don't even know if it's fully possible. I just like, the narrative is hot. People talk about it all the time in Web two.

**Me:** I get it. I get it. Yeah, I'll do some thinking on it, bro. Yeah, but, like, I like, the data breaches will happen regardless of whether you're using, like, confidential compute environment, right? Because, like, let's assume, like, I have, like, my phone, which is where I store all my data, and, like, I have this advertiser that's. Like, trying to, like, pull all this data, like, somehow type thing. I'm like. I'm basically, like, sort of like the TEE environment there, where, like, I'm just, like, connecting both of these guys, right? But, like, you could still, like, go directly to the data and, like, data breaches happen all the time you could fuck, like, the data up, like, you know, whenever, if you're, like, a really powerful sort of thing or whatever. Like the actual security is actually happening within the transmission in your argument, which is like using a tee, but for that ZKTLS is better theoretically.

**Other:** Okay. Interesting. I'll have more questions about that, but.

**Me:** Yeah.

**Other:** Just for my own personal.

**Me:** 100%? Yeah, 100%.

**Other:** Curiosity. All right.

**Me:** Dude. Right.

**Other:** Cool guys.

**Me:** Off. Yeah, we should definitely make this in 45 minute thing. I think moving forward.

**Other:** Cool. Yeah, I'll make this one 45. And then we can always just carve out some time Fridays if we have follow ups, because there's no reason to wait systematically, like weekly.

**Me:** Yes. Yeah, yeah, yeah. 100%.

**Other:** Yeah. No. Excited to, like, dig in. I think we all have different, like, lenses into this, so just talking through some of these.

**Me:** Cool.

**Other:** Maybe they're not our domains. Maybe they are, and we'll just obviously learn and put our brains together here.

**Me:** Yeah. Easy.

**Other:** Guys. Good stuff. Talk later. Peace.
