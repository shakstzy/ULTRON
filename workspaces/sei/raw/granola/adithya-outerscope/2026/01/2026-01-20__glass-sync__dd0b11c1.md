---
source: granola
workspace: sei
ingested_at: '2026-05-07T04:23:57.244510Z'
ingest_version: 1
content_hash: blake3:c53180d767fedd9771c441981a3890ee85492b5be340ef930ac12257a3b151d9
provider_modified_at: '2026-01-20T21:39:55.133Z'
account: adithya@outerscope.xyz
account_slug: adithya-outerscope
document_id: dd0b11c1-c63c-402c-bdfd-01aab0545f0e
document_id_short: dd0b11c1
title: Glass Sync
created_at: '2026-01-20T21:06:41.114Z'
updated_at: '2026-01-20T21:39:55.133Z'
folders:
- id: 3ca3cb55-d6e1-49ef-961a-8ba2469731a5
  title: SEI
creator:
  name: Adithya
  email: adithya@outerscope.xyz
attendees:
- name: null
  email: chetan@seinetwork.io
- name: null
  email: jay@seinetwork.io
- name: null
  email: cody@seifdn.org
- name: null
  email: paulg@seinetwork.io
- name: null
  email: cody@seinetwork.io
- name: null
  email: campbell@seinetwork.io
- name: null
  email: jeff@sierrawood.io
calendar_event:
  title: Glass Sync
  start: '2026-01-20T15:00:00-06:00'
  end: '2026-01-20T15:30:00-06:00'
  url: https://www.google.com/calendar/event?eid=YW90MTl2dnN1bWM1cnZ0cm04ZXUxNHUzcHJfMjAyNjAxMTlUMTgwMDAwWiBhZGl0aHlhQHNlaW5ldHdvcmsuaW8
  conferencing_url: https://meet.google.com/teo-dbhh-nhb
  conferencing_type: Google Meet
transcript_segment_count: 239
duration_ms: 1987840
valid_meeting: true
was_trashed: null
routed_by:
- workspace: sei
  rule: folder:SEI
---

# Glass Sync

> 2026-01-20T21:06:41.114Z · duration 33m 7s · 8 attendees

## Attendees

- **Adithya** (creator) <adithya@outerscope.xyz>
- <chetan@seinetwork.io>
- <jay@seinetwork.io>
- <cody@seifdn.org>
- <paulg@seinetwork.io>
- <cody@seinetwork.io>
- <campbell@seinetwork.io>
- <jeff@sierrawood.io>

## Calendar Event

- Title: Glass Sync
- Start: 2026-01-20T15:00:00-06:00
- End: 2026-01-20T15:30:00-06:00
- URL: https://www.google.com/calendar/event?eid=YW90MTl2dnN1bWM1cnZ0cm04ZXUxNHUzcHJfMjAyNjAxMTlUMTgwMDAwWiBhZGl0aHlhQHNlaW5ldHdvcmsuaW8
- Conferencing: Google Meet https://meet.google.com/teo-dbhh-nhb

## AI Notes

### Customer Research & Outreach Strategy

- Chetan conducting customer discovery calls this week

    - Jonathan at Databricks (Chief AI scientist from Mosaic ML acquisition)
    - CISO of Glean (deep security background)
    - Jabali startup (early stage, seed/CDC)
    - 6-7 additional prospects in pipeline from Chetan’s network
- LinkedIn outreach campaign needs immediate cleanup

    - Adithya to manually review Series A/B/C company lists line-by-line
    - Focus on quality over quantity - targeting next 5-10 conversations vs. 50
    - Top 100 list had 90% irrelevant companies (AI video/image/content generation)
    - Only 7 companies marked as viable prospects from initial review
    - Chetan will provide final vetted list of 50 target accounts
- ICP clarification needed

    - Current focus: companies building models touching PII data
    - Need better alignment on data/model provenance value proposition

### Product Development Updates

- Two core verticals in development

    1. Trusted execution (TE) infrastructure enablement
    2. Model/data lineage tracking system
