from flask import Flask, render_template, session, request, abort, redirect
from flask_socketio import SocketIO, join_room, leave_room, send, emit
from sassutils.wsgi import SassMiddleware
import random

app = Flask(__name__)
app.config.from_pyfile("config.py", silent=True)
app.wsgi_app = SassMiddleware(app.wsgi_app, {'app': ('static/scss', 'static/css', '/static/css', True)})
socketio = SocketIO(app)

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

@socketio.on('control')
def on_event(data):
  print("control", data)
  emit('control', data, to=session.get("room", None))