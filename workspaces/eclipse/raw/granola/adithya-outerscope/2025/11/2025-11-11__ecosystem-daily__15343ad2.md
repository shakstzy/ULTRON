---
source: granola
workspace: eclipse
ingested_at: '2026-05-05T02:07:56.333013Z'
ingest_version: 1
content_hash: blake3:9d31cb976b7fd902ae04514449a2b17c88c21e80c7a8eda8554e4b1171fbe843
provider_modified_at: '2025-11-11T17:19:40.053Z'
account: adithya@outerscope.xyz
account_slug: adithya-outerscope
document_id: 15343ad2-3996-4e23-bbbb-0cdc09229139
document_id_short: 15343ad2
title: Ecosystem Daily
created_at: '2025-11-11T16:40:25.844Z'
updated_at: '2025-11-11T17:19:40.053Z'
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
  email: sydney@eclipse.builders
- name: null
  email: adi@eclipse.builders
calendar_event:
  title: Ecosystem Daily
  start: '2025-11-11T08:30:00-08:00'
  end: '2025-11-11T09:00:00-08:00'
  url: https://www.google.com/calendar/event?eid=ZjRkZnY0M2M1YWJzdWJkamp0cXA1dTFuNWpfMjAyNTExMTFUMTYzMDAwWiBhZGl0aHlhQG91dGVyc2NvcGUueHl6
  conferencing_url: https://meet.google.com/kmp-jmdk-rut
  conferencing_type: Google Meet
transcript_segment_count: 196
duration_ms: 1434843
valid_meeting: true
was_trashed: null
routed_by:
- workspace: eclipse
  rule: folder:ECLIPSE
---

# Ecosystem Daily

> 2025-11-11T16:40:25.844Z · duration 23m 54s · 6 attendees

## Attendees

- **Adithya** (creator) <adithya@outerscope.xyz>
- ? <cemal@eclipse.builders>
- ? <julien@eclipse.builders>
- ? <daniel@eclipse.builders>
- ? <sydney@eclipse.builders>
- ? <adi@eclipse.builders>

## Calendar Event

- Title: Ecosystem Daily
- Start: 2025-11-11T08:30:00-08:00
- End: 2025-11-11T09:00:00-08:00
- URL: https://www.google.com/calendar/event?eid=ZjRkZnY0M2M1YWJzdWJkamp0cXA1dTFuNWpfMjAyNTExMTFUMTYzMDAwWiBhZGl0aHlhQG91dGVyc2NvcGUueHl6
- Conferencing: Google Meet https://meet.google.com/kmp-jmdk-rut

## AI Notes

### Technical Infrastructure Progress

- Cleaning up large PR for database setup

    - Decluttering initial DB implementation
    - Removing unnecessary metadata architecture components
- Next priorities:

    - Merge current PR to unblock team
    - Complete initial database setup
    - Build first endpoint for user audio uploads
- Object storage decision pending

    - AWS vs GCP vs other providers still undecided
    - Most storage packages (like Minio) are universal across providers
    - Can mock out storage layer until decision made

### Business Development & Partnerships

- Partner triaging in progress

    - Identified key contacts to reach out to
    - Will route outreach through Sydney for better response rates
- Target conferences identified for upcoming months
- Micro-app strategy development

    - Document scanner concept with backend data collection
    - AI tax consultant app with valuable data monetization
    - Focus on providing legitimate utility while capturing data
- Priority targets:

    - Data brokers and AI labs for data gaps analysis
    - Voice data and LLM companies
    - 11 Labs connection in progress
    - Cemal as potential partnership opportunity

### Data Collection Strategy

- Exploring partnerships with existing AI tools

    - Fireflies and other AI notetakers for data licensing
    - Transcription services as potential data sources
- YC startup ecosystem focus

    - 70-80% of YC companies primarily generate data
    - Opportunity to partner with “bullshit startups” for backend data plays
- Public speaking app framework

    - Front-end utility with backend data collection
    - Speech training and transcription operations focus

