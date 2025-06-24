import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import UploadView from '../views/UploadView.vue'
import SearchView from '../views/SearchView.vue'
import DocumentView from '../views/DocumentView.vue'
import ChunkGraphView from '../views/ChunkGraphView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/upload',
    name: 'upload',
    component: UploadView
  },
  {
    path: '/search',
    name: 'search',
    component: SearchView
  },
  {
    path: '/document/:id',
    name: 'document',
    component: DocumentView
  },
  {
    path: '/chunks',
    name: 'chunks',
    component: ChunkGraphView
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
