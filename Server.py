from socket import SocketIO
from urllib import request
from aiortc import RTCSessionDescription, RTCPeerConnection
import main
from flask import Flask, jsonify
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*', async_mode='threading')
pcs = set()
# 定义接口路由
@app.route('/start', methods=['GET'])
def get_uuid():
    return jsonify({'uuid': main.start()})\



@app.route("/offer", methods=["POST"])
async def offer():
    params = request.json
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("track")
    def on_track(track):
        print("Track received:", track.kind)
        if track.kind == "video":
            pc.addTrack(main.VideoTrack(track))

    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return jsonify({
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type
    })

@app.route("/health")
def health():
    return "OK"

if __name__ == '__main__':
    # 监听所有网络接口（0.0.0.0），端口 5000
    app.run(host='0.0.0.0', port=5000, debug=True)