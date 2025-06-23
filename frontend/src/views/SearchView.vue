<template>
  <div class="search-view">
    <input v-model="query" placeholder="输入查询" />
    <button @click="search">搜索</button>
    <p v-if="loading">搜索中…</p>
    <ul v-else-if="results.length > 0">
      <li v-for="(item, i) in results" :key="i">
        <router-link
          :to="{
             name: 'document',
             params: { id: item.metadata.file_id },
             query: { page: item.metadata.page_num + 1 }
          }"
        >
          {{ item.text }}（第 {{ item.metadata.page_num + 1 }} 页）
        </router-link>
      </li>
    </ul>
    <p v-else>暂无结果</p>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import { API_BASE } from '../api'
const query = ref('')
const results = ref<any[]>([])

const loading = ref(false)

async function search() {
  if (!query.value.trim()) return
  loading.value = true
  try {
    const res = await fetch(`${API_BASE}/search?q=${encodeURIComponent(query.value)}`)
    const data = await res.json()
    results.value = data.results || []
  } catch (err) {
    console.error(err)
    results.value = []
  } finally {
    loading.value = false
  }
}

</script>

<style scoped>
.search-view {
  padding: 1rem;
}
.search-view ul {
  margin-top: 1rem;
}
.search-view li {
  line-height: 1.8;
}
</style>
