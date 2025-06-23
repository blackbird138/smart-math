import { defineStore } from 'pinia'

export const useViewerStore = defineStore('viewer', {
  state: () => ({
    fileId: '' as string,
    page: 1
  }),
  actions: {
    setFile(id: string, page = 1) {
      this.fileId = id
      this.page = page
    },
    setPage(page: number) {
      this.page = page
    }
  }
})
