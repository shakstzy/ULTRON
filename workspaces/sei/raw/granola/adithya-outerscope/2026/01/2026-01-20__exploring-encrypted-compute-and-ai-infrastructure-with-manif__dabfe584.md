---
source: granola
workspace: sei
ingested_at: '2026-05-07T04:23:57.244510Z'
ingest_version: 1
content_hash: blake3:31146c53ba2afe5ddf9f33be2db20ebcc1d0ede5d95a6de411a666e085b909a8
provider_modified_at: '2026-01-20T18:43:44.202Z'
account: adithya@outerscope.xyz
account_slug: adithya-outerscope
document_id: dabfe584-f649-448f-a320-161de97481d1
document_id_short: dabfe584
title: Exploring encrypted compute and AI infrastructure with Manifold
created_at: '2026-01-20T18:31:22.436Z'
updated_at: '2026-01-20T18:43:44.202Z'
folders:
- id: 3ca3cb55-d6e1-49ef-961a-8ba2469731a5
  title: SEI
creator:
  name: Adithya
  email: adithya@outerscope.xyz
attendees: []
calendar_event: null
transcript_segment_count: 78
duration_ms: 736470
valid_meeting: true
was_trashed: null
routed_by:
- workspace: sei
  rule: folder:SEI
---

# Exploring encrypted compute and AI infrastructure with Manifold

> 2026-01-20T18:31:22.436Z · duration 12m 16s · 1 attendees

## Attendees

- **Adithya** (creator) <adithya@outerscope.xyz>

## AI Notes

### Meeting Background & Personal Updates

- Manifold team member apologized for missing last week’s meeting
- Both parties catching up - skiing trip out west, returning to Austin for 2026
- Adithya currently in LA handling rental matters, planning return to Austin/NYC by March-April
- Confirmed Adithya’s family connection to Austin

### Current Work Status

- Adithya working at SAY and Eclipse (contract work)
- Building AI products for both companies
- Ideas stemming from customer conversations
- Planning to bring incubation project to SAY eventually
- Both SAY and Eclipse pivoting to AI products post-funding

    - Loaded with funding, focusing on internal incubations

### SAY & Eclipse AI Projects

- SAY project: FHE + TEE compute solution

    - TEEs for linear operations (efficiency)
    - FHE encrypted compute for nonlinear operations
- Eclipse project: Voice AI data gathering

    - Conversational voice data sourcing
    - Similar to Trovio Turing model but smaller scale
- Projects must drive value back to SAY (not necessarily built on SAY blockchain)

### Manifold’s Encrypted Compute Infrastructure

- Built Targon Virtual Machine (TVM) - encrypted VMs for confidential computing
- Runs in TEEs for distributed decentralized compute
- Completed mid-2024, already attested thousands of Nvidia GPUs
- Compatible with:

    - All Nvidia Hopper and Blackwell architectures
    - All Intel and AMD CPU chips
- Established relationships with Intel and Nvidia for future compatibility
- Currently licensing technology to other compute networks

### Bittensor & Manifold Operations

- Team of 10-12 people, raised $10M Series A (summer 2024)
- Co-founders from OpenTensor Foundation (Bittensor builders)
- Run oldest active subnet on Bittensor (Targon - subnet 4)
- Current services:

    - Inference and compute network on subnet
    - Aggregate compute for open source model serving
    - GPU rental via serverless SDK
- Scaling limitations on subnet leading to expansion beyond Bittensor
- Exploring partnerships with Akash, Ionet, other networks
- Using TVM security to ensure encrypted AI workloads across decentralized networks

### Technical Discussion Points

- Adithya inquired about side channel risk mitigation in TEEs
- Manifold offering technical documentation and engineer follow-up call
- Architecture alignment: TEEs for linear operations, FHE for nonlinear operations
- Manifold’s model compared to Prime Intellect (similarities in GPU rental, differences in training focus)

---

