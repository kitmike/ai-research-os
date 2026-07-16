# AI Research OS — Editorial/Product Brief

Purpose: twice-daily AI research system for Michael Kit.

Cadence:
- Morning 11:00 HKT briefing: fast, actionable, executive briefing.
- Afternoon 16:00 HKT essay: distilled, thoughtful research-paper analysis in the spirit of Gwern.net — rigorous, footnoted, longform, high-signal, with uncertainty, counterarguments, and practical implications.

Visual principles researched from Gwern.net and design references:
- Gwern-like density: serif editorial typography, visible structure, footnotes/citations, abstracts, margin notes, table of contents, calm monochrome base, high information density without clutter.
- GOV.UK principle: start with user needs; do less but better; make the important path obvious; write in plain language.
- Apple/Material chart principles: charts should clarify comparisons, use restrained color, preserve legibility, and encode only meaningful distinctions.
- Dashboard principle: combine overview + drilldown. Show the current answer first, preserve provenance and history underneath.

UI direction:
- Editorial research journal + mission-control dashboard, not generic SaaS.
- Ivory/paper background, ink-black text, bronze/blue accents, subtle grain, dense cards, timeline, source ledger, concept graph placeholder.
- Outputs must be saved in this folder as durable artifacts: Markdown reports, JSON records, and updated index.html dashboard.

Data contract:
- data/research.json contains an array of records: id, date, cadence, title, executive_summary, key_claims, papers, concepts, sources, implications, open_questions, report_path.
- The cron jobs should append or update records idempotently by date + cadence.

Quality bar:
- No invented citations. Cite URLs/DOIs/arXiv IDs actually found.
- Prefer primary sources: arXiv, papers, author pages, labs, GitHub, reputable analysis.
- Include why it matters to Michael: AI/product, finance/trading, agentic company OS, career/opportunities.
