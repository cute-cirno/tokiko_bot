from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# 目标 API 服务器地址
TARGET_API_SERVER = "http://sign.lagrangecore.org"

# 代理服务器配置
PROXY = {
    # "http": "http://49.235.253.44:7897",
    # "https": "http://49.235.253.44:7897",
}

@app.route('/api/sign/25765', methods=['GET'])
def sign():
    # 获取请求参数
    params = request.args

    # 将请求转发到目标 API 服务器
    try:
        response = requests.get(f"{TARGET_API_SERVER}/api/sign/25765", params=params, proxies=PROXY)
        if response.headers.get('Content-Type') == 'application/json':
            return jsonify(response.json()), response.status_code
        else:
            return jsonify({"error": "Invalid response format"}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
