<template>
  <v-container class="document-view">
    <pdf-embed
      v-if="fileUrl"
      :source="fileUrl"
      :page="page"
      style="width: 100%; height: 80vh;"
    />
    <p v-else>未找到文档</p>
  </v-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import PdfEmbed from 'vue-pdf-embed'
import { API_BASE } from '../api'

const route = useRoute()
const page = computed(() => Number(route.query.page || 1))
const fileId = computed(() => route.params.id as string)
const fileUrl = computed(() => `${API_BASE}/files/${fileId.value}.pdf`)
</script>

<style scoped>
.document-view {
  padding: 1rem;
}
</style>
