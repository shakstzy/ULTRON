---
source: granola
workspace: outerscope
ingested_at: '2026-05-07T04:23:57.244510Z'
ingest_version: 1
content_hash: blake3:e39f9a42a46f9956c76d87dde910175b7aeb1e2585792724a0fdb782668d0f7e
provider_modified_at: '2026-03-03T13:47:41.728Z'
account: adithya@outerscope.xyz
account_slug: adithya-outerscope
document_id: 202f70f4-d332-4b6a-88b3-16f7d2a1e1b4
document_id_short: 202f70f4
title: Shopify crypto token buyback platform prototype scoping with potential partner
created_at: '2026-02-05T02:18:51.012Z'
updated_at: '2026-03-03T13:47:41.728Z'
folders:
- id: 53c78f6b-58f0-4ad3-aa3b-8a45802f67b5
  title: OUTERSCOPE
creator:
  name: Adithya
  email: adithya@outerscope.xyz
attendees: []
calendar_event: null
transcript_segment_count: 150
duration_ms: 1012480
valid_meeting: true
was_trashed: null
routed_by:
- workspace: outerscope
  rule: folder:OUTERSCOPE
---

# Shopify crypto token buyback platform prototype scoping with potential partner

> 2026-02-05T02:18:51.012Z · duration 16m 52s · 1 attendees

## Attendees

- **Adithya** (creator) <adithya@outerscope.xyz>

## AI Notes

### Platform Concept & Legal Structure

- Creator-backed meme coins with revenue sharing from e-commerce sales
- Non-permanent revenue promises to avoid security classification

    - 10% revenue buyback for 2 years with mandatory renewal gaps
    - Discrete pre-announced events with regulatory cooldowns
- $95k legal opinion from prominent firm to engage crypto task force

    - Series A expense, not viable for current stage

### Go-to-Market Strategy

- Bootstrap approach over raise-first strategy
- Confirmed creator: Azalea Banks (massive following, high engagement, $M+ e-commerce history)

    - Already committed, no effort required
- Additional Miami influencers (several million followers) lined up
- Prototype → case studies → fundraising sequence preferred over deck-first approach

### Technical Architecture Assessment

- Core challenge: Shopify integration for automatic fiat-to-token conversion
- Proposed stack:

    1. Creator OAuth connection to Shopify
    2. Webhook triggers on sales
    3. Fiat on-ramp (Moonpay/Ramp) for USD conversion
    4. Solana/Jupiter for token swaps
    5. Tokens sent to LP/burn addresses
- Platform phases:

    1. Automatic buyback solution
    2. Coin deployment (Pump Fun clone)
    3. Full storefront aggregation

### Partnership & Funding Opportunities

- Solana Foundation grant potential (existing connections)
- Trump administration/Don Jr. fund ties for policy support
- Shopify revenue-sharing partnership model (50% profit split on custom frontend)
- Institutional Coinbase account for fiat conversion

### Next Steps

- Adithya: Technical feasibility assessment this week

    - Shopify API integration scope
    - On-ramp provider limits and KYB requirements
    - Webhook latency and gas handling validation
- In-person meetup planned for Feb 11th in LA
- Follow-up on technical assessment later this week

---

