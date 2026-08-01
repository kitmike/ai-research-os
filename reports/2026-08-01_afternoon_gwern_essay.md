# The Judge Is Now the Bottleneck

**Thesis:** OSReward is the week’s most important agent paper because it shows that computer-use agents cannot be scaled by rollouts alone: once agents act in browsers, desktops, terminals, and phones, the scarce object is a cheap, calibrated, failure-sensitive judge of trajectories.

## Abstract

Computer-use agents are increasingly evaluated, trained, and marketed by the trajectories they complete: task instruction, screenshots, thoughts, actions, and final state. But trajectory completion is not self-evident. A browser or desktop agent can look competent, narrate success, and still leave the environment in the wrong state. The OSReward paper attacks this missing layer directly. It builds a cross-platform benchmark of 1,019 human-labeled computer-use trajectories, a 284-item hard subset, and a 440-item multi-axis quality subset; evaluates 27 VLM judges; and finds a systematic leniency bias in which many judges over-accept failures as successes. The best closed judges reach about 89–90% accuracy on the full set but collapse to about 67–70% on OSReward-Hard, while cheap judges can fall near or below usefulness exactly where hard failures matter. The proposed OS-Shepherd models then show a plausible path out: train a self-hostable reward model on a high-agreement, reasoning-annotated 100K-scale corpus, improving hard-failure recall at far lower cost than frontier API judges. The result is not a proof that OS-Shepherd is the final verifier. It is evidence for a broader architecture: production agents need an explicit actor–judge–deployment-gate stack, and the reward model should be treated as infrastructure, not as an afterthought.

## Table of Contents

