<template>
  <v-container class="upload-view">
    <v-file-input label="选择PDF" accept=".pdf" @change="onChange" />
    <v-btn color="primary" class="mt-2" @click="upload" :loading="isUploading" :disabled="!file">上传</v-btn>
    <v-alert type="success" class="mt-2" v-if="success">上传成功，ID: {{ success }}</v-alert>
    <pdf-embed v-if="previewUrl" :source="previewUrl" style="width: 100%; height: 60vh;" class="mt-4" />
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onBeforeUnmount } from 'vue'
import PdfEmbed from 'vue-pdf-embed'
import { useParseStore } from '../stores/parse'
import { API_BASE } from '../api'

const file = ref<File | null>(null)
const store = useParseStore()
const result = computed(() => store.result)
const previewUrl = ref<string | null>(null)
const isUploading = ref(false)
const success = ref<string | null>(null)

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
    success.value = null
    isUploading.value = true
    const res = await fetch(`${API_BASE}/ingest`, {
      method: 'POST',
      body: formData
    })
    if (!res.ok) throw new Error('上传失败')
    const data = await res.json()
    store.setResult(data)
    store.setFileId(data.file_id)
    success.value = data.file_id
  } catch (err) {
    console.error(err)
  } finally {
    isUploading.value = false
  }
}
</script>

<style scoped>
.upload-view {
  padding: 1rem;
}
</style>
