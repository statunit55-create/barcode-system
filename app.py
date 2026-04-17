from flask import Flask, render_template_string
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

barcodes = []

HTML = """
<!DOCTYPE html>
<html lang="ar">
<head>
<meta charset="UTF-8">
<title>نظام الباركود</title>

<style>
body {
    margin:0;
    font-family: 'Segoe UI';
    background: linear-gradient(135deg, #0f172a, #1e293b);
    color: white;
    text-align:center;
}

.container {
    margin-top: 40px;
}

.card {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(12px);
    padding: 20px;
    margin: 15px auto;
    width: 60%;
    border-radius: 20px;
    box-shadow: 0 0 20px rgba(0,0,0,0.3);
}

h1 {
    color: #38bdf8;
}

#last {
    font-size: 30px;
    color: #22c55e;
}

.list {
    max-height: 300px;
    overflow-y: auto;
    text-align:left;
}

.item {
    padding: 8px;
    border-bottom: 1px solid rgba(255,255,255,0.1);
}
</style>

<script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>

</head>
<body>

<div class="container">
    <h1>📡 نظام قراءة الباركود المباشر</h1>

    <div class="card">
        <h3>آخر باركود:</h3>
        <div id="last">---</div>
    </div>

    <div class="card">
        <h3>السجل:</h3>
        <div class="list" id="list"></div>
    </div>

    <div class="card">
        <h3>افتح الرابط من الهاتف:</h3>
        <p id="link"></p>
    </div>
</div>

<script>
var socket = io();

socket.on('barcode', function(data){
    document.getElementById("last").innerText = data;

    var list = document.getElementById("list");
    var item = document.createElement("div");
    item.className = "item";
    item.innerText = data;
    list.prepend(item);

    new Audio("https://www.soundjay.com/buttons/sounds/button-3.mp3").play();
});

document.getElementById("link").innerText = window.location.href + "scan";
</script>

</body>
</html>
"""

SCAN_PAGE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Scanner</title>

<script src="https://unpkg.com/html5-qrcode"></script>
<script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>

<style>
body {
    margin:0;
    background:black;
}
#reader {
    width:100vw;
    height:100vh;
}
</style>

</head>

<body>

<div id="reader"></div>

<script>
var socket = io();

function onScanSuccess(decodedText) {
    socket.emit('barcode', decodedText);
}

var scanner = new Html5Qrcode("reader");

scanner.start(
    { facingMode: "environment" },
    {
        fps: 10,
        qrbox: 250
    },
    onScanSuccess
);
</script>

</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/scan')
def scan():
    return render_template_string(SCAN_PAGE)

@socketio.on('barcode')
def handle_barcode(data):
    barcodes.append(data)
    emit('barcode', data, broadcast=True)
    print("تم الاستلام:", data)

# تشغيل محلي أو على السيرفر
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
