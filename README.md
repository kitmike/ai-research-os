# AI Research OS

A twice-daily AI research briefing + longform paper-analysis workspace maintained by Hermes cron jobs.

## Live site

- GitHub repository: <https://github.com/kitmike/ai-research-os>
- GitHub Pages: <https://kitmike.github.io/ai-research-os/>

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
