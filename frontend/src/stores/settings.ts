import { defineStore } from "pinia";

export const useSettingsStore = defineStore("settings", {
  state: () => ({
    SILICONFLOW_API_KEY: "",
    OPENAI_COMPATIBILITY_API_KEY: "",
  }),
  persist: true,
});
