---
source: granola
workspace: eclipse
ingested_at: '2026-05-07T04:23:57.244510Z'
ingest_version: 1
content_hash: blake3:653925212b9100eac5c5617a70c6df09df1b20d9e9765392b282095db5116723
provider_modified_at: '2026-03-31T22:53:52.853Z'
account: adithya@outerscope.xyz
account_slug: adithya-outerscope
document_id: 381cea1b-f21a-481c-89c0-5c89d0095d7c
document_id_short: 381cea1b
title: lock in app tasks
created_at: '2026-03-31T21:55:50.494Z'
updated_at: '2026-03-31T22:53:52.853Z'
folders:
- id: 84a8f86d-16f6-4529-a4b3-11a687032b07
  title: ECLIPSE
creator:
  name: Adithya
  email: adithya@outerscope.xyz
attendees:
- name: null
  email: daniel@eclipse.builders
- name: null
  email: sydney@eclipse.builders
calendar_event:
  title: lock in app tasks
  start: '2026-03-31T16:30:00-05:00'
  end: '2026-03-31T17:00:00-05:00'
  url: https://www.google.com/calendar/event?eid=MmZhdmUyb2t1Z2ZqdXFzcGs1dmtucGM2ZTIgYWRpdGh5YUBlY2xpcHNlLmJ1aWxkZXJz
  conferencing_url: https://meet.google.com/srz-rwgj-dbp
  conferencing_type: Google Meet
transcript_segment_count: 859
duration_ms: 3468837
valid_meeting: true
was_trashed: null
routed_by:
- workspace: eclipse
  rule: folder:ECLIPSE
---

# lock in app tasks

> 2026-03-31T21:55:50.494Z · duration 57m 48s · 3 attendees

## Attendees

- **Adithya** (creator) <adithya@outerscope.xyz>
- <daniel@eclipse.builders>
- <sydney@eclipse.builders>

## Calendar Event

- Title: lock in app tasks
- Start: 2026-03-31T16:30:00-05:00
- End: 2026-03-31T17:00:00-05:00
- URL: https://www.google.com/calendar/event?eid=MmZhdmUyb2t1Z2ZqdXFzcGs1dmtucGM2ZTIgYWRpdGh5YUBlY2xpcHNlLmJ1aWxkZXJz
- Conferencing: Google Meet https://meet.google.com/srz-rwgj-dbp

## AI Notes

### App Tasks — Immediate (Before Tomorrow’s PR)

- Remove test task from marketplace before PR goes live

    - Don’t want early users completing it and expecting payout
- Daniel to share task creation UI with Adithya and Sydney so they can manage tasks independently
- App confirmed live in App Store (found under Business category, search “Human API”)
- Bug: verification code input getting stuck on second digit — create GitHub issue

### Task Creation Dashboard — Improvements

- Add custom instructions per task (currently hard-coded generic “speak clearly” prompt)
- Add demographic targeting (e.g. push task to male 25–35)
- Add task caps (e.g. max 1,000 hours, auto-closes on fulfillment)

### Metadata & Dialect Collection

- Current profile fields: location, gender, language, accent — good baseline
- Language list is hard-coded in frontend → any dialect expansion triggers App Store review
- Plan: add sub-dropdown for dialect once language is selected (e.g. Mandarin → Shanghainese / Taiwanese)
- Collect device location per sample (IP-derived, no UX friction needed)

    - Use to flag anomalies (e.g. user claims England, recording from Indonesia)
    - Not a substitute for self-reported language — use together, not combined as a single signal
- Birthplace flagged as more reliable than current location for dialect inference

### Two-Channel / Conversational Audio

- Core requirement: two mics in same room, each phone recording independently, files linked as one session
- No need to diarize or splice — just two full-length files with background noise intact

    - Buyers want proximal voice + ambient room noise; not a clean isolated track
- Current app has no multi-speaker session matching — but retroactive matching is viable

    - Diarize uploaded audio → match silence timestamps across files → auto-pair in backend
    - Reviewer (Adithya) can confirm matches in a front-end UI
- Longer-term: in-app VOIP calling (both users on app, call recorded natively)

    - VoIP via GCP or AWS; estimated ~1–2 weeks if kept simple
    - Requires both users on the app; could drive network effects via contacts import
    - Sydney: write up requirements before scoping — still open questions on exact spec
- Immediate unblock: users can already upload single-channel audio; retroactive pairing means two-channel tasks can go live without waiting for the feature

### Pipeline & Data Deals

- Trovio: shopping around (~4 active conversations), likely wants conversational data in regional dialects — need to clarify if scripted or natural
- Fluffle: already live, paying out via bank transfer/invoice (B2B partners to follow same model)
- Podcast data: Sydney close to signing ~1,500–2,000 hours of licensed podcast audio this week
- Piler: potential buyer for SFX indexing/classification data — Adithya to confirm on reply
- SFX demand: Johnny indicated demand has cooled recently — deprioritized
- Medical/HIPAA angle: better suited for direct B2B channel (WHO contact) than in-app tasks
- Neil: now available to tap for warm intros to founders — Adithya to put together a shortlist

### Next Steps

- Daniel

    - Remove test task before tomorrow’s PR goes live
    - Confirm deletion to Sydney (so PR can be paused if needed)
    - Share task creation UI link
    - Write down task dashboard requirements (instructions, targeting, caps)
    - Research LiDAR/ARKit feasibility for future physical AI feature
- Sydney

    - Finalize podcast data licensing deal (~1,500–2,000 hrs)
    - Clarify with Trovio: scripted reads vs. natural conversation in regional dialects
    - Spec out two-channel/VOIP feature requirements before engineering kicks off
- Adithya

    - Send two-channel PRD to group chat
    - Send updated Trovio QA doc to Sydney
    - Send revised data pipeline Excel to Sydney
    - File GitHub issue for verification code input bug
    - Put together shortlist of founders to intro via Neil
    - Follow up with Piler on SFX data interest once they reply

---