Chat with meeting transcript: [https://notes.granola.ai/t/66950c56-a462-4dda-9319-55118d8c5fb4](https://notes.granola.ai/t/66950c56-a462-4dda-9319-55118d8c5fb4)

## Transcript

**Other:** But keep them busy. For sure. But been off to a good start to the year so far. Was out west doing a little skiing a couple weeks ago, which was nice. But yeah, back in Austin, selling in, getting back into the swing of things for 2,026. Sorry about last week again, man. That was totally my.

**Me:** No worries.

**Other:** I knew about it earlier in the day, and I knew that I had that meeting. I could have sworn I texted you, but obviously I didn't, so I'm sorry about that.

**Me:** You're mad, joe. You're mad. Gentlemen. Dope, bro. Nice.

**Other:** How are you? Out in la or out in california.

**Me:** Out in la right now, man. Yeah. But most likely we'll be coming back to Austin or New York probably by, like, March or April time frame.

**Other:** Okay. So did you move out, then?

**Me:** I'm out in just like la, just taking care of some rental stuff, but that's about it.

**Other:** Okay? So do you still have your place in Austin, then, or.

**Me:** That's just like my parents place. So I just like crash with.

**Other:** That nice. Okay. I didn't realize that your family was from here also.

**Me:** Yay. Yeah.

**Other:** Nice man. Well, how's everything going with you and. What was it? Synapse, I think it's called.

**Me:** Yeah, I just, like, reuse the domain, dude. It's a completely different idea. But I'm working at SAY and then Eclipse as well right now, so we're working on just AI products about those companies. So just, like, chatting with a couple of those customers is actually even where, like, the idea stemmed from. But firstly.

**Other:** Contract work per se.

**Me:** It says four time and then eclipses contract work. Yeah.

**Other:** Okay. Nice. Cool. How's that been going? So are you still doing your side gig, kind of like, thing on the side that you're building, or you're not really as focused on that anymore?

**Me:** No, no. I'm, like, pretty focused on that. Like, it's just an incubation that I'll probably bring up to say at some point, but that's kind of the idea.

**Other:** Okay. Nice. How is everything? We'd say an eclipse these days. I've heard a good amount about Eclipse. They officially launched last year, I think, right? They're like,

**Me:** Yeah, the token is clipped to both places, bro, but both of them are just now focusing on incubations internally. Like, they're both loaded from, like, the funding and whatnot, but now they just want incubations in order to, like, take them, you know, like, further. So both of them are pivoting to like AI products for, say, we're building out like a FHE plus tee place. So for linear operations, we're using a tee. For nonlinear operations, we're using an FHE encrypted sort of compute play. And then for Eclipse, it's more so sort of just a like data gathering play. Right? Like, so for voice AI, if you want sort of conversational voice data, like, you're essentially closing that from, like, folks like Trovio Turing and other folks that just need voice AI data. That's about it. We're acting like, but just smaller scale.

**Other:** Nice. With, say, in the compute stuff. So you mentioned they're kind of doing like an incubator. Does that mean they're kind of looking for and supporting projects that are building on say, or is it just in general, they're just kind of like incubating different projects regardless of if they're built on sales chain.

**Me:** So I'm like. I'm, like, just part of, like, the incubations team, so I'm like. Their incubation is growth lead. So we just, like, have, like, ideas that are like. We just, like, generate, and then we'll just, like, test and spin up pretty quickly. Just to see.

**Other:** But they have to be built on, say, blockchain or not necessarily.

**Me:** Not necessarily, but drive value back to, say, in some form.

**Other:** Yeah. Cool. So I'm kind of curious about the compute stuff, as you mentioned, like tees and encrypted compute. I'm curious, is that something that's, like, being built internally or that's, like, part of the incubation, like, one of the projects in the incubation program?

**Me:** I mean, like, we don't have an official program. It's just, like, a team internally that just, like, incubates projects.

**Other:** Oh, I see, I see. Because there's some overlap with what we built here at Manifold, what we call the Targon virtual machine. Which is essentially like our encrypted VMs for fully confidential computing technology running in TES for like distributed deceptualized compute. So we've actually begun having some conversations with some of these other networks on like licensing are security infrastructure. Which we built. We finished that maybe, like midway through last year and have, like, already attested thousands of Nvidia GPUs. So it's compatible with all Nvidia Hopper and Blackwell architectures. And then all intel and amd cpu chips. And that's all, you know, fully secure, fully encrypted. We working with a number of different hardware players and kind of like establishing KNOW security infrastructure and making sure it's compatible with all future models. We've already, like, begun building a relationship with intel and Nvidia to kind of ensure this. And now we're starting to kind of license this tech to other compute networks that, you know, are working on building this, or thought they wanted it, but didn't know how to build it or didn't want to take the time to build it. So if that could be of use to you guys or any interest, I would be happy to talk about some of that as well.

**Me:** Do you guys, like, candle, like, side channel risks, like, in your tees. Like, make isolation, like, constant time kernels. Things like that.

**Other:** Side channeling, you said.

**Me:** Like side channel risks? Pretty much.

**Other:** I'd have to check with, like, one of our engineers. You know, I'm obviously not, like, the one developing this stuff, so I'm sure they probably know about it. But if it would be useful for you guys, I can send you over, like, an article or some documentation on our tvm. I don't know if it's like, you guys have already built this or you're in the process of building it, but if it's something.

**Me:** Valuable. Like, you know, read about where, like, we've architected the solution, right? Like, tees are extremely efficient, right? From a compute perspective. For only your operations, right?

**Other:** What was that?

**Me:** Whereas with, like, nonlinear operations, right? Like, you'd want to run them in some form of, like, a FHE format. That's kind of the idea, but we'd love to learn more about what you guys are building. For sure. Yeah.

**Other:** Yeah. Well, I can send you over some information and like, if it would be helpful, we can do like a follow up call with one of my engineers and like someone from here, potentially kind of like technical team that's developing this stuff. But if it's, if I'm following correctly with what you're saying it sounds very similar to, like, what we and our team have already built. And we've begun, like, licensing this technology to different, you know, compute and decentralized network providers, which, you know, potentially could be a great fit for you guys as well. So it sounds like just sounded similar. So maybe there are limitations or isn't the right fit, but it could be, you know, potentially what you guys are already working towards.

**Me:** For sure. For sure, dude. I thought so. I thought you were, like, working in the AI space, too, right? Or no.

**Other:** Yeah. So we build on a blockchain called Bittensor. Yeah. You're familiar with Bittensor, I think.

**Me:** You founded this. This is like something that you founded.

**Other:** No, no, I didn't found Bittensor or this company.

**Me:** No, but I. I know you joined Potential, but you founded Manifold.

**Other:** No, no. So I'm working with. We have a team of, like, about 10, like, 12 people or so now. We just raised our Series A this past summer for 10 mil, which is. Which is great. So we got a couple years of Runway, and I didn't. Found this. My two co founders actually came from the open Tensor Foundation.

**Me:** Okay? N. Ice.

**Other:** So my two co founders were like early researchers and builders at the Open Tensor foundation, which built a bit tensor blockchain and we run the oldest subnet on Bittensor, actually Targon, which is subnet four. So technically there's subnet one, two and three came before some that are subnet, but those ones have all changed hands since then, so ours is kind of like the longest standing active subnet. But yeah, so we built like, we have kind of inference and compute network on our subnet. So, like, we've used our subnet to aggregate compute and then we serve inference for open source models on that compute as well as, you know, allow people to kind of just rent it or use our serverless SDK. And so that's been, like, working really well. And we've been onboarding more and more customers for that. The problem is with our subnet, it has, like, a limitation on the amount of compute that it can really serve and pay out at one time. So it kind of has a little bit of a ceiling, which is why we realized, like, in order to scale and, like, serve more customers and meet more demand and, like, Grow our distribution. We need to access more compute beyond just our subnet. And so this led us to. Okay, well, how do we access more compute? Obviously, there's all these different networks. We have a lot of relationships with some of them, like other subnets on Bittensor, like, you know, Akash, for example, Ionet. Or some of these teams we've been talking to of how we can leverage their compute. But also part of what we built is this TVM security so that we can ensure that, you know, even though it's a decentralized network, all of this AI workloads are fully secured and, and encrypted. And so we've been talking with these other networks on how we can bring our security technology we've already built. To leverage compute off their networks to continue scaling and serving more customers. So I think that's kind of like the direction we're heading, which is why, you know, what you said just kind of struck a chord and sounded like it potentially could be a good fit for us.

**Me:** So just to like, kind of summarize, right, like, you know, and like, this is like kind of like my dumbed down version, I guess, but like. So you guys are kind of just kind of building secure vaults for GPUs in a way, right? Like, you guys are wrapping these Nvidia chips and encrypted. Containers so no one can kind of peek at what's running inside. Right, like you're running a compute network on Bit Tensor as well. Kind of like sort of a rental for your GPU model, right? Where you guys are pulling machines together and then, like, letting folks rent out these machines, right? For, like, running AI models. Is that similar to, like, kind of like the Prime Intellect model in a way? Yeah.