### Payment Infrastructure

- Stripe Connect platform evaluation

    - Meeting scheduled to discuss marketplace payments
    - Crypto PM involved for stablecoin payout capabilities
    - Platform allows simplified payments in any currency/stablecoins
- Questions around specific needs for marketplace functionality

---

Chat with meeting transcript: [https://notes.granola.ai/d/15343ad2-3996-4e23-bbbb-0cdc09229139](https://notes.granola.ai/d/15343ad2-3996-4e23-bbbb-0cdc09229139)

## Transcript

**Other:** That makes sense for straight up, I can say. Oh, yeah. I mean, we're not building Rabbit, right? We're just, like, deploying it. And so it has Docker containers and UIs and all this crap, and so you really just kind of. It's not even a ton more because you have to build a lot of that stuff to work with sqs anyway, so it's really much different. And then you're blocking your brain as well. API. Yeah. We haven't even decided what using Amazon we might use, like GCP or some other thing. So whatever. We'll figure that out. I can go. Yeah. So we're going to clean up. My PR that I made. It was a giant pr, So I made a bunch of mess myself to clean up. So I'm just deorganizing that or reorganizing that now, kind of decluttering what I did to get the DB Going. I was also looking at. The metadata architecture. Some of that, some of the stuff I have in there isn't going to need it for the final product. So our goal today is just to get that PR going and then do finish that PR app so we can merge that in so that nothing else is lingering behind it and doesn't just kind of drag along and then pretty quickly follow up after with the initial database setup. And then start working on, I guess, first endpoint of, like, you know, user uploading audio to our servers. I think probably my only question is then if I. I kind of. I assumed we were set on ads. If we're not done on aws, Which I guess I can mock out, like, whatever the object storage is or. I don't know if you want to, just because it's kind of become. It's going to be a quick thing. I'm going to be searching it soon. Yeah, I believe all the object storage packages are the high. Not all, but most of the prominent ones are universal. Quote me on that. That's good. What was that? It's all investigate. Or like that measure. Yeah, I'm pretty sure that. Like Minio is, like, the big one, and it has, you know, it's universal object storage. And so you can create. Yeah, you can create a client, and then it's like, works for Google or Amazon or whatever. That's cool. Yeah, like Google, Amazon, and Azure, they all have the same APIs for, like, the core services. Like ec2st, whatever. Because they're all like, trying to vampire tech any us for the longest time. You're trying to run the us. Vampire attack aws. Like, they wanted to take your customers, and so their customers, like, oh, we don't. Like, you don't have to.

**Me:** The article about me. Gcp. Eric Anthropic moving to GCP or something like making it cheaper. Yeah.

**Other:** Wait. Using different chips. Yeah. Yeah, Sounds like a big moment to us. Hopefully. Cool many other things.

**Me:** Where's my shit? Dying. No. Not again, bro. Jesus christ. Fuck my life, man. What the hell is this? Shit. God. Okay, don't worry, boys. The laptop's coming in today. Man, we're clutching. We're clutching. Oh, my goodness. Okay, I've been working on basically just like partner triaging, essentially. Right. In a nutshell. I've identified a couple of folks that I need to start talking with. Now it's just a matter of how I get to them. So Sydney and I have a pretty good sync yesterday. We're just like. I've covered all the docs that are thrown together right now I'm throwing together the rest of the docs and copying and pasting everything to the GitHub wiki. I think I have access to it now too. I logged in. Everything looks good. I'm just working on sort of like a list of sort of cool DMS for AI companies as well, since that seems to be working historically well. Probably be routed through Sydney just because my polygon optics aren't as good as hers and she might get more responses. I'm also looking at tangible conferences over the coming months that would be good to just start regenerating for us. And then also we discuss this content of micro apps that we can kind of build. So I'm like, kind of ideating on that as well. Like maybe just basically. Absolutely. We can provide tangible value to users just through Document Scanner or something like xyz, and they do still actually get the data collection play in. The back end, right type thing. Sydney Ford is something that you could literally have. An AI tax consultant type thing, but you also invest in all that data. It's very valuable data that you can sell off to other people on the back end, too. So I'm starting to think about maybe how we can start providing. Legit utility, but also truly just a data collection plan. The back end type thing. So that is another thing I'm working on. I think the immediate priority is understanding what sort of data brokers dapps are true like AI labs data gaps as well as sort of voice data LLM companies like data gaps. Are trying to get a connected cartoon. Still, 11 months is also a priority recon. Sydney, you've already connected with them. But maybe just having. Oh, yeah, I'm connecting with 11. Okay? Well, I can actually ever get into 11 of the guys I know. Like, LA is connected with founders. So hopefully that will be an easy. End. Also, Cemal could be an interesting one as well. We actually live nearly 500 for that too. So that would be pretty sick. Okay? And then I think, yeah, I'm just working on putting everything over to the GitHub wiki. There's nothing really else. Working on the immediate. Term. But, yeah, I guess that's my update. As. We were looking at yesterday. Was. Making public. Content. Speaking. Literally. Tell them exactly. What scripts to read. And what to. Follow. I kind of wonder if they get enough Fireflies. And these AI notetakers would be willing to license data to us? Like, if they're already doing it to LLM marketplaces and whatnot. But I mean, speaking. Absolutely. Live speech ops, like of any cotton cut thing, just like transcription ops, is something we should probably focus on, I think. Yeah. I wonder. If transcript. Ion ads will give us. Their data. Though. Because I feel like that's. A plumb mode for them too, and they must take Ultra Train their internal model based on the. Help. With. Public speaking? Yeah. Voice and flex family training for ads passes, all that shit. Yeah, totally. Right. The. Frame is like. A. Public speaking app. But then. We just use their data. We can just find a bunch of found with a bunch of bullshit YC startups and just happen to get data collection plays for us in the back end, dude. I feel like. Going. To. The web. B. But. Straight up. Dude. Most of the. Yc companies are. Think it's. Like 70, 80%. Of yc startups. Are only. More. Like. Generating data. As well. With. The infra. Because we're going to go around. Us we're going to need kind of like. The data pipeline. The way it affect. S more. And things of that nature. How the use. R interacts. For. The goal. Notice that. Because I sent it from a. Core yesterday. Just to. See what their. Platform's like. There's. This full heat. I'll take a LinkedIn. Resume. You put your link. Edin in. And you. Can refer people again. There's. Fully like. A job, hun. Ting play. But you use. Stripe. I didn't notice. That. What's the. What? 's the. Stripe call. For today. Then. They were just. Interested in what we're building. Find. S me building out the. Payment stuff. Right. Y. Es. But if there's any questions that we have, because this is one of their newer offerings, right. We're going to use our stablecoin payouts. Yeah. Stablecoins are newer. But the Marketplace Connect platform is not as newer. I think that one's a little older. Yeah. But the PM we're talking to is the crypto pm. I just got ELO from them and said, I forget what it's called. I want to say it's like markets or financial markets, like that. They just started this thing where it's like you can. Basically, it's for paying people out and allows you to simplify paying out in any currency. Or stable coins. Honestly. That's the marketplace. I don't know what. The hell I call it? I think it's called Connect. The thing. I don't know. A financial account. Is that what it is? I don't know. I just got an email. Like yesterday. The. Day before. Yeah. Start. Connect platform marketplace payments. Yeah, I think. That's what I was talking about. That's it. I don't know if this is. What we need or anything like that. I don't. Know what that one is. They had so much stuff. That's the thing that I just. I think that's the thing. I just got the email account. I don't know. As. Far as I can tell. It's straight. Connect is what we need. Yeah. Stripe connect. Yeah. I think this is only like, two or three years old. I guess this replaced drive Treasury. Never. That was. Great. Anything else. Thanks. Guys.
