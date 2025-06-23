<template>
  <div class="upload-view">
    <input type="file" @change="onChange" />
    <button @click="upload">上传</button>
    <pre v-if="result">{{ JSON.stringify(result, null, 2) }}</pre>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useParseStore } from '../stores/parse'

const file = ref<File | null>(null)
const store = useParseStore()
const result = computed(() => store.result)

function onChange(e: Event) {
  const target = e.target as HTMLInputElement
  if (target.files && target.files[0]) {
    file.value = target.files[0]
  }
}

async function upload() {
  if (!file.value) return
  const formData = new FormData()
  formData.append('file', file.value)
  try {
    const res = await fetch('http://localhost:8000/parse', {
      method: 'POST',
      body: formData
    })
    if (!res.ok) throw new Error('上传失败')
    const data = await res.json()
    store.setResult(data)
  } catch (err) {
    console.error(err)
  }
}
</script>
