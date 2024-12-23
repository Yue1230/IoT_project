# 前端視覺化專案說明

此專案基於 React 開發，結合 WebSocket 技術，實現分類結果的即時展示與統計視覺化功能，適用於缺陷分類和 Saliency Map 的顯示。

---

##  網頁連結
Add front-end app: https://yue1230.github.io/IoT_project/

---

## 關鍵功能

- **WebSocket 通信**：與後端實時通信，接收分類圖片、顯著圖（Saliency Map）、分類結果及統計數據。
- **動態數據渲染**：即時更新分類圖片和對應數據。
- **互動視覺化**：整合條形圖與圓餅圖展示統計信息。
- **UI 優化**：響應式設計，支持多設備顯示。

---

## 文件結構

```
Frontend/
├── public/
├── src/
│   ├── App.js        # 主應用邏輯
│   ├── App.css       # 核心樣式
│   ├── Chart.js      # 條形圖元件
│   ├── PieChart.js   # 圓餅圖元件
│   └── index.js      # React 進入點
├── pakage-lock.json
├── package.json 
```

---

## 核心功能說明

### WebSocket 通信

- **伺服器地址**：`http://host:port`
- **事件監聽**：
  - `update_data`：接收分類結果、圖片與 Saliency Map。
  - `update_stats`：接收統計數據。

### 動態數據渲染

- **分類圖片與描述**：
  - 圖片來源使用 base64 編碼。
  - 根據分類結果顯示對應缺陷描述。

- **Saliency Map 顯示**：
  - 支持與分類圖片並排顯示。

- **統計與進度視覺化**：
  - 條形圖顯示分類數據。
  - 圓餅圖展示完成進度。

---

## 樣式與互動設計

- **主要容器**：
  - `.image-saliency-container`：分類圖片與顯著圖的並排展示。
  - `.charts-container`：統計與進度圖表的展示。

- **動態效果**：
  - 鼠標懸停時卡片浮動效果。
  - 等待數據時的動畫提示。

---

## 啟動方式

### 1. 安裝相依套件

使用 npm 安裝專案依賴：

```bash
npm install
```

### 2. 啟動開發伺服器

啟動本地開發伺服器，檢視專案：

```bash
npm start
```

伺服器啟動後，可在瀏覽器中訪問 `http://localhost:3000`。

---