- Technical progress

    - Sam working on Kubernetes setup for TE hardware integration
    - Paul building MVP lineage tracking via MLflow with CLI
    - GPU instance quote: $13k/month for 8-GPU bare metal setup
- Customer validation insights

    - Pinterest: need to understand data impact on model weights during training
    - Adobe: want lineage tracking from checkpoints back to source models
    - Both spending ~$2M annually (4 engineers + infrastructure costs)
    - Adobe scaling investment for customer-facing brand products
- Competitive differentiation focus

    - Analyzing Weights & Biases and CoreWeave offerings
    - Identifying unique value props around dataset difference detection

### Fundraising & Pitch Preparation

- Investor meeting timeline

    - Intro calls: next week
    - Formal pitches: first week of February
    - Target close: end of February
- Pitch deck structure priority (per Jeff’s recommendation)

    1. Founding team credibility
    2. Why now / market inflection points
    3. Product vision details
    4. Customer engagement validation
- Current investor pipeline

    - Mostly junior associates reaching out (90%)
    - Several calls scheduled for next week (targeting 5 intro calls)
    - Majority are inbound inquiries, 2-3 from existing network

### Action Items

- Chetan: Complete line-by-line review of Series B/C prospect lists, provide vetted target list
- Adithya: Complete Databricks go-to-market evolution research using timeline analysis tools
- Cody & Paul: V1 pitch deck completion by Thursday (working session tomorrow morning)
- Paul: Continue competitive analysis on lineage products, send screenshots of current MVP
- Team: Assess pitch readiness by Thursday/Friday to confirm next week investor calls

---

