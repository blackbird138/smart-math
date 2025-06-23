<template>
  <div class="layout">
    <div class="main">
      <router-view />
    </div>
    <PdfViewer />
  </div>
</template>

<script setup lang="ts">
import PdfViewer from './components/PdfViewer.vue'
</script>

<style scoped>
.layout {
  display: flex;
}
.main {
  flex: 1;
  padding-right: 1rem;
}
</style>
