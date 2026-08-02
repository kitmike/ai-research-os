# More Tasks Per Repository: Change2Task and the Industrialization of Coding-Agent Evaluation

**Thesis:** Change2Task is important not because it is another coding benchmark, but because it reframes repository history as reusable agent infrastructure: a maintained codebase can be converted into many provenance-linked, executable tasks only if the task-construction pipeline itself has lifecycle checks, fidelity checks, and outcome-equivalence tests.

## Abstract

Coding agents are increasingly limited less by chat-model intelligence in the abstract than by the supply of realistic, executable, non-stale repository tasks on which they can be trained, benchmarked, and continuously regression-tested. **Change2Task: From Repository Changes to Executable Coding Agent Tasks and Environments** attacks this bottleneck directly. Starting from merged pull requests, it reconstructs developer-grounded tasks on healthy descendant revisions of the same repository through three escalating routes: Patch Reversal, Code Mapping, and Agent Reconstruction. The paper reports 900 finalized paired tasks from 1,130 eligible changes, 500/621 Bug Fix recoveries versus 387/621 for a matched SWE-smith PR Mirror-style baseline, 0.894 task-weighted source-change-profile fidelity, balanced aggregate agent outcomes across historical and reconstructed branches, and substantial environment reuse: 388 modern bases instead of 900 per-task bases, reducing setup time by 58.4% and retained storage by 71.2%.[^change2task]

The deeper lesson is that evaluation data is now a capital asset. A coding-agent company should not merely collect tasks; it should operate a task foundry with provenance, executable oracles, scope guards, modern-base reuse, and drift audits. The caveat is equally important: Change2Task only works where historical intent, modern behavior, and executable checks can be made legible. It is infrastructure for verified software work, not a magic generator of arbitrary product judgment.

## Table of Contents

