import asyncio
from urllib import request
from flask_socketio import SocketIO
from flask import Flask, jsonify
from flask_cors import CORS  # 导入 CORS
from aiortc import RTCSessionDescription, RTCPeerConnection
import main

app = Flask(__name__)
CORS(app)  # 启用 CORS，允许所有域名访问
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')
# 记录每个用户的 WebRTC 连接
peer_connections = {}
uuid_to_ws = {}

# 定义接口路由
@app.route('/start', methods=['GET'])
def get_uuid():
    return jsonify({'uuid': main.start()})

@socketio.on('/ws')
def handle_connect():
    print("Client connected")


@socketio.on('message')
def handle_message(msg):
    asyncio.run(handle_signaling(msg))


async def handle_signaling(msg):
    msg_type = msg['type']
    uuid = msg.get('uuid')

    if msg_type == 'offer':
        pc = RTCPeerConnection()
        peer_connections[uuid] = pc

        @pc.on("track")
        def on_track(track):
            if track.kind == "video":
                local_track = main.VideoProcessorTrack(track, uuid)
                pc.addTrack(local_track)

        offer = RTCSessionDescription(sdp=msg['sdp'], type='offer')
        await pc.setRemoteDescription(offer)
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)

        socketio.emit('message', {
            'type': 'answer',
            'uuid': uuid,
            'sdp': pc.localDescription.sdp
        })

    elif msg_type == 'candidate':
        pc = peer_connections.get(uuid)
        if pc:
            candidate = msg['candidate']
            await pc.addIceCandidate(candidate)

if __name__ == '__main__':
    # 启动Flask应用
    app.run(host='0.0.0.0', port=5000, debug=True)