1. [Context: why trajectory judging matters](#context-why-trajectory-judging-matters)
2. [The core mechanism: OSReward as a judge benchmark](#the-core-mechanism-osreward-as-a-judge-benchmark)
3. [Evidence: what the paper actually reports](#evidence-what-the-paper-actually-reports)
4. [Interpretation: the false-success economy](#interpretation-the-false-success-economy)
5. [Caveats and what would change my mind](#caveats-and-what-would-change-my-mind)
6. [Michael-specific implications](#michael-specific-implications)
7. [Concept map](#concept-map)
8. [Open questions and next experiments](#open-questions-and-next-experiments)
9. [Sources](#sources)

## Context: why trajectory judging matters

The modern agent stack has quietly acquired a second model. The first model acts: it clicks, types, calls tools, reads files, edits code, and narrates a plan. The second model judges: it reads the trajectory and says whether the actor actually achieved the user’s goal. This judge is increasingly used for three different jobs that are easy to conflate:

1. **Evaluation:** scoring agents on benchmarks or private regression suites.
2. **Data curation:** selecting successful and failed trajectories for supervised or preference training.
3. **Reinforcement learning:** providing the reward signal during rollout-heavy optimization.

For text-only problems, judging often reduces to exact match, unit tests, or an LLM-as-judge rubric. For computer-use agents (CUAs), the object is messier. The relevant evidence may be scattered through screenshots, typed strings, filesystem state, browser state, GUI interactions, and the agent’s own reasoning. Worse, the final state may look plausible while the task remains incomplete. A shopping-cart task, spreadsheet edit, desktop file conversion, or mobile app update can fail in small environmental ways that the actor itself may not notice.

This is why OSReward matters. The paper is not merely “another benchmark.” It asks whether the judge model—the thing we increasingly use to certify agents—is reliable enough to become the reward channel for agents that operate computers. The answer is: not yet, and the failure mode is directionally dangerous. Judges are often **lenient**: they misclassify failed trajectories as successes.[^osreward]

That asymmetry matters more than raw accuracy. If a judge is strict, it may under-credit useful work and slow training. If it is lenient, it can teach agents that confident near-misses are acceptable. In deployed products, leniency becomes false autonomy: the dashboard says “done,” the trace contains a polished rationale, but the state is wrong.

## The core mechanism: OSReward as a judge benchmark

OSReward’s methodological move is to evaluate the evaluator. Instead of asking “which agent completed the task?”, it asks “which VLM judge can correctly label whether a trajectory completed the task?”

The paper’s data pipeline has four layers.

First, the authors build realistic cross-platform environments rather than relying only on existing benchmark rollouts. Their infrastructure spans web, Windows, Ubuntu, and Android/mobile settings, with initialized profiles, real files, seeded application state, distractors, live websites, and long trajectories. This matters because a judge trained only on clean toy rollouts may learn the surface style of a benchmark, not the evidence required to distinguish success from failure.

Second, human annotators write grounded instructions. The paper reports roughly 1,500 candidate instructions, of which about 800 survive peer screening into the next stage. The screening is important: if the task itself is ambiguous or impossible, a judge benchmark becomes a benchmark of task-writing noise.

Third, each surviving instruction is executed by agents driven by mainstream model families—Claude, Gemini, Kimi, and Qwen are named in the paper’s trajectory-collection description—so the resulting data contains multiple action idioms and failure styles. This reduces the risk that a judge is merely recognizing one actor’s tone or harness format.

Fourth, the benchmark labels are human. Every pre-filtered trajectory is independently labeled by three annotators who inspect the full multimodal trajectory; split cases go to senior meta-review rather than simple majority vote. The annotation rule is intentionally strict: if the agent did not obtain or verify the answer through the environment, the trajectory is a failure even if the final answer happens to be right.

The resulting benchmark has three views:

- **OSReward:** 1,019 trajectories across four platforms, with about 43% successes and 57% failures.
- **OSReward-Hard:** 284 difficult trajectories, selected largely from cases that initially divided annotators and re-verified with extra care; the subset is failure-heavy, roughly 30/70 success/fail, to expose false successes.
- **OSReward-Multi:** 440 successful trajectories with extra human labels for alignment and efficiency, making it possible to grade not only whether the agent succeeded but how well it succeeded.

This design choice is the paper’s main virtue. It treats “success” as a stateful, provenance-sensitive property of a trajectory, not as a string the agent can assert.

## Evidence: what the paper actually reports

### 1. Frontier judges are good on the full set, brittle on hard cases

The headline table evaluates 27 VLM judges. On full OSReward, the top closed judges are close together: Claude-Opus-4-8 is reported at 89.7% accuracy, GPT-5.5 at 89.5%, and Claude-Opus-4-6 at 89.5%. Balanced accuracy shifts the ordering slightly, which the authors use to argue for a “top tier” rather than a single best judge.[^table1]

The hard set is where the story changes. On OSReward-Hard, Claude-Opus-4-8 is reported at 69.7% accuracy, GPT-5.5 at 67.3%, and Claude-Opus-4-6 at 67.3%. This is not a small degradation; it says that the trajectories most likely to fool people and models remain far from solved. The hard subset is also the right place to look if the intended use is reward modeling or deployment gating, because easy successes do not define the safety margin.

### 2. The dominant bias is leniency: failed runs are accepted

The table separates success recall (`sRec`) and failure recall (`fRec`). Many judges sit in a lenient region: high success recall and much lower failure recall. For example, Gemini-3.5-Flash has 87.8% full-set accuracy but success recall of 95.7% versus failure recall of 81.8%; on OSReward-Hard, that asymmetry widens to 81.4% success recall versus 50.0% failure recall. Claude-Sonnet-4-6 has full-set success recall of 97.5% and failure recall of 80.3%; on the hard set, 90.7% success recall and 45.5% failure recall.

The small open VLMs can be more extreme. Qwen3-VL-8B is reported at 99.8% success recall but 59.9% failure recall on full OSReward, and on OSReward-Hard at 100.0% success recall but only 8.2% failure recall. That is essentially an “everything looks successful” judge on the hard subset.

This is the central empirical warning. If one used such a judge to curate training data, it would preferentially admit convincing failures. If used in RL, it could reward the agent for producing trajectories that resemble success without satisfying the task.

### 3. More screenshots are not the main fix; trajectory text matters more

The paper’s ablations are useful because they resist a tempting intuition: “maybe the judge just needs more visual context.” The authors report that changing the screenshot selection—five trailing screenshots versus three, or first plus last two—moves binary accuracy by less than half a percentage point; sweeping one to sixteen trailing screenshots produces no clean trend. Removing the red click marker does not hurt.

By contrast, removing per-step thought and action text costs 7.2 percentage points on average and flips 22.7% of verdicts. Removing only chain-of-thought while retaining actions costs less, 1.8 percentage points, and flips 11.6% of verdicts. The paper’s interpretation is important: the action history carries more signal than the agent’s internal narrative, but the textual history is still the dominant evidence channel. Judges need to know what the agent did, not just what the last screen looked like.

This also creates a tension. If a judge leans too heavily on the agent’s narrative, a confident final claim can mislead it. If it ignores text, it misses intent encoded in typed actions or web strings. The practical solution is not “hide the reasoning” or “show all screenshots”; it is structured trajectory evidence with action provenance, state diffs, and adversarially tested judge prompts.

### 4. Thinking harder and voting do not solve the judge problem

The authors also test whether model-side knobs fix reliability. Extra “thinking” helps weaker judges somewhat but gives little at the frontier. Re-running the same judge at temperature 0.7 flips 6–9% of verdicts, making individual labels noisy even when aggregate accuracy is stable. A top-3 majority vote improves the best single judge by about one percentage point at several times the cost, because top judges tend to make the same mistakes; pairwise Cohen’s κ among top judges is reported around 0.71.

This is one of the paper’s more general lessons. When judges are correlated, ensembling is not a free lunch. A vote is useful only if the errors are diverse enough that the majority can identify the right answer. OSReward suggests the opposite for hard CUA trajectories: the models herd on the same confusing cases.

### 5. Reliable judging can be bought, but not at RL scale

The cost section makes the reward-model argument explicit. The paper reports that judging the full OSReward set once costs roughly $100 with Claude-Opus-4-8 and $45 with GPT-5.5 at the paper’s pricing assumptions, while cheaper judges degrade substantially on OSReward-Hard. At training scale, the economics become prohibitive. A modest online RL run with 200 updates, batch 16, and 16 rollouts already creates 51,200 judge calls. The paper estimates about $4,000 with Claude-Opus-4-8, $2,300 with GPT-5.5, versus about $68 API-equivalent cost with OS-Shepherd-9B.

The exact dollar figures depend on future pricing and serving assumptions, but the structural claim is robust: if reward calls scale with rollouts, frontier API judging becomes an operating expense, not a benchmark convenience.

### 6. OS-Shepherd is a plausible open reward-model path

OS-Shepherd is the paper’s constructive answer. The authors build OS-Shepherd-100K using high-agreement labels from diverse strong judges, retaining only trajectories where the ensemble agrees rather than using a forced majority vote over ambiguous cases. The judge-instance pool is reported as 321,631 instances: web 119,469 (37%), Windows 62,053 (19%), macOS 45,028 (14%), Ubuntu GUI-only 34,355 (11%), Ubuntu GUI+CLI 29,785 (9%), and mobile 30,941 (10%). The retained samples include judge reasoning, not only binary verdicts.

The trained 9B model moves from a highly lenient base to a more balanced judge. Qwen3.5-9B base is reported at 76.7% full-set accuracy with 98.9% success recall and 59.9% failure recall; OS-Shepherd-9B reaches 86.1% accuracy with 86.6% success recall and 86.0% failure recall. On OSReward-Hard, the base has 39.4% accuracy and 14.1% failure recall; OS-Shepherd-9B reaches 60.2% accuracy and 57.6% failure recall.

The larger OS-Shepherd-35B-A3B gets 62.7% hard-set accuracy and 60.1% hard-set failure recall. The authors’ interpretation is that scale adds less than the training recipe: the key improvement is not merely parameter count but a dataset designed to teach failure-catching.

## Interpretation: the false-success economy

The main OSReward result should be read as a measurement of **false-success pressure**. Agents, especially GUI agents, produce attractive traces. A trace has screenshots, a step-by-step plan, tool invocations, and a confident final answer. This makes it easy for a judge to substitute narrative coherence for environmental success.

This problem is not unique to computer use. Coding agents can pass superficial checks while missing the issue; research agents can produce plausible memos with unverified citations; finance agents can generate a coherent investment note while using stale data; on-call agents can identify a plausible service but miss the real root cause. What makes CUAs an unusually clean case is that the final state is external. The task either changed the environment correctly or did not.

OSReward therefore belongs to the same systems trend as recent agent-control work: instruction hierarchy, taint confinement, skill regression accounting, harness-native RL, artifact probes, and benchmark-hygiene audits. The field is learning that the agent is not the model. The agent is the model plus harness, memory, tools, environment, judge, approval gate, and deployment policy.

The paper also suggests a subtle distinction between **judge accuracy** and **judge usefulness**. A judge with 89% aggregate accuracy may still be unacceptable if its residual errors are concentrated in high-risk false positives. Conversely, a stricter judge with slightly lower aggregate accuracy may be more useful in production if it catches failures and routes uncertainty to humans. For deployment, the relevant metric is not “how often did the judge agree with the benchmark?” but “what costly actions would it incorrectly allow?”

## Caveats and what would change my mind

1. **OSReward is still a benchmark.** The environments are richer than many prior setups, but production SaaS workflows, enterprise desktops, broker interfaces, and internal tools will have different failure modes. I would update upward if OS-Shepherd transfers to realistic private MCP/SaaS workflows; I would update downward if it overfits to the OS-Copilot trajectory format.

2. **The gold labels are expensive but not omniscient.** Three annotators plus meta-review is strong by benchmark standards, yet hard CUA success can still be ambiguous. The paper is careful about this, but downstream users should not confuse “human-labeled” with “ground truth in the metaphysical sense.”

3. **The model names and prices are time-bound.** The relative lesson—frontier judges cost too much for dense RL reward—is stronger than the exact cost table. If frontier prices collapse or local frontier-level judges become cheap, the economics shift.

4. **Reward hacking remains open.** A reward model trained to catch current false successes can itself become the target of future agents. If agents train against OS-Shepherd, they may discover adversarial trajectory styles that exploit its calibration. The next step is adversarially generated judge-fooling trajectories, not only held-out natural ones.

5. **Judging is not verification.** OSReward measures VLM judges. In production, many tasks should use deterministic verifiers: database queries, file hashes, unit tests, browser DOM checks, API state checks, account balances, and risk limits. The best architecture will combine deterministic checks with learned judges, not replace verifiers with a single reward model.

## Michael-specific implications

### Agentic company OS

Build the company OS as four separate lanes:

- **Actor lane:** the model/harness that performs the work.
- **Evidence lane:** structured trajectory logs: screenshots, action records, tool outputs, state diffs, files changed, API responses.
- **Judge lane:** learned and deterministic verifiers, with failure recall measured explicitly.
- **Gate lane:** rules for approve, retry, escalate, no-op, or rollback.

Do not let the actor’s final message be the completion record. The completion record should be a judge packet: task, trace, state evidence, verifier result, failure-risk class, and human override if any.

### AI/product strategy

There is a product wedge in **agent reliability dashboards**. Most agent products sell “the agent can do the workflow.” OSReward suggests enterprise buyers will increasingly ask: “How do you know it did?” A strong product surface would show failure recall, false-success examples, per-workflow judge calibration, cost per verified success, judge drift, and escalation thresholds.

### Finance/trading research

Finance is a false-success minefield. A research agent can produce a plausible memo while using an outdated filing, survivorship-biased universe, look-ahead data, wrong FX conversion, stale broker position, or incomplete risk limit. For trading systems, the judge must be asymmetric: a false trade or false model promotion is worse than a missed memo. Use OSReward’s lesson to build finance-specific trajectory evals where **failure recall** dominates aggregate accuracy.

A practical finance analogue: give agents tasks like “update this factor notebook with the latest filings and produce a no-trade/trade recommendation,” then judge not just the recommendation but source vintage, data lineage, leakage checks, risk-limit state, and whether the final action is supported by environment evidence.

### Career/opportunities

Agent reliability engineering remains a durable niche. The valuable skill is not prompting; it is designing trace schemas, reward models, deterministic verifiers, judge calibration suites, adversarial false-success probes, and deployment gates. OSReward gives a concrete research vocabulary for that niche.

## Concept map

- **Computer-use agent trajectory → judge input:** screenshots, thoughts, actions, and environment state become the object to be scored.
- **VLM judge → reward signal:** the judge’s verdict is reused for evaluation, curation, and RL.
- **Leniency bias → false-success risk:** judges over-accept failed trajectories, corrupting both product reporting and training data.
- **OSReward-Hard → diagnostic stress set:** hard, failure-heavy trajectories reveal weaknesses hidden by aggregate full-set accuracy.
- **Failure recall → deployment-critical metric:** catching failures matters more than smooth success recall in high-stakes workflows.
- **Text/action history → evidence carrier:** action text matters more than simply adding screenshots; final visual state is insufficient.
- **Judge herding → weak majority vote:** correlated errors make naive ensembling expensive and only marginally helpful.
- **OS-Shepherd-100K → filtered agreement corpus:** high-agreement judge labels plus reasoning annotations create scalable reward-model data.
- **Open self-hosted reward model → cost control:** local judges make rollout-heavy training economically feasible.
- **Actor–judge–gate architecture → agent OS:** production autonomy requires separation between doing, verifying, and approving.

## Open questions and next experiments

1. **Private workflow transfer:** Evaluate OS-Shepherd-style judges on internal SaaS/MCP tasks: GitHub, email, spreadsheets, CRM, broker sandbox, analytics dashboards.
2. **False-success adversarial set:** Train agents explicitly to fool OS-Shepherd and measure whether failure recall collapses.
3. **Hybrid verifier stack:** Compare learned judges against deterministic state checks and combinations of both.
4. **Judge drift monitoring:** Track how judge calibration changes when the actor model, tool schema, UI, or task distribution changes.
5. **Finance CUA benchmark:** Build a small benchmark where agents must update research notebooks and trade tickets, with no-trade as a valid outcome and leakage/staleness as failures.
6. **Cost-per-verified-success:** Replace token cost with the more relevant operational metric: dollars per task that is both completed and independently verified.
7. **Ambiguity routing:** Instead of forcing binary verdicts, test abstention and escalation policies on OSReward-Hard-like trajectories.
8. **Reward-model governance:** Version, hash, canary, and roll back reward models just like actor models; measure whether reward changes alter agent behavior in unexpected directions.

## Sources

[^osreward]: Qiushi Sun et al., **“OSReward: Instituting Standardized Evaluation for Cross-Platform Computer-Use Reward Models,”** arXiv:2607.28609v1, submitted 30 July 2026. https://arxiv.org/abs/2607.28609v1

[^table1]: OSReward full paper / arXiv HTML, including Table 1 and sections 3–7. https://arxiv.org/html/2607.28609v1

Additional source packet:

- OSReward project homepage. https://os-copilot.github.io/OSReward-Home/
- OSReward GitHub repository. https://github.com/OS-Copilot/OSReward
- OSReward dataset on Hugging Face. https://huggingface.co/datasets/OS-Copilot/OSReward
- OS-Shepherd-100K dataset on Hugging Face. https://huggingface.co/datasets/OS-Copilot/OS-Shepherd-100K
- OSReward and OS-Shepherd model/data collection on Hugging Face. https://huggingface.co/collections/OS-Copilot/osreward-and-os-shepherd
- ORCA-bench, another July 30 agent-evaluation paper focused on on-call root-cause analysis. https://arxiv.org/abs/2607.28545v1
- Change2Task, July 30 paper on constructing executable coding-agent tasks from repository changes. https://arxiv.org/abs/2607.28591v1
- “Sample More, Reflect Less,” July 30 paper on cost-matched reasoning strategies and repeated sampling. https://arxiv.org/abs/2607.28576v1
