---
source: granola
workspace: eclipse
ingested_at: '2026-05-05T02:07:56.333013Z'
ingest_version: 1
content_hash: blake3:bf3b37412edb82f113f5240b6a9e8d7bda956a8e56c37f4b3c5dc0bb12d73864
provider_modified_at: '2026-03-23T15:53:12.949Z'
account: adithya@outerscope.xyz
account_slug: adithya-outerscope
document_id: ddb1a77e-2cc1-4892-8149-e1438ab2ef42
document_id_short: ddb1a77e
title: All Hands
created_at: '2026-03-23T15:33:36.919Z'
updated_at: '2026-03-23T15:53:12.949Z'
folders:
- id: 84a8f86d-16f6-4529-a4b3-11a687032b07
  title: ECLIPSE
creator:
  name: Adithya
  email: adithya@outerscope.xyz
attendees:
- name: null
  email: cemal@eclipse.builders
- name: null
  email: julien@eclipse.builders
- name: null
  email: daniel@eclipse.builders
- name: null
  email: kayla@eclipse.builders
- name: null
  email: vedant@eclipse.builders
- name: null
  email: chinghua@eclipse.builders
- name: null
  email: sydney@eclipse.builders
calendar_event:
  title: All Hands
  start: '2026-03-23T10:30:00-05:00'
  end: '2026-03-23T11:00:00-05:00'
  url: https://www.google.com/calendar/event?eid=MHZzaDRrdWxoNjk1bmFuYmtvOGRrYTN2YXRfMjAyNjAzMjNUMTUzMDAwWiBhZGl0aHlhQGVjbGlwc2UuYnVpbGRlcnM
  conferencing_url: https://meet.google.com/yjd-xszp-ghv
  conferencing_type: Google Meet
transcript_segment_count: 104
duration_ms: 1143280
valid_meeting: null
was_trashed: null
routed_by:
- workspace: eclipse
  rule: folder:ECLIPSE
---

# All Hands

> 2026-03-23T15:33:36.919Z · duration 19m 3s · 8 attendees

## Attendees

- **Adithya** (creator) <adithya@outerscope.xyz>
- ? <cemal@eclipse.builders>
- ? <julien@eclipse.builders>
- ? <daniel@eclipse.builders>
- ? <kayla@eclipse.builders>
- ? <vedant@eclipse.builders>
- ? <chinghua@eclipse.builders>
- ? <sydney@eclipse.builders>

## Calendar Event

- Title: All Hands
- Start: 2026-03-23T10:30:00-05:00
- End: 2026-03-23T11:00:00-05:00
- URL: https://www.google.com/calendar/event?eid=MHZzaDRrdWxoNjk1bmFuYmtvOGRrYTN2YXRfMjAyNjAzMjNUMTUzMDAwWiBhZGl0aHlhQGVjbGlwc2UuYnVpbGRlcnM
- Conferencing: Google Meet https://meet.google.com/yjd-xszp-ghv

## AI Notes

### GTC Conference Insights & Data Strategy

- Two key data angles identified from conference

    - Audio eval frameworks: No good audio data eval exists currently

          - Audio more nuanced than other modalities (image = yes/no, audio has cultural context)
          - Opportunity to establish as best audio data provider for frontier labs
    - Agent-native marketplace: End vision for Human API

          - Agents natively request tasks, contributors fulfill
          - Data collection builds contributor network for future automation
          - Goal: <2 hour turnaround on agent requests
- News Research partnership opportunity from GTC

    - Their MES agent went viral, want to collaborate

### 2026 Roadmap Overview

- Q1: Contributor app release

    - Focus on user volume + coverage diversity (age, location, background)
    - Enable location-specific task fulfillment
- Q2: Voice AI partnerships push

    - Leverage existing audio research and app infrastructure
- Q3: Expand beyond audio data

    - Additional task types beyond recording/submitting
- Q4: Agent request automation

    - Transition from managed services to agent-driven requests

### App Store Submission Status

- Submitted to both Apple and Google Play stores
- Build 1.09.22 currently under review
- 48+ hours in review (typical 24-40 hours)
- Release strategy moving forward:

    - Submit next release Tuesday/Wednesday while current under review
    - Metadata changes possible during review, code changes require resubmission
    - Subsequent reviews faster than initial (payment features trigger extra scrutiny)

### High-Value Data Opportunities

- Gulf Coast/Arabic region languages extremely valuable

    - Haitian Creole in high demand, paying top dollar
    - Connected with WHO organization contact for Haitian Creole speakers
- Physical/robotics AI data surge

    - World simulation environments, multi-point object pictures in demand
    - Robotics motion data (RP1 dataset = 700 hours, bought by everyone)
    - Opportunity for flagship dataset as launch spike
