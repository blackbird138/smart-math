import { defineStore } from 'pinia'

export const useRefMapStore = defineStore('refMap', {
  state: () => ({
    /** 根据 chunk_id 存储完整的 chunk 数据 */
    idMap: {} as Record<string, any>,
    /** 按类型与编号索引 chunk_id */
    refMap: {} as Record<string, Record<string, string>>
  }),
  actions: {
    /**
     * 设置引用映射表
     * @param idMap 以 chunk_id 为键的 chunk 数据映射
     * @param refMap 按类型与编号索引的映射
     */
    setMap(idMap: Record<string, any>, refMap: Record<string, Record<string, string>>) {
      this.idMap = idMap
      this.refMap = refMap
    }
    ,
    /**
     * 合并新的引用映射
     * @param items 包含 id、chunk_type、number 等字段的数组
     */
    mergeItems(items: any[]) {
      for (const item of items) {
        if (!item?.id) continue
        this.idMap[item.id] = item
        const type = item.chunk_type?.toLowerCase()
        const num = item.number
        if (type && num) {
          if (!this.refMap[type]) this.refMap[type] = {}
          this.refMap[type][num] = item.id
        }
      }
    }
  }
})
