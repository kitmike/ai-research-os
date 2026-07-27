# The Regression Tax: Why Agent Skills Need a Loss Function

**Thesis —** *The Regression Tax* is important because it turns “skills make agents better” from an average-performance slogan into an accounting identity: every reusable procedure has both gross gains and newly broken tasks, and in the reported office-agent experiments regressions offset 59% of gross gains.[^tax]

## Abstract

Darshan Tank and Baran Nama’s 24 July 2026 paper, **“The Regression Tax: Decomposing Why Skills Help — and Hurt — LLM Agents,”** is a useful correction to the current enthusiasm for agent skills. The paper does not deny that procedural skills help. Across two office-automation benchmarks and three model/harness stacks, the authors observe 553 transitions where a skill library turns a previous failure into a pass. But they also observe 324 transitions in the other direction: tasks solved without skills that fail after skills are added. The resulting “regression tax” cancels 59% of the gross gains. The most interesting claim is mechanistic rather than numerical: failures often arise outside the procedural step skills are supposed to improve. A skill can alter behavior merely by its description being present in context (“osmosis”); it can displace grounding by making the agent follow a canned procedure instead of reading the right evidence; and it can displace verification by suppressing checks the agent would otherwise have performed. For product builders, this reframes skill libraries as mutable, safety-relevant infrastructure. A mature agent OS should report gross gains, regressions, presence-only effects, grounding failures, and verification failures—not just net pass rate.

## Table of contents

