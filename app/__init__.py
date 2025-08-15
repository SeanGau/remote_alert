from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import random, sqlite3, datetime, json
import sass
from typing import Dict, Set
from contextlib import contextmanager

# Database setup
sqlite3.enable_shared_cache(True)
sqlite3_db = 'file::memory:?cache=shared'
_db_connection = None  # Global connection holder

def get_db_connection():
    global _db_connection
    if _db_connection is None:
        _db_connection = sqlite3.connect(sqlite3_db, uri=True)
    return _db_connection

# FastAPI app setup
app = FastAPI()

# Call init_db() during startup
@app.on_event("startup")
async def startup_event():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS ra_rooms (
        rid TEXT PRIMARY KEY,
        current_countdown TEXT
        )
    ''')
    conn.commit()
    print("Database initialized")

# Add shutdown event to properly close the connection
@app.on_event("shutdown")
async def shutdown_event():
    global _db_connection
    if _db_connection is not None:
        _db_connection.close()
        _db_connection = None

# Templates setup
templates = Jinja2Templates(directory="app/templates")

# Serve static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# SASS Middleware setup
with open("app/static/scss/main.scss", "r") as f:
    scss_content = f.read()
    compiled_css = sass.compile(string=scss_content)
    with open("app/static/css/main.css", "w") as f:
        f.write(compiled_css)

# Database connection management
@contextmanager
def get_db():
    conn = get_db_connection()
    try:
        yield conn
    finally:
        # Don't close the connection, just commit if needed
        conn.commit()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room: str):
        await websocket.accept()
        if room not in self.active_connections:
            self.active_connections[room] = set()
        self.active_connections[room].add(websocket)

    def disconnect(self, websocket: WebSocket, room: str):
        if room in self.active_connections:
            self.active_connections[room].discard(websocket)
            if not self.active_connections[room]:
                del self.active_connections[room]

    async def broadcast_to_room(self, message: dict, room: str):
        if room in self.active_connections:
            for connection in self.active_connections[room]:
                await connection.send_json(message)

manager = ConnectionManager()

def randomString():
    stringList = ["data", "analysis", "algorithm", "compute", "storage", "encryption", "network", "cybersecurity", "software", "hardware",
    "database", "cloud", "API", "server", "programming", "code", "interface", "protocol", "machinelearning", "artificialintelligence",
    "internet", "protocol", "analytics", "biometrics", "authentication", "authorization", "firewall", "hacking", "phishing", "malware",
    "virus", "blockchain", "IoT", "sensor", "streaming", "backup", "recovery", "virtualization", "interface", "repository", "debugging",
    "scripting", "frontend", "backend", "responsive", "scalability", "usability", "open-source", "agile", "metadata", "API",
    "automation", "bigdata", "chatbot", "cluster", "dashboard", "debug", "DevOps", "endpoint", "framework", "git", "GUI", "hash",
    "HTML", "HTTP", "HTTPS", "IDE", "Java", "JavaScript", "JSON", "kernel", "Linux", "machinecode", "microservices", "mobile", "modem",
    "module", "node", "objectoriented", "paradigm", "query", "router", "SDK", "SQL", "stack", "syntax", "token", "UNIX", "UX", "VPN",
    "web", "XML", "YAML"]
    
    return "".join(random.choice(stringList) for _ in range(3)).lower()

# Routes
@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "rid": randomString()})

@app.get("/viewer/{rid}")
async def viewer(rid: str, request: Request):
    if not rid:
        raise HTTPException(status_code=403)
    return templates.TemplateResponse("viewer.html", {"request": request, "rid": rid})

@app.get("/sender/{rid}")
async def sender(rid: str, request: Request):
    if not rid:
        raise HTTPException(status_code=403)
    return templates.TemplateResponse("sender.html", {"request": request, "rid": rid})

# WebSocket endpoints
@app.websocket("/ws/{rid}")
async def websocket_endpoint(websocket: WebSocket, rid: str):
    await manager.connect(websocket, rid)
    
    try:
        # Send current countdown on join
        with get_db() as db:
            current_countdown = db.execute(
                "SELECT current_countdown FROM ra_rooms WHERE rid = ?", 
                (rid,)
            ).fetchone()
            
            if current_countdown:
                current_countdown = json.loads(current_countdown[0])
                sync_val = float(current_countdown.get('timestamp')) + float(current_countdown.get('val')) - datetime.datetime.now().timestamp()
                if sync_val > 0:
                    await websocket.send_json({
                        "name": "countdown",
                        "val": sync_val
                    })

        while True:
            data = await websocket.receive_json()
            data['timestamp'] = datetime.datetime.now().timestamp()
            
            if data.get('name') == 'countdown':
                with get_db() as db:
                    db.execute(
                        "INSERT OR REPLACE INTO ra_rooms (rid, current_countdown) VALUES (?, ?)",
                        (rid, json.dumps(data))
                    )
                    db.commit()
            
            await manager.broadcast_to_room(data, rid)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, rid)