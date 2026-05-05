---
source: granola
workspace: eclipse
ingested_at: '2026-05-05T02:07:56.333013Z'
ingest_version: 1
content_hash: blake3:43933f0de6ea96e86f85c3c0519bd718caa0290ec4ed9d6d614aa79b7bd59bfd
provider_modified_at: '2025-11-20T17:32:11.905Z'
account: adithya@outerscope.xyz
account_slug: adithya-outerscope
document_id: 0f72b1be-938b-402c-acd8-f79844cd8239
document_id_short: 0f72b1be
title: Ecosystem Daily
created_at: '2025-11-20T16:31:02.705Z'
updated_at: '2025-11-20T17:32:11.905Z'
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
  email: chinghua@eclipse.builders
- name: null
  email: adi@eclipse.builders
- name: null
  email: vedant@eclipse.builders
calendar_event:
  title: Ecosystem Daily
  start: '2025-11-20T08:30:00-08:00'
  end: '2025-11-20T09:00:00-08:00'
  url: https://www.google.com/calendar/event?eid=ZjRkZnY0M2M1YWJzdWJkamp0cXA1dTFuNWpfMjAyNTExMjBUMTYzMDAwWiBhZGl0aHlhQG91dGVyc2NvcGUueHl6
  conferencing_url: https://meet.google.com/kmp-jmdk-rut
  conferencing_type: Google Meet
transcript_segment_count: 1902
duration_ms: 7315979
valid_meeting: true
was_trashed: null
routed_by:
- workspace: eclipse
  rule: folder:ECLIPSE
---

# Ecosystem Daily

> 2025-11-20T16:31:02.705Z · duration 121m 55s · 8 attendees

## Attendees

- **Adithya** (creator) <adithya@outerscope.xyz>
- ? <cemal@eclipse.builders>
- ? <julien@eclipse.builders>
- ? <daniel@eclipse.builders>
- ? <sydney@eclipse.builders>
- ? <chinghua@eclipse.builders>
- ? <adi@eclipse.builders>
- ? <vedant@eclipse.builders>

## Calendar Event

- Title: Ecosystem Daily
- Start: 2025-11-20T08:30:00-08:00
- End: 2025-11-20T09:00:00-08:00
- URL: https://www.google.com/calendar/event?eid=ZjRkZnY0M2M1YWJzdWJkamp0cXA1dTFuNWpfMjAyNTExMjBUMTYzMDAwWiBhZGl0aHlhQG91dGVyc2NvcGUueHl6
- Conferencing: Google Meet https://meet.google.com/kmp-jmdk-rut

## AI Notes

### Rayhan Connection & Market Intelligence

- Rayhan from Scale mentioned connection to Outerscope team

    - Knows head of GTM at Cursor (has history with them)
    - Connected to friends from UT Turing Scholars Program
- Scale’s targeting parameters

    - Only takes contracts from labs with 9-figure budgets ($100M+)
    - Contracts likely 8-figures comfortable range
    - Won’t compete for smaller tier companies
- Potential partnership opportunities

    - Can make intros to 11 Labs and Cartesia
    - Willing to help with market research on what AI labs want
    - Could leverage Scale’s distribution for long tail data assets

### Development Progress Updates

- Daniel’s focus areas

    - Hiring data scientist with Sydney
    - Clerk authentication system ready for merge
    - Landing page development starting

    - Using Framer with custom components
    - Clerk integration working
- Chinghua’s backend progress

    - Merged multiple PRs for upload flow
    - Refactored database types and shared package functionality
    - Added worker/task endpoints to TaskCore
    - Object storage PR ready (waiting on review)
    - Integration tests in progress

### Infrastructure & User Management

- RPC URL updates completed for existing users
- Triton shared info transition plan

    - Standard shared info list received (not DAs)
    - Users include ABK Labs, Metaplex, Rarible
    - Decision: Provide free RPC access to all existing users
- Payment system completion

    - Stripe integration nearly finished
    - User withdrawal functionality final task

### Notification System Strategy

- Twilio pricing analysis by country

    - US: Cheapest option (optimized for marketing)
    - High-cost countries identified:

    - Armenia: $0.25/text
    - Egypt: $0.40/text
    - India: Expensive, WhatsApp preferred
- Implementation approach

    - Start with low-cost, no-paperwork countries
    - iMessage for US iOS users
    - WhatsApp for international users ($0.04/message)
    - Selective waitlist releases based on phone numbers

### UX/UI Design Direction

- Visual design philosophy

    - Dark mode with glass morphism (Apple style)
    - Minimal gradients (5% effects, 95% canvas)
    - Retro vibes but welcoming aesthetic
- App clip functionality questions

    - Half-screen recording interface desired
    - Voice memo-like UX for familiarity
    - Microphone selection for quality
    - Subtle navigation icons (home/profile)

### Gamification & Quality System

- Real-time scoring system (3 metrics)

    - Clarity: Audio quality/crispness
    - Speech: Reduced filler words, natural delivery
    - Emotion: Contextual appropriateness (for relevant tasks)
- Badge system implementation

    - Elite badges for 4.5+ scores
    - 1.1x pay multipliers for badge holders
    - Progress bars showing badge completion
    - Tutorial content for improvement
- Task discovery interface

    - TikTok/Instagram Reels style scrolling
    - Swipe right to start recording
    - “For You” curated vs general list view

### Next Steps

- Adithya: Send research doc with questions to Rayhan via shared Slack
- Vedant: Consolidate design questions list for team review
- Team: Daily async updates in Slack (no standup tomorrow)
- Sydney: Review Rayhan partnership doc from Adithya

---

