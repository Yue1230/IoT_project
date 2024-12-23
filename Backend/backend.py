from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from collections import defaultdict
import base64
import os
from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# 分類統計數據
classification_stats = defaultdict(int)

# 創建保存圖片和 Saliency Map 的文件夹
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploaded_images')
SAL_MAP_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'saliency_maps')
print(f"上傳文件夾路徑: {UPLOAD_FOLDER}")
print(f"Saliency Map 文件夾路徑: {SAL_MAP_FOLDER}")

# 確保文件夾存在
for folder in [UPLOAD_FOLDER, SAL_MAP_FOLDER]:
    if not os.path.exists(folder):
        try:
            os.makedirs(folder)
            print(f"創建文件夾: {folder}")
        except Exception as e:
            print(f"創建文件夾失敗: {e}")

@app.route('/classify', methods=['POST'])
def classify():
    try:
        data = request.json
        print(f"接收到的數據類別: {data['category']}")
        
        # 獲取分類结果
        category = data['category']
        classification_stats[category] += 1

        # 保存圖片
        if 'image' in data:
            try:
                # 解碼圖片
                image_data = base64.b64decode(data['image'])
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                image_filename = f'image_{timestamp}.jpg'
                image_path = os.path.join(UPLOAD_FOLDER, image_filename)

                with open(image_path, 'wb') as f:
                    f.write(image_data)
                print(f"圖片已保存: {image_path}")
            except Exception as e:
                print(f"保存圖片時出錯: {e}")
                raise

        # 保存 Saliency Map
        saliency_map_data = None
        if 'saliency_map' in data:
            try:
                saliency_data = base64.b64decode(data['saliency_map'])
                sal_map_filename = f'saliency_{timestamp}.jpg'
                sal_map_path = os.path.join(SAL_MAP_FOLDER, sal_map_filename)

                with open(sal_map_path, 'wb') as f:
                    f.write(saliency_data)
                print(f"Saliency Map 已保存: {sal_map_path}")
                
                # 轉換回 Base64 以便發送給前端
                with open(sal_map_path, 'rb') as f:
                    saliency_map_data = base64.b64encode(f.read()).decode('utf-8')
            except Exception as e:
                print(f"保存 Saliency Map 時出錯: {e}")
                raise

        # 廣播數據給前端
        socketio.emit('update_data', {
            'stats': classification_stats,
            'image': data.get('image'),
            'category': category,
            'saliency_map': saliency_map_data  # 新增 Saliency Map 資料
        })

        return jsonify({
            "status": "success",
            "stats": classification_stats,
            "message": "數據處理成功"
        })

    except Exception as e:
        print(f"處理數據時出錯: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    return jsonify(classification_stats)

@socketio.on('connect')
def handle_connect():
    print("客戶端已連接")
    emit('update_stats', classification_stats)

if __name__ == '__main__':
    host = '172.20.10.12'  # 請確保這是正確的IP地址
    port = 5001
    print(f"服務器正在運行，監聽地址: http://{host}:{port}")
    print(f"上傳文件夾位置: {UPLOAD_FOLDER}")
    print(f"Saliency Map 文件夾位置: {SAL_MAP_FOLDER}")
    socketio.run(app, host=host, port=port)
