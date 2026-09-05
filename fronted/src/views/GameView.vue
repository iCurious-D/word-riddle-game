<template>
  <!-- Toast 弹窗 -->
  <Transition name="toast">
    <div v-if="gameStore.toastVisible" class="toast">
      🎉 {{ gameStore.toastMessage }}
    </div>
  </Transition>

  <div class="game">
    <div class="topbar">
      <button class="btn-back" @click="goHome">&larr; 返回</button>
      <div class="score-badge">
        <span class="score-label">得分</span>
        <span class="score-value">{{ gameStore.score }}</span>
      </div>
    </div>

    <div v-if="loading" class="loading">
      <div class="loading-text">加载谜题中...</div>
      <div class="fun-fact">{{ funFact }}</div>
    </div>

    <div v-else-if="error" class="error-card">{{ error }}</div>

    <div v-else-if="currentRiddle" class="game-content">
      <div class="riddle-card">
        <div class="riddle-label">谜题</div>
        <div class="riddle-text">{{ currentRiddle.question }}</div>
        <!-- 赞/踩按钮 -->
        <div class="vote-row">
          <button
            class="vote-btn"
            :class="{ 'vote-active': currentVote === 'up', 'vote-disabled': currentVote !== null }"
            @click="handleVote('up')"
            :disabled="currentVote !== null"
          >
            👍 <span class="vote-count">{{ gameStore.currentLikes }}</span>
          </button>
          <button
            class="vote-btn"
            :class="{ 'vote-active-down': currentVote === 'down', 'vote-disabled': currentVote !== null }"
            @click="handleVote('down')"
            :disabled="currentVote !== null"
          >
            👎 <span class="vote-count">{{ gameStore.currentDislikes }}</span>
          </button>
          <!-- 收藏按钮 -->
          <button
            class="vote-btn"
            :class="{ 'vote-active-fav': isFav }"
            :title="isFav ? '取消收藏' : '收藏'"
            @click="toggleFav"
          >
            {{ isFav ? '❤️' : '🤍' }}
          </button>
        </div>
      </div>

      <!-- 提示区域 -->
      <div class="hint-area" v-if="result === null">
        <button
          class="btn btn-hint"
          @click="gameStore.getHint(currentRiddle.id)"
          :disabled="gameStore.hintLevel >= 3"
        >
          💡 提示 ({{ gameStore.hintLevel }}/3)
        </button>
        <div class="hint-list" v-if="gameStore.hints.length > 0">
          <div v-for="(h, i) in gameStore.hints" :key="i" class="hint-item">
            <span class="hint-label">提示{{ i + 1 }}：</span>
            <span class="hint-text">{{ h }}</span>
          </div>
        </div>
      </div>

      <div class="answer-row">
        <input
          v-model="userAnswer"
          class="answer-input"
          placeholder="输入你的答案"
          maxlength="1"
          @keyup.enter="submitAnswer"
          :disabled="result !== null"
        />
        <button
          class="btn btn-primary btn-submit"
          @click="submitAnswer"
          :disabled="result !== null"
        >提交</button>
      </div>

      <div v-if="result !== null" class="result-wrapper">
        <!-- 撒花效果 -->
        <div v-if="result.correct" class="confetti">
          <span v-for="i in 18" :key="i" class="confetti-piece"></span>
        </div>
        <div class="result-card" :class="result.correct ? 'result-correct' : 'result-wrong'">
          <p v-if="result.correct" class="result-text">
            回答正确！+{{ gameStore.getCurrentScore() }} 分
            <span v-if="gameStore.hintLevel > 0" class="hint-deduction">（用了 {{ gameStore.hintLevel }} 次提示）</span>
          </p>
          <p v-else class="result-text">回答错误，正确答案是：<strong>{{ result.answer }}</strong></p>
        </div>
      </div>

      <!-- 汉字详情卡片 -->
      <div v-if="gameStore.charInfo && result !== null" class="char-detail">
        <h3 class="char-detail-title">📖 {{ gameStore.charInfo.char }} 的详细信息</h3>
        <div class="detail-grid">
          <div class="detail-item"><span class="detail-label">拼音</span>{{ gameStore.charInfo.pinyin || '—' }}</div>
          <div class="detail-item"><span class="detail-label">部首</span>{{ gameStore.charInfo.radical || '—' }}</div>
          <div class="detail-item"><span class="detail-label">笔画</span>{{ gameStore.charInfo.strokes ? gameStore.charInfo.strokes + ' 画' : '—' }}</div>
          <div class="detail-item"><span class="detail-label">结构</span>{{ gameStore.charInfo.structure || '—' }}</div>
          <div class="detail-item detail-item-wide"><span class="detail-label">释义</span>{{ gameStore.charInfo.meaning || '—' }}</div>
        </div>
      </div>

      <button
        v-if="result !== null"
        class="btn btn-primary btn-next"
        @click="nextRiddle"
      >下一题 &rarr;</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useGameStore } from '@/stores/game'
