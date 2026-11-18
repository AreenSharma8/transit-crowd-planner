from __future__ import annotations
import csv
from pathlib import Path
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from .analytics import REQUIRED_COLUMNS, load_aggregate, missing_vehicle_percent, ticket_signal, validation_summary
from .network import make_options

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DEMO_PATH = DATA_DIR / "demo_tickets.csv"
ACTIVE_PATH = DATA_DIR / "active_tickets.csv"
MAX_UPLOAD = 350 * 1024 * 1024
app = FastAPI(title="Transit Crowd Planner API", version="0.1.0", description="Local demo API; sample paths are illustrative, not live transit advice.")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"], allow_credentials=False, allow_methods=["GET", "POST"], allow_headers=["*"])

def active_path() -> Path: return ACTIVE_PATH if ACTIVE_PATH.exists() else DEMO_PATH
def active_data(): return load_aggregate(active_path())
def dataset_status():
    stats = active_data(); is_demo = active_path() == DEMO_PATH
    return {"mode": "illustrative sample" if is_demo else "local CSV import", "is_demo": is_demo, "ticket_rows": stats["ticket_rows"], "missing_vehicle_number_percent": missing_vehicle_percent(stats), "file_name": active_path().name, "route_network": "illustrative sample only", "occupancy_available": False}

@app.get("/api/health")
def health(): return {"status":"ok", "service":"transit-crowd-planner", "data":dataset_status()}

@app.get("/api/data/status")
def data_status(): return dataset_status()

@app.get("/api/journeys")
def journeys(origin: str="Kashmere Gate ISBT", destination: str="Nehru Place", depart: str="08:30"):
    stats = active_data(); options = make_options(origin.strip() or "Origin", destination.strip() or "Destination", depart, lambda key, when: ticket_signal(stats,key,when))
    return {"origin":origin, "destination":destination, "departure":depart, "options":options, "notice":"Illustrative demo routes and times; not verified against GTFS or live operations.", "data":dataset_status()}

@app.get("/api/validation")
def validation(route: str="SAMPLE-A"): return validation_summary(active_data(),route)

@app.post("/api/data/upload")
async def upload_ticket_data(file: UploadFile=File(...)):
    if not file.filename or not file.filename.lower().endswith(".csv"): raise HTTPException(status_code=400,detail="Choose a .csv ticketing file.")
    DATA_DIR.mkdir(parents=True,exist_ok=True); temp=DATA_DIR/"active_tickets.csv.part"; total=0
    try:
        with temp.open("wb") as target:
            while True:
                chunk=await file.read(1024*1024)
                if not chunk: break
                total += len(chunk)
                if total > MAX_UPLOAD: raise HTTPException(status_code=413,detail="CSV exceeds the 350 MB local import limit.")
                target.write(chunk)
        with temp.open("r",encoding="utf-8-sig",newline="") as source: header=next(csv.reader(source),[])
        missing=sorted(REQUIRED_COLUMNS-set(header))
        if missing: raise HTTPException(status_code=400,detail="CSV is missing required columns: "+", ".join(missing))
        with temp.open("r",encoding="utf-8-sig",newline="") as source:
            if next(csv.DictReader(source),None) is None: raise HTTPException(status_code=400,detail="CSV has headers but no ticket rows.")
        temp.replace(ACTIVE_PATH)
        return {"ok":True,"status":dataset_status(),"message":"Ticket CSV imported locally. Route paths remain illustrative."}
    except HTTPException:
        temp.unlink(missing_ok=True); raise
    except (UnicodeDecodeError,OSError,csv.Error) as exc:
        temp.unlink(missing_ok=True); raise HTTPException(status_code=400,detail=f"Could not read CSV: {exc}") from exc
    finally: await file.close()
