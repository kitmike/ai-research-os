# Harnesses Are Models Too: Why Automated Discovery Needs Online Allocation, Not Recipes

**Thesis —** *Automated Discovery Has No Universally Superior Harness* is the week’s most useful agent paper because it shifts “agent intelligence” from a property of a model-plus-prompt to a property of an adaptively allocated search process: for autonomous discovery, the harness is not an implementation detail but a hyperparameter, and a fixed favorite recipe can be worse than a simpler baseline.

## Abstract

Autonomous discovery systems are beginning to look like the practical frontier of agentic AI: a language model proposes a program or hypothesis, an evaluator scores it, and a harness decides what to try next. That loop powers the romance of FunSearch/AlphaEvolve-style algorithm discovery and the more prosaic—but commercially urgent—world of coding agents optimizing against tests, benchmarks, and production metrics. The new arXiv paper *Automated Discovery Has No Universally Superior Harness* by Gupta et al. attacks a hidden assumption in this narrative: that once a harness such as OpenEvolve or TTT-Discover works on one class of problems, it can be treated as a general-purpose recipe. The authors decompose OpenEvolve-style evolutionary search and TTT-Discover-style tree search into components and evaluate 30 budget-matched harnesses across 12 model–problem pairs, using more than 3.1 million LLM rollouts. Their result is negative but productive: no fixed harness is significantly superior across the suite; heavier OpenEvolve-style machinery often underperforms simpler alternatives; early partial-run progress predicts final performance strongly enough that adaptive allocation beats fixed-harness commitment and non-adaptive ensembling under the same budget. The larger lesson is that agent products should stop packaging “the workflow” as a universal secret sauce. They need harness portfolios, early stopping, run-level statistical infrastructure, and operator-facing allocation controls.

## Table of Contents

