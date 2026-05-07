---
source: granola
workspace: sei
ingested_at: '2026-05-07T04:23:57.244510Z'
ingest_version: 1
content_hash: blake3:5b18916fc4f4a3313e9931c07896ead98266aa6d106eadefd9a935a6ee53426a
provider_modified_at: '2026-01-21T21:30:55.603Z'
account: adithya@outerscope.xyz
account_slug: adithya-outerscope
document_id: 1c8fb3b2-d896-449f-a730-cbea26e884b7
document_id_short: 1c8fb3b2
title: Adi x Cody | Alpha Trade Vibecoded Waitlist Sync
created_at: '2026-01-21T21:30:54.837Z'
updated_at: '2026-01-21T21:30:55.603Z'
folders:
- id: 3ca3cb55-d6e1-49ef-961a-8ba2469731a5
  title: SEI
creator:
  name: Adithya
  email: adithya@outerscope.xyz
attendees:
- name: null
  email: cody@seinetwork.io
calendar_event:
  title: Adi x Cody | Alpha Trade Vibecoded Waitlist Sync
  start: '2026-01-21T15:30:00-06:00'
  end: '2026-01-21T16:00:00-06:00'
  url: https://www.google.com/calendar/event?eid=M2Q2MmF2ZDgxMWQyMWhmZnBsbWtvODdla3QgYWRpdGh5YUBzZWluZXR3b3JrLmlv
  conferencing_url: https://meet.google.com/dbz-beoj-mqv
  conferencing_type: Google Meet
transcript_segment_count: 337
duration_ms: 3895088
valid_meeting: null
was_trashed: null
routed_by:
- workspace: sei
  rule: folder:SEI
---

# Adi x Cody | Alpha Trade Vibecoded Waitlist Sync

> 2026-01-21T21:30:54.837Z · duration 64m 55s · 2 attendees

## Attendees

- **Adithya** (creator) <adithya@outerscope.xyz>
- <cody@seinetwork.io>

## Calendar Event

- Title: Adi x Cody | Alpha Trade Vibecoded Waitlist Sync
- Start: 2026-01-21T15:30:00-06:00
- End: 2026-01-21T16:00:00-06:00
- URL: https://www.google.com/calendar/event?eid=M2Q2MmF2ZDgxMWQyMWhmZnBsbWtvODdla3QgYWRpdGh5YUBzZWluZXR3b3JrLmlv
- Conferencing: Google Meet https://meet.google.com/dbz-beoj-mqv

## AI Notes

### Alpha Trade Demo Review

