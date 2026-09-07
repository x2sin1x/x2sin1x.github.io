<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { withBase } from 'vitepress'

type AbcJs = {
  renderAbc: (
    target: HTMLElement,
    source: string,
    options?: { responsive?: "resize" | "resize-overflow" }
  ) => void
}

const props = defineProps<{ source: string }>()
const target = ref<HTMLElement>()
let disposed = false

function currentAbcjs(): AbcJs | undefined {
  return (window as typeof window & { ABCJS?: AbcJs }).ABCJS
}

function waitScript(script: HTMLScriptElement): Promise<AbcJs | undefined> {
  return new Promise((resolve) => {
    script.addEventListener('load', () => resolve(currentAbcjs()), { once: true })
    script.addEventListener('error', () => resolve(undefined), { once: true })
  })
}

let abcjsReady: Promise<AbcJs | undefined> | undefined

function ensureAbcjs(): Promise<AbcJs | undefined> {
  abcjsReady ??= ((): Promise<AbcJs | undefined> => {
    const ready = currentAbcjs()
    if (ready) return Promise.resolve(ready)
    const existing = document.querySelector<HTMLScriptElement>('script[src*="abcjs-basic-min"]')
    if (existing) return waitScript(existing)
    const script = document.createElement('script')
    script.src = withBase('/js/abcjs-basic-min.js')
    script.defer = true
    document.head.appendChild(script)
    return waitScript(script)
  })()
  return abcjsReady
}

onMounted(async () => {
  const abc = await ensureAbcjs()
  if (disposed || !abc || !target.value) return
  abc.renderAbc(target.value, decodeURIComponent(escape(atob(props.source))), {
    responsive: 'resize',
  })
})

onBeforeUnmount(() => {
  disposed = true
})
</script>
<template><div ref="target" class="abc-score" /></template>
