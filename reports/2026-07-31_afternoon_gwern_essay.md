# Spend the Inference Budget on Attempts, Not Self-Flattery

**Thesis —** Mirzaei’s *Sample More, Reflect Less* is important less because it “debunks reflection” than because it gives agent builders a clean accounting rule: every proposed test-time reasoning ritual must beat the boring equal-token alternative of drawing more independent attempts and aggregating them.

**Date:** 2026-07-31, afternoon essay  
**Primary paper:** Iliya Mirzaei, *Sample More, Reflect Less: Self-Refine and Reflexion Lose to Repeated Sampling at Equal Token Cost, from 1.5B to 7B*, arXiv:2607.28576v1, submitted 2026-07-30.[^main]

## Abstract

The most useful new AI paper in the July 30–31 window is a small, careful negative result about test-time reasoning. *Sample More, Reflect Less* reruns the “do reasoning tricks really help, or do they merely spend more tokens?” comparison as a paired experiment: seven prompting/inference methods, Qwen2.5 open models at 1.5B, 3B, and selected 7B comparisons, GSM8K and MATH-500, 150 fixed questions per benchmark, exact answer grading, generated-token accounting, paired bootstraps, and Holm correction. Its headline is stark: across 36 method-setting comparisons, no method is reliably better than self-consistency/repeated sampling at its own measured generated-token cost; ten are reliably worse, and all ten are methods where the model inspects its own output. The core mechanism is not “simplicity good, complexity bad.” It is that an untrained model may be better at producing at least one correct answer among several attempts than at recognizing which attempt is correct. For agents, code generation, finance research, and product strategy, the result argues for budget-frontier dashboards: plot accuracy or utility against tokens, latency, dollars, and tool calls; compare every reflective loop to best-of-N or majority baselines; and instrument whether adaptive control flow actually fires.

## Table of contents

