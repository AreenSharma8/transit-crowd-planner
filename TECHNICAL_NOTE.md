# Technical note — Problem 2 prototype

## Decision and scope

Phase 1 is currently scoped to Problem 2, a crowding-aware bus planner. This is a runnable interface and API prototype, not a real trip planner. Its route options, names and travel times are illustrative; they must not be used for travel decisions or represented as live Delhi service data.

## Data and method

The supplied hackathon brief describes October 2026 e-ticketing/ETM data with `passenger_count`, `amount`, `vehicle_number`, `ticket_type_id`, `end_stop_name`, `route`, `start_stop_name`, `created_at` and `is_ac`. Vehicle numbers may be blank for about half the rows. No actual extract, Transport Stack account or API key was available in the build context. The official access instructions say to sign up on the platform and request the needed datasets. The included CSV is generated synthetic demo data, not a copy of the hackathon dataset.

DuckDB aggregates rows by route and local hour, summing passenger counts and counting ticket rows; the UI displays a route-relative 0–100 ticket-activity index, with confidence based on sample volume. A missing matching route is shown as “No matching samples,” not as empty/quiet. This is not an occupancy estimate: ticketing alone does not establish how full a bus is, and missing vehicle numbers prevent reliable vehicle-level attribution.

The “Peak vs midday” panel is a descriptive per-service-day sanity check on available sample rows. It is not a held-out validation and does not prove predictive accuracy. Real validation still needs a documented sample of route/time pairs, observed trip outcomes and explicit coverage/missingness.

## Architecture

- Next.js App Router, React and TypeScript frontend, responsive for desktop and phone.
- FastAPI API with `/api/health`, `/api/data/status`, `/api/journeys`, `/api/validation` and `/api/data/upload`.
- DuckDB for compact route/hour aggregation so the 2.56-million-row CSV can be processed without materializing all rows as Python dictionaries.
- A clean SVG route schematic replaces a geographic map until verified GTFS stops/shapes are available. No MapLibre map is claimed.

## Data contract and next technical step

The local import checks the expected ticket CSV headers and streams to `backend/data/active_tickets.csv` (350 MB limit). The route network remains illustrative; current sample route keys will not match real ticket-route values unless mapped. After obtaining authorized e-ticket/ETM and static GTFS access, build an explicit route/stop adapter, verify route IDs and stop names, then replace the demo network. Keep a “no matching sample” state and avoid occupancy language.

Next validation should hold out dates or trips, compare predicted route/time activity with held-out ticket counts, and spot-check observed peak/off-peak patterns. If the judging brief requires Google Maps travel-time comparison, add it only after verified route journeys and a lawful comparison method are available.