- Built functional waitlist landing page with Supabase backend

    - Live database tracking sign-ups in real-time
    - Google sheet integration for waitlist management
    - Position tracking (showed #6 in queue)
- Development process

    - Used Cursor with Opus 4.5 on Max mode
    - Gemini-to-Claude prompt chaining technique for better results
    - Total build time: couple hours (would’ve been faster without Supabase integration issues)
- Fully modular codebase - logo/design changes take ~1 minute

### Copy and Design Updates Needed

- Minor copy refinements required on landing page
- Xander handling logo productization (replacing current placeholder)
- Domain switch needed - alpha trade domain was taken, new one reserved
- Cody to provide Figma comments with specific edits

### Technical Implementation

- Deployment successful and functional
- Easy to modify - demonstrated live edits capability
- Can hook up to reserved domain tomorrow
- Ready for launch early next week pending refinements

### Team Coordination Planning

- Need to establish communication flow with design/shipping teams
- Xander and Brian currently overloaded with launch pad project for Foundation
- Will determine handoff process tomorrow after refinements complete

### Action Items

- Adithya: Complete Glass project contact list within 1 hour

    - Target roles: Head of Engineering, Head of AI/ML Platform, Head of Product
    - Add 1-2 people per company where possible
- Cody: Provide Figma comments on Alpha Trade landing page
- Tomorrow: Refine waitlist page, determine team handoff process
- Future: 30-minute vibe coding tutorial session

---

Chat with meeting transcript: [https://notes.granola.ai/t/7fd5c492-f76a-4047-80e9-70fdd297b690](https://notes.granola.ai/t/7fd5c492-f76a-4047-80e9-70fdd297b690)

## Transcript

**Other:** Get me back. When we got ap. Art. That's just. How we go. Steady making. But I don't. Want to love just. To say alone. We're trying to find. My demons. Baby, don't. Let go. I'm waking. Up. Kayla. 's already know. I'm picking up. Next scene. If you still feel me, I. Used to go. Remember me? Stand point. When you know that I. 'm in. I guess it's. What things you say. Really what you. Mean? All your. Friends we wanted me, but. They can be yours. I really love you. Baby. This time I ain't Cheetah, but promise if you cross me. All I'm saying is keep a duck, do the best. Be my any thought she won't do the things she in a fair. Time. Where you go. Stick through faces. To the ceiling. I got fighted though. Hoodie, red feet, she be tripping. On a seat along the. Sun. Give me love. She didn't want. To keep me. I'm Dr. Y. Even though I'm. Always trying to. Find. She gonna get me back? When we better. Fuck. That's just how it's gonna stead. Y make enough. But I don't. Want to love just. To say hello. Yo.

**Me:** Hey, cody. How's it going?

**Other:** Good. How are you?

**Me:** Doing well. Doing well.

**Other:** Nice. Yeah. So I want to use this time to get, like, a demo of what you cook yesterday.

**Me:** Nice.

**Other:** Kind of see where we're at with it.

**Me:** Cool.

**Other:** But. Yeah, in the meantime, when we hang up here. And let's still try and get those things to cheat that by end of day, too. I know you're still cooking on some of those.

**Me:** Yeah. So this is basically like, I'm trying to pull, like, a couple of folks manually from each company that we've found, either on the product side or lead engineering pretty much. So this is just like sort of a continuing work on that list. I should have that list probably ready within the hour, though.

**Other:** Cool. We can run through. Your demo.

**Me:** Yeah, let's do it.

**Other:** And then. Back to that.

**Me:** I should have it deployed by now.

**Other:** Cool. And, yeah, talk to me, like, how that process was, like, what you used. I'm genuinely curious also, of, like, how you spun that up. How you like deploy it. Et cetera, et cetera.

**Me:** It is deployed. I think if you click that link. It should be working. Is it working for you?

**Other:** Yeah.

**Me:** The animation sucks, dude. I tried to get it to be, like, slightly better, but I will get it better on V2.

**Other:** So alpha trade. Trade stocks with leverage. Join the waitlist for early access to equity perps. So 561, is there, like, an actual DB in the background? Like, tracking them? Like, if we were to go live with this, or is it still very high key?

**Me:** It already works. I'm about to give you access to a sheet that actually tracks it.

**Other:** Reserve your spot. You're in position number six.

**Me:** Yeah. And then try putting in, like, another number, pretty much.

**Other:** Five, six, one.

**Me:** And then if you type your original number and it'll reserve your spot. But anyways, there's, like a live DB on Supabase that works right now. That essentially tracks everything live.

**Other:** Sick and let me pull up. Do you have that doc that we had for that one pager?

**Me:** Let me check.

**Other:** Let's see. I have it somewhere. Yeah, I think there's, like, minor copy refinements we can make, but, no, this is, like, a solid first step. And then, yeah, we have, like, Xander. He can replace, like. The other question, too, is, like. Okay, you vibe coded this. Did you use cursor or Claude?

**Me:** Both, actually. So I used Opus 4.5 on Max mode in cursor.

**Other:** Nice. And so how editable is it? Like, say we draft a new logo, right? And Xander cooks a new logo, and we want to just, like, add that, but not change anything else. Can you, like, plug in a new logo?

**Me:** Fully modulated, like a matter of a minute. Yeah.

**Other:** Nice. Dude, at some point, like, I. I was getting into, like, I was using lovable and some shit. Like, when was it earlier this year or. I guess, like, early 25.

**Me:** Y. Eah.

**Other:** And we were trying to actually get some vibe coding platforms on sei. Justin and I were, like, investing in a couple teams. They were all shit, if I'm being honest. And then I just kind of neglected it the second half of the year at the most important time when it, like, ramped up. And so I need to get back on my bullshit here.

**Me:** Yeah. Dude. I think honestly like over lovable or anything else. If you describe the right prompt to open and what I've like found has been like tremendously valuable is you prompt Gemini, right? In order to come up with a prompt. In order to prompt opus type thing. So because like an AI knows how to best to prompt another AI, you essentially use that to your advantage.

**Other:** Same. Gemini, write me a prompt to build this, and then you copy that over and put it in Claude. Holy shit. All right.

**Me:** Yeah. Exactly. Exactly.

**Other:** Fucking love that.

**Me:** But cool dude. Yeah, but I mean, so that's that. It works fully functional on Supabase too. So we have access to like the lab sign up sheet that is also live tracked on a Google sheet that'll give you access to.

**Other:** Cool. I'm going to probably make a couple, like, copy requests on it.

**Me:** Happy to. Yeah.

**Other:** We also reserved a domain. Already, so we can hook it up to a domain, like, later today if we want.

**Me:** Five.

**Other:** Realistically, probably tomorrow.

**Me:** Okay?

**Other:** But let's see. Sorry. Where. Where was that, doc? Do you have it, by any chance?

**Me:** Oh, dude, sorry. I was looking for that. Then let's try. Let me try.

**Other:** Ok? Ay.

**Me:** It was named One Page or something, right?

**Other:** I think I can go to my docs. I just have too many tabs open, so I'm trying to find it.

**Me:** Sorry. I'm trying to find it on my end. Too. Product. Oh, equity perps, Waitlist. Right.

**Other:** Yep. Boom.

**Me:** Got it. Okay.

**Other:** Yeah, I got it, too. Okay. That's helpful.

**Me:** Oandar's on it, actually, I think, yeah.

**Other:** Nice because, yeah, I have Xander working on actually, like, productizing this logo. I told you, like, obviously, don't spend too much time. Making a meticulous logo.

**Me:** Right. Yeah.

**Other:** Especially this splooche logo that you cooked.

**Me:** That's ridiculous. Yeah.

**Other:** Crazy. Okay? So I'm trying to think. Yeah, low lift. So, yeah, I'll actually go through. And just do like some copy edits on it. Like today again, like the glass stuff will take priority. But like as you have time tomorrow morning slash early afternoon.

**Me:** Y.

**Other:** Feel free to jump in there.

**Me:** Eah.

**Other:** Don't spend any more time on the logo, let you know. Xander handle that. It's what we pay him for.

**Me:** Yeah.

**Other:** And, yeah, we could probably get something like this live, like, early next week.

**Me:** I'm. Yeah, I'm super down, dude. Honestly, what would be, like, the best way to communicate with sort of the design team and then, like, shipping team as well, just to get my code over? If that'd be helpful.

**Other:** That's a good question. Let's figure that out tomorrow. Let's, like, refine it a little bit. It's a great first stab. I just have Xander and Brian working on, like, a ton of other shit right now. And so if I throw this on their lap also, they're going to be like, yo, chill. They're doing, like, this launch pad thing that foundation wants.

**Me:** Yeah.

**Other:** So, side question. But no, this. This is solid stuff. And at some point. Next week or the week after, I'm going to have you show me how you vibe. Code and give me a. Give me like a 30 minute lesson.

**Me:** Yeah. Definitely down. Definitely down, dude.

**Other:** Yeah.

**Me:** 100.

**Other:** Cool. Let me see. Let me pull it up one more time. All right. How long did it take you to do something like this? Curious.

**Me:** Like, probably a couple hours to it. Honestly, not nothing. More like the only major. It would have taken way less. Honestly, it was just super bass just giving me trouble with, like, integrations.

**Other:** Cool.

**Me:** Do you think it, like, fulfilled all the requirements, though? Like, I'm happy to make, you know, edits as you see fit, honestly.

**Other:** Yeah, that's where I want to just, like, jump off. And go through it a little bit, I guess. Here. I'm trying to get back to. Yeah, the beginning page. Okay, so. Yeah, we'll call it Alpha Trade. You know, we'll do like another one liner. Join the waitlist for early access to equity perps. This next one. Reserve your spot. Looks good. Yeah. You're in position six. Like, really, like, it does not need to be rocket science, it's just stopping. We'll want to, like, change the domain, given we have, like, a new domain now. So alpha trade was taken. Little things, but. Let me take two screenshots of these. Drop them in a figma. And I'll just put some comments on it and it's no rush at all. Like it's a tomorrow thing, honestly.

**Me:** Yeah.

**Other:** Let's focus on glass the rest of the afternoon here.

**Me:** Yeah.

**Other:** And get Chatham, you know, some stuff to make progress on. But, yeah, tomorrow we can reach out to glass and refine this a bit. And by end of day, I think we make decent progress on both.

**Me:** Okay? Fire. Okay, sounds like a plan.

**Other:** Nice man. All right, cool. I'll let you go. Keep me posted on if you like. I know there's a ton of different names and stuff. In the deck. Here, let me pull up this, too, real quick. But. Yeah. As you have a chance today. I know we talked about earlier, but. Yeah, just Adam here. If there's two. If, like, there's more than one, you know, just add them in the same thing. It's totally fine. We'll try and find, like, the number one person to target there. And then, yeah, I think we're in a good spot.

**Me:** Nice.

**Other:** But, yeah, let's definitely, like, try and get that to Chai Thin by realistically, like, the next hour or so, just because we chatted with them a couple hours ago.

**Me:** Y. Eah, great. Easily. And then like, is it okay if I just put one person from product? One person from, like, the technical side, I guess. From the contacts I find or.

**Other:** Yeah, we're try. That would be a question to ask him. Maybe in the chat, like, what are the two biggest weighted roles you'd want to talk to? It sounds like head of Engineering.

**Me:** Yeah.

**Other:** It sounds like head of Al AIML platform. If they're big enough to have one of those, some of these won't be. And then the se. If they're big enough again, some of these won't have that. So, yeah, my guess as head of engineering, it sounds like head of product is like a future call.

**Me:** Yeah.

**Other:** But I think those three archetypes.

**Me:** Okay? Perfect. Okay. Okay. I'll get that done and then over to you guys probably within the next hour.

**Other:** All right. Keep me posted. If you don't have blockers and we can, you know, jump back on, my afternoon is pretty free now.

**Me:** Perfect. Okay.

**Other:** Cool. See you, man. Thanks for the work.

**Me:** Ready.

**Other:** If I know it's released when you slip. How. Many times? How many times have we been here before? That's why some mess you'll come back for more but you need it best why don't you just close the door and put it to rest? Wish you all the best. You want it? It's 4am now. You call in. You. Started smoking and drinking right after we parted. Told. Me. You wanted the sky, now you fall in. Usually. I'm tempted, but let's just agree to be honest. But. There's a price to the things that. You crave. It'll be wise if you. Look the other way. You know he kills you. But you want it anyway. How many times? How many times have we been here before? Space and bus, you come back for more. But you need it, that's why, don't you? Just close. The boys to. Us. Wish you all the best. How many times? How many times have we been here before? We spend a lot of time figuring out what are we going to do if we lose communication with Earth, which is a very real possibility. Probably won't happen, but it's. Right. At cameraman. You can see my face, right? Yeah. Awesome. And big smile. My name is Kinjun, and I run Imbue. We build AI systems that can reason so that they can help us accomplish much bigger goals in the world. I've always believed that technology can liberate people. If I were born in 1900, as a woman, I'd be spending all my time preparing food. If I were born in 1900, as a woman, I'd be spending all my time preparing food and stoking fires to cook it and mending clothing. Because we have the refrigerator and the loom and the dishwasher and all these technologies, I'm free. Well, actually, the modern day is not that different from the 1900s. Back then, we didn't have machines. MIT basically solved unlimited context windows, and you can apply this to any model. This is called recursive language models, and it's just another example of how scaffolding building out infrastructure around the core intelligence of the model still has so much room to grow. Let me tell you about this paper because it is kind of incredible. We study allowing large language models to process arbitrarily long prompts through the lens of inference, time scaling. And let me just show you the high level results and I'm going to give you all of the details. So over here you're seeing GPT5 and it's not using the technique, and what you see is that for needle in the haystack it works really well, but then for oolong and oolong pairs, it rapidly declines in quality as the context length increases and basically goes to zero right around 262k. However, with our new recursive language model strategy, we can see the quality stays pretty consistent over time, even up to 1 million tokens. And when I tell you the technique that they discovered, it's going to be so obvious, and you're going to ask yourself, okay, how do we not think of this before? All right, let's take a step back for a moment. Modern language models have this thing called the context window. When you submit a prompt, you can't just put anything and everything into it. There is a limit on the input size. That is called the contacts window. And what typically happens is the more information you put into that context window, the harder time the model has. Finding things and kind of making connections within that context window, within that prompt that you just gave it. And this is called context rot, and it's a big problem. And going back up here, that's basically what we're seeing. And I'm going to explain what Naystack is. I'm going to explain what oolong is. Just stick with me. And so these MIT researchers ask themselves, can we drastically increase the size of the context window without actually changing the core model? Can we make a context window a million tokens? We're about 10 million. This is going to be especially important for long horizon tasks for searching over millions of documents for giant code bases. Having a large context window is incredibly important now. One general and increasingly popular inference time approach in this space is context condensation or compaction. Basically, what a lot of model providers and a lot of service providers do is they look at the context window and once it starts to reach the limit of what the context window can be, they start to compact it. They basically use an LLM to summarize what's in the context window, shrink it down. But that is lost blind fixes. Then you do that again and again. Eventually you're just going to lose details and you're not going to have the full story anymore. Essentially, that's what happens with compaction. And now we play with the proposing because it is so obvious in retrospect infrastructure around the core intelligence infrastructure around the core intelligence.

**Me:** Shaq, I'm leaving. My key here. Thank you. Thank you. Yo. Do you know where Zobear left the monitors? Okay? They're chilling. It smells like maple candle. Okay. Dude, I swear to God, every time I walk. Buy his room. I'm like, how many eating fucking pancakes? It was just a candle. Yeah. Crazy Bathroom body works. No, I don't think it was. His girlfriend gave it to him. Oh. Man. Working. At. Easy. Oh. My God. Bro. This. I'm so. High. It's. As dirty as. Did. I clean it. D. Ude. Look at this. Str. Aight up, black. Shit. In the. Ball. Jesus. That. Shit's going into. The. Quint. Smoking for? A while. After I. Like, finish. I. Have one. One and. A half. I'm. Pretty sure. Do you have? Fun. What? I have. One and a half. Left. Okay? I have a. Gram. How many tubs you said exactly? Yeah, not. For good. I'm just going to take a break. We'll see. There. May be a. Week or so. Maybe. A few months. We'll see. The valley and effort. I'm just. Being honest. Bro. I'm just telling you. My dreams. Hard to. Quit. On, God. This. Shit's cooked.
