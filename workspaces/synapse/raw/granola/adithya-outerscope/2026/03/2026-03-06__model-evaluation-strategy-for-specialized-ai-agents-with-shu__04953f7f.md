---
source: granola
workspace: synapse
ingested_at: '2026-05-07T04:23:57.244510Z'
ingest_version: 1
content_hash: blake3:df5a663a2126ef2d999149c184181230bfcbfcc677094258ddc29644f8a70883
provider_modified_at: '2026-03-06T20:17:18.958Z'
account: adithya@outerscope.xyz
account_slug: adithya-outerscope
document_id: 04953f7f-2b31-4c8e-ac0e-080a37d69d12
document_id_short: 04953f7f
title: Model evaluation strategy for specialized AI agents with Shubham and Ram
created_at: '2026-03-06T19:38:09.701Z'
updated_at: '2026-03-06T20:17:18.958Z'
folders:
- id: 91a78f08-eb95-45f7-ac10-8cb0ec3c45b4
  title: MOSAIC
- id: 2ace9cb8-854d-4638-9adb-ba6455b0eeb5
  title: SYNAPSE
creator:
  name: Adithya
  email: adithya@outerscope.xyz
attendees: []
calendar_event: null
transcript_segment_count: 343
duration_ms: 2336670
valid_meeting: true
was_trashed: null
routed_by:
- workspace: synapse
  rule: folder:SYNAPSE
---

# Model evaluation strategy for specialized AI agents with Shubham and Ram

> 2026-03-06T19:38:09.701Z · duration 38m 56s · 1 attendees

## Attendees

- **Adithya** (creator) <adithya@outerscope.xyz>

## AI Notes

### Product Concept: Specialized Model Evaluation Platform

- Core problem: Current model evaluations use generic LLMs (GPT-4, Anthropic)

    - Like using high school principal to train specialized software engineer
    - Generic judge models lack domain expertise for healthcare, finance, etc.
    - Provide only vague feedback (“60% correct”) vs detailed counterexample traces
- Market landscape:

    - Brain Trust raised $45M (commercial ML Ops tool, no eval value-add)
    - Applied Compute raised $80M (verticalized agents with contextual history)
    - Vellum, Petronas offer “verticalized” judge models but trained on generic data
- Solution approach: Three-component system

    1. Agent gym for continuous iteration
    2. Multi-agent debate tribunal for non-deterministic checks
    3. Verticalized judge models with customer data

### Technical Implementation Strategy

- Data sourcing approach:

    - 90% customer-provided context (similar to Applied Compute model)
    - Partnerships with data brokers (Trobio, Tiering through Eclipse connections)
    - Focus on narrow task domains vs general-purpose training
- Core value proposition: Speed through detailed feedback

    - Counter-example traces vs route correctness
    - Faster iteration cycles for specialized models
- Key hiring need: Senior engineer with model evaluation experience

### Validation Opportunity: Medical Use Case

- Shubham’s contact: Top-tier dermatologist in India

    - MD ranked 3rd nationally, published 14-15 papers
    - Core team member of new OpenAI lab in India
    - Built symptom identification model on open-source foundation
    - Gap between his assessment accuracy and model output
    - Access to 50,000+ doctors for beta testing
    - Sees ~1M patients weekly through platform
- Immediate next steps:

    1. WhatsApp group setup for introduction
    2. POC development to close doctor-model accuracy gap
    3. Potential design partner agreement

### Action Items & Next Steps

- Adithya: Apply to a16z Speed Run program today
- Shubham: Create WhatsApp group, introduce dermatologist contact
- Team: Review deck materials and white paper
- Focus: Build rudimentary POC within 12 weeks maximum
- Strategy: Start with junior developer, fragment problem into focused tasks
- New York meetup planned later this month

---

