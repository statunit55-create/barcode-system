from flask import Flask, render_template_string
from flask_socketio import SocketIO, emit
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# ---------------- صفحة الكمبيوتر ----------------
PC_PAGE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Barcode System</title>

<style>
body {
    margin:0;
    font-family: Arial;
    background:#0f172a;
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

#last {
    font-size:30px;
    color:#22c55e;
}

.item {
    padding:8px;
    border-bottom:1px solid rgba(255,255,255,0.1);
    text-align:left;
}
</style>

<script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
</head>

<body>

<h1>📦 نظام الباركود</h1>

<div class="card">
    <h2>آخر قراءة</h2>
    <div id="last">---</div>
</div>

<div class="card">
    <h2>السجل</h2>
    <div id="list"></div>
</div>

<script>
var socket = io();

socket.on('barcode', function(data){

    document.getElementById("last").innerText = data;

    let div = document.createElement("div");
    div.className = "item";
    div.innerText = data;

    document.getElementById("list").prepend(div);

    // صوت نجاح
    new Audio("https://www.soundjay.com/buttons/sounds/button-3.mp3").play();
});
</script>

</body>
</html>
"""

# ---------------- صفحة الهاتف (الكاميرا) ----------------
SCAN_PAGE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Scanner</title>

<script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
<script src="https://unpkg.com/@zxing/library@latest"></script>

<style>
body {
    margin:0;
    background:black;
}
video {
    width:100%;
    height:100vh;
    object-fit:cover;
}
</style>
</head>

<body>

<video id="video"></video>

<script>
const socket = io();
const codeReader = new ZXing.BrowserMultiFormatReader();

function startCamera() {

    codeReader.listVideoInputDevices()
    .then((devices) => {

        let backCamera = devices[0].deviceId;

        // اختيار الكاميرا الخلفية
        for (let d of devices) {
            if (d.label.toLowerCase().includes("back")) {
                backCamera = d.deviceId;
            }
        }

        codeReader.decodeFromVideoDevice(backCamera, 'video', (result, err) => {

            if (result) {
                socket.emit('barcode', result.text);
                console.log("READ:", result.text);
            }

        });

    })
    .catch(err => console.log(err));
}

startCamera();
</script>

</body>
</html>
"""

# ---------------- routes ----------------
@app.route('/')
def home():
    return PC_PAGE

@app.route('/scan')
def scan():
    return SCAN_PAGE

# ---------------- socket ----------------
@socketio.on('barcode')
def handle_barcode(data):
    print("Barcode:", data)
    emit('barcode', data, broadcast=True)

# ---------------- تشغيل ----------------
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
