<template>
  <div class="admin">
    <div class="admin-header">
      <button class="btn-back" @click="$router.push('/')">&larr; 返回首页</button>
      <h1>字谜管理后台</h1>
      <button v-if="authenticated" class="btn-logout" @click="logout">退出</button>
    </div>

    <!-- 未登录：显示密码输入 -->
    <div v-if="!authenticated" class="login-card">
      <h2 class="login-title">管理员登录</h2>
      <input
        v-model="password"
        type="password"
        class="login-input"
        placeholder="请输入管理密码"
        @keyup.enter="login"
      />
      <p v-if="loginError" class="login-error">{{ loginError }}</p>
      <button class="login-btn" @click="login" :disabled="!password">登录</button>
    </div>

    <!-- 已登录：显示管理面板 -->
    <template v-else>
      <div class="tabs">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          class="tab-btn"
          :class="{ 'tab-active': currentTab === tab.key }"
          @click="switchTab(tab.key)"
        >
          {{ tab.label }}
          <span v-if="tab.count > 0" class="tab-badge">{{ tab.count }}</span>
        </button>
      </div>

      <div v-if="loading" class="loading-state">加载中...</div>
      <div v-else-if="riddles.length === 0" class="empty-state">暂无{{ currentTabLabel }}的谜题</div>

      <div v-else class="riddle-list">
        <div v-for="r in riddles" :key="r.id" class="riddle-item">
          <div class="riddle-info">
            <div class="riddle-question">{{ r.question }}</div>
            <div class="riddle-meta">
              <span class="answer-badge">{{ r.answer }}</span>
              <span>{{ r.grade }}年级</span>
              <span>难度{{ r.difficulty }}</span>
              <span>👍{{ r.likes }} 👎{{ r.dislikes }}</span>
              <span v-if="r.source === 'user'" class="source-user">用户: {{ r.submitter || '匿名' }}</span>
              <span class="quality-badge" :class="'q-' + r.quality">{{ r.quality }}</span>
            </div>
          </div>
          <div class="riddle-actions">
            <template v-if="currentTab === 'pending'">
              <button class="action-btn approve" @click="review(r.id, 'approve')">通过</button>
              <button class="action-btn reject" @click="review(r.id, 'reject')">拒绝</button>
            </template>
            <template v-if="currentTab === 'flagged'">
              <button class="action-btn restore" @click="review(r.id, 'restore')">正常</button>
              <button class="action-btn lower" @click="review(r.id, 'lower')">降权</button>
              <button class="action-btn reject" @click="review(r.id, 'reject')">下架</button>
            </template>
            <template v-if="currentTab === 'low_quality'">
              <button class="action-btn restore" @click="review(r.id, 'restore')">恢复</button>
            </template>
            <template v-if="currentTab === 'rejected'">
              <button class="action-btn restore" @click="review(r.id, 'restore')">恢复</button>
            </template>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'

// 认证状态
const authenticated = ref(false)
const password = ref('')
const loginError = ref('')
const token = ref(sessionStorage.getItem('admin_token') || '')

if (token.value) {
  authenticated.value = true
}

async function login() {
  loginError.value = ''
  try {
    const res = await axios.post('/api/admin/verify', null, {
      params: { password: password.value }
    })
    if (res.data.error) {
      loginError.value = res.data.error
      return
    }
    token.value = res.data.token
    sessionStorage.setItem('admin_token', res.data.token)
    authenticated.value = true
    password.value = ''
    // 登录成功后加载数据
    fetchRiddles()
    fetchCounts()
  } catch (err) {
    loginError.value = '网络错误，请重试'
  }
}

function logout() {
  authenticated.value = false
  token.value = ''
  sessionStorage.removeItem('admin_token')
}

function authHeaders() {
  return { Authorization: token.value }
}

const tabs = ref([
  { key: 'pending', label: '待审核上传', count: 0 },
  { key: 'flagged', label: '差评标记', count: 0 },
  { key: 'low_quality', label: '已降权', count: 0 },
  { key: 'rejected', label: '已下架', count: 0 },
])

const currentTab = ref('pending')
const riddles = ref([])
const loading = ref(false)

const currentTabLabel = computed(() => {
  const tab = tabs.value.find(t => t.key === currentTab.value)
  return tab ? tab.label : ''
})

async function switchTab(key) {
  currentTab.value = key
  await fetchRiddles()
}

async function fetchRiddles() {
  loading.value = true
  try {
    const res = await axios.get('/api/admin/riddles', {
      params: { filter: currentTab.value },
      headers: authHeaders()
    })
    riddles.value = res.data
  } catch (err) {
    if (err.response && err.response.status === 401) {
      logout()
    }
    console.error('加载失败:', err)
  } finally {
    loading.value = false
  }
}

