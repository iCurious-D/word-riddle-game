<template>
  <div class="home">
    <!-- 本轮统计卡片 -->
    <div v-if="showSummary" class="summary-card">
      <h3 class="summary-title">📊 本轮成绩</h3>
      <div class="summary-grid">
        <div class="summary-item">
          <span class="summary-num">{{ gameStore.totalQuestions }}</span>
          <span class="summary-label">做题数</span>
        </div>
        <div class="summary-item">
          <span class="summary-num">{{ gameStore.sessionCorrect }}</span>
          <span class="summary-label">答对数</span>
        </div>
        <div class="summary-item">
          <span class="summary-num">{{ gameStore.getAccuracy() }}</span>
          <span class="summary-label">正确率</span>
        </div>
        <div class="summary-item">
          <span class="summary-num">{{ gameStore.getDuration() }}</span>
          <span class="summary-label">用时</span>
        </div>
        <div class="summary-item summary-score">
          <span class="summary-num">{{ gameStore.score }}</span>
          <span class="summary-label">得分</span>
        </div>
      </div>
      <div class="summary-actions">
        <button class="btn btn-outline btn-dismiss" @click="dismissSummary">知道了</button>
        <button class="btn btn-primary btn-share" @click="generateShareImage">分享成绩</button>
      </div>
    </div>

    <!-- 分享图片弹窗 -->
    <div v-if="showShareImage" class="share-overlay" @click.self="showShareImage = false">
      <div class="share-modal">
        <img :src="shareImageUrl" class="share-preview" alt="成绩分享图" />
        <div class="share-actions">
          <a :href="shareImageUrl" :download="'字谜成绩.png'" class="btn btn-primary btn-save">保存图片</a>
          <button class="btn btn-outline" @click="showShareImage = false">关闭</button>
        </div>
      </div>
    </div>

    <div class="header">
      <h1 class="title">字谜挑战</h1>
      <p class="subtitle">选择你的挑战难度，开始字谜之旅</p>
    </div>

    <div class="card">
      <div class="form-row">
        <label class="form-label">教材版本</label>
        <select v-model="selectedPublisher" class="form-select">
          <option value="">全部教材</option>
          <option v-for="pub in publishers" :key="pub" :value="pub">{{ pub }}</option>
        </select>
      </div>

      <div class="form-row">
        <label class="form-label">年级</label>
        <select v-model="selectedGrade" class="form-select">
          <option :value="0">全部年级</option>
          <option v-for="g in grades" :key="g" :value="g">{{ g }}年级</option>
        </select>
      </div>

      <div class="form-row">
        <label class="form-label">学期</label>
        <select v-model="selectedTerm" class="form-select">
          <option :value="0">全部学期</option>
          <option :value="1">上学期</option>
          <option :value="2">下学期</option>
        </select>
      </div>

      <div class="actions">
        <button class="btn btn-primary" @click="startGame">开始游戏</button>
        <button class="btn btn-outline" @click="resetRecords">清除记录</button>
      </div>
    </div>

    <div class="extra-links">
      <button class="link-btn" @click="$router.push('/submit')">📝 上传字谜</button>
      <button class="link-btn" @click="$router.push('/admin')">⚙️ 管理后台</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useGameStore } from '@/stores/game'
import axios from 'axios'

const router = useRouter()
const gameStore = useGameStore()

const publishers = ref([])
const grades = ref([])
const selectedPublisher = ref('')
const selectedGrade = ref(0)
const selectedTerm = ref(0)

const showSummary = ref(false)
const showShareImage = ref(false)
const shareImageUrl = ref('')

onMounted(async () => {
  // 检查是否有本轮统计数据
  if (gameStore.hasSessionData() && gameStore.sessionEndTime) {
    showSummary.value = true
  }
  try {
    const res = await axios.get('/api/textbooks')
    publishers.value = res.data.publishers
    grades.value = res.data.grades
  } catch (err) {
    console.error(err)
  }
})

