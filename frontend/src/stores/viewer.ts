import { defineStore } from "pinia";

export const useViewerStore = defineStore("viewer", {
  state: () => ({
    fileId: "" as string,
    page: 1,
    collapsed: false,
  }),
  actions: {
    setFile(id: string, page = 1) {
      this.fileId = id;
      this.page = page;
    },
    toggleCollapsed() {
      this.collapsed = !this.collapsed;
    },
    setCollapsed(val: boolean) {
      this.collapsed = val;
    },
    setPage(page: number) {
      this.page = page;
    },
  },
});