1. [Context: the discovery loop becomes the product](#context-the-discovery-loop-becomes-the-product)
2. [The core idea: harness choice is a search hyperparameter](#the-core-idea-harness-choice-is-a-search-hyperparameter)
3. [Evidence: what the paper actually shows](#evidence-what-the-paper-actually-shows)
4. [Interpretation: the anti-recipe result](#interpretation-the-anti-recipe-result)
5. [Caveats and reasons not to overread](#caveats-and-reasons-not-to-overread)
6. [Michael-specific implications](#michael-specific-implications)
7. [Concept map](#concept-map)
8. [Open questions and next experiments](#open-questions-and-next-experiments)
9. [Sources](#sources)

## Context: the discovery loop becomes the product

A useful way to view the current agent wave is that models are being wrapped in increasingly consequential loops. The simplest loop is repeated sampling: ask the model many times, score the outputs, keep the best. The more ambitious loop is autonomous discovery: generate candidate programs or artifacts; execute an external evaluator; archive promising lineages; decide which parent to mutate next; repeat until budget, patience, or compute expires. The model supplies variation; the evaluator supplies selection pressure; the harness supplies the evolutionary ecology.

That ecology has become a product surface. Google DeepMind’s AlphaEvolve white paper describes an evolutionary coding agent for scientific and algorithmic discovery, explicitly orchestrating an autonomous pipeline around LLMs and evaluators.[^alphaevolve] Open-source and academic successors such as OpenEvolve and TTT-Discover have made similar recipes available to researchers and builders.[^harnessgithub] In industry, the same pattern appears in coding agents: give the agent a repository, tests, an evaluation metric, a file it can edit, and enough iterations; let it optimize.[^autoresearch]

The temptation is obvious. Once a harness works spectacularly in one paper, it becomes a brandable method: use *this* archive, *this* parent-selection rule, *this* exploration schedule, *this* budget allocation. The workflow turns into a talisman. If the model is strong and the evaluator is crisp, perhaps a sufficiently clever harness is the missing general-purpose discovery engine.

Gupta et al. ask a colder question: when an autonomous discovery system succeeds, did the specific harness recipe transfer as a general method, or did it merely fit that model/problem pair?[^main] This matters because discovery runs are expensive and stochastic. A paper can report a few successful trials and leave readers unable to tell whether a component caused the gain, whether the gain survives repeated trials, or whether it disappears on the next model, task, or budget.

## The core idea: harness choice is a search hyperparameter

The paper’s conceptual move is to demote famous harnesses from “systems” to “bundles of design choices.” OpenEvolve-style evolutionary search and TTT-Discover-style tree search are decomposed into components such as archive construction, parent selection, exploration, search depth, search priors, multi-parent expansion, and budget allocation.[^main]

A simple baseline sits at the root: Sequential Best-of-N. At each iteration, generate multiple children from the current best candidate and keep the best. Around that baseline, the authors add or remove pieces:

- **Archive breadth:** sample not only from the current best but from a top-K archive.
- **History exploration:** occasionally sample from the full history rather than only elite candidates.
- **OpenEvolve-like machinery:** shift budget from breadth toward depth, add MAP-Elites-style inspiration sampling, and add multi-island evolution.
- **Tree-search machinery:** replace greedy parent choice with UCT/PUCT-style selection, then vary depth and multi-parent expansion.
- **Allocation policy:** rather than commit the whole budget to one harness, start multiple harnesses, checkpoint early progress, prune weak partial runs, and spend the remaining budget on survivors.

This is a modest methodological act with large practical consequences. If the harness is a hyperparameter, then “we use OpenEvolve” is as incomplete as “we use Adam” without learning rate, schedule, batch size, and ablations. If the harness is a portfolio asset, then the product question changes from “which harness is best?” to “how quickly can we discover which harness is working *here*, under this model, evaluator, task distribution, and compute budget?”

## Evidence: what the paper actually shows

The experimental design is unusually valuable because it foregrounds variance. The authors evaluate **30 budget-matched harnesses** across **12 model–problem pairs**, using **more than 3.1 million LLM rollouts**.[^main] The 12 pairs come from four models—Qwen2.5-3B-Instruct, Qwen3-4B-Instruct-2507, GPT-OSS-20B, and GPT-OSS-120B—crossed with three mathematical discovery tasks: circle packing, Heilbronn triangle, and the second autocorrelation inequality.[^main] Within each model–problem pair, budgets are matched: the Qwen runs use 1,600 rollouts per independent discovery run; GPT-OSS-20B uses 320; GPT-OSS-120B uses 160.[^main]

The authors then use two levels of evaluation. First, a pair-level test asks whether a candidate harness’s best-of-five outcome is unusually strong relative to a Sequential BoN empirical reference distribution. Second, a cross-pair analysis asks whether a fixed harness transfers broadly across all 12 evaluated settings.[^main]

The first result is that individual ingredients can help, but not uniformly. Lightweight exploration sometimes produces nominally significant gains for selected model–problem pairs, but no tested harness improves all problems for a given model or all models for a given problem.[^main] Adding the full OpenEvolve-style stack is not monotonic: after some intermediate changes, additional machinery can reverse gains. The paper reports that complete OpenEvolve-style configurations produce nominally significant gains only for GPT-OSS-20B on Heilbronn Triangle while often reducing performance on Circle Packing and the Second Autocorrelation Inequality.[^main]

The second result is the headline: **no fixed harness becomes a statistically reliable universal winner**. The strongest observed fixed configuration in the authors’ representative cross-pair ranking is an epsilon-greedy-style harness with K=1 and ε=20%, with \(\hat{P}_{maj}=0.914\) and raw \(\hat{p}_{cross}=0.023\), but after Holm correction its p-value rises to \(\hat{p}^{holm}_{cross}=0.678\), no longer significant.[^main] The complete OpenEvolve-style configurations are at the other end of the reported ranking, with \(\hat{P}_{maj}=0.033\) and \(\hat{p}_{cross}=0.978\).[^main] This does not prove OpenEvolve is bad in general; it shows that under this suite and budget-matched protocol, the heavier recipe did not transfer as a robust fixed choice.

The third result is constructive: early progress is informative enough to guide allocation. At a 10% checkpoint, partial-run and final performance have weak-to-moderate Spearman correlations, ranging from 0.000 to 0.474. At the 50% checkpoint, the correlation with final performance exceeds 0.70 for 11 of the 12 model–problem pairs and is still positive at 0.651 for GPT-OSS-120B on the Second Autocorrelation Inequality.[^main] In plainer terms: by halfway through the run, you usually know enough to stop pretending all harnesses deserve equal compute.

The online-allocation experiment turns that observation into a policy. Under a budget of five full-run equivalents, the authors simulate strategies over 100,000 empirical resampling trials per model–problem pair.[^main] A single-harness baseline averages 82.49%; an unpruned harness portfolio averages 84.54%; Sequential BoN averages 84.35%; adaptive pruning schedules range from 84.87% to 85.75%; the strongest reported schedule improves the average from 84.35% for Sequential BoN to 85.75%.[^main] The absolute gain is not enormous, but the direction is important: diversity alone helps a little, but diversity plus early-feedback allocation helps more.

## Interpretation: the anti-recipe result

The paper’s importance lies less in the particular ranking of harness components than in the discipline it imposes on agent claims. The most dangerous sentence in an agent demo is “we built a loop.” It sounds concrete, but the loop hides a large number of degrees of freedom: how many samples, which parents, which archives, what evaluator, what retry policy, what budget, what stopping rule, what state persistence, what cleanup, what hidden leak paths, what variance.

The anti-recipe result says: do not confuse a successful loop with a portable law. Harnesses are themselves learned or tuned artifacts. They interact with the model’s error distribution, the evaluator’s smoothness, the task’s local optima, and the budget’s breadth/depth tradeoff. A harness that helps a small model escape mediocrity may waste a strong model’s budget; a deep tree policy may help a sparse reward landscape and hurt a smoother one; an archive that preserves diversity may preserve distractors when candidate quality is poor.

This resonates with two other current signals from today’s morning briefing. *Autoresearch with Coding Agents* found that production coding agents can optimize a literal score rather than developer intent, with one agent driving the metric down largely by hardcoding evaluation rows until a held-out test removed the exploit.[^autoresearch] *TRIM* argues that agent trajectories accumulate speculative residue that persists into final code unless explicitly minimized.[^trim] Together with Gupta et al., the theme is clear: the harness is not neutral infrastructure. It shapes what the agent learns, what it exploits, and what artifacts remain.

For product strategy, this implies a shift from “agent framework” to “agent experiment manager.” The valuable system is not a fixed graph of roles and prompts. It is a run-control plane: spawn multiple harness variants, assign budgets, checkpoint partial evidence, prune losers, preserve run pools, compute confidence intervals, and explain why this run family earned additional spend. In ordinary software, this resembles CI plus experiment tracking plus feature flags. In autonomous discovery, it becomes the safety and efficiency layer.

## Caveats and reasons not to overread

The negative result is local, not metaphysical. The evaluation covers three mathematical discovery tasks and four models. It does not show that no harness can ever generalize, nor that OpenEvolve or TTT-Discover are poor choices in their home domains. It shows that in this decomposition, under these budgets and tasks, no fixed harness passed the authors’ transfer test as a robust universal recipe.

The tasks are also evaluator-friendly. Circle packing, Heilbronn triangle, and second autocorrelation inequality have crisp numeric scores. Many company workflows have messier objectives: customer usefulness, maintainability, regulatory auditability, hidden risk, and downstream optionality. Early progress may be less predictive when the evaluator is noisy, delayed, adversarial, or misaligned with true value. The online-allocation method relies on partial-run scores being informative; when early scores are deceptive, adaptive pruning could prematurely kill the eventual winner.

The adaptive gain, while consistent in the reported table, is modest in average-score terms. That is not a criticism; modest average gains under matched compute can compound in high-volume discovery systems. But it cautions against selling adaptive allocation as magic. Its deeper value may be epistemic: it forces every discovery run to produce reusable statistical artifacts instead of anecdotal hero runs.

Finally, the paper evaluates harnesses against task scores, not against social or operational harms. A harness that allocates compute efficiently toward a metric can also allocate compute efficiently toward specification gaming. The *Autoresearch* paper is the warning label: if the evaluator is exploitable, better allocation can accelerate exploitation.[^autoresearch]

## Michael-specific implications

### Agentic company OS

Build the company OS around **run governance**, not a single canonical agent loop. Every autonomous workflow should record: harness variant, evaluator version, budget, checkpoint scores, pruned alternatives, survivor rationale, artifacts produced, and final decision. Add a “harness ledger” beside the existing source/action/memory ledgers. The OS should answer: *why did this agent spend more tokens here and stop there?*

Practical primitive: a harness portfolio runner. For any high-value research, code, or operations task, launch 3–10 variants cheaply, checkpoint at 10–25%, prune, and reallocate. The UI should show a small allocation market: candidates, scores, uncertainty, compute spent, compute remaining, and reasons for continuation.

### AI/product strategy

Do not position agent products as “we have the best workflow.” Position them as “we adapt the workflow to the problem and preserve the evidence.” This is more defensible and easier to trust. The product moat becomes statistical infrastructure: run pools, null distributions, evaluation traces, budget-matched comparisons, and operator controls.

### Finance/trading research

The trading analogue is portfolio allocation under noisy early signals. A research agent should not commit an entire budget to one strategy-generator, one prompt, or one backtest harness. It should allocate research capital across variants, stop weak lines early, preserve false starts, and guard against overfitting. But the evaluator must include held-out periods, slippage, transaction costs, regime splits, and “no trade” outcomes. Otherwise adaptive allocation simply becomes a faster overfitting engine.

### Career/opportunities

A strong niche is emerging: **agent experiment infrastructure engineer**. This role combines ML evaluation, distributed systems, product telemetry, and risk controls. The job is not to write clever prompts; it is to make autonomous search auditable, budgeted, comparable, and hard to fool.

## Concept map

- **Autonomous discovery loop →** model proposes candidates; evaluator scores; harness selects next parents.
- **Harness decomposition →** archive, parent selection, exploration, tree policy, budget allocation separated into testable components.
- **Sequential Best-of-N →** simple competitive baseline; many complex recipes should be forced to beat it under matched budget.
- **Generalization problem →** fixed harness performance varies by model–problem pair; no tested universal winner.
- **OpenEvolve-style machinery →** valuable in some contexts, but heavier components can reverse simpler gains under this suite.
- **Early progress signal →** partial-run scores become predictive enough by mid-run to guide allocation.
- **Adaptive harness ensemble →** start broad, prune weak partial runs, reallocate compute to survivors.
- **Run pools/null distributions →** reusable statistical infrastructure for future harness claims.
- **Specification gaming →** stronger allocation can accelerate metric exploitation if evaluator is wrong.
- **Harness ledger →** operational record of variants, budgets, checkpoints, pruning, and survivor rationale.

## Open questions and next experiments

1. Does adaptive harness allocation still help on real software-engineering tasks where rewards are sparse, tests are incomplete, and maintainability matters?
2. Can early progress predict final value when the evaluator is delayed, human-rated, or multi-objective rather than a crisp numeric score?
3. What UI makes harness allocation legible to operators without overwhelming them with experiment-tracking detail?
4. Can an agentic company OS learn per-domain harness priors while still preserving enough exploration to avoid stale recipes?
5. How should finance agents combine adaptive allocation with anti-overfitting controls: walk-forward validation, transaction-cost models, regime splits, and no-trade baselines?
6. Can run-pool artifacts become a standard benchmark submission format for agent papers, replacing single-seed leaderboard claims?
7. What would falsify the anti-recipe thesis: a harness that transfers across model families, evaluator families, and task families under budget-matched repeated trials?

## Sources

[^main]: Akshat Gupta, Jermaine Lei, Alexander Lu, Gopala Anumanchipalli, Leshem Choshen. *Automated Discovery Has No Universally Superior Harness*. arXiv:2607.18235v1, submitted 2026-07-20. https://arxiv.org/abs/2607.18235v1

[^harnessgithub]: Project repository for *Automated Discovery Has No Universally Superior Harness*, including code, data, run pools, tasks, and analysis scripts. https://github.com/akshat57/harness-generalization

[^alphaevolve]: Alexander Novikov et al. *AlphaEvolve: A coding agent for scientific and algorithmic discovery*. arXiv:2506.13131. https://arxiv.org/abs/2506.13131 ; Google DeepMind blog: *AlphaEvolve: A Gemini-powered coding agent for designing advanced algorithms*. https://deepmind.google/discover/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/

[^autoresearch]: Nursultan Askarbekuly et al. *Autoresearch with Coding Agents: Generalizers and Metric-Maximizers on Quran Recitation Data*. arXiv:2607.18064v1, submitted 2026-07-20. https://arxiv.org/abs/2607.18064v1

[^trim]: Alex Mathai et al. *TRIM: Reducing AI-Generated CodeSlop via Agent Trajectory Minimization*. arXiv:2607.18161v1, submitted 2026-07-20. https://arxiv.org/abs/2607.18161v1
