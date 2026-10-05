# bog-standard-weekly

Pictures for [Bog Standard](https://bogstandard.uk)'s weekly posts: one hand-drawn sheet per English water company for the week just gone, and a cover ranking them.

Each picture is the site's own sheet, photographed. The live versions, with the figures as tables, are at [bogstandard.uk/week](https://bogstandard.uk/week).

## What's here
- `weeks/<Monday>/`: that week's slides (`01-cover.png`, then the companies in ranking order), `index.json` (each slide's address and description, and the captions), and `data/` (the week's reports exactly as the site's API sent them).
- `latest.json`: which week is the newest.
- `last-run.json`: how the last drawing run went.
- `tools/draw.mjs`: the script that draws them. `.github/workflows/draw.yml` runs it.

## How to read a sheet
- **Rain** is the average of the Environment Agency's rain gauges in the company's area.
- **Spills** are hours of reported discharges from Bog Standard's own record of the water companies' live storm overflow feeds, counted the Environment Agency's way. Hours, not volume: monitors record how long, not how much.
- Figures are provisional. A discharge report is not by itself proof of a permit breach. England only.
- How it's worked out: [bogstandard.uk/methods.html#weekly](https://bogstandard.uk/methods.html#weekly).

Bog Standard is independent, non-campaigning and not affiliated with any water company.
