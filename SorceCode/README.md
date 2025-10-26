# NudgeeQ

NudgeeQ is an event-floor assistant that combines seat assignment with lightweight messaging. The frontend (Vite + React) walks staff through creating or updating attendee profiles, visualises seat usage, and surfaces inbox activity. The backend (Express + SQLite) enforces seating rules, streams events through SSE/WebSocket, and exposes search endpoints.

## Project Structure

```
.
├─NudgeeQ/            # Frontend (Vite + React + Tailwind + Zustand)
│  ├─src/             # Pages, global store, inbox features
│  ├─public/avatars   # Built-in avatar assets
│  └─.env.local       # Local API/WebSocket configuration
└─server/             # Backend (Express + better-sqlite3)
   ├─src/             # REST API, WebSocket, SSE, data layer
   ├─data/            # SQLite database location
   └─.env             # Backend environment variables (port, CORS, seeds)
```

## Tech Stack

- Frontend: React 19, Vite 7, Tailwind CSS 4, Zustand state management.
- Backend: Express 4, better-sqlite3 (WAL + FTS5), ws, Server-Sent Events.
- Tooling: TypeScript across both apps, `tsx` for TypeScript runtime builds.

## Requirements

- Node.js 20 or newer (needed for better-sqlite3 binaries).
- npm 10+ (bundled with Node 20) or a compatible package manager.
- SQLite ships automatically with better-sqlite3; no manual install required.

## Getting Started

1. **Install dependencies**
   ```bash
   # Backend
   cd server
   npm install

   # Frontend
   cd ../NudgeeQ
   npm install
   ```

2. **Review environment variables**
   - `server/.env`: HTTP host/port, database path, initial table seeds, CORS origin.
   - `NudgeeQ/.env.local`: defaults to `http://localhost:8000/api` and `ws://localhost:8000/ws`.
   Adjust them as needed for your environment.

3. **Run in development**
   ```bash
   # Terminal 1 – backend: REST + WS + SSE
   cd server
   npm run dev

   # Terminal 2 – frontend: Vite dev server (defaults to http://localhost:5173)
   cd NudgeeQ
   npm run dev
   ```
   The first backend start will create `server/data/db.sqlite` and seed the tables defined in `SEED_TABLES`.

4. **Build for production**
   ```bash
   # Backend: compile TypeScript
   cd server
   npm run build    # outputs to dist/

   # Frontend: bundle assets
   cd ../NudgeeQ
   npm run build    # outputs to dist/
   npm run preview  # optional: verify the build locally
   ```

## Useful Scripts

| Location  | Script              | Description                               |
|-----------|---------------------|-------------------------------------------|
| server    | `npm run dev`       | tsx watch mode for hot-reloading TS files |
|           | `npm run build`     | Compile TypeScript to `dist/` via `tsc`   |
|           | `npm run start`     | Run the compiled `dist/index.js`          |
| NudgeeQ   | `npm run dev`       | Launch the Vite development server        |
|           | `npm run build`     | TypeScript build + Vite bundle            |
|           | `npm run preview`   | Serve the production bundle locally       |
|           | `npm run lint`      | ESLint checks                             |

## Environment Variables

### server/.env

| Key           | Default                        | Notes |
|---------------|--------------------------------|-------|
| `PORT`        | `8000`                         | HTTP/WS/SSE listener port |
| `HOST`        | `127.0.0.1`                    | Bind address |
| `DB_FILE`     | `data/db.sqlite` (or absolute path) | SQLite database file |
| `SEED_TABLES` | `24,12,23,25`                  | Table IDs created on first boot |
| `CORS_ORIGIN` | `https://nudgeeq.heilomeow.com` | Allowed origin for browsers |

### NudgeeQ/.env.local

| Key                | Default                     | Notes |
|--------------------|-----------------------------|-------|
| `VITE_API_BASE_URL`| `http://localhost:8000/api` | REST API base URL |
| `VITE_WSS_URL`     | `ws://localhost:8000/ws`    | WebSocket endpoint (`?userId=...`) |
| `VITE_SSE_URL`     | *(optional)*                | Override SSE endpoint (defaults to `.../api/events`) |

## Backend Capabilities

- **REST API** (prefixed with `/api`)  
  - `/tables`, `/tables/:id`: seat occupancy overviews and nearby sorting.  
  - `/roles` endpoints: create, read, update, and delete roles with seat validation and signal editing.  
  - `/search/signals`: SQLite FTS5 search across role signals.  
  - `/roles/:id/messages/{sent|received}`, `/messages`: cursor-based messaging endpoints.
- **Server-Sent Events**: `/api/events?roleId=...` pushes inbox messages in real time.
- **WebSocket**: `/ws?userId=...` enables peer-to-peer delivery and acknowledgements (`src/app/ws.ts`).
- **Storage Layer**: SQLite in WAL mode with triggers to keep `role_signals` and the FTS index in sync. `server/data/db.json` remains as legacy seed data; current state lives in SQLite.

## Frontend Highlights

- Wizard flow (role → table → seat → status → signal → finalize) for guided onboarding.
- `NearbyTables` visualises occupancy and highlights matching signals via `GET /api/tables?near=`.
- `ContactCompose` and inbox components integrate REST, SSE, and Zustand for request/response workflows.
- `IncomingRequestGate` and `Toasts` react to SSE or polling updates to surface new messages immediately.
- Global state persists recent attendee names in LocalStorage for quick reuse.

## Data & Reset

- Default data lives in `server/data/db.sqlite`. Delete the file to reset; the next launch reseeds tables from `SEED_TABLES`.
- To preload roles, either adapt the sample in `server/data/db.json` or script calls against the REST API.

## Deployment Checklist

1. Build both apps: `server/npm run build` and `NudgeeQ/npm run build`.
2. Provide environment files (`.env`, `.env.production`, `.env.local`, etc.) with production values.
3. Run the backend with a process manager (PM2, systemd) via `node dist/index.js`.
4. Serve the frontend `dist/` bundle via a static host or reverse proxy alongside the API.
5. When serving across domains, align CORS, SSE, and WebSocket origins/URLs accordingly.

## Troubleshooting

- **better-sqlite3 install errors**: Ensure Node.js 20+, clear `node_modules`, and reinstall. Windows may require the Build Tools included with the official Node installer.
- **Frontend cannot reach the API**: Confirm `VITE_API_BASE_URL` and `VITE_WSS_URL` match the deployed backend and that CORS allows the origin.
- **SSE not delivering events**: Verify `CORS_ORIGIN` includes the frontend host and enable `withCredentials` if cookies are required.

Feel free to extend this README with deployment walkthroughs or domain-specific instructions as the project evolves.