Chat with meeting transcript: [https://notes.granola.ai/d/0f72b1be-938b-402c-acd8-f79844cd8239](https://notes.granola.ai/d/0f72b1be-938b-402c-acd8-f79844cd8239)

## Transcript

**Other:** Where it says local, you can click that and it works your cloud. You can make a cloud one. The cloud ones are a little bit more involved to set up, and I don't think. Oh, cool. Yeah. Especially I get, like, if I have a PR I could put up, and then maybe the tests are formatting. It's messed up or something like that. I'll have a work tree working on that while I work on the next thing. Yeah, that's interesting. The only thing is when if you open up a work tree and you want to use a specific branch, you have to tell it that or you have to make it uses that make your switches to that branch. Because there's two nuance one, when you switch to a work tree, it keeps your working tree in the work tree that it makes. So it doesn't make like a fresh branch, so to speak. Like, let's say whatever you have in your working directory, it copies the work tree. So you have to make sure it gets rid of that. And then it's going to make its own branch. It won't just be automated or anything like that. It's going to make its own branch for the work tree. And so you have to be like, hey, switch, switch to main. Or if you want to have a fresh branch off my. You do, like, switch back to main and branch off or whatever. Or you have to do that yourself. But I'll usually just put it in, like, a prompt. Cool. That's really the only thing. Though. Yeah, the new model, the cursor one. It's so fast. Yeah, I'm trying to start using more. It's pretty good. And the speed is crazy. It changes the whole workflow. It's no longer prompt, and go get lunch. It's like, oh, you're done? Yeah. I'm dipping a donut. Wow, that's looks delicious. Can I get a bite of that? That's not great. It's a tim hortons. Donut. What, are you in Canada? Yeah. I don't know. It's random. Is that like a smaller donut or is that regular size and you're. That's a regular sized dota. I just have a giant donuts. They're like life preservers for other people. Oh, my God. That's really funny. That's what I decided. Was this coffee? Look around your size. This is extra large. That looks regular size, but I don't know if it looks extra large. That's funny. Nice. Well, what up? Rion texted me that, like, what a small world.

**Me:** Well, I'm liking you so you my friends. It was a holy shit, man. But. No, I know. It's excellent. Yeah, well, actually.

**Other:** You guys know each other well.

**Me:** I have some drama. I cannot fucking say anybody, bro. This is like insane. Dude, he knows that head of not had him go to market, but one of the founding GTMs at cursor that used to go out with this chick or something. So I'm like, all right, I'm going to stay real quiet on that call, man. But, no, he knew a bunch of my friends from one of the classes I was into. A bunch of my friends have that are going to the Turing Scholars Program at ut. One of these guys, dude, he was such an idiot. In high school. It's like pour water on kids notes before tests, pick up, submit at homeworks and shit. And so I got back at him, and in junior and senior year, by snipping his hair slowly and slowly using a pair of scissors every modern physics class.

**Other:** Nothing is. Here. Wait, what?

**Me:** Yeah. No, I was like, dude, you're being a little bitch. Everyone called him out on it, too. And I literally just give him a little haircut just to make him like, there's one bald patch on his head, dude, Literally, because of me, straight up.

**Other:** How many days did you cut his hair?

**Me:** Periodically over, like, two years. I'm not even joking you. Just a little snip every day, bro. Just a little snip every day. It was me and my boy.

**Other:** You're a psycho. I am not going to cross you. Jesus Christ, that's dedication.

**Me:** No. Just quit? Yeah, absolutely. We gave him a chance to quit, man. Reaching for some policies, bro. If not being.

**Other:** Wasn't he getting haircuts?

**Me:** He was. He was now, like, we'd snip a very little off, but he'd get pissed as fuck. And to this day, he would not talk to me after graduation, which is funny as fuck.

**Other:** Yeah, no, I get that. That part of the story is very believable.

**Me:** Yeah. But yeah, high school was an interesting time, but anyways. Okay, so Rayon actually gave me some interesting insights. I mean, obviously there's definitely conflict of interest, a little type thing between what they do and what we do. Their thing is that they don't target any labs that don't have a budget above or. Sorry. Below nine figures, which is insane to me, but. Nine figures. That's Cartesia's entire fucking raise. Literally. That's like, holy shit, dude. So that's a really.

**Other:** What do you mean by budget? Like 9 fig.

**Me:** Budget like on contract. They don't take any contracts at the.

**Other:** They have $100 million to buy data.

**Me:** Yeah. Which is like, what the fuck? Who are you talking to, bro? Like, straight up. Yeah. So I'm like, dude, that's literally. We can target anybody else. Pretty much is what he said. And he's ultimately.

**Other:** They're at, like, 500 mil. Arrow. You tell me they only have five contracts.

**Me:** I'm pretty sure. Bullshitting me, bro. I would think he went, like, full ego mode or whatever, but that's what he said. He was like nine figures.

**Other:** Well, I assume he told it over the course of years. I think they target companies that have nine figure budgets, but they can get much smaller contracts because it's not the whole.

**Me:** Contract is just a budget. Yes, they make it. Yeah. So I think that's probably what he meant, too. That's fair.

**Other:** Yeah. But then the contracts are probably eight figures comfortably then, right?

**Me:** Ly? Yeah, like, definitely, bro. Yeah.

**Other:** Yeah.

**Me:** They're pulling stupid amounts of money. Yeah. So I think. He obviously also mentioned that guys like Touring Surge would probably not want to talk to him. Right. Because they're also competitors and whatnot. But he can make intros for us. He's connected directly to 11 labs and Cartesia. I was like, just repeatedly mentioned to him. It's like, bro, like we're just trying to get calls on the books type thing. We love for intros to some of these more media. According to being a tiered, small tier company. We're probably going to get a couple intros from him. He said the best way to, you know, leverage him as a resource is probably to just get his say on, like, what these guys are, like, wanting. I kind of don't want to do that. Like, I kind of want it to come from the horse's mouth. Right. Because he probably has his own biases about these companies. Like, obviously, as tremendous learnings and whatnot. So I'm going to send him a doc with a couple questions along with like a research report. Outfit together already. Like, just on, like, like, you know, what types of data we're looking into. Remember that scorecard essentially sent me basically on the GitHub Wiki thingy? So that's basically what I'm going to send over to him to get his thoughts, and then I have a couple questions for him on, like, okay. Like, why are these people targeting this type of long tail data asset? Like, what is the priority? What type of data? Like, specifically within, you know, voice? Do they like, do they like high fidelity, your low fidelity, like, you know, things like this type thing. And so just pepper with a bunch of questions, Async, so that we can get efficient answers. To him. Unsubmitted. Sorry, intro of someone. Okay. But, yeah, that's pretty much my to do immediately from the call. And takeaways from the call. Too.

**Other:** Yeah. So, any questions? Because we have the shared slack with him. So feel free to just drop it in there and tag him.

**Me:** Perfect. Yeah, no, I see him as a guest internally here. So 100. I'll grab a group chat between both of us.

**Other:** Okay, Daniel, you want to go? Yeah. Working on hiring a data scientist with Sydney. And going to reach out to McCor Guy, a person input there as well. Like, clerk stuff is ready, so I'm going to get that merged. And then I think we'll be able to start on the landing page as well. So talk about that as well. Sounds like the doc's going to work for the landing page a bit. But we'll be up. We'll have to do a little bit of a custom component. For the actual functionality. It's supported by a framer, Elton, who a little bit. So. And it works with clerk, so we can make that work. Yeah. And then other than that, I think it's time to kind of start. Stitching some stuff together and send me out tasks. And. And so forth. So going to try and, like, get the system working a little bit today from end to end. Who wants to go next? Sick I end up in. Let's see. Yeah, let's see. I merged, I think, a couple PR yesterday. For the just I'm kind of trying to break up the the upload flow implementation like a you know more bite sized PRs and so like different works coming out of side of that. So yeah merge period state kind of refactoring to like the database types and like the shared package functionality. Extracted the Q contents into, like, the shared package because I'm going to put the sound broker's message types and, like, all the constants there as well. Added the worker and task endpoints to taskcore so that sound worker can come into when it's doing the upload. And yeah, I have a PR open. I have, I guess, one PR that needs review, I think. Daniel, if you have a second. That one. There's, like, some questions. I had a question for you. Specific vendor. Because I changed the schema of task or change the. Yeah. Scheme of task or task request. Look. Okay, cool. Yeah, so that and then I have the object storage PR ready to go as well, but just branched off of this one, so I have to wait for the skimmers. And then I'm working on the rest. I'm working on the. I'm finishing up the upload flow right now. I'm, like, adding some integration tests. And, yeah, this one's kind of like, I'm trying, like, I think integration tests are kind of like, I can try also from, like. A postman type situation, but without the mobile app, it's kind of hard to like, like creating some sort of simulation. It's hard to fully test, so I'll sometimes do integration test for this. So yeah. But yeah, I'm going through everything just like upload flow should be ready to go basically pretty soon, minus the transcode worker, which, I don't know, maybe I'll include this command as well. Yeah. And then, Sydney, I got up those. As you saw, I got up those RPC URLs, the people I have to update the docs, though, so I'll do that soon. I'll do that today. Yeah, thanks for doing that. I also asked Triton for a list of people on their shared info, so they just sent that over. It's actually more cool. Yeah, I think it's their standard shared info. Not like DAs or anything, but we should probably figure out some kind of transition plan for these folks by then. How? Yeah, if it's just RPC, we can give them RRPCs and it'll be fine. Cool. Do we want to like, so if. But if. How many people are there that do you think like or roughly do you know? I just sent the list in DevOps. Oh, it's okay. I thought I was making sure it was only a ton. Do we want to just give all of them for free? Yes. Yeah. It's shared anyway, right? Yeah. Yeah. I mean, they were paying, like, a small amount. And just looking at some of these names like ABK Labs and Metaplex. Like, rarible. Like, I don't know how much use there really is. So I think it just makes sense to give it away. So what's Unskippable? Wallet. I've never even heard of that. Yeah, like, how. How much of this is real? Like, in Matrica, was it the Discord Integration? Like, is that still working or not? I don't think. I think we stopped playing for magic. A yeah, so. All right, cool. Yeah, let's see. I'm trying to see if they support. I'm looking on this unstippable website or that's unstoppable. Or maybe there must be the same thing. I don't know. Anyway. Yeah, we can just, like, send an email to all of them or something, right? I guess. I think may or no hologram. I don't know if we have telegram. Yeah, that makes more sense. Yeah, I probably don't have all their emails. All right. Edit to list. I'll do that after I finish up the. What's I called. This gear. Frog. The payment. Okay? I can withdraw. The user can withdraw the payment. Like implement. Subscription. With a stripe account update. I think that's if it. That's the final task in. In the stripe integration. And work out. So you want to put up a draft PR so we can see your. Your progress? Yeah. You have. Okay. Yeah. I'm still working on the notification service. Update. You want to talk through the question in slack, the Twilio thing? Yeah, I guess Daniel answered that. What are you saying? Like us, uk, eu. Japan. What? Do you mean? I'm saying for places to text. Where are we texting? I think just any country that's not in the seven countries. I need registration, right? Okay? And they also mentioned that the prices are kind of high. For some other countries. So probably. So expensive for India. Yeah. Yeah. That's why I assume WhatsApp gets to be a lot cheaper compared to, like. Yeah. I think it's also coming from a US number two. I think I probably. If you had a number in India, it'd probably be cheaper for, like, anything. Texting. And I guess what's up kind of works in India more because, like, imessage kind of. We talked about that. People don't use it even though they have iPhones. Yeah. I wonder if we should just limit it so it's like imessage limited to us. And then everywhere else. Do WhatsApp. Why can't we do both? For. What can we do? Both. Just come in for app, I think for the experience side because it's better. In the iOS. So that's why we restricted us, you're saying. Yeah. I mean, for the U.S. i think we should just do imessage for the people with iOS device, of course. I mean, that's what I think really thinks with me. Yeah. Yeah. A message for iOS device and then everyone else. WhatsApp. And detect if a phone has imessage with the client. Like, what if you just ask the user to put in their number? And they're like, you can't until they respond. That would have been handy. Can I download it on Android? There are these apps that, like, let you proxy it. Which I messed with. They're not super great. Yeah, okay. Well, is there a cost associated with WhatsApp notification? No. That's completely free. It's just texting. It's not free. What's the message? There is cost associated with WhatsApp too. Oh yeah? Wait. How much is that in here? How much was it per message? $0.4. Oh, that's way better. And 0.$5 per video. Yeah. It's way cheaper, though. That's good. Okay. Where can I. Is there, like, a list somewhere? Like, pricing for different countries? Yeah, yeah. Can you just link it to me? Yeah. Because we might. I mean. The sign up flow a little bit based on which option is cheaper? I mean, I think what you can do, though, is, like, you can also just get, like, if we know what countries are gonna work in, we can just get phone numbers in each of those countries. They're not expensive. And then within internal country, texting would be cheaper. Are these Twilio cost or is it the texting cost? These are two new costs. Yeah, they are the texting costs. They target. They like, they're the middlemen that charge whatever the types of house. And then if we use like a local number, does that. Word the polio cost. Yeah, it's. Show them. Double check. I'm pretty sure, like, local texting is cheaper. Honestly, no, actually, It's. It's still 8 cents a text. That's crazy. Yeah, I feel like it. Just Julio's feet. I've seen it. I think it's. It's the country's. It's the carrier fees in that country. In addition to Twilio's fee. Like, in the US it's extremely cheap because, like, the carrier fees are essentially zero. I always thought us was more expensive. First, most things. But when it comes to spamming people with advertisements, we have everything optimized here. Clearly. Yeah. This is the cheapest. This is the best place in the world to sell shed. A media has 25 or text messages in our media 25 cent. 25, and it doesn't receive inbound texting. I think we should definitely just be sure we don't have cell towers over there. Probably. What's going on? Might be the case. In 2020 countries. Egypt is 40 cents. 40 cents? That's crazy. That's like a rare commodity. Yeah, what the fuck? We're a resource. Okay? Yeah, let's just go. Daniel, Center. Let's go with the easy countries and then discuss the ones with paperwork later. And we'll figure out the cost. Like the ones that don't require paperwork. So we need to look at all of them and. Yeah, one thing is also because we're doing well, let's start with the smallest. Get it working, get things functioning, and then we can expand to other countries. As we understand our customer base and the requirements. Like if we have a million people in Armenia that really want to work, we will pay the 25 cents. Since we're doing Waitlist anyway, we can let people off selectively just based on their phone number. Precisely. Exactly. They got to be. What's happened? Armenia. For 45 cents a text. I hope so. Yeah, right. Okay? I think. Yeah, I think that's it. For trying to think what else. Vedant. I know you want to go over some design explorations. Yeah. So, yeah, savvy. I was exploring a bunch of patterns or, like, UX things that we can do in the app site. And on the visual direction side, like how I would want the visual aspect to be because, like how we talked about running and stuff, like how kind of like relates all together. So I know, like walking over Figma file is always not the best thing. To do, so I just created, like, a quick Deck presentation. So let me know if you guys can see my screen. Okay, great. So. I started to like think from the first user experience perspective. So what's the first time the user is signing up or like interacting with human API? Whether it's iMessage or like landing page, whatever, right? So we need to like think like the user lands on the landing page, they fill in their contact, agree to the terms of service there, right? And they like the chat interface or they are already in the wait list and we send them a text through message, iMessage, WhatsApp, whatever or whatever country and then we kind of send our first message, Right. And at the same time, I don't want it to sound, you know, one of those scam companies, like make 400, $700, then click this link, Right? So I don't want to be in that tone. So. And also, like, I don't want to use anymo. Jeez. I don't want to use emojis because it's. I don't like it on. Especially something like what we're trying to create because it's not very professional. So. Yeah. So two things here is, like, we want to build trust that because, like, people would be sharing. Stuff like demographic and KYC and stuff with stripe. Of course, that's other thing, but for us as well. That's, like, super important. So we need to, like, establish some cues early on. So that starts with the landing page, of course. Then it boils down to the first message that we send. So kind of like, let's see it visually, like, how? I think, like, we should make some experience. So at the top, it is, like, they get a message from us. Like, get paid instantly to, like, record short voice notes for AI training, no app download required. And we have, like, two options here. Like, yes, I'm interested in seconds. Like, what is human API? Why they're in text streaming? Because they might have forgotten about the waitlist that they signed up for. Or maybe they just signed up on the landing page really quickly and did not read. So the give give them an option to, like, know more about what we are. Right. So maybe click on this, they go to the next section, which is, you know, kind of explaining what we are, and we have a little thumbnail of whatever website we have that's also super important to, like, kind of make this preview kind of high quality rather than, like, kind of, like, scammy. So. And also, like, give value. This is just a plain icon right now, but I would want this to be something where they could understand. Okay, we can. Do tasks. This is what I have to do through this small thumbnail as well. This is both on WhatsApp and on iMessage. Like, the preview looks the same, so we can kind of play around with that. So yeah, they could click that or learn more, or here they could just, you know, click yes itself. So I'm going to show you the happy path, which is when they click yes. Right. So as soon as it click yes, maybe we will do verification code or not. Depends. But let's say we do it so. We'll ask them to, like, send verification code. Maybe they'll receive a notification from top and then we'll, like, enter that code. Or maybe we can, like, ignore this step. So part of discussion later on. But yeah, I mean, pretty much that's it. We don't ask for any demographics right now. We don't ask for no payment settings, no kyc, nothing. That comes later when the user has to actually withdraw the funds. Right. So how does the task work? Right, so after this, I would want them to give. I would want them to do a certain task. Right, so let's focus on the top three ones. I've given like one example in the next screen which is going to be like the scripted one, but all of the other ones is going to be pretty much the same in terms of like how it looks on the iMessage or the WhatsApp. So for the first task, I would want the users to, like, kind of do, like, a test task or maybe something which is very generic and not demographic focused. So we can give that to the user without actually letting a lot of details from them so they can, like, get a hold of, like, okay, this is what Human API does I have to, like, you know, record my voice or whatever, Right. So as soon as they enter the code, right, we send them like. Thanks for verifying. Below you can find test task. Your first test task. Task type, scripted, read exactly. So this is an example, like, could you grab milk on your way home? Like, that's what they're going to record it. And then we also give a task value. For this reason I just added like 0.01 USDC we could do like any number, but I would want to do a certain number here. Or maybe, yeah, I would want to have a certain number here because people could go over that, you know, whole process of withdrawing and stuff like that, which I'll show you later in the steps. But one question here is can we like bold and italic the text in imessage? Because I know it can happen in WhatsApp, but I'm not sure if they can be happening on imessage. We can add it to. We should get a list of questions and we can figure that out for you, but I don't know. Okay, cool. So. All right, let's keep that in mind. And this one is the start recording. I mean the click start recording app clip kind of pops up like small. They can click open to immediately open the app clip itself or if they haven't downloaded the app they will be redirected to the app store. But question is that can this still have this small pop up come up if they don't have the actual app and if they click open they can be redirected to the App Store or the Play Store. Or no. Sorry. Ask that one more time. So as soon as somebody clicks, start recording. If they don't have the app. Right. Can this small app clip, thumbnail kind of thing still pop up, which is kind of like common across app clips, or it can only pop up when they actually have the app. I think you can only get that one. You actually have the app, but. We could have the start recording be like a deep link where it has them download the app if they don't have it, and pop up the app publicly. Do I believe that's how it works? But if you don't have that, Then once they click, start recording. We will have to redirect them to the application. If they don't have the application. Yeah, cool. That works. Okay, so the person records and complete the task. Okay, we'll cover that clip and what I have in terms of exploration later. But reds, like right now skip to that part and kind of like see how the imessage works. So they submitted the task, Right. We give them a receipt. I know, I use numo. Gear, but I guess it's fine for here in this case. But, yeah, checking quality. So our housing discussion with Sydney there, like, I think, like, there should be a timestamp for the user to know, like, this is going to be a proven a certain time or maybe a message that shows that, you know, quality is. Super important for us because we're working with Fortune 100 AI Labs or whatever. Kind of like add to that, do you think there is a time limit that this quality check can be done within 10 minutes or less or no?

**Me:** Zero. 00. Zero. Zero. Zero.

**Other:** Yeah, it can be done in way less than 10 minutes.

**Me:** Zero. Zero. Zero. Zero.

**Other:** Okay, great, great. So, yeah, we just want to give, like, whatever the time is, like, two times more than that. So the user. Yeah, I mean, question is more. So, like, the initial validation versus the actual sentence of the task. Two different things. So the initial validation pretty much like almost instantly or at least a couple seconds after, but. The actual substance might take a little bit longer.

**Me:** Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** Yeah, we can have. So we probably have, like, three phases of validation. One is on device, which is like, did you record what you meant to record? Almost. Right. And then we can do kind of like AI driven transcription and stuff on the server and validate that, like, a few minutes later.

**Me:** Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** And then, you know, once, I don't know if beyond that we like giving another is if their data was accepted by an alert or something beyond that, but after that is like the, the sale, the selling back end, right? Which can happen like much, much later. So it's like seconds.

**Me:** Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** You know, a minute or two, and then, like, days, weeks, months.

**Me:** Zero. Zero. Zero.

**Other:** Okay. So as a task can take days to get approved. I think for them to actually get paid out, Yeah.

**Me:** Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** Yeah. For them to get paid out into their bank accounts, that's what can take days.

**Me:** Zero. Zero. Zero. Zero. Zero.

**Other:** But forgetting the task. Approved. Right. So getting the bank account is actually, I think, pretty instant. It's the. The approving of the task, I mean, not the test. Test I'm talking about maybe the actual task.

**Me:** Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** Maybe. I mean, actual task, I think, like the ones that are sent by the ad companies to us, basically, not the test task. So this is the test task, one which will give five, but, like, the actual task, which they would be getting actually paid for, like, 90 cents or whatever. So how much time can it take? Like, it can vary two days or like, is there a maximum limit? That's up to us. Because if we're doing the. If we're sending out the test task, then it depends on how much validation we want to do.

**Me:** Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** I mean, test task is fine. I mean, I get that test task can be approved faster. I'm talking about, like, let's say you do this task, you complete the test test, whatever you say. Keep in my wallet and do the next task. The next task would be, like, maybe, let's say, read, like, 50. Word. Scripted paragraph. Right. So how. How long would that take?

**Me:** Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** I don't think there's like a. I don't think that's, like, a technical thing.

**Me:** Zero. Zero. Zero. Zero. Zero.

**Other:** I think it's more so like for us to review the data.

**Me:** Zero. Zero.

**Other:** Okay, so this data is going to be, like, validated by some backend thing, right?

**Me:** Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** Yeah, I think that's an open question is like, how? Because when I use these, like, task work websites, it usually says, like, oh, you'll be notified in, like, a week or so. But then it's like, what are they doing to validate the data?

**Me:** Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** Okay?

**Me:** Zero.

**Other:** So it's better to not the timeline in that case.

**Me:** Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** It's better not to give a timeline in that case.

**Me:** Zero. Zero.

**Other:** Yeah. I would just say, like what? You know, it's like, pending or like in the View or something.

**Me:** Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** But they can actually, like, do another task. Meanwhile, of course. Right.

**Me:** Zero. Zero. Zero. Zero. Zero.

**Other:** Okay, so, like, I'm seeing here on this. Like, I did this task, like, weeks ago or maybe like two weeks ago, and it still says in review and not payable.

**Me:** Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** Okay, that's interesting.

**Me:** Zero. Zero.

**Other:** Okay. So they would have to, like, come back to the, like. Okay, that will be, like, native app experience, that innovative app. You can keep, like, under review, tests and, like, completed and stuff like that.

**Me:** Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** Yeah. We would separate out the earnings of, like, what's, like, inflate versus, like, what's actually, you can withdraw.

**Me:** Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** Okay?

**Me:** Zero.

**Other:** Yeah, Makes sense. Cool. I mean, it's fine. The first week kind of like right now, this whole deck is like the first time experience. So the first time experience is not hindered by that because, like, where if we have a decent confidence level, especially for the test. Test, maybe we just pay it out faster just so. They get that initial, like, dopamine hit, and then for the actual, like, real AI tasks, they take a little bit longer because it could explore something like that.

**Me:** Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** Yeah.

**Me:** Zero.

**Other:** I mean, this is pretty much that. Only, like, you get paid fast.

**Me:** Zero. Zero. Zero. Zero.

**Other:** Like 0.01 is not. I mean, they're not going to be cashing that out, of course, but there will be something like getting. Reflecting into their balance.

**Me:** Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** Yeah. I mean, we. We can have it reflecting their balance and not have it available to withdraw for some time.

**Me:** Zero. Zero. Zero. Zero. Zero.

**Other:** Yeah, like that's an option, too.

**Me:** Zero. Zero. Zero.

**Other:** And I think there's a way to do it and not appear super scammy.

**Me:** Zero. Zero.

**Other:** Yeah. I mean.

**Me:** Zero.

**Other:** We can do, like, a limit to withdraw, like, $10 or something.

**Me:** Zero. Zero. Zero. Zero.

**Other:** That's a lot of people do that. So it's not like we're doing something out of. I was more saying, like, we could credit them with the completion of the task and say, like, a funds on hold.

**Me:** Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** And so, like, because, like, different, like, tax payouts are going to come available at different times, right?

**Me:** Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** And so we can show them the balance optimistically.

**Me:** Zero. Zero.

**Other:** And then allow it to withdraw on once, like we're ready to pay them out.

**Me:** Zero. Zero. Zero. Zero.

**Other:** Okay, so, like, like, you ever done, like, a transfer from, like, bank to bank and, like, credit you with the balance, but then it's, like, in a pending state, too?

**Me:** Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** Yeah. Yeah, okay.

**Me:** Zero.

**Other:** So. Okay. Or, like, when you, like, deposit to, like, a crypto exchange. Like, oh, you can't, like, move it out right away. Yeah, yes, I get it. Like, the cooldown. Pure does something. Yeah, yeah.

**Me:** Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** Yeah.

**Me:** Zero.

**Other:** We're not going to say, like, funds on hold. That's not a good word, but yeah.

**Me:** Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** Cool. Awesome. So that's done. And maybe they withdraw it or whatever. So let's say the withdrawal. I mean, not withdraw, but, like, they would have to do KYC on stripe. So stripe is the only way that we're doing it right now. Correct.

**Me:** Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** For now.

**Me:** Zero.

**Other:** Yeah. Okay, cool. So that will be the whole thing. So I just clicked like, no, because this is a happy path we're doing. If it's yesterday, then we'll give them, I don't know, troubleshoots, like redirecting it to the stripe paperwork anyways. But yeah, so then we can. Ask them, okay, like, are you ready to do your first task? So that was the test task, and this is the first task.

**Me:** Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** If we have a task ready for them, and then that might take weeks to approve whatever. They have to check native app for that. So then the whole experience is going to be pretty much the same. We're going to send them the task, something like this, and then they'll start recording. But now let's talk about, like, how they're recording and everything kind of works in the app clip. And what do I think?

**Me:** Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** But before that, I would want to, like, talk about visual direction. Like, how, like, I think the visual direction should be and how, I mean.

**Me:** Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** Like how it should look like, basically, in terms of visuals. But then I'll be Chinghua you some actual examples which not might be visually close to this, but in terms of the ux, that's what we're going to do. So the first the UI and then the ux. So this is how I imagine it to be kind of like in the dark mode. They're dark as the canvas. Maybe black or dark gray or maybe a really dark purple. Like, this is like a dark purple shade. And using a little bit of gradients, like, probably to the whole context of like 5% and, you know, 90% is going. To be the canvas and the 5% again is going to be something like these little bit of effects or maybe like these buttons. I really like that.

**Me:** Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** Kind of looks like, you know, retro vibes, but also, like, at the same time, not very, you know, I would say welcoming in general because, like, that's the why we're going for, so. Yeah. And I also want to incorporate a little bit of glass morphism, Apple style, like.

**Me:** Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** Into this design style, so that's what I think is, like, a good thing. But do you guys rely on that or no?

**Me:** Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** Yeah. I love this.

**Me:** Zero. Zero.

**Other:** Yeah, I love. Let's do apple glass.

**Me:** Zero. Zero. Zero.

**Other:** Yeah.

**Me:** Zero. Zero. Zero.

**Other:** Great. Another example. So I was exploring some inspirations for Waitlist and, like, page like that.

**Me:** Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** I could not find anything that I liked a lot, but I did like a little bit of this. I mean, this is also like glass. When it's like sunlight reflects on it, it's kind of like gives you this rainbow kind of thing. I don't know exactly the technical term for that, but yeah, we. Could add this bit of something into that. So maybe somebody's moving, moving their mouse. They might experience it from certain angle.

**Me:** Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** Or maybe, like, add a little bit of Easter egg somewhere. I don't want to make, like, super crazy. Of course, it's like a normal waitlist, but, like, still, we should have some sort of character. I know we're going for the cold branding in the cold kind of, like, character, but it should still. Have that character. Like, it's cold, but, like, you know. So, Adithya. I, I, I kind of fuck with that white.

**Me:** Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** Some more examples in that direction. So, yeah, I mean, that was the visual. So now I'll show you some of your explorations right along with, like, some examples, because I would want you to, like, imagine a little bit, but I do have some examples.

**Me:** Zero. Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** Together. So kind of, like, relates, but it's not going to be exactly how it's going to look, but still.

**Me:** Zero. Zero. Zero. Zero. Zero.

**Other:** So I want to. So we're talking about the experience when the person click start recording. Okay. So as soon as they click start recording, I would want it to be like super simple, like the record, the submit and they get paid and it should be all done to an imessage once they have the app. We will put that clip. It gets done. Cool. They get paid, they get dye message. If you want to go to the app. Cool. They can click a certain icon in order go to the native app. But mostly want to keep it like 90% focused on recording the task. So when you design like primary action first. So traditional kind of app clips open up to the full length as far as that we experience. So But I would want to create something where it does not open to the full length. I would want it to be just this size. Imagine this is an imessage conversation going on and you click start recording.

**Me:** Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** And it pops up. Something like this is not exactly. Because I don't like it in certain ways, but that's the point that you get the primary action that's recording and you start recording. You can choose your mic to get a better output or whatever.

**Me:** Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** And the store recording. Once it's done, you submit it.

**Me:** Zero. Zero. Zero. Zero.

**Other:** And it closed off. So first question is, is it even possible to create an app clip of half the size? Can we, like, control the size or is it standard?

**Me:** Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** I don't know, but we will find out.

**Me:** Zero. Zero.

**Other:** Okay, cool, Cool. So this was, like, super important because, like, I don't want it to open the whole thing because we don't have, like, a lot of stuff for them to do, so that's, like, very important.

**Me:** Zero. Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** So. Yeah. And also along with that, we'll have some minimal controls, like, you know, transcribe. They already have downloaded. They should be able to just open up like half screen.

**Me:** Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** I think if they don't have the app downloaded and they're receiving it as an app clip, then maybe there's, like, some limitations around it.

**Me:** Zero. Zero. Zero. Zero. Zero.

**Other:** This is being recorded or transcribed at all.

**Me:** Zero. Zero.

**Other:** No.

**Me:** Zero. Zero. Zero.

**Other:** I'm just going to click Jim and I start taking notes.

**Me:** Zero. Zero. Zero.

**Other:** Yeah.

**Me:** Zero.

**Other:** Cool.

**Me:** Zero. Zero. Zero.

**Other:** Okay. So, I mean, I'm going to send it either way to you guys, so you can, like, go. Yeah. The questions about the App Club functionality, I just want to make sure we don't forget those.

**Me:** Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** Typically. Oh, you have a couple lined up?

**Me:** Zero.

**Other:** Oh, they're in there. Awesome. Thank you.

**Me:** Zero. Zero.

**Other:** So you don't have to let me. But, yeah, it's cool. Like, we should have recorded this meeting as well. Yeah, I know. Gemini.

**Me:** Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** The same. Aptman's on the case or whatever.

**Me:** Zero.

**Other:** Yeah, no worries. So, yeah, this like the microphone to get the better audio quality as well. And so we want to create something like this compact and kind of like going from that angle. And we don't want to, like, reinvent the wheel here. We will pretty much just learn from the already existing recording applications. Voice Memos. Or whatever, so people are aware of that. I pretty much want to keep it very similar to voice memos as well. That part of course, like the visual would be a lot different. Like what? I showed you the why, but in terms of UX it should be pretty similar because most of the iOS users I used to that experience. So, yeah, and I would also want to have, like, a small icon, like top left, maybe a small home icon, and top right, profile icon, which shouldn't be, like, very visible, like super subtle. But still, if they want to access it through that clip screen, they could go to the whole app experience itself.

**Me:** Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** So. Yeah, Already talk about the audio enhancements and stuff.

**Me:** Zero. Zero. Zero. Zero.

**Other:** So, yeah. Now. Now let's talk about, like, this thing, which I think, like, we should do in terms of, like, gaming, flying a little bit and adding a little bit of layer of fun to this. And also, like, people should come back to the app every single day.

**Me:** Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** To, you know, record more stuff. So what I want to do is, like, have, like, subtle real time scores. So imagine, like, once you record it, you complete the recording, whatever, it's 20 seconds or whatever.

**Me:** Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** And you get a little small badge there, like, maybe clarity. Or, like, there could be a small icon depicting that, and it should be, like, super large. But once they click it, they can maybe see, like, top. I mean, the three emotions that I think, like, right now we can, like, start with three, but we can add later, more. But I would want to stick with three as well, because, like, that's pretty much covers everything. So the three things that are, like, clarity, speech and emotion, that's what I want to score their recording based on.

**Me:** Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** So clarity is like the audio clarity and how crisp the mic actually sounds. So later on, they would also maybe invest in a mic because they would get, like, better value out of it. Yeah, whatever. So I'll show you that later.

**Me:** Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** But like speech like how well they spoke. Maybe like with left less like ifs and buts and like ums and oz, but also like not super rewarding at the same time. So we need to keep check that people are not just feeling in chat GPT voice there. So. Yeah. And in terms of emotion, that could be like, more for like, motive and contextual tasks, but we want to like, base it out. Like how? Well, their emotion kind of match the requirement, but I don't know exactly how that we would do that. But if there's a way that we can like pre fill or, I don't know, database. With the emotions that we would want it to like, exactly be like, if they match it, then that's, like, a good thing. But can that be done?

**Me:** Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** So.

**Me:** Zero. Zero. Zero. Zero.

**Other:** Yes. So this would be on the. On the second time frame. So there's three time frames are on device.

**Me:** Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** On this Eclipse servers, and then, like, after feedback from the buyer,

**Me:** Zero. Zero. Zero. Zero. Zero.

**Other:** And so on that second time frame, we'd be able to do this sort of thing.

**Me:** Zero. Zero.

**Other:** Okay, great.

**Me:** Zero. Zero.

**Other:** And some of it can be on the first time frame, but to really give, like, the depth that we, that you're probably looking for, it's. It's on that second time frame.

**Me:** Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** Yeah, we have, like, rudimentary values for, like, clarity. We know clarity mostly. And then speech we like. It would be like, all right, well, this is like, rele your input volume relative to the ground noise level type thing.

**Me:** Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** Maybe more. I don't know. But, yeah, we need AI or some external service to do that. Or we have to build our own service.

**Me:** Zero. Zero. Zero. Zero.

**Other:** But either way,

**Me:** Zero.

**Other:** Second flow.

**Me:** Zero.

**Other:** It'll be like host upload is the most important. Yeah, yeah, yeah. No, yeah, that's what I. So it'll be post upload and. But how fast do you like pillow talk? Kind of like that. Tag the conversation really fast.

**Me:** Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** Like, I guess even in real time. Sydney have, like, tried pillow talk, right? Yeah. I mean, like, it's hard to say because we. We have to talk about the length of the clip and then exactly what we're looking for.

**Me:** Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** But I think it's on the order of, like, less, you know, a minute or less. Right. And it's like, maybe two minutes. Right. Like, how much do we really want to wait? We want to wait more than two minutes? Probably not.

**Me:** Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** But I think that's. That's what we're looking at. So something where, like, you probably won't want to stand there looking at it, but we could send them, like, a push notification when it's done, or we could have the scores available later.

**Me:** Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** So you'd have to think about, like, an asynchronous flow, I think, because it wouldn't be like it. It'll take. I. I think it'll take at least like, two to three times the length of the clip is kind of what I've been seeing.

**Me:** Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero.

**Other:** So a 10 second clip could take, you know, 20 to 40 seconds or something, but until we have, like, very. A little more specifics, it's hard to give an exact time.

**Me:** Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. Zero. 0 I tried my dwelling finish.

**Other:** It also depends. On how intense the AI is. Yeah, precisely.

**Me:** Couldn't you do. Couldn't you do this process, like maybe synchronously, and hold user funds in an escrow account and have them withdraw the funds, like later the asynchronously. So, for example, you instantaneously deposit whatever theoretical funds they would earn from that clip synchronously? And then the QC ends up not checking out. Then you just pull it back. That's kind of the idea.

**Other:** So what was that? Yeah, I think that's what we're more or less getting at. Like, we optimistically credit them, and then, you know, there'll be some state where it's like,

**Me:** Yes.

**Other:** Assuming nothing bad happens, we. I think we're talking about, like, one week in grade, the emotions of the. Like, the emotions of the script, right? Yeah.

**Me:** Ok. And that would require, like, a more intense model type thing that's way more asynchronous than just basic qc.

**Other:** Yeah. So like again, there'll be like three phases. So one will be like kind of basic rudimentary, like qual, like on device quality and clarity that will be like near instant. And then we'll have like a post upload phase where we feed it into other AI models to assess like emotive. And contextual content. And that'll, you know, we don't know exactly how long that'll take. From what I've been researching and doing and understanding, it's two to four times the length of the audio.

**Me:** Yes.

**Other:** And then we can. We can provide that data to people.

**Me:** Ok. And you would require the second QC in order to validate sort of any clip, right?

**Other:** You know, I don't know. I think that's gonna be up to the buyers and, like, something that we have to figure out what the market needs.

**Me:** Ok? Yeah. What their qc needs are. Yeah, 100%.

**Other:** You know, so some people, some people who make emotive LLM models, they don't want the emotions from other LLM models, right? They just want the raw data.

**Me:** Oh, yeah, yeah.

**Other:** Yeah. And so that just depends.

**Me:** 100% ok.

**Other:** Yeah. Is the emotive one can come later when, like, it's an emotional, contextual task. Like the clarity and speech could be done fast, in my opinion. I mean, that's what I think. And why would I want it to be faster? Because if it doesn't match a certain score. So we will, like, rate this whole all three out of, like, five. Score. So basically if a restored like 4.5, they like unlock a certain percentage on their badge. I'll explain badges later on, but that's why I would want it to be like kind of faster, so people can re record it in a better environment in better settings, so we end up getting a better data. And high quality. And also, like, they have a certain. Like, they want to do it again because they would also, like, get paid in the future higher if they keep doing something like that. So that's the idea. Makes sense. I think there's definitely, like, pillow talk. Definitely does it kind of instantly, but I think they just have more, and they're just using an AI to, like, transcribe and give you the emotions right after you speak. So there's a way to do it, but I don't think it's, like, a huge thing for us, though. Yeah. I mean. I mean, in terms of the emotion, one, we can be laid by one, two, or, like, three minutes, but, like, anything more than that is, like, too much. Because the first two can be, like, clarity and speech are, like, for every single type of tasks, but, like, emotion is for only one type of that. So, Adithya. That's something. But, yeah, we, we can. So I'll explain this system so it kind of, like, makes more sense. So what happens is, like, after, you know, this score, whatever, if a user kind of scores well on all of these three things, or, like, two things, they unlock score more than.4.5. The analog certain badge. Let's just say, like elite emotion for like, somebody who scores 4.5 out of the emotion side. So the progress bar kind of fills up and let's say, like, it filled up 2%. Imagine this is the elite emotion one. It's namely demotion and below. Is mentioned that you will get 1.1x higher pay than and average user if you unlock this badge for emotional contextual tasks. Right. So people could see like immediately, okay, I would want to like re record it again. Because I would get like 10% higher pay compared to others if I get more tasks like this. And we can also send more of those kind of tasks to these users to get higher quality data, because that's what I've been doing consistently. Because there's not, there's not a lot in one time, so that's kind of the basic idea. And if a user is kind of like, also scores low, let's say like, like this, like one emotion, right? We can also have like, many tutorials or like, sound snippets of how it sounds like, not the exact word, but like somebody, an actual, like maybe a higher, higher voice artist or something, which actually like, shows the some of the five maybe words in that emotion. So, yeah, that's an added layer to that. It's optional, but, yeah, and scoring can also influence, like, how quickly a user's recording get approved. I know. Like, we get. Probably. I control this on the backend. Like, if that score is higher than whatever number, we can approve this faster. But I guess it depends on the AI Labs as well. So, yeah, I mean, that's the kind of idea. That's why we're talking about emotions and creating it. I just thought an idea. This is, you know, how Record started with, like, interviewing people, and that's how they got a lot of their initial, like, labeling data imagines. Me and Nadia are based in LA and we start hosting auditions. We're able to read, like, lines. That'll be great. We have, like, grid. Lines and different emotions and have people act it out. Yeah. We're like, in an audition videos.

**Me:** That would be, especially in la, honestly.

**Other:** So, like, read certain lines. Yeah, I feel like it could work. Like, for the initial batch of work. They just asked. Because I was just thinking there's a. There's probably a lot of voice actors in la. And we could probably, like, tap into that.

**Me:** Yo. I actually totally forgot to mention this. Rayon and I talked about this as well. Sydney, you're concerned with sort of. Ok where are the samples going to come from? Are totally valid, right? Like we over promised on a lot of these messages. Ray Han said he could help us out with that because Mecore already has the distribution for a lot of this shit, right? And they don't really give a fuck about Long tail data assets, so he said you could just put up a job for us within Racore and just get the data through them type thing, so we could lean on that with a partner there.

**Other:** Okay? Nice.

**Me:** But no, I think this idea is pretty sick too. I mean, there's like, everyone in LA is trying to make it out or whatever, has acting gigs on the side. I feel like people would just show up.

**Other:** We just go to catch LA and be like, hey, you want to audition?

**Me:** Damn. Yeah.

**Other:** That's nice. Interesting. Something like Adi, we can talk about it like ways to bootstrap the task workers.

**Me:** Yeah.

**Other:** That's so funny. Like. Very similar to, like, what I did at Cameo Mora. Just, like, paying actors to, like, talk to their phone. Yeah, so, yeah, I mean, so after that, we once were kind of like. Like we passed this one. So the task discovery, right. There's. I know initially, like, we won't have a lot of tasks for the user, so maybe, like, we could have like, five, six or whatever amount of tasks. So in the native app, now we're talking about the native app.

**Me:** Y. Es. Y. Es. Yes. Y. Es. Y. Es. Y. Es. Y. Es. Yes. Yes. Y. Es. Y. Es.

**Other:** Is we're going to have maybe a screen like this. This is also pull a doc screenshot of Chinghua like, one task. So kind of like looks like a TikTok or Instagram Reels or like a Tinder experience, which, like, gives you high dopamine and kind of like you can see, like, scroll through it fast and, like, do all these tasks and could be like a swipe right gesture and then could, like pop up recording screen for you, like, start recording immediately and then once it's done, you submit it.

**Me:** Y. Es. Y. Es. Yes. Yes. Y. Es. Y. Es. Y. Es. Y. Es. Yes. Y. Es. Yes. Yes. Yes. Y. Es. Y. Es. Yes. Yes. Yes. Y. Es. Y. Es. Y. Es. Yes. Y. Es. Yes. Yes. Yes.

**Other:** And it gets processed. So, yeah, that's an idea for that. I was also thinking that.

**Me:** Y. Es. Y. Es. Y. Es. Y. Es. Y.

**Other:** And also like we'll of course have like a normal general view as well a small tab above like switch to 4u for u could look something like this and general view would be a normal like how list view or maybe. Yeah, a list view basically. So yeah, I was also thinking like we could do if we have more of things coming in. Uh, we could do, like, high performance or, like, a curated pool. Like, Upwork has, like, this talent cloud pool where you get, like, paid higher. And also, like, it's kind of invite only. Only, like, good designers or, like, whatever. Not designers. I mean, in terms of this good artist kind of. Get invited into this, and then they get.

**Me:** Es. Y. Es. Yes. Y. Es. Y. Es. Y. Es, yes. Yes. Y. Es. Y. Es. Y. Es. Yes. Y. Es. Yes. Y. Es. Y. Es. Yes. Yes. Yes. Yes, yes. Yes. Yes. Y. Es. Y. Es. Y. Es. Y. Es. Y. Es. Yes. Y. Es? Yes. Y. Es. Y. Es. Yes. Y. Es. Yes. Y. Es.

**Other:** Higher paying tasks or whatever, and they could, like, apply. So we could give, like a little pop up or something somewhere or maybe like have a dedicated area for that that they can apply to that. So we could have some sort of requirements so that will even ensure a higher quality of people.

**Me:** Y. Es. Y. Es. Yes. Y. Es. Y. Es. Y. Es. Y. Es. Y. Es. Y. Es. Y.

**Other:** So. Yeah. And also we could do, like, something like a leaderboard of, like, how many tasks somebody recorded or, like, like, top three performers.

**Me:** Es. Y. Es. Y. Es. Y. Es. Y.

**Other:** And people could see those profiles and see, like, which kind of badges they have. And then we could also show, like, this guy gets paid 1.8x more than the other person because they have these many badges. And these badges equate to what they can also, like, click on certain cdf, which, like, learn more. About badges, which kind of leads you to something like this, where you can see, like, all the logged badges that they have. And then we say, like, you unlock whatever, like higher pay or something. Whatever. Maybe some XP or something. So we could, like, mention that if you have that, then you, like, you know, powerful. More powerful than an average user.

**Me:** Es. Yes. Yes. Y. Es. Yes. Y. Es. Y. Es. Y. Es. Yes. Y. Es. Yes. Y. Es. Yes. Yes. Y. Es. Yes. Yes. Y. Es. Y. Es. Y. Es. Y. Es. Yes. Y. Es. Y. Es. Y. Es. Yes. Yes. Yes. Y. Es. Yes. Y. Es. Y. Es. Y.

**Other:** So I was also talking once, I was talking about emotions back there. So this is kind of like it relates to. This is like a visual, kind of visualizer of moons, right?

**Me:** Es. Yes. Y. Es. Yes. Yes. Y. Es. Y. Es. Yes. Y. Es. Yes. Yes. Yes.

**Other:** Can we do something like, you know, a Grok does it? Grog has this example. I also had a dark mode example of this. So it has like a little bit of magical feel to it. But I also don't want to make it super magical because of the vibe that we are going for. But if we can have some sort of, like, you know, haptics in the app. If somebody says something based on an emotion, color gets triggered or something that could be nicer.

**Me:** Y. Es. Y. Es. Yes. Y. Es. Y. Es? Yes. Y. Es. Yes. Y. Es. Yes, yes. Y. Es. Y. Es. Y. Es. Y. Es. Yes. Yes. Yes. Y. Es. Yes. Y. Es. Y. Es. Yes. Yes. Y. Es. Y. Es.

**Other:** Adithya. That's like that. I mean, kind of like if. I don't know if I Adam do cards, I would like checking out this S class feature. When you, like, turn on heater, it kind of sends a red strip across that part of the door. And it's also not very gimmicky. It kind of looks like kind of clean. So maybe we can pick something like that and add to this. Of course, not a lot of, like, cloudy gradient, but, yeah, that's what I was thinking. So, yeah, these are the explorations that I've done.

**Me:** Yes. Yes. Y. Es. Y. Es. Y. Es. Yes. Y. Es. Y. Es. Y. Es. Yes. Yes. Yes. Y. Es. Y. Es. Y. Es. Yes. Yes. Yes. Y. Es. Yes. Y. Es. Yes. Yes. Y. Es. Yes. Yes. Y.

**Other:** And. Yeah, let me go. What? Do you guys have any questions? Yeah, I think the. The thing that you can imagine with, like, what Grok does, I think that could be kind of cool in that I notice for these task work.

**Me:** Es. Yes. Y. Es. Yes. Yes. Yes. Y. Es. Y. Es. Y. Es. Yes. Y. Es. Y.

**Other:** Like the audio tasks, they typically will analyze some kind of, like, ambient noise, make sure you're in a quiet spot. And then they also usually ask for, like, gaps. So, like, one second gap before you start talking and then one second gap after you finish talking. So I wonder if we could, like, show that in the color. As well, like, oh, it's been a second that you can start talking now.

**Me:** Es. Yes. Yes. Yes. Yes. Y. Es. Yes. Y. Es, yes. Yes. Yes. Y. Es. Yes. Y. Es. Yes, yes. Yes. Y. Es. Y. Es. Yes. Y. Es. Yes. Yes. Yes. Yes. Y.

**Other:** Yeah. Yeah. I also did some more explorations. This is like the Dark Mode 1.

**Me:** Es. Y. Es. Y.

**Other:** And this is the light mode. And this is like, maybe, maybe imagine somebody's talking. This is, like, more filled, and this is, like, nobody's talking, so maybe it's, like, quieter.

**Me:** Es. Yes. Y. Es. Y. Es. Y. Es. Yes. Y. Es.

**Other:** So, yeah, also something like this. This is too much, too bright, but, yeah.

**Me:** Y. Es. Y. Es. Yes. Yes. Yes. Yes, yes. Yes. Yes. Y. Es. Y. Es. Y.

**Other:** Yeah.

**Me:** Es. Yes. Y. Es. Yes.

**Other:** So I have, like, a few questions that I've also listed in here, so I would. If you guys can send me an answer by this week, that would be great. So I can, like, start on the Lo Fi wireframes itself, and then we can complete the app and I can, like, design the app and you can start working on it. And I'll start working on the landing page, meanwhile, so that way, like, we can move faster.

**Me:** Yes. Y. Es. Y. Es. Yes, yes. Yes. Y. Es. Y. Es. Y. Es, yes. Yes. Y. Es. Yes. Yes. Y. Es. Y. Es. Y. Es. Yes. Y. Es. Y. Es. Yes.

**Other:** Do you think that's possible?

**Me:** Y. Es. Y. Es. Yes. Y. Es.

**Other:** Can you consolidate the list of questions and just send in slack?

**Me:** Y. Es. Yes. Yes. Y.

**Other:** So instead of, like, digging through. Yeah. Reading through the deck or listening back to the recording, I think it's easier if they just have, like, checklist of, like. These are all stupid questions.

**Me:** Es. Y. Es. Yes. Y. Es. Yes. Yes. Y. Es. Y. Es. Yes. Yes.

**Other:** No, that makes sense. Is that another question? As we're talking about this?

**Me:** Yes. Y. Es. Yes. Y. Es.

**Other:** I had a question around, like task density and maybe this is for like a Ray Hun question where maybe for the new data scientist. But I'm just thinking in terms of coverage. I assume, like, one person will be able to do multiple tasks, tasks for the same buyer, right? In the same data set.

**Me:** Yes. Y. Es. Y. Es. Y. Es. Yes. Y. Es. Y. Es. Y. Es. Y. Es. Y. Es. Yes. Y. Es. Y. Es. Yes. Y.

**Other:** I would really assume so, but, I mean, yeah, that's a good.

**Me:** Es. Y. Es. Yes. Y. Es. Yes.

**Other:** Good question to get to people that know the answer.

**Me:** Y. Es. Y. Es. Y. Es. Y. Es. Yes. Y. Es. Yes. Yes. Yes. Yes, yes. Yes. Yes. Y.

**Other:** But I I don't know. Okay.

**Me:** Es. Y.

**Other:** Yeah. Maybe I'll ask

**Me:** Es. Y.

**Other:** I'll ask Rayham for now and see if he had he has an answer for that. But

**Me:** Es. Yes. Y. Es.

**Other:** if not,

**Me:** Yes.

**Other:** probably data scientist question.

**Me:** Yes. Y. Es. Yes. Y.

**Other:** Okay. Any questions from anyone? Oh, this is dope. I wanna

**Me:** Es.

**Other:** definitely wanna look at this again.

**Me:** Y. Es.

**Other:** I know you're unsure. I don't if you already shared the link, but definitely, I'd love look it again.

**Me:** Y. Es, yes. Y. Es. Yes, yes.

**Other:** Yeah. I'll share it.

**Me:** Yes. Yes.

**Other:** We'll share that on Slack. So

**Me:** Y. Es. Y.

**Other:** it's in the last Yep. At the Slack. Yeah.

**Me:** Es. Yes. Y. Es. Yes, yes. Yes y. Es. Y. Es y.

**Other:** Clear. Thanks for putting that together. You guys.

**Me:** Es. Yes. Y. Es. Yes y. Es. Yes.

**Other:** Yeah. I've already made the file on the Figma as

**Me:** Y.

**Other:** well, and I've just sent you the link on

**Me:** Es. Yes.

**Other:** that. So

**Me:** Y. Es.

**Other:** access it wherever.

**Me:** Yes. Y. Es. Y.

**Other:** It didn't show the preview.

**Me:** Es.

**Other:** Interesting. Okay. Anything else we should discuss on this call?

**Me:** Right. Now.

**Other:** Nothing for myself.

**Me:** Y. Es. Y. Es. Yes, Sydney, I am going to DM you the doc I just put together for Reyhan.

**Other:** Okay. Sounds good. The only ask is tomorrow since we don't have stand up. Let's just drop in, like, what we're working on on that little, like, stack Slack update thing. Just so we can keep track asynchronously. Cool. K. K. Thanks, everyone. That's good. Dope. Thanks, Vedant. Stuff. Bye.

**Me:** Nice guys.
