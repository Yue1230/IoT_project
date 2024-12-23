import time
import socket
from adafruit_servokit import ServoKit
import RPi.GPIO as GPIO
import threading
import serial
ser = serial.Serial('/dev/ttyUSB0', baudrate=9600, timeout=1)  # 修改為 Arduino 的 USB 串口

# GPIO 引腳設定
TRIG = 17  # GPIO17 (Pin 11)
ECHO = 27  # GPIO27 (Pin 13)

# 超聲波相關設定
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# 初始化 ServoKit，支援 16 通道
kit = ServoKit(channels=16)

# 定義每個舵機的通道
SHOULDER_SERVO_1 = 0  # 肩膀舵機 1
SHOULDER_SERVO_2 = 1  # 肩膀舵機 2（反向）
ELBOW_SERVO = 2       # 手肘舵機
WRIST_SERVO = 3       # 手腕舵機
GRIPPER_SERVO = 4     # 夾爪舵機
BASE_SERVO = 5        # 底座舵機

# 定義每個舵機的最小值和最大值
shoulder_min, shoulder_max = 0, 180
elbow_min, elbow_max = 0, 180
wrist_min, wrist_max = 0, 180
gripper_min, gripper_max = 20, 100
base_min, base_max = 0, 180

# A 點（目標點的初始角度）和 Reset 點（復位角度）
A_POINT_ANGLES = [55, 180 - 55, 0, 170, 90, 82]  # A 點：肩膀、手肘、手腕、夾爪、底座
RESET_ANGLES = [90, 90, 100, 90, 20, 82]  # Reset 點：肩膀、手肘、手腕、夾爪、底座

# 目標點角度設定（分類點 0、1、2、3、4）
TARGET_POINTS = [
    [26, 180 - 26, 0, 180, 90, 180],  # 0 點
    [26, 180 - 26, 0, 180, 90, 160],  # 1 點
    [26, 180 - 26, 0, 180, 90, 140],  # 2 點
    [26, 180 - 26, 0, 180, 90, 120],  # 3 點
    [26, 180 - 26, 0, 180, 90, 100],  # 4 點
    [26, 180 - 26, 0, 180, 90, 110]  # 5 點
]

# 平滑移動舵機
def gradual_move(servo, start_angle, end_angle):
    step = 1 if end_angle > start_angle else -1
    for angle in range(start_angle, end_angle + step, step):
        servo.angle = angle
        print(f"舵機 {servo}: 當前角度 {angle}")
        time.sleep(0.02)

# 同步移動肩部舵機
def move_shoulders(start_angle1, end_angle1, start_angle2, end_angle2):
    print(f"肩部開始移動: 從({start_angle1}, {start_angle2}) 到 ({end_angle1}, {end_angle2})")
    step = 1 if end_angle1 > start_angle1 else -1
    step2 = 1 if end_angle2 > start_angle2 else -1

    for angle1, angle2 in zip(
        range(start_angle1, end_angle1 + step, step),
        range(start_angle2, end_angle2 + step2, step2)
    ):
        try:
            kit.servo[SHOULDER_SERVO_1].angle = angle1
            kit.servo[SHOULDER_SERVO_2].angle = angle2
            print(f"肩部同步: Servo1={angle1}, Servo2={angle2}")
            time.sleep(0.02)
        except Exception as e:
            print(f"肩部舵機移動失敗: {e}")

    # 確保舵機最終位置準確
    kit.servo[SHOULDER_SERVO_1].angle = end_angle1
    kit.servo[SHOULDER_SERVO_2].angle = end_angle2
    print(f"肩部移動完成: Servo1={end_angle1}, Servo2={end_angle2}")

# 抬高手臂動作
def lift_object():
    print("抬高手臂...")
    # 抬高手臂 (肩膀到 70°，手腕到 160°)
    gradual_move(kit.servo[SHOULDER_SERVO_1], A_POINT_ANGLES[0], 80)  # 肩膀
    gradual_move(kit.servo[SHOULDER_SERVO_2], 180 - A_POINT_ANGLES[0], 180 - 80)  # 反向肩膀
    gradual_move(kit.servo[WRIST_SERVO], A_POINT_ANGLES[3], 150)  # 手腕
    print("手臂已抬高")