import { useAchievementStore } from '@/stores/achievement'
import { useFavoriteStore } from '@/stores/favorite'
import axios from 'axios'

const router = useRouter()
const gameStore = useGameStore()
const achievementStore = useAchievementStore()
const favoriteStore = useFavoriteStore()

const currentRiddle = ref(null)
const userAnswer = ref('')
const result = ref(null)
const loading = ref(true)
const error = ref('')

// 当前题的投票状态
const currentVote = computed(() => {
  if (!currentRiddle.value) return null
  return gameStore.getVoteStatus(currentRiddle.value.id)
})

// 当前题是否已收藏
const isFav = computed(() => {
  if (!currentRiddle.value) return false
  return favoriteStore.isFavorited(currentRiddle.value.id)
})

function toggleFav() {
  if (!currentRiddle.value) return
  favoriteStore.toggle(currentRiddle.value)
}

function handleVote(type) {
  if (!currentRiddle.value) return
  gameStore.voteRiddle(currentRiddle.value.id, type)
}

// 汉字小知识（loading 时随机展示）
const funFacts = [
  '“明”由“日”和“月”组成，日月同辉即为明',
  '“休”是人靠在树旁，表示休息',
  '“林”是两棵树并排，“森”是三棵树',
  '汉字中笔画最多的是“龘”(dá)，共 48 画',
  '“好”由“女”和“子”组成，女子即为好',
  '“鲜”由“鱼”和“羊”组成，鱼羊味道鲜',
  '“看”是手放在目上方，远望即为看',
  '“众”是三个人，表示很多人在一起',
  '“从”是两个人一前一后，跟从的意思',
  '“尖”上面小下面大，上小下大即为尖',
  '中国最早的汉字可以追溯到 3000 多年前的甲骨文',
  '“灾”是宝盖头下面一个火，家里着火就是灾',
]
const funFact = computed(() => funFacts[Math.floor(Math.random() * funFacts.length)])

async function fetchRiddle() {
  loading.value = true
  error.value = ''
  result.value = null
  userAnswer.value = ''
  gameStore.resetHint()
  try {
    const res = await axios.get('/api/riddles/random', {
      params: {
        grade: gameStore.grade,
        publisher: gameStore.publisher,
        term: gameStore.term,
        use_auto: true,
        exclude_ids: gameStore.getExcludeIds()
      }
    })
    if (res.data.error) {
      error.value = res.data.error
    } else {
      currentRiddle.value = res.data
      gameStore.addSeenId(res.data.id)
      // 初始化当前题的赞踩数
      gameStore.setCurrentVotes(res.data.likes || 0, res.data.dislikes || 0)
    }
  } catch (err) {
    error.value = '网络错误，请重试'
  } finally {
    loading.value = false
  }
}

