---
source: granola
workspace: outerscope
ingested_at: '2026-05-07T04:23:57.244510Z'
ingest_version: 1
content_hash: blake3:4928324295bb49d760a2720f9f180f71249820c03fa9b139c9eac30f7525b5ef
provider_modified_at: '2026-05-06T19:32:29.949Z'
account: adithya@outerscope.xyz
account_slug: adithya-outerscope
document_id: 65b02b95-bda4-4e85-824a-cfbf099fa322
document_id_short: 65b02b95
title: AI infrastructure and social media automation strategy
created_at: '2026-03-30T16:56:38.399Z'
updated_at: '2026-05-06T19:32:29.949Z'
folders:
- id: 53c78f6b-58f0-4ad3-aa3b-8a45802f67b5
  title: OUTERSCOPE
creator:
  name: Adithya
  email: adithya@outerscope.xyz
attendees: []
calendar_event: null
transcript_segment_count: 477
duration_ms: 2024272
valid_meeting: true
was_trashed: null
routed_by:
- workspace: outerscope
  rule: folder:OUTERSCOPE
---

# AI infrastructure and social media automation strategy

> 2026-03-30T16:56:38.399Z · duration 33m 44s · 1 attendees

## Attendees

- **Adithya** (creator) <adithya@outerscope.xyz>

## AI Notes

### AI-Powered Social Media Strategy

- Automated content pipeline for Seatback

    - Scrape saved Instagram posts from Avery’s folder
    - Analyze content clusters and messaging optimization
    - Focus on text-based posts for X/Reddit vs visual for Instagram
- Podcast content extraction strategy

    - Monitor new podcasts mentioning sperm health
    - Extract quotes from speakers (e.g., “sperm is the new blood”)
    - Auto-generate X/Reddit posts from extracted content
- Cost comparison: AI automation vs €2,000/month intern

    - 10 Claude subscriptions = €200/month equivalent
    - No sick days, holidays, or performance variability
    - Higher quality, faster execution, broader reach

### Advanced AI Infrastructure Setup

- Current workflow capabilities

    - Auto-pulls meeting notes from Granola
    - Creates GitHub PRs and dispatches to agents
    - Self-healing system with nightly memory optimization
    - Auto-suggests new skills based on task failures
- Multi-agent debate system for medical accuracy

    - Custom LLM trained on IEEE research papers only
    - Agent-of-agents model with master dispatching to sub-agents
    - Reduces hallucinations through cross-validation
- Continuous content scraping challenges

    - Podcast/Reddit monitoring requires massive token usage
    - Estimated €30k/month in API costs for full implementation
    - Hardware solution more cost-effective long-term

### Hardware Requirements & Constraints

- Current laptop limitations: 8 tokens/second, 96GB RAM
- Mac Studio M3 Ultra (512GB RAM) - ideal but backordered

    - 60-80 tokens/second performance
    - Entire US stock backordered until summer
    - €20k+ on secondary market
- NVIDIA workstation alternative

    - 4x RTX 4090 cards = €16k, 128GB VRAM
    - Hundreds of tokens/second performance
    - Requires Mac for orchestration, NVIDIA for processing
- Proposed €12k build as interim solution

    - Upgrade path available when better hardware accessible
    - Future-proof for 2-3 years with proper GPU selection

### Business Applications Beyond Social Media

- Medical device development support

    - FDA-compliant research agent network
    - Trained on verified medical paper databases
    - Proactive consumer skepticism addressing
- Customer service automation integration
- Meeting-to-code pipeline already functional

    - High-level feature discussions → auto-generated PRs
    - Real-time implementation during meetings

### Next Steps

- Adithya: Create 3 hardware proposals with layman explanations

    1. €12k NVIDIA build with upgrade path
    2. Mac Studio option (when available)
    3. Full NVIDIA workstation setup
- Avery: Connect with Chris (advertising agency CEO) for AI optimization discussion
- Team: Source NVIDIA cards through network connections vs retail markup

---

