---
source: granola
workspace: eclipse
ingested_at: '2026-05-05T02:07:56.333013Z'
ingest_version: 1
content_hash: blake3:17e3caaf6436f37703a4da4969b392eeddeac11cf491aab71170dc1c37b958a8
provider_modified_at: '2026-04-13T18:24:10.416Z'
account: adithya@outerscope.xyz
account_slug: adithya-outerscope
document_id: 83fc0030-32bf-4d2b-a3c6-34d14661c584
document_id_short: 83fc0030
title: 'Adi/Veronica: Catch Up'
created_at: '2026-04-13T18:01:49.666Z'
updated_at: '2026-04-13T18:24:10.416Z'
folders:
- id: 84a8f86d-16f6-4529-a4b3-11a687032b07
  title: ECLIPSE
creator:
  name: Adithya
  email: adithya@outerscope.xyz
attendees:
- name: null
  email: veronica@fluffle.world
calendar_event:
  title: 'Adi/Veronica: Catch Up'
  start: '2026-04-13T13:00:00-05:00'
  end: '2026-04-13T13:30:00-05:00'
  url: https://www.google.com/calendar/event?eid=MHQ5MjByZGVqY3RlcGQ4a21wcnIzdDQyN2sgYWRpdGh5YUBlY2xpcHNlLmJ1aWxkZXJz
  conferencing_url: https://meet.google.com/shf-vrsy-eqd
  conferencing_type: Google Meet
transcript_segment_count: 291
duration_ms: 1313242
valid_meeting: true
was_trashed: null
routed_by:
- workspace: eclipse
  rule: folder:ECLIPSE
---

# Adi/Veronica: Catch Up

> 2026-04-13T18:01:49.666Z · duration 21m 53s · 2 attendees

## Attendees

- **Adithya** (creator) <adithya@outerscope.xyz>
- ? <veronica@fluffle.world>

## Calendar Event

- Title: Adi/Veronica: Catch Up
- Start: 2026-04-13T13:00:00-05:00
- End: 2026-04-13T13:30:00-05:00
- URL: https://www.google.com/calendar/event?eid=MHQ5MjByZGVqY3RlcGQ4a21wcnIzdDQyN2sgYWRpdGh5YUBlY2xpcHNlLmJ1aWxkZXJz
- Conferencing: Google Meet https://meet.google.com/shf-vrsy-eqd

## AI Notes

### Audio Quality & Technical Solutions

- Current compression issues from phone hardcoded compression in Daily’s WebRTC SDK

    - No compression happening on Fluffle’s end - issue is device-level
    - Need native WAV files for Outerscope’s buyer requirements
- Potential workarounds discussed:

    1. Native app development (both companies exploring)
    2. White-labeled front-end solution using Outerscope’s recording capabilities
    3. Custom web framework deployment
- Fluffle’s constraint: consent capture built into current app (critical for partners)
- Outerscope willing to dispatch Daniel to collaborate on technical solution

### Market Opportunities & Data Catalog

- Fluffle has 10,000+ hours available across 100+ languages

    - 5,000 hours English ready off-the-shelf
    - Most content is non-native speakers (valuable for Outerscope)
    - Arabic samples available (confirmed buyer demand)
    - Strong coverage: Indian languages, African dialects, Portuguese, French
- Current deal opportunity: compressed audio acceptable at different rate

    - Deadline: April 17th for conversational deal
    - Outerscope exploring audio cleanup/normalization as workaround
- Technical specs: 48kHz, 16-bit sample rate

### Next Steps

- Adithya: Discuss white-label solution with Sydney and technical approach with Daniel
- Veronica: Send Arabic audio sample via Telegram
- Both: Schedule follow-up in ~1 week after technical consultation
- Adithya: Investigate metadata display issue (age, gender, location data should be available)
- Explore bulk data transfer for immediate deal if audio cleanup proves viable

---

