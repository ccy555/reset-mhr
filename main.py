import uuid
import cv2
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from Server import socketio, app
def start():
    # 生成一个随机的UUID
    unique_id = uuid.uuid4()
    return str(unique_id)

def send_ws_message(message):
    socketio.emit('hit_result', message)

# 视频轨道处理器
class VideoTrack(VideoStreamTrack):
    def __init__(self, track):
        super().__init__()  # don't forget this!
        self.track = track

    async def recv(self):
        frame = await self.track.recv()
        img = frame.to_ndarray(format="bgr24")

        # 图像识别逻辑（示例）
        ring = detect_red_dot_ring(img)  # 👈 你的识别逻辑
        if ring is not None:
            send_ws_message({'ring': ring})

        return frame

# 靶纸识别逻辑（简单示例）
def detect_red_dot_ring(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask1 = cv2.inRange(hsv, (0, 70, 50), (10, 255, 255))  # 红色范围1
    mask2 = cv2.inRange(hsv, (170, 70, 50), (180, 255, 255))  # 红色范围2
    mask = cv2.bitwise_or(mask1, mask2)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        # 找到最大轮廓，计算其半径 → 环数判断逻辑
        c = max(contours, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        if radius > 5:
            # 示例：根据 radius 粗略估算环数
            return int(max(0, 10 - radius // 10))  # 环数估算
    return None


