---
source: granola
workspace: power-kinetics
ingested_at: '2026-05-07T04:23:57.244510Z'
ingest_version: 1
content_hash: blake3:2aa9fcf5649cf20c5a561d1b87587877fcba449b4e92f6992b3ddbe909030cd8
provider_modified_at: '2026-05-06T19:32:34.704Z'
account: adithya@outerscope.xyz
account_slug: adithya-outerscope
document_id: 922c97bd-8e27-416a-ab69-7dc545862190
document_id_short: 922c97bd
title: Machine integration and user profile architecture with Brian
created_at: '2026-03-30T02:58:07.866Z'
updated_at: '2026-05-06T19:32:34.704Z'
folders:
- id: b3ec9fde-f09b-466a-bfe4-f3c0512cdce0
  title: POWERKINETICS
creator:
  name: Adithya
  email: adithya@outerscope.xyz
attendees: []
calendar_event: null
transcript_segment_count: 162
duration_ms: 976691
valid_meeting: true
was_trashed: null
routed_by:
- workspace: power-kinetics
  rule: folder:POWERKINETICS
---

# Machine integration and user profile architecture with Brian

> 2026-03-30T02:58:07.866Z · duration 16m 16s · 1 attendees

## Attendees

- **Adithya** (creator) <adithya@outerscope.xyz>

## AI Notes

### Machine Integration & Data Points

- Fitness machine has extensive data collection capabilities

    - Power, speed (per second), range of motion, range of motion per second
    - Multiple measurement types beyond basic metrics
- Need physical machine access to understand full integration potential

    - Current software has comprehensive data points
    - All existing data should be preserved in new interface
    - Focus on making display “sexy” and gamified

### Hardware Setup & Logistics

- Getting machine delivered this week for development

    - Contact Zach to arrange shipment
    - Setup location: garage (not upstairs)
- Potential road trip from San Francisco to Austin if needed

    - Multi-day drive with stops in Dallas

### Current Technical Issues

- Demo functionality failing during presentations

    - Second occurrence of system crashes
    - Works on local machine but fails after deployment
- Need screen recording for Brian instead of live demo

### User Experience Requirements

- Circuit training environment drives design needs

    - 30-second intervals between exercises
    - Heart rate maintenance critical for training effectiveness
- Key user flows needed:

    1. Athletes: Quick machine access, immediate profile loading
    2. Coaches: Simple athlete profile management via tablet/website
- Facial recognition integration potential

    - Auto-load profiles when athletes approach machines
    - Eliminate manual login delays

### Technical Architecture Questions

- Current system limitations:

    - All data stored locally on machine computers
    - No internet connectivity on existing machines
    - No API endpoints currently exposed
- Hardware components:

    - Potentiometer for measurement
    - Oil transducer for pressure detection
- Previous cloud integration existed (Martin/Alan’s work)

    - Multi-location data sharing capability
    - Need to reconnect with Martin and Alan for details

### Next Steps

- Adithya: Screen record working demo for Brian
- Get machine delivered this week for hands-on development
- Connect with key stakeholders:

    - Martin (previous developer) and Alan
    - Dr. Christensen (14 machines in facility)
    - Previous UI team for research insights
    - Cal coach and athletes for user feedback
- Brian: Provide PRD with user stories and requirements by Monday/Tuesday

    - Justify each requirement with 1-2 user examples
    - Share previous team’s research and interview process

---

