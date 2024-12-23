import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import socket
import time
import cv2
import numpy as np
import tensorflow as tf
from tensorflow import keras
import glob
from tensorflow.keras.preprocessing import image
import base64
from datetime import datetime
import matplotlib.pyplot as plt
from io import BytesIO
# hi
# 後端伺服器地址
SERVER_URL = "http://172.20.10.12:5001/classify"

# Raspberry Pi 的伺服器配置
RPi_HOST = '172.20.10.13'  # 替換為 RPi 的 IP 地址
RPi_PORT = 5000          # RPi 的端口

# 圖像預處理配置
size_0 = 288
size_1 = 288
target_size = (size_0, size_1) 

# 加載 TensorFlow 模型
model = keras.models.load_model('model.h5')

# 圖片下載函數
def download_images(base_url, image_folder='images'):
    # 確保圖像資料夾存在
    os.makedirs(image_folder, exist_ok=True)

    # 發送請求並解析目錄頁面
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 遍歷頁面中的所有連結(查找所有的 <a> 標籤) ------ <a href="image1.jpg">image1.jpg</a>
    # 找到所有圖片連結，並排序（假設名稱規律）
    image_links = [link.get('href') for link in soup.find_all('a') if link.get('href') and link.get('href').endswith('.jpg')]
    image_links.sort()  # 按名稱升序排序

    if image_links:
        # 獲取最新圖片的 URL
        latest_image = image_links[-1]
        image_url = urljoin(base_url, latest_image)
        image_name = os.path.basename(latest_image)

        # 本地存檔路徑
        save_path = os.path.join(image_folder, image_name)

        # 下載最新圖片
        response = requests.get(image_url)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            print(f"下載最新圖片: {image_name}")
        else:
            print("下載最新圖片失敗。")
    else:
        print("伺服器上未找到圖片。")

# 圖片預處理函數
def load_and_preprocess_image(image_path, target_size):
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # 轉換到 RGB
    img = cv2.resize(img, target_size)         # 調整大小
    img = keras.applications.imagenet_utils.preprocess_input(img)  # 預處理
    img = np.expand_dims(img, axis=0)          # 添加 batch 維度
    return img

# 獲取資料夾中最新圖片
def get_latest_image(image_folder='images'):
    image_files = glob.glob(os.path.join(image_folder, '*.jpg'))
    if not image_files:
        return None
    latest_image = max(image_files, key=os.path.getmtime)
    return latest_image

# 模型預測函數
def predict_class(model, img):
    predictions = model.predict(img)
    pred_label = np.argmax(predictions, axis=1)[0]  # 獲取預測類別
    return pred_label, predictions

# Saliency Map 計算並轉成 Base64
def compute_saliency_map_base64(model, img):
    images = tf.Variable(img, dtype=float)
    with tf.GradientTape() as tape:
        pred = model(images, training=False)
        class_idx = np.argmax(pred.numpy())
        loss = pred[0][class_idx]
    grads = tape.gradient(loss, images)
    dgrad_abs = tf.math.abs(grads)
    dgrad_max_ = np.max(dgrad_abs, axis=3)[0]
    grad_eval = (dgrad_max_ - np.min(dgrad_max_)) / (np.max(dgrad_max_) - np.min(dgrad_max_) + 1e-18)

    # 將 Saliency Map 轉換為圖片並存為 Base64
    buffer = BytesIO()
    plt.imsave(buffer, grad_eval, format='png', cmap='jet')
    buffer.seek(0)
    saliency_map_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    buffer.close()
    return saliency_map_base64


# 傳送分類結果到 RPi
def send_classification_to_RPi(classification, host, port):
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                print(f"嘗試連接到 {host}:{port}")
                client_socket.settimeout(5)  # 設置超時時間
                client_socket.connect((host, port))
                message = str(classification) + '\n'
                print(f"發送分類結果: {message.strip()}")
                client_socket.sendall(message.encode('utf-8'))

                # 接收伺服器響應
                response = client_socket.recv(1024)
                print("收到 RPi 回覆:", response.decode())
                break  # 如果成功發送，退出循環
        except socket.timeout:
            print("連接超時，重試...")
        except ConnectionRefusedError:
            print("連接被拒絕，請檢查伺服器是否正常運行，重試...")
        except Exception as e:
            print(f"發送分類結果失敗: {e}，重試...")
        time.sleep(2)  # 等待後重試

def send_data_to_server(category, image_path, saliency_map_base64):
    try:
        # 讀取圖片並轉換為 Base64
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

        # 準備要發送的數據
        data = {
            "category": category,
            "image": encoded_image,
            "saliency_map": saliency_map_base64
        }

        # 發送 POST 請求
        response = requests.post(SERVER_URL, json=data)
        
        if response.status_code == 200:
            print(f"分類結果和圖片已發送")
            print(f"伺服器回應: {response.json()}")
        else:
            print(f"發送失敗: {response.text}")
    except Exception as e:
        print(f"發送數據出錯: {e}")

# 主程式循環
if __name__ == "__main__":
    base_url = 'http://172.20.10.13:8000/'  # Raspberry Pi 伺服器 URL
    image_folder = 'images'  # 圖像資料夾路徑
    processed_images = set()  # 已處理圖像記錄

    while True:
        try:
            # 下載新圖片
            download_images(base_url, image_folder)

            # 獲取最新圖片
            image_path = get_latest_image(image_folder)
            if image_path and image_path not in processed_images:
                print(f"檢測到新圖片: {image_path}")
                processed_images.add(image_path)  # 標記圖片為已處理

                # 加載並預測圖片
                img = load_and_preprocess_image(image_path, target_size)
                pred_label, predictions = predict_class(model, img)
                print(f"預測類別: {pred_label}")

                # 計算 Saliency Map
                saliency_map_base64 = compute_saliency_map_base64(model, img)

                # 傳送分類結果到 RPi
                send_classification_to_RPi(pred_label + 1, RPi_HOST, RPi_PORT)  # 假設分類結果為 1~5
                send_data_to_server(int(pred_label) + 1, image_path, saliency_map_base64)
                
            else:
                print("未檢測到新圖片或圖片已處理")

            # 等待下一次檢查
            time.sleep(1)

        except KeyboardInterrupt:
            print("程式中斷，退出...")
            break
        except Exception as e:
            print(f"運行出錯: {e}")
