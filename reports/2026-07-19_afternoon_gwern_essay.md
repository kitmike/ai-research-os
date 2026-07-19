# The Install Gap: Why Coding Agents Need Package-Trust Firewalls Before They Need More IQ

**Thesis —** Bagmar & Saraf’s new paper, *Setup Complete, Now You Are Compromised*, is important because it reframes a fashionable question (“how smart is the coding model?”) as a systems question: agent safety during project setup is determined by the model–harness–package-manager boundary, and today that boundary often executes untrusted dependency instructions before it proves name, source, or version integrity.[^setup]

## Abstract

AI coding agents are now competent enough to clone a repository, read its README, create a virtual environment, and install dependencies with little human supervision. That competence exposes an old flaw in a new place. Package installation has always been executable trust: `pip install` can run code, dependency names can be confused, registries can be redirected, and known-vulnerable versions can be pinned. What changed is that the last human friction point—the developer glancing at the install command—is being delegated to an agent harness.

Bagmar & Saraf evaluate documentation-borne install-time attacks against production coding-agent harnesses across twelve scenarios, five attack classes, nine harness-model configurations, four harnesses, and seven models. Their strongest finding is not merely that agents can be tricked; it is that the same model can catch an attack in one harness and install it in another. Agents are comparatively good at obvious package-name mistakes, weaker on plausible separator-confusion names such as `azurecore` vs. `azure-core`, and poor at source and version checks such as registry redirection, hidden indexes, and CVE-pinned installs. Security prompts help narrowly; deterministic pre-install verification helps structurally. The long-run implication is that agentic company operating systems need package-trust firewalls, permission ledgers, and action receipts, not just better prompts or smarter models.

## Table of contents

