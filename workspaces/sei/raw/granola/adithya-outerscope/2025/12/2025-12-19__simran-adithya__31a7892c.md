---
source: granola
workspace: sei
ingested_at: '2026-05-07T04:23:57.244510Z'
ingest_version: 1
content_hash: blake3:b0035b711add0de5a10ae79a1baad0c89c9f57f32e864f6137fc70ec81771287
provider_modified_at: '2025-12-19T22:30:50.163Z'
account: adithya@outerscope.xyz
account_slug: adithya-outerscope
document_id: 31a7892c-3e9b-47a9-aaf6-17093776bfa4
document_id_short: 31a7892c
title: Simran <> Adithya
created_at: '2025-12-19T22:00:34.526Z'
updated_at: '2025-12-19T22:30:50.163Z'
folders:
- id: 3ca3cb55-d6e1-49ef-961a-8ba2469731a5
  title: SEI
creator:
  name: Adithya
  email: adithya@outerscope.xyz
attendees:
- name: null
  email: simran@0xmonaco.com
calendar_event:
  title: Simran <> Adithya
  start: '2025-12-19T16:00:00-06:00'
  end: '2025-12-19T16:30:00-06:00'
  url: https://www.google.com/calendar/event?eid=NTE5YjljNmEyZDUxNDEyMjhkOGQ5YzUwZTZiNTQ5ZjQgYWRpdGh5YUBzZWluZXR3b3JrLmlv
  conferencing_url: https://meet.google.com/tjg-uaub-rvi
  conferencing_type: Google Meet
transcript_segment_count: 322
duration_ms: 1761600
valid_meeting: true
was_trashed: null
routed_by:
- workspace: sei
  rule: folder:SEI
---

# Simran <> Adithya

> 2025-12-19T22:00:34.526Z · duration 29m 21s · 2 attendees

## Attendees

- **Adithya** (creator) <adithya@outerscope.xyz>
- <simran@0xmonaco.com>

## Calendar Event

- Title: Simran <> Adithya
- Start: 2025-12-19T16:00:00-06:00
- End: 2025-12-19T16:30:00-06:00
- URL: https://www.google.com/calendar/event?eid=NTE5YjljNmEyZDUxNDEyMjhkOGQ5YzUwZTZiNTQ5ZjQgYWRpdGh5YUBzZWluZXR3b3JrLmlv
- Conferencing: Google Meet https://meet.google.com/tjg-uaub-rvi

## AI Notes

### Background & Career Journey

- Simran: Born India, moved to US at 3.5, raised Pennsylvania
- Penn State (math/finance) → Goldman straight from undergrad
- Goldman trajectory:

    - Started risk management (1 year)
    - Oil options trading when oil went negative (trial by fire)
    - London stint, then moved to crypto via GSR (Feb 2022)
- GSR roles progression:

    - Product development → Sales → Alpha Group portfolio manager → DeFi trading head
    - Helped incubate Katana while running DeFi trading
- Age 29, no wife/kids → took asymmetric risk joining Monaco 1.5 months ago

### Monaco Technical Architecture & Performance

- Rebuilt architecture from ground up over past 1.5 months
- Current latency: Single digit milliseconds (sub-10ms)
- Target: Sub-millisecond for public testnet
- Not targeting retail traders but HFT firms (Tower, Hudson vs GSR/Wintermute)
- Central limit order book/liquidity engine (not DEX aggregator)
- Revenue model: Trading fees + transaction costs, giving front-end rebates

### Product Vision & Strategy

- Core thesis: Abstract away blockchain complexity like Apple Pay abstracts payment tech
- Multi-asset trading in single account:

    - 5x leveraged NVIDIA trades
    - Prediction markets on earnings
    - Cross-chain deposits via intents abstraction
- Tokenized assets as collateral for perpetual trading
- Bridge TradFi and DeFi without “versus” mentality
- Target: $100M monthly revenue from trading fees

### Go-to-Market Approach

- Multi-front-end strategy:

    - Mobile-first (Robinhood-style button traders)
    - Desktop trading UI (HyperLiquid-style with LLM integration)
    - Institutional custody integration (Fireblocks, Copper, Anchorage API)
- B2B partnerships:

    - Meeting with Fidelity crypto operations head next week
    - Target Interactive Brokers, Charles Schwab routing
- Trader referral codes system:

    - 30% of referred user’s trading fees
    - 15% from second-level referrals
    - 5% from third-level referrals
- Fundraising: $10-12M at $100-120M valuation

### Competitive Differentiation & Retention

- Post-airdrop volume sustainability strategy
- Dynamic fee tiers tied to tenure/volume for top referrers
- Trading community cabal targeting
- Geographic front-end specialization (Korean, Indian, Nigerian markets)
- TikTok advertising + organic community growth

