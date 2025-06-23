import { defineStore } from 'pinia'

export const useParseStore = defineStore('parse', {
  state: () => ({
    result: null as any,
    fileId: ''
  }),
  actions: {
    setResult(data: any) {
      this.result = data
    },
    setFileId(id: string) {
      this.fileId = id
    }
  }
})
