---
source: granola
workspace: eclipse
ingested_at: '2026-05-05T02:07:56.333013Z'
ingest_version: 1
content_hash: blake3:ec2d4838917fa4397249028bdab3d0ba9b3d5efbd716c8c1eeb3b93cd12b239a
provider_modified_at: '2025-11-13T16:53:19.104Z'
account: adithya@outerscope.xyz
account_slug: adithya-outerscope
document_id: 69d01b20-b35a-4bdf-8a82-e0be06a1b474
document_id_short: 69d01b20
title: Ecosystem Daily
created_at: '2025-11-13T16:29:11.956Z'
updated_at: '2025-11-13T16:53:19.104Z'
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
  email: daniel@eclipse.builders
- name: null
  email: sydney@eclipse.builders
- name: null
  email: chinghua@eclipse.builders
- name: null
  email: adi@eclipse.builders
calendar_event:
  title: Ecosystem Daily
  start: '2025-11-13T08:30:00-08:00'
  end: '2025-11-13T09:00:00-08:00'
  url: https://www.google.com/calendar/event?eid=ZjRkZnY0M2M1YWJzdWJkamp0cXA1dTFuNWpfMjAyNTExMTNUMTYzMDAwWiBhZGl0aHlhQG91dGVyc2NvcGUueHl6
  conferencing_url: https://meet.google.com/kmp-jmdk-rut
  conferencing_type: Google Meet
transcript_segment_count: 257
duration_ms: 2843440
valid_meeting: true
was_trashed: null
routed_by:
- workspace: eclipse
  rule: folder:ECLIPSE
---

# Ecosystem Daily

> 2025-11-13T16:29:11.956Z · duration 47m 23s · 6 attendees

## Attendees

- **Adithya** (creator) <adithya@outerscope.xyz>
- ? <cemal@eclipse.builders>
- ? <daniel@eclipse.builders>
- ? <sydney@eclipse.builders>
- ? <chinghua@eclipse.builders>
- ? <adi@eclipse.builders>

## Calendar Event

- Title: Ecosystem Daily
- Start: 2025-11-13T08:30:00-08:00
- End: 2025-11-13T09:00:00-08:00
- URL: https://www.google.com/calendar/event?eid=ZjRkZnY0M2M1YWJzdWJkamp0cXA1dTFuNWpfMjAyNTExMTNUMTYzMDAwWiBhZGl0aHlhQG91dGVyc2NvcGUueHl6
- Conferencing: Google Meet https://meet.google.com/kmp-jmdk-rut

## AI Notes

### Development Progress Update

- Boomi service sizes progressing well

    - Julian completed sound broker service basics
    - Notification system improvements with RabbitMQ integration
- Clerk authentication integration planned for today

    - Hosted service with Google/GitHub/email sign-in options
    - Will power both requester and worker user authentication
    - Aligns with decoupled architecture approach
- Message PR merged and ready for use
- Notification service development ongoing

### Payment System Architecture

- Onboarding process needs decision on timing

    - Task completion vs KYC requirements
    - Balance maintenance for both tribe and individual users
- Lazy payment approach agreed upon

    - Users can complete tasks first, add payment details later
    - Dashboard shows pending earnings (e.g., “$200 pending”)
    - Payment service as wrapper around multiple providers
- Bridge upgrade scheduled for tomorrow

    - UI blocker coverage review needed
    - Cemal to assist with front-end PRD

### Data Licensing & Rights Framework

- Comprehensive documentation added to GitHub wiki
- Three core licensing rates established:

    - Training
    - Reference
    - Redistribution
- Additional pricing layers:

    - Purpose, model family, security restrictions
    - Exclusivity as premium upsell option
    - Category and time-limited exclusives
- Global compliance considerations

    - Region of origin and regional processing requirements
    - User consent templates and data revocation rights

### Go-to-Market Strategy

- API positioning: “Programmable labor” for last-mile AI gaps
- Target lighthouse partners prioritized:

    - Voice/Audio, LMS, Robotics, AR companies score highest
    - Focus on specialized vertical data vs generic datasets
- Initial pilot structure:

    - 10,000 minutes of voice data
    - 5,000 IRL images
    - Sub-10 cent validation costs
    - Acceptance rate optimization
- Cold outreach list development prioritized over compliance work

    - Legal team (Cooley) to handle data rights documentation

### Design Direction & Team Updates

- Logo feedback: Too abstract, needs more obvious human representation

    - Current designs remind of gaming/trading apps rather than human-centric platform
    - Request for more literal human motif
- Vedant starts Monday as designer

    - Priority: Worker signup flow and mobile app design
    - Landing page with phone number capture and app download flow
- Worker platform prioritized over requester dashboard

    - Building worker base as key early asset for outreach

### Next Steps

