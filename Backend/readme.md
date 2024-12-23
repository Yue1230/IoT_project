# 後端：Flask + Socket.IO 分類結果服務器說明

此專案基於 Flask 和 Socket.IO，實現分類結果處理、圖片與 Saliency Map 的存儲，以及數據的實時廣播。

## 關鍵功能

1. **分類結果處理**：接收前端發送的分類數據，並更新分類統計。
2. **圖片與 Saliency Map 存儲**：將接收到的圖片和 Saliency Map 解碼並保存到指定目錄中。
3. **實時數據廣播**：通過 WebSocket 將最新數據廣播給前端。
4. **統計數據查詢**：提供分類統計數據的查詢介面。

---

## 文件結構

```
project/
├── backend.py            # 主服務器代碼
├── uploaded_images/  # 上傳圖片存儲目錄
├── saliency_maps/    # Saliency Map 存儲目錄
```

---

## API 說明

### 1. `/classify` (POST)
- **功能**：接收分類結果、圖片和 Saliency Map，更新分類統計並廣播給前端。
- **請求參數**：
  - `category` (int)：分類類別。
  - `image` (string, base64)：圖片數據（選填）。
  - `saliency_map` (string, base64)：Saliency Map 數據（選填）。
- **回應**：
  ```json
  {
    "status": "success",
    "stats": {
      "0": 5,
      "1": 3,
      ...
    },
    "message": "數據處理成功"
  }
  ```

### 2. `/stats` (GET)
- **功能**：返回當前分類統計數據。
- **回應**：
  ```json
  {
    "0": 5,
    "1": 3,
    ...
  }
  ```

---

## WebSocket 事件

### 1. `connect`
- **功能**：客戶端連接時，發送當前分類統計數據。
- **發送數據**：
  ```json
  {
    "0": 5,
    "1": 3,
    ...
  }
  ```

### 2. `update_data`
- **功能**：廣播最新的分類數據、圖片和 Saliency Map。
- **發送數據**：
  ```json
  {
    "stats": {
      "0": 5,
      "1": 3,
      ...
    },
    "image": "<base64-encoded-image>",
    "category": 2,
    "saliency_map": "<base64-encoded-saliency-map>"
  }
  ```

---

## 運行方式

### 1. 安裝依賴

使用 pip 安裝必要套件：

```bash
pip install flask flask-socketio
```

### 2. 啟動服務器

運行以下命令啟動服務器：

```bash
python backend.py
```

服務器將在指定的 IP 地址和端口上運行，例如：`http://host:port`

### 3. 文件目錄設置

確保以下目錄存在，並具有可寫權限：
- `uploaded_images/`：用於存儲上傳的分類圖片。
- `saliency_maps/`：用於存儲 Saliency Map。

---

## 注意事項

- **IP 地址設置**：請確保服務器的 IP 地址和端口配置正確，並在本地網絡中可訪問。
- **數據驗證**：服務端對接收到的數據進行基本的驗證，避免不完整或錯誤數據導致問題。

---

## 聯繫方式

如果有任何疑問，請聯繫：[您的姓名](mailto:您的郵箱)。
