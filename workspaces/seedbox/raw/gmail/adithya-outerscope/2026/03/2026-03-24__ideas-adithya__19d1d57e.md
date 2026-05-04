---
source: gmail
workspace: seedbox
ingested_at: '2026-05-04T20:03:34+00:00'
ingest_version: 1
content_hash: blake3:f2c157beba74b63888def1b9af645094da2b02dfb2fadc28dc40d294e81418de
provider_modified_at: '2026-03-26T09:03:57+00:00'
account: adithya@outerscope.xyz
account_slug: adithya-outerscope
thread_id: 19d1d57e7ef8b873
message_ids:
- <CAHj2+rcZOA5VcS13J3SNmGjNzcXatjdyRDoJ4fP=fa44Z_fbEg@mail.gmail.com>
- <42C11826-0932-4C00-A05B-F4BAA97B1470@seedboxlabs.co>
- <5C25C14A-A135-4303-827B-693FCB86EF84@seedboxlabs.co>
- <CAJNMsb_GKJ2Fv2LZ+6WVg9QM4MnXKGsz81HhJgpKsXLiutyTmA@mail.gmail.com>
- <EF6EADEF-3EDA-460B-99C7-4E23C82D6D1F@seedboxlabs.co>
subject: 'Re: Ideas: Adithya'
participants:
- name: Adithya Kumar
  email: adithya@seedboxlabs.co
  roles:
  - from
  - to
- name: Lara Daniel
  email: lara@seedboxlabs.co
  roles:
  - to
  - from
- name: Avery Haskell
  email: avery@seedboxlabs.co
  roles:
  - to
  - cc
- name: adithya@outerscope.xyz
  email: adithya@outerscope.xyz
  roles:
  - cc
  - from
  - to
labels:
- IMPORTANT
- CATEGORY_PERSONAL
- Seedbox
- SENT
first_message: '2026-03-24T00:56:19+00:00'
last_message: '2026-03-26T09:03:57+00:00'
message_count: 5
attachments:
- id: ANGjdJ8e
  filename: Bildschirmfoto 2026-03-16 um 09.19.46.png
  size_bytes: 131055
  mime: image/png
  message_index: 0
- id: ANGjdJ9S
  filename: seedbox_agent_prds.docx
  size_bytes: 19258
  mime: application/vnd.openxmlformats-officedocument.wordprocessingml.document
  message_index: 0
- id: ANGjdJ9T
  filename: seedbox_agent_prds.docx
  size_bytes: 41227
  mime: application/vnd.openxmlformats-officedocument.wordprocessingml.document
  message_index: 2
routed_by:
- workspace: seedbox
  rule: label:Seedbox
deleted_upstream: null
---
# Re: Ideas: Adithya

## 2026-03-23 19:56 CDT — Adithya Kumar <adithya@seedboxlabs.co>

Hi Lara,

I've put together a few PRDs based on the descriptions you sent last week.
My apologies for the delay in responding; I was in San Jose for the NVIDIA
GTC conference.

Could we schedule a meeting for this week to review these PRDs and discuss
how I can start contributing?

Best regards,

Adithya Kumar

### Attachment: Bildschirmfoto 2026-03-16 um 09.19.46.png
Binary attachment, content not extracted.

### Attachment: seedbox_agent_prds.docx
Binary attachment, content not extracted.

## 2026-03-24 11:32 CDT — Lara Daniel <lara@seedboxlabs.co>

Hi Adithya,

Thank you will have a look. :) How does tomorrow your 9.30am sound? :) I’ve tentatively scheduled the call for us.


Best

Lara

## 2026-03-25 11:02 CDT — Lara Daniel <lara@seedboxlabs.co>

Hola, 

See enclosed with a couple comments in yellow:) Ignoring my ideas, what do you think we would benefit most from? :) Very much value your professional expertise. 

￼

### Attachment: seedbox_agent_prds.docx
Binary attachment, content not extracted.

## 2026-03-25 15:26 CDT — Adithya Kumar <adithya@outerscope.xyz>

Hey Lara,

Went through all your yellow highlights — really helpful feedback. Let me
address each one, then answer your bigger question at the end.



*CRM INTAKE AGENT*
"Important also to know who added / owns the contact."
Totally agree. I'll add an added_by field to the schema, auto-populated
based on whoever triggers the Slack command. Simple fix.