Chat with meeting transcript: [https://notes.granola.ai/t/0f3fe368-5a8e-44bd-a60f-765f58222815](https://notes.granola.ai/t/0f3fe368-5a8e-44bd-a60f-765f58222815)

## Transcript

**Other:** Then we would try to structure this in such a way that it least looked like a security. While still maximizing the amount of value accruals to token holders. In like a defensible way. And so I think what this could look like is non permanent revenue promises. So maybe there's a promise of 10% of revenue as buyback and add to LP for two years, but then maybe there has to be a period of non renewal. So like two years of or even if it's 24 hours, you can't renew the revenue promise for that period of time so that it's not continuous and indefinite. And kind of that's just, like, the whole overall goal. So Darren already has lined up, like, one celebrity who would be interested in launching a store on our platform. It's Azalea Banks. I believe. I always confuse it with mix it up every time there's her. And then I have a couple Miami based influencers with several million followers who will also be down. And we talked to a really prominent law firm, and essentially they want, like, $95,000 to kind of gauge whether this can be done legally or not. And they will talk to the crypto task force for us. That sounds cool, but that's kind of more of like a Series A type purchase, in my opinion. I don't think that precede or certainly not like a friends and family type expense we can do. So I think that realistically we'll have to just raise first. That, or just kind of like, we could just totally bootstrap launch with one or two people, Just get some traction, like some level traction, even if it's only like a million dollars in trading volume. And that I think we could raise a crazy round. Know, do a little bit more effort on the legal front. But either way, I think we at the very least should put together some materials in, like, a deck. I just wanted to gauge Adithya, like, if you'd be super interested in working on this with some degree of commitment.

**Me:** Yeah. I mean, definitely sounds interesting. Man. I'm not 100%. So just to kind of clarify. There's two pads here. Like, one is raised first, or two is, like kind of bootstrap, like one to two creators to get traction.

**Other:** Yeah. Yeah. And look. I think what we're leaning towards at the moment, and this isn't for certain, but I think the feeling that Will and I have right now is that the better approach is just to build it and launch, get a prototype live.

**Me:** Approach.

**Other:** Something simple. Or the simplest version of a prototype. Bring on Azalea Banks. Bring on a couple other founders. And go to market, and I think that puts us in a much stronger position. To go in to raise with some of the contacts that Will has, that I have, because it's always more compelling from an investor standpoint. When there's any kind of traction. And trying to raise money to go out and get a legal memo. It's a little bit of a workaround, and we still end up without the traction, which is what any serious investor wants to see. But I also think that we will be able to raise capital for this very easily with one or two case studies. I don't think just one or two. And we've got like azaleas a little bit crazy. I've told Will, but she's got a pretty massive following, very high engagement. She's already, you know, done a few million dollars and passed E commerce sales for products and soaps. And she said yes, like, right away, she's in. There's no effort there. And so the key is to kind of build the architecture, build the platform in some kind of prototype format. And then prove it. And then I think from there, we could easily raise like a, you know, a million dollars plus. And now we've. Now we can go out and bring in the law firm, get the opinion, go to the crypto task force. Hire more devs, all of it. I just think that's always going to be the better approach. So, you know, we're looking for development partner that kind of knows this space in and out and would be interested in helping build the prototype and then taking it to market so we can get one or two of these case studies out there as quickly as possible.

**Me:** Now, that makes a ton of sense. Makes a ton of sense. And so the current status is like, you guys are sort of working towards the rail.

**Other:** Current status is I would say again, thinking about how we can get a prototype out to get a case study or two and then go out and raise so launch a prototype platform. Have Azealia come onto the platform, one other founder, and then go out and raise. Yes. We can put together a deck now, and I think that's great, but, you know, the deck is a narrative, and it's less compelling than saying, hey, we built this, we launched it. You can see it right here. You know, Azilia signed a contract. He's committed to putting, you know, 5% of all of her product sales into the token buyback. And we've generated X amount of trading volume in the first 24 hours, 48 hours, week, month. That's what will raise capital for this business.

**Me:** No, that makes, that makes a ton of sense. Right. And then so to avoid continuous revenue, promises were to kind of use maybe discrete pre announced events. Right. Would it cool down to non chain?

**Other:** Can you. Can you expand on what that means? I'm not familiar with discrete. Whatever the rest of the sentence was.

**Me:** Oh, yeah, just like, discreet, pronounced events with sort of cooldowns.

**Other:** Discrete pre announced events.

**Me:** Yeah. Yeah. So sort of instead of continuous revenue promises for creators. You just sort of have just more silo.

**Other:** Right.

**Me:** Pre announced events for distribution. Because I think.

**Other:** What do you mean by pre announced?

**Me:** There'd be, like, a regulatory concern, right? Where, like, okay, like, you'd want to document that to show, like, regulators clear breaks and know, like, expectations of, like, ongoing profits.

**Other:** Yeah, exactly. Exactly. Exactly. And so our platform would basically, like, showcase maybe a countdown of, like, okay, there's still, like, two years left of revenue sharing. And another cool example of this might be, like, let's say that some big charity organizer that is cool with crypto launches some type of, like, fundraiser meme coin. And they promised that they pledged, like, 24 hours of sales going into buybacks of a certain coin. And so it can be like really short term thing. Like, imagine if, like. You know, I guess I won't give an example, but I think things like that could be super cool. So from an engineering standpoint, I guess, like, the real question that we have to solve is, is it possible? To build out some kind of module. Within Shopify or some other e commerce platform that automatically deducts incoming sales and converts that into. Converts that fiat into a meme coin. That's essentially like the engineering task. And I think it's totally doable, but it might be a little bit of a headache. With, like, banking. So that's kind of something we would have to look into. But I know that the Trump administration is extremely friendly on this right now, and these are partnerships I think Darren and I could find.

**Me:** Nice.

**Other:** Absolutely, yeah. Yeah, we do. We have, we have ties to Donald Trump's Don Trump Jr. His fund, you know, a number of people within the White House on the policy side. So we've got the connectivity there. And I think to Will's comment, I think that is the build is some kind of integration into Shopify. Or public square where some portion of revenue on every product sale. Is automatically going into this token. To support price. And it's, you know, basically, once a creator, entrepreneur signs an agreement with us, You know, they're committing to that percent for at least a year. And so that's. That's kind of what we need. And I was thinking a long term vision for this could look like us coming into some type of an agreement with Shopify or Public Square, where we say, hey, look, we're going to build our own front end for the store and we want to take like 50% of the profits that you would have made as the merchant provider when sales come through our front end. But then if sales come from Shopify from their front end, then obviously they keep everything. But. Okay, let's say obviously. Obviously, Shopify takes like, take some fees, right? Hypothetically, if we were to partner with a Shopify. We might ask them. If we can kind of host our own front end. Where we're still using their stack. And. And stuff like that, but. Do you guys see where I'm going with this, or should I. Should I do a better example? I'm thinking, essentially, we, like, collect all the different stores that are using that have Meme coins on our site, and we list their items on our own website. So, like, it's kind of like a little, like crypto, like a store, an online store where every single product is tied to a coin.

**Me:** No, this makes sense. Makes sense.

**Other:** Right. So I'm thinking, as far as faces go, like, phase one would just be. A solution that enables people to automatically buy back a coin. Phase two would be a solution that automatically allows people to buy back a coin and launch a coin where we would essentially clone Pump Fun and Radium. And then step three would be to have like the full on storefront. So there's like a. We have a coin. So we have buy box a coin deployment platform. And we have a storefront. Front end. And that storefront front end could even just be a redirect to Shopify or Public Square. Like, it could just be, like, a beautiful organization of all the different items that are sold. By our founders. With backlinks to the source shop.

**Me:** Makes sense, man. Yeah.

**Other:** Yeah. Cool. So do you. So I guess, like, how interested are you? Are you down? And if. Yes. How long do you think you can. It will take for you to find out if this is technologically feasible.

**Me:** So I have a couple comments. Right. Like if you had to on ramp conversion piece. Like, the engineering bottleneck here, right? I think. Like, have you looked at using an existing on ramp, like Moonpay or Ramp kind of embedded in the checkout flow, rather than building direct banking rails that could literally cut months off the prototype time? I think it would make a ton of sense to you. It's just like a third party.

**Other:** Yeah. So, I mean, unfortunately, I just don't think that people have that strong of a desire right now to pay for things. With crypto. And I also don't think that people would want to pay like 3% more to buy the same good using, like Moonpay. I know that Moonpay takes like a pretty egregious fee. I think it's something like 2.95% as the base fee and then like the platform providers always strap something on top of that.

**Me:** I don't. Think that people would. Want to. Buy. From.

**Other:** So, like, if you're just looking to buy, like, I don't know, like. A toothbrush or something, like an electric toothbrush for dollars.

**Me:** Something. Like.

**Other:** Then you have to pay, like, you know, a couple extra dollars just because of, like, this bottleneck. So I think.

**Me:** That.

**Other:** Ideally, we would. And the other problem is that, like, it's going to be hard for online stores. To. Sign up for this if they have to, like, use an entire different tech stack and, like, move things out of Shopify. Right? Like, people already already have stores on Shopify. And they probably just want some. Some tool that can automatically deduct their balance, send it to our bank account, convert it to crypto, and then send it to the coin. Like, I think we could probably just get, like, some type of institutional coinbase account, and as soon as cash is sent to us, we. We buy usdc, and then that's used. To the usdc is used to buy the meme coin.

**Me:** Yeah. No, I'm definitely interested, dude. Like, let me scope about feasibility this week, right? I can maybe have, like, a technical assessment back in about just a couple days after digging into the Shopify API and then on ramp options. I think like the quick tech spec great for like the phase one prototype, the core flow. You're going to get the creator that connects the Shopify store via like some form of oauth. Your creator sets like percentage of sales for buyback. You put like 10%, for example. On each sale. The webhooks would then trigger the back end. The back end would call Fiat on Ramp API, Right? So, like, man, that would be like Moonpay or Ramp or something. To convert the USD to SOL or like whatever smart contracts. Then execute the swap on radium or Jupiter for maybe the creator's native token. And then the tokens are said and done to LPS for like burn addresses, right? So the stack like back end. You could use node Python hosted on Vercel, Railway, whatever. Shopify integration. You just need the admin API. I've worked with it before, it's like, it's fine. And then using webhooks, you can just sort of, you know, get calls and triggers. For your on ramp. You can use moon pay or ramp API. But I mean, you know, depending on what we end up deciding there, right? Obviously. Shane Solano. Probably just simple build, low fees, vast penalty. Also like a native ecosystem.

**Other:** Yeah, Solana is definitely. Solana is definitely it. And I know a lot of people at the Solana foundation, so I'm pretty confident I can get us, like, a grant from them.

**Me:** Pretty. Confidently to get a second. Cool. Yeah, and then. Yeah, and then like the decks, right? Like, for best swap execution, since we chose Solano, we probably just use Jupiter. The open questions I need to still validate are like, do Moon pay and ramp have any B to B limits? And then like, KYB requirements for creator accounts. And then the Shopify webhook latency and then reliability. Occur for, like, real time triggers. And then necessarily gas slippage handling on low volume tokens pretty much pay. Out.

**Other:** Right. Okay. Yeah. It sounds like you totally, totally taken all of this in. I think. Yeah, that's probably all. From Ascend. If you can scope this out, that'd be awesome. And it sounds like you'll get back to us later this week.

**Me:** The. Same. Yeah, yeah, bro, yeah.

**Other:** How long are you in? You're in SoCal right now?

**Me:** You. 're in. No. I wish.

**Other:** Okay?

**Me:** I was really there until today. Or yesterday morning, actually.

**Other:** Damn. I would have met. I would have met up. When will you be back?

**Me:** Probably on the 11th, bro. So, like, a week from now.

**Other:** Okay? Cool. Yeah. So you guys. You guys should hang out or something on the 11th. Yeah. Coffee or lunch? When you're back here in LA, just give me a heads up.

**Me:** Not 100%, Matt. No, I'm definitely down there. We should definitely find some time to maybe catch up in person.

**Other:** Let's do it, man. Yeah. I really appreciate you hopping into this so quickly and super impressed with your background.

**Me:** Quickly.

**Other:** And just kind of grasping the vision here so quickly. Will and I are super. Yeah.

**Me:** Wrong, too. I mean, it's like kind of my first pass.

**Other:** Yeah, of course. And if you have any of your own ideas for, like, how this could be made better or more efficient than, like, a course, voice it as well. Yeah. So super, super excited that you're interested in this, and I'll hear from you guys later this week.

**Me:** Yeah.

**Other:** Rock and roll. All right, we'll catch you later. Talk soon. Bye. Bye.
