import { defineStore } from 'pinia'
import { ref } from 'vue'

const STORAGE_KEY = 'riddle_favorites'

export const useFavoriteStore = defineStore('favorite', () => {
  // 收藏的字谜快照（持久化），新收藏排在前面
  const favorites = ref([])

  function load() {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      favorites.value = stored ? JSON.parse(stored) : []
    } catch (e) {
      console.error('加载收藏失败:', e)
    }
  }

  function save() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(favorites.value))
  }

  function isFavorited(id) {
    return favorites.value.some(f => f.id === id)
  }

  // 切换收藏，返回切换后是否为已收藏
  function toggle(riddle) {
    const idx = favorites.value.findIndex(f => f.id === riddle.id)
    if (idx >= 0) {
      favorites.value.splice(idx, 1)
      save()
      return false
    }
    favorites.value.unshift({
      id: riddle.id,
      question: riddle.question,
      answer: riddle.answer,
      grade: riddle.grade,
      difficulty: riddle.difficulty,
    })
    save()
    return true
  }

  function remove(id) {
    favorites.value = favorites.value.filter(f => f.id !== id)
    save()
  }

  load()

  return { favorites, isFavorited, toggle, remove }
})
