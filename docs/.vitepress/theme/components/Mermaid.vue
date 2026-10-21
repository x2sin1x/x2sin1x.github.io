<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useData } from "vitepress";
import type { Mermaid } from "mermaid";

const props = defineProps<{ source: string }>();
const { isDark } = useData();
const target = ref<HTMLElement>();
let disposed = false;
let renderQueue: Promise<void> = Promise.resolve();
let mermaidPromise: Promise<Mermaid> | undefined;

// 源码由 config.mts 进行 base64 编码，避免 Mermaid 语法与 HTML 转义冲突。
const code = new TextDecoder().decode(Uint8Array.from(atob(props.source), (char) => char.charCodeAt(0)));

function loadMermaid(): Promise<Mermaid> {
  mermaidPromise ??= import("mermaid").then((module) => module.default);
  return mermaidPromise;
}

function render(): void {
  renderQueue = renderQueue
    .then(async () => {
      const element = target.value;
      if (disposed || !element) return;

      const mermaid = await loadMermaid();
      if (disposed) return;

      mermaid.initialize({
        startOnLoad: false,
        suppressErrorRendering: true,
        theme: isDark.value ? "redux-dark-color" : "redux-color",
      });

      // run() 跳过已处理的节点；切换主题时先恢复源码并清除处理标记。
      element.textContent = code;
      element.removeAttribute("data-processed");
      await mermaid.run({ nodes: [element], suppressErrors: true });
    })
    .catch(() => {});
}

onMounted(render);
watch(isDark, render);

onBeforeUnmount(() => {
  disposed = true;
});
</script>

<template>
  <pre ref="target" class="mermaid">{{ code }}</pre>
</template>