async function review(riddleId, action) {
  try {
    await axios.post(`/api/admin/riddles/${riddleId}/review`, null, {
      params: { action },
      headers: authHeaders()
    })
    await fetchRiddles()
  } catch (err) {
    if (err.response && err.response.status === 401) {
      logout()
    }
    console.error('审核失败:', err)
  }
}

async function fetchCounts() {
  for (const tab of tabs.value) {
    try {
      const res = await axios.get('/api/admin/riddles', {
        params: { filter: tab.key },
        headers: authHeaders()
      })
      tab.count = Array.isArray(res.data) ? res.data.length : 0
    } catch (err) {
      tab.count = 0
    }
  }
}

onMounted(() => {
  if (authenticated.value) {
    fetchRiddles()
    fetchCounts()
  }
})
</script>

<style scoped>
.admin {
  max-width: 720px;
  margin: 0 auto;
  padding: 20px;
  min-height: 100vh;
}

.admin-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.admin-header h1 {
  font-size: 20px;
  color: var(--text-primary);
  margin: 0;
}

.btn-back {
  background: none;
  border: none;
  font-size: 14px;
  color: var(--text-secondary);
  cursor: pointer;
}

.btn-logout {
  margin-left: auto;
  background: none;
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 4px 12px;
  font-size: 12px;
  color: var(--text-secondary);
  cursor: pointer;
}

.btn-logout:hover {
  background: var(--bg);
}

/* 登录卡片 */
.login-card {
  max-width: 360px;
  margin: 60px auto;
  background: var(--card-bg);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
  padding: 32px 28px;
  text-align: center;
}

.login-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 20px 0;
}

.login-input {
  width: 100%;
  padding: 10px 14px;
  border: 1.5px solid var(--border);
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  box-sizing: border-box;
  transition: border-color 0.2s;
}

.login-input:focus {
  border-color: var(--primary);
}

.login-error {
  color: #dc2626;
  font-size: 13px;
  margin: 8px 0 0 0;
}

.login-btn {
  width: 100%;
  margin-top: 16px;
  padding: 10px;
  background: var(--primary);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}

.login-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.login-btn:hover:not(:disabled) {
  opacity: 0.9;
}

.tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.tab-btn {
  padding: 8px 16px;
  border-radius: 20px;
  border: 1.5px solid var(--border);
  background: var(--card-bg);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
}

.tab-btn:hover {
  border-color: var(--primary);
}

.tab-active {
  background: var(--primary);
  color: #fff;
  border-color: var(--primary);
}

.tab-badge {
  background: rgba(0, 0, 0, 0.15);
  padding: 1px 6px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 700;
}

.tab-active .tab-badge {
  background: rgba(255, 255, 255, 0.3);
}

.loading-state, .empty-state {
  text-align: center;
  padding: 40px;
  color: var(--text-secondary);
}

.riddle-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.riddle-item {
  background: var(--card-bg);
  border-radius: var(--radius);
  border: 1px solid var(--border);
  padding: 14px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.riddle-info {
  flex: 1;
  min-width: 0;
}

.riddle-question {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.riddle-meta {
  display: flex;
  gap: 8px;
  font-size: 12px;
  color: var(--text-secondary);
  flex-wrap: wrap;
  align-items: center;
}

.answer-badge {
  background: var(--primary-light);
  color: var(--primary);
  padding: 1px 8px;
  border-radius: 4px;
  font-weight: 700;
  font-size: 13px;
}

.source-user {
  color: #8b5cf6;
}

.quality-badge {
  padding: 1px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
}

.q-normal { background: #ecfdf5; color: #059669; }
.q-flagged { background: #fffbeb; color: #d97706; }
.q-low_quality { background: #fef2f2; color: #dc2626; }
.q-rejected { background: #f3f4f6; color: #6b7280; }

.riddle-actions {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}

.action-btn {
  padding: 6px 12px;
  border-radius: 6px;
  border: none;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.approve { background: #ecfdf5; color: #059669; }
.approve:hover { background: #d1fae5; }
.reject { background: #fef2f2; color: #dc2626; }
.reject:hover { background: #fee2e2; }
.lower { background: #fffbeb; color: #d97706; }
.lower:hover { background: #fef3c7; }
.restore { background: #eff6ff; color: #2563eb; }
.restore:hover { background: #dbeafe; }

@media (max-width: 480px) {
  .riddle-item {
    flex-direction: column;
    align-items: flex-start;
  }
  .riddle-actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>
