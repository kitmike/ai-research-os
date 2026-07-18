# Bridge Evidence and the Retrieval Metric Mismatch

**Thesis —** *Bridge Evidence* is important because it gives a counterfactual measurement of a problem every serious research agent now has: the document that helps an agent is often not the document that helps a stateless reader, so RAG metrics optimized for answer-local relevance may be training the wrong sense of “usefulness.”

## Abstract

The most consequential AI research item I found this afternoon is **“Bridge Evidence: Static Retrieval Utility Does Not Predict Causal Utility in Multi-Step Agentic Search”** by Debayan Mukhopadhyay, Utshab Kumar Ghosh, and Shubham Chatterjee, posted to arXiv on 2026-07-16.[^bridge] The paper is modest in scope—one ReAct-style Qwen2.5-7B-Instruct agent, HotpotQA, BM25 plus cross-encoder retrieval, deterministic replay—but it asks the right causal question. For every document the agent actually read, the authors remove that document and replay the rest of the trajectory from that point. They then compare static reader utility (SRU) with counterfactual trajectory utility (CTU), a composite of final answer loss, next-query retrieval loss, and extra effort. Across 23,322 document observations from 1,000 HotpotQA development questions, SRU and CTU are nearly independent: Spearman rho is reported as −0.0257. In the reader-based quadrant, 35.72% of read documents are “bridge” documents: statically useless, causally load-bearing. A robustness check replacing the reader with BM25/cross-encoder scores still leaves a 27.16% bridge cell. The paper’s caveats are unusually useful: the 35.72% number partly restates independence under a skewed SRU marginal, CTU is agent-specific, and the full method is too expensive for training. The practical implication is nevertheless sharp: agentic research, trading, and company-OS systems need retrieval labels for *trajectory steering*, not merely answer containment.

## Table of contents

