# Sales Call Prep Agent

## Description

An agent that researches prospects and prepares personalized briefings before sales calls.

Given a list of companies or contacts, the agent researches each one and produces a concise briefing document with everything you need to have an informed conversation. It finds recent news, identifies potential pain points, surfaces connections to your offering, and suggests talking points.

The agent remembers your previous interactions with each prospect. If you've talked to Acme Corp before, it recalls what was discussed, what objections came up, and what messaging resonated. This context carries across sessions.

For multiple prospects, the agent prioritizes by deal potential and time-sensitivity, letting you focus prep time where it matters most.

**What the agent needs from you:**
- Company names or contact list (can be pasted, uploaded as CSV, or pulled from CRM)
- Your product/service (one-time setup, then remembered)
- Any known context ("met them at a conference," "inbound from website")
- Time available for prep (adjusts depth accordingly)

## Example Session

```
User: I have 6 calls tomorrow. Can you prep me?

Acme Manufacturing - 10am
Brightside Health - 11am
Coastal Logistics - 1pm
DataFlow Systems - 2pm
EverGreen Energy - 3pm
FirstRate Financial - 4pm

Agent: I'll research all 6 and prepare briefings. A few quick questions:

1. Are any of these existing conversations, or all new prospects?
2. How much time do you have—quick bullets or deep research?
3. Any specific angles you want me to look for? (Recent funding, leadership changes, tech stack, etc.)

User: Acme and Coastal are follow-ups from last month. Others are new. I have about an hour to prep—give me enough to sound informed but don't go overboard.

Agent: Got it. I'll do focused research on the 4 new prospects and pull up your previous notes on Acme and Coastal.

[progress: researching Brightside Health...]
[progress: researching DataFlow Systems...]
[progress: researching EverGreen Energy...]
[progress: researching FirstRate Financial...]
[progress: retrieving Acme Manufacturing history...]
[progress: retrieving Coastal Logistics history...]

Agent: Here are your briefings, prioritized by opportunity:

---

**PRIORITY: DataFlow Systems** (2pm) ⭐
*Why priority: Just raised $40M Series C, actively hiring for ops roles—likely scaling fast*

- **What they do:** Data integration platform for mid-market companies
- **Recent news:** Series C announced 2 weeks ago, expanding to European market
- **Key person:** You're meeting Sarah Chen (VP Ops)—promoted 3 months ago from Director
- **Pain point signal:** 4 job postings for "data operations" suggest they're overwhelmed
- **Your angle:** Position as force multiplier for their scaling ops team
- **Opening line:** "Congrats on the Series C—saw you're expanding to Europe. How's the team handling the growth?"

---

**Acme Manufacturing** (10am) 🔄 *Follow-up*

- **Last conversation:** March 15—spoke with Tom Bradley (Procurement)
- **What happened:** Interested but said they're mid-contract with incumbent until Q3
- **Objection raised:** "Switching costs concern us"
- **What resonated:** You showed the ROI calculator, he asked for case studies
- **Status:** You sent 2 case studies, no response yet
- **Your angle:** Check if Q3 timeline is still accurate, offer pilot program
- **Opening line:** "Tom, wanted to check in—last time you mentioned evaluating options in Q3. Is that still the timeline?"

---

**Brightside Health** (11am)

- **What they do:** Telehealth platform, mental health focus
- **Recent news:** Launched new anxiety treatment program, partnership with Blue Cross
- **Key person:** Meeting with James Morrison (COO)
- **Pain point signal:** Glassdoor reviews mention "operational chaos" and "scaling too fast"
- **Your angle:** Operational efficiency for fast-growing health tech
- **Opening line:** "Saw the Blue Cross partnership news—that's a big deal. How's the team managing the growth?"

---

**Coastal Logistics** (1pm) 🔄 *Follow-up*

- **Last conversation:** March 20—spoke with Maria Santos (CTO)
- **What happened:** Strong interest, requested pricing for 500-seat deployment
- **Status:** You sent proposal, she said "reviewing with CFO this week" (3 weeks ago)
- **Your angle:** Check decision status, offer to address CFO concerns directly
- **Opening line:** "Maria, following up on the proposal—were you able to connect with your CFO? Happy to jump on a call with them if helpful."

---

**EverGreen Energy** (3pm)

- **What they do:** Renewable energy developer, solar and wind projects
- **Recent news:** Announced 3 new wind farm projects in Texas, stock up 15% this quarter
- **Key person:** Meeting with David Park (VP Technology)
- **Pain point signal:** LinkedIn post from David complaining about "tool sprawl"
- **Your angle:** Consolidation narrative—reduce tool sprawl
- **Opening line:** "I saw your post about tool sprawl—that resonates with a lot of our customers. What's driving that for you?"

---

**FirstRate Financial** (4pm)

- **What they do:** Regional bank, 50 branches across Midwest
- **Recent news:** Quiet—no major announcements in past 90 days
- **Key person:** Meeting with Linda Thompson (SVP Operations)
- **Pain point signal:** None obvious—may be exploratory
- **Your angle:** Discovery call, understand their current state
- **Opening line:** "Linda, I appreciate you taking the time—I'd love to learn more about how your team handles [your domain] today."

---

Anything you want me to dig deeper on?

User: This is great. Can you find out more about Sarah Chen at DataFlow? And what case studies did I send to Acme?

Agent: **Sarah Chen (DataFlow Systems):**
- Stanford MBA, 2018
- Previously at Snowflake for 3 years (Senior Manager, Customer Operations)
- Promoted to VP Ops at DataFlow in December
- LinkedIn shows she's connected to 2 people in your network: Mike Torres (your colleague) and Jennifer Wu (former customer)
- Recent post: Shared an article about "operational excellence in hypergrowth"

Consider mentioning the Mike Torres connection if appropriate, or reference the operational excellence theme.

**Acme case studies you sent:**
- March 17: "Midwest Manufacturing Corp" case study (PDF)
- March 17: "Atlantic Industrial" case study (PDF)

Both focus on procurement efficiency. Neither has been opened according to your email tracking (if you use one). Might be worth re-sending or offering to walk through one live.

User: Perfect. Let's finalize this.

Agent: Your sales prep briefings are ready. I've saved the key points about each call and will remember them for future follow-ups.

Good luck tomorrow!
```

## Deliverables

1. **Prioritized briefing document** with one section per prospect:
   - Company overview (what they do, size, industry)
   - Recent news and signals (funding, hiring, leadership changes)
   - Key person background (role, tenure, LinkedIn highlights)
   - Identified pain points or opportunities
   - Recommended angle and opening line
   - For follow-ups: conversation history, objections raised, pending items

2. **Quick-reference cheat sheet:**
   - One-line summary per call
   - Priority ranking
   - Key names and pronunciations if needed

3. **Updated CRM notes** (if connected):
   - Research findings attached to contact record
   - Follow-up tasks created for post-call actions