# 移動到目標分類點
def move_to_target_point(target_index):
    print(f"移動到分類點 {target_index + 1}")
    
    lift_object()  # 抬高手臂動作
    gradual_move(kit.servo[BASE_SERVO], A_POINT_ANGLES[5], TARGET_POINTS[target_index][5])  # 移動底座
    gradual_move(kit.servo[WRIST_SERVO], 150, TARGET_POINTS[target_index][3])  # 移動腕部
    gradual_move(kit.servo[ELBOW_SERVO], 0, TARGET_POINTS[target_index][2])  # 移動手肘
    move_shoulders(80, TARGET_POINTS[target_index][0], 180 - 80, TARGET_POINTS[target_index][1])  # 移動肩膀

    # 打開夾具釋放物體
    gradual_move(kit.servo[GRIPPER_SERVO], TARGET_POINTS[target_index][4], 20)  
    print(f"分類點 {target_index + 1} 的操作完成")

    send_command(str(classification_result + 2))

    # 抬高手臂動作
    lift_object()

    # 等待 1 秒後發送啟動指令
    time.sleep(0.5)
    ser.write(b'1\n')
    print("發送啟動指令給 Arduino")

    # 返回到初始位置
    reset_to_reset_point()

# 返回到 A 點
def move_to_a_point():
    print("從 Reset 點移動到 A 點")
    # 平滑移動其他舵機
    gradual_move(kit.servo[WRIST_SERVO], RESET_ANGLES[3], A_POINT_ANGLES[3])  # 手腕
    gradual_move(kit.servo[ELBOW_SERVO], RESET_ANGLES[2], A_POINT_ANGLES[2])  # 手肘

    # 同步移動肩部舵機
    move_shoulders(RESET_ANGLES[0], A_POINT_ANGLES[0], RESET_ANGLES[1], A_POINT_ANGLES[1])

    gradual_move(kit.servo[GRIPPER_SERVO], RESET_ANGLES[4], A_POINT_ANGLES[4])  # 夾爪
    gradual_move(kit.servo[BASE_SERVO], RESET_ANGLES[5], A_POINT_ANGLES[5])  # 底座
    print("機械手臂已到達 A 點")

# 重置到 Reset 點
def reset_to_reset_point():
    move_shoulders(RESET_ANGLES[0], RESET_ANGLES[0], RESET_ANGLES[1], RESET_ANGLES[1])  # 肩膀
    gradual_move(kit.servo[ELBOW_SERVO], RESET_ANGLES[2], RESET_ANGLES[2])  # 手肘
    gradual_move(kit.servo[WRIST_SERVO], RESET_ANGLES[3], RESET_ANGLES[3])  # 手腕
    gradual_move(kit.servo[GRIPPER_SERVO], RESET_ANGLES[4], RESET_ANGLES[4])  # 夾爪
    gradual_move(kit.servo[BASE_SERVO], RESET_ANGLES[5], RESET_ANGLES[5])  # 底座

# 測量範圍和誤差設定
grip_range = 20  # 夾取範圍：物體距離小於 8 公分
threshold = 2    # 測量誤差範圍：±1 公分
measurement_time = 2  # 連續測量時間：2 秒
interval = 0.2   # 每次測量間隔：0.2 秒

def measure_distance():
    GPIO.output(TRIG, True)
    time.sleep(0.00001)  # 觸發信號持續 10µs
    GPIO.output(TRIG, False)

    start_time = None  # 初始化 start_time
    end_time = None    # 初始化 end_time

    # 等待 ECHO 信號變為高電平
    timeout = time.time() + 1  # 超時時間為 1 秒
    while GPIO.input(ECHO) == 0:
        start_time = time.time()
        if time.time() > timeout:
            print("ECHO 信號未檢測到高電平（超時）")
            return -1  # 返回 -1 表示測量失敗

    # 等待 ECHO 信號變為低電平
    timeout = time.time() + 1  # 超時時間為 1 秒
    while GPIO.input(ECHO) == 1:
        end_time = time.time()
        if time.time() > timeout:
            print("ECHO 信號未檢測到低電平（超時）")
            return -1  # 返回 -1 表示測量失敗

    if start_time is None or end_time is None:
        print("測量失敗：未檢測到有效的 ECHO 信號")
        return -1

    duration = end_time - start_time
    distance = (duration * 34300) / 2  # 單位: 公分
    return distance

