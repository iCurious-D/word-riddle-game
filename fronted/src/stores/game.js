import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export const useGameStore = defineStore('game', () => {
  const publisher = ref('')
  const grade = ref(0)
  const term = ref(1)
  const score = ref(0)
  const seenIds = ref([])

  // 提示相关状态
  const hintLevel = ref(0)
  const hints = ref([])
  const charInfo = ref(null)

  // 扣分规则：0次扣0，1次扣1，2次扣3，3次扣6
  const hintDeductions = [0, 1, 3, 6]

  // 累积答对计数 + 里程碑
  const correctCount = ref(0)
  const toastMessage = ref('')
  const toastVisible = ref(false)

  // 本轮做题统计
  const totalQuestions = ref(0)
  const sessionCorrect = ref(0)
  const sessionStartTime = ref(0)
  const sessionEndTime = ref(0)

  // 投票状态（全局，不按年级隔离）
  const votedRiddles = ref({})  // { riddleId: 'up'|'down' }
  const currentLikes = ref(0)
  const currentDislikes = ref(0)

  const milestones = [
    { count: 5, text: '初露锋芒！' },
    { count: 10, text: '渐入佳境！' },
    { count: 20, text: '字谜达人！' },
    { count: 50, text: '汉字大师！' },
  ]

  // 生成 LocalStorage 的 key，按教材/年级/学期隔离
  function getStorageKey(pub, grd, trm) {
    return `riddle_seen_${pub}_${grd}_${trm}`
  }

  // 从 LocalStorage 加载当前年级的做题记录
  function loadSeenIds() {
    const key = getStorageKey(publisher.value, grade.value, term.value)
    const stored = localStorage.getItem(key)
    seenIds.value = stored ? JSON.parse(stored) : []
  }

  function setOptions(pub, grd, trm = 0) {
    publisher.value = pub
    grade.value = grd
    term.value = trm
    score.value = 0      // 重置分数
    correctCount.value = 0 // 重置答对计数
    startSession()         // 重置本轮统计
    loadSeenIds()          // 加载该年级的做题记录
  }

  function addScore(points) {
    score.value += points
  }

  // 计算当前题得分（基础 10 分 - 提示扣分）
  function getCurrentScore() {
    const deduction = hintDeductions[hintLevel.value] || 0
    return Math.max(0, 10 - deduction)
  }

  // 获取提示
  async function getHint(riddleId) {
    if (hintLevel.value >= 3) return
    hintLevel.value++
    try {
      const res = await axios.get('/api/riddles/hint', {
        params: { riddle_id: riddleId, level: hintLevel.value }
      })
      if (res.data.hint) {
        hints.value.push(res.data.hint)
      }
    } catch (err) {
      console.error('获取提示失败:', err)
    }
  }

  // 重置提示状态
  function resetHint() {
    hintLevel.value = 0
    hints.value = []
    charInfo.value = null
  }

  // 获取汉字详情
  async function fetchCharInfo(char) {
    try {
      const res = await axios.get('/api/char/info', {
        params: { char }
      })
      if (!res.data.error) {
        charInfo.value = res.data
      }
    } catch (err) {
      console.error('获取汉字详情失败:', err)
    }
  }

  // 记录一次答对，返回是否触发里程碑
  function recordCorrect() {
    correctCount.value++
    sessionCorrect.value++
    const milestone = milestones.find(m => m.count === correctCount.value)
    if (milestone) {
      showToast(`${milestone.text} 已答对 ${correctCount.value} 题`)
    }
  }

  function showToast(msg) {
    toastMessage.value = msg
    toastVisible.value = true
    setTimeout(() => {
      toastVisible.value = false
    }, 2500)
  }

  // 记录做过的题，同步写入 LocalStorage
  function addSeenId(id) {
    if (id && !seenIds.value.includes(id)) {
      seenIds.value.push(id)
      const key = getStorageKey(publisher.value, grade.value, term.value)
      localStorage.setItem(key, JSON.stringify(seenIds.value))
    }
  }

  // 返回逗号分隔的字符串，传给后端 exclude_ids 参数
  function getExcludeIds() {
    return seenIds.value.join(',')
  }

  // 清空当前年级的做题记录
  function resetSeenIds() {
    seenIds.value = []
    const key = getStorageKey(publisher.value, grade.value, term.value)
    localStorage.removeItem(key)
  }

  // 本轮统计相关
  function startSession() {
    totalQuestions.value = 0
    sessionCorrect.value = 0
    sessionStartTime.value = Date.now()
    sessionEndTime.value = 0
  }

  function endSession() {
    if (sessionStartTime.value && !sessionEndTime.value) {
      sessionEndTime.value = Date.now()
    }
  }

  function recordAttempt() {
    totalQuestions.value++
  }

  function getAccuracy() {
    if (totalQuestions.value === 0) return '0%'
    return Math.round(sessionCorrect.value / totalQuestions.value * 100) + '%'
  }

  function getDuration() {
    const end = sessionEndTime.value || Date.now()
    const seconds = Math.floor((end - sessionStartTime.value) / 1000)
    const minutes = Math.floor(seconds / 60)
    const secs = seconds % 60
    if (minutes > 0) return `${minutes} 分 ${secs} 秒`
    return `${secs} 秒`
  }

  function hasSessionData() {
    return totalQuestions.value > 0
  }

  // ---------- 投票功能 ----------

  function loadVotedRiddles() {
    const stored = localStorage.getItem('riddle_votes')
    votedRiddles.value = stored ? JSON.parse(stored) : {}
  }

  function saveVotedRiddles() {
    localStorage.setItem('riddle_votes', JSON.stringify(votedRiddles.value))
  }

  // 初始化时加载
  loadVotedRiddles()

  function getVoteStatus(riddleId) {
    return votedRiddles.value[riddleId] || null
  }

  function setCurrentVotes(likes, dislikes) {
    currentLikes.value = likes
    currentDislikes.value = dislikes
  }

  async function voteRiddle(riddleId, type) {
    // 已投过票则不允许再投
    if (votedRiddles.value[riddleId]) return

    try {
      const res = await axios.post('/api/riddles/vote', null, {
        params: { riddle_id: riddleId, vote: type }
      })
      if (!res.data.error) {
        // 记录投票状态
        votedRiddles.value[riddleId] = type
        saveVotedRiddles()
        currentLikes.value = res.data.likes
        currentDislikes.value = res.data.dislikes

        // 踩：加入排除列表，不再出给这个用户
        if (type === 'down') {
          addSeenId(riddleId)
        }
      }
    } catch (err) {
      console.error('投票失败:', err)
    }
  }

  return {
    publisher, grade, term, score, seenIds,
    hintLevel, hints, charInfo,
    correctCount, toastMessage, toastVisible,
    totalQuestions, sessionCorrect, sessionStartTime, sessionEndTime,
    votedRiddles, currentLikes, currentDislikes,
    setOptions, addScore, getCurrentScore, recordCorrect,
    addSeenId, getExcludeIds, resetSeenIds,
    getHint, resetHint, fetchCharInfo,
    startSession, endSession, recordAttempt, getAccuracy, getDuration, hasSessionData,
    getVoteStatus, setCurrentVotes, voteRiddle
  }
})