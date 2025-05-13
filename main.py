import uuid
import cv2
import numpy as np
import socketio
from aiortc import VideoStreamTrack, MediaStreamTrack


def start():
    # 生成一个随机的UUID
    unique_id = uuid.uuid4()
    return str(unique_id)

def send_ws_message(message):
    print("发送的WebSocket消息:", message)  # 打印要发送的消息
    from Server import socketio  # 延迟导入避免循环导入
    socketio.emit('hit_result', message)  # 使用socketio发送消息


# 视频轨道处理器
class VideoProcessorTrack(MediaStreamTrack):
    kind = "video"

    def __init__(self, track, uuid):
        super().__init__()  # 初始化父类
        self.track = track
        self.uuid = uuid

    async def recv(self):
        frame = await self.track.recv()

        # 转为 OpenCV 格式
        img = frame.to_ndarray(format="bgr24")

        # 图像处理逻辑
        result = process_target_image(img)

        # 把结果通过 websocket 推送回客户端
        socketio.emit('message', {
            'type': 'result',
            'uuid': self.uuid,
            'data': result
        })

        return frame  # 原样返回，实际用途可能是记录等
def process_target_image(frame):
    """图像分析逻辑：识别红点位置和环数"""
    # 假设红色点用 HSV 筛选
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_red = np.array([0, 100, 100])
    upper_red = np.array([10, 255, 255])
    mask = cv2.inRange(hsv, lower_red, upper_red)

    # 找轮廓
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    ring = 0
    if contours:
        largest = max(contours, key=cv2.contourArea)
        (x, y), radius = cv2.minEnclosingCircle(largest)
        ring = int(10 - min(radius / 10, 10))  # 假设环数与红点半径反比
    return {'ring': ring}
# 靶纸识别逻辑（简单示例）
def detect_red_dot_ring(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)  # 转换为HSV格式
    mask1 = cv2.inRange(hsv, (0, 70, 50), (10, 255, 255))  # 红色范围1
    mask2 = cv2.inRange(hsv, (170, 70, 50), (180, 255, 255))  # 红色范围2
    mask = cv2.bitwise_or(mask1, mask2)  # 合并掩码

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # 查找轮廓
    if contours:
        # 找到最大轮廓并计算其半径
        c = max(contours, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        if radius > 5:
            # 示例：根据半径估算环数
            return int(max(0, 10 - radius // 10))  # 环数估算
    return None
