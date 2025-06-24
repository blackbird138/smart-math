<template>
  <v-container class="search-view">
    <v-row class="align-center">
      <v-col cols="12" md="4">
        <v-select v-model="selected" :items="files" label="选择文件" density="comfortable" />
      </v-col>
      <v-col cols="12" md="6">
        <v-text-field v-model="query" label="输入查询" @keyup.enter="search" density="comfortable" />
      </v-col>
      <v-col cols="12" md="2">
        <v-btn color="primary" class="mt-2 mt-md-0" @click="search" :loading="loading">搜索</v-btn>
      </v-col>
    </v-row>
    <v-progress-linear indeterminate class="mt-4" v-if="loading" />
    <v-list two-line class="mt-4" v-else-if="results.length > 0">
      <v-list-item v-for="(item, i) in results" :key="i">
        <v-list-item-content>
          <v-list-item-title>
            <a href="#" @click.prevent="open(item.metadata.file_id, item.metadata.page_num + 1)">
              <span v-html="renderMarkdown(item.text)"></span>
              （第 {{ item.metadata.page_num + 1 }} 页）
            </a>
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </v-list>
    <p v-else class="mt-4">暂无结果</p>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import MarkdownIt from 'markdown-it'
import markdownItMathTemml from 'markdown-it-math/temml'
import DOMPurify from 'dompurify'
import { API_BASE } from '../api'
import { useViewerStore } from '../stores/viewer'
const query = ref('')
const results = ref<any[]>([])

const loading = ref(false)
const files = ref<string[]>([])
const selected = ref('')
const viewer = useViewerStore()

const md = new MarkdownIt({
  html: false,
  linkify: true,
  typographer: true,
}).use(markdownItMathTemml)

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

function open(id: string, page: number) {
  viewer.setFile(id, page)
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
</style>