Chat with meeting transcript: [https://notes.granola.ai/t/c57c893f-2c6e-4f92-bd85-a4c536905e7b](https://notes.granola.ai/t/c57c893f-2c6e-4f92-bd85-a4c536905e7b)

## Transcript

**Other:** He and I, we're going to jump on a call with Jonathan at Databricks. He's a chief AI scientist. So he came through the Mosaic ML acquisition, so I'm looking forward to that call tomorrow with him. We have a call with the CISO of Glean. He is like, a deep security guy, so it's going to be great to kind of get his insight. And then I wanted to get into the startup phase. So there's a startup called Jabali. Very small company there. Like seats, cdc, kind of stage. So I'm talking with them also later. And then just to wrap up. And I have like fillers out for the next six or seven of them that I've listed in the work in progress side. So hopefully I'll get these two, maybe three more conversations this week to not have to bet Jay. Are all these folks from your network? Or is it from, I guess, outreach that Cody and Adyav owned? This is all my network. I'd like to figure out how we can have the outreach be more effective. I'm guessing that's one of the talking points over here. Anyway, so let's. The next thing. So, Adi, Cody, you guys, the LinkedIn thing we've talked about for a few weeks now. I think we landed on a plan, but we have not been able to kind of action on it. So, Addi, can you jump in? Like. I made a couple of very specific requests around cleaning up the list for series A and B. And maybe even crc companies.

**Me:** Yes. The initial list, I agree. I think was a bit sort of focused on sort of regulatory compliance policy. Instead of that, I think the Series B and C list are kind of more cleaned up to focus on exactly sort of what the ICP that you were targeting is. On top of that, I think sort of the most straightforward way here would either be sort of you or I sort of directly sort of messaging folks at the initial topic.

**Other:** Sorry to interject. So we came up with that list last week. My ask was for you to actually go line item by line item to actually review that. Because when I did that, for the ones that were listed in, like, whatever was the top 100 list, I realized that vast majority of them, 90%, were not relevant. To what we're trying to do. There were a whole bunch that seemed like just vaporware kind of stuff where AI generated videos, images, content. Like, I just didn't feel good about us kind of doing a mass outreach using modeling account for those class of customers. So again, I think I made this very specific ask that I need for you to actually go through, line item by line item, all the companies that you shouldn't take you more than like an hour to actually go through the CSB and SE list. And identify by looking at their website, which are the ones that we should actually reach out with. There were some, like, mass market email campaign where we were blasting from, like a no name account. I think we could have been a little bit more liberal in all these outreaches, but since it's coming from me, I want to be very mindful of, like, you know, who we connect with. The focus here needs to be like quality, not quantity. Right? I don't need for us to kind of line up the next 50 conversations. We just need the next five to 10.

**Me:** Yes. I think the right place to start there is like, probably the Karthik list that I'd thrown together. So there's a list at the top 30 folks probably from that list that we should start with the outreach for then.

**Other:** What is this card thinking? We're shifting context now. What is this contact list.

**Me:** The Karthik, like, AI list, sort of. So he had sort of.

**Other:** No, no. Let's stay on topic. Right? So let's stay on topic. The series A, B and C that we have talked about, my ask was you actually go through line item by line item and let us know green, yellow, red marking, which other ones we should actually connect with.

**Me:** The Series B and C list should probably align better with sort of what you were looking for with the icp. I had gone in and sort of revised those manually as well.

**Other:** I've got a very specific Ask Adya. I'm sorry about this. But I need for you to review their website and their product portfolio, line item by line item.

**Me:** Yeah, I'm happy to, but the existing list should probably be sort of a revised copy. I've gone and sort of manually reviewed sort of most of them. Again, sort of the ICP that we had discussed.

**Other:** Can one of you guys pull up this list, by any chance? I think that would be helpful to see it. Yeah, I can do that. And yeah, from my understandings, next steps after our last call were to have Chetan hand over his LinkedIn. Have that script. I think you did both of those. And if we could align on just, you know, these first 25 to 50 folks to target, those messages should have been sent out late last week going into early this week. Yeah. So let's start with this tab, right? The top 100 list, right? So I went through each of this. And that's majority of them are not actionable. Like, it's just going to be not a good use of our time for us to kind of reach out to them. Right. And then. The ones that you guys see in green. So, 1, 2, 3, 4, 5, 6. Seven turned out to be, like, valuable enough for us to kind of reach out. And my ask was for series B for us to do the same thing. Because I don't. Because I think add either way you have come up with this list is like running through some sort of database that has access to it. And maybe you're just prompting Cloud or OpenAI to kind of come up with you know how the fit might look like that is not that did not work for the top 100, right? Because again, the fit. When I reviewed what these companies were like, little to none for vast majority of them.

**Me:** So I believe the ICP that we discussed was essentially sort of companies that are building models of any kind. Right. Is that correct? That are needing some form of.

**Other:** You have been collaborating with us on this project for several weeks now, right?

**Me:** Correct.

**Other:** What is your understanding of, like, who the ICP is?

**Me:** Yeah. I mean, so the two sort of like core moats of sort of. The product is that we're focusing on sort of data and model, sort of provenance, sort of the ability to sort of track where data is coming from and where sort of model training is occurring. And so as such, you're wanting to sort of get at least what my understanding was, Cody and I were sort of focusing on consumer facing, sort of model companies, right? And so that's primarily sort of the list that I put together. All these companies are touching PII data in some form or fashion, which would primarily be sort of what we're targeting, in my opinion.

**Other:** Okay. Sorry. I'm still struggling with it, I'll be honest. So let's take a look at this. Right, so this is the first link that we have on series B. What we think is a value in connecting with this company. It looks like they're not even based in the US probably based in South America somewhere. And what can we tell from their website that might give us confidence that they're indeed doing something that's going to be valuable for us?

**Me:** They're LinkedIn. It indicated that they were backed by some decent folks, so I thought it might be worth reaching out.

**Other:** Okay, well, in this case, I would mark this as yellow. Like, I would not spend cycles in kind of reaching out to them, right? Let's take a look at the next one. Okay. What are these guys doing?

**Me:** So, I mean, it's identity and credential management, which is like, pretty directly PII data, which I thought would sort of affect what we're doing.

**Other:** Yeah. Anywho, you know what? Let's take it offline. Since we have limited time. What I'll do is, like, I'll go through these line by line and just identify. And then Cody and Adi, I'll just give you a list of, like. Okay, Here are the 50 accounts that I would. Want us to go after. And then you guys can take over and kind of run with it, starting to borrow money. Does that work?

**Me:** Yeah, And I mean, Chetan, I'm also happy to, like, sort of schedule a 30 minute with you to explain sort of my logic.

**Other:** 30 minutes. Adi. Like, the thing is, like, reviewing these things, just making sure there's a good fit takes time. Like when I went through the list for the top hundred, it took me about an hour or so. It was not that. So 30 minutes is not going to be that productive. Especially if you want to go through the Series B series stuff, right? And I have a fairly good understanding of the product and the value proposition. So I guess I should be pretty effective at kind of running through this lesson, coming up with a list of that I want you guys to action on.

**Me:** Sure.

**Other:** A similar note. We had talked about doing a deep dive on the databricks go to market side and just better understand, you know, how they executed over the last ten years or so. So Adi, I know you had that action item to kind of and Cody had given you pointers around using Hourglass or some other tool to just kind of look through how their product positioning and portfolio kind of evolved over the time. I just want to check in on that, if you've been able to kind of make progress on it.

**Me:** Yeah, so I'd sent like sort of a databricks, like product summary, I think, in sort of the.

**Other:** That's not what we need. Sorry. We already discussed that two weeks ago, right? Outside of that initial dump, we probably have not done any further work on that. It shifted to, you know, these initial product calls. Okay? How did you recall the action item, though? Are you able to kind of work on that today?

**Me:** Yeah. I mean, I'm happy to get back to you on that, for sure.

**Other:** Okay? Sounds good. Thank you. Okay, I'm going to switch back. Jay. Yeah, on that, Doc. Can we just have the source of control, the outstanding action items, and we can at least use that as a source of truth for everyone else on the team. Yeah. Let me take notes here. I'll share my screen so that everybody can see what I'm typing. Okay? And Cody from your side, do you feel like you understand the action items well enough? To work with Adi on these. Yeah. Cool. Do you want to continue, Chetan? Yeah, let's go. So, Paul, I think we should update the team on some of the work that. You have been doing. Semir has been doing. I've got one ask, which is a little bit of a reach. To be honest. But between you and I, Paul, I think we do have high confidence in the product value by end of the week. What I mean by that is we had agreed that starting next week, we want to start having some of these intro conversations with investors, like going into that, working on the pitch deck. I would prefer for us to, like, give ideated, like, two or three things that we think we want to build and have, like, a decent position on it. But I would prefer to kind of close on it, you know, through, like, us evaluating competitive offerings or customer workflows and pain points and things like that. Does that make sense from a gold perspective? I think it's a great. I think it's a great goal. We've been iterating on these basically two vertical ideas for the last couple of weeks now, and I feel pretty strongly that they both have a good value prop. We definitely need to do a little bit more around the lineage piece and how that differs from existing offerings, which I'm doing right now. Do you want me just to give a brief of. Of, like, what we're working on right now? Yes, please. So what we're working on right now is again, we have these two things. One is enabling TE infrastructure and the other one is creating a system around how to track lineage of models and development process so that you can then deploy that ultimately on the TE infrastructure. Sam is working on on like base learning for Kubernetes setup at the RAW level so that we can start integrating this with TE hardware. Basically, the TE hardware is somewhat expensive, so he's doing base work, not using that. We are then going to deploy this system to some bare metal and then we can work through the confidential containers and some of the other systems that need to be run in order for the TE stuff to work. So Sam is working on that path right now. I have. I'm getting a quote back somewhat soon for a GPU instance with 8 GPUs on it so that we could even try multi GPU setup, etc. So that's coming today or tomorrow. It's roughly 13k a month for that bare metal machine. Jaython. I just found out. Pretty expensive. But maybe we need to do it. So that's in progress there with Sam. What I am working on is looking at the lineage side of it. So I've made an MVP based upon adding, like, lineage tracking to MLflow, and I have a CLI that we can use to work through that. And I'm also looking at the weights and biases product from core weave and looking at how they track and display lineage and seeing what we can do better there. I think the place that I've been sitting is. Is getting to the point where I want to know exactly what tool we could do that they can't do. That adds value. So that's what we're trying to get to. I think it might be something around being able to show the differences between data sets or something like that. Kind of detecting that end to end. So that's what I'm working on now. I can send you guys some screenshots or whatever if we want that today, Jay. Two questions on data lineage. The first of all is do we know how much like Pinterest, Adobe, these other guys are spending, or is that still kind of question mark from our side? We know roughly, like our team of like four engineers, times whatever is the bone rate and then the associated cloud infrastructure to go with the Jay. Okay? So. So, like four engineers, let's say 300 kilo on average, like 1.2 mil. Yeah. All up. Is going to be about two mail per year kind of thing. And both of them have, like, recently started this investment, Right. So it is quite possible that they start to kind of scale up. Their focus there. I think, actually specifically what your, your person at Adobe was saying with the work that they're going to be doing with brands, I imagine that's going to be a scale that is interesting. Yeah, yeah. This entire notion of, like, that's the other trend that I kind of picked up on, so. Graph database basically lets you have, like, relationships between different objects. And they definitely want a system that maintains that. A leadership for all the AI assets like data prompts, models X, Y and Z. Right? What, what Paul was alluding to is that Adobe has customer facing products, like they actually make products for marketers and things like that. So it is very likely that a lot of that work from like base enablement perspective. After they've addressed the needs of internal customers, we'll start flowing into external customers also. Right. There's a possibility that. If you're able to kind of come up with a service that addresses the V1 needs of Adobe Internal, that we could potentially partner with the platform team to offer something that plugs into their external customer, basing products Also underneath. Really cool. That makes sense. And that kind of ties into my second question, which is, is that are the data that Lineage needs for Adobe and Pinterest the same, or is it going to, like, vary company by company, and it's harder to build some specific product around that? It's going to be similar, Jay. The specific use cases that both of them identified were slightly different but overlapping. Still. Like Pinterest was around. Like, hey, I need to understand, like, during my training runs, What data is actually impacting the model's weights. Right. So from an impact perspective, What Adobe was saying was, like, when they actually do checkpoints during the training run, when, when they write those checkpoints, they want to have lineage of that checkpoint all the way back to the source model, so it's all related. But there are different aspects of the same of a similar problem, right? Like, once you have a mapping of, like, the models, the data, the training parameters, the checkpoints and everything, you get both of those benefits of being able to kind of train during the experimentation phase and then also doing the training phase. Okay, got it. And then for the pitch, this seems pretty separate from, like, the managed TE product. Do you view this as, like, somehow being able to tie both of these in together? Do you think they'd kind of be two separate products? If you need to, yeah. So I think we tie them together, Jay, like, and we want to still work around with the wording. So what I've been using in some of these customer conversation is like a verifiable trust and governance platform. And that overarching team maps to actually both of these specific use case and products. Like once they're able to trust your systems, fully understand, you know, what your data sets or your AI asset store look like and how it's kind of flowing through the entire pipeline. It starts to. It starts to resonate fairly well, at least with some of the prospect we have been working with. Okay? Got it. Yeah, that answers all the questions now. Then. All right, Cody, next thing is like, the pitch deck, and we have Campbell here, too. So here's how I was kind of thinking about that. So I had a chance to kind of talk to Jeff also about it this morning. What? What Jeff and I talked about was, with respect to the investors, Like, if you look at, like, all the things they care about, like, his recommendation was a priority as, like, the founding team. You know, what, what credibility they bring to the table, followed by, why now? Like, why are they deciding to build whatever they want to build? Like, what are some of the big, like, market trends? That are driving like an inflection point because of which something needs to be done. Then switching it over to, like, the specific product vision of the company. Like, what do we actually want to build? Get into that detail. And the last, from a priority perspective, was talking about, like, customer engagements and Lois and things like that. That, okay, we're not just kind of cooking up something in isolation. We're actually running it. Running it through customers and getting their feedback and things like that, right? So first off, let's discuss this overall priority, and then once we align on that, I think we need to come up with, like, an updated flow for the actual deck. And then start cranking. Right. So I would love for us to kind of aim to get a version one. Of the pitch deck by end of this week. It doesn't need to be like investor ready at all, but at least something that looks cohesive from, like, start to finish. Like, okay, we think we've got a story, right? And obviously there might be things we need to fix up. On the visual side, from the content side, things like that. So let me pause there. Jay, you want to jump in? I think that order sounds that also matches stays like when we did our series A matches, that it matches what we had as well. So I think that makes storytelling really easy. My main concern is going to be the point that I brought up before, around the three separate products maybe not being very cohesive. I think that one liner of like control and governance might not be the flashiest one. So we probably need to figure out. Yeah, tell the story around that. Let me take a note here, iterate on. Yeah. While you're taking that down, I would say to the doc, I linked in the chat here, scroll to the bottom. See initial deck structure that is very close to what you just outlined. Paul, like I mentioned, I could use some help of yours there. Me and you can put together just like a white, black and white version. We'll have Xander and Aaron, you know, put it into the actual design by end of week. But me and you, based on those 12 slides. Similar to what we did. Like day one. You know, of glass. I think we shouldn't there with us. Maybe we can do this in a working session. Chetan on a, like, I don't know, fucking tomorrow. Morning or Thursday. Yeah, let's do it. So here's. Here's what I was going to do, like. I was going to take the structure that you have, Cody, and just adapt it to what we just talked about. Like, you know, the four key areas that we want to hit. Today. And then on set of time for us to get together tomorrow morning. So that is better for for Campbell on his time. And then. Yeah, let's start hacking through. We can assign orders, we can track, like, specifics of what we want to build from a content perspective. And then get going. So let me take a note of that. Okay? Yeah. And the last thing I just want to cover is from an overall framework, from a timing perspective, the goal would be. To like intro conversations. Next week. Formal deep dive product pitches the first week of Feb. To actually close Spineffeb. Jay. So when you say intro conversation, I mean, the way this will probably work is the intro conversation is the same thing as the first pitch where they will ask you some high level product questions and then the second conversation will be with broader group folks and that'll be the quote, unquote. I realize that basically just. Is it my connection? Sorry, Jay. You were breaking out. I don't know. Probably the office connection. I was saying, are we on the same page with, like, that is basically the first pitch, and if it goes poorly, then, like, there won't be, like, the product P5 Conversation. Yeah. I got. Yeah. That's why I think this week is critical for us to just align on. The V1 of the pitch and make sure we have a strong connection on the product side. The founder story, the why now? I feel pretty good about being able to, you know, just make it super, super compelling for the investors, right? We just need to make sure we don't have job in connecting the dots from the vision down to the specific areas we want to investigate as part of a seed ground find find the PMF and then. Also highlight the customer engagements we have. Okay, two other thoughts there. First of all, is there a sheet where we can see which, like, when you have investor calls set up. Like maybe your last calendar or something. Yeah. I. I'm tracking stuff on my side, like in the neomorphic email domain. Jay. I've been using that. And I have a series all set up for next week. And I don't want to hold them back too much because many of these engagements, like, they reached out to me, like, two weeks ago, and I've been, like, consistently pushing it up. We can certainly stagger them. But again, I just want to make sure that I don't. I, I don't push it off too much. Right. And for one or two of them are actually two of these calls that I've had whenever I've set up the context, like, hey, We'll have a formal pitch. This is just an intro conversation. We're still working through the product specifics and the vision. And that has kind of worked well enough where they were like, oh, okay, we get it. We get your experience. We get the area that you work in. We would love to cut a Stay engaged. Right? So that's my perspective for the next week. Calls is like, to actually hook them enough so that we actually can get an hour of their time. The following week. Or the week after. And the other thing I want to be mindful of is, like, whatever calls we can do of meetings we can do. I would, I would like to see if I can do them in person. Not the intro calls, but the actual formal hour long pitches. Because again, in person conversation is always, in my opinion, go better than virtual ones. Yeah, I agree with the in person convos. It sounds like you're treating the intro call as like. A little bit different than, like, a core pitch. Probably like you should treat it as, like, the first round of the core pitches. And most of these guys, next week, they will ask you about, like, the product, and if you have good answers there, then they'll just move on to whatever the second round is with them. Okay? Yeah, there's no problem in leaving these folks on red for longer than you think. Like they are going to be wanting to sell you on taking their money opposed the other way around. So you can come circle back in like a month or so. Realistically, don't feel like you need to stay super close with them. If you leave them on red, ping them late Feb, like they'll, they will jump at the chance to jump on the phone with you. Okay, sounds good. So I should. Feel pressure to get on the phone with these guys. No. And I think to kind of just tie it all together. I don't think you need to rush having these calls. Like, they're not like some intercool. Like it basically is the first round pitch. It's better to, like, iron out your pitch and then talk to them two weeks from now versus having a bunch of them next week when it's not fully baked out. Like, pushing it back by week won't really matter. Like, yeah, if you push it out three months, then maybe they'll forget and be less interested, but another week won't really move too much. Okay. Understood. So let's see how this week goes. It is a shorter week. If by, like, Thursday, Friday, we don't feel good about, you know, how the pitch deck is coming along and our actual pitch, I'm happy to kind of move out those connections, no problem. Yeah. FYI, I'm going to be out. Sorry. Go ahead. These meetings you set up. Are they with people you had known before or folks that reached out? Jeff, these are all folks who have reached out. A few of them, like I would say two or three, have been folks that I've known for a long time. But vast majority have been inbound. Are they like these more junior folks at the fund? Yeah, vast majority of it's a 90% our junior folks. Okay? So put these into context. SaaS Venture Investing is like really mechanized, which you're probably aware of. Like, there are most skilled funds have like a pretty large team of like 20 or 30 associates whose job is to email every possible. Yeah. In existence. It is pretty low. Like you. You can get a couple out bats because they'll lose you in their CRM. Maybe some helpful concepts. Got it. Cool. That's it from my side. Any other topics? Yeah. The only other thing would be intros to investors in our network for Web2 investors. I think Jeff would probably be the right person here. So once you built up conviction on the pitch and like, some of these initial condos are going well, I think it's. I mean, certainly better to talk to people that are more tenured at these firms. So once you're ready, J. And Jeff can start helping out there. Okay? Got it. Cool. Yeah, we can certainly do that, I think. I think early next week. You know, once I go through a few intro conversations and see how they're going, we can. We can do a really quick assessment about, you know, our overall readiness to start hitting up our network. Cool. Okay? Again, just to reiterate the ones the things that I've had in yellow. Those are the goals for this week. Forget the target for the sea drone. Close. But the three core things. Lois, Paul, you and I to continue to chip away on the product side. And then for us to get, like, a V1. Of. Cody. I'm going to take a goal, or at least I'm going to take a target for. How creatures. I'm going to say. Five deep dive calls or five intro calls. Nine. 13 0. Seems pretty doable. Again. Fifteen that will have. Sounds good. Yeah, FYI, I'm out Friday just for everybody here. I'm reachable, but not going to be on calls. I'll aim to get with you and Paul the flow of the deck complete by Thursday when I sign off. And then we have Aaron, one of our designers, working on the deck. How to call with him today. And so he just needs to beautify, like, the template and we can add, you know, our content to it. Realistically, that comes early next week. Just knowing his cadence as well and what's on his plate. But realistically, by early next week, we should have a deck that's, you know, ready to roll with some. Some investors, so I can do my best to stick to that. All right, team, we'll end here. And, Cody, I don't think we need. Oh, you already canceled the GTM sync. Yeah, yeah, we're good. Okay? All right, thanks, everybody. We'll catch you guys later. Bye. Thanks. Thanks, everyone.
