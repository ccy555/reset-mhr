import main
from flask import Flask, jsonify
app = Flask(__name__)

# 定义接口路由
@app.route('/start', methods=['GET'])
def get_uuid():
    return jsonify({'uuid': main.start()})
if __name__ == '__main__':
    # 监听所有网络接口（0.0.0.0），端口 5000
    app.run(host='0.0.0.0', port=5000, debug=True)