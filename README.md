# AI Research OS

A twice-daily AI research briefing + longform paper-analysis workspace maintained by Hermes cron jobs.

## Live site

- GitHub repository: <https://github.com/kitmike/ai-research-os>
- GitHub Pages: <https://kitmike.github.io/ai-research-os/>
- Synchronized source import: <https://github.com/agilentic/ai-research-wire> → [`sources/agilentic-ai-research-wire`](sources/agilentic-ai-research-wire)

## Repository synchronization

This repo is now the canonical combined repository. It preserves the original lightweight AI Research OS dashboard and imports the Agilentic AI Research Wire as a namespaced subtree under `sources/agilentic-ai-research-wire/`.

Current sync model:

- `kitmike/ai-research-os` remains the canonical published GitHub Pages site.
- `agilentic/ai-research-wire` remains the upstream source for its Astro/news-wire system.
- `data/agilentic_articles.json` summarizes imported Agilentic wire articles for the root dashboard.
- To update the import later:

```bash
git remote add agilentic https://github.com/agilentic/ai-research-wire.git 2>/dev/null || true
git fetch agilentic main
git subtree pull --prefix=sources/agilentic-ai-research-wire agilentic main --squash -m "chore: sync agilentic AI research wire"
python3 - <<'PY'
import json
from pathlib import Path
root = Path('.')
src = root/'sources/agilentic-ai-research-wire/data/articles.json'
out = root/'data/agilentic_articles.json'
items = json.loads(src.read_text()) if src.exists() else []
out.write_text(json.dumps(items[:30], indent=2, ensure_ascii=False) + '\n')
PY
python3 scripts/verify_site.py
```

## Schedule

- Morning briefing: ~11:05 HKT (`5 3 * * *` UTC)
- Afternoon essay: ~16:05 HKT (`5 8 * * *` UTC)

Times are staggered by 5 minutes to avoid existing cron slot collisions.

## Files

- `index.html` — aesthetic interactive dashboard
- `data/research.json` — durable research database
- `reports/` — generated Markdown briefings/essays
- `STYLE_GUIDE.md` — design and research contract used by cron prompts
- `.github/workflows/pages.yml` — GitHub Pages deployment workflow
- `AGENTS.md` — operating rules for autonomous improvement jobs
- `scripts/verify_site.py` — deterministic local site verifier

## Local preview

```bash
cd /home/hermes/deliverables/ai_research_os
python3 -m http.server 8765
```

Then open `http://127.0.0.1:8765`.

## Windows copy

```powershell
scp -P 22 -r hermes@YOUR_HOST:/home/hermes/deliverables/ai_research_os .\ai_research_os
```