Chat with meeting transcript: [https://notes.granola.ai/t/95f4c2bc-6e59-484b-8faa-74886157820d](https://notes.granola.ai/t/95f4c2bc-6e59-484b-8faa-74886157820d)

## Transcript

**Me:** Come on, buddy. Okay?

**Other:** Boston about three hours.

**Me:** Okay, so I think I've told you both about the idea. First pass, but let me.

**Other:** Do you want me to get Shubham also on the call? He's in the other room, by the way.

**Me:** If you have a monastery. Be tremendously valuable to run this fight honestly.

**Other:** Okay, let me send this just to. Boom. And he just sit in the other room watching some dinosaur.

**Me:** Excellent. Yeah, perfect.

**Other:** Tips. I'll tell him. Give me one second. Let me pop over. Here. He's joining at. Let's give it a minute or so.

**Me:** Yeah. But just while he's joining. Right. Just to give you sort of the quick overview, basically like a quick refresher. Right now. Model evaluations suck, right? They're using generic LLMs pretty much. The market leaders in this space are basically using GPT 40 and throppix, sort of very basic sort of embedding.

**Other:** Adi, will you let Subhaman.

**Me:** Perfect. Yeah, perfect. Let's run. Admit to guests. Perfect. Hey, Shovam. How's it going, man? Great to see you. Hope you're having a good start to the year. Can you. Can you hear me? Fine. Perfect.

**Other:** Good to see you as well, sir.

**Me:** Yeah, likewise, man. Hope you guys are staying safe. I know this, like, stuff in the Gulf happening right now.

**Other:** Bitch. Area.

**Me:** Nice. Dude. Yeah. So I just running through like an idea that I've been thinking about for a while just with the Robin James here. James just to give you intro shoebum shiv Mr. CTO router, very crack technical.

**Other:** Nice.

**Me:** Individual.

**Other:** Very good. Call it quality. And by the way, Adi, I got to update you on that.

**Me:** Which one?

**Other:** The Greek colored polychain for blink today, by the way, Just fy.

**Me:** Oh, nice, dude. Okay, nice. Yeah. Down, definitely.

**Other:** I. I'll tell you more when? Please continue.

**Me:** Yeah, 100%. So, basically, right, guys. I can give you maybe sort of the quick overview here when you guys do slide deck and then also maybe run either like a basic example of the product. So let me maybe first run through the basic pitch, right? Right now sort of model EVAL is a very generic. Right? They're using sort of generic models like GPT 40 anthropics, sort of very highly expensive, like per token, sort of EVAL models that are not specialized at all. The analogy I like to use here in order to explain this is you're essentially using a high school principal to train a highly specialized software engineer, right? Instead of using a Facebook engineering manager or somebody that's very knowledgeable in that space to train that same person. The other thing here is you're also using very generic things, right? Like you're essentially asking this guy to carve a pumpkin type thing. Like why would he need to know how to carpet pumpkin? That software engineer should be learning how to code on leetcode, right? Type thing. Very specialized sort of things. Similarly, right? The exact same analogy applies to the LLM space right now. Any and all sort of LLMs that you guys are using right now are being trained by judge models, right? These are basically other smaller LLM models that are evaluating the output constantly of these LLM models. The issue with this frequently is that they miss is for highly specialized models like healthcare models like verticalized models like finance models, et cetera. These generically trained judge models are just often don't have enough training detail in order to extract sort of value and actually provide sort of what are known as counterexample traces. So these are essentially stack traces of sort of agents performing in the wild. By using tool calls like doing performing actions, et cetera, et cetera. But the judge models are unable to provide any detailed feedback on what broke, why it broke, how it broke, and how to fix it. Rather, it's very just generic vibe checks, right? Being like, hey, percentage, you got the 60% right, but there's no logic as to why pretty much market leaders right now are Brain Trust in Vellum and Petronas as well. Right. So Petrona says they're verticalized judge models, but these are, again, trained from foundational sort of generic models and don't yet actually have customer data. They're just sort of trained. In very generic sort of data that they've scraped in the wild. They are models, namely, are glider. And these are very, again, just generic sort of LLM Ebola models, rather than sort of verticalized sets, rather than, okay, with a finance sort of focus, with sort of a healthcare focus, et cetera, et cetera. Right type thing. There's nobody in production right now that is actually building these verticalized judge models. The only person that's building anything verticalized at all is verticalized agents with the contextual history known as Applied Compute. These guys recently raised an 80 million dollar round. Just to put you in perspective. Like what? Sort of a scale of a problem we're talking about here. Brain Trust recently raised 45 million type thing. And this is just basically a commercial sort of tool to simplify the ML Ops pipeline. There's no actual value add on the model eval side. Now you guys might be asking. Okay, they raised their smart people. Why didn't they even target this model? You've outside, right? The issue is it's a hard problem to solve, frankly. Right. It requires a ton of customer data in order to actually get a valuable output type thing. And so in order to sort of solve the chicken and the egg problem, it's basically just a massive go to market effort and it's a tough problem. To solve, right? Type thing. You need a ton of foundational model builders to actually put trust in you and give you access to their data, which is often the most valuable thing possible. The good thing is here again, go to market is basically what we specialize in. Type thing. So we already have a lot of folks that at least I have folks in my network that can connect me with a lot of foundational model builders. I'm sure you guys do as well, right? And if I can lean on Yalls network and support, that'd be tremendously helpful. My next door neighbor is Sandeep. He's the UT PhD. Advisor to a ton of students. One of the students has had years of experience in model evals who's looking to potentially come on as either a senior lead developer or the CTO product. But honestly, it's been going on for months conversation with this guy, so we're probably just going to scrap that. Conversation. Shubham, we're praying to you, bro. Literally. But for your advice on that. And then Sandeep might also come on as potentially a technical advisor. He's currently the head of AI at Story, so that's a really high signal just for him to come on as well. He's already down. Verbally committed to sign on as an advisor to the product. So we have that going for us. There's a couple other folks, the students that we could potentially target as potential senior developers that we can come in and just give equity. Initially, the current status of the product basically just sort of very sort of generic sort of Excel eval pretty much that can objectively tell you where an agent has gone wrong. So, for example, if you want some A2 and A3 and write it in A4, the agent has gotten the sum correct, but written in cell A5, the current MVP that I've built out will tell you exactly what went wrong. So the agent has summed the port correct, written it in the right cell, but written it in the wrong cell. So next time, for next time, basically remember to write it in the right cell as a four, and it basically can dynamically provide those counterexample traces. I know that's a ton of information to throw at you guys. Let me pause there really quick, and then maybe I can double click on specific nuances in the competitive landscape.

**Other:** So. Hi, adi. So I'm just trying to grasp this. So if I get it right, Are you training the specialized model or what exactly it is like, can you just dumb it down for me?

**Me:** Totally. Yeah. So from the start to finish, basically, here's what would happen, right, for the product usage. Essentially, if you're a foundational model builder and you're deterministic model type thing, right? So this is like you're taking just some programmatic action type thing, then you would basically just stick with the agent gym, right? So there's three sections to this product. There's the agent gym. There's a multiagent debate tribunal model for non deterministic checks with the subject matter expert in the loop. I'll explain that process in a bit. And the third final product is sort of the verticalized judge model pretty much. So the agent gym is essentially allowing the agent to continuously iterate and improve upon itself. Let's take the example of Aladdin, which is BlackRock's financial auditing platform. My friend actually from college is literally running their model evals right now. We're talking about exactly what they're doing. They're running into the issue of they're unable to find ground truth data, right? Like good ground truth data. This requires a shit ton of analysts to come in, right? In order to actually understand how analysts work in Excel type thing. The second issue that they're running into is the fact that they're unable to actually have a quality eval output with minimal data type thing. This is just due to the fact that.

**Other:** So. Eddie. Eddie. Sorry to interrupt. I'm just trying to participate here. So let's take a step back. Right. So you have said there are three type of models. These are training models that will train your data pipeline asset.

**Me:** So the first like so the agent gym is basically an environment that the agent can train in so it can call upon MCP tools or anything else that would be exposed to in the real world environment. If the agent runs into an issue there, then it gets passed into a multi agent debate system that basically debates.

**Other:** What is the data that they are being trained upon?

**Me:** Basically, the data will be provided by the customer, pretty much. Right. So if we're in blackrock's case, if they had sort of customer data for exactly how they would want the agent to operate or behave, then we do that. We also like the other side of this as well is we are connected with data. Brokers. I have a ton of connection with Trobio and tiering just through my job at Eclipse type thing, so they'd be able to provide sort of ground truths data pretty easily as well. So we'd be able to consolidate the data pipelines that they would need in order to aggregate a lot of this work pretty much for model Yasta.

**Other:** The data rock, for example. Let's take data rock skd, right? So let's say data rock. Is BlackRock is using it for their specific use case. And what would be these use cases?

**Me:** So in this case,

**Other:** Financial modeling, for example.

**Me:** Yeah, exactly. A Latin is like, yeah. Financial.

**Other:** Let's say risk modeling is the use case. Right. Financial response around commodities. Right. And most of this data will come from. For example, for this. So they have to curate the data. And this is closed data and open it or open data.

**Me:** Black. It would be like a mixture of both. So it depends on sort of what they're doing. Right. So if it would be like sort of. Let's assume you're building a disparity map model, for example, that doesn't actually have many public data sets, we'd go out and source that. Data for you from third party providers. If it is sort of a more public data set that's available that we can just sort of source in general, then we just source that for you and then use that. Essentially. The entire value add here is basically we're adding Taylor selected like index data to a judge model in order to provide more context on what your agent is theoretically doing in order to theoretically get a better eval output. So we're just tailor selecting the data and context needed in order to get a better eval.

**Other:** Then you plan to procure specialized data per use case or per entity who tries to build on this.

**Me:** Correct. The idea is initially you'd build out sort of these models just with publicly available data, right? So you'd have sort of a generic financial model train, generic healthcare like model train, et cetera, for eval stuff. And these emails are continuously only iterate and get better pretty much. Basically, the more customers we work with. Is the idea.

**Other:** So something like this is already there in Pipeline, right? For example, you see Codex models, right? Unlike generalize Chat GPT model. There are also Codex models, right? And they only train on the programming feedback loop, right?

**Me:** Good.

**Other:** And they also have a very elaborate setup around this. So basically, it takes around two to three weeks to roll out the new Codex version. Once the base version is live. And they do have lot of. Open source data, all the private repositories that they have access to, sort of where users are already interacting with these data pipelines and models, right? And there also I see them sort of like struggle, right? Even with the amount of data they have, the specialized closed data that's not publicly available, they sort of struggle to build out efficient model for programming. For example, me as a programmer, I can spot hallucination even with Codex models, right? And I'll not say that. I'm there. I'm the best programmer out there.

**Me:** Very likely.

**Other:** But when it comes to use cases like Blackrock, right. I feel their needs are more specialized and more competent. And if the data is not of that quality, or the data itself is not available there, right? Like good amount of data, which is of quality again.

**Me:** Yeah, that's totally a fair assumption. Yeah, 100%. Basically what you're saying is even with the publicly available data that they'd probably already have access to and that they're using, essentially the outputs would need to be tip top shape, right? Because they have.

**Other:** Yes. So if anything has to be relevant for BlackRock, right? That has to be world class. And if BlackRock is responsible for providing that data, I know that they have limited resources, at least from my level of information. Right. Even when OpenAI is trying to do a specialized model on programming, like on languages like Rust, I know that they feel very badly and you have to do 20 iteration on basic program to get it right. Which I could have got it right just by looking at it, like in the first attempt or second attempt. Right. So there's lot of steering involved, even when the data. Is in abundance. I feel right. So what I'm not able to sort of understand here is like, how we plan to build something which is specialized and where the organization itself is responsible for providing the data. So either we become that curation entity and try to curate that specialized data. Like, the biggest problem right now is structured data, which is relevant. Or data which is auditable like this data is relevant for a company, Right? And to be even that judge, we need to have that confidence in that subject.

**Me:** Y. Eah. Yeah.

**Other:** So the sole reason why BlackRock would outsource this, if we have that competence to just that data, okay, this might be relevant for BlackRock. If we are not in that position, I feel BlackRock.

**Me:** Totally.

**Other:** Will not engage at the level that we are anticipating.

**Me:** 100%. The Black Hawk example is a bad one to start off with. Obviously, we'd probably need to have significant sort of traction, legitimacy, proving the shit out. But regardless, my point still holds. Actually, I completely agree with your concern. Right. You're pointing at sort of the real crux, right, with just sort of data quality and depth, not just model architecture. Right. As you mentioned.

**Other:** Because that's the base reasoning, right? That's what we start with. We will figure out a way to build specialized model, right? And for specialized model, the biggest point is that specialized data assertion around the correctness of data or accuracy of data like this is high IQ data, right? So.

**Me:** Correct? Correct. Yeah.

**Other:** I don't know. Like in our scenario, who provides that assertion? At that level.

**Me:** No, that's a great question. Right? I mean, so typically the data would honestly be provided by the customer themselves. Right. Type thing. Like, in all honesty, right. So like 90% of the time that the customer would have to provide us with their context. This is exactly what applied compute does. For example, in order to build a highly specialized agent for you. We need all your information pretty much. That's an upfront thing. That's not the problem that we're trying to solve. We're not trying to solve data provenance or anything like that, or data collection. That's not the core problem or the core mode. The core. Problem that we're trying to solve is the velocity of which these teams ship. Right. Type thing. And we're not trying to beat OpenAI at sort of training a general purpose model, but rather we're trying to narrow the problem down into very, very tight domains. Right? Eval is in very tight domains, and also using three levers that three or even four levers that most of these larger players aren't optimizing for. Right. And these three are. Right. Like, you're basically getting. What do you call it? You're only caring about a very narrow slice of tasks. Right. So very. Even in the Aladdin workflow. Very specific risk for closing Aladdin is what we'd focus on, not just all sort of financial modeling. And so for that we'd focus on collecting. Okay, maybe, hey, we need to run a data campaign for this for XYZ reason. Then we justify that budget to them, and then we'd go out to trobia or whatever. We're not doing the data collection part. That's way too tough to solve. Right. And that's already been solved. There's many major players in that. The other unique thing here is we focus on counter example traces rather than route correctness. Right. What this really offers compared to any other person is just raw speed and shipping type thing. If you have a complete model that you're starting out with, and you had sort of an email model that's constantly telling you how to fix yourself rather than just generically, okay, you're 60% right, you're going to fix yourself much faster and iterate much more rapidly type thing if you have more quality output. So by having a more quality email, which is essentially what we're providing, then only would you essentially get this. In order to do this, obviously we need to bring on someone with tremendous eval experience, which is a tough hire. To make. I'm not going to lie. That's definitely a barrier in the step, but James has access to a shit ton of product engineers in this network. I'm hoping that'll probably hedge the bet against. That. But that is, I think, really the real core value. It's not really like the data collection or data problem and so where the data is coming from, but rather what we're doing with the data and how we're using it in order to provide higher tier model output.

**Other:** So end goal, if I'm not wrong. Right. So end goal is limited amount of data and higher accuracy in terms of prediction. Right. That. That's the. That's the end goal. Right?

**Me:** Precise. Exactly.

**Other:** And with lowest turnaround time. So I have actually one interesting use case. Right. So I'm helping one friend of mine.

**Me:** More evals. Precise.

**Other:** He's like one of the top tier doctor in India. He's MD in Dermat. He ranked around third in India in one of the exams, I guess, right? And he's trying to. So he, he was able to figure out basic training around, like, so, identifying symptoms by just providing a photo and some, some, some. Some. Some details around symptoms. He was able to sort of, like, narrow down, like, what the root cause might be. Right. And he was doing it. With some rapper on top of Gemini, if I'm not wrong. And he. He has access to data, by the way, right? So it's like some refined model on top of Gemini where he was able to sort of like do some. Some not. Not exactly Gemini. I guess it was Kimmy. One of the open source mobile available, right? So maybe what we can do is I can try to set up a group with him. You guys can try to help him if he's able to improve the accuracy of his model by plugging into you guys and able to achieve sort of, like, better result, right? I feel that can be a good validation on its own that this thing works. So at the end, the problem that we are trying to solve. Is whatever you are doing in your specialized domain, we have a better way to fix it. If the data is small scale, basically, at least the small scale businesses should be able to build something more specialized than using something which is open source, publicly available, right?

**Me:** Ly do more with your data, essentially is kind of the motto. Yeah, 100%.

**Other:** Yes. So I guess if we are able to achieve this with one use case that we have, then then the thesis is validated, right? Then we'll have. Then we'll have a use case to talk about that. Okay? This was a problem, and I know the problem that he's facing. So what's happening is he's using something open source, he has built something on top of it, but the reason that he can produce just by looking at it and the result that AI is producing are very different.

**Me:** Okay? Right.

**Other:** Like he can just look. Look at the footer and tell, okay? This is the cause. By being the symptoms. This is the cause. Right. And the AI is not able to do that.

**Me:** Yeah, bro.

**Other:** And then he has to. He has to sort of, like, manually annotate all these photos. Write the symptoms.

**Me:** This is exactly like the issue that Mercoura was trying to solve, right? This is why they became a fucking 10 billion dollar. And dude, these are three 22 year olds that became billionaires overnight. Dude. What is the reason for this? They started off as a hiring platform and they switched over to model. Sort of like. Tagging, like data tagging. Right. Why is this valuable? Because scale got acquired by Meta at the time, and everyone was looking for a data labeler and they had subject matter experts that were paying. They were paying a mill plus two per day type thing. Literally milled payouts per day type thing. Right. So that's essentially what they did. They brought in guys like your friend in order to come in and start tagging these things manually. And so essentially, what am I trying to do? The exact same, but just more automated. We have access to better technology now. There's no need to give these subject matter in the loop guys the power type thing. We don't need human in the loop in every sort of instance. For more deterministic checks, we can automate it. This is literally where my thesis came from, dude. I was like. Like, I saw them. I saw, like, the post. I'm like, how the do these guys became billionaires, right? Type thing. And then I saw one of my other friends in college, right? Copy, Literally exact copycat of their idea. Raised a 35 million Series A like last year, right? Literally, exact same thing. It's called micro1.AI uses subject matter experts like, you know, evaluate. He just got a couple decent contracts and raised off. It. I'm confident. I'm telling you, dude, if we can literally like, like, implement this with, like, even one use case, it's more than rasable, pretty much, especially in this market. Type thing.

**Other:** By the way. Right. So the use case that I'm talking about. So this guy. Is to be honest, not some cheap. He is like one of the tier one doctor in India right now. Very sharp. He. He is also sort of like, He is handling one of the vertical and newly open AI lab in India ams, which was open. Which was opened by this guy, President. Right. Macron. Yeah. So he's in core team of that. I guess I'll connect you with him.

**Me:** There are people.

**Other:** If you could help him solve the problem. I feel you have very good use case because he has access to almost like what 50,000 doctors write on his pocket. They are willing to beta test the application right away. Just that he is not very confident in the outcome of that application. So if you could help him automate lot of the shit, get the product going. I guess he already has a version of product. Just to give you some data point, like he started on this, like couple of months back. And he was able to build everything on his own. Like he was able to pick AI model training, cleaning, annotations, almost everything from zero. And he has no computer science background. It's all medical background, right?

**Me:** Dam. N.

**Other:** He's like. Yeah. So I feel I'll connect you with him. And if you could get this POC going, right, and if you can refine the model that he has, Then you have the real user base and real use case to showcase. Actually.

**Me:** That would be. That would be excellent intro, man. Honestly, if we could sign him on as a design partner, that'd be tremendously helpful for this race. Yeah, 100%.

**Other:** Perfect. Then. Then you have the use case, I guess. Perfect. He's also. But he is more into sort of like government side of things. Doing things for mainly nonprofit that will also make your use case actually more strong. He was sort of like cover page of International Magazine of Dermatology. By the way, he has written close to 14, 15 papers around dermatology. So yeah.

**Me:** Damn. Not 100% would be a tremendously helpful intro, dude. He's basically needing improve his model, like foundational model or something that he's building.

**Other:** Yes. Yes. What he wants to do is improve. He wants to sort of, like, reduce the gap.

**Me:** Excellent.

**Other:** Between his own assessment and the model's assessment. That's the end goal that he's trying to achieve.

**Me:** Nice. Okay? Makes sense. Dude.

**Other:** And his own assessment is next level, by the way.

**Me:** Nice. Yeah, exactly. Exactly. Yeah, Honestly, it would be a very good intro, dude. That's basically the problem that we're trying to solve without sort of needing human at the loop, essentially. So there's an automated way that we could do that. Obviously, maybe in a medical setting, it's tougher, but, I mean, we can give it. A shot. At least it's a POC Signed right type thing, which is, like, always a good thing.

**Other:** At least we'll have more data, right? That. Okay, this did not work out. Maybe we have to tweak our strategy or tweak the data.

**Me:** Exactly. Yeah.

**Other:** At least some validation on both the front. Right, whether this will work or not, because end of the day, you want, you don't want to restrict yourself to use cases.

**Me:** Y. Eah. Yeah.

**Other:** Or even to restrict. Right? You need data point, so at least this will give you data point. Can you just ping me on WhatsApp?

**Me:** Y. Eah. Yeah.

**Other:** Very quickly. I'll just create a group and then we can get to it.

**Me:** Dude, I'm going to. Also, I'm applying to this thing, a 16Z speed run with a couple ideas today. This is one of them. So this ends up getting picked up, you know, hopefully that'll give us some initial roadmap, you know, where the hell.

**Other:** Yeah. Here. In case. If he sort of, like, he starts working with you, you. You'll have good credibility. Actually, you'll have. Right now, what am sees around almost like, what, a million people in a week? A million patients in a week? Something like that. So.

**Me:** I don't have your contact, bro. Rom, would you mind affording Shubham's contact real quick through WhatsApp if possible? I thought I had it due to save. I don't know.

**Other:** This is good, I guess. That's it. Anything else. Ram.

**Me:** That's it.

**Other:** But this is interesting. If. If we are, we can validate our thesis. Nothing like it, to be honest.

**Me:** Yeah.

**Other:** Then you don't. You have to get into technicalities around how it works. Then we can just focus on optimizing how it works. Right. Rather than debating whether it works or not.

**Me:** Exactly, dude. Precisely. Yeah. Like, literally testing this in production is the best way to, like, actually go about it 100%.

**Other:** Yes, yes. Actually, that's the whole thesis of post hoc. So they always test things on production rather than.

**Me:** Yeah.

**Other:** Fantasizing.

**Me:** Yeah, exactly. Exactly. Literally. Art of crypto is fantasizing, bro. Literally. That's it.

**Other:** Crypto, alpha and sizing. Dude, we are fantasizing for seven years now.

**Me:** Endless talk, bro. Yeah, exactly. Fuck that, dude, literally. Yeah. Okay. So. So. Sounds good, man. Dude, do you know anyone that has speciality in model eval? I was trying to talk to this guy, like, my neighbor's, like, student to come on as a cto, but, like, he's, like, you know, flaky, and so do you, like, do you. I mean. I don't know if you have been with yourself, dude. I don't know what you're working on right now. Right, like, or do you have folks in your network, like, if you don't have bandwidth type thing? Just looking for, like, an engineering brain to kind of start bouncing ideas off of more concretely.

**Other:** Dude. I'm not that connected, to be honest.

**Me:** Like engineers and either, like, I thought, like, you typically have a good engineering network, right? Or something.

**Other:** That's not something that I'm willing to reveal.

**Me:** Okay, okay, that's fair. That's fair.

**Other:** It's fine. I'll let you know if I find someone to be honest. Right.

**Me:** Okay, okay, okay.

**Other:** Yeah, I'll. I'll find someone.

**Me:** To be fair, we need more traction before we bring someone on, dude. Right, but, like.

**Other:** So I have a guy who had run his own LLM, models, inference, all that. Build everything from zero. I have a guy. But I don't know if he's available.

**Me:** Okay? I mean.

**Other:** Like, good hands on guy, to be honest. Like, can pick any problem, can juggle in any domain, at least on tech side, right?

**Me:** Dude, I just. I need someone like that, man. Honestly. Like, it's like, if. If there's anyone like that, you know, like, that, we can even, like, start compensating, too. Like, I'm going to see if I can get some, like, initial cash in the door. One of my friends, like, committed, like, 300, like, you know, like, way long ago. I don't know if he's still legit about it, if he is, like, super cool. I mean, if we can start comping this guy, like, if you have just killer engineers, dude, that, like, you know, are cheap rate to. Hire like that'd be ideal.

**Other:** And then I thought you are building the model which is killer engineer, right?

**Me:** Dude, I can like, literally build. I can build these basic use cases, right? Like for, like, okay, like Excel, like, okay, like checking, deterministic checks and all that stuff is very programmatic. You. I can just. Anyone can claude code that. That's not an issue. But, like, for highly specialized, like, anything beyond that, where it's. Like, okay. Eval is like, how do you actually go about, like, ranking what is good, what is bad? Like, you know, semantically, all this shit, like, anything beyond the basics, right? I'm, like, fucked when it comes to ML, so that's why I'm, like, smarter than I am.

**Other:** AI agent as software developer is just a hoax. To be honest, I was showing one video to RAM the other day, right?

**Me:** Y. Eah.

**Other:** It's like the whole world is in some billion years of debt. Just to develop a debt.

**Me:** Yeah. No facts. Yeah, 100%. 100%, dude. All the modern, most modern software is being written by.

**Other:** So 11 question, adi. So what is the so what are you looking for? So from validation perspective, when we spoke in December yesterday, this company that was not Scalia. There's some company that you separate this so the model.

**Me:** And. Oh, fucking. I forgot their name, bro, but, yeah. What are you saying? Anti map. Sorry.

**Other:** But are you still looking for the validation of this thing?

**Me:** Basically.

**Other:** Or what's the big problem? What are the top.

**Me:** So first. First problem is basically, like, once we have, like, POCs, that's first problem, right? Which, like, honestly, like, you know, hopefully this will solve as well, like this intro. So once we have, like, some level of, like, traction, okay, we actually have, like, folks that are, like, maybe interested in using the product. We actually need to build a fucking thing, right? Type thing. So now I need an engineer. That's my next immediate pressing problem. Right. After I have, like, POC and an engineer I know I can raise. There's, like, no question about it in my head. I can read off this. But so I just, like, you know, that those two things I just need to solve pretty much. Right now.

**Other:** Do you have a dick that I can float with another friend deep in the AI Space?

**Me:** Yes, yes. I'll send you the Gamma. Yeah, absolutely.

**Other:** No. Also one thing, Ram. Don't send out anything unless you have one working POC ready. Please talk to that because it will be a bounce and then you will not have a second guy to reach out to, to be honest. So best is like orchestrated properly. Adi, get something going. Get one use case ready. See if you can really optimize the model. Figure out a tech guy who can do it for you. If it is just a thesis. If it is a clean product. Then do a poc, right? And then go reach out to someone 100% they reply. Because these few of these connects are very sensitive, right? And if you hit once, it's a bounce, then it's very hard to get that attention again. Right, right, right. So best is figure out all the gaps before pitching it to investors, and then we address those gaps.

**Me:** 100%. 100. This is like the. This is the current working version here. Name Shangr on deck. This is the current working version of the deck. Let me know if you guys have any Gone some shit. Basically just running through the points. I just, like, ran through with the units.

**Other:** And stop doing this. AI dec, man. I'm 100% done with these AI days after Ram presented me 10 different ideas right after one night.

**Me:** Bro.

**Other:** They all have.

**Me:** I've been going insane with the cameras, bro. I literally. The past three days, I've made, like. Like a bunch of these. Bunch. Bunch of these, honestly, but.

**Other:** Yeah, I had this face as well. Like, when you go, it's okay. Initial within friends. Validating. Nothing against the idea to be honest, right? Just that we want to be sure. If we present it to investors, we want that legitimacy, right?

**Me:** Externally. Right. Right.

**Other:** Then we are serious. Because I'm sure they did not raise 80 million with this tech, right? Perfect, perfect man.

**Me:** Sounds good, dude. Well, yeah. I mean, I'll send you over, like, the white paper and stuff. Dude, I'd love to get your thoughts, show them, like, on, like, the technical side of things, you know? Then James, Ram, I'll send you guys over all the materials I have right now. So I have, like, put together this deck.

**Other:** Sure.

**Me:** And then, like, a couple other materials.

**Other:** Sure. Perfect.

**Me:** Cool.

**Other:** Yeah, we're still in Denver. Buddy.

**Me:** This thing. Which one? Denver, bro.

**Other:** I'm a student, general.

**Me:** I told you all this, dude. It's been a retardedly stupid month for me, bro. Like, life has gone to shit. Honestly, like, slowly recovering in Austin. Now.

**Other:** Might make the New York later this month. I'll keep you posted.

**Me:** Sounds good, man. Nice. I'll probably be. Are you coming to Nvidia? Like GTC or whatever the developer conference thing they're having?

**Other:** We might see you in New York if you're around. So we are.

**Me:** For Das. Where are you guys coming for?

**Other:** Yep.

**Me:** That's okay. I'll make it out then. I'll figure out.

**Other:** Y. Eah. It's someone, I think it seems.

**Me:** Oh, nice. Man. Nice. Cool, cool, cool. Alrighty, guys. Well, it sounds like a plan. I'll keep you guys posted and they'll stay in touch via WhatsApp. Dude. Actually, Rom, could you afford me showroom's contact so that we can.

**Other:** Yeah, Just focus. So just focus on a quick poc. Focus. 12 weeks max, and then I guess this is good to go.

**Me:** Y. Es Nice, dude. I need an hinge guy, though, dude. Like, honestly, in order to, like, build out a full fledged poc.

**Other:** Yeah.

**Me:** It's like a chicken and the egg problem, right? Type thing. So should I. Should I build out, like, a rudimentary version myself? Test it out, like, kind of shadyly with, like, the doctor's thing, and then be like, hey, this kind of works. This is interesting. And then get some funding and then hire. Like, what is the order of operations there, do you guys think?

**Other:** So what's the order? I'll tell you. The best order is. Ask for help when you are stuck. So always start with anything that you have. Like start building with whatever you can. Whenever you hit a block. Just ask for help. That's the best way to be honest, right?

**Me:** Okay? That's fair.

**Other:** Put 200% of your bandwidth, and if that doesn't move something, just reach out for help. Then you'll know what to ask for help.

**Me:** Okay? Facts, Fact, facts. That is true. Only way I know is by doing it.

**Other:** Yes, yes, just start.

**Me:** Okay, dude. I'll start trying to build a damn thing myself then. Honestly.

**Other:** So start on something. Best is also hire a junior developer instead of a senior developer. To be honest. Right. Right now, AI tooling is at a level where if you guide them right, this is the expectation. That. Okay, I want sort of like fragment the problem statement. Don't make the problem statement very elaborate.

**Me:** Right.

**Other:** Fragmented. Like you just want to do one thing. For example, initial thing is two AI agents just doing one thing. Finding the error, calling MPC and finding a fault. Right? Let's say that is your unit problem statement. Once you are satisfied with that, you reach to next block and then you solve it, right? That's how you will build the eventual pipeline and just get. So get a junior developer and make the task very focused instead of very elaborate. That. Okay, build me this time machine.

**Me:** Right. Right. Yeah.

**Other:** Like, start with the VD that, okay, you have to build something which is round, and if you just throw it, it will roll away.

**Me:** Y. Eah. Yeah. 100%.

**Other:** And in that process, if you are stuck, I can always guide, no problem.

**Me:** Yeah, 100%, dude. 100%.

**Other:** Cool.

**Me:** Nice. Man. Okay, dude, on WhatsApp, with, like, next steps and stuff. And then James and Romol's helping you guys with this deck. I'll also have, like, a designer guy, like, working on an updated thing, so I'll send you guys that, too, once I have it.

**Other:** Awesome. Brother.

**Me:** Nice. Cool, cool, cool, guys. Appreciate the time. And then I'll stay in touch by WhatsApp. Probably. Cool.

**Other:** Thank you, ron. Thanks. Thank you, jibs. Thank you, ad. Thanks, guys.
