<template>
  <div class="search-view">
    <select v-model="selected" class="file-select">
      <option v-for="f in files" :key="f" :value="f">{{ f }}</option>
    </select>
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
          <span v-html="renderMarkdown(item.text)"></span>
          （第 {{ item.metadata.page_num + 1 }} 页）
        </router-link>
      </li>
    </ul>
    <p v-else>暂无结果</p>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import MarkdownIt from 'markdown-it'
import markdownItKatex from 'markdown-it-katex'
import DOMPurify from 'dompurify'
import { API_BASE } from '../api'
const query = ref('')
const results = ref<any[]>([])

const loading = ref(false)
const files = ref<string[]>([])
const selected = ref('')

const md = new MarkdownIt({
  html: false,
  linkify: true,
  typographer: true,
}).use(markdownItKatex)

function renderMarkdown(text: string): string {
  const rawHtml = md.render(text)
  return DOMPurify.sanitize(rawHtml)
}

async function search() {
  if (!query.value.trim()) return
  loading.value = true
  try {
    const res = await fetch(`${API_BASE}/search?file_id=${selected.value}&q=${encodeURIComponent(query.value)}`)
    const data = await res.json()
    results.value = data.results || []
  } catch (err) {
    console.error(err)
    results.value = []
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  try {
    const res = await fetch(`${API_BASE}/list_files`)
    const data = await res.json()
    files.value = data.files || []
    if (files.value.length && !selected.value) {
      selected.value = files.value[0]
    }
  } catch (err) {
    console.error(err)
  }
})

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
