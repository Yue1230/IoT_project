# 缺陷檢測及數據傳輸

基於 TensorFlow 和 OpenCV，實現圖像分類、Saliency Map 計算，並通過網路傳輸數據至伺服器與 Raspberry Pi。

## 關鍵功能

1. **圖像下載與處理**：
   - 從指定 URL 下載最新圖像。
   - 將圖像進行預處理，適配模型輸入。

2. **模型預測與 Saliency Map 生成**：
   - 使用 TensorFlow 加載預訓練模型，對圖像進行分類。
   - 基於 GradientTape 計算 Saliency Map 並轉換為 Base64。

3. **數據傳輸**：
   - 將分類結果和 Saliency Map 傳輸至 Flask 伺服器。
   - 通過 Socket 傳遞分類結果至 Raspberry Pi。

4. **錯誤處理與重試機制**：
   - 在網絡通信失敗時，自動重試連接。
   - 詳細的錯誤日誌記錄。

---

## 文件結構

```
PC/
├── model.h5                # 預訓練模型文件
├── main.py                 # 主程式
```

---

## 系統依賴

### 1. Python 版本
- Python 3.8 或更高版本

### 2. 安裝所需套件

使用 pip 安裝必要的依賴：

```bash
pip install tensorflow opencv-python requests beautifulsoup4 matplotlib
```

---

## 使用方式

### 1. 配置參數

在主程式 (`main.py`) 中，配置以下參數：
- **伺服器地址**：`SERVER_URL`，例如 `http://<flask_server_ip>:port/classify`。
- **Raspberry Pi 地址**：`RPi_HOST` 和 `RPi_PORT`。
- **圖像來源 URL**：`base_url`。

### 2. 運行程式

啟動主程式：

```bash
python main.py
```

### 3. 運行結果

- 系統將下載最新圖像並進行分類。
- 計算 Saliency Map，並將結果發送至伺服器與 Raspberry Pi。
- 分類與 Saliency Map 的結果將顯示於終端。

---

## 模型說明

### 模型路徑

預訓練模型應保存在 `model.h5` 中。
- [Download model.h5 from Google Drive](https://drive.google.com/file/d/12MZbANG89C-afBirAZgldY6KPROiLqut/view)

### 輸入與輸出

- **輸入**：尺寸為 `(288, 288, 3)` 的圖像。
- **輸出**：分類概率向量。

---

## 日誌與錯誤處理

### 日誌輸出

- 圖像下載成功與失敗的日誌。
- 模型預測結果與分類類別。
- Saliency Map 計算與傳輸狀態。

### 錯誤處理

- 在網絡連接失敗時，系統會自動重試。
- 支援鍵盤中斷 (`Ctrl+C`) 安全退出。

---

## 注意事項

1. 確保伺服器地址和 Raspberry Pi 地址可用。
2. 圖像來源 URL 必須包含圖片列表，且支持 HTTP 請求。
3. 預訓練模型需符合輸入規格，否則可能導致錯誤。

---

## 聯繫方式

如果有任何疑問，請聯繫：[您的姓名](mailto:您的郵箱)。
