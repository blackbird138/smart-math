<template>
  <v-container class="search-view" @click="onClickRef">
    <v-row class="align-center">
      <v-col cols="12" md="4">
        <v-select
          v-model="selected"
          :items="files"
          label="选择文件"
          density="comfortable"
        />
      </v-col>
      <v-col cols="12" md="6">
        <v-text-field
          v-model="query"
          label="输入查询"
          @keyup.enter="search"
          density="comfortable"
        />
      </v-col>
      <v-col cols="12" md="2">
        <v-btn
          color="primary"
          class="mt-2 mt-md-0"
          @click="search"
          :loading="loading"
          >搜索</v-btn
        >
      </v-col>
    </v-row>
    <v-progress-linear indeterminate class="mt-4" v-if="loading" />
    <v-expansion-panels
      class="mt-4 result-panels"
      v-else-if="results.length > 0"
      v-model="expanded"
      multiple
    >
      <v-expansion-panel
        v-for="(item, i) in results"
        :key="i"
        :value="item.metadata.chunk_id"
        elevation="2"
        class="mb-2"
      >
        <template #title>
          <div class="panel-title">
            <strong
              >{{ displayChunkType(item.metadata.chunk_type) }}:
              {{
                item.metadata.summary || item.text.slice(0, 50) + "..."
              }}</strong
            >
          </div>
        </template>
        <template #text>
          <div v-html="renderMarkdown(item.text, item.metadata.chunk_id)"></div>
          <div class="d-flex justify-end mt-2">
            <v-btn
              size="small"
              color="primary"
              @click="open(item.metadata.file_id, item.metadata.page_num + 1)"
            >
              加载 PDF 第 {{ item.metadata.page_num + 1 }} 页
            </v-btn>
          </div>
          <div
            class="mt-4"
            v-if="related[item.metadata.chunk_id]?.loading || related[item.metadata.chunk_id]?.items.length"
          >
            <h4>相关词条</h4>
            <v-progress-circular indeterminate v-if="related[item.metadata.chunk_id]?.loading" />
            <v-expansion-panels v-else multiple>
              <v-expansion-panel v-for="r in related[item.metadata.chunk_id]?.items" :key="r.id">
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
    <p v-else class="mt-4">暂无结果</p>
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
const query = ref("");
const results = ref<any[]>([]);

const loading = ref(false);
const files = ref<string[]>([]);
const selected = ref("");
const expanded = ref<string[]>([]);
const related = ref<Record<string, { loading: boolean; items: any[] }>>({});
const viewer = useViewerStore();
const refMap = useRefMapStore();

const md = new MarkdownIt({
  html: false,
  linkify: true,
  typographer: true,
}).use(markdownItMathTemml, { inlineAllowWhiteSpacePadding: true });

const dialog = ref(false);
const refContent = ref("");

function renderMarkdown(text: string, id = ""): string {
  const rawHtml = md.render(text);
  const sanitized = DOMPurify.sanitize(rawHtml);
  return linkRefs(sanitized, refMap.refMap, id);
}

async function search() {
  if (!query.value.trim()) return;
  loading.value = true;
  try {
    const res = await fetch(
      `${API_BASE}/search?file_id=${selected.value}&q=${encodeURIComponent(query.value)}`,
    );
    const data = await res.json();
    results.value = data.results || [];
    expanded.value = [];
    related.value = {};
    await loadRefMap();
  } catch (err) {
    console.error(err);
    results.value = [];
  } finally {
    loading.value = false;
  }
}

async function loadRelated(id: string) {
  if (related.value[id]) return;
  related.value[id] = { loading: true, items: [] };
  try {
    const res = await fetch(
      `${API_BASE}/list_related?file_id=${selected.value}&chunk_id=${id}`,
    );
    const data = await res.json();
    related.value[id].items = data.related || [];
  } catch (err) {
    console.error(err);
    related.value[id].items = [];
  } finally {
    related.value[id].loading = false;
  }
}

function open(id: string, page: number) {
  viewer.setFile(id, page);
}

async function loadRefMap() {
  if (!selected.value) return;
  try {
    const res = await fetch(
      `${API_BASE}/list_chunks?file_id=${selected.value}`,
    );
    const data = await res.json();
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
  } catch (err) {
    console.error(err);
  }
}

async function loadRef(id: string) {
  try {
    const res = await fetch(
      `${API_BASE}/list_chunks?file_id=${selected.value}`,
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

onMounted(async () => {
  try {
    const res = await fetch(`${API_BASE}/list_files`);
    const data = await res.json();
    files.value = data.files || [];
    if (files.value.length && !selected.value) {
      selected.value = files.value[0];
    }
    await loadRefMap();
  } catch (err) {
    console.error(err);
  }
});

watch(selected, () => {
  loadRefMap();
});

watch(
  expanded,
  (val) => {
    val.forEach((id) => loadRelated(id));
  },
  { deep: true },
);
</script>

<style scoped>
.search-view {
  padding: 1rem;
  width: 100%;
}
</style>