async function submitAnswer() {
  if (!userAnswer.value.trim() || !currentRiddle.value) return

  const riddle = currentRiddle.value

  try {
    const res = await axios.post('/api/riddles/check', null, {
      params: {
        riddle_id: riddle.id,
        answer: userAnswer.value
      }
    })
    result.value = res.data
    gameStore.recordAttempt()  // 记录一次答题
    if (res.data.correct) {
      gameStore.addScore(gameStore.getCurrentScore())
      gameStore.recordCorrect()  // 累积答对 + 检查里程碑
      // 成就埋点：是否用过提示
      achievementStore.recordCorrect({ usedHint: gameStore.hintLevel > 0 })
    } else {
      achievementStore.recordWrong()  // 成就埋点：连对清零
    }
    // 获取答案字的详细信息
    const answerChar = res.data.correct ? userAnswer.value : res.data.answer
    if (answerChar) {
      gameStore.fetchCharInfo(answerChar)
    }
  } catch (err) {
    console.error(err)
    result.value = { correct: false, answer: '请求出错，请重试' }
  }
}

function nextRiddle() {
  fetchRiddle()
}

function goHome() {
  gameStore.endSession()  // 记录结束时间
  router.push('/')
}

onMounted(() => {
  if (!gameStore.sessionStartTime) {
    router.push('/')
    return
  }
  fetchRiddle()
})
</script>

<style scoped>
.game {
  max-width: 520px;
  margin: 0 auto;
  padding: 20px;
  min-height: 100vh;
}

.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
}

.btn-back {
  background: none;
  border: none;
  font-size: 15px;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 6px 0;
}

.btn-back:hover {
  color: var(--primary);
}

.score-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--primary-light);
  padding: 6px 16px;
  border-radius: 20px;
}

.score-label {
  font-size: 13px;
  color: var(--text-secondary);
}

.score-value {
  font-size: 18px;
  font-weight: 700;
  color: var(--primary);
}

.loading {
  text-align: center;
  padding: 60px 0;
}

.loading-text {
  color: var(--text-secondary);
  font-size: 16px;
  margin-bottom: 16px;
  animation: pulse 1.5s ease-in-out infinite;
}

.fun-fact {
  color: var(--primary);
  font-size: 14px;
  background: var(--primary-light);
  border-radius: 12px;
  padding: 12px 20px;
  max-width: 360px;
  margin: 0 auto;
  line-height: 1.6;
  animation: fadeIn 0.5s ease;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.error-card {
  text-align: center;
  padding: 24px;
  background: var(--error-light);
  color: var(--error);
  border-radius: var(--radius);
  font-size: 15px;
}

.game-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.riddle-card {
  background: var(--card-bg);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
  padding: 36px 28px;
  text-align: center;
}

.riddle-label {
  font-size: 12px;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 2px;
  margin-bottom: 16px;
}

.riddle-text {
  font-size: 26px;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.5;
}

/* 赞/踩按钮 */
.vote-row {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 16px;
}

.vote-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 16px;
  border-radius: 20px;
  border: 1.5px solid var(--border);
  background: var(--bg);
  font-size: 15px;
  cursor: pointer;
  transition: all 0.2s;
  color: var(--text-secondary);
}

.vote-btn:hover:not(:disabled) {
  border-color: var(--primary);
  background: var(--primary-light);
}

.vote-btn:disabled {
  cursor: not-allowed;
}

.vote-active {
  border-color: #10b981;
  background: #ecfdf5;
  color: #059669;
}

.vote-active-down {
  border-color: #f59e0b;
  background: #fffbeb;
  color: #d97706;
}

.vote-active-fav {
  border-color: #ef4444;
  background: #fef2f2;
}

.vote-count {
  font-size: 13px;
  font-weight: 600;
}

.answer-row {
  display: flex;
  gap: 10px;
}

.answer-input {
  flex: 1;
  height: 46px;
  padding: 0 16px;
  font-size: 17px;
  color: var(--text-primary);
  background: var(--card-bg);
  border: 1.5px solid var(--border);
  border-radius: var(--radius);
  outline: none;
}