---

Chat with meeting transcript: [https://notes.granola.ai/t/418cfe30-2c78-4fdb-945d-67f9f4ed3f50](https://notes.granola.ai/t/418cfe30-2c78-4fdb-945d-67f9f4ed3f50)

## Transcript

**Me:** Hey, Simran, how's it going?

**Other:** How are you?

**Me:** Doing well. Doing well. Where are you calling in from?

**Other:** I'm in new york. Are you in the world?

**Me:** The office by Chancellor.

**Other:** I'm about two minutes away from the office. I was just running an errand, but I'm walking back there.

**Me:** Nice, nice, nice. No super cool stuff. No, I'm calling in from Austin today, but I'll be at New York in the office in about two months. Actually, typically based in LA and SF right now.

**Other:** Nice. Okay, Cody said you'll be joining on the incubation side, mostly focusing on AI front, correct?

**Me:** Exactly. Exactly. Yeah, that's right. So I'm like 90% glass, 10% Monaco right now. Sally asked me to play.

**Other:** Yes. Let's see what we can do to strip that 90. I'm kidding. No.

**Me:** Yes, indeed. I'm excited to chat. Actually, a ton of ideas for you all as well, but no, 100%. No, I heard. Dude. So you came from gsr, dude. So you must know Alex and all the guys there, right?

**Other:** Alec pop? Or is there another alex?

**Me:** Alex. Yeah. Alex. Taf. Yeah. Head bd us, I think. Right. Right now.

**Other:** Yeah, him and I joined vsr the same day, actually.

**Me:** Nice.

**Other:** February 22, 2022 yeah, yeah.

**Me:** Wow, that's sick, actually. Nice. Man in 2022. Damn. So you guys were there a while, man? Actually, I met him in, I think, like, 24 March or something, actually. But, yeah, super.

**Other:** Yeah. So he so he was coming from Im coming from Goldman. I just moved over from the oil options. That's there.

**Me:** Nice. Okay?

**Other:** And then, yeah, he was just a sales guy that I didn't see. Brought him all the version. Yeah, we happened to be reporting to the same guy doing literally the same day, so it was quite a. Quite a coincidence.

**Me:** Killer. Killer. Nice. Nice. You were ahead of trading there, right? I think is what Cody was mentioning.

**Other:** Yeah. Defi trading at psr. Yeah.

**Me:** Nice man. Super killer. Give me that. Alpha, please. I can eat my bags up. Joking.

**Other:** If you buy low and you sell high, you make a money 100% of the time. That's a free office trader.

**Me:** There it is. Here's the strategy.

**Other:** No. But what people for, what people forget is you can also sell high and buy low.

**Me:** There it is. Yes, indeed. Yes, indeed.

**Other:** But yeah. What have you been doing in the space with? Let's learn a little bit more about you. I can go.

**Me:** Quick rundown 2 minute and then would love to learn more about you. Your personal background too 100% but I think you're on me like 2 minute summary. Grew up in the Bay then moved to Austin before Elon made it. Cool. Went back to the bay for school and then studying eeks in business out in Berkeley. During my time in Berkeley, I was running the blockchain accelerator there. Blockchain at Berkeley accelerator and then consulted for PayPal, crypto and deepinity. But I always thought my path was like, oh, Google, Facebook. One of these companies ended up as SpaceX. As a software engineer for about a year before hopping back into crypto. An EVML2 was there for six to seven months as their head of growth and product because I wanted a bit more like sales side experience rather than just super technical side. Because I realized, dude, honestly, after talking to many of my mentors, all of them wanted sales experience first, right? I think people science matters a lot more than actual science these days. Which kind of sucks to say, honestly, but like, you know, coming from a tech and go background, but, you know, I think that's the truth. And so founder to go to market shop after that, where I was focusing on product ecosystem at a couple companies. On contract was a pretty lucrative gig and then left that. Found my own thing, actually this summer. Raised like a 3 mil round for that almost until my. The house fund for my alma mater. Actually, like the Berkeley house fund, unfortunately ended up pulling out as our lead. So Ray's ended up. I mean, we could have honestly. Pursued it a bit more, but just wanted to spend a bit more time in like a larger ecosystem where like a VC type thing before I got back into like the raise and honestly, you know, I was thinking about it being like just a couple month gig, but after, like learning about this gig and you know, you know, from. Cody. And, like, through the interview process, I'm thinking of sticking it out, you know, like, for a couple years. Cause I think this gig that I have right now is honestly, basically unicorn school, man. Right. It's after school in a way, working under the team that we have right now. It's just extremely, extremely killer. And so super excited to be joining on here. And I think it's kind of a generalist role, like kind of all in one and learning a ton already type thing. So excited to be here, but that's about it. Quick intro.

**Other:** No. I love the entrepreneurial drive. I love the recognition of the fact that EQ is probably mattering more and more.

**Me:** Yeah. Yeah.

**Other:** Compared to iq.

**Me:** Absolutely. Absolutely.

**Other:** At least, at least in today's day and age, because a lot of those skills have become commoditized. And so you have to.

**Me:** This is a commodity, man. Well said. Right. Like anyone can use GPT and get smart in, like, five minutes. Right? So now it's about agency and who you know, right? In a way, I think.

**Other:** I'm, like, coming from Goldman, like, one of the first things that my boss told me, he's like, it's a relationship business.

**Me:** Yes.

**Other:** Right. You could be the best trader out there, but you can't. You can't replace having relationship with the right places.

**Me:** Yeah.

**Other:** Right. And what's the old adage? Your network is your net worth, I believe.

**Me:** Yeah. Exactly right. Exactly. Literally. I'm seeing it more and more in my career, honestly being true 100%.

**Other:** Yeah, yeah. And so. Yeah, no. So what can I tell you about Monaco that you don't already know? What can I tell you about myself? How can I best help get you up to speed? I guess.

**Me:** Yeah, no, I've read up a bit on Monaco, man. I just love to learn more about you, your personal background, you know, were you born and raised in the States or where were you. Where were you based?

**Other:** So. Born in India, came over to the States when I was super young.

**Me:** Nice, nice.

**Other:** Yeah. So when it's about three and a half. Moved over from Delhi. Most of my life in Pennsylvania. I went to Penn State studying math and finance.

**Me:** N. Ice.

**Other:** Started at Goldman straight out of undergrad.

**Me:** N. Ice.

**Other:** Initially did, like, a year of, like, risk management. I'm like, this is more about risk reporting rather than risk management. A friend of mine's like, oh, why didn't you talk to the commodities guys?

**Me:** Jiller.

**Other:** And that. That used to be the Wild west of asset class. Es. And so I joined the oil up to that year after starting at Goldman, and then shortly later, oil went negative.

**Me:** Right. Yeah.

**Other:** So when once, when one of those like, never happened in the history of mankind kind of events happened, it really is a trial by fire.

**Me:** Yeah.

**Other:** For lack of a better word. And so, yeah, did that for a few years. How did Blast spend some time in London for Goldman as well?

**Me:** Nice.

**Other:** Learned a lot. And then at some point, we begin to ask yourself, like, hey, is this the best risk reward? What is my forward perk look like? Like, I knew very early on, even when I was an intern. I'm like, being a Goldman lifer doesn't seem like my. My cup of tea, I think. Like, I just don't have the desire to be political or, like, play in those kind of games. I'd rather play in games that are a bit more democratized, and then it truly is a bit more meritocratic.

**Me:** Yeah, 100%. 100%.

**Other:** And so my first boss also told me, everything is an option as long as you know how to trade it. And so crypto felt like a great option. I dabbled back in 2017, made enough money to help pay for my brother's wedding.

**Me:** Nice.

**Other:** And that nothing happened, really, until 2020.

**Me:** Indian man, which are very expensive here, and so. That's a good point.

**Other:** That is. That is very true. Thankfully, the wedding was in India, so there was that. I got a little bit of an effects carry trade there, but besides that, I dabbled in DeFi in 2020, obviously, DeFi Summer happened. Made my own, like, little tip token, sent it to Vitalik's wallet.

**Me:** Okay? Good. Good. Good. Okay. Great. Nice.

**Other:** And yeah, it was just getting fun. And then 2022 made the full time jump to GSR. And so originally I joined on the product in different development team because trading is trading no matter what after clouds you're doing, but actually learning about the tech under the hood and being like hey, what is it that's actually being built here. What is the central creation? Why do people give a shit about this?

**Me:** Nice. Great. Yeah.

**Other:** With kind of the name of the game. So product and beauty was a perfect way to kind of look at the sports more broadly.

**Me:** Nice.

**Other:** Then they said hey, you've worked with clients before, why don't you run everything? Feeling for two small sales I would tell you association of failed which was really just explaining to bitcoin miners why they should hedge explaining some token treasuries how they can get yield of how they can risk manage. Did that for about 9ish months. And then they're just like, the firm went through a reorg. They're like, hey, we have a trading group called the Alpha Group that we're forming. We need someone with market acumen to actually run this. And so then I became a portfolio manager in the Aqua Group. So the name of the game was very much. Hey, here's some balance fee. Go make some more money.

**Me:** Yeah. Right.

**Other:** And yeah, did that. Made a few million. The firm had another reorg and they're just like, okay, we need you to run Defi Trading. You have enough experience on the trading side, but we need someone who's a little bit more interested in defi side. And yeah, was running Defi Trading for a few months and came across Kitana, or rather Katana came across me and then helped incubate Katana.

**Me:** Oh.

**Other:** Along with. Along with.

**Me:** Wow. Sick.

**Other:** My primary focus for most of my time when I was running DFI Trading, which is helping each of China and a lot of the projects that we're building on, on top of them.

**Me:** That is. Nice.

**Other:** And then. Sorry. Yep.

**Me:** Killer. And what made you hop to Monaco? I guess, like, was that, like, the next thing for you? Naturally.

**Other:** Yeah. So Monica had originally reached out initially to GSR to be an integration partner and provide liquidity as a market maker, and then had the guys over at say reach out to me and said, hey, we actually had the engineering resources to build something pretty amazing. We just need someone at the helm who can quarterback this and understands the scope, the nature and the landscape of the problem that we're trying to solve. And for me, I'm like, I'm 29. I don't have a wife and kid to worry about. If there ever a time to take asymmetric risk because this is an option, you might as well. Do it now. So I moved back from London, came back to New York about a month and a half ago, settled into Lori's side and been on the desks ever since then, and, yeah.

**Me:** Yeah. Absolutely. Nice. Were you at. Were you at an les, man? Out of curiosity?

**Other:** One Manhattan Square in the east side.

**Me:** Oh, okay, okay, okay. Got it, got it. Do you know where Mr. Purple is?

**Other:** Yes, of course I know. Mr. Yes.

**Me:** Two doors down from Mr. Purple for, like, three months this summer, actually.

**Other:** Oh, wow.

**Me:** That's crazy nice. Practically neighbors, man. No. Super killer stuff, dude. That's like, very, very like, dude, you're 29. That's crazy. Holy shit. That's insane. That is actually insane. I expect you to be a full blown uncle, bro. That is insane. Man crazy.

**Other:** I mean, I hope I'm not giving UNC energy, but I guess you'll have to make that.

**Me:** Not. At all. Bro, your career is going to be. Good thing, man. That's a good thing, bro. That's crazy. Holy shit.

**Other:** I appreciate it, but. Yeah, no, I'm looking forward to this, being heads down building something pretty incredible.

**Me:** Very nice.

**Other:** We've got a lot of partnerships already in place or happening in progress. The past month and a half has really been spent gutting the old architecture and making sure that we're aligned on the new architecture with the eco engine.

**Me:** Nice. Right. You guys? Latency, right? Actually, with the new architecture. So Cody was saying, as opposed to 130 or 160, which was posted online.

**Other:** Yeah, it's like single digit. Millis is what we're at now. I'm hoping to go sub in a second. Over the next few months when we hit public testnet. But, like, that's more fine tuning and optimization. I wanted to get under 10 milliseconds just to get us through the door. Right, because retail doesn't give a shit.

**Me:** Yeah.

**Other:** But.

**Me:** Absolutely do. Yeah. Like, I'll make know in milliseconds. Absolutely. 100%.

**Other:** Retail doesn't give a shit, but HFT does. And if my target audience is not, dare I say, you know, GSR or Windermere, but it's Tower and Hudson, that I need to be much more performant.

**Me:** Right.

**Other:** Right.

**Me:** Right? Absolutely. No, that's super killer, dude. And actually one thought I had on that note, right. Actually, now that you mentioned HFT as well, right. It's like a lot of alpha and like proprietary algos are just that they're alpha and they need to be protected. Right. Type thing, you know, folks want to deploy. Inference models and whatnot on any alpha or any sort of, like, training. I honestly thought there might be a pretty cool synergy between glass and Monaco there. This is a couple months out, obviously, Ray, type thing where it's like, if you want private sort of like not dark pool necessarily, but like privatized sort of inference based training. Then, like, you know, there could be potential POC deployment that we could build out in like, two to three months for. That was my thought there. But you guys have already done a killer job with the go to market, man. The product, everything is like, you know, super flush, and honestly, it's just. A flywheel right now. Very type thing. And Cody mentioned that you guys were trying to raise somewhere between, like, 10 to 12, right? At, like, 100 to 120. Val, if I'm not mistaken,

**Other:** Yeah. I mean, I think we're still there's still a long way to go. I think within the, say, echo chamber, there's obviously momentum, but the goal is to amplify that. I've been more focused on just the product side initially, just because it needed a lot of blood. Now it's more about go to market, getting the momentum, building a brand, building a track record, being at the right places with the right people at the right conferences. And so I'll be going to eat Denver. I'm trying to get a bcc, trying to either stick on panels or, or give keynotes.

**Me:** Nice. Cool. Nice. Absolutely.

**Other:** Yeah. And the goal is really just like, this should be a no brainer that this is a product that needs to be built. Because for, for me, the original promise of crypto, the 0 to 1, was very much like, hey, we no longer need a trusted central intermediary to store and own our own value, right? But then a bunch of people created a thousand different versions of the same thing, and it's, it's like, well, well, what the hell am I supposed to do now? And so the 1 to 2 is, how do I abstract away all of that nonsense to be able to use that value in the most scalable way, not just sort it. Right. And the best example I can give is how many people who pay for their overpriced Starbucks with Apple pay no actually know how it works. I would argue less than 30%, 20%. Realistically, right.

**Me:** Yeah. All right. Where is that?

**Other:** Probably Even less than 10% of people actually understand how the underlying tech works. But they don't need to, because it's part of their app, it's part of their iPhone, it's the new ubiquitous technology, and all of that is abstracted away. And so, until I can trade Nvidia 5x Leopard perks and the same account that I can bet on using prediction markets the earnings for like earnings beat or miss on a prediction market like all of that should be able to happen in a seamless way and I should never even have to think about what chain I am an abstract all of that away.

**Me:** Right. Exactly. Exact. Ly. Bro. Exactly, bro. Like it's always product versus thinking right type thing that should really occur. And that's honestly why I joined this over like other offers is like, dude, like J and like Cody are extremely product for his thinkers, right? Like I've gotten screwed by technical autist founders in the past, right? That like, literally do not go about, go to market and just give a about building features that no one wants. Right? And, like, just because it's cool to build and it's like, dude, like, that's really just not how it works. It's always customer focus, like discovery. Right. And, like, features should always be informed with customer conversations. Right. Type thing. So not super refreshing. You say that too. Honestly.

**Other:** I have zero appetite for just intellectual masturbation for the sake of intellectual masturbation.

**Me:** Yes, exactly.

**Other:** And it's like one of those things where.

**Me:** I'm gonna use that, bro. I'm gonna use that from now on. Intellectual masturbation. That's hilarious.

**Other:** No, but that's what it becomes, right? Realistically, like, people like to do hyper convoluted things because they feel like that makes them feel smarter, but.

**Me:** That's the word all day, man. That's.

**Other:** But. But if we're being intellectually honest, the truest measure of intelligence is being able to get what you want. And the truest measure of wisdom is in wanting the right things.

**Me:** Yeah. Yes. Absolutely, yeah.

**Other:** Right. And like, that's it.

**Me:** Yeah, dude. Well said, man. Actually, very well said. Not super killer, dude. And people get that wrong all the time, man. It's just like, dude, convoluted fucking Dex buzzwords thrown on fucking decks for the sake of, like, vanity metrics for a raise. It's like, dude, come on, man. Like, look, I. Get. You gotta play the game somewhat, right? For sure, like, no one's not playing the game in this industry and that it's successful, right? But, like, for the sake, like, expending valuable, like, resources to build fucking features that are completely irrelevant to the core product and, like, the core offering is just extremely stupid. It's a core sign of like, fucking, like, dude, ADHD to a peak. Right? Type thing. It's just, oh, let me fucking focus on it. It just doesn't make sense, right? Type thing. And that's why I think engineers that are really focused on sort of like product first thinking or like the most powerful people, man, honestly ever type thing. So that's super killer to hear you say that too, man. And your thought there is very interesting. Actually, I kind of had a similar thought I shared with Cody, man, where it's like, dude, imagine you have a structured product that you can sell users where it's like, okay, you can literally hedge your long position on the quality of an earnings report type thing or do prediction. That's the example that you stated. But at least other examples include like, okay, dude, you can just do things in between prediction markets and sort of like tradfi markets, right? Like an Osteo play. Type thing and what's super cool. And actually I learned this after coming on board, right? Is like Monaco is a Dex aggregator. And honestly, an L2 right. Type thing on say, which is like super, super sick, right? To know. Because that means that we can get a lot of these front facing, like, sort of like apps. That I've already achieved virality to come on board as really power out, go to market cycle and like a very viable way. Right. Hopefully. And like, if we can, yeah.

**Other:** I appreciate it. I don't know if I would call it a Dex aggregator. Like, not to be pedantic about, like, verbiage. I more just call this more Call it a liquidity engine or central limit order book. Right. Like, we can have multiple dexes build on top of us.

**Me:** Fair. Fair. Yeah. Yeah.

**Other:** But, like, I wouldn't call it because I feel like when people hear the word aggregator, like, if the wrong person hears that, namely vc, well, they're going to be like, well, how are you monetizing?

**Me:** Yeah. Right.

**Other:** And the way we're monetizing is directly through trade, like trading fees and transaction costs. Not necessarily. Like, hey, like, you give me a rebate if I use you in my routing, right? It's actually the other way around. We're giving front ends rebates from the trading fees that we're accumulating because people are tapping into our liquidity.

**Me:** Yeah. Yeah. Y. Eah. Yeah. Right. Right, right, exactly. 100%. No, no, absolutely. Dude, have you heard of layer? And by any chance, dude, out of curiosity.

**Other:** I've heard of Larry Zero, but I've never been there. And.

**Me:** That was the evml too, I was talking about, man. We actually had, like, a lot of theses back in the day, right? The thesis was like, okay, you want app chain level performance, but, like, with the composability of a monolithic architecture, right? Because there was no interoperability. Like, you had horizontally scaling. Compute for a lot of app chains already at that time, but there's no interoperability between app chains. Right. So if you really wanted this, like, and that's essentially what Monaco is actually becoming here. Right. Quickly it's like, dude, you want sort of. Obviously, we didn't have the specs that we're promising right now at later end but like that's no, that's super killer I think like what. How do you. How are you viewing the go to market motion maybe and like what's like your North Star metric over the coming quarter, do you think for that?

**Other:** Okay?

**Me:** Curiosity.

**Other:** I mean, my ultimate metric is very simple. I want to build a business that makes $100 million a month.

**Me:** Fire. Hell. Damn. Yeah.

**Other:** Third, how do we get that? We get that from trading fees. Where does the trading team comes from? It comes from retail. YouTube. Right. Because makers will get rebates.

**Me:** Yeah.

**Other:** Why should those traders come to Monaco of all places?

**Me:** Yeah.

**Other:** Well, because we're taking a multi front end approach.

**Me:** Yes.

**Other:** We don't have to cater to every type of creator in one front end, right? Different front ends are incentivized to play different games, and they should all feel like they're competing with each other in order to provide the best experience. So we have a team that's building more of a mobile first approach, which is just like, hey, the same click traders or the same button pressers. That trade on Robinhood on their phones.

**Me:** Right. Right.

**Other:** Or. Or dare I say, interactive broker should be able to come in and. And access Monica liquidity.

**Me:** Right.

**Other:** Then you've got the cohort of guys who like trading on their laptops on hyperliquid. With the SEC and training ui, we have something that's very analogous. It's going to be even, like, more performant because we'll incorporate LLMs.

**Me:** Right.

**Other:** And other elements that come on top. And yes, we can explore, like synergies with class AI, obviously as well.

**Me:** Right.

**Other:** Right? Then you've got your institutional style approaches, not partnerships, but approaches. And what I mean by that is think about the number of people who don't actually either trust defi or no defi. Right? That is orders that magnitude bigger than people who do. Know, I never want to see the word defi when when pitching. And the reason is because there's. It's not DeFi versus C file, right?

**Me:** Right. Right.

**Other:** They're all the same. Like, we should be focused on how to bridge those worlds, not treating it as an us versus them. And so think about the people that trade on centralized exchanges and have custodians, but never trust defi. I want to be able to give those people the ability to create a Monaco. Because those assets that they would post as collateral on perposition can stay in a firebox, they can stay in a copper, they can stay in Anchorage. And the only time we would ever need to touch the liquidity or the underlying capital is if they're being liquidated. Right. Which is. Which is just a simple. API call. This is beneficial for those traders because it gives them another venue to trade on. It's beneficial to Fireblocks because or any of these custodians because it's a product offering that they can pitch to high net worth and institutions stock clients. And it is an actual rev share because if they're building a front end that's attaching onto our liquidity. We're going to give them pit pass revenue, which is just a key rebate, effectively. Right. And it's beneficial for us because then we get another cloud base.

**Me:** Right. Right. Exactly. Right.

**Other:** Like. Like Robinhood has already shown that they're willing to double down on the likes of Lighter. Why can't I have interactive brokers or Fidelity or Charles Schwab be. Be routing flow my way? Right. And I'm actually hopping on the phone with the guy who runs crypto operations for Fidelity. Next week because he. He was. He's exgi. Asar.

**Me:** Facts. That's fire, dude. Holy.

**Other:** Right. And so that's not to say that, like, they're going to be on us in the next year. I don't even know what their crypto roadmap looks like. But my point is, like, it's one of those things where, like. Like, my goal is not to build a crypto. Product. My goal is to build something that is much bigger than that, right? It should be something that I would use. It should be something the same people that use Interactive Brokers should use. It should be the same thing that people use Robinhood should use, right? Like why? Why limit yourself to that? I'll give a very glaring example. One of the biggest challenges with tokenized equities is that you can't do anything with them, right? What is the incremental benefit of being holding tokenizing video on versus dare I say, holding it in my interactive brokerage account and then being able to lend it out and collect, collect. From those who are borrowing to short.

**Me:** Right. Yeah. Yeah. Yeah. Great. Great.

**Other:** Right? But now. But now, if I can post tokenized equities as collateral on the perfdex, now I can put on funding trades. Now I can do capital efficiency. Now I can play all these different games that I never could afford. Now you've actually given people something useful to do with their fucking. Assets that are sitting there, right? They're not just wasting a lot.

**Me:** Yeah, exactly, dude. Exactly. 100%, man. 100 and yeah, dude. Yeah. Very well fucking said, man. None of this is on paper, bro. Fuck. Okay, I'm going to create a document that summarizes all this shit, man. This is very sick, actually. Okay, so what are maybe some of the other things that aren't? Publicly facing on the website or things that would be extremely valuable to know about your entire motion over the next quarter, I guess. Are there any standout features or anything that are internal that would be valuable to know about, I guess, as incubations?

**Other:** Of the. I mean, just outside of latency and throughput, outside of the fact that we'll have tokenized assets RWAs, outside of the fact that I'm willing to let prediction markets be posted as collateral, outside of the fact that we'll probably have multi chain deposits because we'll abstract that away using intents.

**Me:** Yeah.

**Other:** Right. You should be able to use a cross rely for any of these things to access Monaco. You never even have to think about the fact that, like, you're on site. Right. All of that gets abstracted away. We'll, we'll cover gaps for any like, for when we publish the proofs and do back settlements. Like. Like. Yeah, that's kind of it. Like, it doesn't have to be. It doesn't have to be complicated. Like, I prefer. Keep it simple, stupid. Like, all. All, like, people have tried to do all of these little things in isolation. I'm just bringing those test pieces together.

**Me:** Right. Yeah. Just aggregating them. Yeah, 100%, dude. No, absolutely, man. Very sick. Very sick. And how does this compare to maybe other HFT clubs that exist today that could potentially it's the most in go to market motion, I guess, in a way.

**Other:** I think a lot of differentiation can be in gotomerc, but I think it's more about. One what you do to keep people in your ecosystem after the original incentive try up. Right. So people are farming lighter. Because obviously airdrop hasn't happened. I'm very curious to see what volumes persist post airdrop. But, like, one of the things that we're doing, for example, is trader codes. I don't know if you've read into it or if Cody has gone into it.

**Me:** Yeah. No, not yet.

**Other:** So trader. Trader codes is very much. It's out of the axiom playbook. Right. So if I refer you, I get 30% of your net trading fees.

**Me:** Sure? Yeah.

**Other:** But. But then if you refer someone else, I get 15% of theirs, and if they refer someone else, I still get 5% of theirs. Right. And because. Because that's still less than 1. The math works out. There's a wazi, it's a wuzzy, it's very. It's like. It very much is synergistic. Right? So not only am I incentivized to trade because like, obviously, like I can get rebates if I make a rebates and all these things, but I can also tap into other people who I think are pro level traders to be able to incentivize.

**Me:** Right. Yeah. Absolutely. Absolutely. Nice, dude. And, yeah, these trading communities probably typically stick together, so that's probably very killer. Go to market there, too. Very nice.

**Other:** Yeah, there's. There's trading cabal. After trading cabal, like, there will be farmers. I want people to come and inform this. But, like, the goal is use that as part of gaining critical mass and critical momentum. Right. Like you launch ads on Tik Tok, you start having people that are building front ends. For Korean markets or Indian. Indian markets or they say Nigerian markets. Right? Like. Like these are like. That's how we differentiate ourselves.

**Me:** Yeah. Great. 100% dude. And is your primary focus in D to C or like B to B? I guess initially. It would be like B to B to, I guess, higher or, sorry, bring on sort of like the initial front ends, right? Type thing. And then after that, you'd focus on the D to C motion.

**Other:** I would say they're kind of a little bit in parallel.

**Me:** Okay?

**Other:** Because I would say B to B first, because, like, those businesses have some distribution already. They're just looking to tap into a unique product offering that like, provides a better UX and UI. And so yeah, I would argue B2B probably, but then must be the same. But like, there are discussions being had directly to for how to set up the B2C. But, yeah, I would say, yeah, B2B and then B2C.

**Me:** Yeah. Yeah. Nice. Okay. Make sound. And how is, like, how could I like. Or, you know, as, like, sort of. Or me and Cody, like, together, right? As incubations, like, best help support you guys, right? Like, in the coming quarter, seems like there's a lot of, like, go to market, like, work that needs to get done. What? Else could we, like, maybe start out, like, you know, just, like, sinking your teeth into.

**Other:** I think. I think Cody's already been incredibly helpful. Like I'm. I'm talking with Xander around Monaco design stuff. Next week, along with Cody, we're putting together a pitch deck just to start, you know, pre hedging into raise conversations while we approach public test set. I'm looking to hire someone who will own, like, the Monaco Twitter account and just see, like very aggressively focused on. On running that and maintain that. And like can balance both the posting with the like, like strong pedigree and blue blood. Of like, trad flag kind of stuff. So, yeah, I think it'll be. I think we've got the right pieces in place. We just have to execute. I like the execution is happening, but it just doesn't happen overnight. Right? Like you. Like there are things that we have done in parallel, but like you only have finite number of people to do it.

**Me:** No, absolutely, dude, absolutely. Very cool dude. And. And I guess, final question, right, like, with the traitor Claude, like, flywheel, it's right to avoid, like, post airdrop, like, drop off. Like, could we tie, like, maybe higher rev share or fee tiers almost to, like, tenure or share, like, you know, like, maybe, like, make your volume in a way. So top refers are kind of locked in by ongoing yield rather than like one time points in a way, I guess.

**Other:** Yeah, yeah, there's. There's a lot of levers.

**Me:** Got you.

**Other:** There's a lot of levers that we're going to play with.

**Me:** Got. Cha.

**Other:** Yeah. I think that part is easy to do. It's more just like right now, for example, Perp sudden can be built right. Like I'm. So I've written up kind of a conceptually what all the pieces should look like. But I still need engineering to go build them. But like, once, once I confirmed with them that, like, my ass is abundantly clear and they can just go and fucking do it. Then, then we start focusing a little bit more on the nuance of the points that everything else. But yes, I, I agree. It's not going to be a static thing, right, because it's very easy to to get farmers through the door. It's harder to have folks stay in the room once the incentives are not as apparent.

**Me:** Yeah. Retain. Them. Yeah, 100%, dude. Killer, man. Now, this has been super killer and honestly gives me a lot more breadth than insight into, like, you know, how you're viewing sort of like next coming months for Monica and just on the product itself, you know, type thing, a lot more information. So really appreciate the call. Let me know anything I can do or. Anything I can help spin up, you know, over the coming week or two. I know, like, Cody's kind of deployed me on glass. Sleek. But, like, honestly, dude, like, more than happy to help out because, you know, it sounds like there's a lot of cool work you guys are doing, too, so if there's. Anything I can help spin up immediately, you know, just definitely let me know. I'm always on Slack. 100%.

**Other:** No, I. I appreciate it. Let's definitely stay in touch when I catch up every. Every. Maybe like, two, three weeks or something. Just like to give each other updates as to what. What's going on. I'm sure you'll know the updates because you'll be on the Monaco. Sorry. On the say. All hands, which I guess I'm not allowed to join, technically because of, like, segregation of turf and state.

**Me:** Right. Yeah. Really, actually.

**Other:** Yeah, yeah. We don't join the audience.

**Me:** Entity or something.

**Other:** We're talking. There's Monica Research in its own entity. We have our own foundation as well.

**Me:** Man. Okay, I didn't know that. Interesting. Damn. I guess your voice on those calls. He's been doing a good job, honestly.

**Other:** Yeah. No, I. I fully trust him. Paul has also been a good advocate. I'm sure you've already talked to him. Right.

**Me:** Yeah, yeah.

**Other:** Yeah.

**Me:** We have, like, our one on one single Monday, but, yeah, absolutely.

**Other:** Yeah. Pg He's a sharp guy. Yeah, I. I really like the guy. Like he, he doesn't come from a trading background but like from a pure engineering Chelsea smart, contract level knowledge. He's. He's a gig at that in that regards there.

**Me:** Yeah. Yeah. Crazy. Architect. 100%. Killer, man.

**Other:** Cool, man. Well, let me. Let me. Let me know when you're. Let me know when you're in New York. Would love to catch up in person otherwise. Yeah, let's keep the momentum going. Say warm, stay safe during the fucking holidays, and let's knock shit out in this fucking new Year, man. There's. Too much to conquer.

**Me:** Yeah. Exactly. Yeah. Absolutely. Yes. Yes, indeed. Now very prone to join on and no Great to meet you, man. 100%.

**Other:** Yeah.

**Me:** Killer.

**Other:** But.

**Me:** Peace out, bro. See you. See you.
