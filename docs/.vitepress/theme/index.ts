// .vitepress/theme/index.ts
import type { Theme } from "vitepress";
import Teek from "vitepress-theme-teek";
import "vitepress-theme-teek/index.css";
import AbcScore from "./components/AbcScore.vue";

export default {
  extends: Teek,
  enhanceApp({ app }) {
    app.component("AbcScore", AbcScore);
  },
} satisfies Theme;