"Ideally it would also be able to read images — screenshot of an Instagram
profile, or a link to X."
Doable. We can use Claude's vision capability to parse screenshots
(Instagram profiles, X bios, etc.). The flow: paste an image into the Slack
command, the agent extracts name/handle/bio via vision, then enriches from
there. For X and Instagram links, we'd scrape the public profile. I'd put
image input in the MVP since it's actually easier to build, and social link
scraping in the fast follow.

"Side note: I have a German WhatsApp number."
Noted. We were already planning to punt WhatsApp to v2 anyway. When we do
get to it, the German number won't be a blocker — the WhatsApp Business API
is region-agnostic. The real complexity is the WhatsApp-to-Slack bridge
regardless of number. For now, Slack-first is the right call.

"I think if Slack worked, that would be great."
Perfect — Slack is the primary input channel. Everything through Slack
commands and message forwarding.

"What can Clay do that Apollo can't?"
Apollo is a contact database — you search for someone, it returns their
title, company, email, and phone. That covers about 80% of what you need
and it's cheaper (~$50/mo).

Clay is a workflow engine that chains multiple data sources together.
Example: take a LinkedIn URL, enrich via Apollo, also pull their recent
tweets, check if their company raised funding recently, then score them.
More powerful, but more complex and more expensive (~$150+/mo).

My recommendation: start with Apollo. It covers the core need. If you later
need multi-source enrichment chains, we upgrade to Clay. No reason to pay
for it upfront.



*COMPETITOR REVIEW CRAWLER*
"We would not only need to look at the at-home world but also the clinics
if possible."
Good call. I'll expand the scrape targets to include clinic reviews —
Google Reviews and Trustpilot for major fertility clinics (CCRM, Shady
Grove, RMA, plus European clinics if you have a target list). The schema
stays the same, we just add clinic names. Heads-up: clinic review volume is
much higher than at-home products, so the LLM analysis pass costs a bit
more — maybe an extra $5-10 for the full run. Nothing dramatic.



*INVESTOR RESEARCH AGENT*
"I think we can move this as a secondary relevance as we will postpone
further active fundraising for now."
Makes sense. Moving it to the back of the queue. It's fully specced
whenever you need it — we can spin it up in a day or two when fundraising
becomes active again.



*MEETING NOTES TO TASKS*
"This is actually amongst the most important. Likely priority 1 for me."
Heard. Elevating this to the top of the build order. Revised priority:

1. Meeting Notes to Tasks Agent (your #1)
2. CRM Intake Agent (foundation for everything else)
3. Competitor Review Crawler + Scientific Lit Monitor (parallel)
4. Press & Narrative Tracker
5. Investor Research Agent (when fundraising resumes)

"Notion sounds good. What about Apollo or there was one tool you
recommended as well?"
For task management, Notion is the right call — it handles tasks,
timelines, Kanban views, and databases natively. Apollo is purely for
contact enrichment (filling in job titles and emails), so it's relevant to
the CRM agent but not task management.

The other tool worth mentioning is Linear if you ever want something more
structured, but Notion covers your needs at this stage and keeps everything
in one place. No need to add another tool right now.



*DECK FEEDBACK TRACKER*
"Not high priority right now."
Agreed, parking it. This comes back naturally when fundraising ramps up
again.


*SCIENTIFIC LITERATURE MONITOR*
"High priority — might be a 1x job?"
It can be both. The initial run is a 1x job — pull everything relevant from
the last 12-24 months, summarize it, hand you a doc. That's maybe 2-3 hours
of compute time.

But the real value is making it recurring. A weekly PubMed scan costs
essentially nothing and takes about 30 seconds. My suggestion: do the 1x
backfill first to get you current, then set up an automated weekly scan
that drops new papers into a Notion page or Slack channel. The weekly run
is zero-maintenance — just a scheduled job that runs on its own.


*PRESS & NARRATIVE TRACKER*
"Very important to understand what is happening in the space" / "To show
that interest in the space is growing" / "To understand what the content
and narrative is."
Crystal clear on the use cases. Three deliverables:

1. A running log showing growing media interest in male fertility (useful
in investor conversations even while not actively fundraising)
2. Narrative tracking — what angles journalists and podcasters are taking
3. Early competitor press detection

"Can we use Claude or similar to populate the most relevant news before
forwarding?"
Yes, exactly. The flow: Google Alerts + podcast transcript APIs feed raw
results into Claude, which filters for relevance, tags each item
(competitor mention, new research, market trend, etc.), writes a 1-2
sentence summary, and ranks by importance. You'd get a weekly Slack digest
or Notion page with only the stuff that matters — not a firehose.


*BUILD TIMELINE*
"Do we really think this takes this long? I've done a 75% version of the
Amazon/Tagger scraping and it took 30 minutes of active work and then about
1-2 hours of the agent working."
Fair challenge. You're right that the scraping itself is fast. The
week-long timelines were accounting for setup, testing, LLM prompt
iteration, and making things robust enough that you and Avery can run them
without me. If you're comfortable with a "works but might need babysitting"
version, we can compress significantly. I'll bring a tighter timeline on
Monday.

"What do you suggest for: CRM, Task management (with timeline)?"

My recommendation:
- CRM: Google Sheets, fed by the CRM Intake Agent via Slack. Simple,
shareable, works well until you hit ~500+ contacts. At that point you'd
graduate to HubSpot free tier or Attio.
- Task management with timeline: Notion. A single database with multiple
views — table view for everything, Kanban board by status, and
timeline/calendar view for deadlines. The Meeting Notes agent writes
directly into this.



*Monst Benefit*
Ignoring the specific tools, the thing that would move the needle most for
Seedbox right now is a single operational hub where every action item,
contact, and piece of market intel lands without anyone manually filing it.
Right now your knowledge is fragmented across WhatsApp, email, and memory.

The Meeting Notes to Tasks agent solves the most acute pain — nothing falls
through the cracks after a call. The CRM agent solves the second — you
always know who you know and how to reach them. Everything else (literature
monitor, press tracker, competitor intel) gives you strategic advantages,
but the first two are operational survival. You were right to flag task
management as priority 1.

I'll bring a proposed Notion schema to the Monday call so we can set it up
together.

Talk Monday!
Adithya

## 2026-03-26 04:03 CDT — Lara Daniel <lara@seedboxlabs.co>

Hi Adithya,

Much appreciated, see below. :) 