1. [Context: when “setup” becomes execution](#context-when-setup-becomes-execution)
2. [Core mechanism: documentation as a code-execution vector](#core-mechanism-documentation-as-a-code-execution-vector)
3. [Evidence: what the paper actually tested](#evidence-what-the-paper-actually-tested)
4. [Interpretation: the harness is the security product](#interpretation-the-harness-is-the-security-product)
5. [Caveats: where not to overread](#caveats-where-not-to-overread)
6. [Adjacent evidence: permissions, CAVA, MCP, memory, payment benchmarks](#adjacent-evidence-permissions-cava-mcp-memory-payment-benchmarks)
7. [Michael-specific implications](#michael-specific-implications)
8. [Concept map](#concept-map)
9. [Open questions and next experiments](#open-questions-and-next-experiments)
10. [Sources](#sources)

## Context: when “setup” becomes execution

The first surprising fact about coding agents is how much of their usefulness lives before “coding” begins. They inspect the repository, infer the stack, install dependencies, run tests, build local context, and only then edit files. That setup phase is normally treated as clerical. Bagmar & Saraf argue it should be treated as an execution boundary.

Their term for the relevant defect is the **install gap**: the absence of an authenticity, name, or vulnerability check between a package named in documentation and that package’s code executing on a developer machine.[^setup] This gap predates agents. Python packages can execute code at install time; JavaScript and Rust ecosystems have their own script/build surfaces; package confusion and registry confusion are long-standing supply-chain problems. In human workflows, the gap has been partly masked by a brittle social control: a developer may notice a strange package name, an unfamiliar domain, or an odd flag before pressing enter.

Agents remove exactly that checkpoint. A coding assistant told “set up this repo” may read a README or Makefile and run the implied commands with the user’s filesystem, credentials, shell, and network context. If the repository’s instructions say to use an extra package index, pin a vulnerable version, or install a plausible but wrong dependency name, the agent must either notice and refuse or become the installer for an attacker-controlled artifact.

The paper is therefore less about exotic jailbreaks than about mundane delegated trust. This is why it is a better afternoon essay target than a larger model release: it identifies a near-term failure mode at the exact boundary where product teams are moving from chatbots to working agents.

## Core mechanism: documentation as a code-execution vector

The attack model is deliberately modest. The attacker does not need to compromise the agent provider or jailbreak the base model directly. They only need to modify project files that agents naturally read: README instructions, `requirements.txt`, `pyproject.toml`, Makefiles, or runtime error text. The agent’s job is to interpret those files as setup guidance. The attacker’s job is to make malicious setup look ordinary.

Bagmar & Saraf decompose secure installation into three properties:[^setup]

- **Authentic:** the package comes from a trusted source/index, not an attacker-controlled registry.
- **Intended:** the package name corresponds to what the developer actually wants, not a typosquat or wrong-but-plausible name.
- **Safe:** the requested version is not a known unpatched vulnerable version.

Current agent setup workflows often verify none of these before executing the install. That is the key inversion. The agent may be able to explain package security after the fact; it may refuse a direct request to install malware; it may even be generally “aligned.” But if a malicious instruction is laundered through ordinary repository documentation, the agent may treat it as task context rather than adversarial input.

This makes “documentation” a privileged code path. In a human organization, READMEs are low-friction, low-review artifacts. In an agentic organization, READMEs become operational instructions for autonomous execution. The same is true of product runbooks, analytics notebooks, deployment guides, and MCP tool descriptions. The important generalization is not “README attacks”; it is **semantic configuration drift into executable authority**.

## Evidence: what the paper actually tested

### Evaluation design

The paper reports twelve evaluation scenarios, grouped into five attack classes, using realistic Python project setup patterns. The untrusted-registry scenario is split into localhost and external HTTPS variants, so some result tables contain thirteen attack columns. The authors evaluate nine harness-model configurations over four harnesses and seven models.[^setup]

The scenarios include:

| Class | Examples | Broken property |
|---|---|---|
| Name attacks | obvious typosquat (`tranformers`), separator confusion (`azurecore` vs. `azure-core`), transposition, social-engineered name, cross-file conflict, volume of stacked typosquats | Intended |
| Source attacks | dependency confusion through `--extra-index-url`, untrusted localhost registry, untrusted HTTPS registry, hidden index in `requirements.txt` | Authentic |
| Version attacks | known-vulnerable version pins across a 10-package CVE battery | Safe |
| Config attacks | Makefile sets `PIP_CONFIG_FILE` to redirect package resolution | Authentic |
| Output attacks | ImportError suggests an attacker-controlled package | Intended |

For name and CVE-battery cases, the authors sweep 10 packages at 3 runs each; most other scenarios run a single instance 10 times per configuration. This is useful because it prevents the paper from being a single cherry-picked prompt and instead makes the unit of analysis the interaction between scenario type, harness, and model.

### Key empirical claims

The headline empirical claims are careful but forceful:

1. **The same model can be safe or unsafe depending on the harness.** The paper states that a controlled ablation, swapping only the harness, flips the same attack from fully caught to mostly installed—reported as `10/10` caught versus `9/30` caught in one comparison.[^setup] This is the paper’s most important product implication: model intelligence is not the security boundary.

2. **Agents handle obvious bad names better than bad sources.** Obvious typosquats are usually corrected or refused. Plausible separator confusion names remain a residual vector. Source-based attacks—registry redirection and hidden indexes—are missed “almost everywhere” in the authors’ summary.[^setup]

3. **The source blind spot generalizes across ecosystems.** The authors report analogous source-based failure patterns on npm and Cargo: nearly every model installs the untrusted dependency, while name detection transfers less consistently.[^setup]

4. **Security prompts recover only the named dimension.** If prompted to care about source trust, agents improve on source checks; if prompted about versions, they may activate version-specific knowledge. But prompts do not create a general policy firewall.

5. **A deterministic pre-install hook is the structural fix.** The authors argue that verifying package names, sources, and versions before any code runs closes most of the gap. In other words, safety belongs in the harness/package-manager checkpoint, not in a post-hoc review after install-time code has already executed.[^setup]

### Why the evidence is credible enough to act on

The paper’s strongest evidence is not a single percentage improvement but a pattern that matches surrounding incidents and adjacent work. It cites prior supply-chain incidents and surfaces real-world prevalence: the paper states that the deprecated `sklearn` stub drew 1,773,620 PyPI downloads in a trailing 30-day period in June 2026, that a live `tdqm` typosquat appeared in over 960 `requirements.txt` files, and that `--extra-index-url` patterns appeared in over 5,500 README files and 6,900 `requirements.txt` files, with the PyTorch CUDA-wheel index URL alone in over 10,000 `requirements.txt` files.[^setup] These GitHub code-search counts are explicitly described as order-of-magnitude estimates, not precise census numbers, but they make the attack surface feel less hypothetical.

The background incidents are also recognizable: the PyTorch `torchtriton` dependency confusion incident, the Ultralytics compromise via GitHub Actions injection, and dependency-confusion attacks against major companies.[^pytorch][^ultralytics][^birsan] None of these require a science-fiction adversary. They are mundane supply-chain mechanics meeting automation.

## Interpretation: the harness is the security product

The paper’s conceptual contribution is the claim that “agent safety” is not located inside the model. It is located at the boundary between model intent, harness mediation, and tool execution. That boundary is where an instruction becomes a shell command, browser click, API call, dependency install, database query, email send, or payment.

A strong model can know that package provenance matters and still fail if its harness normalizes setup as a routine execution task. Conversely, a weaker model can become safer if the harness refuses to execute until deterministic checks pass. This is the same lesson GitHub recently reported from Copilot code review: better shared tools initially increased cost and reduced useful findings until GitHub rewrote the workflow instructions around how a reviewer actually reads pull requests; after that, the migration became roughly 20% cheaper at similar review quality.[^github] In both cases, the agent product is the workflow, not the model call.

For agentic systems, this suggests a hierarchy of controls:

1. **Hard pre-execution checks:** package source allowlists, version/CVE checks, package-name normalization, lockfile verification, signature/provenance checks where available.
2. **Semantic suspicion:** the model can explain why an instruction is odd, but its judgment should not be the sole gate.
3. **Permission binding:** approvals should bind to canonical actions, not vague summaries.
4. **Receipts:** after execution, the system should produce a durable record of what was installed, from where, under what policy, with what hash/lockfile state.
5. **Post-hoc auditing:** useful, but insufficient for install-time execution because the code may already have run.

This also gives a useful criterion for product evaluation. A coding agent that says “I checked dependencies” is less valuable than one that can produce a machine-checkable dependency trust receipt. A company OS should prefer boring gates over theatrical autonomy.

## Caveats: where not to overread

First, the main paper is an arXiv preprint from July 16, 2026. Its claims deserve replication across more repositories, package ecosystems, harness versions, enterprise policies, and agent deployment modes. Production coding-agent harnesses change quickly, and vendors may patch specific failure modes after public disclosure.

Second, the paper’s setup scenarios are controlled. That is a strength for diagnosis but a limit for prevalence inference. The fact that an attack works in a benchmark does not tell us how often real attackers will use that vector, how often agent users run with auto-approval, or how much blast radius enterprise sandboxes already remove.

Third, package-source policy is genuinely hard. A naive allowlist can block legitimate workflows: private registries, GPU wheels, nightly builds, editable installs, monorepo-local packages, and research artifacts. The defense should not be “never use a non-default index”; it should be “make index trust explicit, inspectable, and policy-bound.”

Fourth, deterministic checks can themselves become brittle. Names are ambiguous, version vulnerability feeds are incomplete, signatures are unevenly adopted, and dependency resolution can be non-obvious. The correct architecture is layered: deterministic gate, model explanation, user approval for exceptions, sandboxed install, and post-install audit.

Finally, the result should not be read as “agents are unsafe, therefore avoid agents.” It says something narrower and more useful: agents are useful enough that they now need the same kind of pre-execution controls we already expect around CI/CD, secrets, production deploys, and payment rails.

## Adjacent evidence: permissions, CAVA, MCP, memory, payment benchmarks

This week’s surrounding papers look like pieces of the same operating-system migration.

**Permissions.** Michael & Roesner survey 21 proposals for agent permission systems and analyze five prominent commercial agents, emphasizing the gap between user-level preferences, UI specification, internal policy derivation, and runtime enforcement.[^permissions] This complements Bagmar & Saraf: even if a user wants to allow “set up project dependencies,” the system still needs to know whether “install from attacker.example via hidden index” is inside that permission.

**Canonical action records.** CAVA proposes canonical runtime action objects for heterogeneous agent runtimes and evaluates a reference implementation through a 96-seed, 384-variant benchmark.[^cava] The link to install security is direct: “install package X from source Y at version Z” should be a canonical action with approval binding and receipt integrity, not an opaque shell transcript.

**MCP runtime evidence.** FlowGuard argues that MCP scanners need runtime evidence, not just suspicious semantic signals. It evaluates 1,880 MCP cases across five vulnerability categories, reports F1 scores of 0.879 for command injection and 0.942 for file-system access, and reports 523 findings across 326 servers in a real-world evaluation.[^flowguard] This is the MCP version of the same lesson: tool descriptions are not enough; execution behavior matters.

**Persistent memory poisoning.** MemPoison introduces 1,227 hand-validated cases across four attack types, three injection channels, and three memory substrates, showing that write-time defenses can suppress direct attacks while failing on compositional or dormant corruption.[^mempoison] The analogy to setup files is useful: static filtering at ingestion time misses how benign-looking records compose into harmful future behavior.

**Payment integration.** Alipay-PIBench evaluates realistic payment-integration tasks across nine product-specific projects and 18 task instances. Under a with-skill condition, mean rubric pass rate ranges from 68.58% to 91.37%, with an average 10.31 percentage-point improvement over without-skill.[^alipay] This is the positive mirror image. Domain skills and deterministic rubrics improve agents—but in payment workflows the same domain skill must be wrapped by permission and provenance controls.

Together, these papers imply that “agentic OS” is not a metaphor. It is a stack: package trust, memory trust, tool trust, permission trust, action identity, and benchmark trust.

## Michael-specific implications

### Agentic company OS

Build the company OS around ledgers, not chat transcripts:

- **Source ledger:** every dependency, paper, market datum, and claim has a provenance link.
- **Setup ledger:** every install action records package, version, source, hash/lockfile state, CVE status, and policy decision.
- **Permission ledger:** approvals bind to canonical action objects, not natural-language vibes.
- **Memory ledger:** persistent memories are source-scoped, reviewable, TTL-bound, and quarantined when they conflict.
- **Evaluation ledger:** each workflow has deterministic rubrics and “safe refusal/no-action” success states.

For coding agents specifically: no autonomous setup in a privileged environment until a pre-install trust gate passes. If the agent needs an exception, it should produce an exception request with source URL, package metadata, why it is needed, risk class, sandbox plan, and rollback.

### AI/product strategy

A durable product opportunity: **agent trust middleware** for coding and internal-ops agents. The primitive is not another chat surface; it is a pre-execution policy firewall plus receipts. Possible SKUs:

1. Dependency firewall for coding agents.
2. MCP runtime evidence scanner.
3. Canonical action ledger for browser/API/tool actions.
4. Agent memory quarantine/review system.
5. Domain-skill benchmark harness for regulated workflows.

The buyer is anyone moving agents from “assistant” to “operator”: fintech, insurance, devtools, security, data platforms, and internal automation teams.

### Finance/trading research

For trading and finance workflows, the install-gap lesson generalizes to data and execution provenance. A research agent should not silently add a data source, change a backtest universe, install an unvetted package, alter slippage assumptions, or place an order because a notebook or README implied it. The finance equivalent of package trust is:

- dataset trust,
- strategy-code trust,
- broker/API trust,
- order-intent trust,
- backtest-to-live drift controls.

“No trade” should be a valid successful state when provenance is weak.

### Career/opportunities

The emerging career niche is **agent reliability/security engineer**: someone who can combine LLM product sense, package/security engineering, eval design, audit UX, and regulated workflow constraints. The high-leverage portfolio project would be a small but real open-source “agent setup firewall” that intercepts dependency installs from coding agents, scores package/source/version risk, and emits a signed JSON receipt.

## Concept map

1. **Install gap → pre-execution risk:** package code can execute before authenticity/name/version checks occur.
2. **Documentation → executable authority:** READMEs and Makefiles become privileged instructions when agents obey them autonomously.
3. **Harness-model interaction → outcome variance:** the same model may catch or install an attack depending on tool mediation.
4. **Name trust ≠ source trust:** obvious typosquats are easier than registry redirection or hidden indexes.
5. **Prompt mitigation → narrow activation:** prompts help the dimension they mention but do not create complete policy.
6. **Deterministic hook → structural defense:** package trust should be checked before install-time code runs.
7. **Permission policy → user intent binding:** “set up repo” must not imply “trust arbitrary indexes.”
8. **Canonical action object → auditability:** installs, payments, publishes, and exports need stable action identities.
9. **Runtime evidence → real tool security:** MCP/tool scanners need execution evidence, not only semantic warnings.
10. **Memory poisoning → persistent context risk:** agent state must be governed like a mutable dependency.
11. **Domain skill → capability amplifier:** skills improve agent performance but must be policy-bound in high-stakes domains.

## Open questions and next experiments

1. Can an agent setup firewall be implemented as a local wrapper around `pip`, `uv`, `npm`, `cargo`, and shell execution without requiring vendor integration?
2. What false-positive rate would a strict source allowlist create on real AI/ML repositories that use CUDA wheels, private indexes, or nightly builds?
3. Which signal best predicts risky package-name confusion: edit distance, normalized-name collision, download asymmetry, maintainer reputation, or embedding similarity?
4. Can package-install receipts be standardized as a lightweight JSON schema and attached to coding-agent transcripts?
5. How much of the problem disappears under sandboxed ephemeral dev containers with no host credentials—and how much remains because poisoned dependencies enter committed lockfiles?
6. For finance agents, what is the equivalent of a CVE database for data vendors, broker APIs, and strategy templates?
7. Does a CAVA-like canonical action identity improve user comprehension of permission prompts, or does it mainly help auditors?
8. Can domain skills like Alipay-PIBench’s payment integration skill be made safe by construction through included policy checks and deterministic rubrics?

## Sources

[^setup]: Aadesh Bagmar and Pushkar Saraf, “Setup Complete, Now You Are Compromised: Weaponizing Setup Instructions Against AI Coding Agents,” arXiv:2607.15143v1, submitted July 16, 2026. https://arxiv.org/abs/2607.15143v1
[^permissions]: Alexandra E. Michael and Franziska Roesner, “How Agents Ask for Permission: User Permissions for AI Agents, from Interfaces to Enforcement,” arXiv:2607.13718v1, submitted July 15, 2026. https://arxiv.org/abs/2607.13718v1
[^cava]: Zexun Wang, “CAVA: Canonical Action Verification and Attestation for Runtime Governance of Agentic AI Systems,” arXiv:2607.13716v1, submitted July 15, 2026. https://arxiv.org/abs/2607.13716v1
[^flowguard]: Baichao An, Pei Chen, Geng Hong, Yueyue Chen, and Mengying Wu, “FlowGuard: From Signals to Evidence for MCP Security Detection,” arXiv:2607.14754v1, submitted July 16, 2026. https://arxiv.org/abs/2607.14754v1
[^mempoison]: Jifeng Gao et al., “MemPoison: Uncovering Persistent Memory Threats and Structural Blind Spots in LLM Agents,” arXiv:2607.14651v1, submitted July 16, 2026. https://arxiv.org/abs/2607.14651v1
[^alipay]: Shiyu Ying et al., “Alipay-PIBench: A Realistic Payment Integration Benchmark for Coding Agents,” arXiv:2607.14573v1, submitted July 16, 2026. https://arxiv.org/abs/2607.14573v1
[^github]: Napalys Klicius, “Better tools made Copilot code review worse. Here’s how we actually improved it,” GitHub Blog, July 10, 2026. https://github.blog/ai-and-ml/github-copilot/better-tools-made-copilot-code-review-worse-heres-how-we-actually-improved-it/
[^pytorch]: PyTorch Team, “PyTorch dependency confusion via torchtriton,” PyTorch Blog, December 2022, cited in Bagmar & Saraf. https://pytorch.org/blog/compromised-nightly-dependency/
[^ultralytics]: William Woodruff / Yossarian, “Ultralytics YOLO compromised via GitHub Actions injection,” December 2024, cited in Bagmar & Saraf. https://blog.yossarian.net/2024/12/06/zizmor-ultralytics-injection
[^birsan]: Alex Birsan, “Dependency Confusion: How I Hacked Into Apple, Microsoft and Dozens of Other Companies,” February 2021. https://medium.com/@alex.birsan/dependency-confusion-4a5d60fec610