.answer-input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(74, 144, 217, 0.15);
}

.answer-input:disabled {
  background: var(--bg);
  color: var(--text-secondary);
}

.btn {
  font-family: inherit;
  font-size: 16px;
  font-weight: 600;
  border-radius: var(--radius);
  cursor: pointer;
  border: none;
  transition: all 0.3s ease;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--primary);
  color: #fff;
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-hover);
}

.btn-submit {
  width: 80px;
  height: 46px;
  flex-shrink: 0;
}

.result-card {
  border-radius: var(--radius);
  padding: 16px 20px;
  text-align: center;
}

.result-correct {
  background: var(--success-light);
  border: 1.5px solid var(--success);
  animation: popIn 0.4s ease;
}

.result-wrong {
  background: #fffbeb;
  border: 1.5px solid #f59e0b;
  animation: shake 0.4s ease;
}

.result-text {
  font-size: 16px;
  margin: 0;
}

.result-correct .result-text {
  color: var(--success);
  font-weight: 600;
}

.result-wrong .result-text {
  color: #b45309;
}

.result-wrong .result-text strong {
  font-size: 20px;
  color: #d97706;
}

.btn-next {
  height: 48px;
  font-size: 17px;
  margin-top: 4px;
}

/* 提示区域 */
.hint-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.btn-hint {
  background: #fff8e1;
  color: #f59e0b;
  border: 1.5px solid #fcd34d;
  padding: 8px 20px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-hint:hover:not(:disabled) {
  background: #fef3c7;
  box-shadow: 0 2px 8px rgba(245, 158, 11, 0.2);
}

.btn-hint:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.hint-list {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.hint-item {
  background: #fffbeb;
  border: 1px solid #fde68a;
  border-radius: 8px;
  padding: 10px 14px;
  font-size: 14px;
  line-height: 1.5;
}

.hint-label {
  color: #d97706;
  font-weight: 600;
  margin-right: 4px;
}

.hint-text {
  color: var(--text-primary);
}

.hint-deduction {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 400;
}

/* 汉字详情卡片 */
.char-detail {
  background: var(--card-bg);
  border-radius: var(--radius);
  border: 1.5px solid var(--border);
  padding: 18px 20px;
}

.char-detail-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 12px 0;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px 16px;
}

.detail-item {
  font-size: 14px;
  color: var(--text-primary);
}

.detail-item-wide {
  grid-column: 1 / -1;
}

.detail-label {
  color: var(--text-secondary);
  font-size: 12px;
  margin-right: 6px;
}

/* Toast 弹窗 */
.toast {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: linear-gradient(135deg, #f59e0b, #fbbf24);
  color: #fff;
  font-size: 16px;
  font-weight: 700;
  padding: 14px 28px;
  border-radius: 30px;
  box-shadow: 0 4px 20px rgba(245, 158, 11, 0.4);
  z-index: 1000;
  white-space: nowrap;
}

.toast-enter-active {
  animation: toastIn 0.4s ease;
}

.toast-leave-active {
  animation: toastOut 0.4s ease;
}

@keyframes toastIn {
  from { opacity: 0; transform: translateX(-50%) translateY(-30px) scale(0.8); }
  to { opacity: 1; transform: translateX(-50%) translateY(0) scale(1); }
}

@keyframes toastOut {
  from { opacity: 1; transform: translateX(-50%) translateY(0) scale(1); }
  to { opacity: 0; transform: translateX(-50%) translateY(-20px) scale(0.9); }
}

/* 答对弹跳 */
@keyframes popIn {
  0% { transform: scale(0.85); opacity: 0; }
  60% { transform: scale(1.05); }
  100% { transform: scale(1); opacity: 1; }
}

/* 答错摇晃 */
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  20% { transform: translateX(-8px); }
  40% { transform: translateX(8px); }
  60% { transform: translateX(-5px); }
  80% { transform: translateX(5px); }
}

/* 撒花容器 */
.result-wrapper {
  position: relative;
}

.confetti {
  position: absolute;
  top: -10px;
  left: 0;
  right: 0;
  height: 100%;
  pointer-events: none;
  overflow: visible;
}

.confetti-piece {
  position: absolute;
  width: 8px;
  height: 8px;
  border-radius: 2px;
  animation: confettiFall 1.5s ease-out forwards;
  opacity: 0;
}

/* 每个碎片不同颜色、位置、延迟 */
.confetti-piece:nth-child(1)  { left: 5%;  background: #f59e0b; animation-delay: 0s; }
.confetti-piece:nth-child(2)  { left: 12%; background: #ef4444; animation-delay: 0.1s; width: 6px; height: 10px; }
.confetti-piece:nth-child(3)  { left: 20%; background: #3b82f6; animation-delay: 0.05s; border-radius: 50%; }
.confetti-piece:nth-child(4)  { left: 28%; background: #10b981; animation-delay: 0.15s; }
.confetti-piece:nth-child(5)  { left: 35%; background: #f59e0b; animation-delay: 0.08s; width: 10px; height: 6px; }
.confetti-piece:nth-child(6)  { left: 42%; background: #8b5cf6; animation-delay: 0.12s; border-radius: 50%; }
.confetti-piece:nth-child(7)  { left: 50%; background: #ef4444; animation-delay: 0.03s; }
.confetti-piece:nth-child(8)  { left: 57%; background: #3b82f6; animation-delay: 0.18s; width: 6px; height: 10px; }
.confetti-piece:nth-child(9)  { left: 64%; background: #10b981; animation-delay: 0.07s; border-radius: 50%; }
.confetti-piece:nth-child(10) { left: 71%; background: #f59e0b; animation-delay: 0.14s; }
.confetti-piece:nth-child(11) { left: 78%; background: #8b5cf6; animation-delay: 0.02s; width: 10px; height: 6px; }
.confetti-piece:nth-child(12) { left: 85%; background: #ef4444; animation-delay: 0.11s; border-radius: 50%; }
.confetti-piece:nth-child(13) { left: 92%; background: #3b82f6; animation-delay: 0.06s; }
.confetti-piece:nth-child(14) { left: 8%;  background: #10b981; animation-delay: 0.2s; width: 6px; height: 6px; border-radius: 50%; }
.confetti-piece:nth-child(15) { left: 25%; background: #f59e0b; animation-delay: 0.16s; }
.confetti-piece:nth-child(16) { left: 45%; background: #8b5cf6; animation-delay: 0.09s; width: 10px; height: 10px; }
.confetti-piece:nth-child(17) { left: 65%; background: #ef4444; animation-delay: 0.13s; border-radius: 50%; }
.confetti-piece:nth-child(18) { left: 82%; background: #10b981; animation-delay: 0.04s; }

@keyframes confettiFall {
  0% {
    transform: translateY(-20px) rotate(0deg);
    opacity: 1;
  }
  100% {
    transform: translateY(80px) rotate(360deg);
    opacity: 0;
  }
}

/* 移动端适配 */
@media (max-width: 480px) {
  .game {
    padding: 12px 16px;
  }

  .topbar {
    margin-bottom: 16px;
  }

  .score-badge {
    padding: 4px 12px;
  }

  .score-value {
    font-size: 16px;
  }

  .riddle-card {
    padding: 24px 18px;
  }

  .riddle-text {
    font-size: 20px;
  }

  .answer-input {
    height: 50px;
    font-size: 18px; /* 防止 iOS 自动缩放 */
  }

  .btn-submit {
    height: 50px;
    width: 72px;
    font-size: 15px;
  }

  .btn-next {
    height: 50px;
    font-size: 16px;
  }

  .fun-fact {
    font-size: 13px;
    padding: 10px 16px;
  }

  .toast {
    font-size: 14px;
    padding: 12px 20px;
  }

  .detail-grid {
    gap: 6px 12px;
  }
}
</style>