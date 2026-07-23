# Programmatic Memory Is the Agent’s Real Context Window

**Thesis:** PRO-LONG is important less because it posts another high ARC-AGI-3 score, and more because it makes a clean architectural claim: for long-horizon agents, the right memory primitive may be a complete append-only event log plus code-based search, not ever-larger prompt stuffing or premature summarization.

## Abstract

Fox, Wang, Rosu, and Dhingra’s **PRO-LONG: Programmatic Memory Enables Long-Horizon Reasoning** (arXiv:2607.20064v1, 22 July 2026) is this afternoon’s best paper to read because it isolates a recurring production-agent lesson in unusually concrete form. Long-horizon agents fail not only because the base model lacks “reasoning,” but because the harness decides what the agent can remember and how it can re-enter old experience. PRO-LONG chooses a deliberately boring write policy—append every action and observation to a structured log—and a powerful read policy: let a coding agent use files, search, and Python over that log. On the full 25-game ARC-AGI-3 public set, the authors report average gains of 18.0 percentage points over a no-log coding-agent baseline across frontier models; matched comparisons claim 4.2–5.8× fewer billed tokens than stronger specialized harnesses; Fable 5 with a 2,000-action budget reaches 94.6% pass@1 and 97.4% best@2 at a reported total cost around $1,750. The caveats are substantial: public-set saturation is not semi-private generalization, run variance is high, model names are future/frontier-specific, and the referenced GitHub repository was not reachable during this cron run. Still, the design pattern is durable: keep lossless history outside the context window, make memory executable, and measure agents by their ability to re-query their own past.

## Table of contents

