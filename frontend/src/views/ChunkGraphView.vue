<template>
  <v-container class="chunk-graph-view" @click="onClickRef">
    <v-select
      v-model="selectedFile"
      :items="files"
      label="选择文件"
      class="mb-4"
      @update:modelValue="loadChunks"
    />
    <v-select
      v-model="selectedTypes"
      :items="chunkTypeItems"
      label="筛选类型"
      multiple
      chips
      clearable
      class="mb-4"
      @update:modelValue="loadChunks"
    />
    <v-progress-linear indeterminate v-if="loading" />
    <v-expansion-panels
      v-else-if="chunks.length"
      v-model="expanded"
      multiple
      class="mt-2"
    >
      <v-expansion-panel
        v-for="c in chunks"
        :key="c.id"
        class="mb-2"
        :value="c.id"
      >
        <template #title>
          <strong>
            {{ displayChunkType(c.chunk_type) }}
            <template v-if="c.number"> {{ c.number }}</template>
            : {{ c.summary || c.content.slice(0, 50) + "..." }}
          </strong>
        </template>
        <template #text>
          <div v-html="renderMarkdown(c.content, c.id)" />
          <div class="d-flex justify-end mt-2">
            <v-btn
              size="small"
              color="primary"
              @click="openPdf(c.page_num + 1)"
            >
              查看 PDF 第 {{ c.page_num + 1 }} 页
            </v-btn>
          </div>
          <div
            class="mt-4"
            v-if="related[c.id]?.loading || related[c.id]?.items.length"
          >
            <h4>相关词条</h4>
            <v-progress-circular indeterminate v-if="related[c.id]?.loading" />
            <v-expansion-panels v-else multiple>
              <v-expansion-panel v-for="r in related[c.id]?.items" :key="r.id">
                <template #title>
                  <strong>{{ r.relation }}: {{ r.summary || r.id }}</strong>
                </template>
                <template #text>
                  <div v-html="renderMarkdown(r.relation_summary, r.id)" />
                </template>
              </v-expansion-panel>
            </v-expansion-panels>
          </div>
        </template>
      </v-expansion-panel>
    </v-expansion-panels>
    <p v-else>暂无chunk</p>
    <v-dialog v-model="dialog" max-width="600">
      <v-card>
        <v-card-text @click="onClickRef">
          <div v-html="renderMarkdown(refContent)" />
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from "vue";
import MarkdownIt from "markdown-it";
import markdownItMathTemml from "markdown-it-math/temml";
import DOMPurify from "dompurify";
import { API_BASE } from "../api";
import { useViewerStore } from "../stores/viewer";
import { useRefMapStore } from "../stores/refMap";
import { displayChunkType, linkRefs } from "../utils";

const files = ref<string[]>([]);
const selectedFile = ref("");
const selectedTypes = ref<string[]>([]);
const chunkTypeItems = [
  "definition",
  "theorem",
  "lemma",
  "corollary",
  "example",
  "exercise",
  "remark",
].map((t) => ({ value: t, title: displayChunkType(t) }));
const chunks = ref<any[]>([]);
const loading = ref(false);
const expanded = ref<string[]>([]);
const related = ref<Record<string, { loading: boolean; items: any[] }>>({});
const viewer = useViewerStore();
const refMap = useRefMapStore();

const dialog = ref(false);
const refContent = ref("");

const md = new MarkdownIt({
  html: false,
  linkify: true,
  typographer: true,
}).use(markdownItMathTemml, { inlineAllowWhiteSpacePadding: true });

function renderMarkdown(text: string, id = ""): string {
  const raw = md.render(text);
  const sanitized = DOMPurify.sanitize(raw);
  return linkRefs(sanitized, refMap.refMap, id);
}

async function loadFiles() {
  const res = await fetch(`${API_BASE}/list_files`);
  const data = await res.json();
  files.value = data.files || [];
  if (files.value.length && !selectedFile.value) {
    selectedFile.value = files.value[0];
    loadChunks();
  }
}

async function loadChunks() {
  loading.value = true;
  related.value = {};
  if (!selectedFile.value) return;
  try {
    const typeParam = selectedTypes.value.length
      ? `&chunk_type=${selectedTypes.value.join(",")}`
      : "";
    const res = await fetch(
      `${API_BASE}/list_chunks?file_id=${selectedFile.value}${typeParam}`,
    );
    const data = await res.json();
    chunks.value = data.chunks || [];
    const idMap: Record<string, any> = {};
    const refMapData: Record<string, Record<string, string>> = {};
    for (const c of data.chunks || []) {
      idMap[c.id] = c;
      const type = c.chunk_type?.toLowerCase();
      const num = c.number;
      if (type && num) {
        if (!refMapData[type]) refMapData[type] = {};
        refMapData[type][num] = c.id;
      }
    }
    refMap.setMap(idMap, refMapData);
  } finally {
    loading.value = false;
  }
}

async function loadRelated(id: string) {
  if (related.value[id]) return;
  related.value[id] = { loading: true, items: [] };
  try {
    const res = await fetch(
      `${API_BASE}/list_related?file_id=${selectedFile.value}&chunk_id=${id}`,
    );
    const data = await res.json();
    related.value[id].items = data.related || [];
    refMap.mergeItems(related.value[id].items);
  } catch (err) {
    console.error(err);
    related.value[id].items = [];
  } finally {
    related.value[id].loading = false;
  }
}

function openPdf(page: number) {
  viewer.setFile(selectedFile.value, page);
}

async function loadRef(id: string) {
  try {
    const res = await fetch(
      `${API_BASE}/list_chunks?file_id=${selectedFile.value}`,
    );
    const data = await res.json();
    const item = (data.chunks || []).find((c: any) => c.id === id);
    if (item) {
      refContent.value = item.content;
      dialog.value = true;
    }
  } catch (err) {
    console.error(err);
  }
}

function onClickRef(e: MouseEvent) {
  const target = (e.target as HTMLElement).closest(
    ".ref-link",
  ) as HTMLElement | null;
  if (target) {
    const idAttr = target.getAttribute("data-id");
    let id = idAttr || "";
    if (!id) {
      const type = target.getAttribute("data-type") || "";
      const num = target.getAttribute("data-num") || "";
      id = refMap.refMap[type]?.[num] || "";
    }
    if (id) {
      const chunk = refMap.idMap[id];
      if (chunk) {
        refContent.value = chunk.content;
        dialog.value = true;
      } else {
        loadRef(id);
      }
    }
  }
}

watch(expanded, (val) => {
  val.forEach((id) => loadRelated(id));
});

watch(selectedTypes, () => {
  loadChunks();
});

onMounted(loadFiles);
</script>

<style scoped>
.chunk-graph-view {
  padding: 1rem;
}
</style>