1. [Context: why this paper matters now](#context-why-this-paper-matters-now)
2. [Core mechanism: the cost-matched baseline](#core-mechanism-the-cost-matched-baseline)
3. [Evidence: what was actually measured](#evidence-what-was-actually-measured)
4. [Interpretation: the self-judgment gap](#interpretation-the-self-judgment-gap)
5. [Caveats and ways to overread the result](#caveats-and-ways-to-overread-the-result)
6. [Michael-specific implications](#michael-specific-implications)
7. [Concept map](#concept-map)
8. [Open questions and next experiments](#open-questions-and-next-experiments)
9. [Sources](#sources)

## Context: why this paper matters now

The last two years of LLM application work have had a strange recurring shape. A method is proposed to make a model “think harder”: chain-of-thought, plan-then-solve, self-refine, reflection, tree/graph search, best-of-N, debate, verifier reranking, process rewards, tool-aided retries. Some of these methods are genuinely different, and some of them are thin prompt wrappers over the same base model. But most share a confound: they make the model produce much more text than a single answer.

More text is itself a resource. If a model gets sixteen independent shots at a math problem, one of them may be right even if any single shot is unreliable. Self-consistency made that point early: sample multiple reasoning paths and marginalize/majority-vote the final answer.[^selfconsistency] Inference-scaling work later broadened the same intuition: test-time compute is a knob, not merely an implementation detail.[^snell] The problem is that many “reasoning method” papers compare against one chain-of-thought, not against the best boring use of the same token budget.

Mirzaei’s paper is therefore not merely another entry in the self-correction debate. It is a measurement discipline paper. It says: when a method consumes generated tokens on critiques, reflections, debates, self-verification, or checking, ask whether those tokens would have done better as more independent attempts. If the method cannot beat that frontier, the mechanism is not proven useful, even if it beats a one-shot baseline.

This is directly relevant to agents. An agent loop often contains exactly these costly rituals: plan, act, inspect, critique, retry, summarize, reflect into memory, ask another model to judge, and then choose an action. Without a budget frontier, the loop may look intelligent while merely burning tokens on a worse allocation.

## Core mechanism: the cost-matched baseline

The paper’s central move is simple and unusually clarifying:

1. Run a pool of repeated samples for the same model and question.
2. Measure the generated tokens spent by each fancy method on each task.
3. Locate the self-consistency baseline at the same generated-token cost, interpolating between integer sample counts when needed.
4. Compare method accuracy against that matched-cost repeated-sampling point, paired question by question.

The baseline is not a straw man. It is the natural null hypothesis for test-time reasoning: maybe the method helped only because it spent more output tokens. The paper examines seven methods/configurations: chain-of-thought, Plan-and-Solve, Self-Refine, Reflexion, a forced Reflexion variant, Best-of-N with self-verification, and Multi-Agent Debate.[^main][^cot][^plansolve][^selfrefine][^reflexion][^debate]

Two design details matter.

First, no method is shown the correct answer. This avoids the known self-correction pitfall where “retry until correct” leaks ground truth into the procedure.[^selfcorrect]

Second, the paper treats generated tokens as the cost measure. This is conservative for reflective/debate methods. If input tokens or wall-clock latency were charged, methods that reread long histories or require sequential rounds would generally look worse: independent sampling can be parallelized, while Self-Refine and Reflexion have dependency chains.

## Evidence: what was actually measured

The experimental design is compact enough to summarize without hand-waving:

- **Models:** Qwen2.5-1.5B-Instruct and Qwen2.5-3B-Instruct for the full comparison; Best-of-N/self-verification comparisons also extend to Qwen2.5-7B.[^main]
- **Hardware:** CPU-only llama.cpp runs on a single AMD EPYC 7452 machine with 125 GB RAM, Q8_0 quantization, no GPU.[^main]
- **Benchmarks:** 150 fixed GSM8K questions and 150 fixed MATH-500 questions, paired across methods.[^gsm8k][^math]
- **Statistics:** paired bootstrap confidence intervals over questions, 10,000 resamples, Holm–Bonferroni correction within settings.[^main]
- **Cost:** generated tokens reported from the inference server’s completion-token accounting; sampling-baseline costs computed from recorded per-sample token counts.[^main]

The main result:

> Across 36 method-setting comparisons, after Holm correction within each setting, **0** methods are significantly better than self-consistency at matched token cost; **10** are significantly worse; **26** are statistically indistinguishable.[^main]

The pattern is more informative than the count. Thirty of 36 point estimates are negative. All 18 comparisons involving methods where the model inspects its own output are negative. The significantly worse cells include, among others:

- Best-of-N on Qwen2.5-1.5B/GSM8K: **−7.7 percentage points**, 95% CI **[−13.3, −2.2]**.
- Best-of-N on Qwen2.5-1.5B/MATH-500: **−8.1 pp**, CI **[−14.2, −2.1]**.
- Best-of-N on Qwen2.5-3B/MATH-500: **−14.1 pp**, CI **[−20.0, −8.4]**.
- Forced Reflexion on Qwen2.5-7B/MATH-500: **−10.1 pp**, CI **[−15.0, −5.7]**.
- Self-Refine on Qwen2.5-7B/MATH-500: **−6.3 pp**, CI **[−11.1, −2.0]**.[^main]

The self-consistency frontier itself is not trivial. For Qwen2.5-1.5B/GSM8K, it rises from **70.1%** at one sample, about **297 tokens**, to **80.9%** at 16 samples, about **4,749 tokens**. For Qwen2.5-3B/MATH-500, it rises from **55.7%** at one sample, about **550 tokens**, to **69.3%** at 16 samples, about **8,803 tokens**. For Qwen2.5-7B/MATH-500, it rises from **67.9%** at one sample to **74.4%** at 16 samples.[^main]

The cleanest internal comparison is Best-of-N. The method draws eight candidate solutions and asks the model to pick the best. The paper can then take the exact same eight candidates and instead use majority vote. Same samples, same generation cost, same model; only the selection rule changes. Counting beats model selection in every setting:

- 1.5B/GSM8K: model judges **71.3%**, counting **79.3%**, difference **−8.0 pp**.
- 1.5B/MATH-500: **46.7%** vs **58.0%**, difference **−11.3 pp**.
- 3B/GSM8K: **84.0%** vs **89.3%**, difference **−5.3 pp**.
- 3B/MATH-500: **52.0%** vs **69.3%**, difference **−17.3 pp**.
- 7B/GSM8K: **90.7%** vs **92.7%**, difference **−2.0 pp**, not significant.
- 7B/MATH-500: **71.3%** vs **72.7%**, difference **−1.3 pp**, not significant.[^main]

This isolates the mechanism. The extra answers contain useful information. The untrained model’s self-verifier throws some of that information away.

There is also a valuable “method can pass by not running” lesson. Reflexion, as published, retries only when the model judges its own answer wrong. On Qwen2.5-1.5B, that judgment never fired on either benchmark: **100%** of questions stopped immediately, with mean rounds used **0.00**. Reflexion therefore became a single chain-of-thought under a fancier name. Its apparent efficiency was not evidence for reflection; it was evidence that reflection silently did not happen.[^main]

The authors also report the uncomfortable parts of their own pipeline: a first Best-of-N run failed on long MATH-500 prompts due to context limits, producing a biased easier subset; a scoring bug initially treated Best-of-N candidate lists as majority-vote lists. Both were fixed and documented. This is not a blemish so much as evidence of why replication-style papers matter: many evaluation errors are invisible until the analysis computes the same quantity two ways.[^main]

## Interpretation: the self-judgment gap

The slogan version is “sample more, reflect less.” The more durable version is:

> A base model can be better at generating a correct candidate somewhere in a sample set than at identifying the correct candidate once it sees the set.

That distinction is underappreciated in agent design. Generation, verification, selection, and revision are different capabilities. The same model may be strong at the first and weak at the latter three. Majority voting works not because it understands the solution, but because repeated independent attempts tend to concentrate probability mass on the right final answer when the model has a useful but noisy solution distribution. A self-verifier must do something harder: detect which candidate is correct in cases where candidates disagree.

The paper’s scaling observation makes this precise. As model size rises from 1.5B to 7B, self-verification disagrees with the majority less often. But among disagreements where exactly one of the two is right, the verifier is still usually wrong: the reported verifier-correct shares are below 50% in the measured buckets, though the 7B disagreement counts are small. The gap closes mainly because the model increasingly agrees with the tally, not because it learns to override the tally well.[^main]

This reconciles the paper with verifier-training results. If a trained verifier beats majority voting, the useful ingredient may be verifier training, not the act of asking the base model “which one is best?”[^trainedverify][^processverify] That matters operationally. “Add a critic step” and “train/evaluate a critic as a separate model with calibration and held-out labels” are not the same engineering decision.

A useful analogy for Michael’s product/agent work: a company does not become safer because the same employee reviews their own work in a tired second pass. It becomes safer when review has independence, calibration, checklists, separate incentives, and audit trails. In LLM terms: independent samples, external tools, deterministic tests, trained reward/verifier models, and domain-specific validators.

## Caveats and ways to overread the result

The paper is careful, but its scope is narrow.

1. **Model scale is limited.** The full method comparison is at 1.5B and 3B, with Best-of-N extended to 7B. The paper does not settle frontier-scale self-verification. It suggests what to measure: disagreement rate and override accuracy versus majority vote.

2. **The domain is math with exact answers.** This is both a strength and a limitation. Exact grading makes the comparison clean. But Self-Refine was originally motivated by open-ended generation where critique can improve style, factual coverage, or coherence. Majority voting is naturally strong when final answers can be canonicalized; it may be unavailable for prose, design, or strategy tasks.

3. **Generated tokens are not the only cost.** The paper chooses output tokens because they are deployment-agnostic and easy to record. For real agents, Michael should track input tokens, tool calls, wall-clock latency, dollar cost, failure probability, and human-intervention cost. The qualitative result may strengthen under latency accounting, because independent samples parallelize while sequential reflection does not.

4. **One implementation per method.** Prompting methods are prompt-sensitive. A better Self-Refine prompt, a trained critique model, or a tool-grounded verifier could behave differently. The paper is not a proof that “reflection never works”; it is a proof that claims of reflection helping require a stronger baseline.

5. **Statistical power is modest for small effects.** The paper states its detectable effect sizes: typical intervals are several percentage points wide. “Not significantly better” is not “exactly equal.” For expensive production decisions, a 1–2 pp improvement may still matter if the cost/latency trade is favorable.

The right null hypothesis changes from “does it beat one chain?” to “does it beat the frontier?” That is the paper’s enduring contribution.

## Michael-specific implications

### 1. Agentic company OS

Every agent workflow should have a **test-time budget frontier**:

- one-shot answer;
- N independent attempts;
- majority/self-consistency when answers are comparable;
- best-of-N selected by the base model;
- best-of-N selected by a trained/external verifier;
- reflection/rewrite loops;
- tool-grounded tests;
- human escalation.

The OS should plot success rate versus generated tokens, input tokens, tool calls, latency, and cost. A reflective loop earns its place only if it moves the frontier, not if it merely feels more thoughtful.

### 2. AI/product strategy

This is a product differentiation wedge. Most agent platforms expose “reasoning mode,” “reflection,” or “multi-agent debate” as vibes. A professional platform can expose **budget-evidence cards**:

- “This retry policy improves pass@1 by X at Y additional tokens.”
- “This critic fires on Z% of tasks.”
- “When critic and majority disagree, critic override accuracy is W%.”
- “Parallel sampling reaches the same quality with lower latency on available hardware.”

That is much more valuable for enterprise buyers than another anthropomorphic planning UI.

### 3. Finance/trading research

Trading already understands the paper’s moral: a complex model must beat naive baselines after transaction costs. Here, token spend is transaction cost. For forecasting agents, portfolio research copilots, and strategy-discovery systems, Michael should require:

- equal-budget baselines for every “reflection” or “committee” method;
- walk-forward evaluation, not just retrospective cherry-picking;
- separate selector/verifier evaluation when an agent chooses among candidate trades;
- abstention and no-trade as first-class outcomes;
- latency-aware comparison when market windows matter.

A self-reflective trading agent that produces three rationales and picks one is not automatically safer than sampling three independent forecasts and aggregating.

### 4. Career/opportunities

The opportunity is not to argue that reflection is dead. It is to build the tooling discipline around inference-time compute:

- evaluation harnesses that automatically produce cost-frontier plots;
- verifier calibration dashboards;
- adaptive-loop instrumentation (“did the agent actually reflect?”);
- budget allocators that choose between sampling, tool use, verifier calls, and human review;
- domain-specific graders for code, finance, operations, and research synthesis.

The career edge is becoming the person who can tell when “agentic reasoning” is mechanism versus token spend.

## Concept map

- **Test-time compute** → budget spent during inference rather than training.
- **Generated-token accounting** → conservative cost proxy used to compare methods.
- **Self-consistency / repeated sampling** → boring but strong baseline for exact-answer tasks.
- **Self-inspection** → model critiques, verifies, or rewrites its own output.
- **Verifier override accuracy** → key statistic when model judgment disagrees with majority vote.
- **Adaptive control-flow engagement** → how often a method’s loop actually runs.
- **Budget frontier** → accuracy/utility versus tokens, dollars, latency, and tool calls.
- **Parallelism advantage** → independent samples can run concurrently; reflective loops often cannot.
- **Trained verifier** → separate route by which judging may become worth its cost.
- **Agent operating system** → orchestrator that selects among sampling, reflection, tool tests, verifier calls, and escalation.

## Open questions and next experiments

1. At frontier model scale, does untrained self-verification ever exceed majority voting on disagreement cases, or merely converge to it?
2. Does the same equal-token result hold on code generation when the aggregator is not majority vote but executable tests?
3. For open-ended tasks where final answers cannot be canonicalized, what is the right “boring baseline”: random sample, pairwise preference model, rubric judge, or human spot check?
4. Can a lightweight trained verifier beat both majority vote and base-model self-verification at lower total cost?
5. In agent loops, which is usually better: one reflective trajectory, several independent trajectories, or a hybrid where only uncertain cases get a critic?
6. What is the production-optimal objective: accuracy per output token, accuracy per dollar, latency-constrained success, or expected value after human review cost?
7. Can Reflexion-style methods be made auditable by requiring loop-engagement metrics, not just final scores?
8. For finance/trading agents, does self-critique reduce tail-risk errors or simply add latency and narrative overfitting?

## Sources

[^main]: Iliya Mirzaei, “Sample More, Reflect Less: Self-Refine and Reflexion Lose to Repeated Sampling at Equal Token Cost, from 1.5B to 7B,” arXiv:2607.28576v1, submitted 2026-07-30. https://arxiv.org/abs/2607.28576 ; PDF/source: https://arxiv.org/pdf/2607.28576 and https://arxiv.org/e-print/2607.28576 ; DOI: https://doi.org/10.48550/arXiv.2607.28576
[^selfconsistency]: Xuezhi Wang et al., “Self-Consistency Improves Chain of Thought Reasoning in Language Models,” ICLR 2023, arXiv:2203.11171. https://arxiv.org/abs/2203.11171
[^cot]: Jason Wei et al., “Chain-of-Thought Prompting Elicits Reasoning in Large Language Models,” NeurIPS 2022, arXiv:2201.11903. https://arxiv.org/abs/2201.11903
[^plansolve]: Lei Wang et al., “Plan-and-Solve Prompting: Improving Zero-Shot Chain-of-Thought Reasoning by Large Language Models,” ACL 2023, arXiv:2305.04091. https://arxiv.org/abs/2305.04091
[^selfrefine]: Aman Madaan et al., “Self-Refine: Iterative Refinement with Self-Feedback,” NeurIPS 2023, arXiv:2303.17651. https://arxiv.org/abs/2303.17651
[^reflexion]: Noah Shinn et al., “Reflexion: Language Agents with Verbal Reinforcement Learning,” NeurIPS 2023, arXiv:2303.11366. https://arxiv.org/abs/2303.11366
[^debate]: Yilun Du et al., “Improving Factuality and Reasoning in Language Models through Multiagent Debate,” ICML 2024, arXiv:2305.14325. https://arxiv.org/abs/2305.14325
[^selfcorrect]: Jie Huang et al., “Large Language Models Cannot Self-Correct Reasoning Yet,” ICLR 2024, arXiv:2310.01798. https://arxiv.org/abs/2310.01798
[^snell]: Charlie Snell et al., “Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters,” arXiv:2408.03314. https://arxiv.org/abs/2408.03314
[^gsm8k]: Karl Cobbe et al., “Training Verifiers to Solve Math Word Problems,” arXiv:2110.14168. https://arxiv.org/abs/2110.14168
[^math]: Dan Hendrycks et al., “Measuring Mathematical Problem Solving With the MATH Dataset,” NeurIPS Datasets and Benchmarks 2021, arXiv:2103.03874. https://arxiv.org/abs/2103.03874
[^trainedverify]: Fuxiang Zhang et al., “Incentivizing LLMs to Self-Verify Their Answers,” cited in Mirzaei as arXiv:2506.01369. https://arxiv.org/abs/2506.01369
[^processverify]: Hunter Lightman et al., “Let’s Verify Step by Step,” ICLR 2024, arXiv:2305.20050. https://arxiv.org/abs/2305.20050
