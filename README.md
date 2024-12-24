# 基於物聯網的智慧缺陷檢測與機械手臂分類系統

此專案結合深度學習與物聯網技術，設計一個智慧缺陷檢測與機械手臂分類系統，適用於工業製造中的品質控制與自動化操作。透過 CNN 模型進行缺陷檢測，並結合Rasberry Pi、Arduino 與機械手臂實現物料的準確分類。此系統目的在提升製造效率、減少人工干預並確保產品品質。

---

## 專案目錄結構

```
project/
├── Digital Twin         # 數位孿生相關資源與實作
├── Frontend             # 前端程式碼
├── Backend              # 後端程式碼
├── PC                   # 電腦端缺陷模型處裡
├── Rasberry Pi          # 樹莓派相關腳本
├── .gitattributes       # Git 屬性文件
├── README.md            # 專案說明文件
```

---

## 核心模組與功能

### 1. **數位孿生 (Digital Twin)**
- 使用 Unity 建構工業生產的虛擬場景，模擬機械手臂操作與缺陷分類流程。
- 實現物理系統與虛擬模型的同步，通過 TCP 通信（5002、5003 埠）實現實時數據傳輸。
- 增強系統透明度，支持操作模擬與生產優化。

### 2. **前端 (Front-end)**
- 使用 React 開發，用於數據可視化和遠端監控。
- 實時顯示缺陷檢測結果、分類統計與生產數據。

### 3. **後端 (Back-end)**
- 使用 Flask 開發，實現分類結果處理、圖片與 Saliency Map 的存儲。
- 使用Websocket達到數據的實時廣播。

### 4. **電腦端 (PC)**
- 使用 TensorFlow 架構的 CNN 模型進行缺陷檢測。
- 基於 EfficientNet 進行遷移學習，實現多類型缺陷的高準確率檢測。

### 5. **樹莓派 (Raspberry Pi)**
- 實現超聲波檢測與相機拍攝功能，確保物料定位與影像捕捉的準確性。
- 負責與 PC 和 Arduino 之間的數據通訊。

### 6. **機械手臂控制**
- 配備六自由度機械手臂，使用伺服馬達和 PCA9685 驅動板實現高精度動作控制。
- 根據分類結果將物料準確放置至指定區域。

---

## 資源鏈接與說明

- **主要程式碼**:
  - 缺陷檢測：[`PC/main.py`](https://github.com/Yue1230/IoT_project/blob/main/PC/main.py)
  - 前端：[`Frontend/src/App.js`](https://github.com/Yue1230/IoT_project/blob/main/Frontend/src/App.js)
  - 後端：[`backend.py`](https://github.com/Yue1230/IoT_project/blob/main/Backend/backend.py)
  - 樹莓派：[`camera.py`](https://github.com/Yue1230/IoT_project/blob/main/Rasberry%20Pi/camera.py)
  [`robot.py`](https://github.com/Yue1230/IoT_project/blob/main/Rasberry%20Pi/robot.py)
  - 數字孿生：[`Unity`](https://reurl.cc/46jey3)

- **報告文件**:
  - 專案報告：[`IoT_project.pdf`](https://drive.google.com/file/d/1YnGLvVpFJfwUTbgSdwhTG09hL9BHeSRv/view?usp=sharing)
  - Demo Video: [`IoT_Project Video`](https://drive.google.com/file/d/10WVgfGhtrSy46MkUgc-l3Ab0iV0Z2K4a/view)
---

## 部署與啟動

### 1. **環境準備**
- 安裝必要的 Python 套件：
  ```bash
  pip install tensorflow flask react
  ```

### 2. **啟動伺服器**
- 運行樹莓派腳本：
  ```bash
  python Rasberry\ Pi/camera.py
  python Rasberry\ Pi/robot.py
  ```
- 啟動電腦端分類與模型處理：
  ```bash
  python PC/main.py
  ```

### 3. **啟動前端**
- 進入 `Frontend` 資料夾，運行：
  ```bash
  npm install
  npm start
  ```
### 3. **啟動後端**
- 進入 `Backend` 資料夾，運行：
  ```bash
  python backend.py
  ```
---

## 聯繫方式

如有任何疑問，請聯繫：[Zheng Lin Wu](mailto:r12522636@g.ntu.edu.tw) 或 [Yue Zhang](mailto:r13522739@g.ntu.edu.tw)。
