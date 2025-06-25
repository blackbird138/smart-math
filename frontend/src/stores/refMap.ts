import { defineStore } from 'pinia'

export const useRefMapStore = defineStore('refMap', {
  state: () => ({
    map: {} as Record<string, any>
  }),
  actions: {
    setMap(data: Record<string, any>) {
      this.map = data
    }
  }
})
