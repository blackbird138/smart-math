<template>
  <v-container class="solve-view" @click="onClickRef">
    <v-row class="align-center">
      <v-col cols="12" md="4">
        <v-select
          v-model="selected"
          :items="files"
          label="选择文件"
          density="comfortable"
        />
      </v-col>
      <v-col cols="12" md="6">
        <v-text-field
          v-model="question"
          label="输入题目"
          density="comfortable"
          @keyup.enter="solve"
        />
      </v-col>
      <v-col cols="12" md="2">
        <v-btn color="primary" class="mt-2 mt-md-0" @click="solve" :loading="loading">
          解答
        </v-btn>
      </v-col>
    </v-row>
    <v-progress-linear indeterminate class="mt-4" v-if="loading" />
    <div v-else-if="answer" class="mt-4" v-html="renderMarkdown(answer)"></div>
    <p v-else class="mt-4">暂无解答</p>
    <v-dialog v-model="dialog" max-width="600">
      <v-card>
        <v-card-text @click="onClickRef">
          <div v-html="renderMarkdown(refContent)" />
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import MarkdownIt from 'markdown-it'
import markdownItMathTemml from 'markdown-it-math/temml'
import DOMPurify from 'dompurify'
import { API_BASE } from '../api'
import { useRefMapStore } from '../stores/refMap'
import { linkRefs, replaceRefTags } from '../utils'

const question = ref('')
const answer = ref('')
const loading = ref(false)
const files = ref<string[]>([])
const selected = ref('')
const refMap = useRefMapStore()

const dialog = ref(false)
const refContent = ref('')

const md = new MarkdownIt({ html: false, linkify: true, typographer: true }).use(markdownItMathTemml, { inlineAllowWhiteSpacePadding: true })

function renderMarkdown(text: string, id = ''): string {
  const raw = md.render(text)
  let sanitized = DOMPurify.sanitize(raw)
  sanitized = replaceRefTags(sanitized, refMap.refMap)
  return linkRefs(sanitized, refMap.refMap, id)
}

async function solve() {
  if (!question.value.trim() || !selected.value) return
  loading.value = true
  try {
    const res = await fetch(`${API_BASE}/solve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ file_id: selected.value, question: question.value })
    })
    const data = await res.json()
    answer.value = data.answer || ''
    await loadRefMap()
  } catch (err) {
    console.error(err)
    answer.value = ''
  } finally {
    loading.value = false
  }
}

async function loadFiles() {
  try {
    const res = await fetch(`${API_BASE}/list_files`)
    const data = await res.json()
    files.value = data.files || []
    if (files.value.length && !selected.value) {
      selected.value = files.value[0]
    }
    await loadRefMap()
  } catch (err) {
    console.error(err)
  }
}

async function loadRefMap() {
  if (!selected.value) return
  try {
    const res = await fetch(`${API_BASE}/list_chunks?file_id=${selected.value}`)
    const data = await res.json()
    const idMap: Record<string, any> = {}
    const refMapData: Record<string, Record<string, string>> = {}
    for (const c of data.chunks || []) {
      idMap[c.id] = c
      const type = c.chunk_type?.toLowerCase()
      const num = c.number
      if (type && num) {
        if (!refMapData[type]) refMapData[type] = {}
        refMapData[type][num] = c.id
      }
    }
    refMap.setMap(idMap, refMapData)
  } catch (err) {
    console.error(err)
  }
}

async function loadRef(id: string) {
  try {
    const res = await fetch(`${API_BASE}/list_chunks?file_id=${selected.value}`)
    const data = await res.json()
    const item = (data.chunks || []).find((c: any) => c.id === id)
    if (item) {
      refContent.value = item.content
      dialog.value = true
    }
  } catch (err) {
    console.error(err)
  }
}

function onClickRef(e: MouseEvent) {
  const target = (e.target as HTMLElement).closest('.ref-link') as HTMLElement | null
  if (target) {
    const idAttr = target.getAttribute('data-id')
    let id = idAttr || ''
    if (!id) {
      const type = target.getAttribute('data-type') || ''
      const num = target.getAttribute('data-num') || ''
      id = refMap.refMap[type]?.[num] || ''
    }
    if (id) {
      const chunk = refMap.idMap[id]
      if (chunk) {
        refContent.value = chunk.content
        dialog.value = true
      } else {
        loadRef(id)
      }
    }
  }
}

onMounted(loadFiles)
watch(selected, () => {
  loadRefMap()
})
</script>

<style scoped>
.solve-view {
  padding: 1rem;
  width: 100%;
}
</style>