function dismissSummary() {
  showSummary.value = false
  // 重置统计，避免下次再显示
  gameStore.startSession()
}

function startGame() {
  gameStore.setOptions(selectedPublisher.value, selectedGrade.value, selectedTerm.value)
  router.push('/game')
}

function resetRecords() {
  gameStore.setOptions(selectedPublisher.value, selectedGrade.value, selectedTerm.value)
  gameStore.resetSeenIds()
  alert('已清除当前选择的做题记录')
}

function generateShareImage() {
  const canvas = document.createElement('canvas')
  const dpr = 2  // 高清
  const W = 360 * dpr
  const H = 520 * dpr
  canvas.width = W
  canvas.height = H
  const ctx = canvas.getContext('2d')
  ctx.scale(dpr, dpr)

  // 背景渐变
  const grad = ctx.createLinearGradient(0, 0, 0, 520)
  grad.addColorStop(0, '#667eea')
  grad.addColorStop(1, '#764ba2')
  ctx.fillStyle = grad
  ctx.beginPath()
  ctx.roundRect(0, 0, 360, 520, 16)
  ctx.fill()

  // 白色内卡
  ctx.fillStyle = 'rgba(255,255,255,0.95)'
  ctx.beginPath()
  ctx.roundRect(20, 80, 320, 360, 12)
  ctx.fill()

  // 标题
  ctx.fillStyle = '#fff'
  ctx.font = 'bold 22px sans-serif'
  ctx.textAlign = 'center'
  ctx.fillText('📊 字谜挑战成绩', 180, 55)

  // 得分大字
  ctx.fillStyle = '#667eea'
  ctx.font = 'bold 56px sans-serif'
  ctx.fillText(String(gameStore.score), 180, 155)
  ctx.fillStyle = '#999'
  ctx.font = '14px sans-serif'
  ctx.fillText('得分', 180, 175)

  // 分隔线
  ctx.strokeStyle = '#eee'
  ctx.lineWidth = 1
  ctx.beginPath()
  ctx.moveTo(50, 195)
  ctx.lineTo(310, 195)
  ctx.stroke()

  // 四项数据
  const stats = [
    { label: '做题数', value: String(gameStore.totalQuestions) },
    { label: '答对数', value: String(gameStore.sessionCorrect) },
    { label: '正确率', value: gameStore.getAccuracy() },
    { label: '用时', value: gameStore.getDuration() },
  ]
  const startY = 225
  const rowH = 50
  stats.forEach((s, i) => {
    const y = startY + i * rowH
    ctx.fillStyle = '#333'
    ctx.font = 'bold 20px sans-serif'
    ctx.textAlign = 'left'
    ctx.fillText(s.value, 60, y)
    ctx.fillStyle = '#999'
    ctx.font = '13px sans-serif'
    ctx.fillText(s.label, 60, y + 20)
  })

  // 底部
  ctx.fillStyle = 'rgba(255,255,255,0.7)'
  ctx.font = '12px sans-serif'
  ctx.textAlign = 'center'
  ctx.fillText('来挑战我吧！', 180, 465)
  ctx.fillStyle = 'rgba(255,255,255,0.5)'
  ctx.font = '10px sans-serif'
  ctx.fillText('elegant-muffin-bcb717.netlify.app', 180, 485)

  shareImageUrl.value = canvas.toDataURL('image/png')
  showShareImage.value = true
}
</script>

<style scoped>
.home {
  max-width: 480px;
  margin: 0 auto;
  padding: 60px 20px 40px;
}

.header {
  text-align: center;
  margin-bottom: 36px;
}