1. [Context: the long-horizon memory bottleneck](#context-the-long-horizon-memory-bottleneck)
2. [Core mechanism: append-all write, programmatic read](#core-mechanism-append-all-write-programmatic-read)
3. [Evidence: what the paper actually reports](#evidence-what-the-paper-actually-reports)
4. [Interpretation: why this matters](#interpretation-why-this-matters)
5. [Caveats: where not to overread](#caveats-where-not-to-overread)
6. [Michael-specific implications](#michael-specific-implications)
7. [Concept map](#concept-map)
8. [Open questions and next experiments](#open-questions-and-next-experiments)
9. [Sources](#sources)

## Context: the long-horizon memory bottleneck

The obvious story about long-horizon agents is “give the model a longer context window.” That story has been weakening for a while. Chroma’s 2025 *Context Rot* report argues, across 18 LLMs, that models do not use context uniformly and that performance becomes increasingly unreliable as input length grows, even under controlled tasks where nominal difficulty is held fixed.[^contextrot] The ARC-AGI-3 benchmark pushes this weakness into an agentic setting: an agent is dropped into 25 public turn-based game environments, gets grid observations and legal actions, but receives no rule sheet, object list, goal statement, or shaped reward.[^arc3] The task is not to recall one hidden string; it is to infer the world.

This is a memory problem in a strict sense. A failed action at step 40 may become the key evidence at step 900. A color pattern that initially appears irrelevant may become decisive after the agent discovers a hidden mechanic. If the harness summarizes early experience too aggressively, the decisive fact can vanish. If it keeps everything in the active prompt, the model pays for a swollen context and may still fail to retrieve the right fact. If it uses vector retrieval, it must guess a similarity metric before the agent knows what the relevant abstraction is.

PRO-LONG’s contribution is to refuse that tradeoff. It says: do not decide what is important at write time. Save the whole trajectory. Decide relevance later, with code.

## Core mechanism: append-all write, programmatic read

The paper frames agent context as two different things:

- **Accessed information:** what is currently inside the model’s active context window.
- **Accessible information:** tool-reachable external state, such as files, logs, notes, and code.

PRO-LONG’s write operation is deliberately lossless: after each action, it appends a structured record of the action and observation to a log. The active model does not need to compress, summarize, rank, or curate the experience while the task is still unfolding.

The read operation is where the intelligence moves. Because the agent is a coding agent with file-system and shell access, it can run `grep`-style searches, parse logs with Python, reconstruct state transitions, count patterns, write hypothesis tests, and build small simulators. Memory becomes not a bag of embeddings but a dataset the agent can query.

This is a subtle shift from “memory as facts” to **memory as inspectable instrumentation**. A normal long-term memory system asks: what facts should be retained? PRO-LONG asks: what complete event trace should be available so the agent can compute the facts later?

That choice is aligned with a broader 2026 pattern. The paper cites work arguing that coding agents are effective long-context processors: file systems and executable tools let agents externalize long-context processing from latent attention into explicit operations over text corpora.[^codinglong] PRO-LONG applies the same philosophy to the agent’s own experience.

## Evidence: what the paper actually reports

The main benchmark is **ARC-AGI-3**, whose technical report describes interactive abstract environments calibrated so humans can solve the public environments while frontier AI systems scored below 1% at the benchmark’s March 2026 introduction.[^arc3] ARC-AGI-3 uses **Relative Human Action Efficiency** (RHAE), comparing an agent’s per-level action count against a first-exposure human baseline.

The paper reports several concrete results:

1. **Average gain over a no-log coding-agent baseline.** On the full public game set, PRO-LONG improves over a base coding agent by an average of **18.0 percentage points** across frontier models.[^prolong]

2. **Matched score/cost comparisons.** Under matched scoring setups, PRO-LONG is reported as comparable to or better than specialized harnesses while using **4.2–5.8× fewer billed tokens**. In one Codex-family comparison, the extracted text reports PRO-LONG at **41.2 pass@1** versus WorldModeler’s **45.1**, while using **4.2× fewer billed tokens**; in Claude-family comparisons it either surpasses or comes within a few points of specialized systems depending on the model and harness.[^prolong]

3. **High-budget Fable 5 run.** With Fable 5 at a **2,000-action budget**, PRO-LONG reports **94.6% pass@1** at a cost of **$1,500** / **150M billed tokens**, and **97.4% best@2** at a total cost of **$1,750**.[^prolong]

4. **Tool-ladder ablation.** The tool access ladder matters. For GPT-5.5, the extracted Table 1 reports: read-only **23.1%**, plus grep/regex search **27.2%**, plus Python **38.3%**, plus write/edit **41.2%**. This supports the authors’ claim that programmatic access is not decoration; it is a causal part of the harness.[^prolong]

5. **Workspace persistence ablation.** PRO-LONG is robust to clearing the workspace every call because the full log remains available: persistent workspace **41.2 ± 3.5**, cleared every call **40.7 ± 3.6**. The no-log baseline drops from **24.0 ± 2.0** to **19.9 ± 2.1** under the same clearing condition. This is a useful control because it suggests the append-only event log, not merely arbitrary scratch files, is carrying much of the benefit.[^prolong]

6. **Tool-use distribution.** In GPT-5.5 runs, PRO-LONG spends more tool calls on programmatic analysis: Python rises from **40.8%** in no-log to **60.6%** in PRO-LONG; log-parsing tools account for **20.3%** of calls; search across turns accounts for **9.6%**. The baseline spends far more on workspace management (**59.2%** vs **19.1%**).[^prolong]

The qualitative examples matter because they explain the mechanism. The paper says PRO-LONG is especially helpful in games requiring longer-horizon reasoning, including examples where logs exceeded **320,000 lines**. The agent can search old transitions, build a world model, and plan with breadth-first search rather than repeatedly re-discovering the same facts by acting in the environment.

## Interpretation: why this matters

The simplest reading is “better ARC-AGI-3 harness.” The more useful reading is “a memory system should preserve optionality.”

Summarization is attractive because it lowers token cost, but it is a lossy bet on what will matter later. Retrieval is attractive because it avoids full-context cost, but it often depends on semantic similarity before the agent has discovered the right ontology. PRO-LONG’s append-all log is expensive in storage but cheap in decision regret: it keeps every observation queryable until the agent knows what question to ask.

For company agents, this maps cleanly onto audit logs. A finance research agent may not know at 09:30 that a small footnote in a filing matters to the trade thesis. A customer-support agent may not know which earlier complaint will later identify a systemic incident. A coding agent may not know which failed test run first revealed the root cause. The memory substrate should therefore be lossless at the event layer and selective at the access layer.

The paper also reinforces a point from the recent multi-agent and harness literature covered in prior AI Research OS essays: the harness is part of the model. A base model plus an event log plus Python is not the same cognitive system as the same base model plus a summarized scratchpad. PRO-LONG’s reported tool-ladder ablation makes that visible.

## Caveats: where not to overread

Several cautions are necessary.

First, **ARC-AGI-3 public performance is not the same as private-set generalization**. The Schema release from Impossible Research, also focused on ARC-AGI-3, explicitly warns that its near-ceiling public-set results are self-reported and that public-to-semi-private transfer is unknown.[^schema] PRO-LONG is not making exactly the same claim, but the same benchmark epistemology applies: public game scores are suggestive, not proof of durable agentic intelligence.

Second, **run variance is high**. The PRO-LONG authors emphasize independent-run variation and report best@k where possible. This matters operationally: a production agent cannot usually spend $1,750 per task and pick the best of two runs unless the task value justifies it.

Third, **the model frontier is moving underneath the harness**. The paper evaluates models such as GPT-5.5, Opus 4.6, and Fable 5. Those model names and costs are paper-reported conditions, not independently revalidated by this cron run. The conclusion I trust most is not “Fable 5 solves ARC-AGI-3,” but “programmatic memory strongly changes the performance/cost surface.”

Fourth, **code availability was not verified**. The arXiv abstract states that relevant code and logs are available at `https://github.com/alexisfox7/PRO-LONG`, but during this run that repository returned 404 via both raw README and GitHub API checks. The paper itself and arXiv HTML/PDF were reachable; the repository was not. Treat replication as pending.

Fifth, **append-only logs create governance problems**. Lossless memory is good for reasoning and bad for privacy if unscoped. A company OS cannot simply record everything forever. It needs data classification, redaction, retention limits, access control, and source-linked deletion semantics.

## Michael-specific implications

### Agentic company OS

Make the event log the primitive. Every long-running agent should have a structured, append-only, queryable task ledger: observations, actions, tool outputs, state diffs, failures, approvals, and rollbacks. The active context should be a working set derived from that ledger, not the ledger itself.

A practical design:

- `events.jsonl`: lossless task trace with timestamps, source IDs, tool names, action classes, and hashes.
- `derived/`: agent-written scripts, hypotheses, state parsers, and world models.
- `queries/`: saved retrieval/search programs that explain how evidence was found.
- `receipts/`: commit-boundary artifacts for externally visible or regulated actions.
- `summaries/`: optional lossy views, never the source of truth.

### AI/product strategy

The product wedge is not “infinite memory”; it is **programmable memory with audit controls**. A dashboard should let operators ask: what did the agent see, what did it test, what old evidence changed its mind, and which log query supports this claim? This is more defensible than chat-history search or generic vector memory.

### Finance/trading research

Finance is a long-horizon partial-observability problem. The agent does not know in advance whether a supplier reference, covenant clause, insider-sale footnote, or macro release revision will matter. Use PRO-LONG’s lesson to separate:

- raw evidence ledger: filings, transcript snippets, prices, revisions, broker notes;
- programmatic read layer: parsers, joins, event studies, anomaly scans;
- memo layer: human-readable thesis;
- action layer: no-trade / trade / watchlist decisions with receipts.

Most “AI trading” failure modes will come from lossy memory and hidden transformations before they come from lack of model cleverness.

### Career/opportunities

A high-value niche is **agent memory infrastructure engineer**: building event ledgers, programmable retrieval, retention policy, replay tooling, and evaluation harnesses for regulated workflows. This is less glamorous than frontier prompting but closer to where durable enterprise value will concentrate.

## Concept map

- **Long-horizon reasoning → requires → sustained state reconstruction**
- **Active context → bottlenecked by → token cost and context rot**
- **Accessible memory → should preserve → optionality**
- **PRO-LONG → implements → append-only structured log**
- **Programmatic read → uses → grep/search/Python/file system**
- **Coding agents → convert → latent long-context processing into explicit computation**
- **ARC-AGI-3 → tests → exploration, world-model inference, and action efficiency**
- **World model → becomes useful when → verifiable against complete history**
- **Best@k variance → implies → allocation/retry policy matters**
- **Company OS memory → needs → privacy, retention, provenance, and replay controls**
- **Finance research agents → need → raw evidence ledger + programmatic read layer + action receipts**

## Open questions and next experiments

1. Can PRO-LONG’s append-only log pattern improve non-game tasks such as code migration, fraud investigation, market research, and due-diligence memos?
2. What is the minimum schema for an agent event log that supports replay, privacy controls, and programmatic querying across tools?
3. Does code-based log search outperform vector retrieval on enterprise workflows where relevance is discovered late?
4. Can an agent learn when to summarize without losing optionality—e.g., retain raw events but create typed indexes over them?
5. How much of PRO-LONG’s gain comes from full-history access versus inducing executable world models?
6. What is the public-to-private-set transfer for PRO-LONG-style harnesses on ARC-AGI-3?
7. Can cost-aware retry policies close the gap between pass@1 and best@k without uncontrolled spend?
8. How should regulated companies retain complete agent logs while respecting privacy, deletion, and privilege boundaries?

## Sources

[^prolong]: Alexis Fox, Junlin Wang, Paul Rosu, Bhuwan Dhingra. **PRO-LONG: Programmatic Memory Enables Long-Horizon Reasoning**. arXiv:2607.20064v1, 22 July 2026. https://arxiv.org/abs/2607.20064v1 ; HTML full text used in this run: https://arxiv.org/html/2607.20064v1

[^arc3]: ARC Prize Foundation. **ARC-AGI-3: A New Challenge for Frontier Agentic Intelligence**. arXiv:2603.24621v2. https://arxiv.org/abs/2603.24621

[^codinglong]: Weili Cao, Xunjian Yin, Bhuwan Dhingra, Shuyan Zhou. **Coding Agents are Effective Long-Context Processors**. arXiv:2603.20432v1. https://arxiv.org/abs/2603.20432

[^contextrot]: Kelly Hong, Anton Troynikov, Jeff Huber. **Context Rot: How Increasing Input Tokens Impacts LLM Performance**. Chroma Technical Report, 14 July 2025. https://www.trychroma.com/research/context-rot

[^schema]: Impossible Research. **[schema]: Frontier Models with the Right Harness Achieve ~99% on ARC-AGI-3 Public**. July 2026. https://schema-harness.github.io

Additional background consulted:

- Charles Packer et al. **MemGPT: Towards LLMs as Operating Systems**. arXiv:2310.08560v2. https://arxiv.org/abs/2310.08560
- Zeyu Zhang et al. **A Survey on the Memory Mechanism of Large Language Model based Agents**. arXiv:2404.13501v1. https://arxiv.org/abs/2404.13501
- Prateek Chhikara et al. **Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory**. arXiv:2504.19413v1. https://arxiv.org/abs/2504.19413
