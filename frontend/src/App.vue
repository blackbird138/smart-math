<template>
  <v-app>
    <v-app-bar app color="primary" dark>
      <v-toolbar-title>Smart Math</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn to="/" variant="text">首页</v-btn>
      <v-btn to="/upload" variant="text">上传</v-btn>
      <v-btn to="/search" variant="text">搜索</v-btn>
      <v-btn to="/chunks" variant="text">Chunk 图</v-btn>
    </v-app-bar>
    <v-main>
      <v-container fluid class="d-flex">
        <div class="view-area">
          <router-view v-slot="{ Component }">
            <v-fade-transition mode="out-in">
              <component :is="Component" />
            </v-fade-transition>
          </router-view>
        </div>
        <PdfViewer />
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import { watch } from 'vue'
import { useRoute } from 'vue-router'
import PdfViewer from './components/PdfViewer.vue'
import { useViewerStore } from './stores/viewer'

const route = useRoute()
const viewer = useViewerStore()

watch(() => route.fullPath, () => {
  viewer.setFile('')
})
</script>

<style>
body {
  margin: 0;
}
.view-area {
  width: 50%;
}
</style>
