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