> Am 25.03.2026 um 21:26 schrieb Adithya Kumar <adithya@outerscope.xyz>:
> 
> Hey Lara,
> 
> Went through all your yellow highlights — really helpful feedback. Let me address each one, then answer your bigger question at the end.
> 
> 
> CRM INTAKE AGENT
> 
> "Important also to know who added / owns the contact."
> Totally agree. I'll add an added_by field to the schema, auto-populated based on whoever triggers the Slack command. Simple fix.
> 
> "Ideally it would also be able to read images — screenshot of an Instagram profile, or a link to X."
> Doable. We can use Claude's vision capability to parse screenshots (Instagram profiles, X bios, etc.). The flow: paste an image into the Slack command, the agent extracts name/handle/bio via vision, then enriches from there. For X and Instagram links, we'd scrape the public profile. I'd put image input in the MVP since it's actually easier to build, and social link scraping in the fast follow.
> 
> "Side note: I have a German WhatsApp number."
> Noted. We were already planning to punt WhatsApp to v2 anyway. When we do get to it, the German number won't be a blocker — the WhatsApp Business API is region-agnostic. The real complexity is the WhatsApp-to-Slack bridge regardless of number. For now, Slack-first is the right call.
> 
> "I think if Slack worked, that would be great."
> Perfect — Slack is the primary input channel. Everything through Slack commands and message forwarding.
> 
> "What can Clay do that Apollo can't?"
> Apollo is a contact database — you search for someone, it returns their title, company, email, and phone. That covers about 80% of what you need and it's cheaper (~$50/mo).
> 
> Clay is a workflow engine that chains multiple data sources together. Example: take a LinkedIn URL, enrich via Apollo, also pull their recent tweets, check if their company raised funding recently, then score them. More powerful, but more complex and more expensive (~$150+/mo).
> 
> My recommendation: start with Apollo. It covers the core need. If you later need multi-source enrichment chains, we upgrade to Clay. No reason to pay for it upfront.
I know Apollo - sounds great! :) 
> 
> 
> COMPETITOR REVIEW CRAWLER
> 
> "We would not only need to look at the at-home world but also the clinics if possible."
> Good call. I'll expand the scrape targets to include clinic reviews — Google Reviews and Trustpilot for major fertility clinics (CCRM, Shady Grove, RMA, plus European clinics if you have a target list). The schema stays the same, we just add clinic names. Heads-up: clinic review volume is much higher than at-home products, so the LLM analysis pass costs a bit more — maybe an extra $5-10 for the full run. Nothing dramatic.
Great. I think if we focus on the largest clinics in the US that would be enough for now. But Avery can give some more context there. 
> 
> 
> INVESTOR RESEARCH AGENT
> 
> "I think we can move this as a secondary relevance as we will postpone further active fundraising for now."
> Makes sense. Moving it to the back of the queue. It's fully specced whenever you need it — we can spin it up in a day or two when fundraising becomes active again.
> 
> 
> MEETING NOTES TO TASKS
> 
> "This is actually amongst the most important. Likely priority 1 for me."
> Heard. Elevating this to the top of the build order. Revised priority:
> 
> 1. Meeting Notes to Tasks Agent (your #1)
> 2. CRM Intake Agent (foundation for everything else)
> 3. Competitor Review Crawler + Scientific Lit Monitor (parallel)
> 4. Press & Narrative Tracker
> 5. Investor Research Agent (when fundraising resumes)
> 
> "Notion sounds good. What about Apollo or there was one tool you recommended as well?"
> For task management, Notion is the right call — it handles tasks, timelines, Kanban views, and databases natively. Apollo is purely for contact enrichment (filling in job titles and emails), so it's relevant to the CRM agent but not task management.
> 
> The other tool worth mentioning is Linear if you ever want something more structured, but Notion covers your needs at this stage and keeps everything in one place. No need to add another tool right now.
Ok great, then we’ll start with notion and then add linear where necessary. 
> 
> 
> DECK FEEDBACK TRACKER
> 
> "Not high priority right now."
> Agreed, parking it. This comes back naturally when fundraising ramps up again.
> 
> SCIENTIFIC LITERATURE MONITOR
> 
> "High priority — might be a 1x job?"
> It can be both. The initial run is a 1x job — pull everything relevant from the last 12-24 months, summarize it, hand you a doc. That's maybe 2-3 hours of compute time.
> 
> But the real value is making it recurring. A weekly PubMed scan costs essentially nothing and takes about 30 seconds. My suggestion: do the 1x backfill first to get you current, then set up an automated weekly scan that drops new papers into a Notion page or Slack channel. The weekly run is zero-maintenance — just a scheduled job that runs on its own.
Sounds great!
> 
> PRESS & NARRATIVE TRACKER
> 
> "Very important to understand what is happening in the space" / "To show that interest in the space is growing" / "To understand what the content and narrative is."
> Crystal clear on the use cases. Three deliverables:
> 
> 1. A running log showing growing media interest in male fertility (useful in investor conversations even while not actively fundraising)
> 2. Narrative tracking — what angles journalists and podcasters are taking
> 3. Early competitor press detection
> 
> "Can we use Claude or similar to populate the most relevant news before forwarding?"
> Yes, exactly. The flow: Google Alerts + podcast transcript APIs feed raw results into Claude, which filters for relevance, tags each item (competitor mention, new research, market trend, etc.), writes a 1-2 sentence summary, and ranks by importance. You'd get a weekly Slack digest or Notion page with only the stuff that matters — not a firehose.
Lovely!! :)
> 
> BUILD TIMELINE
> 
> "Do we really think this takes this long? I've done a 75% version of the Amazon/Tagger scraping and it took 30 minutes of active work and then about 1-2 hours of the agent working."
> Fair challenge. You're right that the scraping itself is fast. The week-long timelines were accounting for setup, testing, LLM prompt iteration, and making things robust enough that you and Avery can run them without me. If you're comfortable with a "works but might need babysitting" version, we can compress significantly. I'll bring a tighter timeline on Monday.
Let’s discuss today what we see as priority. :)
> 
> "What do you suggest for: CRM, Task management (with timeline)?"
> 
> My recommendation:
> - CRM: Google Sheets, fed by the CRM Intake Agent via Slack. Simple, shareable, works well until you hit ~500+ contacts. At that point you'd graduate to HubSpot free tier or Attio.
> - Task management with timeline: Notion. A single database with multiple views — table view for everything, Kanban board by status, and timeline/calendar view for deadlines. The Meeting Notes agent writes directly into this.
Perfect!
> 
> 
> 
> Monst Benefit
> Ignoring the specific tools, the thing that would move the needle most for Seedbox right now is a single operational hub where every action item, contact, and piece of market intel lands without anyone manually filing it. Right now your knowledge is fragmented across WhatsApp, email, and memory.
> 
> The Meeting Notes to Tasks agent solves the most acute pain — nothing falls through the cracks after a call. The CRM agent solves the second — you always know who you know and how to reach them. Everything else (literature monitor, press tracker, competitor intel) gives you strategic advantages, but the first two are operational survival. You were right to flag task management as priority 1.
> 
> I'll bring a proposed Notion schema to the Monday call so we can set it up together.
I have a meeting scheduled for today. Would you like to move it? :)
