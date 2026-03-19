from flask import Flask, jsonify
import json
import datetime

AIRPORT = "VMMC"
today = datetime.date.today()
tomorrow = today + datetime.timedelta(days=1)

if datetime.datetime.now().hour > 12:
    target_date_obj = tomorrow
else:
    target_date_obj = today

# target_date_str = target_date_obj.strftime("%Y-%m-%d")
target_date_str = "2026-03-20"
outputFileName = f"{AIRPORT}_{target_date_str}_selected_arrivals.json"
    
app = Flask(__name__)

# 模拟云端接口
@app.route('/api/flights', methods=['GET'])
def get_flights():
    try:
        # 直接读取你生成的现成 JSON 文件
        with open(outputFileName, 'r', encoding='utf-8') as f:
            flights_data = json.load(f)
            print(f"Serving data from {outputFileName} with {len(flights_data)} flights")
        # 包装成通用的接口返回格式
        return jsonify({
            "code": 200,
            "data": flights_data
        })
    except FileNotFoundError:
        return jsonify({"code": 404, "msg": "JSON file not found", "data": []})

if __name__ == '__main__':
    # 启动本地服务器
    print("Mock server running at http://127.0.0.1:5000/api/flights")
    app.run(host='127.0.0.1', port=5000, debug=True)