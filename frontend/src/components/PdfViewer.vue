<template>
  <div class="viewer-container">
    <v-btn
      icon
      class="collapse-btn"
      v-show="!viewer.collapsed"
      @click="viewer.toggleCollapsed()"
    >
      <v-icon>{{
        viewer.collapsed ? "mdi-chevron-left" : "mdi-chevron-right"
      }}</v-icon>
    </v-btn>
    <v-slide-x-reverse-transition>
      <v-sheet
        class="pdf-viewer"
        v-if="fileId && !viewer.collapsed"
        elevation="2"
      >
        <iframe
          :key="reloadKey"
          :src="viewerSrc"
          style="width: 100%; height: 100vh; border: none"
        />
      </v-sheet>
    </v-slide-x-reverse-transition>
  </div>
</template>

<script setup lang="ts">
import { computed, watch, ref } from "vue";
import { API_BASE } from "../api";
import { useViewerStore } from "../stores/viewer";

const viewer = useViewerStore();
const fileId = computed(() => viewer.fileId);
const fileUrl = computed(() =>
  fileId.value ? `${API_BASE}/files/${fileId.value}.pdf` : "",
);
const viewerSrc = computed(() =>
  fileId.value
    ? `/pdfjs/viewer.html?file=${encodeURIComponent(fileUrl.value)}#page=${viewer.page}`
    : "",
);

const reloadKey = ref(0);
watch(
  () => viewer.page,
  () => {
    reloadKey.value++;
  },
);
</script>

<style scoped>
.viewer-container {
  position: sticky;
  top: 0;
  width: 50%;
  height: 100vh;
}
.pdf-viewer {
  width: 100%;
  padding: 1rem;
  position: relative;
}
.collapse-btn {
  position: absolute;
  left: -20px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 2;
}
</style>
