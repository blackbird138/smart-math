<template>
  <v-container class="chunk-graph-view">
    <v-select
      v-model="selectedFile"
      :items="files"
      label="选择文件"
      class="mb-4"
      @update:modelValue="loadChunks"
    />
    <v-list v-if="chunks.length">
      <v-list-item v-for="c in chunks" :key="c.id">
        <v-list-item-title>
          <a href="#" @click.prevent="showRelated(c.id)">{{ c.summary || c.id }}</a>
        </v-list-item-title>
      </v-list-item>
    </v-list>
    <p v-else>暂无chunk</p>

    <div v-if="relatedChunks.length" class="mt-4">
      <h3>相关 chunk</h3>
      <v-list>
        <v-list-item v-for="r in relatedChunks" :key="r.id">
          {{ r.summary || r.id }}<span v-if="r.relation"> ({{ r.relation }})</span>
        </v-list-item>
      </v-list>
    </div>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { API_BASE } from '../api'

const files = ref<string[]>([])
const selectedFile = ref('')
const chunks = ref<any[]>([])
const relatedChunks = ref<any[]>([])

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
  relatedChunks.value = []
  if (!selectedFile.value) return
  const res = await fetch(`${API_BASE}/list_chunks?file_id=${selectedFile.value}`)
  const data = await res.json()
  chunks.value = data.chunks || []
}

async function showRelated(id: string) {
  const res = await fetch(`${API_BASE}/list_related?file_id=${selectedFile.value}&chunk_id=${id}`)
  const data = await res.json()
  relatedChunks.value = data.related || []
}

onMounted(loadFiles)
</script>

<style scoped>
.chunk-graph-view {
  padding: 1rem;
}
</style>
