import RPi.GPIO as GPIO
import time
from picamera2 import Picamera2
from datetime import datetime
import socket
import threading
import serial

# GPIO 引腳設置
SIG = 22  # GPIO 引腳連接到 SIG 引腳
GPIO.setmode(GPIO.BCM)
GPIO.setup(SIG, GPIO.OUT)  # 初始將 SIG 設為輸出模式

# 初始化相機
picam2 = Picamera2()
camera_config = picam2.create_preview_configuration()
picam2.configure(camera_config)
picam2.start()

# 初始化串口（更新為 Arduino 的對應端口）
ser = serial.Serial('/dev/ttyUSB0', baudrate=9600, timeout=1)  # 根據 Arduino 的連接進行修改

# 初始化參數
threshold = 7  # 距離閾值（單位：厘米）
duration = 2  # 持續時間閾值（單位：秒）
start_time = None
object_detected = False
wait_for_clear = False
clear_count = 0  # 計數器，用於確認物體已清空
clear_threshold = 3  # 連續讀數超過閾值的次數，以確認物體清空
post_action_delay = 5  # 操作完成後的延遲時間（單位：秒）

# TCP 伺服器設置
TCP_HOST = '10.0.0.101'  # 替換為你的 Raspberry Pi IP 地址
TCP_PORT = 5002

client_socket = None

# 距離緩衝區，用於平滑數據
distance_buffer = []  # 最近距離讀數的緩衝區
buffer_size = 5  # 移動平均窗口大小

def measure_distance():
    """使用 Grove 超聲波傳感器測量距離。"""
    try:
        GPIO.setup(SIG, GPIO.OUT)
        GPIO.output(SIG, False)
        time.sleep(0.00001)  # 確保穩定的低電平信號
        GPIO.output(SIG, True)
        time.sleep(0.00001)  # 發送 10 微秒的脈衝
        GPIO.output(SIG, False)

        GPIO.setup(SIG, GPIO.IN)
        pulse_start = pulse_end = None

        start_time = time.time()
        while GPIO.input(SIG) == 0:
            pulse_start = time.time()
            if pulse_start - start_time > 0.01:
                return -1

        start_time = time.time()
        while GPIO.input(SIG) == 1:
            pulse_end = time.time()
            if pulse_end - start_time > 0.01:
                return -1

        if pulse_start is None or pulse_end is None:
            return -1

        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150  # 轉換為厘米
        return round(distance, 2)

    except Exception as e:
        print(f"[錯誤] 距離測量失敗: {e}")
        return -1

def start_tcp_server():
    global client_socket
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((TCP_HOST, TCP_PORT))
        server_socket.listen(1)
        print(f"[TCP] 伺服器正在監聽 {TCP_HOST}:{TCP_PORT}")

        client_socket, client_address = server_socket.accept()
        print(f"[TCP] 客戶端已連接: {client_address}")
    except Exception as e:
        print(f"[TCP] 伺服器錯誤: {e}")

def send_command(command):
    """向連接的客戶端發送指令。"""
    global client_socket
    try:
        if client_socket:
            client_socket.sendall(command.encode())
            print(f"[TCP] 發送指令: {command}")
    except Exception as e:
        print(f"[TCP] 發送指令時發生錯誤: {e}")
        client_socket = None  # 如果出現錯誤，重置客戶端 socket

# 在執行緒中啟動 TCP 伺服器
tcp_server_thread = threading.Thread(target=start_tcp_server, daemon=True)
tcp_server_thread.start()

# 添加計數器
below_threshold_count = 0  # 連續小於閾值的計數
above_threshold_count = 0  # 連續大於閾值的計數
required_below_count = 5  # 連續小於閾值的次數要求
required_above_count = 5  # 連續大於閾值的次數要求

try:
    while True:
        distance = measure_distance()
        if distance == -1:
            print("測量失敗")
            continue

        print(f"測得距離: {distance} cm")

        # 如果處於等待物體清空狀態
        if wait_for_clear:
            if distance > threshold:
                above_threshold_count += 1
                if above_threshold_count >= required_above_count:  # 需要連續多次大於閾值
                    print("物體已清空，準備進行下一次檢測。")
                    wait_for_clear = False  # 重置標誌位，準備下一次檢測
                    above_threshold_count = 0  # 重置計數器
            else:
                above_threshold_count = 0  # 重置計數器
            time.sleep(0.1)
            continue

        # 檢查距離是否低於閾值
        if distance < threshold:
            below_threshold_count += 1
            if below_threshold_count >= required_below_count:  # 需要連續多次小於閾值
                if not object_detected:  # 物體剛剛進入檢測範圍
                    time.sleep(2)  # 延遲確認
                    ser.write(b'0\n')  # 發送停止指令到 Arduino
                    send_command("2")  # 發送停止指令到 Unity
                    print("已發送 STOP 指令到 Arduino 和 Unity")
                    object_detected = True  # 標記物體已被檢測到

                # 如果尚未開始計時，則啟動計時
                if start_time is None:
                    start_time = datetime.now()

                elapsed_time = (datetime.now() - start_time).total_seconds()
                if elapsed_time >= duration:  # 如果物體在範圍內持續足夠長時間
                    print("拍攝照片")
                    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
                    file = f"/home/johnny/IoT_Project/images/{current_time}.jpg"
                    picam2.capture_file(file)
                    print(f"照片已保存: {file}")

                    ser.write(b'1\n')  # 發送啟動指令到 Arduino
                    send_command("1")  # 發送啟動指令到 Unity
                    print("已發送 START 指令到 Arduino 和 Unity")
                    object_detected = False  # 標記物體未被檢測到
                    start_time = None  # 在拍攝照片後重置計時器
                    wait_for_clear = True  # 設置標誌位，等待物體離開範圍
            above_threshold_count = 0  # 重置計數器
        else:
            below_threshold_count = 0  # 重置計數器
            if object_detected:  # 如果之前檢測到物體
                above_threshold_count += 1
                if above_threshold_count >= required_above_count:  # 需要連續多次大於閾值
                    ser.write(b'1\n')  # 發送啟動指令到 Arduino
                    send_command("1")  # 發送啟動指令到 Unity
                    print("已發送 START 指令到 Arduino 和 Unity")
                    object_detected = False  # 標記物體未被檢測到
                    above_threshold_count = 0  # 重置計數器
            else:
                above_threshold_count = 0  # 重置計數器

        time.sleep(0.1)  # 每次測量之間的延遲
finally:
    GPIO.cleanup()  # 釋放 GPIO 資源
    ser.close()  # 關閉串口連接
