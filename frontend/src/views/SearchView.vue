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
    <v-expansion-panels class="mt-4 result-panels" v-else-if="results.length > 0" multiple>
      <v-expansion-panel v-for="(item, i) in results" :key="i" elevation="2" class="mb-2">
        <template #title>
          <div class="panel-title">
            <strong>{{ item.metadata.chunk_type }}: {{ item.metadata.summary || item.text.slice(0, 50) + '...' }}</strong>
          </div>
        </template>
        <template #text>
          <div v-html="renderMarkdown(item.text)"></div>
          <div class="d-flex justify-end mt-2">
            <v-btn size="small" color="primary" @click="open(item.metadata.file_id, item.metadata.page_num + 1)">
              加载 PDF 第 {{ item.metadata.page_num + 1 }} 页
            </v-btn>
          </div>
        </template>
      </v-expansion-panel>
    </v-expansion-panels>
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
  width: 50%;
}
.result-panels .panel-title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  min-height: 48px;
}
</style>