Chat with meeting transcript: [https://notes.granola.ai/t/da201944-4107-4d6e-80b1-067028b2f60b](https://notes.granola.ai/t/da201944-4107-4d6e-80b1-067028b2f60b)

## Transcript

**Other:** Somewhat of product functions as well, then has accounting and people. So I think all of these functions enrolled are filled with people. Now we can go and say, hey, we build a tech enabled company, which essentially means that some of these people will use AI to improve some of the workflows. But then we can also get to a point where it's not tech enabling the humans, but it's a company that is more based on AI than what we currently know. So I think one of the questions is like, what would that company look like? And then the question is more. Technically, what does that mean in the day to day? And that was like one of the things I think that Avery said. So we were brainstorming today, you know, how can we set up social media? And one of the ideas that came up was like, how about, because for the initial phases of seatback, we don't necessarily need to create new content. We want to use content that's out there, understand how relevant the content is in terms of messaging. Optimize the messaging and then post that. Wait, tell them what you did this morning with claude to scrape all of our. Just so he understands. Yeah. So this morning, for example, what I said is like for claude to like log into Avery's Instagram account, and then he has a folder called sperm to look at every post that he saved in this folder to analyze every post and then to give us feedback as to how we can cluster that. And what that means in regards to seed boxes, you know, Instagram account, like what type of content should we be posting and what can we learn essentially from that? So if all of that was, you know, automated.

**Me:** I have that exact workflow setup for me running right now actually for eclipses account. So we have.

**Other:** Where. Does it do?

**Me:** So it basically pulls a couple. Like first it looks up sort of like online using an exit search and a fire crawl MCP search what the best hashtags are and what the best sentiment would be based on updated product like documented rewrites every morning based off of updated context on my Gmail slack etc etc it has a thorough understanding of our product revamped every morning so it reads any GitHub PRs that have happened any new slack messages that have occurred any DMS that I've gotten etc etc uses that to update its knowledge on the product based on that then determines the best hashtags to represent that product on social media uses that to pull the top 20 performing posts for the past week for those hashtags figures out what's good about those posts by downloading those videos as mp4s locally and then scrapes those videos frame by frame to understand okay what made it viral I've trained then basically like a skill on like just understanding what makes a video viral as well something that I'm implementing right now which is like straight dystopian bro like this should not even be possible right but like Facebook literally released a like model that essentially allows you to understand how a brain fires based off of visual stimulus and so I'm training a model right now on this to understand what makes a video viral and what parts of your brain fire when it seems a viral idiom crazy okay and so like literally you can now like tailor make a video to fire those exact parts of your brain type as well so that's kind of like what I'm trying to integrate to now that's like way like futuristic shit but like I don't think that's going to work even but like it could be cool it could be cool if it does but like like it's like it's so tough to be like oh shit like here Higs field like make a thousand videos and then understand like like like feature mapping from that to like exactly what makes a neuron tick like you can you can go the reverse way very easily like because like Facebook has the model already out you can literally just expose the model to like whatever high world video you want to see in your niche or whatever and then understand what like neurons are.

**Other:** 1. 1:20. Can you create a bunch of content and then see what it hit, what, what each.

**Me:** Yes but like it would require a stupid number of credits like is the issue like it would literally be like probably like just 500 and API cost just on that like one skill.

**Other:** I mean, you know what the reality is. I think video is very complex and I'm not even sure we like for stock specifically, I'm not even sure we need that complex right now. So if we were able to build a similar model, I mean one is for x and reddit, you know x and red very much male focused target audiences, very tech space. So if we're able to understand, I think that is a lot easier. In an ideal world, what I would love to do is for x and reddit. To run a content strategy that's based on one, for example one idea was let's look at any podcast that launches. That speaks about sperm. Let's then use whatever the person said in the podcast that say Steve Bartlett, use that as a quote and post it on x. So saying for example I didn't have Steven Bartlett said, I think that's the example a game is like sperm is the new blood. Which I think is so much easier than creating video content out the back. So the idea would be to have an AI, you know, look at, you know, all of the resources that's out there. Look at all the new content that's out and then based on that create post on X and reddit that are purely text. As opposed to creating video. And for Instagram. I don't like majority of the post that, you know Adrian, I have funnily enough saved. We're also not video content, but they were reels. So a couple different slides. So I think that as well they're not even pretty, it's something that probably you could set up as well. As an automated process where it continues to learn what's working, what's not working. And to then also engage.

**Me:** I mean that's that's more than possible honestly like it requires like just basic scraping of sort of like. It would require a ton of quad credits but that's fine dude I think we have plot max or whatever already so it's fine.

**Other:** I mean. The reality is like the same here, the alternative is to have an intern who cost 2,000 euros a month.

**Me:** Yeah exactly.

**Other:** So what is it?

**Me:** 10 claud subscriptions right there.

**Other:** Yeah, so what's the, what is the, what is the cost if AI was to do it?

**Me:** Yeah. Great. Great.

**Other:** Versus having an intern will also has holidays goes gets sick. It was like sniffing. I'm like you're getting sick. It's not. You know, someone who gets sick who has heartbreak who I don't know how to bad night's sleep who is distracted, you know, and this is where I think when I look at it from a cost perspective, yes, it might be expensive. But if we're able to set up some of that quality wise is better and faster and cost half. That's in my view there are two different things and the best thing would be an intern who was actually able to use some of these tools because you can't be as precise and analytical and far reaching as a single person as you can with what you're describing your setup, right? But you also there's no human touch to what the AI is going to do, which I think could add some value. But yeah, so I don't know, do you have any thoughts?

**Me:** Can you guys see my screen. I showed you this yesterday kind of.

**Other:** And.

**Me:** The multi agent debate thing bro I'm just bringing that back up again.

**Other:** I just had rock super heavy for $300 and it has this right?

**Me:** Oh bro are you serious?

**Other:** Yeah. Why?

**Me:** That's sick okay yeah Grock super happy is like mad.

**Other:** Have that topic here in rock cloud? And Gemini, not, not GPT.

**Me:** Oh I got gbts so okay fire dude that's that's super sick.

**Other:** So I've been like having them each run like.

**Me:** Look at that see he's literally scraping as you speak actually yeah anyways.

**Other:** So are we going to be able to use my grok login and my cloud login when we set this up, how does that work? Or we're going to run our own local model.

**Me:** Do you get API creds with super heavy.

**Other:** I don't think so. I don't know.

**Me:** Yeah you do.

**Other:** Oh really only $50.

**Me:** Oh fire that's more than enough bro that's more than enough.

**Other:** For how long?

**Me:** If we scrape. Like we could probably scrape like 20 or 30 searches a day. You know enough I guess. Yeah.

**Other:** Will be good for Twitter because they on Twitter.

**Me:** Yeah yeah of course.

**Other:** So, okay, so yeah, we can keep talking about this, but so we want to understand also and brainstorm with you like once we have this all set up on the hardware side and infrastructure side and can like send it to do stuff. What are some other things in different, maybe different departments of the company or whatever, right, that we can apply the AI to, does that make sense?

**Me:** I mean.

**Other:** Like this is really good for social, but like you have any ideas on some other sort of things for.

**Me:** Yeah yeah so there's like for okay I'll just like maybe scroll through here right like this is like all sort of the skills I've sort of given the AI for it to do so it can natively interface with like GitHub it can actually auto poll for like my my meeting notes like Granola it's like it's taking notes right now for example right like auto pulls from that and then creates auto creates to dos that then go on to the board right that then gets auto.

**Other:** You. Okay, that's a good one. So I can read all of our meeting notes.

**Me:** Yeah autonomously does based off the meeting notes so we don't even have to do it literally auto creates GitHub PRS and auto dispatches to agents and whatnot.

**Other:** And then do. That.

**Me:** It's dude.

**Other:** When I explained the lore what that means. So basically it'll have a meeting where Aditha could be talking at a high level about a feature with someone for the app or website. It'll hear that in the transcription of the notes and then start coding it and keeping and then saving the code files in the repository and shipping the product based on.

**Me:** Like.

**Other:** Right.

**Me:** Look babe literally as we speak bro that's actually crazy yeah yeah it's.

**Other:** Also by the way Laura was wondering if like the CEO of her advertising agency company could maybe talk to and maybe give you some CEO of Chris who's my co-founder in the advertising agency. He's launching his own company where he wants to invest into other companies and help them set up and optimize. Process and workflows with AI.

**Me:** Cool.

**Other:** So I said to him that I spoke to someone who is very inspiring and cool and he's like I'd love to talk to them so I'd love to.

**Me:** Yeah absolutely no I'd love to.

**Other:** Yeah he's honestly from a business perspective if I had to invest all of my money into one person but I'd probably still invested into him because he's a really, really special incredible business person.

**Me:** Yeah. Nice yeah no happy to chat with 100.

**Other:** What else besides meeting notes could we do?

**Me:** So bang this just happened right what the just okay so there's no new meeting notes to pull okay that's fine and then it like it auto heals itself like there's like a doctor script that runs every night that stores memories that deduplicates memories compacts memories it auto heals means it auto improves as well so it can like autonomously read what it did historically read why failed autonomously dispatch tasks to fixed skills as well auto suggests so if I give it a task that I can't do then it auto suggests agent creation as well. Then auto suggests new skills to create so this is a new skill that it asked me to create based off like things that I asked for it it's asking it's telling me why it wants me to create all that as well. Yeah what else dude.

**Other:** One bro.

**Me:** Yeah.

**Other:** Ther that I have that I was discussing with Averys well is like we're building a medical device.

**Me:** Yeah.

**Other:** With the intent is for it to be FDA approved for it to be you know medically solid and safe to protect us from you know lawsuits to ensure that you know nothing that we're doing is illegal obviously but also not you know can't be compromised. So the question is like is there you know is there like an like a medical AI as well that we can use as a baseline that gives us different messaging is that something that you've seen or heard or what's the is there like doctors intelligence. Or you know. Like laboratory acts like I don't know more from the medical perspective.

**Me:** Do you mean like an llm that's specifically like tailored for. Me?

**Other:** Crawling research. I don't know like not even like yes crawling research but also you know how doctors are always quite elite in terms of their knowledge and everything that they know and then it's like not they're not normal humans. I just wonder if there's a way to. You know, AI what a doctor could do. Like the optimized doctor like someone who knows more than your average doctor because he has read every single paper and he is able to compare every paper. And he's not, you know he didn't go to med school 10 years ago but he went to med school today like someone who. S yeah because I think a lot of the times when you use AI like the. What's it called like people people say like oh it's not true is not legit it's not an actual doctor doesn't know like what is the way that we can save the company or be like as protective and as safe as possible to have a setup that allows us to have an AI as if we had, you know, a board of doctors that is as reliable and as you know accurate and as. Research knowledge. Does that make sense or does it not make sense at all?

**Me:** Like ish kind of like just to clarify like are you basically saying you want a team of like research agents I guess in a way that I like.

**Other:** Maybe? Yeah maybe it's like a debate but I just want to make sure that the knowledge that they're bringing in isn't something they're making up that is actually like research that is only based on like. Accurate papers. Or that they're able to challenge the papers the same as a doctor would or I guess senior yeah, we probably need multi agents to debate each other and cite sources and stuff.

**Me:** You just buzzworded me didn't you for a multi agent.

**Other:** No what are you talking about like where grok has the different agents arguing.

**Me:** He buzzworded me.

**Other:** That's in grok that's a feature of drug that's not a buzzword no, but I wonder if we can set that is there like medical AIs for example you know that are based and I don't know how they work that are.

**Me:** Okay. He's actually not wrong I'm just like I'm just poking fun.

**Other:** Yeah no no it's fine you can be used to take criticism you need to work on that he's not he's not good at taking no but like you know what I mean where it's like maybe.

**Me:** He's like. Left the call man that's hilarious.

**Other:** You're. You did he's like bye bye you know but maybe there's like a Harvard I don't know like a harbor trained AI that's like a medical one that you can license because I know that there are those like models that are accepted for their medical acumen.

**Me:** To be honest there is.

**Other:** I have no idea.

**Me:** Like there's no way to control hallucinations there's the only way you can limit these is by using like a series of agents like that seriously process like sort of information meaning like they each get their information from different sources and then kind of conglomerate and like an agent of agents model like one mastery agent that then like dispatches jobs to a bunch of mini agents actually very similar to the process I have right now but it would be a dedicated research agent so think of that's like a spider web right one master dispatches it to the sub agent the sub agent is now a master of a bunch of other sub agents right etc etc and that's how you increase accuracy and you can have like end levels of this stack happening it just depends on how much context and token windows you need and that's why we're getting powerful hardware to run all the shit is because you're going to eventually like 80 agents running like concurrently type thing which takes a ton of ram right.

**Other:** I mean. Let's pretend like chat GPT and Groks were like medically accepted AI. Tools my wording probably sucks like they don't take like any word that I'm saying for like and imagine all of them from like society were accepted for their medical knowledge because they have certain limitations I think what she's saying is a custom LLM that's trained on the medical data which actually exists.

**Me:** Now you're chilling yeah. Bro she's basically like just wanting to limit hallucination correct me if I'm wrong your Lara but she just wants to limit hallucinations from like agents she wants to make sure like all the output of this is not garbage it's actually like medically accurate type.

**Other:** Yes. And I would love for the I would love you know for us not to rely on a single medical agent but for them to discuss to have like the best possible outcome.

**Me:** Yeah that's that's so that's literally the the debate boardroom thing I had like going on here that I was showing you guys exactly that to implement yeah technically it would.

**Other:** Yeah. But. I would love for the boardroom to not be you know like made up agents as a sense of like hey pretend like your XYZ but for the agent to be based on an llm that is accepted by.

**Me:** Just.

**Other:** The research world but I feel like these are all accurate enough that.

**Me:** Yeah that's not a thing actually I don't think there's like a specific model that is necessarily what what Avery is saying is right where it's like there's open source models that are custom trained on only IEEE research papers for example.

**Other:** Instead of being trained on the whole internet like like Claude and Grok and everything they are just trained on like the all the corpus of medical knowledge from the internet so they're really good just to ask about medical stuff but not general purpose. So like for our AI chat bot in the app. Which recommends things will need to train it on something like that I think okay would it work that we for example.

**Me:** Not exactly but yeah almost like basically like it's basically like think like Kimmy K2 bread or Kimmy K 2.5 which is a large source model that is actually trained on the entire corpus of the internet right in order to have general purpose reasoning tasks and logical inference and then you take that and then fine tune it with like a smaller corpus of data like IEEE research papers so that it now has like think about it is like almost like a chatbot interface for like a giant corpus of like research papers that's basically it giving it like custom context.

**Other:** No.

**Me:** You know.

**Other:** Is there. I'm not sure how this works but like because if I want to download medical paper sometimes I can download them and there's no problem I can access them and sometimes there's like a pay wall between me and the medical paper is there like one medical paper database? That we could for example scrape because it has all medical papers in the world I don't know they're making us up. As a foundation.

**Me:** There's a couple but I'd have to like rank them honestly by like relevance to us type thing but.

**Other:** I'm just drawing in ideas on things that I'm like.

**Me:** Yeah.

**Other:** I'm just thinking because if I were a consumer and someone would tell me hey. Because getting medical insights from AI still is something that I would assume consumers were skeptical about. So if we're able to take the skepticism and confront it proactively as to how our AI is different to your average chat GPT or like Google I don't know that you know thing. That would help. But I'm just like thinking. I mean okay. But I feel like also it's so easy to get off track with the things that are so important because there's so many cool things that you can do so I'm really enjoying these conversations because I'm also.

**Me:** I think first thing we do is like implement like I think the more business right like the immediate like okay what's actually going to move the needle what's actually going to help us out on a day to day and then we like start thinking about like some of these longer running tests where it's like it's going to take me a while to set this up too like this is like a pretty non-trivial task like you know from like a coding perspective for sure like it's but you know I think like the more complex tasks like deep research agents all that stuff will definitely like we'll definitely hop it's just like I think deprioritized for you know just very immediately I already have a lot of this shit built right so I'm just going to try and implement this like asap as soon as I get the laptop like we'll have that up and running within like you know two or three days hopefully is what I'm hoping.

**Other:** Foundation. Yeah. Yeah. We also want to scrape all of the podcasts and content out there about sperm and like constantly be gathering that knowledge and then also read it there like hourly posts and some subreddits about people who've used yo or like gone to the doctor for a sperm test and if we can gather all.

**Me:** Back studio bro like low key bro. Like that's like.

**Other:** There's literally none available online or what's the deal?

**Me:** Yes dude like if we're having continuous scraping and shit that's going to be like insane token streaming we're kind of clipped like literally.

**Other:** Trying to do that?

**Me:** It's like legitimately.

**Other:** I don't get why you can't do this in the cloud.

**Me:** It's going to cost way more you're going to spend like 30k in API credits a fucking month you might as well just buy like a Mac from eBay out right at this point and that's like stupid because it's just like expensive.

**Other:** Like. How much do we find that for?

**Me:** That's 20 racks bro for that price we should be considering yes we should be considering in video like hardcore chips like honestly.

**Other:** Okay how much two laptops plus the Nvidia chip. How powerful is that compared to the maxed out Mac.

**Me:** The max to last double the ram.

**Other:** As the two left so four laptops is equivalent.

**Me:** P literally. Bro yeah. Like it's like kind of dummy like how like powerful yeah it's like that's why everyone wants it bro even every link you sent me today on eBay there had like 530 people viewed like 20 people has in bro what.

**Other:** Yeah. It was either divide this like two months ago.

**Me:** Bro we needed to buy this like four months ago bro like literally dude there's like guys selling a Mac studio for 30k right now literally and he got it like he got it to his crib like I think delivered March 27th three days ago.

**Other:** Okay, so we can use the two laptops for like three or four months and then get the. Mac mini.

**Me:** We're not going to have. Like yes we're not going to have like all of this implemented though because there's just no way I can fit that on the ram like literally deep research agents alone are probably going to have like an instance of Olama running which takes up like probably about 70 gigs of ram we have about 96 square disposal.

**Other:** Okay question like a step back. What is the like. What does it look like if like nine months down the line. We want to have social media essentially running by itself in the sense of like scraping the internet every day understanding what's happening autoresponding on reddit Outer posting on tiktok I'm not sure those are like the text ones I think are easy Instagram probably I would still have a person post but like scraping the internet then having. You know a really deep understanding of all new resource that's coming out blah blah blah like what do we and then also having it the day-to-day stuff running with like meeting notes and to do's and updating so sorry. As well as then customer service also running entirely through AI. Like what is the setup that we need at that point in time? And how can we. Hardwareize and how can we ensure that we're setting ourselves up in a way now that we're able to just add on as opposed to having to scrape and replace. Like would I think the answer is right right Adithya will be we'll have that in nine months basically the product that we really need is back order until the summer like May like June or July so within.

**Me:** We either. Double the premium we paid double the price of apple to get it instantaneously which solves problems.

**Other:** The product isn't available or what's the problem it gets backward because everyone's trying to buy it so yes and in nine months we'll be set. In a different country yeah I was wondering the same thing like from India.

**Me:** I tried setting my VPN to literally every continent in the world bro.

**Other:** For example.

**Me:** I couldn't find this thing dude.

**Other:** We can okay.

**Me:** Literally yeah like it sucks. Like yeah.

**Other:** Let me ask like even through like when you ask apple directly.

**Me:** I called them.

**Other:** What is it yeah, I think it's backwards.

**Me:** All the entire us stock of back back order.

**Other:** Let me email the German guys as well what is it called that we need.

**Me:** Okay. We need a Mac Studio 512 gig.

**Other:** To put it in the whatsapp you put it in the what? Studio as an m3.

**Me:** M3 Ultra 512 gig ram.

**Other:** Capital r a m. R a m. Yeah.

**Me:** See this like an infinity dude. You can't find it anywhere.

**Other:** I And we don't need M4. Yeah. As

**Me:** M three ultra has higher memory bandwidth, bro. We need a

**Other:** Okay.

**Me:** I wish we could just have the m five ultra out right now so you could just, like, fall out.

**Other:** When does that launch?

**Me:** Probably July, August, which is, like, too long.

**Other:** Okay.

**Me:** And and it's gonna be two months from then because, like, no one's gonna get it instantly. So we're we're gonna get it to in our hands in September, October, which is fucking way too long. Yeah. I fucking hate this. Yeah. Literally all weekend, bro. I've just been looking at, like, shit, dude. Like, I actually like, this is so stupid. I know. I I think we just, like, either like, like, I just because Laura's, like, bro, if

**Other:** Okay.

**Me:** if you wanna add on this shit, like, we just build a PC, bro. Like, we just

**Other:** Yeah.

**Me:** start stacking up NVIDIA cards. Like, you know,

**Other:** But why don't we why why don't we do that?

**Me:** Cards are pretty stupidly expensive right now. Like, you basically if you want, like, a $50.90, you'd probably be paying let me look up cheapest $50.90 right now. You're probably paying yep, four racks.

**Other:** And how many do we need? Let me ask. Like,

**Me:** Cheap.

**Other:** How many would we need?

**Me:** 32, 32, 30 like, three or four of these.

**Other:** Okay.

**Me:** Yeah. So it starts to get bright.

**Other:** And that only gets us to one twenty eight or what?

**Me:** That gets us to if you got to dude, you get four of these? If you have, like, lucky four of these, like, that would be stupid config.

**Other:** That's 20 gram.

**Me:** Like, that would actually solve all of our problems. But, like because then that that because that would put you yes. But that would put you at $20, and you're your, but that would put you at one twenty eight gig VRAM. The thing is, like, one twenty eight is enough to host Olama, like I mentioned. And it would also have, like, stupid token speeds. And so at that point, like, you can start paralyzing tasks.

**Other:** How much faster is the ideal setup from the setup?

**Me:** The laptop, you're looking at, like, eight tokens per second. A Mac Studio, you're looking at about, like, 60 to 80 NVIDIA chip, you're looking at, like, the hundreds pretty much.

**Other:** Where do you order the NVIDIA chips from?

**Me:** I'm just looking at Amazon right now.

**Other:** On Amazon?

**Me:** Yeah. Yeah.

**Other:** Is that the retailer there overcharging?

**Me:** Dude, yeah. It's, like, it's fucked right now. Like, the GPU market is fucked. You know?

**Other:** This is stressing me out. I'm like Yeah.

**Me:** I I've been spread all fucking week. I literally

**Other:** We need to find someone whose company has, like, thousands of these chips and have them just give us

**Me:** Dude, that's really what you need to do is just, like, ask

**Other:** yeah.

**Me:** the discount from one of your boys that just has a server rack in his crib, like, literally.

**Other:** Yeah.

**Me:** We need a damn server. Literally to run this shit. Like, there's no other way, like, type thing.

**Other:** Yeah. We need to think of someone who runs it in. Like, a physical server?

**Me:** No. No. No. Like,

**Other:** So, basically, they have stacks Yeah. Of these cards graphics cards. Right?

**Me:** he still didn't like it. The power equivalent to a server is what I'm

**Other:** Like, Elon's built, like, in his thing. Like, an entire giant data center stacked column by column, the entire floor, right, with these chips. We need four. So someone's company probably has, like, a 100. Elon's has, like, 500,000. OpenAI has, like, a million chips. Right? Cloud has, like, a million chips of these things. We need, like, four.

**Me:** Walmart Walmart has a

**Other:** Right?

**Me:** four rack, this thing, dude.

**Other:** My dad's company has them, but I don't think he could get them to, like, just give us jokes. I mean, I'm so sorry. Like, I don't think I have any friends who I probably do. I'd have to think and then convince Take one second.

**Me:** Even the

**Other:** What's your

**Me:** 50 nineties, bro. Give me them 50 nineties. Architecture, buddy. Straight up, bro. It's act

**Other:** We're

**Me:** lit, bro. Like, it literally got released, at two k, and it's literally minimum four k right now. That's so stupid. The fuck. What if we just chained up, like, fucking a stupid number of 50 eighties?

**Other:** Like, how many?

**Me:** Thinking.

**Other:** Walmart has them.

**Me:** No. I'm look oh, no. I'm looking on what do you call it? Amazon a and f.

**Other:** But you're saying the max Studio is cheaper, but it's just not in stock.

**Me:** Dog, yeah, bro. Like,

**Other:** Okay.

**Me:** you know, it's just

**Other:** Got it.

**Me:** it's a very unideal scenario. We should've yeah. If we had bought, like, hardware, like, literally, three months ago, it would've been half the price.

**Other:** Okay. Isn't it better to buy four NVIDIA chips than two or whatever and one chip, or what's the deal? Can you how does that work?

**Me:** Laptop for orchestration. Even if you had the NVIDIA chips, OpenCloud runs way better on macOS. So regarding

**Other:** I see.

**Me:** you need a Mac base,

**Other:** Okay. Got it.

**Me:** the NVIDIA chips would just be, like, more of, like, a like, think about it as, like, a server. Literally. Right? Like, so I'd basically just expose an IP address to it, and then I just route tasks to it, you know, essentially.

**Other:** Yeah. Yeah. I got

**Me:** So

**Other:** it.

**Me:** the computer basically on the NVIDIA chips, the Mac is just orchestrating tasks to that point.

**Other:** Got it.

**Me:** The the local visual model probably running

**Other:** I don't think that computer chips now. But they might be able to help us. Or maybe, like, he's just like a startup who's, like, going broke. No. I'm serious. Like, he's, like, no. Maybe not, like, they have, like I'm sure I know people with the chips. I don't know if they would be willing to sell them to us.

**Me:** They like, there's, like, no yet. Like, they they give it they give it to us at cost, honestly, and then probably before.

**Other:** You

**Me:** Regardless.

**Other:** Okay. Can you send me the link so I can take look, like, on WhatsApp?

**Me:** Yeah.

**Other:** Thanks.

**Me:** Yeah. Yeah.

**Other:** We gotta hop in, like, three minutes. We have a VC meeting.

**Me:** Okay. Fire. Fire. Yeah, dude. Like, our our biggest like, the rest of the PC build

**Other:** Okay.

**Me:** is gonna be, like, a grand. Like, literally. Right? Like, it's best GPU that's fucking us right now. Yeah. It's an ideal But it does have it has d u r seven. We'd be future proof for years. Like, literally. Like, that's, like, the top of the line. Right?

**Other:** We wouldn't need to upgrade to the Mac Studio or what?

**Me:** If we had a yeah. If we had an NVIDIA fucking, like, like, workstation four, like, fifty nineties, we wouldn't have to touch anything for, like, the next couple So, like, that's more than enough for inference.

**Other:** Why wouldn't we need to upgrade it?

**Me:** Because that's that's super crack token streaming,

**Other:** This summer? Okay.

**Me:** and it has, like, like, cute like, cool architecture. Like, Blackwell, like, if you look at, like, the twenty nineties, they could still probably, like, kinda run local models right now. Right? But, like, there's a very, very big stretch, and then you're

**Other:** And the cost is gonna be what? Almost 20 k?

**Me:** I gotta look at alternatives, I don't think that's, like, you know, justifiable.

**Other:** Okay. Okay.

**Me:** I don't think that's justifiable. What we could do low key is is have, like, a stupidly powerful build for, like, like, 12 k and then upgrade NVIDIA chips if we find it Like, we actually find the agents are actually doing shit, like, for us, and, like, we find it useful. Then upgrade later if we need more power.

**Other:** How much does that cost us in the meantime, extra 12 k?

**Me:** Yeah.

**Other:** Okay.

**Me:** Probably, like, a a dual

**Other:** And then we have to pay how much to upgrade it, another 16

**Me:** no. Another like, it just depends. Like, if you wanna, like, if you wanna upgrade, like, your chunk, like, the newest $60.90 and whatever the price is then. Right? Like, if you wanna chunk another, like, $50.90 and you get, like, an extra 32 gigs, which allows you to run more powerful models. That's it. So like, the more the more of these you parallelize, more powerful models you can run. Like and single video chip will outbeat any fucking, like, thing on token streaming because it has CUDA cores. So think about, like, an NVIDIA's Arari. Right? Like, it has, like, no space in it. Right? But, like, it can go crazy fast. So you can run very, like, what do you call it? Like, stupider models. They're basically quantized models. You run stupider models, but very quickly. You have more of these. Okay? You stack, like, four, like, worries. Okay. Now all of a sudden, can pack up and move. Whatever the fuck, right, type thing. Like, you actually have, like, some carrying capacity. And now you can actually run something. The Mac is, like, literally a fucking pickup truck. Okay? This shit doesn't move. Okay? But it has a crazy carrying capacity. This is an insane analogy, bro. I should actually tweet out about this. Wait a minute. Hold on. Wait. Actually, it's a cracked analogy. But, like,

**Other:** Yeah.

**Me:** you you got what I'm saying? Like, you can run crazy models, right, but they can't fucking stream tokens. It's gonna be shitty treat like streaming. So it's gonna be way slower like, you can run better quality models.

**Other:** I'm happy that the two of you are understanding this. I'm just, like, not following the conversation. I'm like,

**Me:** That's it.

**Other:** like, in it to listen and sound like someone's talking, a different language. But I'm happy to figuring it out.

**Me:** Yeah.

**Other:** I think that's, like, it. Alright. Well, we gotta hop, but we can get on in a little bit or tomorrow if you want.

**Me:** Yeah. I'll put together a spec sheet for the 12 k build.

**Other:** Okay.

**Me:** I think that's that's, like, a conclusion, bro. Yeah.

**Other:** For the NVIDIA?

**Me:** And the NVIDIA, I'm gonna I'm gonna put together three proposals.

**Other:** Okay.

**Me:** One is the NVIDIA VTech Spark with, like, the daisy chain MacBook. Is the 12 k build. Then one is the Mac Studio.

**Other:** Okay. And then if you can also dumb it down in a

**Me:** That's it.

**Other:** sentence to explain to us like in layman's terms, what are the differences in power and other in speed and everything and, like, what it means, that that'd be helpful as well.

**Me:** The Rory example didn't work? Fuck, man. Thought that was good.

**Other:** No. Just like, okay. This one will be 10 we can run 10 times as many processes with this setup, but it costs twice as much or, like, whatever.

**Me:** Okay.

**Other:** We have to wait four months for the delivery.

**Me:** Yeah.

**Other:** Alright. We gotta run. Alright. Catch you later, bro. Thanks. Bye.
