<template>
  <v-container class="settings-view">
    <v-text-field
      v-model="store.SILICONFLOW_API_KEY"
      label="SILICONFLOW_API_KEY"
      clearable
    />
    <v-text-field
      v-model="store.OPENAI_COMPATIBILITY_API_KEY"
      label="OPENAI_COMPATIBILITY_API_KEY"
      clearable
    />
    <v-btn class="mt-2" @click="save">保存</v-btn>
  </v-container>
</template>

<script setup lang="ts">
import { useSettingsStore } from "../stores/settings";
import { updateEnv } from "../api";

const store = useSettingsStore();

async function save() {
  await updateEnv({
    SILICONFLOW_API_KEY: store.SILICONFLOW_API_KEY,
    OPENAI_COMPATIBILITY_API_KEY: store.OPENAI_COMPATIBILITY_API_KEY,
  });
}
</script>

<style scoped>
.settings-view {
  padding: 1rem;
  width: 50%;
}
</style>
