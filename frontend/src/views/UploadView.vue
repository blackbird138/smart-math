<template>
  <div class="upload-view">
    <input type="file" @change="onChange" />
    <button @click="upload">上传</button>
    <p v-if="result">文件已上传，ID: {{ store.fileId }}</p>
    <pdf-embed v-if="previewUrl" :source="previewUrl" style="width: 100%; height: 60vh;" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onBeforeUnmount } from 'vue'
import PdfEmbed from 'vue-pdf-embed'
import { useParseStore } from '../stores/parse'

const file = ref<File | null>(null)
const store = useParseStore()
const result = computed(() => store.result)
const previewUrl = ref<string | null>(null)

function onChange(e: Event) {
  const target = e.target as HTMLInputElement
  if (target.files && target.files[0]) {
    file.value = target.files[0]
    previewUrl.value = URL.createObjectURL(file.value)
  }
}

onBeforeUnmount(() => {
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
})

async function upload() {
  if (!file.value) return
  const formData = new FormData()
  formData.append('file', file.value)
  try {
    const res = await fetch('http://localhost:8001/ingest', {
      method: 'POST',
      body: formData
    })
    if (!res.ok) throw new Error('上传失败')
    const data = await res.json()
    store.setResult(data)
    store.setFileId(data.file_id)
  } catch (err) {
    console.error(err)
  }
}
</script>

<style scoped>
.upload-view {
  padding: 1rem;
}
</style>
