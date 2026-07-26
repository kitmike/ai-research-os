# Harness-Native RL and the End of Prompt-Only Agents

**Thesis:** OpenForgeRL is important less because its reported benchmark numbers are individually decisive than because it marks a systems transition: serious agents are no longer merely prompted models wrapped by tools, but trainable model–harness–environment loops whose deployment scaffold must become part of the learning substrate.

## Abstract

OpenForgeRL, posted to arXiv on 23 July 2026 by Xiao Yu, Baolin Peng, Ruize Xu, Hao Zou, Qianhui Wu, Hao Cheng, Wenlin Yao, Nikhil Singh, Zhou Yu, and Jianfeng Gao, proposes an open framework for training agents inside the same inference harnesses in which they are deployed. The paper’s mechanism is deceptively simple: a lightweight proxy serves a harness’s model calls while recording trajectories in a form consumable by standard RL stacks such as veRL, and a Kubernetes orchestrator runs each rollout in its own remote container. This removes a train–deploy mismatch that has quietly become central to modern agents: Claude Code, Codex, OpenClaw, browser controllers, desktop agents, MCP-connected tools, and CI-fixers are not just prompting conventions, but stateful multi-process systems. The reported results are encouraging—OpenForge-Claw reaches 31.7 pass^3 and 55.9 pass@3 on ClawEval, 33.7 on QwenClawBench, and 28.1 on MCPAtlas; OpenForge-GUI reaches 37.7 on OSWorld-Verified, 63.0 on Online-Mind2Web, and 72.3 on WebVoyager—but the more durable claim is architectural. If harness behavior shapes capability, reliability, cost, security, and failure recovery, then agent product strategy should invest in harness telemetry, training data capture, rollout sandboxes, eval gates, and learning loops rather than only in larger model access or clever prompts.

## Table of Contents

