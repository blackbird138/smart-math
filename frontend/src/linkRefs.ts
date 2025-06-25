export function linkRefs(html: string): string {
  const pattern = /\[\[(.+?)\]\]/g
  return html.replace(pattern, (_, ref) => {
    const encoded = encodeURIComponent(ref)
    return `<a href="#/chunks?ref=${encoded}">${ref}</a>`
  })
}
