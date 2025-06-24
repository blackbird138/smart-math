<template>
  <v-container class="chunk-graph-view">
    <v-select
      v-model="selectedFile"
      :items="files"
      label="选择文件"
      class="mb-4"
      @update:modelValue="loadChunks"
    />
    <v-progress-linear indeterminate v-if="loading" />
    <v-expansion-panels
      v-else-if="chunks.length"
      v-model="expanded"
      multiple
      class="mt-2"
    >
      <v-expansion-panel
        v-for="c in chunks"
        :key="c.id"
        class="mb-2"
        :value="c.id"
      >
        <template #title>
          <strong>
            {{ displayChunkType(c.chunk_type) }}
            <template v-if="c.number"> {{ c.number }}</template>
            : {{ c.summary || c.content.slice(0, 50) + '...' }}
          </strong>
        </template>
        <template #text>
          <div v-html="renderMarkdown(c.content)" />
          <div class="d-flex justify-end mt-2">
            <v-btn size="small" color="primary" @click="openPdf(c.page_num + 1)">
              查看 PDF 第 {{ c.page_num + 1 }} 页
            </v-btn>
          </div>
          <div class="mt-4">
            <h4>相关词条</h4>
            <v-progress-circular indeterminate v-if="related[c.id]?.loading" />
            <v-expansion-panels v-else multiple>
              <v-expansion-panel v-for="r in related[c.id]?.items" :key="r.id">
                <template #title>
                  <strong>{{ r.relation }}: {{ r.summary || r.id }}</strong>
                </template>
                <template #text>
                  <div>{{ r.relation_summary }}</div>
                </template>
              </v-expansion-panel>
            </v-expansion-panels>
          </div>
        </template>
      </v-expansion-panel>
    </v-expansion-panels>
    <p v-else>暂无chunk</p>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import MarkdownIt from 'markdown-it'
import markdownItMathTemml from 'markdown-it-math/temml'
import DOMPurify from 'dompurify'
import { API_BASE } from '../api'
import { useViewerStore } from '../stores/viewer'
import { displayChunkType } from '../utils'

const files = ref<string[]>([])
const selectedFile = ref('')
const chunks = ref<any[]>([])
const loading = ref(false)
const expanded = ref<string[]>([])
const related = ref<Record<string, { loading: boolean; items: any[] }>>({})
const viewer = useViewerStore()

const md = new MarkdownIt({
  html: false,
  linkify: true,
  typographer: true,
}).use(markdownItMathTemml)

function renderMarkdown(text: string): string {
  const raw = md.render(text)
  return DOMPurify.sanitize(raw)
}

async function loadFiles() {
  const res = await fetch(`${API_BASE}/list_files`)
  const data = await res.json()
  files.value = data.files || []
  if (files.value.length && !selectedFile.value) {
    selectedFile.value = files.value[0]
    loadChunks()
  }
}

async function loadChunks() {
  loading.value = true
  related.value = {}
  if (!selectedFile.value) return
  try {
    const res = await fetch(`${API_BASE}/list_chunks?file_id=${selectedFile.value}`)
    const data = await res.json()
    chunks.value = data.chunks || []
  } finally {
    loading.value = false
  }
}

async function loadRelated(id: string) {
  if (related.value[id]) return
  related.value[id] = { loading: true, items: [] }
  try {
    const res = await fetch(`${API_BASE}/list_related?file_id=${selectedFile.value}&chunk_id=${id}`)
    const data = await res.json()
    related.value[id].items = data.related || []
  } catch (err) {
    console.error(err)
    related.value[id].items = []
  } finally {
    related.value[id].loading = false
  }
}

function openPdf(page: number) {
  viewer.setFile(selectedFile.value, page)
}

watch(expanded, (val) => {
  val.forEach((id) => loadRelated(id))
})

onMounted(loadFiles)
</script>

<style scoped>
.chunk-graph-view {
  padding: 1rem;
}
</style>
