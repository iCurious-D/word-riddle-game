<template>
  <div class="achievements">
    <div class="topbar">
      <button class="btn-back" @click="$router.push('/')">&larr; 返回</button>
      <div class="progress-badge">已解锁 {{ achievementStore.unlockedCount() }} / {{ ACHIEVEMENTS.length }}</div>
    </div>

    <h1 class="page-title">🏅 我的成就</h1>

    <!-- 累计统计 -->
    <div class="stats-card">
      <div class="stat-item">
        <span class="stat-num">{{ achievementStore.stats.totalCorrect }}</span>
        <span class="stat-label">累计答对</span>
      </div>
      <div class="stat-item">
        <span class="stat-num">{{ achievementStore.stats.bestStreak }}</span>
        <span class="stat-label">最佳连对</span>
      </div>
      <div class="stat-item">
        <span class="stat-num">{{ achievementStore.stats.noHintCorrect }}</span>
        <span class="stat-label">无提示答对</span>
      </div>
      <div class="stat-item">
        <span class="stat-num">{{ achievementStore.stats.bestSpeed }}</span>
        <span class="stat-label">60秒最快答对</span>
      </div>
    </div>

    <!-- 成就徽章墙 -->
    <div class="badge-grid">
      <div
        v-for="a in ACHIEVEMENTS"
        :key="a.id"
        class="badge-card"
        :class="{ 'badge-locked': !achievementStore.isUnlocked(a.id) }"
      >
        <div class="badge-icon">{{ achievementStore.isUnlocked(a.id) ? a.icon : '🔒' }}</div>
        <div class="badge-name">{{ a.name }}</div>
        <div class="badge-desc">{{ a.desc }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAchievementStore, ACHIEVEMENTS } from '@/stores/achievement'

const achievementStore = useAchievementStore()
</script>

<style scoped>
.achievements {
  max-width: 520px;
  margin: 0 auto;
  padding: 20px;
  min-height: 100vh;
}

.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
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

.progress-badge {
  background: var(--primary-light);
  color: var(--primary);
  font-size: 13px;
  font-weight: 600;
  padding: 6px 14px;
  border-radius: 20px;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  text-align: center;
  margin-bottom: 20px;
}

.stats-card {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  background: var(--card-bg);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
  padding: 18px 12px;
  margin-bottom: 24px;
}

.stat-item {
  text-align: center;
}

.stat-num {
  display: block;
  font-size: 20px;
  font-weight: 700;
  color: var(--primary);
}

.stat-label {
  font-size: 12px;
  color: var(--text-secondary);
}

.badge-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}

.badge-card {
  background: var(--card-bg);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 20px 14px;
  text-align: center;
  border: 1.5px solid transparent;
  transition: transform 0.2s;
}

.badge-card:hover {
  transform: translateY(-2px);
}

.badge-locked {
  opacity: 0.5;
  filter: grayscale(1);
}

.badge-icon {
  font-size: 36px;
  margin-bottom: 8px;
}

.badge-name {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.badge-desc {
  font-size: 12px;
  color: var(--text-secondary);
}

@media (max-width: 480px) {
  .achievements {
    padding: 12px 16px;
  }

  .stats-card {
    grid-template-columns: repeat(2, 1fr);
    gap: 14px;
  }

  .badge-grid {
    gap: 10px;
  }
}
</style>
