import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';
import Chart from './Chart';
import PieChart from './PieChart';
import './App.css';

const SOCKET_URL = 'http://172.20.10.12:5001';

// 根據分類結果取得描述
function getDefectDescription(category) {
  const defectDescriptions = {
    0: "normal",
    1: "void",
    2: "horizontal defect",
    3: "vertical defect",
    4: "edge defect",
    5: "particle",
  };

  return defectDescriptions[category] || "未知缺陷"; // 如果沒有對應分類，顯示未知缺陷
}

function App() {
  const [stats, setStats] = useState({});
  const [currentImage, setCurrentImage] = useState(null);
  const [currentCategory, setCurrentCategory] = useState(null);
  const [currentSaliencyMap, setCurrentSaliencyMap] = useState(null); // 新增狀態
  const [defectDescription, setDefectDescription] = useState(""); // 新增狀態
  const [isImageReceived, setIsImageReceived] = useState(false); // 新增状态

  useEffect(() => {
    const socket = io(SOCKET_URL);

    socket.on('connect', () => {
      console.log('WebSocket 連接成');
    });

    socket.on('update_data', (data) => {
      console.log('收到更新數據:', data);
      setStats(data.stats);
      setCurrentImage(data.image);
      setCurrentCategory(data.category);
      setCurrentSaliencyMap(data.saliency_map); // 接收 Saliency Map
      setDefectDescription(getDefectDescription(data.category)); // 新增描述更新
      setIsImageReceived(true); // 收到图片后更新状态
    });

    socket.on('update_stats', (data) => {
      console.log('收到統計數據更新:', data);
      setStats(data);
    });

    socket.on('disconnect', () => {
      console.log('WebSocket 連接斷開');
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  // 檢查數據是否為空
  const hasData = Object.keys(stats).length > 0;

  return (
    <div className="App">
      <header className="App-header">
        <h1>分類結果顯示</h1>

        <div className="content-container">
          {/* 圖片與 Saliency Map 容器 */}
          <div className="image-saliency-container">
            {/* 最新分類圖片 */}
            <div className="image-section" style={{ height: isImageReceived ? '400px' : 'auto' }}>
              <h2>最新分類圖片</h2>
              {currentImage ? (
                <div className="image-container">
                  <img 
                    src={`data:image/jpeg;base64,${currentImage}`}
                    alt="最新分類圖片"
                    style={{ maxWidth: '300px' }}
                  />
                  <p className="category-result">分類結果: {currentCategory}</p>
                  <p className="defect-description">缺陷描述: {defectDescription}</p>
                </div>
              ) : (
                <p>等待新圖片...</p>
              )}
            </div>
            {/* Saliency Map 顯示區域 */}
            <div className="saliency-map-section" style={{ height: isImageReceived ? '400px' : 'auto' }}>
              <h2>顯著圖</h2>
              {currentSaliencyMap ? (
                <div className="image-container">
                  <img
                    src={`data:image/png;base64,${currentSaliencyMap}`}
                    alt="顯著圖"
                    style={{ maxWidth: '300px' }}
                  />
                </div>
              ) : (
                <p>等待顯著圖...</p>
              )}
            </div>
          </div>

          {/* 下方圖表容器 */}
          <div className="charts-container">
            {/* 左側統計圖表 */}
            <div className="stats-section">
              <h2>分類統計</h2>
              {hasData ? (
                <div style={{ width: '100%', height: '300px' }}>
                  <Chart stats={stats} />
                </div>
              ) : (
                <p>等待數據...</p>
              )}
            </div>

            {/* 右側進度圓餅圖 */}
            <div className="progress-section">
              <h2>完成進度</h2>
              {hasData ? (
                <div style={{ width: '300px', height: '300px' }}>
                  <PieChart stats={stats} totalTarget={20} />
                </div>
              ) : (
                <p>等待數據...</p>
              )}
            </div>
          </div>
        </div>
      </header>
    </div>
  );
}

export default App;