Chat with meeting transcript: [https://notes.granola.ai/t/fe76c1c4-e94b-4d9c-a647-d8aeed634da7](https://notes.granola.ai/t/fe76c1c4-e94b-4d9c-a647-d8aeed634da7)

## Transcript

**Other:** Hey Ady, sorry I just saw your messages.

**Me:** Hey, no worries, Veronica. How's it going?

**Other:** I'm good. How are you?

**Me:** Doing well. Doing well. Yeah. So I just want to just schedule some time, you know, just to get things figured out, like with the audio quality stuff. I mean, you guys probably, like, you know, one of our most major providers, so just want to make sure we get this workflow figured out type thing. So just to confirm, I wanted to, you know, first ask you, like, how were the audios, like, actually being recorded? Are they, like, basically like a phone call that's essentially getting, you know, transcribed or something or, like, just downloaded in a way? Like, how does the export process actually occur?

**Other:** Yeah, so the way we're recording, I think you know that we work with daily. So we rely on their web RTC.

**Me:** Yeah.

**Other:** SDK to be able to record the calls. What happens on their end is that they record it. And then they send it to us. There is no compression that's being done at any point from that perspective. I will say though, I think I have kind of an understanding of where the compression is happening, which is what we've been trying to figure out. It is because the devices have hard coded compression on phone calls that truly like we've checked with daily, we've tracked all of our settings. I do truly, truly believe it's just phone hard code right now.

**Me:** Okay. Got you. Okay. Is there a way to circumvent that? Just like. Because I think in order to, like, start paying out, like, we basically need, like, some form of wav file audio natively. And so, like, we've, like, internally also, we kind of struggled with this because in order to do this, you need a native app, right? You need to, like, basically, like, get folks to go offline, like, not like web type thing. There are ways, I think, of, like, maybe, you know, some Frameworks that Daniel was telling me about that allows you to record wav files natively on web. I can actually get him to join this call, too, maybe if, like, that would be helpful.

**Other:** Sure. I haven't seen Daniel in so long. Please.

**Me:** Okay, sure, sure. Okay, let me ping him really quick. Let me see if I can get someone from end to see what's up.

**Other:** Yeah. We're also trying to see if there's a way to do it natively. It's not something that I'm not sure if it's something that will have figured out like today. Truth be told except if Daniel has some sort of like magic fix that we can.

**Me:** No. Yeah. This dude always has magic fixes, dude. Just whips off, like, literally Wizard of all out of his back pocket. Like, dude, damn crazy.

**Other:** That's manual for you. Yeah, we don't have anything right now. I guess my question for you. I have a couple questions. I guess.

**Me:** Yeah, yeah, yeah, totally. Yeah.

**Other:** Long term will probably be able to get you something that is native with zero compression. Are you seeing demand potentially from partners? Because we've had kind of we've had partners reach out with the fact that they're okay that there's background noise. Is there. Have you seen that potentially? And of course, right, I know that the rate wouldn't apply, but we do have it on standby if you are interested in that.

**Me:** No, no, totally. That would actually be, like, the. That would be, like, very valuable for us, actually. So we want background noise matter of fact. So, like, the reason entire reason we're, like, trying to, like, get around this compression thing is because there isn't background noise right now audio. So there's, like, some level of, like, natural dampening that I think, as you mentioned, is probably hard coded in the way that the audio is being captured. But basically, like, I'll work with daniel. I don't know if you replied yet ping them, but in case he doesn't hop on, I'll work with them as well to see if there's any way to, like, maybe vibe code a web app or something, right, that we can maybe deploy custom for you guys to be, like, a custom endpoint, right type thing. Or as a temporary workaround, like, given that you guys already have contributors and stuff, I honestly don't know how this would work, right? Because, like, obviously you guys also want to, like, silo your contributor Network. I totally get that stuff, too. But, like, we have, like, native audio capabilities already, like, built into boomy. So I don't know, like, how willing you'd be, like, to, like, oh, dude.

**Other:** Yeah.

**Me:** Like, because, like, I feel like that's kind of cannibalizing your users in a way, right? Like, I don't want to do that at the same time. Like, like, we get you paid out way quicker if, like, they would, they would have just, you know, maybe use our, like, software in a way while it, you know, you maintaining your contributor Network and, like, you know, Independence, all that. Good.

**Other:** I think the one thing that we have that, you know. Is very core to our product is the fact that we have consent built into the app.

**Me:** Yeah. Yeah.

**Other:** And so. The issue with moving to web app. Would be. That that may not be the case. Right? Like we capture that before and after every call because it is important for our partners. Let me think about it. Let me think about how we could do that. Yeah.

**Me:** Because, like, my limitation, like, internally, like, I'm like, you know, obviously, like, you guys are contributing a ton of, and, like, it's, it's very beneficial to us, but, like, my limitation is, like, our end buyer is going to us up basically at the end.

**Other:** For sure. Yeah.

**Me:** Right? We pay out and then, like, don't get paid at the end. It screws us type thing. Right. And so that's just kind of what I'm trying to hedge against, like, we've kind of already gotten, like, some, like, pushback on, you know, like, some of the more, like, compressed samples, I think. Historically, that we've said not just, you know, to say.

**Other:** Yeah. Question. So I have a question and I understand. I think I fully, I get where you're coming from. Curious. If given that there's some compression, curious to see if it may not be the same buyer. Right, of course. But if you have.

**Me:** Yeah, there's another buyer that we can pay out of custom rate for totally get you. Yeah. No, 100. Like, and that's, we're still open to that, too. It's like, it's just our current buyer has, like, super strict requirements and whatnot. But he was also proposing sort of more of like a licensing agreement type thing where we just have this audio, like, on deck. Right. We have a couple samples already from you guys that we'd start sending out, and we just act as, like, your go-to-market team in a way. Right. Because, like, I, I've been traveling a ton. Like, I'm, like, getting contact just, like, GTC human X, a couple of these conferences. Right. And so hopefully, like, if we close Partners there and, like, you know, your audio is applicable there, then I think that could be a temporary workaround. But for the immediate deal, if there is a way that we can get, like, you know, less compressed audio and whatnot, like, that would be super killer. Like, the way right now that they're operating is through a phone app, or is it like a web app just to confirm?

**Other:** The phone app.

**Me:** Got you phone app that uses web RTC. Okay. Got you. Dang. This is complex.

**Other:** Yeah, so you can download it because Sydney has an Android. If you have an Android, you can also download it. We're live on the Play Store.

**Me:** Yeah. Emulator. Yeah. Play around with it for sure. Not 100. I think she was showing me, like, you know, some of the features and functionality. So not 100. I.

**Other:** I'm trying to think.

**Me:** Yeah, dude, because it's like.

**Other:** How long, how long did it take you to vibe coat the boomi website? Because maybe we have a temporary workaround to start getting our users paid out. We build a website, we add consent. In.

**Me:** Wait, dude, what if we were to, like, white label a front end for you guys, lowkey, you know, this type thing? And, like, it uses art. It uses our where, like, just auto uploads because anyways, like, you guys are uploading to our API. We just go to front end for you guys and, you know, ship it out to your users and bang. We're good.

**Other:** Like that could be a workaround as whilst we figure. Yeah, once we figure this. Yeah, yeah, yeah. And I'm not concerned about that. I think, I think the market's big enough. Let me think.

**Me:** Temporarily, of course. Yeah. Yeah. We don't want this. But.

**Other:** I could think about that.

**Me:** Totally, totally, dude. Yeah.

**Other:** I think. So we're pushing out a couple additional features. Question for you. Okay.

**Me:** Yeah.

**Other:** So. I kind of understand how the boomy side of things works. From like the super initial boomi website, right? Because I remember that you'd upload your files and that was it. Can you now record on the website? How does it work if we're both talking? Do you have some sort of like communication channel or what's the workflow current users?

**Me:** We can definitely incorporate that, actually. And we're in the process of, like, sort of building that out, like, internally. Like, where right now the workflow is, you just kind of onboard and then you record whatever voice prompts that we give you. So it's, like, kind of like teleprompter situation. And, like, we, you know, like, silently users based on, like, a basic onboarding process that tells us more about really dialect, all that good stuff QA process. But right now, yeah, it's just that it's like an app that you just talk into teleprompter style. What we're building out right now is combo stuff, too, where it's like a diarrhea speaker is like, okay, like matching this to this, like, Etc. And so it's like more of like a UI. So, like, that could actually be, like, you know, given the fact that Daniel's building that out right now, we could very easily white label that and then just have that be one of the. You know.

**Other:** I think our whole thing is that it's two way conversations, right? Which is also what you're looking for and not the teleprompting stuff. I'm trying to think. And currently your users do it through a web app. Can they do it through the phone as well?

**Me:** Phone app, actually. Yeah, phone app. Needed. Yeah. Yeah.

**Other:** Phon app as in. Like listed app or a web like phone web like through the browser or is it an actual app?

**Me:** It's, it's an actual app, like on the App Store. All that good stuff. Yeah.

**Other:** Okay, I'm trying to think. So.

**Me:** But we can make it into, like, a front end, dude, or something. Like, you know, like, like what? Like, your users are already native to an app. That's the issue. Like, because it's like pushing.

**Other:** I guess I have a couple questions for you then. Okay. Because this might be helpful for me because you guys already have a phone app and you're reporting natively. Can you help me understand how you're doing it?

**Me:** Yeah. Oh, like, like the actual functionality, like how.

**Other:** Yeah, because if you can help me understand the functionality and it doesn't seem to be that hard, we could potentially also do it.

**Me:** You guys can just.

**Other:** Yeah. And then everything will be fine.

**Me:** Yeah. Yeah. Facts, dude. We could honestly have Daniel maybe work internally with your guys Engineers to see if we can, like, you know, I don't. I like, I'm talking to Sydney right after this, like, you know, I'll definitely, like, propose, like, all these stuff.

**Other:** Yeah, yeah. Because I think we're working on that internally right now, but if there's a way to ship it quickly, technically, maybe we could do it fast and get that sorted out for you. Because like right now we have an egregious amount of data. And you guys only want english data from us. We have a couple other brokers that are looking for other languages. But if you were interested in it, we do have it on standby. We have coverage in about like 100 languages right now.

**Me:** Bro. What? Oh, wait. Okay. Damn, that's crazy. Wait.

**Other:** Yeah. So.

**Me:** Specifically, like, just so I, like, have, like, a mental note. If you have a list of, I'll take a look.

**Other:** Most of our users. Yeah, most of our users are in emerging markets. I can tell you that English, of course, is the primary, given that, you know, we have.

**Me:** At Haitian anything Arabic. Gulf.

**Other:** Yeah, yeah. Arabic we have.

**Me:** Bro. I have buyers for that left and right. Honestly.

**Other:** Yeah, everybody's looking for Arabic right now. We could work something together. It will be a little bit compressed.

**Me:** Yeah. Yeah. Totally.

**Other:** If you're okay with that, I tell you, let me send you an Arab example. Actually, let me write this out.

**Me:** Yeah. Okay, sick, dude. 100. Yeah.

**Other:** Do you have a specific preference on what type of Arabic? Because brokers are a little bit delusional in the sense that they want MSA, but nobody actually speaks MSA.

**Me:** What is that?

**Other:** Modern standard Arabic.

**Me:** Oh, okay, okay, okay, okay.

**Other:** But nobody actually speaks of essays. So like.

**Me:** Yeah.

**Other:** Like we have tons of dialects, but some burgers have. Told us they want the transcripts and the MSA, but like, bro, that's not the actual language it's in, but.

**Me:** Yeah. Dude, these Brokers are low-key like, just like frat Bros, dude. Like. Like, swear to God, dude. Like, dude, we're getting briefs that are just totally. Like, I'm just like, are you, like, do you even know your own data, bro? Do you even know what your buyer's buying? Like, literally type thing.

**Other:** Yeah, somebody recently asked me for something absolutely unhinged. They were like, we need Japanese content with transcription, but the transcripts have to be done in the dialect.

**Me:** Dude. Go, like, scrape anime, bro. Like, what do you. What are you talking about?

**Other:** Literally. And they're like, we will know if it's not from the correct dialect.

**Me:** That's insane, dude. Jesus.

**Other:** Then. Yeah. So I said no to that basically. Like this is just not possible.

**Me:** Like, yeah. Don't collect all the infinity stones for me and come back. Like, what are you talking about, bro? Like.

**Other:** Yeah. Literally. And then this broker was like, I don't want to give you a rating.

**Me:** Bro. Exactly, dude. Exactly. And it's like, yeah, they like strong arm you into, too, because they're like, oh, yeah, bro. Like, we can pay out, like, way after, like, literally right after we can travel. I'm like, dude, you, man. Like, we said.

**Other:** Yeah. That's literally how I feel. Honestly.

**Me:** Though, dude, like, literally all these, you know, I feel like.

**Other:** Yeah, they're crazy. They're actually crazy, but okay, wait, so let me take a look at the catalog real quick.

**Me:** Yeah, yeah, please. Yeah, 100. If you have any. So if you have any, like, secondary speakers as well, that's massively valuable to us, too, as in, like, you know, so native Spanish speakers talking in English, for example, etc. Etc. Like, some of those secondary markets, like, those would be super.

**Other:** So, okay. So I think that's something that you have to derive from our English set and where they're from. I feel like you'd easily be able to derive that.

**Me:** Okay. You guys have that chance, or is that, like, you know, unlabeled right now, like, unstructured?

**Other:** It's unstructured in the sense that we haven't done second. Yeah, we, we haven't labeled that specifically. If you have any specific needs also. So English is big, Indian languages. And gala with Togalu, Marathi, Hindi. We have a lot of that. We have a lot of African dialects as well. African language dialogue. So trying to think Arabic, we have a bunch as well.

**Me:** Yeah. Yeah.

**Other:** Portuguese, we have a bunch. Everything split, Brazilian, Portuguese, normal native Portuguese. We have a lot of French as well.

**Me:** Nice. Nice.

**Other:** Trying to see. So yeah, if any of this is interesting for you, just let me know. I can get you.

**Me:** Arabic sure. I know we have a buyer. And then, like, the other geos, I don't know if anyone's actively looking right now, to be fair, because, like, I think 11 has, like, a super robust, like, movement for those 11s basically leading, like, sort of all text to speech right now. From research standpoint. So I think they have everything covered except for Arabic, according to the guy, like I spoke to this conference.

**Other:** They want a lot of Indian.

**Me:** Really?

**Other:** If you want to push. Yeah. Somebody told me that they're secretly that hindi Indian languages also they're looking for just because India is the biggest market.

**Me:** Oh, yeah, it makes sense, bro. There's two billion of us damn near now, dude. We're like a quarter of the world population is ridiculous.

**Other:** Yeah. So like I'm just being primarily building product. I've been having passive conversations, but like, I know they're looking for that as well. I'll send you an Arabic sample. How about this?

**Me:** Okay. Yeah, yeah, totally.

**Other:** I'll start with that.

**Me:** Yeah. And then. Yeah. So I'll chat with Daniel and then, like, Sydney now, too. So Sydney, I'll propose, like, the idea, too. Okay, maybe we can white label something for them or maybe just dispatch Daniel. You know, it's like a temporary thing.

**Other:** Yeah. Or not even dispatch forget some color. Right. I think we can build it ourselves. If, if it's not crazy, like if it's not crazy, we could probably build something ourselves.

**Me:** Yeah. Just having, like, hop on a call. Yeah. Yeah. At this point, people are vibe coding IBM, dude. We could vibe code this 100.

**Other:** Yeah. Yeah. Honestly, like I've put it a bunch of stuff. We have real engineers who can also do it, I guess.

**Me:** Yeah.

**Other:** But, like, we, we still have a lot of users who are actively still recording conversations. So we can definitely test something with them. We'll be launching a bunch of new features in the next week or so as well.

**Me:** Totally. Nice. Yeah. Yeah. Yeah. I feel like we're pretty much building the same thing, dude, in a way, right? Like, I think.

**Other:** In some way, I think you guys are building more of a marketplace though, honestly.

**Me:** Yeah, exactly. Like, we're, like, less, like, vertical specific, I think, compared to guys. But, yeah, it's more. We're just starting out with voice because that's where the money is and, like, you know, folks are.

**Other:** Yeah. We're actually like branching off to more of a consumer app more than anything. So I think, yeah. So I think we're, we're currently focused on the same vertical, but, but like the product will be very different.

**Me:** Oh. Nice. Yeah, we're branching out to physical robotics AI right now type of thing. So disparity.

**Other:** Yeah, yeah. So I'm definitely not doing that. Like we're going into like more of a social app model.

**Me:** Yeah. But also, dude, I feel like the same thing could be said for, like, everyone in this space, bro. Like, 11 Labs, Vappy, deep gram. Like, what's the difference? Like, you know, type exactly. I asked a lot of these guys, like, literally at the conference, like, a lot of these sales dudes, they're like, oh, like, we've been at the company for a month, bro. Like, dude, what? Like, why did they send you here, man? It's a four thousand dollar ticket, bro.

**Other:** Yeah, yeah, yeah. Literally.

**Me:** Like, dude. And they're like, yeah, we focus on the Enterprise Market and the Enterprise in the case. Like, dude, what? Like, that's your one vertical moat, bro. Like, it's like, Jesus Christ, dude.

**Other:** Yeah.

**Me:** Like.

**Other:** Like we're, we're building like more of a social app, which is like we'll have discord, we'll have banners for our users.

**Me:** Yeah. Totally, totally. Fair. Yeah, yeah, yeah. No, the classic user loops and. Dude.

**Other:** Yeah, yeah, we'll have all of that.

**Me:** You keep beer. Yeah. Nikita beer playbook, right? Literally. Yeah.

**Other:** Basically, we'll have that LBQ. I'll finally get to add profile, like fun profile banners for all of our users.

**Me:** Yeah. It is. There it is. That's when you know you made it as an app, bro. And you start focusing on consumer features. It's over. Yes, sir.

**Other:** Like literally like, I'm deeply focused on consumer features. So yeah, don't worry. I don't think there's much that much of an overlap between us. Cyndy will laugh because she knows about our initial product, which I think had a lot of consumer futures and I selfishly just walk consumer features for a user.

**Me:** No, no, no, no. 100.

**Other:** Like we're, we're letting our users pick ringtones.

**Me:** Then. Was. Okay. Okay. Dude. Yeah, not totally. Totally fair. Right on.

**Other:** Very soon.

**Me:** Well, sick. Okay, right on. I think I have my to dos outlined. I'll get back to you, like what Sydney says, and then also what Daniel says, too. And then in the meantime, I'll also, like, get back to you on the Arabic stuff as well. Yeah.

**Other:** Okay. Yeah, I'll. Have a sample, so I'll just message it to you after this call.

**Me:** Okay.

**Other:** Yeah. And then yeah, if let me know what Daniel, I think that would be really helpful. If not like we're building something internally, it just might take a little bit. If we have some sort of banding solution, we, we can get you all your samples, like whenever you want.

**Me:** Right on. Yeah. Okay, perfect. Dude. Sounds like a plan.

**Other:** And oh, on, on the metadata front, right, I think you said that you wanted to know if a user is a second, like second tongue, non native speaker. Is there anything else that you think would be interesting?

**Me:** And I'll. Be it, honestly. And, like, we actually have a way of figuring that out now internally, too, where we're diarrhea both. And, like, so basically, like, you know, the area of Silence, if that matches up with, like, another audio file, we're able to pair that internally out, too, so. And then maybe if you feel like you have other types of metadata and, like, user type, user geo user region, all that good stuff, that would be massively valuable. So any types of, like, data tags you have.

**Other:** Okay. I think you're getting that from us already.

**Me:** Oh, okay. Okay. Like, we get YouTube.

**Other:** So you get agender location for me already. I think accent, whatever we turn the crown, the upload back on.

**Me:** What if we do that? I'm not getting that, like, displayed on my ends. I'll talk to Daniel on that.

**Other:** Oh yeah, so you should be getting age, gender location for sure.

**Me:** What? Okay.

**Other:** And then technically, I'm not sure because I think some things weren't being sent over initially. Or maybe you're looking at data that's really, really old, but it should like, I think the like V1 should have agender location for sure. You may just not be getting language and access yet.

**Me:** Got you. Then Daniel probably is, like, just not implementing that in, like, the front end. I'll talk to him, like, because we're getting that data. It'd be tremendously valuable to display.

**Other:** Yeah, you should have all of that already for me.

**Me:** Sick. Okay. Cool, dude. Okay, right on. Oh, let's. Let's plan to sink maybe in, like, about a week or so. I'll, like. Like, send a really good tentative invite. Maybe, like, early next. Time.

**Other:** Yeah, that works for me. And yeah, I think top of mind is probably give me some color from Daniel so that we can see if we can hash something out.

**Me:** Yeah. Yeah.

**Other:** For our current users. And then, yeah, I will say if you speak to anybody who's looking for something that may be slightly compressed, I understand the rate may not be the same. I'm definitely a little bit flexible on that. If you have anybody that wants what we've sent you already and truth be told, we, we stopped it. So we actually have a lot more. Like, I probably have like, like over 10,000 hours of shit.

**Me:** Oh, bro, dude. We literally have conversational deal running right now, man. Like, literally, like, if we had all these files by, like, the 17th to be golden, let me do one thing. I'll, like, send, like, a sample of the compressed thing. What I'm gonna do, bro, low-key is like, I might just try, like. Like cleaning up the audio. Like, as a normalizing it, you know, using, like, a.

**Other:** Like we have it. We have.

**Me:** What do you call it? Like, audio remover thingy or whatever. Just some of the background noise and let's see if the buyer takes that. And if they do, then maybe you and I can work out the process where, like, okay, like, we can spin up some, like, temporary tool to just, like, you know, clean up the audio and. And just, like, process because we not stupid on this deal, dude. Like, they're paying, like, really well, so. And if you have.

**Other:** For sure. Yeah. Yeah. And we can, yeah, we can figure something out at scale. Right. I think I have, I have about, I think 10,000 hours of English. I have to check the quality, but at least like OTS, we probably have like 5,000 hours.

**Me:** Already. Yeah. Okay. OTS. What do you mean? Sorry.

**Other:** Yeah. So like it's already there.

**Me:** Oh, okay.

**Other:** Like it's off the, it's off the shelf already.

**Me:** What is OTF stand for, man? Am I like, I'm off the shelf of Jesus Christ.

**Other:** Like off the shelf. So like we have it in our servers. Technically, like if you want it, if you have a deal happy to come in and help.

**Me:** Perfect.

**Other:** Take a cup would be great. We'll get our users paid out to kind of get the engine going. I will say that most of it is non native as well that I can tell you. Most of it is non native. Technically, you should be able to see location. So, yeah, let me know. Just, just message me.

**Me:** Okay. Yeah. Okay. Easy, dude. Okay, let's see if we can get something worked out on that deal. That'd be fire. If we can just clean it up and send it over, like, it's golden. Yeah, 100.

**Other:** Yeah, yeah. And like technically we built like a normalization tool. But given that we turned it off the anything that's been normalized.

**Me:** 0. Oh, okay. Okay. Okay. Okay. Got it. Got it. Got it. Got it. Okay.

**Other:** But like we can work together. If you have something like I will just give you the bulk of our data and if you want to normalize it, like we'll figure it.

**Me:** Yeah.

**Other:** Out.

**Me:** 100. 100. If you can give me two things, the sample rate and also bit rate, that would be massively valuable. So.

**Other:** Yeah. The sample rate on the actual file is a sample array. What's, it's what it used to be 48 khz 16.

**Me:** 40, 48, 16 bit, like, default.

**Other:** Bit. No, whatever the initial sample rate you gave me.

**Me:** Yeah. Cool, cool. Okay. All righty. Let me get back to you via telegram. Then I'll stay in touch via throughout today. Once I have updates.

**Other:** Sounds good. Thank you. Bye.

**Me:** Thanks for the time. See you.
