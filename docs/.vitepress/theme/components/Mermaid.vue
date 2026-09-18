<script setup lang="ts">
// Mermaid 图表组件，渲染方式与官方文档保持一致：
// https://mermaid.ai/open-source/config/usage.html
// 1. 组件输出官方约定的图表定义元素 <pre class="mermaid">源码</pre>（SSR 可见，无 JS 时回退为源码）；
// 2. mermaid.initialize({ startOnLoad: false }) 关闭文档加载后自动渲染，
//    挂载后调用官方 v10+ 首选的 mermaid.run({ nodes: [...] }) 渲染
//    （对应官方 "Render all elements passed as an array" 示例）；
// 3. 渲染失败时（suppressErrorRendering）元素保留原始源码作为回退展示。
// 触发点挂在组件生命周期（onMounted）上：VitePress 保证此时元素已插入 DOM，
// 路由切换时组件随页面销毁重建；修复了全局运行器首屏时序竞争导致渲染失败的问题。
import { onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useData } from "vitepress";
import type { Mermaid } from "mermaid";

const props = defineProps<{ source: string }>();
const { isDark } = useData();
const target = ref<HTMLElement>();
let disposed = false;
// 串行化渲染任务，避免主题快速切换时多次 run 交叉执行、旧主题结果覆盖新主题
let pending: Promise<void> = Promise.resolve();

// fence 渲染时源码经 base64 编码内联，避免 HTML 转义与 mermaid 语法冲突
const code = new TextDecoder().decode(Uint8Array.from(atob(props.source), (c) => c.charCodeAt(0)));

let mermaidPromise: Promise<Mermaid> | undefined;

/**
 * 按需动态加载 mermaid（体积较大，拆成独立 chunk，仅在页面真正出现 mermaid 图时才下载）
 */
function ensureMermaid(): Promise<Mermaid> {
  mermaidPromise ??= import("mermaid").then((m) => m.default);
  return mermaidPromise;
}

function enqueueRun(): void {
  pending = pending
    .then(async () => {
      if (disposed) return;
      const element = target.value;
      if (!element) return;
      const mermaid = await ensureMermaid();
      if (disposed) return;
      mermaid.initialize({
        // 关闭文档加载后自动渲染，改由组件在挂载后显式调用（官方推荐的自定义渲染方式）
        startOnLoad: false,
        // 渲染失败时不向元素插入 mermaid 错误 SVG，元素保留原始源码作为回退展示
        suppressErrorRendering: true,
        theme: isDark.value ? "dark" : "default",
      });
      // run 只处理不带 data-processed 的元素；重跑前还原源码并清除标记
      element.innerHTML = code;
      element.removeAttribute("data-processed");
      await mermaid.run({ nodes: [element], suppressErrors: true });
    })
    .catch(() => {});
}

onMounted(enqueueRun);
// 跟随站点的明暗主题切换重新渲染，保证图表配色与主题一致
watch(isDark, enqueueRun);

onBeforeUnmount(() => {
  disposed = true;
});
</script>

<template>
  <pre ref="target" class="mermaid">{{ code }}</pre>
</template>