def is_stable():
    consecutive_count = 0  # 記錄連續小於閾值的次數
    max_consecutive = 5    # 連續檢測次數閾值
    grip_threshold = 10    # 夾取距離的閾值（公分）

    print("開始檢測物體穩定性...")
    while consecutive_count < max_consecutive:
        distance = measure_distance()
        if distance == -1:  # 測量失敗，跳過本次檢測
            print("測量失敗，重新檢測...")
            consecutive_count = 0  # 重置連續計數
            continue

        print(f"當前距離: {distance} 公分")
        if distance < grip_threshold:  # 如果距離小於閾值
            consecutive_count += 1
            print(f"連續檢測小於閾值次數: {consecutive_count}/{max_consecutive}")
        else:
            consecutive_count = 0  # 如果檢測到大於閾值的值，重置計數
            print("檢測到大於閾值的距離，重置計數")

        time.sleep(0.2)  # 每次測量間隔 0.2 秒

    time.sleep(6)
    ser.write(b'0\n')  # 發送停止指令
    send_command("0")
    print("檢測穩定，發送停止指令到 Arduino")

    return True

# TCP 伺服器邏輯
classification_result = None
classification_lock = threading.Lock()

def start_tcp_server5003(host="10.0.0.101", port=5003): #設定您的host
    global client_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"[TCP] 伺服器正在監聽 {host}:{port}")

    client_socket, client_address = server_socket.accept()
    print(f"[TCP] 客戶端已連接: {client_address}")

def send_command(command):
    """傳送指令給已連接的客戶端。"""
    global client_socket
    try:
        if client_socket:
            client_socket.sendall(command.encode())
            print(f"[TCP] 傳送指令: {command}")
    except Exception as e:
        print(f"[TCP] 傳送指令時出現錯誤: {e}")
        client_socket = None  # 如果出現錯誤，重置客戶端 socket
        
def start_tcp_server(host="10.0.0.101", port=5000): #設定您的host
    global classification_result
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.listen(1)
        print(f"伺服器啟動，監聽 {host}:{port}")
        while True:
            client_socket, client_address = server_socket.accept()
            print(f"客戶端已連接: {client_address}")
            with client_socket:
                data = client_socket.recv(1024).decode().strip()
                if data.isdigit() and 1 <= int(data) <= 6:
                    with classification_lock:
                        classification_result = int(data)
                        client_socket.sendall(f"分類 {data} 已執行\n".encode())
                else:
                    client_socket.sendall("錯誤: 數據格式無效\n".encode())

# 在獨立執行緒中啟動 TCP 伺服器
def start_server_in_thread():
    server_thread = threading.Thread(target=start_tcp_server, daemon=True)
    server_thread.start()

# 在獨立執行緒中啟動 TCP 伺服器（5003）
def start_server_5003_in_thread():
    server_thread = threading.Thread(target=start_tcp_server5003, daemon=True)
    server_thread.start()

# 主程序
if __name__ == "__main__":
    try:
        start_server_in_thread()
        start_server_5003_in_thread()
        state = "RESET"

        while True:
            if state == "RESET":
                reset_to_reset_point()
                state = "CHECK"

            elif state == "CHECK":
                print("準備檢測物體穩定性...")

                if is_stable():
                    state = "MOVE"
                else:
                    print("物體不穩定，繼續檢測...")
                    time.sleep(0.5)  # 短暫延遲後繼續檢測

            elif state == "MOVE":
                print("移動到 A 點...")
                move_to_a_point()
                state = "WAIT"

            elif state == "WAIT":
                print("等待分類指令...")
                with classification_lock:
                    if classification_result:
                        move_to_target_point(classification_result - 1)
                        classification_result = None
                        state = "RESET"
                time.sleep(0.1)  # 避免過度佔用 CPU
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("程式中斷，重置到 Reset 點...")
        reset_to_reset_point()
        print("程式已退出")
