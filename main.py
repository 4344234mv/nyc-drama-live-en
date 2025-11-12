# main.py — NYC DRAMA LIVE v4.0 (NO WEBSOCKET, LOAD ON VISIT)
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
    except:
        return []

def create_map(complaints):
    m = folium.Map(location=[40.7128, -74.0060], zoom_start=12, tiles="CartoDB positron")
    for c in complaints[:50]:
        lat, lon = c.get("latitude"), c.get("longitude")
        if lat and lon and lat != "0":
            desc = c.get("descriptor", "Unknown")
            addr = c.get("incident_address", "Unknown")
            folium.CircleMarker(
                location=[float(lat), float(lon)],
                radius=6, color="#ff3366", fill=True,
                popup=folium.Popup(f"<b>{desc}</b><br>{addr}", max_width=300)
            ).add_to(m)
    return m._repr_html_()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, borough: str = "ALL"):
    complaints = get_complaints(borough)
    map_html = create_map(complaints)
    last_update = complaints[0].get("created_date", "")[:16].replace("T", " ") if complaints else "No data"
    return templates.TemplateResponse("index.html", {
        "request": request,
        "complaints": complaints[:20],
        "total": len(complaints),
        "borough": borough,
        "map_html": map_html,
        "last_update": last_update
    })