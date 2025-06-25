export function displayChunkType(type: string): string {
  const map: Record<string, string> = {
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
  definition: 'definition',
  def: 'definition',
  defn: 'definition',
  theorem: 'theorem',
  thm: 'theorem',
  lemma: 'lemma',
  lem: 'lemma',
  corollary: 'corollary',
  cor: 'corollary',
  example: 'example',
  ex: 'example',
  exercise: 'exercise',
  exer: 'exercise',
  remark: 'remark',
  rmk: 'remark',
};

export function linkRefs(
  html: string,
  refs: Record<string, Record<string, string>>
): string {
  const aliases = Object.keys(refAliases)
    .map(key => key.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'))
    .join('|');
  const regex = new RegExp(`\\b(${aliases})\\s*(\\d+(?:\\.\\d+)*)`, 'gi');
  return html.replace(regex, (match, alias, num) => {
    const type = refAliases[alias.toLowerCase()] || alias.toLowerCase();
    if (refs[type] && refs[type][num]) {
      return `<span class="ref-link" data-type="${type}" data-num="${num}">${match}</span>`;
    }
    return match;
  });
}
