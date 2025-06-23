import { defineStore } from 'pinia'

export const useParseStore = defineStore('parse', {
  state: () => ({
    result: null as any
  }),
  actions: {
    setResult(data: any) {
      this.result = data
    }
  }
})
