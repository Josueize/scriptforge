# Part 2: What I'd build at Blue Foxes

## The workflow I'd automate first

The workflow I'd prioritise is the one I've already built here: a multi-agent content repurposing platform — a system where a content strategist enters one idea once, and every publish-ready asset for every channel is generated automatically, refined, and queued for publication without the team touching a prompt or an API.

## The problem it actually solves

The bottleneck at any content-first company operating at scale isn't ideation, and it isn't scripting — it's the repetitive downstream work of adapting one piece of content into five different formats for five different platforms. That adaptation work is manual, slow, inconsistent, and structurally identical every single time — which makes it a textbook automation target.

## What the platform does

A content strategist enters a topic, target audience, brand voice, and content goal. The platform:

1. Uses OpenAI GPT-4o to generate the initial video script
2. Routes that draft through Claude Sonnet for tone refinement and brand voice consistency
3. Validates the output before further processing
4. Formats the refined script in parallel for every selected platform
5. Stores everything in PostgreSQL, delivers it to a React dashboard, and waits for human approval

On approval, an n8n webhook fires automatically: Slack notifies the creative team, a Google Doc is created, the CMS receives a scheduling request.

## Why this architecture is production-ready

The AI layer uses two models deliberately — each doing what it's better at. Retry logic with exponential backoff means a rate-limited API call recovers automatically. Platform formatting runs concurrently via asyncio.gather. The pipeline is isolated from the HTTP layer entirely. The automation layer is a first-class part of the architecture, not bolted on after the fact.

## Why this workflow first

Because it eliminates the most repetitive, high-volume work at the top of the content funnel. Every piece of content the team produces passes through this pipeline. Automating it compounds across every piece of content, every week, as the team scales.