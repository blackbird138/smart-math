export function displayChunkType(type: string): string {
  const map: Record<string, string> = {
    proposition: "命题",
    definition: "定义",
    defination: "定义",
    theorem: "定理",
    lemma: "引理",
    corollary: "推论",
    example: "例子",
    exercise: "练习",
    remark: "注",
  };
  return map[type?.toLowerCase()] || type;
}

export const refAliases: Record<string, string> = {
  definition: "definition",
  定义: "definition",
  def: "definition",
  defn: "definition",
  theorem: "theorem",
  定理: "theorem",
  thm: "theorem",
  lemma: "lemma",
  引理: "lemma",
  lem: "lemma",
  corollary: "corollary",
  推论: "corollary",
  cor: "corollary",
  example: "example",
  例: "example",
  例子: "example",
  ex: "example",
  exercise: "exercise",
  练习: "exercise",
  exer: "exercise",
  remark: "remark",
  注: "remark",
  rmk: "remark",
  proposition: "proposition",
  命题: "proposition",
  prop: "proposition",
};

export function linkRefs(
  html: string,
  refs: Record<string, Record<string, string>>,
  currentId = "",
): string {
  const aliases = Object.keys(refAliases)
    .map((key) => key.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"))
    .join("|");
  const regex = new RegExp(`(${aliases})\\s*(\\d+(?:\\.\\d+)*)`, "gi");
  return html.replace(regex, (match, alias, num) => {
    const type = refAliases[alias.toLowerCase()] || alias.toLowerCase();
    const id = refs[type]?.[num];
    if (id) {
      if (id === currentId) {
        return `<span class="ref-self chip">${match}</span>`;
      }
      return `<span class="ref-link chip" data-type="${type}" data-num="${num}" data-id="${id}">${match}</span>`;
    }
    return match;
  });
}

export function replaceRefTags(
  html: string,
  refs: Record<string, Record<string, string>>,
): string {
  const valid = /\[REF:([^/\n]+)\/([^/\n]+)\/([^\]\n]*)\]/gi;
  html = html.replace(valid, (_, type, num, summary) => {
    const lower = type.toLowerCase();
    const id = refs[lower]?.[num];
    const display = `${displayChunkType(lower)} ${num}${summary ? ': ' + summary : ''}`;
    if (id) {
      return `<span class="ref-link chip" data-type="${lower}" data-num="${num}" data-id="${id}">${display}</span>`;
    }
    return `<span class="chip">${display}</span>`;
  });
  // 移除无法解析的 REF 标记但保留其他文本
  return html.replace(/\[REF:[^\n\]]*(?:\]|$)/gi, "");
}