- High-quality data focus required

    - Low-quality data easily scraped by competitors
    - Consider acquiring call center for on-demand medium volume/low latency production

### Operations & Finance Updates

- Human API entity funding completed

    - Cross-border payment issues resolved
    - More reliable funding flows established
- Tax transition to new provider in progress
- Services agreement between Labs and Human API being finalized
- Multiple investor audit requests received (standard year-end confirmations)
- V2 app design in progress focusing on easier messaging and market fit

---

Chat with meeting transcript: [https://notes.granola.ai/t/ec1ddf45-a833-466e-aa1d-9489519da58d](https://notes.granola.ai/t/ec1ddf45-a833-466e-aa1d-9489519da58d)

## Transcript

**Other:** Data. So that was one thing that we also noticed from the conference. Like everyone's trying to be creative on how they're getting data and selling it. And obviously there's demand for data, but, you know, it is competitive. So I think for us, there's really two angles that we should approach data from. The first one is around evals, especially as it pertains to audio data. Right now they're really no good audio data, like eval framework out there. And it's because if you think about it. The, like audio data is not as black and white as some of the other modalities. So, for example, if it's like image, like you just answer, is this a car like yes or no, right? It's like pretty black and white, whereas, like, audio has a little bit more nuance to it and say, I can hear something and I could say, like, oh, this person sounds sad. But it's like Daniel hears it. He's like, oh, actually, this person sounds angry. And there's, like, a lot of cultural context related to it. And there's, like, other things. So I think if we could do a good job on potentially setting up more of, like, an email framework and kind of set us up as, like, the best audio data as a result of that, I think that could actually be quite valuable and put us on the map with a lot of the frontier labs. So that's something that I'm thinking through. Another angle that we should really push into is the agent first or agent native angle. I think that's actually the more interesting part of human API. Right. And that's kind of the end vision of human API, which is agents can request tasks or, you know, the task could be data collection, but whatever it is, where a marketplace kind of facilitating both sides where agents natively request tasks, someone fills it on the other end. In the data collection piece of it really is for us to establish the contributor Network for that to be even possible. Right. So it's like us kind of doing managed services right now, but eventually we're going to be. The hope is like we're going to be a lot more hands off and requests are going to come in just from agents themselves. So that's something that we should start, like, focusing on a lot more. I actually met with the news research people at gtc and they have, like, their mes agent, which has gone very viral, and they really want to do something with us. So it could be definitely an interesting, like, partnership to explore. And then on that note, I also, I put together, like, a high level roadmap. This is what I've shared with investors and some, like, external folks. So go through it here quickly. Yeah. So this is an overview that we put together that I put together. In general, the roadmap is pretty aligned with, like, what we've already talked about. We're kind of on, on this path already. But key one, it's really about the contributor app release, the kpis getting as many users on the app as possible and not just, like, sheer number, but also try to get as much coverage in the app as well. What I mean by coverage is really, like, diversity and background and, like, age ranges, like different locations. So I've. So whenever there is a catastrophe that's more location specific, we're able to fill that. So, yeah, key one contributor app release. Q2 really start focusing on voice AI partnerships. That's kind of what we've been doing already. So much of our so much of the app is built around audio and I feel like we've done so much research in audio. Like, we really want to push voice AI partnerships. Q3, I think, is when we can start looking beyond audio data again, like human API is meant to be more of a general marketplace as opposed to only audio. I think audio is a great place to start because there's so much demand for it. But I think around Q3, we should start thinking about additional, like motions within the app. That's not just like recording and submitting. And then the last one in Q4 of this year, we should start thinking more about agent requests. So again, like I said, instead of us being the managed services or more of like us creating task. We want to enable agents to send whatever request. And ideally we can get data requests filled in under two hours. I think that's actually like a really compelling sell. Yeah, that's roughly the roadmap and how I think about how we're breaking down like this year in particular. And I think that's it from gtc. Let me see if there's anything else. I'll share, like, probably like a larger follow up async in slack, more on, like maybe specific conversations. But I think at a high level, we kind of covered it. And then you had Daniel let you talk about the app and kind of where we're at on that in terms of apple approval. But we do have PR lined up for this Wednesday, as well as the ugc program lineup for end of this week. So I think we'll start making videos by the end of this week and start posting them on Monday. But it's. Yeah. Let me know on timeline so it can adjust accordingly. Yeah. We submitted to both app stores. Hooray. Good job. Everyone involved, which is everyone here. And we are awaiting approval from both of them. Still have not heard anything. They don't give you a lot of insight. They say it's typically 24 to 40 hours, but we've been longer than that. So not much you can do. Actually, in business hours, it's. I think we hit 48 this afternoon. So not too bad. And so in terms of. So let's talk about how we kind of deploy and release from here on out, and then we'll talk about timelines and expectations. Given that you have the approval lag and how kind of, like, heavy a mobile release is because it has to go through approval again. You usually are submitting your next release before you require what is approved. And so you kind of just keep the train going because you already have, you know, things you push from the last release because you've discovered things that you think might speed the approval process, what all kinds of reasons to keep the train going. And so we'll practice the same thing. And so we'll be putting together a release probably for like Tuesday or Wednesday. That's. It does feel weird, you know, we're not already out. It's already doing update, but it really is kind of the best way to do things because you don't want to be like, as you discover stuff from going live, you want to have those fixes in place. You want to have a new train kind of on the way forward. In terms of timelines. It's really difficult for me to like, it's hard to estimate software as it is like, I mess that up every time. But like this is extremely out of our control. And so I just don't know. I would say you should not commit yourself. And this is talking directly to Sydney do any sort of timeline right now. Because we do have no control. So if you like ugc subschedule for Wednesday, like I would push that, I just cannot. I can't do anything. You know, like, can you schedule stuff for three weeks out, like probably safer? But again, we just don't have any control here. Sorry to interrupt. You think it's possible, like, while it's under submission, if there are changes that can be done and it will be reflected on as well. So it's a possibility that. Or no. You can. No, no. So you can change your metadata. So screenshots descriptions and that can go before release. But if you want. To change the actual code, you need to resubmit for review and so that most of your timeline, but we can get your changes into the next release. And so we'll have that interview before this one even comes out, most likely. And then the good thing is your initial review is the slowest. And so every subsequent review is much faster because there's a number of reasons for that. Mostly that. Like features like ours paying people, it tends to trigger a lot of review because, like, there's just a lot of rules and regulations and kind of stuff around that for Apple to consider. And so they won't have to review that a second time because they've already kind of understood, like, the model. So the one that is the one that's live on the phone that we're testing right now, correct? It, I hope so. But I don't know what's live on your phone for you. And we have done build since then. Yeah. Yeah. So the build that we submitted is 1.09 build 22. Yeah. Yeah. And so it depends on what's on your phone. But if you want to see what's live, you go to 1.09 22. I can help you figure that out, too, if you want to. DM me or whatever. But, yeah, that's what's currently. Currently going. Okay. Yeah. I mean, that, that's fine. Let's get the release done first because you take, like, it takes a lot of time. So that's. Let's get it out first and then we can, you know, do stuff here and there. So, yeah, So that's exactly what we're not going to do. We keep going while it's in review. And so we're not going to let review block us from making progress. That makes sense. Yeah, for sure. I mean, I'm saying that it should be like, it's fine. You guys submitted. That's perfect. But if it's there's a few changes here and there, we're not going to change the code that's, but we can still change something else or can we not? So, yeah, if we change the code that's submitted, then we, we lose our spot in line, but we can add the new code to current releases and re release a new build. That goes in line right behind our existing one, and then it'll come out like a day later. Okay, that makes sense. Yeah. I mean, as far as, like, changing, like, some requests and design site will maybe, like, a few things that we can change. We can still work on that, but not on the main code. I get that. But we can still work on the changes. That's what I'm asking.

**Me:** You guys are saying the same thing, I'm pretty sure. Literally just what Daniel is saying is like he's just saying we can't like re-release the code or else we're gonna like our line's gonna spot in line's gonna get taken. We can just push out a new release. But all he's saying I think, and which you're saying to it on this, that like we just continue the UGC shit in the meantime, there's no reason to pause progress on that.

**Other:** Yeah.

**Me:** Is that okay?

**Other:** Yeah. Yeah.

**Me:** Cool? I can maybe give like a quick. Like update to on my end. Daniel, were you done there?

**Other:** I'm good.

**Me:** Okay, cool. Yeah, so Sydney covered a lot of it. Like for, you know, what happened with GTC essentially like people with money pulled up. And so like the issue with that is that like people with money already have like internal sort of workflows, right? They have the money to hire internal annotators, et cetera, et cetera. So it really became like a question of where can we actually provide value in the stack. And so to Sydney points, right, she's brought like two great points. The two biggest like ways that we can provide value is being the most agent native platform out there, right? That's like a key spike. And the other one is also just like having a super like user subjective evals type thing where it's like there's super non deterministic processes that are occurring or there's just entirely like geo specific subjective sort of, you know, tasks that occur as well. A prime example is the conversational voice, but there do exist other things as well. For example, I'll, I'll even give the example of like a doctor I was talking to, right? Orthopedic surgeon has like massive corpus of data for like decisions that doctors would make in different geos. Right. And so what he mentioned is like literally just do just like, you know, geo specific sort of patient things like folks in Spain actually approach like sort of a spinal surgery different than like folks in the states. And this is, you know, just due to the way like folks bones are built or some shit. I didn't quite understand, right? But like, like, you know, just speaks to the point that geospecific evas are valuable and like also like do you need to exist, but no one's really targeting that right now. So that could be kind of a course bike for us. The other two like big, you know, holes that we can kind of fill for like data specifically. Uh, the biggest learning there is like we need to start collecting and focusing on high quality data, right? Because honestly, the low quality shit people can just scrape on their own, right? Like it's foolish for us to assume that we'd have like a moat when like, you know, like cloud code could just scrape the shit for them. Like, you know, maybe like a day or two. Right. Um, moat over collecting public audio or public data of any kind. Right. So we need to collect extremely high quality data and that too internally. The idea is like maybe we could even buy up a call center right internally and like start producing on demand sort of data at like super like not high volume, but like medium volume like low latency that could potentially be a spike as well for us. So working with chuh, the Philippines contact to potentially see if that can happen. What was I about to say? Oh, right. Okay, so the gulf coast stuff, right? So Arabic sort of region, Haitian Creole languages are extremely tough to come across and are extremely valuable right now and are in demand. People are actually paying top dollar for this shit. So that should be two corpuses that were like, trying to focus on extremely. The last event I think we went to at GTC, we randomly ran into this dude that like friends this, runs this like who organization is randomly connected with a ton of patient Creole folks. So hopefully that's an in there. We can start producing data pretty quickly. Uh, physical and robotics AI was also like a big, big focus. Uh, there's like a massive shift, I think, to what people are even funding and hence like who even showed up to GTC type thing. I think there's like a massive shift to like robotics in general as even seen by the keynote, right? Even from Jensen. But as a result directly like folks are paying top dollar to left and right for world simulation environment type things, multi-point sort of pictures, right, of like just physical objects and also just like robotics motion like rp1, which is bones flagship data set has been bought up by every one of their mom. It's like a 700 hour data set rate type thing. And this is actually pretty realistic for like team of our size to produce as well. And I think we should maybe focus on, you know, one flagship data set that we can really start selling top dollar. So I'm doing a bit more reading research on that and also just talking to a couple folks this week because I think we should really go like all in on like just one data set to kind of be our spike for our launch as well. But anyways, that's my thoughts. Is that everyone?

**Other:** Another stole Kayla. Quick heads up on finance side. Last week we finished funding the human API entity. There are some initial compliance friction that comes with new accounts and cross bank transfer. So now we have more reliable funding flows in place. For human API going forward. And then on the lab side had started out some issues with cross border payments. So those should be smoother going forward as well. On the tax side. We made progress transitioning our work to the new provider that we're working with going forward. Also closed out some open items with our current one, including the amended returns that we'll be working on with them. As well as some invoicing cleanup as well. So I'm continuing to work through the services agreement between labs and human API to make sure that the relationship between those two entities is set up cleanly and also the tax efficient way. Also on the finance side, we received a few new investor audit requests last week. These are pretty standard year end confirmations, but most of the funds invested in eclipse. Have some version of this. So just continuing to work through those as they come in and then this week will mostly continue to be focused on the tax and finance items mentioned, as well as wrap up the detailed budget update. So Adithya, that's it on the Ops and finance side. I think Vedant may also have an update as well. Yeah, I mean, pretty much just mainly just, you know, the app stuff, it's already done and we have some changes that I mentioned in the github. So hopefully that's covered as well. I'll have to check the recent, you know, the app release again. So if I missed on any updates or stuff. So I just need to kind of go over that once that's done. I would be working on the V2 that we are. It's already under progress, so just need to figure out a better, you know, design overall. And which fits the market and stuff because right now it's more of, you know, getting the branding out and what we are about in terms of, like, messaging. And now we're trying to make it. Like, a little bit easier as well, I would say. So, yeah, main focus is on V2. And if anything else comes up, we'll be working on that. So, yeah, that's pretty much it. Great. Any questions, comments from anyone?

**Me:** Yeah, I mean, I'd love the inch team's thoughts on like this doc I put together just for like more agent native spec. It's like pretty basic shit honestly like pretty rudimentary. Just contains like, you know, some specs on how to turn like, you know, the API potentially into an MCP tool that we can expose and then also like some data structure shit. Like how do we even like structure like, you know, calling upon data or representing data.

**Other:** Take a look and leave any comments?

**Me:** So let's all take it. Thank you.

**Other:** Anyone else? Stay up to date async, especially around the app release timeline whenever we hear back from app store and Google Play store? Yeah. Excited to, to get it out there and get it into, you know, hands of users. All right. Thanks, guys.
