from flask import Flask, render_template_string, jsonify
from flask_socketio import SocketIO, emit
import sqlite3
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# ---------------- قاعدة البيانات ----------------
def init_db():
    conn = sqlite3.connect("barcodes.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT,
            time TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------------- حفظ الباركود ----------------
def save_barcode(code):
    conn = sqlite3.connect("barcodes.db")
    c = conn.cursor()

    # منع التكرار
    c.execute("SELECT * FROM scans WHERE code=?", (code,))
    if c.fetchone():
        conn.close()
        return False

    c.execute("INSERT INTO scans (code, time) VALUES (?,?)",
              (code, time.strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()
    return True

# ---------------- واجهة الكمبيوتر ----------------
PC_PAGE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Barcode System Pro</title>

<style>
body {
    margin:0;
    font-family: Arial;
    background: #0f172a;
    color:white;
    text-align:center;
}

.card {
    background: rgba(255,255,255,0.05);
    margin:20px auto;
    width:70%;
    padding:20px;
    border-radius:15px;
}

table {
    width:100%;
    color:white;
}

button {
    padding:10px;
    background:red;
    color:white;
    border:none;
    cursor:pointer;
}
</style>

<script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>

</head>

<body>

<h1>📦 نظام الباركود الاحترافي</h1>

<div class="card">
    <h2>آخر باركود</h2>
    <div id="last">---</div>
</div>

<div class="card">
    <h2>السجل</h2>
    <button onclick="clearData()">مسح السجل</button>
    <table id="table"></table>
</div>

<script>
var socket = io();

socket.on('barcode', function(data){

    document.getElementById("last").innerText = data.code;

    let row = `<tr><td>${data.code}</td><td>${data.time}</td></tr>`;
    document.getElementById("table").innerHTML += row;

    new Audio("https://www.soundjay.com/buttons/sounds/button-3.mp3").play();
});

function clearData(){
    fetch('/clear').then(()=> location.reload());
}
</script>

</body>
</html>
"""

# ---------------- صفحة الهاتف ----------------
SCAN_PAGE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Scanner</title>

<script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
<script src="https://unpkg.com/@zxing/library@latest"></script>

<style>
body { margin:0; background:black; }
video { width:100%; height:100vh; object-fit:cover; }
</style>

</head>

<body>

<video id="video"></video>

<script>
const socket = io();
const reader = new ZXing.BrowserMultiFormatReader();

reader.listVideoInputDevices().then((devices)=>{

    const id = devices[0].deviceId;

    reader.decodeFromVideoDevice(id, 'video', (result, err)=>{

        if(result){
            socket.emit('barcode', result.text);
        }

    });

});
</script>

</body>
</html>
"""

# ---------------- Routes ----------------
@app.route('/')
def home():
    return PC_PAGE

@app.route('/scan')
def scan():
    return SCAN_PAGE

@app.route('/clear')
def clear():
    conn = sqlite3.connect("barcodes.db")
    c = conn.cursor()
    c.execute("DELETE FROM scans")
    conn.commit()
    conn.close()
    return "ok"

# ---------------- Socket ----------------
@socketio.on('barcode')
def handle_barcode(data):
    saved = save_barcode(data)

    if saved:
        emit('barcode', {
            "code": data,
            "time": time.strftime("%H:%M:%S")
        }, broadcast=True)

# ---------------- تشغيل ----------------
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
