<template>
  <div class="submit-page">
    <div class="submit-header">
      <button class="btn-back" @click="$router.push('/')">&larr; 返回首页</button>
      <h1>上传字谜</h1>
      <p class="subtitle">分享你的字谜，审核通过后将参与出题</p>
    </div>

    <div class="card">
      <div v-if="submitted" class="success-msg">
        <div class="success-icon">✅</div>
        <p>提交成功！审核通过后将参与出题</p>
        <button class="btn btn-primary" @click="resetForm">继续上传</button>
        <button class="btn btn-outline" @click="$router.push('/')">返回首页</button>
      </div>

      <form v-else @submit.prevent="handleSubmit">
        <div class="form-row">
          <label class="form-label">谜面</label>
          <textarea
            v-model="form.question"
            class="form-textarea"
            placeholder="如：太阳和月亮在一起"
            required
            rows="2"
          ></textarea>
        </div>

        <div class="form-row">
          <label class="form-label">谜底</label>
          <input
            v-model="form.answer"
            class="form-input"
            placeholder="单个汉字，如：明"
            maxlength="1"
            required
          />
        </div>

        <div class="form-row">
          <label class="form-label">年级</label>
          <select v-model="form.grade" class="form-select" required>
            <option v-for="g in 6" :key="g" :value="g">{{ g }}年级</option>
          </select>
        </div>

        <div class="form-row">
          <label class="form-label">难度</label>
          <select v-model="form.difficulty" class="form-select">
            <option :value="1">简单</option>
            <option :value="2">中等</option>
            <option :value="3">困难</option>
          </select>
        </div>

        <div class="form-row">
          <label class="form-label">昵称</label>
          <input
            v-model="form.submitter"
            class="form-input"
            placeholder="可选，如：张老师"
            maxlength="20"
          />
        </div>

        <div v-if="errorMsg" class="error-msg">{{ errorMsg }}</div>

        <button class="btn btn-primary btn-submit" type="submit" :disabled="submitting">
          {{ submitting ? '提交中...' : '提交字谜' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import axios from 'axios'

const form = reactive({
  question: '',
  answer: '',
  grade: 3,
  difficulty: 2,
  submitter: ''
})

const submitted = ref(false)
const submitting = ref(false)
const errorMsg = ref('')

function resetForm() {
  form.question = ''
  form.answer = ''
  form.grade = 3
  form.difficulty = 2
  form.submitter = ''
  submitted.value = false
  errorMsg.value = ''
}

async function handleSubmit() {
  errorMsg.value = ''

  if (!form.question.trim()) {
    errorMsg.value = '请输入谜面'
    return
  }
  if (!form.answer.trim() || form.answer.trim().length !== 1) {
    errorMsg.value = '谜底必须是单个汉字'
    return
  }

  submitting.value = true
  try {
    const res = await axios.post('/api/riddles/submit', null, {
      params: {
        question: form.question.trim(),
        answer: form.answer.trim(),
        grade: form.grade,
        difficulty: form.difficulty,
        submitter: form.submitter.trim() || null
      }
    })
    if (res.data.error) {
      errorMsg.value = res.data.error
    } else {
      submitted.value = true
    }
  } catch (err) {
    errorMsg.value = '提交失败，请重试'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.submit-page {
  max-width: 520px;
  margin: 0 auto;
  padding: 20px;
  min-height: 100vh;
}

.submit-header {
  text-align: center;
  margin-bottom: 24px;
}

.submit-header h1 {
  font-size: 24px;
  color: var(--text-primary);
  margin: 12px 0 6px;
}

.subtitle {
  font-size: 14px;
  color: var(--text-secondary);
}

.btn-back {
  background: none;
  border: none;
  font-size: 14px;
  color: var(--text-secondary);
  cursor: pointer;
}

.card {
  background: var(--card-bg);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
  padding: 28px 24px;
}

.form-row {
  margin-bottom: 18px;
}

.form-label {
  display: block;
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 6px;
  font-weight: 600;
}

.form-input, .form-select, .form-textarea {
  width: 100%;
  height: 44px;
  padding: 0 14px;
  font-size: 15px;
  color: var(--text-primary);
  background: var(--bg);
  border: 1.5px solid var(--border);
  border-radius: var(--radius);
  outline: none;
  box-sizing: border-box;
}

.form-textarea {
  height: auto;
  padding: 10px 14px;
  resize: vertical;
  font-family: inherit;
}

.form-input:focus, .form-select:focus, .form-textarea:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(74, 144, 217, 0.15);
}

.btn {
  width: 100%;
  height: 46px;
  font-size: 16px;
  font-weight: 600;
  border-radius: var(--radius);
  cursor: pointer;
  border: none;
  margin-top: 8px;
}

.btn-primary {
  background: var(--primary);
  color: #fff;
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-hover);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-outline {
  background: var(--card-bg);
  color: var(--primary);
  border: 1.5px solid var(--primary);
}

.btn-outline:hover {
  background: var(--primary-light);
}

.error-msg {
  color: #dc2626;
  font-size: 13px;
  margin-bottom: 8px;
}

.success-msg {
  text-align: center;
  padding: 20px 0;
}

.success-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.success-msg p {
  font-size: 16px;
  color: var(--text-primary);
  margin-bottom: 20px;
}

@media (max-width: 480px) {
  .submit-page {
    padding: 12px 16px;
  }
  .card {
    padding: 20px 16px;
  }
  .form-input, .form-select {
    height: 48px;
    font-size: 16px;
  }
}
</style>
