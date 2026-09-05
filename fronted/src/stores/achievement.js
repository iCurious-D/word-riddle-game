import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'

const STORAGE_KEY = 'riddle_achievements'

// 成就定义：判定为纯函数 (stats) => bool，易扩展易测试
export const ACHIEVEMENTS = [
  { id: 'first_blood', name: '初露锋芒', desc: '首次答对一道字谜', icon: '🌱', check: s => s.totalCorrect >= 1 },
  { id: 'correct_10', name: '小有所成', desc: '累计答对 10 题', icon: '📚', check: s => s.totalCorrect >= 10 },
  { id: 'correct_50', name: '字谜大师', desc: '累计答对 50 题', icon: '🏆', check: s => s.totalCorrect >= 50 },
  { id: 'streak_5', name: '连中五元', desc: '单轮连对 5 题', icon: '🔥', check: s => s.bestStreak >= 5 },
  { id: 'streak_10', name: '势如破竹', desc: '单轮连对 10 题', icon: '⚡', check: s => s.bestStreak >= 10 },
  { id: 'no_hint_5', name: '独立思考', desc: '不用提示答对 5 题', icon: '💡', check: s => s.noHintCorrect >= 5 },
  { id: 'speed_master', name: '时间大师', desc: '60 秒内答对 5 题', icon: '⏱️', check: s => s.bestSpeed >= 5 },
  { id: 'share_1', name: '乐于分享', desc: '分享一次成绩', icon: '📤', check: s => s.shared >= 1 },
]

export const useAchievementStore = defineStore('achievement', () => {
  // 累计统计（持久化）
  const stats = reactive({
    totalCorrect: 0,
    bestStreak: 0,
    noHintCorrect: 0,
    bestSpeed: 0,   // 任意 60 秒窗口内答对数的历史最大值
    shared: 0,
  })
  // 已解锁成就 { id: 时间戳 }（持久化）
  const unlocked = reactive({})
  // 本轮当前连对（不持久化）
  const currentStreak = ref(0)
  // 答对时间戳队列（不持久化），用于滑动窗口测速
  const correctTimes = ref([])

  // 解锁提示
  const toastMessage = ref('')
  const toastVisible = ref(false)

  function load() {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (stored) {
        const data = JSON.parse(stored)
        Object.assign(stats, data.stats || {})
        Object.assign(unlocked, data.unlocked || {})
      }
    } catch (e) {
      console.error('加载成就失败:', e)
    }
  }

  function save() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ stats, unlocked }))
  }

  function showToast(msg) {
    toastMessage.value = msg
    toastVisible.value = true
    setTimeout(() => {
      toastVisible.value = false
    }, 2500)
  }

  // 统一跑判定，解锁新满足且未解锁的成就
  function checkUnlocks() {
    for (const a of ACHIEVEMENTS) {
      if (!unlocked[a.id] && a.check(stats)) {
        unlocked[a.id] = Date.now()
        showToast(`${a.icon} 解锁成就：${a.name}`)
      }
    }
    save()
  }

  // ---------- 埋点 ----------

  // 答对：累计 + 连对 + 无提示计数 + 测速
  function recordCorrect({ usedHint = false } = {}) {
    stats.totalCorrect++
    currentStreak.value++
    if (currentStreak.value > stats.bestStreak) {
      stats.bestStreak = currentStreak.value
    }
    if (!usedHint) stats.noHintCorrect++
    // 滑动 60 秒窗口：统计窗口内答对数，更新历史最快
    const now = Date.now()
    correctTimes.value.push(now)
    const cutoff = now - 60000
    while (correctTimes.value.length && correctTimes.value[0] < cutoff) {
      correctTimes.value.shift()
    }
    if (correctTimes.value.length > stats.bestSpeed) {
      stats.bestSpeed = correctTimes.value.length
    }
    checkUnlocks()
  }

  // 答错：连对清零
  function recordWrong() {
    currentStreak.value = 0
  }

  // 分享成绩
  function recordShare() {
    stats.shared++
    checkUnlocks()
  }

  function isUnlocked(id) {
    return !!unlocked[id]
  }

  function unlockedCount() {
    return Object.keys(unlocked).length
  }

  load()

  return {
    stats, unlocked, currentStreak, toastMessage, toastVisible,
    recordCorrect, recordWrong, recordShare,
    isUnlocked, unlockedCount,
  }
})
