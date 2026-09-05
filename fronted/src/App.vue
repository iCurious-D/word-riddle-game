<template>
  <div id="app">
    <router-view />

    <!-- 全局成就解锁提示（底部，避免与页面顶部 toast 重叠） -->
    <Transition name="achv">
      <div v-if="achievementStore.toastVisible" class="achievement-toast">
        {{ achievementStore.toastMessage }}
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { useAchievementStore } from '@/stores/achievement'
const achievementStore = useAchievementStore()
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

/* 成就解锁提示 */
.achievement-toast {
  position: fixed;
  bottom: 30px;
  left: 50%;
  transform: translateX(-50%);
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
  font-size: 15px;
  font-weight: 700;
  padding: 12px 26px;
  border-radius: 30px;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
  z-index: 1000;
  white-space: nowrap;
}

.achv-enter-active {
  animation: achvIn 0.4s ease;
}

.achv-leave-active {
  animation: achvOut 0.4s ease;
}

@keyframes achvIn {
  from { opacity: 0; transform: translateX(-50%) translateY(30px) scale(0.8); }
  to { opacity: 1; transform: translateX(-50%) translateY(0) scale(1); }
}

@keyframes achvOut {
  from { opacity: 1; transform: translateX(-50%) translateY(0) scale(1); }
  to { opacity: 0; transform: translateX(-50%) translateY(20px) scale(0.9); }
}
</style>