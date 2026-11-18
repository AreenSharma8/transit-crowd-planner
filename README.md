# Transit Crowd Planner — Phase 1 prototype

Mobile demo: https://AreenSharma8.github.io/transit-crowd-planner/ (static sample preview; actual crowding data requires the local/API backend and authorized Transport Stack data).

A responsive web prototype for the Transport Stack Hackathon's Problem 2: compare bus journey options using a ticketing-derived relative crowding signal. This is a runnable demo, not a live Delhi journey planner.

## What works

- Origin, destination and local departure-time inputs.
- Three journey alternatives with boarding/alighting, transfer, walking and total-time fields.
- A schematic route view (intentionally not a geographic map) and per-route/segment crowding signal.
- Explicit confidence labels and a warning that ticket activity is not onboard occupancy.
- A local CSV import endpoint for the October ticketing extract, plus a peak-vs-midday validation view.
- Responsive mobile/desktop web app with a PWA manifest and icons (offline caching is not implemented).

## Data status and important limits

No Transport Stack account, API key or downloaded ticketing extract was available to this build. The included `backend/data/demo_tickets.csv` is generated illustrative data only. The sample network and travel times are also illustrative: they are not official routes, schedules, live predictions, or a claim that a particular trip exists. Imported ticket rows affect only matching route keys; actual route IDs will need mapping first, and the route network remains illustrative.

The estimator uses passenger-count-weighted ticket volume by sample route and time of day. It reports a relative 0–100 ticket-activity index; it never claims seat occupancy or exact crowd counts. Confidence is based on ticket-row sample volume. `vehicle_number` is retained and missingness is reported because roughly half of the supplied rows may lack it.

To use real data, request the relevant e-ticketing/ETM dataset and static GTFS access through [Delhi Transport Stack](https://delhi.transportstack.in). Export the ticket CSV with these fields: `passenger_count`, `amount`, `vehicle_number`, `ticket_type_id`, `end_stop_name`, `route`, `start_stop_name`, `created_at`, `is_ac`. Upload it through the UI or place it at `backend/data/active_tickets.csv`. The import is local to the running backend. Static GTFS routing and MapLibre geography are deliberately left as adapter points until those feeds are available and verified.

## Run locally

Requirements: Python 3.11+ and Node.js 20+.

### API

```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload --port 8000
```

API docs: <http://localhost:8000/docs>

### Web app

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open <http://localhost:3000>. The UI falls back to clearly labelled sample results if the API is not running. `NEXT_PUBLIC_API_BASE` can override the API URL; see `.env.example`.

### Tests

```bash
cd backend
python -m unittest discover -s tests -v
```

## Data import

Use the UI's “Import ticket CSV” control after the API is running. The backend streams the file to `backend/data/active_tickets.csv`, checks the required header, and uses that file for crowding statistics. The API enforces a 350 MB maximum. Do not upload data you are not authorized to use. For a clean demo reset, stop the API and remove `backend/data/active_tickets.csv`.

## Demo walkthrough

1. Leave the default origin/destination and press **Compare journeys**.
2. Select a route card to inspect its crowding signal and route schematic.
3. Change departure time from a morning/evening peak to midday and compare the index.
4. Run **Peak / midday check**; this is a data sanity check, not a held-out accuracy benchmark.
5. Optionally import the authorized October ticket CSV and repeat.

## Phase 1 submission checklist

- Working prototype and source-code repository URL.
- README and short technical note (this README includes initial method/limits).
- Demo video showing route options, relative crowding, confidence and the data caveat.
- A proper validation report after real data is available: held-out origin/destination/time samples, observed trip comparison, and explicit coverage/missingness. Do not present the included synthetic validation as official results.

## Timeline note checked 18 Nov 2026

The public Where U Elevate listing showed Phase 1 ending 24 Nov 2026 at 18:29 IST and Phase 2 ending 9 Dec at 18:29 IST. The official hackathon brief says the finale is 11 Dec, while the event listing says 10 Dec. Confirm the organizer's authoritative date before planning a presentation. Registration is listed through 20 Nov 2026, 23:59 IST.

## Architecture

- `frontend/`: Next.js App Router + React + TypeScript.
- `backend/`: FastAPI API with DuckDB aggregations over the CSV (compact route/hour summaries, avoiding loading the full 2.56M-row extract into Python).
- Route geometry is a neutral SVG schematic, not geographic mapping. Plug verified GTFS stops/shapes into `backend/app/network.py` before adding MapLibre.