- Daniel: Implement Clerk authentication, review Clerk payments feature
- Chinghua: Complete notification service, assist with bridge upgrade UI review
- Adithya: Build lighthouse partner outreach list, tag relevant people for wiki review
- Sydney: Refine logo designs with clearer human representation
- Team: Prepare for product announcement and first task launches within a month

---

Chat with meeting transcript: [https://notes.granola.ai/d/69d01b20-b35a-4bdf-8a82-e0be06a1b474](https://notes.granola.ai/d/69d01b20-b35a-4bdf-8a82-e0be06a1b474)

## Transcript

**Other:** Good morning. I can hear you clearly. Let me. Okay? Yeah, it's better. The volume. Is. Like the volume is up and also the echo.

**Me:** Good morning. Okay, let me see here. I could have just.

**Other:** It's better now. It's better. Now.

**Me:** Perfect. Nice. Where are you based again?

**Other:** Type. A private.

**Me:** Type area.

**Other:** Good morning. So after the daylight saving ends, it's getting harder. Getting late. Yeah. In terms of for you right now. Zero. 12. I don't know how to. Anyway, it's in May. It's 12:30.

**Me:** Midnight.

**Other:** Yeah, it's 12:30. Oh, my God, I forgot. Yeah, Daylight savings.

**Me:** City. I updated the GitHub wiki actually, with all my documents. How do I tag people? I couldn't figure that out yesterday.

**Other:** You can, people. You just got another GitHub username.

**Me:** Okay, got you.

**Other:** Yeah.

**Me:** Right on. Morning. Morning. How's it gone?

**Other:** Mine's the same. Everywhere. I'm Daniel with three Z's all over the Internet. But no one else. 's.

**Me:** Guys. Dennis like Thanos, but Dennis.

**Other:** No. Dan goles.

**Me:** Okay? All right.

**Other:** Let's start. Julian's out today or for staying up today at least, and then he's out tomorrow.

**Me:** Actually in SoCal. Not really. For a wedding or something, you're saying? Yeah. It's always fun.

**Other:** Daniel, you want to start? Sure. Yeah. The Boomi service sizzes are coming along. Julian got the basics for the sound broker service done. Some nice progress on notifications. And adding rabbitmq. I'm going to look into Clerk for users and probably add that today. So Clerk is an authentication service that is hosted by. We pay for it, basically. And it comes with all the free sign in goodies. So if you're going to add sign with Google sign up. Yeah, it works really well. Next. Sign in with GitHub. Sign in with whatever. Email, phone, whatever. It just kind of works and gives you widgets to do it, and then it lets us access that data. It should go really well with our architecture decisions already because we're decoupling everything, so it'll just be like something. It's the couple that we don't. Right? So we're going to add that today. And use that to power both the requester and the worker users. I'll just be clerk people. So you'll click some button, sign in with some service, and then boom. And so that'll be good. So that'll save a ton of time. Yeah. That's going to be my focus. Today. I'll pass it to you, Chunk. Yeah. So message PR is merge, so it's ready to use. And I'm still working on the notification service. I was playing around the onboarding process. I think we need to decide onboarding. Process for the tribe. If we are going to make people to do the task before they get the payment before like this. Kyc, we need to. Maintain the balance. Our own. And then we have also have the tribe balance to maintain. So deep UK system. So, yeah, need to decide. When the user. S unbolly to strike connection. And another thing. Caleb called me. Tonight. We are going to upgrade the bridge. So I help to review the update process and see if the UI is covered. The UI blocker is cover all the transition is covering all the cases. And. We may upgrade the bridge tomorrow. If. You were brain. Dude, I just thanked Jamal to do a front end PRD90. Anyone to help him? Are you good? I think it's just change the address and then I can pull up the old commit for the UI grapher, ok? Did you hear that, Jamal? Cool. Thanks. And on the payments question, I think so I'm thinking about it is you should be able to like, upload your payment details at any point in the app itself up even after you complete a task. So we should allow people to complete the task first and then say, like, if you want to get paid out, you need to fill out your payment info. Yeah. Just let them lazily do it. Have, like, their dashboard where it shows, like, 200 bucks pending and they can fill out the details. Again. Exactly. Yeah. So I think balance. Okay, got it. Yeah. So you'll just have, like. You'll just record a balance in the R database and then details on stripe. You can send the payment. Or the payout request. Yeah. And for the future. If we are going to integrate other payments, it will also work. Got it. Yeah. So your service will just be like a wrapper around different payment services. There might only ever be one, but, yeah, in the future, there could be more. Okay?

**Me:** I can go really quick. So basically just put together a ton of docs mentioned, not copied and pasted into the GitHub wiki. Would love y'all's review of it. I'll tag the relevant people now that I know how to do that. Just super brief, I think, stuff that I haven't discussed in the previous standup. So I'm putting together like a data licensing and rights playbook, just like, just to ensure that we're compliant across GEO for just handling PII data potentially and more. On the licensing front, we're kind of standardizing. Three core rates, so training, reference, and redistribution. Right, so that's essentially mapping directly how AI labs already buy data. Including my research. So we are layering on purpose model family and also security restrictions. You can also use exclusivity gate. Exclusivity. It's like an upsell. Right. So it's not exclusive by default. It's kind of the idea. And then you have category and time limited exclusives that we can also price higher. I'm also kind of thinking about, like a pricing scorecard as well, which I've kind of uploaded. Onto the notion, but I'm copying and pasting yet to the wiki. I'll do that right now. But basically for global data collection, we're defining sort of region of origin and regional processing. Basically, both of those kind of need to be compliant. Obviously, once we get delivery, models will kind of sort of follow our expectations in general. So like static snapshots, periodic refreshes, or even like real time feeds of data. You can also, I have expense. I've had some boilerplate, like templates around the consents, larger things that we can get sort of folks to send general data auditability and then also revocation, right? Like you can also pull your data as well so that users are trying to feeling safe type thing and buyers pay for that matter. So that's kind of the idea there. I think I've already covered sort of like the API narrative. Essentially, the gig economy is not really too sexy to work for, according to research. So the positioning is kind of simple, right? Where basically allowing for these people to be programmable labor in a way. Right. And sort of the data layer for agents that kind of hit like last mile gaps and the pitches that AI can't do this without you type thing. Right. Like you are sort of very important for collecting this valuable data, which is true. We're not, like, lying to them or anything. So essentially buy it Lutigramart angle here, right? From like a positioning standpoint and narrative standpoint, it's like buyer the kind of programming like a real world. What is going on in that background, dude? Sorry. I look like Thanos or something. It's weird. I like, just like Jesus. A blob. But basically, buyers are programming the real world. Contributors are turning sort of like individual moments into income streams. The partners, right? And the things that are connecting here is like one massive orchestration agent. Like, once we have more data identifying people, So we know what person to connect to what data vertical. This will also data broker sort of conversations will be tremendously valuable here, which I'm kind of working on. Like pulling together a list as well. I've set up like a mock CIM as well within notion. I'm going to make it more full fledged to capture more sort of work streams because go to market, marketing, kind of go in parallel here, since we're kind of going 0 to 1. For Lighthouse Partners. I've also created like a scorecard. I briefly touched on this earlier this week. I kind of updated a little more Voice Hour. LMS Robotics, AR companies kind of score the highest based on sort of my scoring and I think should be our primary sort of key for Q1 targets just to close. Broker in Tier 2 labs are willing to pay, but lesser sort of moat around the data type thing. They're paying for more generic data. It's not really super vertical specific, which I think is really the advantage of the product as a whole, given that we're able to collect sort of long tail data for lack of a better term, we should focus on highly specialized data where we have a clear note and where we when and where we can also potentially, down the line, create models. Taking off this data is kind of the idea. So first pilots are like, you know, maybe like 10,000 minutes of voice or maybe like 5,000 IRL images. Right? And we can also optimize that for maybe acceptance rate. Then also maybe like under 10 cent, like, validation cost, depending on how we do QC. Anyways, that's about it. I have much more detail on all this stuff in the GitHub wiki outside the relevant people right now to go and review that stuff.

**Other:** I think the priority is really just to get us in front of as many people as possible. So say, like, in a month or so, when we announce the product, like, say, that's like, what we're going to do our first tasks and we're going to build the data set. Like, what data should we be targeting for. I think that's kind of the. The question we're trying to answer here on the compliance stuff. I already talked to Cooley in our general counsel, and I think they probably already have a lot of that. Info, it'll be much faster for them to, like, gather, like, all the data rights type thing, so, yeah, I don't think you have to worry about that for now.

**Me:** Oh. Sick. 100%. Cool.

**Other:** I think the priority is just getting a list of even folks that we can cold DM the lighthouse, partners, whoever we can talk to.

**Me:** 100%. Yeah, I'll work on that today.

**Other:** Did you guys see the logos that I sent yesterday? The updated logos? I didn't look at them. But I will. Thank you for your honesty. Yeah, I was like, I can't. I can't. I can't do this. This, Sydney. These are the V2s. We have quite a few of them. So this was kind of the last time we talked about a little human motif. One that. This is kind of a. Another version of that. This one, probably, honestly, is my favorite. And there's this one. Supposed to look a little bit like a chip. It doesn't. You had some other inspirations behind it. If you watch the video, I think he kind of walks through it a little bit more. Watch the video. He could be really like this one. He thought this one was pretty unique. That one looks like candy. Which one? The gum drop the contra. I see it. Yeah. You guys have strong opinions on any of these? I don't like them. Really? Which one? Or, like, why specifically? I think they're too abstract, honestly. What would be? Let's abstract. I don't know. Am I looking at the logos on my doc? And they all, like, remind me of what the app is. You know, mostly. Mostly, like Slack is horrible logo. Like, Discord has, like, a video game controller, like, Imessage has, like, a speech bubble, and like, Obsidian has a rock. Telegram has a paper airplane. Like you think it should be more literal. I just thought it would. Yeah. At least evoke something. Either like the company or the purpose. I actually felt like this one was more literal because it's supposed to be, like, a human motif. Right. Yeah, I didn't pick that up as, like, a human when I saw it, but now that you say that. That makes it a little more sense. But he has arms. He is a midsection. And then what's like this fourth curve down? Like, why does he have two legs, like multiple humans? It looks like a human with two sets of legs. It makes sense. If it's a stick figure, why does it have so many legs? Because. Do you remember the other one? These were like v1. And again. There's too many limbs there. That's not what people look like. Do you think it should be just like a human? Too many tasks. I just. If it's meant to evoke the human, like, why would it have so many arm? I don't know. I'm not, like, great at this stuff either. So don't take my opinion. Like too seriously. But you're on a Mac, right? Just, like, look at your doc and be like, what are these have in common? Like, find my has like a radar screen. But then what is the opening eye logo, you know? Yeah. No, it's true. They don't all have that. That's fair. Yeah, because I can't remember OpenAI. Literally just a generic butthole. Yeah, It's a generic bowl, and now it's so recognizable.

**Me:** Yeah.

**Other:** Yeah.

**Me:** Morning.

**Other:** Yeah, maybe for. I don't know.

**Me:** Tab. You right? Out.

**Other:** Okay, so a little bit more literal. Also, I don't think I can look too much of just like a human because it kind of. I feel like when you have, like, a human logo, it kind of leans more into, like, education. Nonprofit. I feel like those types typically have, like, a human logo.

**Me:** Now, I appreciate the sentiment of Daniel. Honestly, that is. That is your fair point. Dude, that looks like the Finder logo right now, literally. With, like, my video. Jesus.

**Other:** Yeah. I guess Finder is a weird logo. It's just like. It's just so classic at this point. It's like. They're like. It's like, from like, the 70s or something. I got that a little bit. Okay? Any other thoughts?

**Me:** They look cool. Like they're, like, you know, futuristic, all that stuff. It's just like, the sentiment is true that, like, maybe it's interesting to make it look more like a human or something.

**Other:** So feedback is one, but make it a little bit more obvious that it's a human.

**Me:** What if we just removed, like, the third, you know, or, sorry, like the fourth from the top line?

**Other:** From the top line. Like this.

**Me:** Still wouldn't work. Actually, it's like six. Whatever.

**Other:** But for the human, like if the second curve, like there's two downward, there's two leg to oriented curves. So it just looks like a basketball.

**Me:** Yeah.

**Other:** Yellow basket. Like, if you told me this is an app for trading NBA NFTs, I would totally get. It. Well, I think it's also supposed to be a globe. It's like a globe and a human. This is why I don't do the Lego feed. Rack. Yeah, they. For design feedback, you have to be a little bit more specific. Oh, also, speaking of design, Vedant is starting Monday. What would be the most helpful? Like thing design. Yeah, let's talk about that. So I had a thought about this. Earlier. I think. Our biggest asset. Would be like the number of people we have on the platform early on. So, like, when we're reaching out, we can link. Hey, I'm from Human in the Loop. And we represent a worker for so many thousand people ready to do whatever. And so doing that sign up flow and getting that going makes a ton of sense. And it seems like the mobile app is a way to do that. Or like. Like a splash page and a mobile app, something like that. So I think having him design the worker signup flow and worker app. Where the highest leverage design items are. Also. Like, I don't know. I could see us not making the requester dashboard public for a while. You know, because we'll probably be the first requesters anyway, so we don't care what it looks like. Does that make sense? Cool. Okay, sounds good. Yeah, I think the. The initial signup flow or the landing page, it will be kind of dependent on branding as well. And I think of a pretty clear idea of what the flow is. It's basically just landing page. The call to action is enter your phone number. And then we send some kind of, like, confirmation text, and then at some point, we send them the app to download. But I think the. Yeah, I think what he could probably help with is the actual, like, app design, like, starting on that. Yeah. I think that'll be super clarifying for us to have him think through that for sure, because it's like it all kind of flows through there anyway. Okay? Anything else. Is everyone clear on what they're working on today and tomorrow? Sounds good. Oh, actually, real quick. Or this is just for King Law. Clerk has a payments feature. I don't know how good it is and if it's going to be useful, but you should just check it out. Just to rule it out as something we need to know about or whatever. Got it? Yeah, just take a look. See later. Thanks.
