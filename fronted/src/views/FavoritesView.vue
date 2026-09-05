<template>
  <div class="favorites">
    <div class="topbar">
      <button class="btn-back" @click="$router.push('/')">&larr; 返回</button>
      <div class="count-badge">共 {{ favoriteStore.favorites.length }} 条</div>
    </div>

    <h1 class="page-title">❤️ 我的收藏</h1>

    <div v-if="favoriteStore.favorites.length === 0" class="empty">
      还没有收藏任何字谜<br />
      <span class="empty-tip">在游戏中点击 🤍 即可收藏</span>
    </div>

    <div v-else class="fav-list">
      <div v-for="f in favoriteStore.favorites" :key="f.id" class="fav-card">
        <div class="fav-question">{{ f.question }}</div>
        <div class="fav-meta">
          <span class="fav-answer">谜底：{{ f.answer }}</span>
          <span class="fav-grade">{{ f.grade }}年级</span>
        </div>
        <button class="btn-remove" @click="favoriteStore.remove(f.id)">取消收藏</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useFavoriteStore } from '@/stores/favorite'

const favoriteStore = useFavoriteStore()
</script>

<style scoped>
.favorites {
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

.count-badge {
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
  margin-bottom: 24px;
}

.empty {
  text-align: center;
  color: var(--text-secondary);
  padding: 60px 0;
  font-size: 15px;
  line-height: 2;
}

.empty-tip {
  font-size: 13px;
  color: var(--text-secondary);
  opacity: 0.7;
}

.fav-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.fav-card {
  position: relative;
  background: var(--card-bg);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 18px 20px;
}

.fav-question {
  font-size: 17px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 10px;
  padding-right: 70px;
}

.fav-meta {
  display: flex;
  gap: 12px;
  align-items: center;
}

.fav-answer {
  font-size: 14px;
  color: var(--success);
  font-weight: 600;
}

.fav-grade {
  font-size: 12px;
  color: var(--text-secondary);
  background: var(--bg);
  padding: 2px 10px;
  border-radius: 10px;
}

.btn-remove {
  position: absolute;
  top: 16px;
  right: 16px;
  background: none;
  border: none;
  font-size: 12px;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 4px 0;
}

.btn-remove:hover {
  color: var(--error);
}

@media (max-width: 480px) {
  .favorites {
    padding: 12px 16px;
  }

  .fav-question {
    font-size: 16px;
  }
}
</style>
