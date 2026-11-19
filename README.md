# DartConnect 3DA trend — vision prototype

High-fidelity **My DartConnect** pitch prototype: **vendored** dashboard CSS (`public/dartconnect-dashboard.css`), HTML from a sanitized capture in `reference/dashboard/`, and a React **3DA trend** chart injected at the top of **My Performance**. Chart points come from static `src/data/performances.ts` only (no DartConnect API).

## Run locally

```bash
npm install
npm run dev   # runs scripts/build-captured-shell.py via predev
```

To refresh the shell after updating `reference/dashboard/dashboard.html`:

```bash
python3 scripts/build-captured-shell.py
```

## Data

- **League nights** in `src/data/performances.ts` use real Singles 501 averages from your match list.
- **August–September practice** sessions are illustrative so the first-season improvement curve reads clearly (labeled in tooltips).

Raw captures of my.dartconnect.com stay in `reference/` (gitignored; session tokens and other players’ emails).

## GitHub Pages

1. Push `main` to GitHub.
2. Repo **Settings → Pages → Build and deployment:** source **GitHub Actions**.
3. After the workflow runs: **https://austinae.github.io/dartconnect/**

`reference/` stays local (gitignored). Committed `src/generated/` shells are the sanitized HTML the app needs in CI.

## Pitch angle

Lead with **discoverability and design**, not “you don’t have trends.” The weekly line exists but defaults to a single annual dot and lives at the bottom of the page.