<script lang="ts" setup>
// 可点击的导航下拉组件：
// VitePress 原生下拉菜单（VPNavBarMenuGroup）的标题是 <button>，无法跳转，
// 这里自定义实现 —— 桌面端单击标题跳转到总览页，hover 正常展开子菜单；
// 移动端（VPNavScreenMenu 传入 screen-menu 属性）单击标题跳转，右侧 + 号展开子项。
import { computed, inject, ref, useAttrs } from "vue";
import { useData } from "vitepress";
import type { DefaultTheme } from "vitepress";

defineOptions({ inheritAttrs: false });

const props = defineProps<{
  /** 菜单标题 */
  text: string;
  /** 单击标题时跳转的总览页链接 */
  link: string;
  /** 高亮匹配的正则字符串（与 NavItemWithLink.activeMatch 一致） */
  activeMatch?: string;
  /** 下拉子项 */
  items: DefaultTheme.NavItemWithLink[];
}>();

const attrs = useAttrs();
const isScreenMenu = computed(() => "screen-menu" in attrs);

const { page } = useData();
const closeScreen = inject<() => void>("close-screen", () => {});

/** 与 VitePress shared/isActive 行为一致的路径匹配 */
function normalize(path: string): string {
  return path
    .replace(/#.*$/, "")
    .replace(/\?.*$/, "")
    .replace(/\.(html|md)$/, "")
    .replace(/\/index$/, "/")
    .replace(/\/+$/, "/");
}

function isActive(link: string, activeMatch?: string): boolean {
  const current = `/${page.value.relativePath}`;
  if (activeMatch) return new RegExp(activeMatch).test(current);
  const target = normalize(link);
  if (target === "/") return current === "/";
  const prefix = target.endsWith("/") ? target : `${target}/`;
  return current === target || current.startsWith(prefix);
}

const isSelfActive = computed(() => isActive(props.link, props.activeMatch));
const isChildActive = computed(() =>
  props.items.some((item) => isActive(item.link, item.activeMatch)),
);
const isGroupActive = computed(() => isSelfActive.value || isChildActive.value);

// 桌面端：hover 展开由 CSS 控制，这里保留展开状态用于 aria 属性
const open = ref(false);

// 移动端抽屉菜单：子项展开状态
const isOpen = ref(false);
const groupId = computed(
  () => `NavScreenGroup-${props.text.replace(" ", "-").toLowerCase()}`,
);
function toggle() {
  isOpen.value = !isOpen.value;
}
</script>

<template>
  <!-- 桌面端导航栏：可跳转标题 + hover 下拉 -->
  <div
    v-if="!isScreenMenu"
    ref="el"
    class="nav-dropdown-flyout"
    :class="{ active: isGroupActive, open }"
    @mouseenter="open = true"
    @mouseleave="open = false"
  >
    <a class="button" :href="link" :aria-label="text">
      <span class="text">
        <span>{{ text }}</span>
        <span class="vpi-chevron-down text-icon" />
      </span>
    </a>

    <div class="menu">
      <div class="menu-panel">
        <a
          v-for="item in items"
          :key="item.link"
          class="menu-link"
          :class="{ 'menu-link-active': isActive(item.link, item.activeMatch) }"
          :href="item.link"
          :target="item.target"
          :rel="item.rel"
        >
          <span>{{ item.text }}</span>
        </a>
      </div>
    </div>
  </div>

  <!-- 移动端抽屉菜单：标题可跳转，+ 号展开子项 -->
  <div v-else class="nav-screen-group" :class="{ open: isOpen }">
    <div class="row">
      <a class="row-link" :href="link" @click="closeScreen">
        <span>{{ text }}</span>
      </a>
      <button
        type="button"
        class="row-toggle"
        :aria-controls="groupId"
        :aria-expanded="isOpen"
        :aria-label="`展开 ${text}`"
        @click="toggle"
      >
        <span class="vpi-plus row-icon" />
      </button>
    </div>

    <div :id="groupId" class="items">
      <a
        v-for="item in items"
        :key="item.link"
        class="item-link"
        :href="item.link"
        @click="closeScreen"
      >
        <span>{{ item.text }}</span>
      </a>
    </div>
  </div>
</template>

<style scoped>
/* ===== 桌面端：样式对齐 VPFlyout / VPMenu ===== */
.nav-dropdown-flyout {
  position: relative;
}

.nav-dropdown-flyout:hover .text {
  color: var(--vp-c-text-2);
}

.nav-dropdown-flyout.active .text {
  color: var(--vp-c-brand-1);
}

.nav-dropdown-flyout.active:hover .text {
  color: var(--vp-c-brand-2);
}

.button {
  display: flex;
  align-items: center;
  padding: 0 12px;
  height: var(--vp-nav-height);
  color: var(--vp-c-text-1);
  transition: color 0.5s;
}

.text {
  display: flex;
  align-items: center;
  line-height: var(--vp-nav-height);
  font-size: 14px;
  font-weight: 500;
  color: var(--vp-c-text-1);
  transition: color 0.25s;
}

.text-icon {
  margin-left: 4px;
  font-size: 14px;
}

.menu {
  position: absolute;
  top: calc(var(--vp-nav-height) / 2 + 20px);
  right: 0;
  opacity: 0;
  visibility: hidden;
  transform: translateY(0);
  transition:
    opacity 0.25s,
    visibility 0.25s,
    transform 0.25s;
  z-index: var(--vp-z-index-nav);
}

.nav-dropdown-flyout:hover .menu,
.nav-dropdown-flyout.open .menu {
  opacity: 1;
  visibility: visible;
}

.menu-panel {
  border-radius: 12px;
  padding: 12px;
  min-width: 128px;
  border: 1px solid var(--vp-c-divider);
  background-color: var(--vp-c-bg-elv);
  box-shadow: var(--vp-shadow-3);
  transition: background-color 0.5s;
  max-height: calc(100vh - var(--vp-nav-height));
  overflow-y: auto;
}

.menu-link {
  display: block;
  border-radius: 6px;
  padding: 0 12px;
  line-height: 32px;
  font-size: 14px;
  font-weight: 500;
  color: var(--vp-c-text-1);
  white-space: nowrap;
  transition:
    background-color 0.25s,
    color 0.25s;
}

.menu-link:hover {
  color: var(--vp-c-brand-1);
  background-color: var(--vp-c-default-soft);
}

.menu-link-active {
  color: var(--vp-c-brand-1);
}

/* ===== 移动端：样式对齐 VPNavScreenMenuGroup ===== */
.nav-screen-group {
  border-bottom: 1px solid var(--vp-c-divider);
  padding-bottom: 10px;
  transition: border-color 0.5s;
}

.row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 4px 11px 0;
  line-height: 24px;
  font-size: 14px;
  font-weight: 500;
  color: var(--vp-c-text-1);
  transition: color 0.25s;
}

.row-link {
  color: inherit;
  transition: color 0.25s;
}

.row-link:hover {
  color: var(--vp-c-brand-1);
}

.row-toggle {
  display: flex;
  align-items: center;
  padding: 4px;
  color: var(--vp-c-text-1);
  transition: color 0.25s;
}

.row-toggle:hover {
  color: var(--vp-c-brand-1);
}

.row-icon {
  transition: transform 0.25s;
}

.nav-screen-group.open .row-icon {
  transform: rotate(45deg);
}

.nav-screen-group.open .row {
  color: var(--vp-c-brand-1);
}

.items {
  visibility: hidden;
  display: none;
}

.nav-screen-group.open .items {
  visibility: visible;
  display: block;
}

.item-link {
  display: block;
  margin-left: 12px;
  line-height: 32px;
  font-size: 14px;
  font-weight: 400;
  color: var(--vp-c-text-1);
  transition: color 0.25s;
}

.item-link:hover {
  color: var(--vp-c-brand-1);
}
</style>
