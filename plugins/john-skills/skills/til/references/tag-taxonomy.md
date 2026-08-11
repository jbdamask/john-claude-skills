# TIL tag taxonomy

Tags come from this taxonomy — never invent new ones outside its rules. A controlled vocabulary is what makes a pile of TILs searchable by humans and agents alike; endless one-off tags (`ai-skills`, `skill-design`, `agent-tools`…) fragment the collection until no search finds anything.

## Shape

A tag is a path of one to three levels, slash-separated, all lowercase: `data`, `data/databases`, `data/databases/dynamodb`. Three levels is a hard maximum.

- **Level 1** is a fixed set of nine categories. Never add a level-1 category.
- **Level 2** is a curated list per category (below). Add a new level-2 only when nothing listed fits, and make it broad enough that other TILs will reuse it.
- **Level 3** is a specific technology, product, or standard (`dynamodb`, `react`, `oauth`). Singular nouns, no versions, no project names.

## Rules

1. **Prefer the broadest level that is accurate.** Tag `cloud/aws`, not `cloud/aws/iam`, unless the learning is genuinely about IAM specifically. Broad tags group; fine tags fragment.
2. **1–3 tags per TIL.** One is fine. The first tag is the primary subject.
3. **Descend a level only when the parent would mislead or the detail aids retrieval.** "Would someone searching this term want this TIL?" decides it.
4. **No synonyms, no duplicates along one path.** `data/databases/dynamodb` already implies `data` — don't tag both.

## The nine categories

**`ai`** — models, agents, prompting, and tooling for AI.
Level 2: `agents`, `models`, `prompting`, `skills`, `mcp`, `rag`

**`code`** — writing and maintaining software, language-agnostic or language-specific.
Level 2: `languages`, `testing`, `debugging`, `performance`, `architecture`, `libraries`

**`data`** — storing, moving, and shaping data.
Level 2: `databases`, `pipelines`, `formats`, `analytics`

**`cloud`** — cloud platforms and infrastructure.
Level 2: `aws`, `gcp`, `azure`, `infra-as-code`, `serverless`

**`web`** — building for the web.
Level 2: `frontend`, `backend`, `apis`, `browsers`, `http`

**`security`** — keeping systems and data safe.
Level 2: `secrets`, `auth`, `vulnerabilities`, `privacy`

**`devops`** — shipping and operating software.
Level 2: `git`, `ci-cd`, `deployment`, `monitoring`, `tooling`

**`writing`** — producing and publishing prose.
Level 2: `style`, `docs`, `publishing`

**`process`** — how work gets done.
Level 2: `workflow`, `design`, `collaboration`, `productivity`

## Examples

- A DynamoDB pagination gotcha: `data/databases/dynamodb`, `cloud/aws`
- A lesson about designing portable AI skills: `ai/skills`, `process/design`
- A CSS trick: `web/frontend/css`
- A finding about secrets leaking into logs: `security/secrets`