1. [Context: why skills looked like the next obvious layer](#context-why-skills-looked-like-the-next-obvious-layer)
2. [Core mechanism: gains, regressions, and the hidden accounting identity](#core-mechanism-gains-regressions-and-the-hidden-accounting-identity)
3. [Evidence: what the paper actually measured](#evidence-what-the-paper-actually-measured)
4. [Interpretation: skills are prompts with side effects](#interpretation-skills-are-prompts-with-side-effects)
5. [Where the result can be overread](#where-the-result-can-be-overread)
6. [Michael-specific implications](#michael-specific-implications)
7. [Concept map](#concept-map)
8. [Open questions and next experiments](#open-questions-and-next-experiments)
9. [Sources](#sources)

---

## Context: why skills looked like the next obvious layer

Agent engineering has converged on a practical pattern: do not ask the model to rediscover a workflow every time. Give it tools, memory, examples, and reusable procedural “skills.” In current agent products, a skill is usually a small bundle: a triggering description, natural-language instructions, perhaps helper code, and sometimes examples. It is attractive because it resembles how human organizations scale competence: write a runbook, add a checklist, record the local trick, then reuse it.

The *Regression Tax* paper studies exactly this layer. It defines an agent skill as “a reusable piece of procedural guidance” loaded into the agent’s context to control how the agent performs a task.[^paper] The authors situate the work amid systems that generate or optimize skills from traces—Trace2Skill, EvoSkill, SkillOpt, SkillOS, and skill-creator tools from Anthropic and OpenAI.[^anthropic-skill][^openai-skill] This is the natural next move after tool use and memory: once a model has solved or failed many tasks, distill trajectories into reusable procedures.

But there is a subtle mismatch between the rhetoric of “adding a skill” and the operational reality. A skill is not merely an optional subroutine. Its **description** may sit in the system prompt or skill-selection context at every step. Its **body** may load when invoked. Its instructions can compete with task-specific evidence. It is a local optimization inserted into a global policy.

That matters because enterprise agents are not evaluated only by their average improvement. A finance assistant that gets 20 new spreadsheet tasks right but breaks 10 previously reliable tasks has not simply improved by +10. It has changed its risk surface. The broken tasks may cluster in sensitive workflows; they may be hard to discover; they may happen because an instruction that was useful in one setting silently displaced grounding in another.

The paper’s central move is therefore modest but powerful: **pair each task under “no skill” and “with skill,” then count not only net pass-rate delta but the transitions in both directions.** This converts vague skill usefulness into a balance sheet.

## Core mechanism: gains, regressions, and the hidden accounting identity

For a fixed task set, each task under a skill library can fall into one of four paired outcomes:

- **Stable pass:** passed without skills and passed with skills.
- **Gain:** failed without skills, passed with skills.
- **Regression:** passed without skills, failed with skills.
- **Stable failure / residual failure:** failed in both conditions.

The paper emphasizes that the ordinary pass-rate difference is already equal to gains minus regressions, normalized by task count. But the aggregate hides how that net number was produced. Two skill libraries can have the same net improvement while one creates many gains and many regressions, and another creates fewer gains but preserves baseline competence. For deployment, those are different artifacts.

The authors then propose three candidate regression mechanisms:

1. **Skill-description osmosis.** The skill changes agent behavior simply by being present in context, even when its body is never invoked. This is the most conceptually unsettling mechanism because it means the “inactive” library is not inert.
2. **Grounding displacement.** The skill’s prescribed procedure overrides the agent’s interpretation of the actual input. The model follows the recipe but reads the wrong table, range, definition, year, or artifact.
3. **Verification displacement.** The procedure suppresses checks the agent would otherwise perform on its output. The skill turns an agent from “solve and verify” into “follow runbook and submit.”

The paper’s diagrammatic model is a three-stage task pipeline: **grounding → method/reasoning → verification**.[^paper] The authors argue that existing skills mostly target the middle stage, while many regressions and residual failures occur at the edges. This is a useful decomposition because many agent builders implicitly assume that failures are procedure failures: “the model did not know the right method.” In office work, and especially in finance work, failures are often evidence-selection failures or audit failures.

## Evidence: what the paper actually measured

The authors compare agents with and without skill libraries across **5,832 task-condition runs** on two office-automation benchmarks and three model/harness stacks.[^paper]

### Benchmarks

The two benchmarks are deliberately office-like rather than toy chat tasks:

- **OfficeQA-Pro**, a curated complex question-answering benchmark over U.S. Treasury financial documents. The paper describes tasks that require retrieving facts from long PDFs, reading text and tables, comparing values across reports or years, interpreting financial tables, computing sums or ratios, and combining information into a final answer. The authors note that the hard part is often grounding—finding the right table, vintage, and definition—not arithmetic.[^paper]
- **SpreadsheetBench**, a real-world spreadsheet-manipulation benchmark derived from Excel-forum problems, where the agent edits workbooks: formulas, filtering, filling cells, sorting, removing duplicates, and multi-sheet coordination.[^spreadsheetbench]

### Model/harness stacks

The three reported stacks are:

- OpenCode with MiniMax-M2.7.
- Codex with GPT-5.4-mini.
- Claude Code with Claude Sonnet 4.6.[^paper]

The skill libraries are produced from the same failure signals but by three different creators: an Anthropic-style measurement-driven creator, an OpenAI/Codex-style single-pass structural creator, and the authors’ harness-agnostic self-critique/reuse pipeline. The important experimental control is that, within a stack, the skill library changes while the task set and baseline are paired.

### The headline accounting

Across all eighteen library conditions, the authors report:

- **553 gain transitions**.
- **324 regression transitions**.
- **229 net positive transitions**.
- Regressions therefore offset **59%** of gross gains.[^tax]

The cancellation is not confined to one benchmark:

- On **OfficeQA-Pro**, libraries gained 122 tasks and broke 81; regressions cancelled **66%** of gross gains.
- On **SpreadsheetBench**, libraries gained 431 tasks and broke 243; regressions cancelled **56%** of gross gains.[^tax]

This is the core empirical fact. The skill libraries are not useless. They generate many gains. But a large fraction of the gross improvement is spent merely climbing back from newly introduced failures.

### The table-level picture

The paper’s Table 2 makes the point more vivid. Every library condition breaks at least some tasks that the baseline solved; the regression count ranges from **2 to 41**, and no condition has zero regressions.[^tax]

A few examples:

- On **OfficeQA-Pro**, Claude Code/Sonnet 4.6 with the Anthropic-created library rises from **72.3%** to **80.9%**, with 10 gains and 2 regressions, for a net of +8 tasks and a reported paired delta of +8.5 percentage points with p = 0.039.[^table2]
- On the same stack and benchmark, another library may show similar gross gains but more regressions. The authors highlight that for Claude Code/Sonnet 4.6 and OfficeQA-Pro, the three libraries gain 10, 11, and 12 tasks but regress 2, 4, and 7 respectively; ranking by gross gains differs from ranking by net effect.[^table2]
- On **SpreadsheetBench**, Claude Code/Sonnet 4.6 improves strongly across all three libraries: the “Ours” library rises from **70.2%** to **82.1%**, with 66 gains, 19 regressions, and a net of +47 tasks.[^table2]
- But on SpreadsheetBench, OpenCode/MiniMax-M2.7 with the OpenAI-style library gains 45 tasks while breaking 41; Codex/GPT-5.4-mini with the OpenAI-style library gains 30 while breaking 27.[^table2]

This is why net pass rate alone is insufficient. A library that breaks almost as many tasks as it fixes is operationally different from one that preserves prior competence.

### Mechanism coding

The most useful secondary result is the mechanism taxonomy.

For the **81 OfficeQA-Pro regressions**, Table 3 codes:

- Grounding displacement: **59 / 81 = 72.8%**.
- Osmosis: **14 / 81 = 17.3%**.
- Grounding + verification: **3 / 81 = 3.7%**.
- Other: **5 / 81 = 6.2%**.[^table3]

For the **243 SpreadsheetBench cell-level regressions**, Table 4 codes:

- Osmosis: **70 / 243 = 28.8%**.
- Body engaged: **46 / 243 = 18.9%**.
- Grader artifact: **32 / 243 = 13.2%**.
- Other: **95 / 243 = 39.1%**.[^table4]

The asymmetry matters. OfficeQA-Pro regressions are mostly grounding displacement. SpreadsheetBench has more ambiguous cells and grader artifacts. The authors are appropriately careful: verification displacement is harder to isolate in some settings, and SpreadsheetBench cells do not always permit a clean separation of mechanisms.

The paper also reports correcting evaluation artifacts in SpreadsheetBench: **226 treatment task-conditions** were re-graded after original spreadsheet grader failures, and Table 5 shows corrected pass rates materially above raw rates for several conditions.[^table5] This is an understated but important reminder that agent evaluation is only as reliable as the harness and grader.

## Interpretation: skills are prompts with side effects

The paper’s most durable contribution is not “skills are bad.” It is: **skills are interventions on a policy, and interventions need adverse-event reporting.**

The standard narrative of agent skills has borrowed from human training: when an agent fails, write a skill; when it sees a similar task, retrieve the skill; the agent should improve. But a skill is also context. And context in LLMs is not a passive database. It changes attention, priors, style, and action selection. “Skill-description osmosis” is a memorable name for this general fact: a skill library can perturb behavior before explicit invocation.

This aligns with a broader lesson from long-context and irrelevant-context work: extra text is not free. The paper itself references prior results on distractors and “lost in the middle.”[^lost-middle] In an agent stack, the problem is harsher because the context is not merely a passage to read; it is part of an action policy.

The right analogy may be medicine rather than documentation. A procedural skill is a treatment. Evaluation should report:

- **Efficacy:** how many failures become passes.
- **Adverse events:** how many passes become failures.
- **Contraindications:** which task types, artifacts, or contexts regress.
- **Mechanism:** whether harm comes from presence, invocation, grounding displacement, or verification displacement.
- **Monitoring:** how to detect regressions in production.

This also changes how one should design an agent OS. A skill library should not be a folder of helpful incantations. It should be a versioned, tested, observable subsystem with rollout controls. Adding a skill should look less like editing a prompt and more like deploying code.

A practical architecture follows:

1. **Paired regression harness.** Every proposed skill is evaluated against a fixed task battery with no-skill vs with-skill pairing.
2. **Gross-gain / regression reporting.** Dashboards show gains, regressions, stable passes, and stable failures, not only average pass rate.
3. **Presence-only ablation.** Test skill descriptions in context with bodies unavailable, then bodies invoked, to separate osmosis from procedural value.
4. **Grounding probes.** Add controlled tasks where the tempting procedural shortcut points to the wrong artifact, table, range, vintage, or definition.
5. **Verification probes.** Add tasks where a plausible answer must be rejected after checking.
6. **Skill canaries.** In production, route a small percentage of eligible tasks through new skill versions and watch for regressions on known-stable workflows.
7. **Skill rollback and quarantine.** Treat high-regression skills as deployable artifacts that can be disabled by task class.

If this sounds like software release engineering, that is the point. Skill libraries are becoming part of the runtime.

## Where the result can be overread

There are several caveats.

First, the paper studies two office-automation benchmarks. They are relevant to enterprise agents, but they are not all agents. Web navigation, coding, shell automation, customer support, and scientific agents may exhibit different regression modes.

Second, the reported model names and skill-creator setups are part of a specific 2026 experimental environment. The qualitative mechanism may generalize better than the exact numbers. I would not assume that “59% regression tax” is a universal constant.

Third, the authors’ mechanism coding relies on trace analysis and criteria. It is much better than hand-waving, but mechanism attribution is still harder than paired outcome counting. The paper is careful here: it explicitly says verification displacement is hard to isolate as a regression in OfficeQA-Pro and cannot be cleanly separated in the SpreadsheetBench cells.[^conclusion]

Fourth, some regressions may be evaluation noise. The authors partly address this through re-grading and by identifying grader artifacts, but spreadsheet and document QA grading remains difficult. A deployment system should expect both agent regressions and harness regressions.

Fifth, the fact that best-performing libraries may regress less does not mean one should avoid ambitious skill creation. It means the optimization target should include harm. A library can be aggressive if it is also well-scoped and monitored.

What would change my mind? I would update away from the paper’s practical importance if broad replications across coding, browser, research, and customer-support agents found that regressions are rare once skills are retrieved by a sufficiently good router; or if presence-only ablations showed osmosis disappearing under better context isolation. Conversely, I would update toward stronger concern if production traces show that regressions cluster in high-value workflows, or if skill libraries accumulate interaction effects over time.

## Michael-specific implications

### Agentic company OS

Treat skills as **versioned operational modules**, not prompt snippets. An agentic company OS should track:

- skill version;
- author / generator;
- trigger description;
- body hash;
- tasks improved;
- tasks regressed;
- presence-only effects;
- grounding failure modes;
- verification failure modes;
- rollout status;
- rollback owner.

The OS-level feature is not “agents can learn skills.” The feature is **safe skill lifecycle management**: propose, test, stage, canary, monitor, rollback.

### AI/product strategy

For product design, this paper suggests a differentiator: make reliability accounting visible. Most agent products will advertise skill marketplaces, memory, toolkits, and workflow templates. A more credible product shows a **regression ledger** beside every template: “this skill fixed 42 tasks, broke 5, mostly on spreadsheet range grounding; last tested against benchmark X.”

This is also a trust UX opportunity. Enterprise buyers do not merely want higher demos. They want to know what breaks when the system gets “smarter.”

### Finance/trading research

The finance relevance is direct because OfficeQA-Pro uses U.S. Treasury financial documents, and the authors say the hard part is often grounding: finding the right table, vintage, and definition. This maps to trading research and fundamental finance workflows. The danger is not only wrong arithmetic; it is using the wrong filing, restatement, contract, time window, or factor definition.

For trading agents, a “skill” that teaches a procedure—calculate factor exposure, normalize earnings, compare balance-sheet items—can create silent regressions if it displaces evidence selection or verification. A no-trade or no-update result should be treated as a valid outcome when grounding is uncertain.

### Career / opportunities

There is a growing role for **agent reliability engineering**: building eval harnesses, regression ledgers, skill rollout systems, trace taxonomies, and observability for tool-using LLMs. The opportunity is not just model prompting. It is building the deployment discipline around adaptive agent systems.

## Concept map

- **Agent skill → procedural guidance:** a reusable instruction bundle loaded into an agent context.
- **Skill description → presence channel:** the trigger/description can affect behavior even without body invocation.
- **Skill body → invocation channel:** the procedure itself may help or harm when called.
- **Gross gain → newly solved tasks:** failures without skills that pass with skills.
- **Regression → newly broken tasks:** passes without skills that fail with skills.
- **Regression tax → cancelled gross improvement:** 324 regressions offsetting 553 gains in the reported experiments.
- **Grounding displacement → wrong evidence:** a procedure overrides reading the actual input.
- **Verification displacement → suppressed checks:** a procedure short-circuits output validation.
- **Residual failure → unchanged failure:** task fails both with and without skills; often also grounding/verification related.
- **Skill lifecycle management → production control:** version, test, canary, monitor, and rollback skills like code.
- **Regression ledger → product trust surface:** expose adverse effects alongside aggregate improvement.

## Open questions and next experiments

1. **Cross-domain replication.** Does the regression tax remain large in coding agents, browser agents, research agents, and customer-support agents?
2. **Skill isolation.** Can context isolation or stricter retrieval prevent skill-description osmosis without losing recall?
3. **Router interaction.** Would task-level routing, such as the TRACE-Router idea of pinning a model/backend for a long-horizon task and updating from terminal reward, reduce or amplify skill regressions?[^trace-router]
4. **Skill composition.** Do regressions grow superlinearly as libraries accumulate many skills, or do better retrieval policies keep them bounded?
5. **Adverse-event taxonomy.** Can grounding and verification displacement be detected automatically from traces?
6. **Finance eval.** Build a finance-specific paired benchmark: no-skill vs with-skill across filings, spreadsheets, macro releases, and trading-research notebooks; report gross gains, regressions, no-trade correctness, and audit-trail quality.
7. **Production canaries.** Test whether skill canarying catches regressions before broad rollout in a real agent workflow.
8. **Human-in-the-loop repair.** When a skill regresses a task, is it better to edit the skill, narrow the trigger, add a verification guard, or split the skill into grounding/method/check modules?

## Sources

[^paper]: Darshan Tank and Baran Nama, “The Regression Tax: Decomposing Why Skills Help — and Hurt — LLM Agents,” arXiv:2607.22520v1, submitted 24 July 2026. Abstract and HTML read from arXiv. https://arxiv.org/abs/2607.22520v1 and https://arxiv.org/html/2607.22520v1

[^tax]: Ibid., Abstract, Introduction, and Section 4.1. The paper reports 5,832 task-condition runs; 553 gain transitions; 324 regression transitions; 59% cancellation of gross gains; OfficeQA-Pro cancellation of 66%; SpreadsheetBench cancellation of 56%.

[^table2]: Ibid., Table 2 and Section 4, reporting paired pass rates, gains, regressions, net effects, confidence intervals, and McNemar tests for OfficeQA-Pro and SpreadsheetBench.

[^table3]: Ibid., Table 3, “Mechanism” counts for OfficeQA-Pro regressions: grounding displacement 59, osmosis 14, grounding + verification 3, other 5, total 81.

[^table4]: Ibid., Table 4, SpreadsheetBench cell-regression categories: osmosis 70, body engaged 46, grader artifact 32, other 95, total 243.

[^table5]: Ibid., Table 5 and paper contributions, reporting 226 re-graded treatment task-conditions after spreadsheet grader failures.

[^conclusion]: Ibid., Conclusion, where the authors caution that verification displacement is rare/hard to isolate on OfficeQA-Pro and cannot be cleanly separated from other mechanisms in SpreadsheetBench cells.

[^anthropic-skill]: Anthropic skill-creator repository referenced by the paper: https://github.com/anthropics/skills/tree/main/skills/skill-creator

[^openai-skill]: OpenAI skill-creator repository referenced by the paper: https://github.com/openai/skills/tree/main/skills/.system/skill-creator

[^spreadsheetbench]: Zeyao Ma et al., “SpreadsheetBench: Towards Challenging Real World Spreadsheet Manipulation,” NeurIPS 2024 Datasets and Benchmarks Track, referenced by *The Regression Tax*; benchmark context quoted from the arXiv HTML. The arXiv paper’s source page is https://arxiv.org/abs/2607.22520v1

[^lost-middle]: Nelson F. Liu et al., “Lost in the Middle: How Language Models Use Long Contexts,” arXiv:2307.03172, cited in *The Regression Tax* as related long-context evidence. https://arxiv.org/abs/2307.03172

[^trace-router]: Ritik Raj et al., “TRACE-Router: Task-Consistent and Adaptive Online Routing for Agentic AI,” arXiv:2607.22465v1, submitted 24 July 2026. The abstract reports task-level routing for long-horizon agentic workflows using delayed terminal reward and notes improvements on τ²-Bench and Terminal-Bench. https://arxiv.org/abs/2607.22465v1