1. [Context: the data factory behind coding agents](#context-the-data-factory-behind-coding-agents)
2. [Core mechanism: turning a merged PR into a modern task](#core-mechanism-turning-a-merged-pr-into-a-modern-task)
3. [Evidence: what the paper actually shows](#evidence-what-the-paper-actually-shows)
4. [Interpretation: the task foundry thesis](#interpretation-the-task-foundry-thesis)
5. [Where people may overread it](#where-people-may-overread-it)
6. [What would change my mind](#what-would-change-my-mind)
7. [Michael-specific implications](#michael-specific-implications)
8. [Concept map](#concept-map)
9. [Open questions and next experiments](#open-questions-and-next-experiments)
10. [Sources](#sources)

## Context: the data factory behind coding agents

The public story of coding agents is usually told as a leaderboard story: model A beats model B on SWE-bench; a new agent shell improves tool use; a frontier model closes more GitHub issues. But the more durable bottleneck is the **executable task supply chain**. A useful coding-agent task is not a prompt. It is a bundle: repository state, dependencies, tests or oracles, tool permissions, time budget, hidden checks, and a specification whose success condition survives contact with a real development environment.

Change2Task opens with this systems framing. The authors note that agent training, benchmarking, and continuous evaluation all need a continuing supply of executable data. They cite the cost and scale of existing environment efforts: daVinci-Env is described as reporting 45,320 Docker environments across more than 12.8K repositories and roughly $891K in construction cost, while SWE-Universe is described as producing 807,693 verifiable environments using specialized distributed infrastructure.[^change2task-html] The exact external systems should be separately read before operational adoption, but Change2Task’s own point is modest and convincing: if environments are expensive, a prepared runnable repository should support more than one task.

This is the same lesson that OSReward made visible yesterday from the evaluator side: agents need evidence lanes and judges, not just actors. Change2Task makes the complementary point from the data side: the unit of progress is a **verified trajectory environment**, and the bottleneck is manufacturing enough of them without losing provenance.

A second paper from the same arXiv batch, PAIChecker, sharpens the stakes. It studies SWE-bench Verified instances and reports that 13.6% exhibit PR–issue misalignment across five patterns and eleven fine-grained scenarios.[^paichecker] That is, even highly used “realistic” coding benchmarks can contain task-specification defects. If this result holds up, benchmark construction is not clerical. It is a research problem and a governance problem.

## Core mechanism: turning a merged PR into a modern task

Change2Task starts from a historical merged PR and a healthy descendant revision in the same repository. The historical PR supplies developer evidence: description, implementation patch, and executable checks. The modern descendant supplies a runnable base. The system then constructs a task state and a restoration patch, trying to preserve the maintenance intent while moving it onto current code.

The paper’s lifecycle notation is compact: a historical pre-PR version is transformed by the source patch into a post-PR version; the modern healthy base is transformed by a task patch into a task state; a restoration patch should return it to a healthy restored state.[^change2task-html] In less formal terms: “make today’s repository contain the old problem again, but in a way that today’s tests and code structure recognize.”

The three construction routes are the key engineering idea:

1. **Patch Reversal.** If the historical patch still fits the modern code, reverse it directly. This is the cleanest route and preserves a close textual relationship to the developer change.
2. **Code Mapping.** If direct reversal fails but a unique source block correspondence remains, map the historical post-change block to its modern location and replace it with the historical pre-change form, with conservative normalization and parsing checks.
3. **Agent Reconstruction.** If repository evolution has broken textual correspondence but the behavior is still present, a bounded construction agent receives PR evidence, modern context, task specification, and structured failure feedback. It proposes scoped candidate patches, filtered through apply, syntax, scope, fidelity, and lifecycle gates. The loop allows at most four attempts in the reported setup.[^change2task-html]

The important detail is not that an LLM is used at Level 3. The important detail is that the LLM is not trusted as the source of truth. Candidate tasks must pass a lifecycle: on the healthy base, target and regression checks pass; on the task state, target checks expose the problem while regression checks continue to pass; after restoration, both target and regression checks pass again. Scope gates prevent protected checks or metadata from manufacturing validity. Fidelity gates compare the historical source patch and modern restoration across files, hunks, changed lines, symbols, target checks, and regression checks; the paper reports weights and thresholds in Appendix C.[^change2task-html]

This makes Change2Task less like “generate benchmark questions” and more like a compiler: source history goes in, executable task artifacts come out, and the compiler has type checks.

## Evidence: what the paper actually shows

The paper evaluates five task families: Bug Fix, Feature Addition, Test Generation, API Migration, and Security Repair. The construction study begins with 1,130 construction-eligible source changes: cases where source PR evidence, executable checks, and same-repository base prerequisites are available. It yields 900 paired sets: 500 Bug Fix and 100 each for Feature Addition, Test Generation, API Migration, and Security Repair.[^change2task-html]

The headline construction results are strong but should be read as **conditional on eligibility**:

- **Overall recovery:** 900 of 1,130 eligible changes, or 79.6%.
- **Family range:** reported recovery ranges from 76.3% for API Migration to 82.0% for Feature Addition.
- **Construction route contribution:** 95 tasks from Patch Reversal, 190 from Code Mapping, and 615 from Agent Reconstruction, corresponding to 10.6%, 21.1%, and 68.3% of finalized tasks.
- **Matched Bug Fix comparison:** on 621 Bug Fix candidates, Direct Reversal recovers 81/621 (13.0%), SWE-smith PR Mirror recovers 387/621 (62.3%), and Change2Task recovers 500/621 (80.5%). The paper describes this as 113 additional verified tasks, a 29.2% relative and 18.2-point absolute gain over the PR Mirror baseline.[^change2task-html]

The fidelity and outcome-equivalence results are more interesting than the raw count. The paper reports a task-weighted source-change-profile fidelity of 0.894, with family means from 0.825 to 0.925. It also uses independent model review: Kimi K3 and DeepSeek V4 Pro review 912 anonymized historical/modern pairs, directly accept 834, and after manual adjudication the retained corpus is 900; 92.7% of the final corpus is directly accepted by both judges.[^change2task-html]

The paired agent-outcome test is the strongest evidence that the reconstructed tasks preserve evaluation signal. Across 3,600 matched agent-task pairs, each branch contains 1,478 solved outcomes, or 41.1%. Discordance is exactly balanced: 186 solved only on the Original Branch and 186 solved only on the Change2Task Branch. Aggregate agreement is 89.7%; Cohen’s κ is 0.787; positive agreement is 87.4%; solved-set Jaccard overlap is 77.6%; the paired solve-rate difference is 0.0 points with a 95% interval of [-1.1, 1.1], and exact McNemar p=1.0.[^change2task-html]

For infrastructure, the paper compares one base per task with shared modern bases. Change2Task prepares 388 healthy modern bases for 900 tasks, not 900 separate bases. Reported effects: 56.9% fewer bases, 2.32 tasks per base, total setup time 3,240h → 1,349h, setup time per task 3.60h → 1.50h, retained storage 5,580GB → 1,607GB, storage per task 6.20GB → 1.79GB. The paper also reports a smaller but still material end-to-end expenditure reduction, $1,917 → $1,710, because automation and Agent Reconstruction cost offset some environment savings.[^change2task-html]

These numbers are not universal constants. They are measurements for this task mix, repository distribution, hardware/accounting setup, construction agent, and validation protocol. But they are enough to establish the mechanism: **environment reuse is real, and task reconstruction quality can be audited.**

## Interpretation: the task foundry thesis

The naive view is that benchmarks are datasets. The better view is that benchmarks are **factories**. A coding-agent organization needs a pipeline that continuously turns code history, product tickets, failing tests, customer incidents, migrations, security advisories, and internal refactors into validated tasks. The pipeline must preserve provenance and produce comparable outcomes across model releases.

Change2Task shows one concrete factory design:

- a historical evidence extractor;
- a modern-base resolver;
- escalating task-state construction routes;
- lifecycle validation across healthy/task/restored states;
- source-fidelity scoring;
- independent semantic auditing;
- matched outcome-equivalence evaluation;
- cost accounting for environment reuse.

This is a useful architecture because it separates three things people often collapse:

1. **Intent provenance:** What real developer change is this task grounded in?
2. **Executable validity:** Does the task state expose the intended condition under a verifier while preserving surrounding behavior?
3. **Evaluation equivalence:** Do agents behave similarly on the reconstructed task and its historical anchor?

A benchmark without (1) risks synthetic irrelevance. A benchmark without (2) risks false positives, flaky failures, and test hacking. A benchmark without (3) may silently change what it measures as it modernizes.

The long-horizon implication is that coding-agent advantage may come less from a single giant leaderboard and more from private task-compounding: every merged PR becomes a future eval; every eval is refreshed onto current code; every model release is tested against a moving but provenance-linked archive. This is especially important for companies building agents inside private monorepos where public SWE-bench performance is only weakly diagnostic.

## Where people may overread it

First, Change2Task does not show that all software work can be converted into executable tasks. The paper explicitly depends on a historical PR with identifiable intent, a healthy descendant that still hosts the behavior, an executable oracle, and bounded edit policy. Product judgment, ambiguous design, multi-team migrations, and “make it better” tasks remain harder.

Second, the construction funnel starts from **eligible** changes. The 79.6% recovery rate is not a fraction of all real PRs. It is a fraction of changes already satisfying source-evidence, executable-check, and same-repository prerequisites. For an arbitrary startup codebase with sparse tests, ad hoc infrastructure, and undocumented product behavior, the first bottleneck may be testability, not reconstruction.

Third, the paper uses strong models as both construction and evaluation agents. Agent Reconstruction uses Claude Code with Opus 4.8; evaluation uses Codex CLI with GPT-5.5, Claude Code Sonnet 5, Gemini CLI with Gemini 3.1 Pro, and GitHub Copilot with GPT-5.6 Terra.[^change2task-html] That makes the results highly relevant to frontier-agent workflows, but it also means a cheaper local task foundry might have different recovery/cost tradeoffs.

Fourth, semantic audits involving model judges need caution after OSReward’s warning about judge failure modes. Change2Task mitigates this with anonymization, two independent judges, and manual adjudication, but future deployments should add human sampling, deterministic checks where possible, and adversarial false-validity probes.

Finally, the matched outcome result says reconstructed tasks preserve aggregate comparative signal in this study. It does not prove every task is equivalent in every future model regime. If a future agent exploits modernized code structure or hidden test patterns differently, equivalence can drift.

## What would change my mind

I would become more skeptical if follow-up work found that reconstructed tasks have high surface fidelity but systematically different failure modes under newer agents; if model-constructed Level 3 tasks were especially vulnerable to solver overfitting; if private-repo deployments showed much lower eligibility due to weak tests and environment rot; or if human audits found many cases where the restored modern behavior preserved tests but not product semantics.

I would become more bullish if Change2Task-like pipelines worked inside large private monorepos, across forks and successor projects, with human-audited semantic equivalence; if task-foundry outputs predicted real engineering throughput better than public benchmarks; and if environment reuse compounded across dozens of task variants per maintained base rather than 2.32 in the reported corpus.

## Michael-specific implications

### Agentic company OS

Treat every internal workflow as a future eval candidate. For coding, the company OS should archive PR descriptions, diffs, failing/passing tests, review comments, rollback events, CI logs, and post-merge incidents in a schema that can later produce executable tasks. The operational primitive is not “a prompt”; it is a **task packet**: provenance, base revision, task state, restoration patch, oracle, allowed scope, hidden checks, and evaluation trace.

### AI/product strategy

A productized coding-agent platform should sell not only the agent but the foundry: “we convert your repository history into a private regression benchmark and continuously test model upgrades against it.” This is a stronger enterprise value proposition than generic leaderboard claims because it answers the buyer’s real question: will the agent work on *our* code, *our* migrations, and *our* failure modes?

### Finance/trading research

The analogy in finance is direct. A trading-research agent should not be judged only on generated reports. Historical market events, model promotions, stale-data bugs, risk-limit breaches, execution slippage, and post-trade reviews can become provenance-linked eval tasks. But the oracle problem is harder: “profitable” is not the same as “correct,” and leakage can masquerade as skill. Finance needs Change2Task’s discipline plus stronger time-indexing, no-lookahead guards, and abstention/no-trade outcomes.

### Career/opportunities

“Agent evaluation engineer” is becoming too narrow a title. The opportunity is **agent task-foundry engineering**: build pipelines that mine history, reconstruct tasks, verify outcomes, audit semantic equivalence, measure cost per verified task, and maintain benchmark drift dashboards. This sits between ML evals, developer infrastructure, security, and product analytics.

## Concept map

- **Executable task supply** → limits coding-agent training, benchmarking, and continuous evaluation.
- **Repository history** → supplies real developer intent, patches, tests, and maintenance provenance.
- **Healthy modern base** → amortizes expensive environment setup across multiple task variants.
- **Patch Reversal** → high-fidelity but low-coverage reconstruction route.
- **Code Mapping** → handles local context drift when direct reversal fails.
- **Agent Reconstruction** → increases coverage when behavior remains but textual correspondence breaks.
- **Lifecycle validation** → healthy/task/restored state checks prevent task artifacts from being mere plausible diffs.
- **Fidelity gate** → compares historical and modern changes across implementation and verification surfaces.
- **Outcome-equivalence audit** → tests whether reconstructed tasks preserve comparative agent signal.
- **Task foundry** → an organizational system that continuously converts historical work into verified evals.
- **Benchmark integrity** → threatened by PR–issue misalignment, stale environments, weak oracles, and judge bias.

## Open questions and next experiments

1. Can Change2Task be replicated in a private monorepo with weak tests, internal services, feature flags, and non-public dependencies?
2. How many task variants per healthy base are achievable in high-reuse repositories before tasks become redundant?
3. Do reconstructed tasks predict future engineering-agent performance better than public SWE-bench-family benchmarks?
4. Which Level 3 reconstruction errors survive lifecycle/fidelity gates and only appear under human semantic audit?
5. Can deterministic program analysis reduce dependence on model judges for semantic alignment?
6. Does training on Change2Task-generated tasks create agents that overfit reconstruction artifacts?
7. What is the right unit of economics: dollars per task, dollars per verified solved task, dollars per avoided regression, or dollars per production PR merged?
8. How should a finance/trading task foundry encode time, leakage prevention, risk limits, and no-trade decisions?

## Sources

[^change2task]: Haomin Qi et al., **“Change2Task: From Repository Changes to Executable Coding Agent Tasks and Environments,”** arXiv:2607.28591v1, submitted 2026-07-30. <https://arxiv.org/abs/2607.28591v1>

[^change2task-html]: arXiv HTML full paper, **Change2Task: From Repository Changes to Executable Coding Agent Tasks and Environments.** <https://arxiv.org/html/2607.28591v1>

[^paichecker]: **“PAIChecker: Uncovering and Checking PR-Issue Misalignment in SWE-Bench-Like Benchmarks,”** arXiv:2607.28587v1, submitted 2026-07-30. <https://arxiv.org/abs/2607.28587v1>

Additional primary/source URLs used for orientation:

- Change2Task DOI landing page: <https://doi.org/10.48550/arXiv.2607.28591>
- PAIChecker HTML: <https://arxiv.org/html/2607.28587v1>
- Rethinking Inference-Time Scaling in Local Computer-Use Agents: <https://arxiv.org/abs/2607.28573v1>
- OSReward: Instituting Standardized Evaluation for Cross-Platform Computer-Use Reward Models: <https://arxiv.org/abs/2607.28609v1>
