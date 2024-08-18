from flask import Flask, render_template, session, request, abort, redirect, g
from flask_socketio import SocketIO, join_room, leave_room, send, emit
from sassutils.wsgi import SassMiddleware
import random, sqlite3, datetime, json

sqlite3.enable_shared_cache(True)
sqlite3_db = 'file::memory:?cache=shared'
conn = sqlite3.connect(sqlite3_db, uri=True)

conn.execute('''
             CREATE TABLE IF NOT EXISTS ra_rooms (
             rid TEXT PRIMARY KEY,
             current_countdown TEXT
             )
             ''')
conn.commit()

app = Flask(__name__)
app.config.from_pyfile("config.py", silent=True)
app.wsgi_app = SassMiddleware(app.wsgi_app, {'app': ('static/scss', 'static/css', '/static/css', True)})
socketio = SocketIO(app)

def get_db():
  db = getattr(g, '_database', None)
  if db is None:
    db = g._database = sqlite3.connect(sqlite3_db)
  return db

def randomString():
  string = ""
  stringList = ["data", "analysis", "algorithm", "compute", "storage", "encryption", "network", "cybersecurity", "software", "hardware",
  "database", "cloud", "API", "server", "programming", "code", "interface", "protocol", "machinelearning", "artificialintelligence",
  "internet", "protocol", "analytics", "biometrics", "authentication", "authorization", "firewall", "hacking", "phishing", "malware",
  "virus", "blockchain", "IoT", "sensor", "streaming", "backup", "recovery", "virtualization", "interface", "repository", "debugging",
  "scripting", "frontend", "backend", "responsive", "scalability", "usability", "open-source", "agile", "metadata", "API",
  "automation", "bigdata", "chatbot", "cluster", "dashboard", "debug", "DevOps", "endpoint", "framework", "git", "GUI", "hash",
  "HTML", "HTTP", "HTTPS", "IDE", "Java", "JavaScript", "JSON", "kernel", "Linux", "machinecode", "microservices", "mobile", "modem",
  "module", "node", "objectoriented", "paradigm", "query", "router", "SDK", "SQL", "stack", "syntax", "token", "UNIX", "UX", "VPN",
  "web", "XML", "YAML"]

  for i in range(3):
    string += stringList[random.randint(0, len(stringList))]
  return string.lower()

@app.route('/')
def index():
  return redirect(f'/sender/{randomString()}')

@app.route('/viewer/<rid>')
def viewer(rid):
  if not rid:
    return abort(403)
  return render_template('viewer.html', rid = rid)  
  
@app.route('/sender/<rid>')
def sender(rid):
  if not rid:
    return abort(403)
  return render_template('sender.html', rid = rid)  


@socketio.on('join')
def join(data):
  rid = data['room']
  session['room'] = rid
  join_room(rid)
  db = get_db()
  current_countdown = db.execute("SELECT current_countdown FROM ra_rooms WHERE rid = ?", (rid,)).fetchone()
  if current_countdown:
    current_countdown = json.loads(current_countdown[0])
    sync_val = float(current_countdown.get('timestamp')) + float(current_countdown.get('val')) - datetime.datetime.now().timestamp()
    if sync_val > 0:
      print("join", current_countdown)
      emit('control', {'name': 'countdown', 'val': sync_val}, to=rid)

@socketio.on('control')
def on_event(data):
  data['timestamp'] = datetime.datetime.now().timestamp()
  print("control", data)
  if data.get('name') == 'countdown':
    db = get_db()
    db.execute("INSERT OR REPLACE INTO ra_rooms (rid, current_countdown) VALUES (?, ?)", (session.get("room", None), json.dumps(data)))
    db.commit()
  emit('control', data, to=session.get("room", None))