Chat with meeting transcript: [https://notes.granola.ai/t/9b27859b-ae01-4095-aec8-10f49defa863](https://notes.granola.ai/t/9b27859b-ae01-4095-aec8-10f49defa863)

## Transcript

**Other:** I think we have the onboarding task. And yeah, we have the test task. Yeah. Yeah. Let's remove the test task. Well, let's keep the demo task. Obviously, the onboarding one. But let's remove the test task. Okay. Yeah, because we're going to kick off PR tomorrow. So people are going to start probably downloading it. I don't want people to do the test task and expect to get paid out for it. Yeah. Okay. Will do. So where can we find, like, app download statistics? Is that through the apple developer dashboard? I think they have them there. Let's check it out. We have Sentry, which tracks. Errors and usage and some other. Data as well. So that'll be coming in. Kind of. I don't have thought on me to get used my passkey. I'm just going to grab it. Give me a second.

**Me:** I'm putting together a list right now, Sydney. I'm just sending it over.

**Other:** All right. Store connect. So that's called. I don't know what they call. Do you love plaskies, though? Love a good pass key. Here. Analytics. What does this do? Let's see. The app is currently unavailable for analytics. Oh. Wait. Sorry, I'm on the wrong. App. Analytics. Cool. Not enough data for anything. Yeah. I guess I don't have data. Let's see if we're actually in the App Store.

**Me:** So I think for medium term, I mean, like, we just continue with what we're, you know, has worked and paid historically with just, just natural multi-turn human to human. We already are getting an inbound from fluff. That's already happening.

**Other:** Yeah.

**Me:** The non-native English speakers, you, you got the brief from trovio earlier. Dude, I definitely thought he mentioned Haitian and Arabic for sure. Right. There was that.

**Other:** Is a conversation from before. And then Haitian, I think, was the world health organization guy.

**Me:** Right. But he didn't like, but, like, there wasn't a mention of demand. For location.

**Other:** Not from troubio.

**Me:** Okay. Might have been someone. Okay. But anyways, I think we should obviously prioritize, like, non-native English speakers talking in English. So that's like dialects pretty much from, like, you know, English is probably the most in demand data set. Like, I don't think we need to prioritize Spanish, like, blah, blah, like other dialects for that. Like, we just need to prioritize dialects for English from probably the most major geos, which in this case are Spanish, Arabic and whatever else, like from a population perspective, like European speakers, for example, Etc. Sfx audio, I think has also been identified, like, a couple times, and we already have the infrastructure for it. So I think that's like a short-term goal that we can, like, easy win type thing. I think Johnny also mentioned that they're, like, paying for expax packs as well. So that could be interesting. We have the medic. Like, we have, like, a doctor Network through, like, the, the dude as well. So, you know, if there's, like, medical terminology or whatever, there's, like. Like that. The, the lady I spoke to, like, with the HIPAA compliance thing, that there might be an angle there. Like, I can, like, repaint her and be like, hey, like, we now have a source, right? For, like, maybe, like, doctors that can, like, readily record things for you or share notes or transcriptions with you, whether this be of interest to you. That could be a potential deal. And then emotes, right? Like, basically, like, voice actors type thing where it's like, you know, like, you have, like, various Expressions that are being demonstrated. The issue why this would kind of be, like, a little stickier is because, like, you, you can't really control quality as much, and QA would be extremely difficult to do in this case without, like, a manual audit of some kind. So that's why it's deep prioritized, you know, long-term goal, obviously, is just the disparity map. I, I guarantee you that's probably going to pay out quicker and, like, more. But, like, the issue is we just have, like, infrastructure limitations right now. So. That is. Thoughts from my end.

**Other:** Well, I guess, like, do we have a screen of what it looks like when there are no tasks in the no tasks available? Yeah, we have something. It's in the design file, too, but I don't. I don't. I can't recall what it. What it is. Because the. Okay, so on the ones that you mentioned, I think sfx, I'm pretty sure johnny actually said the demand for that was lower. Like, that was like a previous demand, but they haven't really heard anything about it recently.

**Me:** Oh, rip. What the hell? Okay.

**Other:** Medical stuff. Yeah. I feel like the medical stuff is probably less relevant for the app itself because that's probably the channel we're going to go through. It's like the world health organization guy as opposed to within the app. Yeah.

**Me:** So for those one-off cases, like, are we still going to pay out through boomi, or is it just going to be a direct payout, like, where it's just a batch? Like, what? Like, like a Jaden, for example. Right. Like a podcast guy. Like, would they drop, like, something in, like, a custom, like, you know, page made for them on boomi, or would it just be through something else? Because don't we have basic QA checks going through booby? Wouldn't it be wiser for us to, like, just run everything through, like, the QA check.

**Other:** I guess we could just have them upload via API.

**Me:** Yeah, or some. Yeah. Or, like, some batch upload portal or something, you know, which is like.

**Other:** Right?

**Me:** Yeah, that's possible. And then. But payouts would happen manually. You're saying, like, like we're doing right now with fluffle.

**Other:** Yes. Well, folks who chose to.

**Me:** Okay. Got it. Makes sense.

**Other:** Yeah, they wanted to be in. They want to invoice and, like, do bank transfer.

**Me:** Cool.

**Other:** Yeah. So we're going to do something similar because I think. Yeah. Especially with, like, the more B2B stuff or the partners I think we should just. We should do, like, bank transfer and invoice.

**Me:** Add on. What about that one video team, dude? I followed up with them, like, as well. Like the. They were talking about, like, sort of video to audio. Audio to video transcription. They're right next to Sentinel. In, like, the. You remember them? They're. Like, we're in, like, the accelerators program blanking on the name. I'll find it on in the business cards, like, after the meeting or message it to you. But anyways, they're like, they were definitely paying mass effects, they mentioned. Right. Like you talk to their, their founder or something. Like, because they, they were like, yo, like, we don't have a way of, like, mapping sfx right now to, like, sort of our model.

**Other:** The piler guys.

**Me:** Yes. Yeah. Oh, yeah, exactly. Thank you. Yes. Facts.

**Other:** Yes. So was. That. Was that sfx? Or that was. I think it was them indexing. Audio. I guess. Yeah. Indexing as effect.

**Me:** There were indexing video and audio and then, like. But they didn't have a way of classifying what sfx was what, if I recall properly. So they'd probably pay for that data, if I'm not mistaken.

**Other:** Yeah.

**Me:** It, like, once they reply back to me, I'll confirm that. But. Yeah. Why are there two pilot AIs, bro? What the. Okay. So I think immediate term just dispatched the ones that are working right now, which is just conversational two-way audio. And then localized English transcriptions.

**Other:** Well, we don't have a good way to do that unless we're doing the stitching.

**Me:** Well, I mean, like. Well, Daniel's diarization works, right? If I'm not mistaken.

**Other:** Yeah.

**Me:** Yes. I mean, we just, like, have, like, maybe, like, one audio that then gets diarized automatically.

**Other:** People just record, like, one conversation. Is that what it is?

**Me:** Correct.

**Other:** And then I thought part of it was also the. The room noises.

**Me:** We'd capture that phone now.

**Other:** Like.

**Me:** Like, all we're doing is just chopping audio. We're not, like, removing silence or anything.

**Other:** But wouldn't it be. I know. But once you, when you have the silences, it's going to be completely silent on one side.

**Me:** You're right. You're right. You're right, bro. You're right.

**Other:** What's the problem you're trying to solve? I'm. I'm not.

**Me:** So, like, let's assume you and I are talking, like, a room, Daniel, right? Like, you're, like, one end of the room. Like, the way your voice reflects in the room sounds would be captured on my mic pretty much during this silence. And apparently that's like, that's desirable to folks, which is actually facts. That is desirable to folks like we've heard that multiple times.

**Other:** Okay.

**Me:** So we'd essentially, the feature requirement would essentially be, like, some form of, like, synced time synced. Audio between two phones. I have no idea how that would happen. Well, actually, no, no, I don't know what happened, bro. What am I saying? We basically just start two independent recordings, okay? They'd be. They would basically get tagged by, like, the API to the same session. Okay. And then we just do, like, some form of, like, time code, like syncing. And, like, that's like, there's apis for that. Actually.

**Other:** I don't. Understand the problem you're trying to solve.

**Me:** The, the problem is that we need two mics in the room and we need those, like, we need two sources of audio for a conversation.

**Other:** Like.

**Me:** I don't know. I don't know how to translate that to engineering. Honestly.

**Other:** But why? What's wrong with each person taking out their phone and recording it?

**Me:** That's, that's exactly. That's exactly it. Like, like each person would just, like, record on their own phone, but in the same room. But, like, we need some way to, like, tag, like, that that's the same conversation, because right now, when I, like, go into review, I have, like, no idea which conversation is which, like, type thing, you know, like, which one is, like, paired with which?

**Other:** Like we want. Okay, so I'm sorry. But. All right, so the model buyer, the people buying the data, they want to hear.

**Me:** Both sides of the.

**Other:** They want to hear the two sides of the conversation. So they want to hear the distant voice and the proximal voice.

**Me:** Yeah.

**Other:** And they want two distinct recordings. Not the distant voice in the proximal voice. They actually don't want to hear the other person on the recording, but they want, like, while you're speaking, I'm not saying anything, but they're like room noises still. As I'm waiting for you to speak or, like, finish your sentence. But they don't want to hear the voice. Yeah. They don't want to hear you in the background. So it's like a phone call.

**Me:** Obviously they will. Like, you're right. Obviously they will, but, like, ish.

**Other:** Okay.

**Me:** Yeah.

**Other:** Well, that seems even easier then because isn't that just like, hey, we're having a conversation. I'm holding the mic up to my mouth and whatever happens, happens. Is that what we're describing? Oh, like we pass the phone back and forth, and then we diarize up.

**Me:** Yeah.

**Other:** Yeah. I mean. To the extent they even want to diarize. Sure. But. Yeah.

**Me:** Okay. Okay. Okay. I need a whiteboard or some, bro. Hold on. Like, okay, you have, you have, like, these two speakers, okay? You have two speakers. Okay. That are talking. You have all these waveforms going. Okay. You have two recordings that are going at the same time. Okay. This, this guy shuts up. Okay, bang. You still have room noises here, though. Like, you can't that out. Like, if you have one file that you're diarizing, you're splicing that up. So you don't have room noise here. You want complete silence. So you need two points of recording, correct?

**Other:** Well, I'm saying we. We don't.

**Me:** Audio by wanting that, like, room noise from when the other guy is talking, this guy's shutting up.

**Other:** I know we don't diarize because we're not going to move the mic to speaker.

**Me:** I don't.

**Other:** Two. Right. So there's speaker a and B, and we have a mic per speaker.

**Me:** Yes. Yeah.

**Other:** And we just leave them running the whole time.

**Me:** Correct. Exactly. Yeah. I don't think passing a phone back and forth would work, though. Like, that's not a possibility.

**Other:** Yeah, I have misunderstood the requirement.

**Me:** No, no, but, like.

**Other:** But. Yeah, I think you just give each person a mic, and that's what they want. Which makes sense because that's. Like. And, like, a phone call or a TV. Everyone has their own mic in any audio scenario. Right. And so that's what you want to recreate. So I actually don't think we need to do anything, like anything we would do. We just degrade the quality.

**Me:** If there's some, like, you know, I don't know how this actually gets executed in the back end, but if there's some, like, metadata tag that can, like, be, like, this conversation ID is the same for this.

**Other:** Right. Yeah. So basically, like, when you diarize the final step is making separate files. But you still make timestamps of when every speaker is babbling. And so you would pass that as, like, a metadata. And be like, hey, this speaker is going from here to here. You can hear the background noise. You know, from here to here. Blah, blah, blah, blah, blah. And then the file could be merged, be like, hey, speaker a is minute one and minute two. You know, 201 to 259 is speaker B, and that would be back here in my speaker a.

**Me:** Nice. Would we even need that level of fidelity, low key, like in the data, Sydney?

**Other:** Whatever they want, right? I'm kind of confused. So are we diarrhea or are we not ours? Is it two mics or one diorizing is like a two step process? So one is tagging the timestamps of the speakers. The other is separating them into separate files. So we would just do the first. Okay. So it would start originally as, like, you know, two speakers, two files, but then we would just timestamp it.

**Me:** I don't think there's any need to even timestamp it, dude, to be honest. Like, I don't know if the buyer. Yeah.

**Other:** Yeah. Whatever. Whatever they want. There would still be two files because it's two pieces of data that they want because they want.

**Me:** But.

**Other:** Speakers with background noise. And this is two speakers with background noise. So we would give them two files. But they wouldn't be, like, spliced up each file would be the same length. Right. So they would both have to be recording on their own app.

**Me:** Yeah.

**Other:** They would both need a mic. Yeah. Okay. But then how do we. There's no feature in the app right now. That hides it as, like, a single conversation. No, there isn't. I mean, just take a slight step back. Under this description of requirements, passing the microphone back and forth. It actually better. Right. Because it's functionally the same thing that they want. Like they want speakers with background noise. And so passing the mic back and forth will work.

**Me:** Low key, bro. That's what we're getting from fluffle anyway. Like, there is no background noise in, like, the diarized audio, like, type thing. I don't even know if they can create that, actually, like, because they only have, like, one wave output. Like, is what she was saying on call.

**Other:** Well, they're doing. So it is back and forth.

**Me:** Right, right. But, like, I don't think they're recording both ends of the phone call or, like. And if they are, they're, like, you know, quieting it.

**Other:** I think they are. I think they're calling through the app.

**Me:** With. Okay, then hopefully they can correct that later. They're like, they're, like, manipulating the audio to where it's a complete silence and, like, the. Yeah. Okay, cool. So, okay, so just to confirm, the feature requirement here is just one metadata tag that, like, links two pieces of audio together signify that it's the same conversation. That is like, that's it. We're not implementing anything else, correct?

**Other:** I don't. I don't know. What. I'm confused. On. Do we have to implement that? I'm confused why we would need that right now. We just have individuals uploading one side of conversations. Like, how do we know what to pair them with? But aren't they tagging them with the conversation ID right now?

**Me:** Nothing right now. Zero.

**Other:** I don't think there's conversation ID. Oh, there were. They said they were the fuffle people were.

**Me:** There is. There is no.

**Other:** But that's through.

**Me:** Technology, dude, but they're like. Yeah, it's like a weird thing.

**Other:** Yeah. They are. But not. I'm talking about the operating of the mobile app.

**Me:** Yeah.

**Other:** Yeah. So we don't have, like, any multi speaker support features. So that would be like a whole different thing that we'd have to figure out. But certainly could. I mean, I think the. In terms of the app experience, I think you just want people to pass the microphone around. And then in terms of how we, like, slice and dice the data. I imagine it's going to be buyer specific, but we have the power to do all the stuff we just talked about. Or none of it or some of it. Right.

**Me:** Am I. Wait. Okay. I thought we. Wait. So, like, the passing the mic back and forth, like, would only result in, like, one audio file. Right. But we only. We want to. Like, type thing.

**Other:** It's one initial audio file. But we could. Make two files.

**Me:** Not yet. But, like. Like when we make the two files, like, there's a period of Silence, though, when we chop that, like, type thing. And we don't want the silence. We want the background noise. So we want to audio files to be created. That is like the.

**Other:** Yeah, we can just make two. I mean, you're just describing two identical files then. Right? Because one's going to be background ones. You want the speakers in the background noise?

**Me:** No, no, no, no, no, no, no, no. Okay, so let's assume you're like, you know where you are. I'm where I am. Right type thing. You have your own point source. Like, you literally have a phone in your hand recording.

**Other:** Right. Oh, I see what you're saying. Okay.

**Me:** Because one of my hand recordings.

**Other:** So. Yeah, so if we wanted a speaker a file and a speaker B file. We could kind of just. I think we can just highlight the background noise. During, like, for one. We can identify the speakers using diarization. And then we can, like, mute their channel. In one file and then not in the other.

**Me:** Bro. I see you just clicked for me. You need to diarize it because we need timestamps and we need to match the timestamps across one another in order to automatically do it. I was thinking that the. The users are manually tag it, but honestly, it's way better if we automatically do it. So. Okay. Just to confirm start to finish. Okay. Just so we have it, like end 10. So you have, like, you and I are having a conversation. You have, like, your phone. I have my phone.

**Other:** Yeah.

**Me:** Right? Both of our files get individually uploaded. So now there's two uploads. Right. The. The system somehow, like, diarizes this to the point where we have timestamps on when the speaker is talking, when they stop talking. Right. And that then correlates to another piece of audio. There's two individual pieces of audio where that silence period correlates directly to another speaker talking. And now it gets automatized in the back end. There's, like, some visual, like, you know, cool stuff in the front end where, like, a reviewer like myself can then come in, be like, these are the two things. They're auto merged. Everything is good. Just to confirm.

**Other:** So we'd be diarrhea in the audio with two speakers or more. And then one file would have the same speaker. Muted every time. Not muted. But deafened. Softened.

**Me:** Yeah.

**Other:** Every time. And leave and background.

**Me:** Bro. Wait, Sydney, isn't that requirement kind of like they're like, dude, we want to, like, hear the background noise of the room, but we don't want to hear the other speaker talking.

**Other:** Always.

**Me:** Like, how do we. Wait, we can't just, like, stifle the other speaker talking. We just have to give these people instructions, right? Type thing.

**Other:** Get it. It's the same as, like. Like podcasts.

**Me:** But, like, I'm saying, like. Like, there's going to be background noise bleed in the room. Like, if I'm talking.

**Other:** No, I think they're trying to simulate if you're having a phone call. And you're, like, sitting here in the same room. That's where.

**Me:** Fine, fine, fine. Facts. I got you. I got you. Interesting.

**Other:** It is weird.

**Me:** To do that, bro. That's, like, hella tough, right? You're gonna do some, like, noise cancellation where you reverse phase on, like, a speaker. Like, how do you. How do you only remove the speakers? Like, voice and not the background noise?

**Other:** Yeah.

**Me:** That's an extremely tough problem to solve. No.

**Other:** Yeah.

**Me:** Like, that's not.

**Other:** Like, it'll be. It'll be like if it's. It doesn't even make sense.

**Me:** You could do a vocal remover, reverse the phase, then reduce the amplitude, and then. And then inject that in in order to do some airpods noise canceling, bro. Like, literally, that would be the elite setup. Okay? And they're do exist apis to do each individual step, but, like, still. Do we really need to do all that? Or, like, do we just tell these people to hold up their phone to their mouth? Right.

**Other:** Why do they want this? So I think phone calls, like customer service agents and stuff, like somewhere natural.

**Me:** Yeah, I think 11 labs right now sounds a bit robotic. They want more expressive, like, and, like, realistic sounding. They want an 11 labs to sound like a call center. You know, that's pretty much it. Yeah.

**Other:** Okay. But that's the back room. So I. Let's. Let's call it. Like, customer service agent and customer. So if you want. The primary voice audio for the customer. Do we want the customer? Let's go with the customer service agent. So if you want the primary. Voice audio for the service agent. You also want the background noise whether or not speaking. And so again, I think you would just want someone to have a conversation. And have them, like, constantly in their face. And then the file we would give them is just that they record on their phone. There's no reason to manipulate it. And so I think it's maybe not super complicated of a problem. Right. And then, likewise, if you want to do the same for the customer, it's the same thing. You just want them to record whatever they're doing, whatever they hear is whatever the microphone picks up. It'll be background noise. It'll be back there speaking whatever. But there's no reason to manipulate the audio. Because that would be the most accurate simulation. And so I do this on the app. It would just be like, hey, have this conversation. And you need a partner with the same app. And holding your own mic. Yeah.

**Me:** Facts. It'd be like a video. Call app type thing.

**Other:** Yeah. And then, like, we can match them up in the back end.

**Me:** Live. Yeah, always.

**Other:** But we wouldn't diarize them separately. We won't splice them. Like, it would just be two separate files. And they'd have background audio. And primary. Kind of for full frontal audio, so to speak. Like, the most ideal way to go about this, honestly, is import your contacts and you can, you know, invite someone like. Yeah. Text me like, hey, join me on the app, get paid for it, whatever. And you literally just call them through the app.

**Me:** Called through the app. Here's a. Link. Yeah.

**Other:** Yeah. I mean, they don't even need the other person doesn't even need the app. It's just like, hey, record a phone call with your buddy. And you don't have to record your end. Well, no, because you want both sides to be its own file. So you need both of them on the app. Probably we have to have both sides. Yeah. Okay. Yeah. Then we need both on the app. Sure. Yeah. So if we were to do something like that, how long would it take? If we were to add a for your contacts, have a phone call within the app? So just as an aside, I would press them to write the requirements down because there's still some unanswered questions, and I think we would build it incorrectly without getting a little more detail. But. To let me. I don't know what it's like to record phone calls on iOS. I mean, we don't need phone calls. We can just do voip. Right. And so it shouldn't be that bad. But I I don't. I don't know. I mean. Would we give them each a script? No conversation. Yeah. Like, hey, just having a phone call, me calling my friend, you know, we're talking about random things. Like, that's the. And then we got paid for it. Do they have to be in the app? I think so. It makes it easier because then we can just do what you said. We put contacts in, you start a call. And we record it. I don't think it'd be that bad. But let me.

**Me:** Are you thinking, like, recorded Google meet or something like patchy like that or something?

**Other:** Well, it's not a Google. It's like a Google meet.

**Me:** He's a third party, like, you know, calling service.

**Other:** Yeah. Yeah. I mean, what'd be voice over IP, right? So it'd be.

**Me:** Yeah, I'm trying to think. Yeah.

**Other:** It would be fine quality. It wouldn't be a big problem.

**Me:** We're basically just building fluffle internally.

**Other:** I don't know, but I'll take your word for it. Pluffle neon. All those apps.

**Me:** Yeah. Dude. Okay, fire. Okay.

**Other:** Okay. Well, let's see. Yeah. Do we know how long it's going to take? I mean. You just want to guess, like, a couple weeks, maybe a week or two. I don't know. I really don't know. But just to get anything kind of. Right takes. Takes that long. Right. But I don't know. It's not like a ton that we aren't already doing. Because we're already recording audio already uploading it. We already have interface and app store approved. So. Like, a lot of the hard bits are done. Yeah. I mean, if we wanted to, like, get designed and all that, I think, like, by the time VJ's done designing it. I could get, like, just some. Little bit of research done, which is just gluing. And then have it more accurate estimate. I don't think it'd be that bad. Honestly, like, if we keep it simple, I bet we could get it banged out. Like, in less than two weeks. I'm trying to think if there's any, like, additional back end components. There's really not.

**Me:** You just need a view IP SDK. Right? Like, is functional.

**Other:** What's that? I don't know what those.

**Me:** Voice over IP. Like, just.

**Other:** Oh, yeah, yeah. Oi bestie. Yeah, I'm sure that. I mean, the thing with voip, it's not so much the. The code you need. A hosting provider. Right? You need to get that. And, like, AWS GCS, they all. They'll have it.

**Me:** Yeah.

**Other:** Like, it's just a box, you know, a leopard switch you turn on.

**Me:** Gcp now, bro.

**Other:** I would assume so. I I haven't looked.

**Me:** They have good voice. I didn't know they had.

**Other:** But.

**Me:** Like, voiceover IP to them. They do. Never mind. I'm tripping.

**Other:** Nice. Cool. Yeah. Google. Offers several VoIP capabilities, Enterprise to business. Yeah, they got, like, a bunch.

**Me:** That's sick. Yeah. Nice.

**Other:** Of course. Yeah.

**Me:** Yeah. You need something like Osco's to act as a server, but you can do it. Yeah.

**Other:** Oh, dude, Google voice was the original.

**Me:** It's the OG. No, no, I know, but I didn't realize they had, like, the enterprise office.

**Other:** Yeah. You know, Google voice, that was the original voip.

**Me:** Yeah, no facts. Facts.

**Other:** Yeah. Yeah.

**Me:** Yeah.

**Other:** Do we have a in. Sorry. Go on. No, go ahead. Go ahead. Do you have an interface to create tasks? Yeah. Can you send it to me? Where is it? I think it's Osmet. Is there a way to also edit, like, the instructions that come before the task? I don't think so, but we could add that, too. I guess. Yeah. Right now, are we just doing with generic? Instructions? We do all that before all the tasks, or how do we tailor that to the task? Are we doing? I think the instructions just say speak clearly. Yeah, I think they're hard coded in the app. I see. Okay. Yeah, we should. And maybe the next release we definitely should change that. To, like, tailor to the task. Yeah, you should be able to add instructions. That'd be cool. So hold on. There's like. A couple things that are. Getting thrown around here. Let's. Let's get them all written down. So one second. Another thing on the task request side, I think we should. It'd be great if we could start figuring out, like, targeting, like pushing tasks to certain people. You know how we have that little carousel that cycles through, like, recommended tasks for you. So if we can actually tailor, like, push this to male 25 to 35, you know, stuff like that.

**Me:** I kind of wanted to ask, actually, on that, like, what. What type of metadata are we collecting on individuals right now?

**Other:** If you look at the profile, it's like it's location agender. Language and accents.

**Me:** Okay. That's pretty thorough. Yeah, folks.

**Other:** Do we. Is there a way for us to track device location?

**Me:** They'd have to consent, but. Yeah.

**Other:** Well, it depends. If we just want. We can get. We can derive course location from IP, which is limited to, like your city, your neighborhood kind of thing. And so that's all you want. Then we can get that without any ux stuff and we can just kind of, like, record it. That's, like, pretty easy. Okay. Because I'm almost thinking. So I definitely think we should push for, you know, import your contacts and everything to your phone call, because I think that actually help with network effects of the app as well. But I think the most immediate one we could do is actually the secondary or the regional languages in the different areas. So if we can actually map, like, device location and then also the language that they speak and we can start, like, doing tasks tailored to those. Yeah, the vpn will that up. But we just pretend that doesn't exist. The language thing and location, I think you'd get more noise than signal there. Like, if you speak. I mean, like brazilian, portuguese is the exception, but most languages, I think, of those, like, things people move around a lot. So I don't. I don't know how. How good that's going to be. You know, I'm saying, like, spanish different areas of latin america, like they, you know, they're all going to sound a little bit different.

**Me:** We can.

**Other:** Yeah. I just feel like if you say.

**Me:** From summary.

**Other:** You're. Yeah. And just because you are somewhere doesn't mean that's right.

**Me:** Effect. S. Yeah.

**Other:** You know? Yeah. Yeah. I think it's more so.

**Me:** Native birthplace. We should have, like, birds place, bro. Like birthplace. Like, you know type thing. That should be a metadata.

**Other:** Well, like their language, like they. Yeah. I mean, I think. Oh, they're the input their language, but I think. Right. But they said portuguese, but we don't know if it's brazilian, portuguese or european, portuguese. And if they're in brazil, then we think it's visiting portuguese and it probably is. But when it comes to.

**Me:** Four.

**Other:** Like, you know. Swiss from france or swiss from switzerland or germany from one of the, you know, it's like it's all over the place.

**Me:** You have.

**Other:** So. And, like, I don't even know how india works. I'm sure there's, like, a hundred different. Yeah.

**Me:** A bajillion dude. Yeah, literally.

**Other:** Yeah. And they, those people move around a lot, too, I'm sure. Right?

**Me:** I think the only thing we can collect reliably is birth location. And, like, native. Native tongue. Right. And then beyond that, we just infer. And with those two things, we could infer. Okay. You're, like, most likely a native speaker of this with this dialect that could potentially affect this. Obviously, the more tags we have on our data, the better it is and the more valuable it is, too.

**Other:** Yeah. Yeah. I mean, so collecting location is. Is good and collecting.

**Me:** So.

**Other:** Like, you know, what people say their language is definitely good. But I don't think, like, adding those two together is. Is right.

**Me:** I don't think so either. But I think, like, so the four points of data I'm saying that we need is, like, so birth location, because that then determines, like, okay, even if you have, like, a native language like English that could vary drastically. If you're born in india versus born in the state.

**Other:** I don't know. I think we should let people. We should have a drop down for native language, and there's expanded sets like that include brazilian, portuguese or swiss german or whatever.

**Me:** Drastically.

**Other:** And so.

**Me:** Fine finally accents and. Or something, like, you're, like,

**Other:** It's not so much an accent. It's just like, it is just like a different language almost. Dialect is maybe the word for it.

**Me:** Here's, like. Like, there's a crazy example, right? But, like, let's do. Okay.

**Other:** But.

**Me:** Like, let's like. You're from India. You speak English. Okay. That's your native tongue. Okay. And then you're from America. You speak English. That's your native tongue. You're gonna speak slightly differently already. Okay. Let's assume your mother tongue is English in both these cases, too. Okay. But, like, we're collecting Spanish speaking. Like, English native folks. Right. There's, like, kind of, like, tricky, but, like, it's like the Indian English-speaking native would speak Spanish differently. Than the American English-speaking native. Does that make sense?

**Other:** I know, but I think Sydney clarified this later. We're not actually trying to chase that thing. We're chasing the other thing where it's like there's different versions of every language. Yeah. Yeah. And so, like. The expanded, like, list of languages that I'm talking about, like british, english and american english would be different because, like, those are distinct enough. Whereas, like, I'm sure. I don't know if there'd be an indium drop down. Maybe they would choose british.

**Me:** Yeah. Yeah.

**Other:** Or, like, the packet. Like, I know. People from Hang kang, their englishes really sounds like they're from. Like, northern england. It's very strange.

**Me:** No, same. Do the same. Literally. No, exactly. Same. Like my parent.

**Other:** You ever met a Huang kinese person? It's like the. It's, like, kind of freaks you out. Yeah. Huk and he's weird.

**Me:** Sounds like a Charlie skit, bro. Hunkin. Jesus.

**Other:** I bet, like. Dude, I met, like, some people in japan. I was like, whoa. You sound way different than I thought you would.

**Me:** Yeah. Crazy. It's all that. No, it's all the VCs that pull up to these events, bro. Hello. How are you doing? Like, dude, what are you.

**Other:** But. Yeah. Yeah, yeah, yeah. That's funkanese. They sound like they're like the queen of the sound, like they're the queen of england, but they look like chinese.

**Me:** Going on here? Queen Elizabeth's like, bro, what are we. Are you Dr. Strange, bro? Like, Benedict Cumberbatch pulled up. Like, what's going on here?

**Other:** Yeah. Yeah. It's really weird.

**Me:** You know?

**Other:** It freaks you out. I was in japan, and there was, like, these, like, a bunch of chinese people. I'm like, how's the food? Like, it's amazing. I'm like, what?

**Me:** Yeah. Dude.

**Other:** Okay.

**Me:** No. And then they cuss at you after in their native tongue and immediately after, bro. Like, there's, like.

**Other:** Yeah, because they'll all speak like a. Like a chinese dialect, too.

**Me:** He had some secret and just flew in Chinese, and then they come back to you. Oh, yeah. Everything's. Everything's Stella. Like.

**Other:** Are there hunkines language? Too?

**Me:** I have it, dude. That's actually. There's no way that's legit. Honkin's. Hong Kong. And.

**Other:** How can these is weird?

**Me:** Is this, dude? Hong Kong can use actually a thing, bro. That's insane.

**Other:** No, no, they speak cantonese, but at least we cantons. But a lot of them speak english, too, because of the colonization or whatever.

**Me:** Damn, that's crazy.

**Other:** Okay.

**Me:** Okay, cool.

**Other:** So. All right, so hold on. Let's get back to writing down all the stuff we just decided to do.

**Me:** Yeah.

**Other:** So. Do we want to. Take a beat to think about the phone call thing or are we, like, super committed on that or what's our vibe?

**Me:** I do think two channels, like, definitely a valuable addition to have. Just, like, historically, that's the only thing that's paid out. And, like, also, like, that's where we're, like, finding demand. So there. There should be some way, at least at bare minimum, to match up speakers to one another through the API upload. At Max, we have, like, a native phone calling apps and learned a neon or fluffful. Sydney, what are your thoughts?

**Other:** Okay. Yeah, I agree with that. But I'm trying to think more just immediate term, like, literally tomorrow. What are the tasks?

**Me:** Yeah. Yeah. Like, I I think, like, the short. Yeah, like, given that we don't have this, like, functionality yet.

**Other:** Sure. So, yeah, let's. Let's break it down. So I believe prompt editing and prompt instruction.

**Me:** Like.

**Other:** We need to, like, boof those up a little bit. So you want to be able to provide when you. You're just able to create a prompt. You want to really create specific instructions that go along with the prompt. Sorry. Prompt is how I say task. Yeah. Because in our internal. Yeah, yeah, yeah. We say. We say the task is a prompt. What were the other kind of more immediate things? Like, so the prompt. Creation and editing, we need to improve ability to add prompt instructions ability to target. Specific individuals. Based on demos. And then maybe even, like, add in optional cap. So say we only want a thousand hours of this. Like we cap it. So once that's been fulfilled, like, we don't let people submit anymore. Got it. Yeah, that makes sense. Okay. Okay.

**Me:** On the. On the two channel stuff. Like, do we already have stuff written down for that? Or. I can. I can write down a couple reps for it.

**Other:** I think, yeah, if you. If one of you wants to write down how you think this feature can work, and then we can kind of return to it, maybe even tomorrow before we get, like, spec it out and get it underway. But I really don't think it'll be that bad, especially if, like.

**Me:** Maybe. I can. Yeah. Sydney, the other thing to keep in mind also, like, with, like, a two channel thing is, like, even if users start uploading audio, just, like, using the app right now, like. Like, as it is.

**Other:** Yeah. Anything is a way for someone to upload audio. You can only record natively in the app.

**Me:** Okay. Sorry, sorry. Well, we're coordinatively in the app. Even if they were to just do it, like, right now, just holding it up to their mouth. And we would still have access to both. Both audio channels, and we can dyarize that later so we can still have two channel audio tasks. Right?

**Other:** You can still. Yeah, you could still have, like, you and I have the app, like, and we're both doing it. We just don't have any way of matching it, which isn't because I think.

**Me:** It's not a limitation. Exactly. But we can. But we can retroactively do it is what I'm saying. So it's not an issue. Like, that shouldn't be a limiting factor. And I do think that that's probably one of the most important immediate tasks that we should post. If I'm not mistaken. Yeah. And then I think location is also an immediate priority. Right. Like, actually, like, locking in.

**Other:** Okay. So location, that's a. That's low hanging fruit. I want to do that.

**Me:** Yeah, 100. Like, low hanging fruit and, like, also, like, very, very important for the dialect feature.

**Other:** Do we just want to store the last location we got or just make. So do we want to store the location of the sample when it was recorded? Or, like, the last location or. Like.

**Me:** Nah, bro, what are people traveling? They'll get. I think. I think, like.

**Other:** Well, I know, but that's the thing is, like, which one's better, right? So if I record one sample in france and then I report another in germany, like, which, like, is the user from france or from germany? Like, what are we doing?

**Me:** We should have, like, a way for them to manually verify it. Like, they should actually, like,

**Other:** We do. We do. We have them. We have them enter location.

**Me:** Have. To.

**Other:** Yeah, we asked them.

**Me:** But, like. So what would the new feature be?

**Other:** It's just a.

**Me:** Wait, what was that? Sorry. You guys spoke at the same. Time?

**Other:** Like, verification.

**Me:** Oh.

**Other:** Okay, so let's just record the locations of the samples, and then we can know if it's recorded, like, way outside their comfort zone. Like, if they said they're from england and they're recording in japan, we'll be like, okay, like, maybe we need to listen to this. Yeah, exactly.

**Me:** What if I'm, like, vacationing in Bali, bro? Like.

**Other:** Then those are, like, edge cases that we're gonna have to, like. Yeah, that's fine. It's just like if.

**Me:** Okay, fine. Yeah. Yeah.

**Other:** They're. If we're getting samples from bali, but they said they're from england and then, like, they have a thick accent. Well, like, no. Like, okay, indonesian accent. Yeah. Whatever that sounds like.

**Me:** Yeah. What is an Indonesian accent, bro?

**Other:** Which. Oh, I've heard it.

**Me:** Actually.

**Other:** I just picture someone talking in my life fast.

**Me:** Just wrapping.

**Other:** Is that all Asian languages?

**Me:** Yeah, folks.

**Other:** Except for Huangkenese.

**Me:** Yeah, dude.

**Other:** Okay. Another low hang food I'm thinking of is right now. You know how we have that language selection drop down? Can we. Is there any way we can just add more specific dialects within that list?

**Me:** Yeah.

**Other:** Yeah, that's what I was saying earlier. Yeah.

**Me:** Yeah.

**Other:** And I don't think that would. Would that trigger, like, an app review, or is that something we could just, like, do because it's just a drop down? I don't know where we store our language list. It might be on our back end, in which case no. I just, like, don't know. But it might be hard coded in our front end, which would, again, be totally normal. And then it would trigger an app review, but, like, don't get hung up on the app review too bad. Like, it just. We're gonna be in review for the rest of our lives, like always. It's just kind of how it works. Tell me that. Yeah, it won't be as bad, though. It will not be as nightmarish. It's gonna be really smooth from now. On.

**Me:** Will some level of this be operational by next week? I'm going to something conference next week. I just want to, like, demo the app live to, like, a couple folks, you know, if possible.

**Other:** I mean, you can demo it now, but, like, will you have, like, a language dialects? Like, yeah, you don't need demo dialects by next week.

**Me:** What's that point? Yeah. Okay, cool. Cool, cool, cool. Right on.

**Other:** Yeah, we will add. We'll add expanded. Dialects. And I'll look for some standard list, and we'll start there. And if it's no good, we'll. I guess it comes out. Yeah. Could you. I guess the media action would be could you check if it's backend or frontend and if it'll trigger an app review? If not, you could just, like, change a list to be more specific. Let's just make that change prior to tomorrow.

**Me:** Fire.

**Other:** Oh, we have a need for tomorrow. Well, so tomorrow, the pr is going live, and then the ugc stuff kicks off Monday. Have you checked if we're in the app store yet? Yeah, I've downloaded it. Oh, you. You got it. I didn't. I couldn't get it.

**Me:** Yeah. I couldn't get it either, bro. I was scrolling down like max.

**Other:** No only download here.

**Me:** Wait, actually, yeah.

**Other:** No, I tried when I was on this call. Well, do you see it in the app store?

**Me:** I only see the, like, human fitness thing.

**Other:** No, it's really weird when I search the human API, like, get paid by AI shows up. That didn't show up like that showed up in the actual app didn't show up. But when I just search human API, the app shows up if you just, like, scroll.

**Me:** Oh, I got. Fire. D facts. Yeah, it is. Downloading. Second download.

**Other:** Dude, I see human API, and it's like a health and fitness, and it's got all this other weird crap in it. You gotta scroll more past, like, a bunch of.

**Me:** She looks clean, bro.

**Other:** The app looks good. Oh, there it is.

**Me:** This is fire.

**Other:** Oh, it's in the business category. Yeah.

**Me:** It's.

**Other:** So the previews look really good.

**Me:** Fire.

**Other:** These look sick, honestly.

**Me:** Dude, the onboarding. Everything looks hella good, actually. It's fire.

**Other:** No, no, that's. That's solid. It's nice. It's a nice. It's good. It's good to build on. Is the verification code up for you guys?

**Me:** Nah, I work. It hit me twice. It hit me twice for some reason. I don't know why.

**Other:** Yeah, I also hit me twice. But also when I went to fill it, it kept getting stuck on the second number, so it was like replacing the same number in the second one. So I've experienced that. Can you. Create an issue? You've probably taken for that. Yeah. Yeah.

**Me:** Okay. I'm gonna do something on this dialect thing, bro. I think there's a better way we can get this UI, like, going. But I do think there's some level of.

**Other:** Well, I think the. Yeah, if we can just, like, put. If it's just a back end thing, that's not going to trigger a new. Let me. Let me check right now. Okay.

**Me:** Like. What are. You? Doing? Okay, so, like, you have native here, right? Let's assume there's, like, okay, like non dude. Stupid. Let me do something. Like, what if you had an option for, like, secondary native? And then, like, if you. If you click secondary native and then, like, gives you another drop down being like, okay, where are you actually from?

**Other:** So, yeah, it's. The languages are hard coded. Oh, they're hard coded. Yeah. I mean, we'll. We'll change that. But, yeah, it won't. It'll trigger an app review. It will, you said.

**Me:** All right. People.

**Other:** Yeah, it'll have to go through review to change the languages. What we can change that later. But that's the case, then let's just do in the more ideal way, because I was trying to. I was hoping it'd be like a quicker thing of Adenie and app review that we could just, like, you know, change the list in the back. But if it's gonna. It's hard coded, it's gonna trigger review. Let's actually do language, and then maybe ask them more specifically, like dialects once they've selected that language. That's like a sub drop down. Does that make sense? Yeah. Yeah. So, like, for me, if I put, like, mandarin native and then because I put mandarin, it'll be like, okay, what's your dialogue? I'm pushing high knees. And then, you know, whatever else. Yeah. I mean, I think the way most apps do it is they just have in the list of languages, like they include, like the dialects as well. Because for. For a lot of languages, there are no people don't select a dialect for whatever reason. Mandarin. Also, mandarin shang kinese, mandarin or like what? Is that the. I go choose both. Yeah. And you would see, like. Like for you ever seen, like, english, uk, english honkines, english. Like, that's, like, pretty common. For, like, that's what i've seen at least is, like, they have, like, like six versions of english. And, like, for, like, the lesser spoken languages. They won't include any dialect at all because there's, like, too many and then of speakers or whatever. So we could do that. I guess. Yeah.

**Me:** Yo, there's a couple housekeeping things on the app, dude. Just like. Like, literally, like, UI bugs. And where do I make tickets? Would that just be auto boomer?

**Other:** Just the same place. Yeah, the same place you've been making them. Auto boomer is the thing that fixes tickets.

**Me:** Oh, okay.

**Other:** But you just make them in github. You can do slash github.

**Me:** Fire. Yeah.

**Other:** Create in slack, and just make an issue, and then you can even tag boomer to fix it, and that's fine.

**Me:** Okay. Yo, dude, like, by the way, I think. I think language editing works. Right?

**Other:** You know, it works.

**Me:** Oh, I thought you said. Okay. I thought you're saying it was, like, hardcoded or, like. Like, permanent or something.

**Other:** No, no, no. When you're onboarding, that drop down list of languages.

**Me:** Got it. Got it. Got it. Gotta go. Okay.

**Other:** Yeah, that's. That's just like that. It's statically coded in the code, and so I can't change it without reviewing the app. Which makes sense. Because. Yeah, I mean, it's not like an error. It's just. It's one of the. One of the things.

**Me:** Tough to integrate with, by the way. Like plaid definitely has more bank accounts integrated with the rate than stripe. Or am I tripping?

**Other:** You could go through stripe. I don't know.

**Me:** Oh, okay. Fire. And then also Aden, like, is a payment processor for, like, International. So that would be useful.

**Other:** Add a stripe offerings to local currency, or they have the ability to. No.

**Me:** Oh, okay. Never mind. I think Aden's cheaper. I'll, like, type it in. But. Yeah.

**Other:** I think the most immediate thing right now. So the press release tomorrow. I care less about because I actually don't think that's where most of the app downloads are going to come from. It's the ugc program kicking off on monday. I think that's where we're going to see, like, an influx of users, hopefully. So it's like, what task do we want to be? Do we want to have an app for them?

**Me:** Yeah. These are probably, like, the initial brain rot customers in, like, the states, bro, are probably going to be our initial right folks. And that's, like, typically English conversational. So we should focus on two-way and then just single channel output.

**Other:** Well, I don't know if we can get two way done by next Monday, though.

**Me:** Well, no, no, that's what I'm saying. Like, I feel like even with the current, like. Like app build, like, we can still get two-way uploaded. That shouldn't be our blocker, like, is what I'm saying. That was my argument earlier, which is like, they could still do it, and then we retroactively fix, like, you know, everything because Daniel's saying, yo, we can diarize this, right? Diarrhea is everything that's been uploaded. Right. And then timestamp this. And if the timestamps of Silence match up to the timestamps of someone else talking, then that's automatic. Like, we can match this up retroactively. So I don't think the two-way we should be limited by, because that's also what's paying us out the most.

**Other:** I see what you're saying.

**Me:** Yeah.

**Other:** Yeah, I guess, Daniel, what do you. Is there. Are there any checks that we could get between, like, now and next Monday that could help us, like, match the conversation? So it's, like, less backend. So we're not, like, retroactively. Fixing everything. Well. So when you say match the conversation, you're talking about. Like, what exactly? Because we only have. One speaker, one. I don't understand what you're. Yeah, I guess we change something, like, pretty. Pretty significant in the profile or something. Yeah.

**Me:** Friends, like a friend's, you know, leaderboard or whatever the.

**Other:** And then how do you, like, make that connection?

**Me:** And then you, like, you start a call with your friends in the app or whatever the. So it basically just be rebuilding me on.

**Other:** Yeah, I'm thinking. For, since we do have this lead that we can pull on of the regional dialects as well, I think even with the stuff tomorrow, if we do get some app downloads and we can start tracking better metadata around, like, dialects and whatnot, we can start, like, pushing some of those tasks. While we work on the conversational stuff.

**Me:** The surround.

**Other:** Okay.

**Me:** What's a wattassy prioritizing? Sorry.

**Other:** The regional dialects.

**Me:** Okay.

**Other:** So maybe we're just, like, in. This is something that probably have to clarify more with trovio, even if it's like they want conversational data in those languages, or is it like, oh, we just want.

**Me:** Yeah.

**Other:** Like, we want, like, scripts read in those languages or those accents.

**Me:** Makes sense. Okay. Solid. Solid. Cooled. Yo, can we also start tapping on Neil's Network? Maybe, like, to get intro to some of these founders. That's, like, probably, like, warm mentors are probably gonna, like, actually start working. I'll put together a list of folks that I think would be useful.

**Other:** Yeah.

**Me:** To, like, tap on shoulder.

**Other:** I think we should just start tapping way on more now that he doesn't have ties to marco.

**Me:** Wait, is he chill with us now? Like, can we, like, actually leverage him? Okay. Fire sick. Okay.

**Other:** Well, but, like, he's, like, doing it for free.

**Me:** Okay. Oh, it's like. It's like, Neil, we can actually tap on rayon, like, sparing. Okay, fine.

**Other:** Yeah. Yeah.

**Me:** Cool.

**Other:** Okay, so immediately, Daniel, if you could just remove the test task. So when the pr goes out tomorrow, we're not. You know, people are not seeing, like, the rough, rough task and hoping to get paid out for it. That's priority number one. And then if there's, like, some kind of. If you could link me the interface that we have for task creation, that way Adya and I could just, like, do it ourselves without, you know, looping you in every time. And then Adya, I think you're putting together something about the converse stuff.

**Me:** I'll send it in, like, end Channel right now.

**Other:** Okay. Yeah. Does that sound like a plan? So just immediate is remove the test task and get you the task creation dashboard. Okay, here, hold on. Let me make sure that. Remove test task. Creation UI dialogues to. Yeah, you could just write it all down. Select device location. Or contacts. Holy. Okay. Am I missing anything? So I've removed test task, send task creation UI. Add dialogues to language selection. Collect device location and then purity for importing contacts and calling.

**Me:** I wrote the prd to not eng. Ine. There's anything other than that. Oh, Daniel, I kind of want to get your thoughts, man. Like, maybe scoping out, like, a potential, like the. The physical AI. Obviously, there's, like, a. Maybe, like, you know, month timeline thing, like month down the line. But, like, would that be a very high lift, like, activity just to kind of start thinking.

**Other:** Well. To, to think about it.

**Me:** Functionality into the app?

**Other:** What functionality, physical functionality.

**Me:** LiDAR. LiDAR functionality, like on the AR kit, like on iPhone.

**Other:** Like for verification.

**Me:** No, no, no. Like, for, like. I mean, that too, actually, but, like, no, like, for, like, actually scanning objects using lidar. Is that, like, a possible. Or is that non-trivial.

**Other:** I don't. Know. Wait, wait. I don't know.

**Me:** Okay, fair enough.

**Other:** Yeah, we can look into it. Yeah.

**Me:** Cool. Dude.

**Other:** And then, Daniel, I think you have the list of stuff we talked about for task creation. Right. What do you want me to write that down as well? Yeah, I can write that down, too. That'd be great. Sorry, the internal dashboard is redirecting it. It's just some authentication. Okay, so it says instructions. Targeting. Base targeting users. And then cap them. Okay. I think that's it. So tomorrow with the press release going out, we just are going to have, like, no tasks in the task marketplace. And I think that's fine because I'd rather not pay out for things that we don't need. That just to, like, have something there. But we should get something in place by next Monday. So, yeah, we need to figure out what that is, what that looks like.

**Me:** Is it going to be auto QA from now on, given, like, the influx of, like, you know, folks. Starting next week, or is it, like, still, like, you know, semi-manual semi, like, Auto?

**Other:** You mean for the actual audio quality?

**Me:** No, like, yeah, the review process, like, to actually, like, pay out, or is it just going to be complete auto payout? Okay, I'm going to have a fun week next week then, bro.

**Other:** Yeah. I mean, it's up to us, really. Right?

**Me:** Yeah.

**Other:** Here. We don't have a task yet, so there's not.

**Me:** That's. Okay, cool. Sounds good. I'm just going to save myself by vibe coating that I'm joking. Screw that. Okay, cool. Sounds good.

**Other:** Okay. Yeah. Daniel, could you just confirm whenever the test task is deleted? Because if there are any issues with it, I'll make sure. I'll see if I can, like, stop PR or something, because I think that's just a bad look if you have, like, the test task still in the school now. Yeah. Yeah.

**Me:** How long does an app review take at this point now that we're published?

**Other:** Still takes two days, but it, we will get far less rejections. Sorry. I should say up to two days. I think in reality, it's much faster.

**Me:** Dude, have you heard of these, like, services that, like, they're like, you know, super cheap and they push your app in, like, two hours to the App Store. How does that even work? Like, literally. Like, if.

**Other:** I would assume they have an approved app with that's a web client. And so you're allowed to do, like, basically like a website, and then they, they, like, you have, like, a, you remember, like, around with cordova or ionic, you know what those are.

**Me:** Like, okay. That's like what disc, like electron, like, where you, like, transfer JS to a local desktop app? Where am I tripping?

**Other:** It's similar to that. But basically, like, yeah, you ship them js and then they hot load it into, like, some shitty app they have.

**Me:** Yeah. Oh, low-key there's, like, ox that do this where you can install, like, okay, YouTube, for example, locally or whatever. The.

**Other:** So it's like a, it's like a spec before apps. Yeah. Yeah.

**Me:** Back.

**Other:** Except, like, there's no, like, nobody makes any money. Okay. Sounds good. Yeah. Daniel's keep me updated on if we run to any issues with a test task. But, yeah, let's just be. I mean, are you gonna send. Me the list of things? It's in her chat with the three of us. Oh, it's in this task. Okay, cool.

**Me:** I still got, like, two to dos to Sydney. I got O trivio. Like the. The dock or whatever updated QA, and then I'll get you also a doc with, like, revised version of this Excel that actually makes sense type thing.

**Other:** I think, yeah, trovio, by the way, is like shopping around. I think they have, like, four conversations going on right now, so hopefully one of them closes.

**Me:** Super thick. Are we just, dude, we. We're just going to become trovia's go-to data broker, which I'm, like, totally chill with. Like, that's like fire.

**Other:** I also, by the way, I'm, I think I'm gonna sign another, like, 1500 to 2,000 hours of podcast data.

**Me:** But.

**Other:** This week.

**Me:** Oh, stick, man. Holy. Okay, super sick. Licensing?

**Other:** Yeah.

**Me:** How did that. Okay, I will have, like, a longer form convo.

**Other:** Oh, I think it was just because I did a bunch of podcasts, so obviously in the podcast, you're pitching them and they were interested.

**Me:** On that. Oh, okay. Okay. It's a hobie. Homie discount. Okay. Got you. I, like, bro, no way, dude. Teach me your ways, bro. That's like sorcery, dude. Fire. Okay, sick. Sounds like a plan. Okay, I'll update you on slack with those docs later today. Then.

**Other:** Okay. Sounds good. All right, thanks, guys.

**Me:** Cool. All righty. Peace out, dudes.