.title {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.subtitle {
  font-size: 15px;
  color: var(--text-secondary);
}

.card {
  background: var(--card-bg);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
  padding: 32px 28px;
}

.form-row {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.form-label {
  width: 80px;
  font-size: 15px;
  color: var(--text-secondary);
  flex-shrink: 0;
}

.form-select {
  flex: 1;
  height: 44px;
  padding: 0 14px;
  font-size: 15px;
  color: var(--text-primary);
  background: var(--bg);
  border: 1.5px solid var(--border);
  border-radius: var(--radius);
  outline: none;
  appearance: none;
  cursor: pointer;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23666' d='M6 8L1 3h10z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 14px center;
}

.form-select:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(74, 144, 217, 0.15);
}

.actions {
  display: flex;
  gap: 12px;
  margin-top: 28px;
}

.btn {
  flex: 1;
  height: 46px;
  font-size: 16px;
  font-weight: 600;
  border-radius: var(--radius);
  cursor: pointer;
  border: none;
}

.btn-primary {
  background: var(--primary);
  color: #fff;
}

.btn-primary:hover {
  background: var(--primary-hover);
}

.btn-outline {
  background: var(--card-bg);
  color: var(--primary);
  border: 1.5px solid var(--primary);
}

.btn-outline:hover {
  background: var(--primary-light);
}

/* 额外链接 */
.extra-links {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 16px;
}

.link-btn {
  background: none;
  border: none;
  font-size: 13px;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 4px 0;
  transition: color 0.2s;
}

.link-btn:hover {
  color: var(--primary);
}

/* 本轮统计卡片 */
.summary-card {
  background: var(--card-bg);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
  padding: 24px 28px;
  margin-bottom: 24px;
  animation: slideDown 0.4s ease;
}

.summary-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  text-align: center;
  margin: 0 0 16px 0;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.summary-item {
  text-align: center;
  background: var(--bg);
  border-radius: 10px;
  padding: 12px 8px;
}

.summary-num {
  display: block;
  font-size: 20px;
  font-weight: 700;
  color: var(--primary);
  margin-bottom: 4px;
}

.summary-label {
  font-size: 12px;
  color: var(--text-secondary);
}

.summary-score {
  grid-column: 1 / -1;
}

.summary-score .summary-num {
  font-size: 28px;
  color: var(--primary);
}

.btn-dismiss {
  width: 100%;
  height: 40px;
  font-size: 14px;
}

.summary-actions {
  display: flex;
  gap: 10px;
}

.summary-actions .btn {
  flex: 1;
  height: 40px;
  font-size: 14px;
}

.btn-share {
  background: var(--primary);
  color: #fff;
}

/* 分享图片弹窗 */
.share-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.share-modal {
  background: var(--card-bg);
  border-radius: var(--radius-lg);
  padding: 20px;
  max-width: 360px;
  width: 100%;
  text-align: center;
}

.share-preview {
  width: 100%;
  border-radius: 8px;
  margin-bottom: 16px;
}

.share-actions {
  display: flex;
  gap: 10px;
}

.share-actions .btn {
  flex: 1;
  height: 40px;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
}

.btn-save {
  background: var(--primary);
  color: #fff;
  border-radius: var(--radius);
}

@keyframes slideDown {
  from { opacity: 0; transform: translateY(-12px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 移动端适配 */
@media (max-width: 480px) {
  .home {
    padding: 32px 16px 24px;
  }

  .header {
    margin-bottom: 24px;
  }

  .title {
    font-size: 24px;
  }

  .subtitle {
    font-size: 13px;
  }

  .card {
    padding: 20px 16px;
  }

  .form-label {
    width: 64px;
    font-size: 14px;
  }

  .form-select {
    height: 48px;
    font-size: 16px; /* 防止 iOS 自动缩放 */
  }

  .btn {
    height: 50px;
    font-size: 15px;
  }

  .summary-card {
    padding: 18px 16px;
    margin-bottom: 18px;
  }

  .summary-title {
    font-size: 16px;
  }

  .summary-num {
    font-size: 17px;
  }

  .summary-score .summary-num {
    font-size: 24px;
  }
}
</style>