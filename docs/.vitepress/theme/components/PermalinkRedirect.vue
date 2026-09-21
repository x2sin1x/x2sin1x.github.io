<script setup lang="ts">
import { onMounted } from "vue";
import { useRouter, withBase } from "vitepress";

/**
 * 旧地址客户端重定向：主题的文章卡片组件（article-info，scope=post）硬编码了
 * /tags?tag=、/categories?category= 链接且无配置项。博客标签 / 分类页位于
 * /posts/tags、/posts/categories，用该组件在旧地址保留兼容并携带查询参数
 * （?tag=xxx / ?category=xxx），确保筛选状态不丢失。
 */
const props = defineProps<{ target: string }>();
const router = useRouter();

onMounted(() => {
  router.go(withBase(props.target) + window.location.search);
});
</script>

<template>
  <p class="redirect-tip">
    页面已迁移，正在跳转至 <a :href="props.target">{{ props.target }}</a> …
  </p>
</template>

<style scoped>
.redirect-tip {
  color: var(--vp-c-text-2);
}
</style>