1. [Why this paper, and why now](#why-this-paper-and-why-now)
2. [The old retrieval contract](#the-old-retrieval-contract)
3. [The new object: causal utility along a trajectory](#the-new-object-causal-utility-along-a-trajectory)
4. [Evidence and numbers](#evidence-and-numbers)
5. [Interpretation: a metric mismatch, not a new magic trick](#interpretation-a-metric-mismatch-not-a-new-magic-trick)
6. [Caveats and what would change my mind](#caveats-and-what-would-change-my-mind)
7. [Michael-specific implications](#michael-specific-implications)
8. [Concept map](#concept-map)
9. [Open questions and next experiments](#open-questions-and-next-experiments)
10. [Sources](#sources)

## Why this paper, and why now

This week’s research stream has a pattern: agents are being evaluated less like chatbots and more like operating systems. *SearchOS-V1* externalizes search progress into a Frontier Task, Evidence Graph, Coverage Map, and Failure Memory.[^searchos] A coding-agent security paper shows that setup instructions can become a supply-chain attack surface unless dependency name/source/version checks happen before execution.[^setup] A security-agent benchmark argues that fixed-cost performance and tool spend matter, not just peak success under generous budgets.[^cost] Yesterday’s essay focused on abstention: agents need to know when not to act. Today’s paper is the retrieval analogue: agents need to know which evidence is useful *because it changes the future path*.

That is a more fundamental problem than it first appears. An agentic research system is not a single question-answering call. It is a sequence:

1. decide what is missing;
2. search;
3. read;
4. decide what the evidence implies;
5. search again;
6. eventually answer, abstain, trade, escalate, or publish.

Traditional retrieval metrics mostly ask whether a document helps answer the question *now*. But in a multi-step process, a document can help by naming the next entity, falsifying a route, revealing a useful synonym, or narrowing the search space. Such a document may contain none of the final answer. A stateless reader may mark it useless. Yet deleting it may cause the agent to fail.

That is the gap *Bridge Evidence* measures.

## The old retrieval contract

The conventional RAG contract is reader-local: retrieve a document, hand it to a reader with the question, and reward it if the answer improves. The paper calls this **Static RAG Utility** (SRU). Operationally, for each question/document pair, the authors prompt a reader to answer using only that document and compare answer F1 with a no-document baseline.[^bridge-html]

This is not a straw man. It is the shape beneath many retrieval evaluations: nDCG/MAP/MRR variants, dense passage retrieval training, cross-encoder reranking, and RAG benchmarks. The assumption is not “documents should literally contain the answer string” in every case; the more general assumption is that a useful document is useful when read as a self-contained input to a reader.

Agentic search breaks the self-contained assumption. The paper’s example is a HotpotQA-style question: “What political party was the 6th governor of Hawaii that passed bills to help with global warming?” A passage identifying Linda Lingle as the 6th Governor of Hawaii does not answer the political-party question. A static reader sees no answer. But the passage hands the agent the entity “Linda Lingle,” which can be used in the next search. The document is not answer evidence; it is **bridge evidence**.

The paper defines bridge evidence as a document that introduces an entity or relation which appears in the agent’s next query, was absent from prior queries, and whose removal degrades the trajectory, while the document itself scores low on static proxies.[^bridge-html]

This is the conceptual move: the unit of value is no longer “document → answer”; it is “document → next action → future evidence → answer.”

## The new object: causal utility along a trajectory

The paper’s central method is **Counterfactual Trajectory Exploration** (CTE). For every document shown to the agent at a given step, the authors remove that document from the ranked list, keep the logged prefix identical, and replay the remainder of the trajectory with the remaining evidence. This yields a direct omission intervention: what would the agent have done if this document had not been available?

The experimental setup is deliberately constrained:

- backbone: **Qwen2.5-7B-Instruct**;
- agent style: ReAct-like thought/action/search loop;
- data: **1,000** stratified HotpotQA development questions drawn from the 7,405-question dev set after a coverage filter;
- retrieval: BM25 over paragraph-level Wikipedia, top-50 reranked by a cross encoder, top-10 shown;
- decoding: temperature 0.0, sampling disabled, identical hardware;
- maximum search turns: four;
- one-turn trajectories removed from CTU analysis because there is no later step for a document to affect.[^bridge-html]

From each counterfactual replay the authors compute **Counterfactual Trajectory Utility** (CTU) from three deltas:

1. **final answer delta** — did removing the document reduce final answer F1?
2. **next-query delta** — did removing the document degrade the nDCG@10 of the agent’s next query?
3. **effort delta** — did removing the document force extra turns?

All three are oriented so positive means the document helped. They are min-max normalized and summed with equal weights. The authors emphasize that the zero-effect point is not arbitrary: because the observed raw ranges are `[-1,1]`, `[-1,1]`, and `[-2,3]`, a document that changes nothing normalizes to `0.5 + 0.5 + 0.4 = 1.4`. Thus CTU > 1.4 means the document helped on balance; CTU ≤ 1.4 means it did not.[^bridge-html]

The paper then crosses CTU against SRU. The quadrant is simple:

- **A: expected useful** — high SRU, high CTU;
- **B: redundant** — high SRU, low CTU;
- **C: bridge** — low SRU, high CTU;
- **D: genuinely useless** — low SRU, low CTU.

The off-diagonal cells are the interesting ones. Cell B says static retrieval overestimates utility; the agent would have succeeded anyway. Cell C says static retrieval underestimates utility; the document changed the path even though it did not help a stateless reader.

## Evidence and numbers

The headline results are strong, but the right reading is slightly subtler than “one-third of documents are magical bridges.”

### 1. Static and causal utility are nearly independent

After dropping 74 single-turn trajectories, the authors report **23,322 document observations** covering **16,841 unique question/document pairs**.[^bridge-html] Across those records, the Spearman correlation between SRU delta and CTU is:

- all records: **rho = −0.0257**, p = 8.754e−5, n = 23,322;
- two-turn counterfactuals: rho = −0.0083;
- three-turn counterfactuals: rho = −0.0252;
- four-turn counterfactuals: rho = −0.0301.[^bridge-html]

The pooled p-value is small because n is large; the effect size is negligible. The paper explicitly says the right interpretation is not a small negative relation but practical unrelatedness. A system optimized for static utility carries almost no information about which documents this agent needed.

### 2. The reader-based bridge cell is large, but partly because SRU is skewed

The reader-based quadrant reports:

- expected useful: **262** records, **1.12%**;
- redundant: **508**, **2.18%**;
- bridge: **8,331**, **35.72%**;
- genuinely useless: **14,221**, **60.98%**.[^bridge-html]

That 35.72% number is memorable and will probably be over-quoted. The paper’s own caveat is essential: only **3.30%** of observations have positive SRU. If the axes were exactly independent, the expected bridge cell would be `(1 − 0.0330) × 0.3685 = 35.63%`, essentially the observed value.[^bridge-html]

So the bridge percentage is not an independent second discovery. It is the shape independence takes under a very skewed static axis. The discovery is the independence.

### 3. The proxy robustness check is more persuasive

To address the weak-reader problem, the authors replace the reader-based static axis with a combined BM25/cross-encoder proxy. A document is proxy-high when both normalized BM25 and normalized cross-encoder scores agree it is high; proxy-low when both agree it is low. This discards **13,722 of 23,322 observations**—58.84%—where the signals disagree, leaving **9,600** records.[^bridge-html]

On that cleaner subset, the bridge cell remains **2,607 records**, or **27.16%**, and the proxy/CTU correlation is again near zero: **rho = −0.0161**, p = 0.116. This is arguably the more decision-relevant result because it avoids the “stateless reader was too weak” objection. Whatever the BM25/cross-encoder stack confidently likes is still mostly unrelated to what the agent needed.

### 4. The mechanism is entity propagation

The paper’s second experiment asks why bridge documents work. It uses **Observable Entity Relevance** (OER), an entity-ranking signal from prior work by Ghosh and Chatterjee.[^oer] The central test: do entities that discriminate relevant from non-relevant candidates propagate into the agent’s next query?

The answer is yes. Over **227,139 entity-at-step observations**, high-OER entities appear in the agent’s next query **6.1%** of the time under exact whole-title matching, versus **1.5%** for low-OER entities—a **4.02×** ratio, with chi-square p < 1e−300.[^bridge-html] Under partial title-token matching the rates are **14.4%** vs **8.2%**, a **1.77×** ratio.

This is the mechanism that makes the paper more than a quadrant table. Bridge documents are not mysterious. They are often useful because they carry discriminative entities that redirect search.

### 5. A negative result improves the paper

The authors also test whether propagating high-OER entities are specifically localized in bridge documents. That stronger claim does **not** replicate cleanly: exact-match propagation reverses between pilot and full sample, partial-match results are weak, and the relevant Cell A comparison is underpowered. They explicitly decline to claim it.[^bridge-html]

This matters. The paper does not say “bridge documents contain all the magic entities.” It says OER predicts propagation, while localization by quadrant remains unresolved. That restraint makes the main result more credible.

## Interpretation: a metric mismatch, not a new magic trick

The paper’s practical lesson is not “use bridge evidence” as if one could add a dashboard toggle. It is that the field’s labels and metrics may be misaligned with agentic retrieval.

In classical RAG, the question is often: “Which documents help answer this query?” In agentic search, the question becomes: “Which observations improve the policy’s next information-gathering action?” This is closer to reinforcement learning and causal inference than to static retrieval.

The result also explains a familiar failure mode in deep-research agents: they retrieve plausible, answer-shaped material too early and get trapped in local summaries. The documents that would unlock the next branch—the obscure entity, adjacent docket, alternative ticker, supplier name, footnote, regulation, or contradictory phrase—may rank poorly by answer-local criteria. A human analyst recognizes these as leads. Current RAG metrics often score them as noise.

This has a finance analogue. A 10-K paragraph that directly states revenue is answer evidence. A footnote naming a customer concentration, covenant, supplier, regulator, or discontinued segment may be bridge evidence. It does not answer the first valuation question, but it changes the next query. A trading-research agent that only rewards answer-containing evidence will overfit to obvious facts and underweight route-changing clues.

There is also a product-strategy implication: agent UIs should expose the evolving evidence graph, not just final citations. If an answer cites a final source but not the bridge document that caused the search path, the provenance is incomplete. The bridge document may be the reason the system found the final answer at all.

## Caveats and what would change my mind

The paper is unusually explicit about threats to validity. The main ones:

1. **CTU is agent-specific.** Every CTU score is a property of a document, a model, a prompt, a retrieval stack, and a trajectory state. The paper uses Qwen2.5-7B-Instruct under one prompt. A larger model, different reranker, or different tool policy may assign different causal utilities.

2. **The static reader axis is weak and skewed.** Reader answer F1 averages **0.0170** with a document and **0.0122** without one; only **7.50%** of records contain the gold answer at all. This is expected in multi-hop QA, but it weakens the reader-based SRU instrument. The proxy quadrant helps, but it also discards more than half the observations.

3. **Counterfactual replay is expensive.** CTE is a measurement method, not yet a deployable training loop. The authors themselves call for selectors that approximate CTU cheaply.

4. **HotpotQA is not the world.** HotpotQA is useful for controlled multi-hop question answering, but real enterprise/finance research includes noisy documents, adversarial sources, temporal drift, contradictory evidence, and tool costs.

5. **Determinism is approximate.** Temperature 0.0 and fixed hardware reduce variation but do not make language-model execution perfectly reproducible.

What would change my mind? Three replications: (a) the same independence result on frontier closed and open models; (b) the same result on web-scale open-domain research tasks rather than Wikipedia-only HotpotQA; and (c) a learned or heuristic OER-like selector that improves final agent outcomes without simply increasing retrieval breadth and cost. If the phenomenon disappears once models become better query planners, this paper will have identified a transitional bug. If it persists, it is a foundational metric problem.

## Michael-specific implications

### Agentic company OS

A company OS should treat retrieval as state transition, not search result display. Store the evidence graph, failed searches, frontier tasks, and bridge documents. A user should be able to inspect why the agent searched the next thing, not just what it cited at the end. This aligns with *SearchOS-V1*’s explicit state design: Frontier Task, Evidence Graph, Coverage Map, and Failure Memory.[^searchos]

### AI/product strategy

The next high-trust agent product should have a “lead ledger”: documents that changed the agent’s plan, even if they did not directly support the final claim. This becomes a differentiator against generic chat-with-docs systems. It also gives product managers a concrete evaluation target: not “citation precision” alone, but “did the system preserve and exploit useful leads?”

### Finance/trading research

Build a finance-specific bridge-evidence benchmark. Candidate tasks: find the second-order exposure in supplier/customer networks; identify the legal entity behind a filing; trace a commodity, FX, or rates sensitivity; detect when an apparently local event changes the next ticker or jurisdiction to examine. Score evidence by whether it changes the next query and improves the research trajectory, not just whether it contains the answer.

Practical rule: maintain three evidence classes in research agents:

1. **Answer evidence** — directly supports a claim;
2. **Bridge evidence** — changed the next query or path;
3. **Risk evidence** — triggered abstention, escalation, or no-trade.

Most dashboards only show class 1. Serious trading systems need all three.

### Career/opportunities

There is a niche opening around **agent retrieval evaluation engineering**: counterfactual trajectory evaluation, OER-like features, source/path provenance, and cost-aware retrieval policies. This is adjacent to agent reliability engineering but narrower and more defensible: it asks whether the memory/search substrate is optimized for agents rather than readers.

## Concept map

- **Static RAG Utility (SRU)** → measures whether a document improves a stateless reader’s answer.
- **Counterfactual Trajectory Utility (CTU)** → measures whether removing a document harms an agent’s future trajectory.
- **Bridge evidence** → low SRU, high CTU; useless to a reader, useful to the agent path.
- **Redundant evidence** → high SRU, low CTU; answer-looking but causally inert.
- **Counterfactual Trajectory Exploration** → omission intervention over documents actually shown to the agent.
- **Next-query delta** → the term that makes trajectory steering visible.
- **Observable Entity Relevance (OER)** → entity-level proxy for discriminative retrieval signal.
- **Evidence graph** → product structure needed to preserve answer, bridge, and risk evidence.
- **Coverage map** → frontier-state representation for what the agent has and has not searched.
- **Finance lead ledger** → domain adaptation of bridge evidence for market research.

## Open questions and next experiments

1. Replicate CTU/SRU independence on non-HotpotQA research tasks with live web documents.
2. Test whether frontier models reduce bridge reliance or merely use bridge documents more effectively.
3. Train a retrieval selector using OER, query novelty, entity centrality, and failure-memory features; evaluate against CTU without counterfactual replay at inference time.
4. Add bridge-evidence logging to an agentic company OS prototype: record which document caused each subsequent search.
5. Build a finance benchmark where success requires following entity bridges across filings, transcripts, suppliers, legal entities, and macro variables.
6. Measure the cost tradeoff: how much bridge-evidence recall is worth extra retrieval/tool spend?
7. Combine bridge evidence with abstention: can a missing bridge signal indicate “ask for clarification” or “do not trade”?

## Sources

[^bridge]: Debayan Mukhopadhyay, Utshab Kumar Ghosh, Shubham Chatterjee, “Bridge Evidence: Static Retrieval Utility Does Not Predict Causal Utility in Multi-Step Agentic Search,” arXiv:2607.15253v1, 2026-07-16. https://arxiv.org/abs/2607.15253v1

[^bridge-html]: arXiv HTML full text for “Bridge Evidence,” accessed during this run. https://arxiv.org/html/2607.15253v1

[^searchos]: Yuyao Zhang et al., “SearchOS-V1: Towards Robust Open-Domain Information-Seeking Agent Collaboration,” arXiv:2607.15257v1, 2026-07-16. https://arxiv.org/abs/2607.15257v1

[^setup]: Aadesh Bagmar and Pushkar Saraf, “Setup Complete, Now You Are Compromised: Weaponizing Setup Instructions Against AI Coding Agents,” arXiv:2607.15143v1, 2026-07-16. https://arxiv.org/abs/2607.15143v1

[^cost]: Paul Kassianik, Blaine Nelson, Yaron Singer, “Beyond Success Rate: Cost-Aware Evaluation of Offensive and Defensive Security Agents,” arXiv:2607.15263v1, 2026-07-16. https://arxiv.org/abs/2607.15263v1

[^oer]: Utshab Kumar Ghosh and Shubham Chatterjee, “Entity labels are not entity signals: a framework for observable relevance in document re-ranking,” referenced by *Bridge Evidence*; arXiv:2606.15998. https://arxiv.org/abs/2606.15998
