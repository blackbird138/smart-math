<template>
  <v-slide-x-reverse-transition>
    <v-sheet class="pdf-viewer" v-if="fileId" elevation="2">
      <pdf-embed
        :source="fileUrl"
        :page="page"
        style="width: 100%; height: 100vh;"
      />
    </v-sheet>
  </v-slide-x-reverse-transition>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import PdfEmbed from 'vue-pdf-embed'
import { API_BASE } from '../api'
import { useViewerStore } from '../stores/viewer'

const viewer = useViewerStore()
const fileId = computed(() => viewer.fileId)
const page = computed(() => viewer.page)
const fileUrl = computed(() => fileId.value ? `${API_BASE}/files/${fileId.value}.pdf` : '')
</script>

<style scoped>
.pdf-viewer {
  width: 50%;
  padding: 1rem;
}
</style>

