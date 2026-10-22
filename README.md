# Footprint Mapper

> OSINT reconnaissance tool — map a company's digital footprint using crt.sh, Shodan, and public job posts.

## Stack

| Layer    | Tech                        |
|----------|-----------------------------|
| Backend  | Python 3.11+ · FastAPI · httpx · BeautifulSoup4 |
| Frontend | Vanilla HTML / CSS / JS (no build step) |

---

## Quick start

### 1 — Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2 — (Optional) Shodan API key

Get a free key at https://account.shodan.io/ then either:

```bash
# Option A — env var
$env:SHODAN_API_KEY="your_key_here"      # PowerShell
export SHODAN_API_KEY="your_key_here"    # bash/zsh

# Option B — paste it directly in the frontend's Shodan key field
```

### 3 — Start the API server

```bash
cd backend
uvicorn main:app --reload
# Server runs at http://localhost:8000
```

### 4 — Open the frontend

Serve the frontend using a local web server to prevent browser CORS restrictions. Open a new terminal window and run:

```bash
cd frontend
python -m http.server 3000

## API endpoints

| Method | Path | Params | Description |
|--------|------|--------|-------------|
| GET | `/api/subdomains` | `domain` | Enumerate subdomains via crt.sh |
| GET | `/api/services` | `domain`, `api_key?` | Exposed services via Shodan |
| GET | `/api/jobs` | `company`, `domain` | Public job posts + Google dork |
| GET | `/api/scan` | `company`, `domain`, `shodan_key?` | All three in parallel |

Interactive docs available at `http://localhost:8000/docs`.

---

## Ethical use

Only scan companies you are explicitly authorised to test — your own organisation, or targets within a bug bounty programme's stated scope. This tool performs **passive reconnaissance only** (no port scanning, no exploitation).
