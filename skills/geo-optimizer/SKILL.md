## name: geo-reviewer
description: Reviews a webpage URL and provides actionable suggestions to improve GEO (Generative Engine Optimization) — how well the page will be cited and recommended by AI search engines like ChatGPT, Perplexity, Gemini, and Copilot.

# GEO Reviewer Skill

## What is GEO?

Generative Engine Optimization (GEO) is the practice of optimizing web content so AI-powered search engines (ChatGPT, Perplexity, Gemini, Copilot, etc.) will cite and recommend your pages. It differs fundamentally from traditional SEO:

- AI prioritizes **semantic meaning** over keywords
- AI favors **citation authority** over backlinks
- AI rewards **direct answers** over click-optimized headlines
- AI sources often come from **page 21+ in Google results** — your SEO rank doesn't matter much
- AI traffic converts at **3–17x** the rate of traditional channels (Microsoft study of 1,200+ sites)

-----

## Workflow

When asked to review a URL for GEO:

### Step 1: Fetch the page

Use the `web_fetch` tool to retrieve the full page content. Focus on:

- The HTML source (not just rendered text) — check if content is in HTML vs JS-rendered
- Page title, headings (H1–H3), meta description
- Opening paragraphs (first 40–60 words are critical)
- FAQ sections, schema markup indicators
- robots.txt accessibility (if inferable)

### Step 2: Analyze against the GEO framework

Evaluate the page across these dimensions:

#### A. Content Structure (High Impact)

- Does the page follow **Question → Direct Answer → Evidence → Follow-up Questions** format?
- Is the **direct answer in the first 40–60 words**?
- Are there **statistics every 150–200 words**?
- Is there **FAQ formatting**?
- Is content **problem-solving focused** rather than fluffy/opinion-based?
- Are answers **evergreen and definitive** (not trend-chasing)?

#### B. Technical Crawlability (High Impact)

- Is content in **server-side rendered HTML** (not JavaScript-dependent)?
- Does the page appear to block AI crawlers? (Check for signals like noindex, aggressive bot blocking)
- Is **FAQ schema markup** or other structured data present?
- Is content structured for **LLM summarization** (clear sections, no walls of text)?

#### C. Semantic Authority (Medium Impact)

- Does content demonstrate **expertise and specificity** on a topic?
- Are there **citations, statistics, or research references**?
- Is the content **comprehensive enough** to be a "definitive" source?
- Does it answer **multiple related queries** (breadth of coverage)?

#### D. Distribution Signals (Medium Impact)

- Is similar content likely distributed on **external platforms** (Reddit, niche forums, technical blogs, YouTube)?
- Are there **internal links** to related definitive content?

#### E. AI Infrastructure (Medium Impact)

- Any evidence of **llms.txt** file?
- Sitemap signals for **Bing Webmaster Tools** submission?
- No indication of **GPTBot/ClaudeBot/PerplexityBot blocking** in robots.txt?

### Step 3: Generate the report

Structure your output as follows:

-----

## GEO Review: [Page Title / URL]

### Overall GEO Score: [X/10]

Brief 1–2 sentence summary of the page's current AI-citation readiness.

### 🔴 Critical Issues (Fix First)

List 1–3 high-impact problems preventing AI citation. Be specific — quote actual text or structural problems observed.

### 🟡 Improvements (High ROI)

List 3–5 specific, actionable improvements with expected impact. For each:

- **What**: What to change
- **Why**: Why AI engines will respond better
- **How**: Concrete implementation guidance

### 🟢 What's Working

Note 2–3 things the page already does well for GEO.

### Quick Wins

List 2–3 changes that could be made in under an hour with potentially significant GEO impact. (The Tastewise example: restructuring + FAQ schema led to 600% visibility spike in one week.)

### Technical Checklist

- [ ] Content in server-side HTML (not JS-rendered)
- [ ] AI crawlers not blocked (GPTBot, ClaudeBot, PerplexityBot)
- [ ] FAQ schema markup present
- [ ] llms.txt file exists
- [ ] Sitemap submitted to Bing Webmaster Tools
- [ ] Direct answer in first 40–60 words
- [ ] Statistics present every 150–200 words

-----

## Key Principles to Apply

### What AI Engines Want

1. **Problem-solving content** — not opinions or brand perspectives
1. **Definitive, evergreen answers** — median age of cited Reddit posts is 1.5 years
1. **Structured Q&A format** — Question → Answer → Evidence → Follow-ups boosts AI visibility by up to 40%
1. **Semantic depth** — content that covers the intent behind 200–400 different related queries
1. **Citable statistics** — data-rich content gets cited more

### What AI Engines Ignore

- Keyword density and exact-match phrases
- Page 1 Google rankings (90% of AI citations come from page 21+ in Google)
- Click-bait headlines
- Fluffy thought-leadership without substance
- JavaScript-rendered content (AI crawlers don't execute JS — ~11.5% of ChatGPT requests are unused JS files)

### The Current Opportunity

Most companies are still applying 2015 SEO playbooks. Early movers establishing AI citation patterns now create compounding advantages that become increasingly hard for competitors to displace. AI traffic also converts at significantly higher rates than traditional channels (Adobe: 32% better revenue per visit by Jan 2026).

-----

## Example Eval Prompts

To test this skill, use prompts like:

- "Review https://example.com/blog/post for GEO improvements"
- "How well optimized is https://startup.com/product for AI search?"
- "What GEO changes should I make to https://mysite.com/about?"

## Expectations for Good Output

- Identifies whether content is JS-rendered vs HTML-accessible
- Evaluates first 40–60 words for direct-answer presence
- Checks for FAQ structure and statistics frequency
- Provides at least 3 specific, actionable recommendations
- Includes a technical checklist with honest pass/fail assessment
- Gives a prioritized list (critical → high ROI → quick wins)
- Avoids generic SEO advice — recommendations must be GEO-specific