Chat with meeting transcript: [https://notes.granola.ai/t/25cb68e4-24ba-4696-bf06-54919fe24c7b](https://notes.granola.ai/t/25cb68e4-24ba-4696-bf06-54919fe24c7b)

## Transcript

**Other:** Make a seamless. Integration to using the tech, right? So very simple start here, right? You have. Your endurance, you have your power, and then you have your. There's like three. There's like three different types of things that you can have. I forget what the old stuff was. I gotta get you a machine so you can see all the things that you can see on the machine, bro. Like, once you get. It's. It's one thing to look at the code and look at the software, but when you actually turn on the machine and you're. Like, playing with it and you understand the files that we have, you'll understand how to integrate that into a sexy. A sexy thing. So before I even just try to explain it to you. Just know that there's so much data points, bro. They get. They went so hard on. The data points that they are wanting. Right? Power. Speed, speeds per second range of motion per second. Range of motion. Right. Like those are two different things. Range of motion is one thing range of motion per second is another. So, like, it's like there's a bunch of different. Yeah. Anyways, I'll get you the machine as fast as possible. I'm gonna call them company right now and see if we can get one out there, too. Literally, literally, bro. Like, we need that. I need you to know that.

**Me:** Let's get it this week, man. I'm like, I mean, whatever.

**Other:** Yeah. All right, I'll. I'll call Zach right now. I'll call Zach right now and see what we can do to get that out there, too.

**Me:** Okay, nice dude.

**Other:** Make space. Do not have it outside.

**Me:** I'll make some space upstairs. Yeah, I'll figure it out.

**Other:** Here. It. It doesn't need to be upstairs.

**Me:** Or the garage. I'm an idiot.

**Other:** The garage. Yeah, you're. You're so stupid.

**Me:** Yeah, dude, I could get the garage.

**Other:** What the is wrong? Why? Why? What? Like the garage is the first place I thought about.

**Me:** But it's like hella fucking messy. I couldn't have a shit. Whatever. It's fine.

**Other:** I'll pull up to Austin and I'll help you. I'll pull. Literally. Literally, I'll go to San Francisco. I'll go grab an accelerator and I'll drive all the way to Austin.

**Me:** That's a fucking crazy drive, bro. You don't have to do all that.

**Other:** No, it's not. It's like a couple days. I'll some hoes on the way. It's fine. Like, I got some hose I need to see anyway.

**Me:** It pull up.

**Other:** I gotta pull up in Dallas and get that, bro. I'm gonna hit you later, though.

**Me:** Okay, easy. Sounds good, but I'll get to work.

**Other:** I'm ready. I'm trying to screen record and send it to Brian, but I can't send him what you keep saying that you're done and it keeps crapping out on you.

**Me:** Yeah, it's fucking demo never works, bro. Wait, okay, but like, what do you like the full functional shit?

**Other:** It looks cool. It looks cool thus far.

**Me:** Working a fucking pissed? It was working on my.

**Other:** This is the second time, bro. This is the second time.

**Me:** Thing. Working at my local machine and I pushed the shit and didn't.

**Other:** Up one more time and you're off. CEO, bro. I can't do it. And you're over here talking. You're trying to finesse me the way you're trying to finesse these people, bro.

**Me:** I was literally workouts. Okay, I'll screen record it. I'll send it to you, bro.

**Other:** All right, say less. That sounds cool. But no, the functionality looks cool. But before you put too much work into it, let's get you the machine first. Like, don't even bother with it until I get to the machine. That way you can see what it is. And you can just try to, like, I don't want to say copy and paste. But you can try to play around with it, see what's the most valuable. And honestly, I'll say this. Everything that is on that, everything, every data point that is on that current software is important, and we should keep it all. It's just how it comes across on the screen needs to be sexy, needs to look fun and, like, gamified. Okay, so. All right, bro, I'll hit you later.

**Me:** Yeah. But can you describe one thing to me? Like, I need to better understand, like, sort of the back end routing. Okay. Like essentially.

**Other:** Okay, hold on, hold on, bro. Just stay on the line, because this is. I'll just stay on the line.

**Me:** What I need to understand is who are the user profiles and how do they interact with one another? You have coaches, coaches manage what? Coaches manage players. Players should see what.

**Other:** Just stay on the line, dog. Stay on. How do I do this? Yo, Brian. Yo, what's good, bro? Do you have five minutes? Okay. Me. I want to introduce you to Shaq. Shaq is. He's a back end front end code developer. He. I think I talked about him a lot. He's an engineer. I'm trying him out for the CEO position. But he has some questions, and I was wondering if you can help me answer them. Hello?

**Me:** Yeah, yeah, I can hear. You.

**Other:** Oh. He just got off. Yo, what up, B? Hey, can you answer? So Shaq has some questions. I was wondering if you can take five minutes to answer them. Yeah, for sure. Hey, great meeting you, shocked.

**Me:** How's it going, man? Great to meet you. Great to meet you. So I essentially just going through sort of revamping the front end and back end right now. Like, you know, sort of like the code is working at this point. What I need to better understand is sort of like user profile is like actually like how's the app going to fully function, right? Specifically for the back end, right? Like what I'm thinking, okay, like what would be tremendously useful is maybe like a user story or user walkthrough. Right, for the product. Like basically think like, okay, like athletes manage the athlete group manages sort of like, or sorry, the coach manages an athlete group, for example, athletes see xyz on their dashboard, coaches, cxyz on their dashboard. This is like the feature that we need here, like et cetera, et cetera, right? Like some form of like PRD. Obviously, I've done like a bit of thinking on this already. Like there's like some level of like sort of product structure built in. But like what I'm maybe looking to see is the clarity on sort of how, the different user profiles interact with one another and how they interact with machines as well. Like where does the data actually like, you know, sort of flow through too?

**Other:** Where the user interviews and, like, getting feedback directly from athletes and coaches come in. So we actually do have. Two. We have the chest press slash the squad machine and the top of the currently at the hospital Pavilion, which is where a lot of the runners and swimmers for our college teams practice at. Hello. Brian. I can connect you with the coach there, and you can maybe talk to him and maybe even talk with some of the athletes to see what they're looking for. But we've talked to. The coaches and athletes before, and mainly what they were concerned about was making as simple as possible. For. For the athletes because they're constantly, like, switching in between different exercise, getting on and off of machines. So they wanted a way to very easily access.

**Me:** Quickly?

**Other:** Like, just get on the machine and immediately get started. That was one of their main things, being able to have, like, a really quick turnaround time when switching between machines. In terms of. Coaches accessing athlete profiles. They meant they want something that could be. Going on to. Sorry, Brian, you're breaking up. Say that again. So where did I get to? What was the last headset?

**Me:** You're talking about the coaches, man, I'm pretty sure.

**Other:** Yeah. Yeah. So the coach on the coach's end, they want to have a very simple way to bring up the profile of all the athletes. This is preferably through, like, a tablet or through some website. And then instead of, like, going through the screen every time, because currently all of the data is locally stored on the computer, so they would have to go into the computer to bring up data. And so right now they actually, I don't believe they even tracked data at this point because it's just such a hassle for them. Since they're one month quickly, which athletes on and off to do machines. So basically, it's a circuit Shack. It's a circuit. Like, they're in circuit mode. Basically, you have to work out, and you basically have 30 seconds to get into your next interval. Because your heart rate has everything to do with your heart rate, maintaining a certain level of. Of beats per minute or beats per second on your heart. To burn certain calorie to reach a certain type of fatigue, right, that will then train you for that, that, that moment in a game, right, where you're tired as. And you need to perform. So it's called, it's called hyperfit retraining or, like, high, you know, high intensity training. What's happening is that our machines take time to load up the profile. So if we had, like, facial recognition. Integrated on the camera or integrated on the machine where you hop on and it just slides you right into your profile and you're just picking up right where you left off and it just, that would be sick as, right? Like, that's the type of, like. That's the type of upgrade in, in, in, in what would help in any facility, any program, any Collegiate program, any professional program when they're doing group workouts when an athlete just hops in and the machine already knows who's on there. That, that's, like, a big thing. Right. So. But in terms of the data points that we're collecting power acceleration range of motion, what are some of the things that are on there, Brian, like on the accelerator? What are some of the things that we're, we're, we're looking at. Yeah. So you, you mentioned most of it. So right now. I. I'm not sure how much Michael has talked to you about the electronics currently on the machine. But the main electronic components is there's a potentiometer. And then there's a oil transducer, which basically just measures the amount of pressure being by the lever arm on the oil. Yeah. So those are my main two properties. And then from there, you can calculate degrees per second. You could calculate the amount of totals.

**Me:** You gave me like a couple API endpoint routes for that, bro. Like is there a github or anywhere that I could take a look at ignore it's going to be like what actual raw data comes out from these machines. That'd be tremendously helpful, at least really building a product itself. And like, how are you actually with these machines? Like is there like some sort of like API endpoint that's already been exposed?

**Other:** I don't think so.

**Me:** That like.

**Other:** I'm not CS major, so I'm not too familiar with all these terms, but from my understanding, everything is stored locally, I don't think there is any API. That, like, sends data online anywhere. Everything is stored directly on the computer.

**Me:** So wait the machines aren't even connected to the internet right now?

**Other:** If that's what you have to. Do. No, they're not. Well, I do know that Martin, and I need to get you in touch with Martin, Jack. That's Alan's developer. Like, you know, that's you. Basically, you and Martin are one and the same in terms of what you guys do for the company. Like, Martin is what you're doing for us, what Martin did for Alan is he. There was a cloud and there was a way for us to see. What other machines in Chicago or other machines in California were doing all the Australia. They were able to pull up data and see what teams and see what other organizations were doing with their machine. Now where that is and how that's come about and or whether we've lost the ability, that's a question that you need to ask Martin and Alan, and I'll get you in contact with them come in the next couple days. Okay? So. All right. Another thing is, have you. Wait, sir, one more thing. Shaq, have you seen the UI that we have contracted out previously? Obviously, you don't have to take anything from there, but they did their own, like, share of user interviews and research. And they might teach you some inspiration on, like, why people might be looking for. Have you seen the video or, like, looked at the code? Euro type has made.

**Me:** For what cyber you broke up. Your story.

**Other:** Brian, I'm gonna give you Shaq's number, and I want you guys talking all the time. So just spend.

**Me:** Like what do you what do you do sir?

**Other:** S our CTO.

**Me:** Okay. Okay.

**Other:** Brian's our head technician. He's, he's the one that's at Cal. He's been developing V2, and he's been helping start starting the manufacturing process. So, like. We definitely need him on. Yeah.

**Me:** Like request like two deliverables from you maybe by Monday or Tuesday one is if you could put together like a PRD right like you've you've lived and breathed with these like folks for way longer than either of us have you probably know like the exact sort of like requirements of like what these folks would want right and if you can justify each requirement with like one to two user stories or examples right of like why like this requirement would kind of make sense. That would be tremendously helpful right because like that's like customer research is like honestly what we should not go off those assumptions like we should treat ourselves idiots right because that's probably very likely the truth we don't know shit about shit when it comes to this product right and so like the customers know best right and so as such we have like a PRD that we can go off of and design the product off of that would be much much better instead of making it something kind of like trying to like you know fly so.

**Other:** Well, dude, first off, there's, there's other people that you need to speak to, like, that have had, mind you, Jack, this, the company's been around for 35 years. We have access to Dr. Christensen, who has 14 machines in his facility. I'll get you in contact with him. Right? We have con, we have people like Alan and people that have skin in the game, they'll tell you what, what the use cases are. So, I mean, if we need a modified version of that, then we can do that. But I think that there's a lot of people in the pipeline that I'm going to set you up with to ask all the questions you need to better understand our product.

**Me:** Yeah I mean if there is some form of like like just assumptions or any learnings that you've gotten Brian that'd be tremendously helpful to.

**Other:** But, yeah.

**Me:** Learn from.

**Other:** Yeah, of course. I'll also connect you with the previous team that was working on the UI part of the, updated software, and then they could probably tell you a little bit more about their research process and their interviews. But just for a little bit more clarification, I'm working mainly on the physical components. I'm a mechanical engineer, so I'm a very Hands-On person. I'm more on the physical component side. So if you have any, like, questions or insights you want to know about that, and I couldn't answer that, but in terms of, like, software, I'm probably not the best person to ask.

**Me:** Okay like like what specifically are you working on the machines like are you working on like the sensor components or like what do you.

**Other:** No, right now we are getting started on rebuilding the double knee and making upgrades to the frame to, like, cut down on cars and manufacturing. And that's what I'm currently working on with Alan for. It. It's mainly just the physical components, less so on the software side.

**Me:** Got you okay cool cool cool man okay sounds like a plan bro I mean yeah if there's any insights you have in the hardware side I mean you know I suspect there might be some that'd be tremendously helpful but I'll definitely also chat with some of my contacts and see if I can write a computer. Too.

**Other:** Of course, I'll get that over. To you.

**Me:** Sick dude not great to meet you man then yeah we'll stay in touch too I'll get your number for mic and then we'll stay in touch for sure.

**Other:** All right. Sounds good, guys. Thank you. All right, peace.

**Me:** Man.
