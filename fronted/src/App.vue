<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup>
// 不需要额外逻辑
</script>

<style>
:root {
  /* 主色调 */
  --primary: #4A90D9;
  --primary-hover: #3A7BC8;
  --primary-light: #E8F0FE;
  --success: #52C41A;
  --success-light: #F6FFED;
  --error: #FF4D4F;
  --error-light: #FFF2F0;
  --warning: #FAAD14;

  /* 中性色 */
  --bg: #F5F7FA;
  --card-bg: #FFFFFF;
  --text-primary: #1A1A2E;
  --text-secondary: #666;
  --border: #E8E8E8;

  /* 圆角/阴影 */
  --radius: 12px;
  --radius-lg: 20px;
  --shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: "PingFang SC", "Microsoft YaHei", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  font-size: 16px;
  color: var(--text-primary);
  background-color: var(--bg);
  line-height: 1.6;
  min-height: 100vh;
}

#app {
  min-height: 100vh;
}

button, input, select {
  font-family: inherit;
  transition: all 0.3s ease;
}

/* 移动端全局调整 */
@media (max-width: 480px) {
  body {
    font-size: 14px;
  }
}
</style>