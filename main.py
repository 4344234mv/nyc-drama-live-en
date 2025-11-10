# main.py — NYC DRAMA LIVE v3.2 (FINAL VERSION — 100% WORKING)
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import requests
import folium

app = FastAPI(title="NYC DRAMA LIVE")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def get_complaints(borough=None, limit=100):
    url = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"
    params = {"$limit": limit, "$order": "created_date DESC"}
    if borough and borough != "ALL":
        params["borough"] = borough
    try:
        r = requests.get(url, params=params, timeout=15)
        return r.json()
    except Exception as e:
        print(f"API Error: {e}")
        return []

def create_map(complaints):
    nyc_coords = [40.7128, -74.0060]
    m = folium.Map(location=nyc_coords, zoom_start=12, tiles="CartoDB positron")
    for c in complaints[:50]:
        lat = c.get("latitude")
        lon = c.get("longitude")
        if lat and lon and lat != "0":
            desc = c.get("descriptor", "Unknown issue")
            addr = c.get("incident_address", "Unknown address")
27            popup = f"<b>{desc}</b><br>{addr}"
            folium.CircleMarker(
                location=[float(lat), float(lon)],
                radius=6,
                color="#ff3366",
                fill=True,
                popup=folium.Popup(popup, max_width=300)
            ).add_to(m)
    return m._repr_html_()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, borough: str = "ALL"):
    complaints = get_complaints(borough)
    map_html = create_map(complaints)
    last_update = complaints[0].get("created_date", "Unknown")[:16].replace("T", " ") if complaints else "No data"
    return templates.TemplateResponse("index.html", {
        "request": request,
        "complaints": complaints[:20],
        "total": len(complaints),
        "borough": borough,
        "map_html": map_html,
        "last_update": last_update
    })

@app.get("/api/drama")
async def api_drama(borough: str = "ALL"):
    complaints = get_complaints(borough, 20)
    drama_list = []
    for c in complaints:
        desc = c.get("descriptor", "Unknown")
        addr = c.get("incident_address", "Unknown")
        time = c.get("created_date", "")[11:16]
        drama_list.append(f"{desc} — {addr} — {time}")
    return {"drama": drama_list}