<template>
  <v-slide-x-reverse-transition>
    <v-sheet class="pdf-viewer" v-if="fileId" elevation="2">
      <v-btn icon class="close-btn" @click="viewer.setFile('')">
        <v-icon>mdi-close</v-icon>
      </v-btn>
      <iframe
        :key="reloadKey"
        :src="viewerSrc"
        style="width: 100%; height: 100vh; border: none;"
      />
    </v-sheet>
  </v-slide-x-reverse-transition>
</template>

<script setup lang="ts">
import { computed, watch, ref } from 'vue'
import { API_BASE } from '../api'
import { useViewerStore } from '../stores/viewer'

const viewer = useViewerStore()
const fileId = computed(() => viewer.fileId)
const fileUrl = computed(() => fileId.value ? `${API_BASE}/files/${fileId.value}.pdf` : '')
const viewerSrc = computed(() =>
  fileId.value
    ? `/pdfjs/viewer.html?file=${encodeURIComponent(fileUrl.value)}#page=${viewer.page}`
    : ''
)

const reloadKey = ref(0)
watch(() => viewer.page, () => {
  reloadKey.value++
})
</script>

<style scoped>
.pdf-viewer {
  width: 50%;
  padding: 1rem;
  position: relative;
}
.close-btn {
  position: absolute;
  top: 0;
  right: 0;
  z-index: 1;
}
</style>