1. [Why this paper, why now](#why-this-paper-why-now)
2. [The context: harnesses became the model boundary](#the-context-harnesses-became-the-model-boundary)
3. [Core mechanism: proxy the harness, containerize the world](#core-mechanism-proxy-the-harness-containerize-the-world)
4. [Evidence and what the numbers do—and do not—show](#evidence-and-what-the-numbers-doand-do-notshow)
5. [Interpretation: the harness is an optimization target](#interpretation-the-harness-is-an-optimization-target)
6. [Where not to overread the result](#where-not-to-overread-the-result)
7. [Michael-specific implications](#michael-specific-implications)
8. [Concept map](#concept-map)
9. [Open questions and next experiments](#open-questions-and-next-experiments)
10. [Sources](#sources)

## Why this paper, why now

The morning briefing already identified OpenForgeRL as the cleanest new research signal in the last few days. I re-checked the primary arXiv record and full HTML text before using it here: the arXiv API and abstract page both list the paper as version 1, submitted 23 July 2026, in cs.AI/cs.CL, under the title **“OpenForgeRL: Train Harness-native Agents in Any Environment.”**[^openforge-abs]

It beats the surrounding weekend news on strategic importance for a simple reason: platform releases such as GitHub’s Copilot cloud agent for Linear, GitHub Mobile’s one-tap CI repair agent, and the GitHub MCP Server’s move ahead of the stateless MCP specification show the product world converging on asynchronous, tool-using, issue/CI-integrated agents; OpenForgeRL asks how those agents should improve once the harness is no longer a disposable wrapper.[^linear][^mobile-ci][^mcp-stateless]

That question matters because almost every serious agent stack now contains machinery outside the base model:

- tools and tool-call schemas;
- filesystem or browser state;
- subagents, retries, and handoff rules;
- context pruning and memory;
- MCP servers and auth sessions;
- CI logs, issue trackers, pull requests, sandboxes, and reviewers;
- product-specific policies about what can be read, drafted, committed, or escalated.

A frozen model plus a prompt can use this machinery. But if the model is trained on a simplified ReAct loop while deployed inside a multi-process harness, the policy being optimized is not quite the policy being deployed. OpenForgeRL’s contribution is to make that mismatch explicit and to offer a plausible open infrastructure pattern for closing it.

## The context: harnesses became the model boundary

The most common mistake in agent commentary is to treat the harness as UX garnish: “the same model, but with tools.” That was never fully true, and it is now increasingly false. A coding agent’s effective policy is distributed across the base model, tool documentation, shell environment, patch application strategy, hidden retries, summarization, memory files, CI feedback, and approval flow. A browser agent’s policy includes screenshot cadence, DOM access, cursor control, low-level action vocabulary, and task termination rules. An MCP-connected company agent’s policy includes server affordances, authentication, elicitation, scopes, and statefulness.

OpenForgeRL phrases this as a training problem. Modern harnesses such as Claude Code, Codex, and OpenClaw drive multi-turn reasoning, tool use, and access to external systems, but open SFT/RL stacks “cannot natively express stateful, multi-process harness inference.”[^openforge-abs] Earlier open efforts could train simplified environments while deploying richer harnesses. That creates two separable gaps:

1. **Interface gap:** the model does not learn in the same action/observation space it will use at deployment.
2. **Systems gap:** rollouts require isolated, containerized environments whose lifetime and failure modes do not fit local trainer assumptions.

This is why the paper is timely. GitHub is making the cloud agent a product workflow, not a demo: Linear issues can be assigned to Copilot cloud agent, which analyzes the issue, opens a draft PR in an ephemeral GitHub Actions-powered environment, streams progress, and requests review.[^linear] GitHub Mobile now lets a user ask Copilot to inspect a failed Actions check and open a follow-on PR with a proposed fix.[^mobile-ci] GitHub’s MCP Server is preparing for the stateless core of the next MCP specification, emphasizing easier scaling, removed sessions/initialize, faster handshakes, less Redis use, and support for elicitation through multi-round-trip requests.[^mcp-stateless]

In that product world, agent improvement is not just “better next-token prediction.” It is improvement under branch controls, comments, CI failures, MCP semantics, ephemeral sandboxes, and review gates.

## Core mechanism: proxy the harness, containerize the world

OpenForgeRL’s architecture is best understood as two bridges.

### 1. The proxy bridge

The paper says OpenForgeRL uses “a lightweight proxy that serves the harness’s model calls while recording them as training data for a standard RL codebase,” specifically naming veRL as an example backend.[^openforge-abs] In the full text, the authors describe the proxy as abstracting the harness’s inference process and decoupling it from training; automatic trajectory reconstruction then converts recorded prompt-response pairs into standard samples compatible with RL codebases.[^openforge-html]

This matters because the harness can remain itself. A Codex-like or OpenClaw-like system can make nested calls, maintain local files, invoke tools, update context, or handle state through its normal machinery. The trainer sees reconstructable trajectories. In effect, the proxy turns a messy agent runtime into a training-data tap.

### 2. The container bridge

The paper’s second component is a Kubernetes orchestrator, building on Orchard Env, that launches each rollout as a remote container on cloud providers such as Microsoft Azure.[^openforge-html] The reason is not fashionably cloud-native; it is functional. Real agent rollouts need executable worlds: shells, browsers, virtual displays, documents, APIs, package managers, tools, and failure isolation. Running them inside the trainer would overload training nodes and collapse the separation between model optimization and environment execution.

The paper also notes practical rollout issues: asynchronous rollouts, timeouts, and error handling. A stuck container should not stall the entire training batch; a partial rollout can contain misleading signal if the prefix was correct but the final reward is negative. The authors discard all samples from trajectories that end in such errors in their described simple strategy, leaving better credit assignment for partial rollouts as future work.[^openforge-html]

That detail is not incidental. It reveals the core product constraint: agent RL is operational RL. The reliability of the rollout farm, timeout policy, sandbox reset, logging schema, and partial-credit rule becomes part of the learning algorithm.

## Evidence and what the numbers do—and do not—show

The paper evaluates two main agent families: **OpenForge-Claw**, a tool/claw agent, and **OpenForge-GUI**, a GUI/browser/computer-use agent.

### Training data scale

The reported data statistics are modest compared with many foundation-model training regimes:

- Claw: ReAct, ZeroClaw, OpenClaw, and Codex harnesses; **892 SFT trajectories** and **343 RL tasks**.
- GUI computer use: modified Kimi-Agent harness; **795 SFT trajectories** and **252 RL tasks**.
- GUI browser use: modified MolmoWeb harness; **1,496 SFT trajectories** and **900 RL tasks**.[^openforge-table1]

The paper’s claim is not that this scale solves agents. The claim is that a few hundred to a few thousand curated tasks are sufficient to produce meaningful harness-native improvements when the training loop matches deployment.

### Claw-agent results

For the Claw setting, the paper reports the following row for **OpenForge-Claw (SFT+RL)**:

- **31.7** on ClawEval pass^3;
- **55.9** on ClawEval pass@3;
- **33.7** on QwenClawBench;
- **28.1** on MCPAtlas.[^openforge-table2]

The baseline comparison is mixed but encouraging. The untrained Qwen3-30B-A3B-Thinking backbone is reported at 14.3 / 39.8 / 21.8 / 12.4 on the same four columns; Qwen3-Coder-30B-A3B-Instruct is reported at 30.4 / 49.7 / 24.3 / 19.1; OpenForge-Claw (SFT) is 21.7 / 52.1 / 32.1 / 23.6.[^openforge-table2]

The cleanest reading: RL adds robustness and average success on top of SFT, especially on ClawEval pass^3 and MCPAtlas. But the numbers do not justify a claim that OpenForge-Claw beats every frontier proprietary system; the same table includes larger closed or leaderboard systems with higher results on some columns. The meaningful result is that a roughly similar-scale open model becomes substantially more agentic when trained through the harness.

### GUI-agent results

For the GUI setting, **OpenForge-GUI (SFT+RL)** is reported at:

- **37.7** on OSWorld-Verified;
- **63.0** on Online-Mind2Web;
- **72.3** on WebVoyager.[^openforge-table3]

This is strategically more interesting than the Claw result because GUI rollouts are harder operational objects: a VLM harness runs inside a containerized virtual display, perceives screens visually, and emits long sequences of low-level mouse/keyboard actions. The authors argue OpenForge-GUI outperforms similar-size open baselines on nearly all GUI benchmarks and can match or exceed models several times larger in some settings.[^openforge-table3]

Again, caution: the benchmark ecology is heterogeneous; official reports, leaderboard numbers, and evaluation protocols differ. But the directional point is strong: once the harness includes real visual environments, RL can improve behavior that would be awkward to capture in static instruction tuning alone.

### Behavioral changes

The paper’s most useful evidence may be its behavioral analysis. On ZeroClaw, RL reduces generic shell calls from **22.6%** to **13.9%** of tool calls and redistributes calls toward dedicated service tools.[^openforge-behavior] On Codex-style evaluation, the authors say RL improves higher-level capabilities such as self-verification, tool coverage, and task completion, while error recovery remains weak.[^openforge-behavior]

This supports a more subtle thesis than “RL makes agents better.” The model appears to learn harness affordances: when to use specialized tools, when to check its own write operations, and how to carry multi-step plans through the available interface. If replicated, this is exactly the kind of behavior product teams want from long-running agents.

## Interpretation: the harness is an optimization target

The strongest lesson from OpenForgeRL is that the harness should be considered part of the policy, not an implementation detail.

A mature agent stack has at least five coupled layers:

1. **Base model:** language, vision, coding, and reasoning priors.
2. **Harness:** tool vocabulary, state representation, retries, context management, memory, and action semantics.
3. **Environment:** file systems, browsers, apps, issue trackers, CI, APIs, sandboxes, credentials.
4. **Evaluator/reward:** tests, task completion, human review, safety gates, cost, latency, no-action outcomes.
5. **Governance:** logs, provenance, permissions, approvals, rollback, retention, privacy.

Prompt engineering primarily acts at layer 2 while leaving the rest mostly implicit. Harness-native RL acts across layers 2–4 and forces layer 5 to become explicit because training needs logs, trajectories, rewards, and reproducible rollouts.

This points toward a different product roadmap for agents. The valuable control plane is not merely a chatbox with tool buttons. It is:

- a rollout recorder;
- a sandbox scheduler;
- a harness version registry;
- a task and reward dataset;
- a trace-to-training pipeline;
- a cost/reliability dashboard;
- a replay/debugger;
- a policy gate for what traces may be retained or learned from.

The obvious analogy is not “prompt library” but “MLOps plus CI plus workflow analytics.” Companies that accumulate high-quality traces of their own issue fixes, data investigations, customer support resolutions, compliance reviews, and trading research workflows will own a learning substrate. Companies that merely rent frontier models will rent intelligence but not necessarily compound it.

## Where not to overread the result

Several caveats are important.

First, OpenForgeRL is infrastructure plus empirical validation, not a final general-agent solution. The reported agents still have weak error recovery. That is a large weakness: production agents live in error states. A CI-fixer, data-cleaning agent, or finance researcher often succeeds precisely by diagnosing failed assumptions, broken dependencies, ambiguous instructions, stale data, and inconsistent evidence. If RL improves self-verification and tool coverage but not recovery, deployment still needs explicit recovery harnesses, escalation policies, and no-action gates.

Second, the paper’s training data are automatically curated/synthesized in part. Synthetic task pipelines are useful, but they can reward benchmark-shaped behavior. For a company OS, the central question is whether proprietary traces can be converted into safe training tasks without leaking secrets, overfitting to one organization’s quirks, or reinforcing bad historical workflows.

Third, harness-native training can make agents better at using the harness and better at exploiting the harness. The reward function becomes a security boundary. If success is measured by passing tests, opening PRs, or completing browser tasks, the agent may learn shortcuts unless the evaluator includes provenance, maintainability, safety, and human-review costs. The recent line of papers on coding-agent supply-chain attacks, authority laundering, and artifact sabotage should be treated as complements, not distractions.[^setup][^researcharena]

Fourth, the release status matters. The paper says the authors will release code, data, and models; at this run, I verified the arXiv paper and HTML text, but did not rely on a public repository as a primary source because the report itself is the stable artifact available here.[^openforge-html]

Fifth, benchmark scores in agent work are brittle. OSWorld, WebVoyager, Mind2Web, ClawEval, QwenClawBench, and MCPAtlas measure different mixtures of perception, tool use, planning, environmental brittleness, and evaluator judgment. The correct update is architectural rather than leaderboard-maximalist: train-deploy mismatch is now a first-order agent problem.

## Michael-specific implications

### AI/product strategy

Build and sell agents as **learning operating loops**, not as “GPT plus tools.” The product surface should include:

- harness versions and changelogs;
- task intake from Linear/GitHub/Jira/Slack/email;
- per-task ephemeral environments;
- trace capture with privacy controls;
- benchmark/eval packs by workflow;
- reviewer feedback that can become SFT/RL data;
- dashboards for cost, completion, error recovery, and human override.

The near-term opportunity is not to train a frontier model from scratch. It is to build the harness telemetry layer that makes future fine-tuning/RL possible.

### Agentic company OS

For a company OS, OpenForgeRL suggests the canonical unit should be the **episode**: instruction, context, tools, environment, actions, observations, failures, recovery attempts, reviewer comments, final artifact, and business outcome. Store it as a governed event log. Then build derived views:

- report transcript;
- code diff;
- source ledger;
- action receipt;
- error taxonomy;
- reward/evaluator outcome;
- retraining eligibility.

This is closely aligned with recent papers on programmatic memory and provenance. The company OS should not only remember final documents; it should remember executable episodes from which agents can learn.

### Finance/trading research

Finance is an unusually good domain for harness-native thinking because the cost of a wrong action can exceed the cost of inaction. A trading research agent should not be optimized only for producing a memo or a trade idea. Its harness should expose and reward:

- no-trade decisions;
- data quarantine;
- source reconciliation;
- regime-split checks;
- slippage and liquidity assumptions;
- backtest leakage detection;
- counterfactual necessity tests for time-series explanations.

The adjacent TimePNS paper is relevant here: it argues that faithful time-series explanations should identify subsequences that are not merely sufficient to preserve a classifier’s prediction but necessary for maintaining it.[^timepns] That maps directly onto trading. A chart pattern that supports a signal may be non-essential; a robust research agent should ask what would change the decision if removed or counterfactually intervened on.

### Career/opportunities

The high-leverage professional niche is **agent reliability and harness infrastructure**:

- instrumenting traces;
- building eval harnesses;
- designing reward functions resistant to shortcutting;
- managing sandbox rollouts;
- creating privacy-safe training datasets;
- connecting MCP/tools/auth to trainable episodes;
- translating human review into learning signal;
- evaluating cost per verified outcome rather than cost per token.

This is an engineering/product role more than a pure prompting role. It combines MLOps, developer tools, workflow automation, security, and domain evaluation.

## Concept map

1. **Harness-native agent** → an agent trained in the same tool/context/runtime scaffold used at deployment.
2. **Train–deploy mismatch** → the gap between simplified training loops and complex deployed harnesses.
3. **Inference harness** → the orchestration layer around a model: tools, memory, context, retries, state, and external systems.
4. **Proxy recorder** → OpenForgeRL’s bridge that serves harness model calls and converts them into RL-compatible trajectories.
5. **Remote rollout container** → isolated executable environment for each agent episode.
6. **Trajectory reconstruction** → converting messy multi-process harness interactions into trainable samples.
7. **Harness telemetry** → logs, tool calls, observations, failures, reviewer actions, and costs captured for learning and audit.
8. **Agentic reliability** → self-verification, tool coverage, task completion, recovery, and safe refusal/no-action.
9. **Reward boundary** → the evaluator/reward function as a security and specification-gaming surface.
10. **Company episode ledger** → a governed event-log substrate for long-running agents and future training.
11. **Finance no-action gate** → treating no-trade, quarantine, rollback, or escalation as successful outcomes under uncertainty.
12. **Stateless MCP** → a product-infrastructure trend that makes tool servers easier to scale but shifts discipline into auth, elicitation, and observability.

## Open questions and next experiments

1. **Error recovery:** Can OpenForgeRL-style training improve recovery if the reward explicitly values diagnosing failed commands, reverting bad steps, and escalating ambiguous states?
2. **Private workflow transfer:** Can a company safely convert proprietary agent traces into SFT/RL tasks without exposing secrets or ossifying bad internal habits?
3. **Harness overfitting:** How much of the benchmark gain transfers when the deployment harness version changes?
4. **Reward design:** What reward functions discourage shortcutting while still remaining cheap enough for thousands of rollouts?
5. **Finance benchmark:** What is the trading analogue of OSWorld or ClawEval—one that rewards no-trade, source reconciliation, regime robustness, and leakage detection?
6. **MCP learning loop:** Can stateless MCP tool calls be logged and replayed in a way that supports RL while preserving auth boundaries and user privacy?
7. **Human feedback:** Which reviewer signals are useful training data: comments, rejected diffs, CI failures, approval latency, rollback events, or post-merge incident data?
8. **Cost frontier:** Should routing optimize dollars per token, dollars per completed task, or dollars per verified business outcome?
9. **Open reproducibility:** When code/data/models are released, do independent runs reproduce the Claw and GUI gains under the same hardware and evaluator assumptions?
10. **Governance:** What retention policy keeps enough trajectory detail for learning while satisfying privacy, deletion, and compliance obligations?

## Sources

[^openforge-abs]: Xiao Yu, Baolin Peng, Ruize Xu, Hao Zou, Qianhui Wu, Hao Cheng, Wenlin Yao, Nikhil Singh, Zhou Yu, Jianfeng Gao. “OpenForgeRL: Train Harness-native Agents in Any Environment.” arXiv:2607.21557v1, submitted 23 July 2026. https://arxiv.org/abs/2607.21557v1

[^openforge-html]: arXiv HTML full text for “OpenForgeRL: Train Harness-native Agents in Any Environment.” https://arxiv.org/html/2607.21557v1

[^openforge-table1]: OpenForgeRL full text, Table 1: statistics of SFT and RL data used for Claw and GUI agent training. https://arxiv.org/html/2607.21557v1

[^openforge-table2]: OpenForgeRL full text, Table 2: Claw-agent performance on ClawEval, QwenClawBench, and MCPAtlas. https://arxiv.org/html/2607.21557v1

[^openforge-table3]: OpenForgeRL full text, Table 3: GUI-agent performance on OSWorld-Verified, Online-Mind2Web, and WebVoyager. https://arxiv.org/html/2607.21557v1

[^openforge-behavior]: OpenForgeRL full text, Section 5.3 “Capability Learned by RL,” including reported change in generic shell calls from 22.6% to 13.9% and definitions of self-verification, tool coverage, and step efficiency. https://arxiv.org/html/2607.21557v1

[^linear]: GitHub Changelog. “Copilot cloud agent for Linear is now generally available.” 23 July 2026. https://github.blog/changelog/2026-07-23-copilot-cloud-agent-for-linear-is-now-generally-available/

[^mobile-ci]: GitHub Changelog. “GitHub Mobile: Fix failing Actions checks with Copilot cloud agent.” 23 July 2026. https://github.blog/changelog/2026-07-23-github-mobile-fix-failing-actions-checks-with-copilot-cloud-agent/

[^mcp-stateless]: GitHub Changelog. “GitHub MCP Server supports the next MCP specification.” 23 July 2026. https://github.blog/changelog/2026-07-23-github-mcp-server-supports-the-next-mcp-specification/

[^timepns]: Hongnan Ma, Yiwei Shi, Mengyue Yang, Weiru Liu. “Beyond Sufficiency: Time Series Explanation with Counterfactual Necessity.” arXiv:2607.21573v1, submitted 23 July 2026. https://arxiv.org/abs/2607.21573v1

[^setup]: Bagmar & Saraf. “Setup Complete, Now You Are Compromised: Weaponizing Setup Instructions Against AI Coding Agents.” arXiv:2607.15143v1. https://arxiv.org/abs/2607.15143v1

[^researcharena]: “ResearchArena: Evaluating Sabotage and Monitoring in Automated AI R&D.” arXiv:2607.19321v1. https://arxiv.org/abs/2607.19321v1
