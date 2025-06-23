<template>
  <div class="search-view">
    <input v-model="query" placeholder="输入查询" />
    <button @click="search">搜索</button>
    <ul v-if="results.length">
      <li v-for="(item, i) in results" :key="i">
        {{ item.payload.text }}
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const API_BASE = 'http://localhost:8001'
const query = ref('')
const results = ref<any[]>([])

async function search() {
  if (!query.value) return
  try {
    const res = await fetch(`${API_BASE}/search?q=${encodeURIComponent(query.value)}`)
    if (!res.ok) throw new Error('搜索失败')
    const data = await res.json()
    results.value = data.results
  } catch (err) {
    console.error(err)
  }
}
</script>
