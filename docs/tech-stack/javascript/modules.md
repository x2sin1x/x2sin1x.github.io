---
title: JavaScript 模块
weight: 90
---

# JavaScript 模块

> 本节目标：使用 ES 模块拆分代码，以命名导出、默认导出和动态导入管理依赖。

## 命名导出和导入

模块文件可导出多个具名值。导入时名称需匹配，可用 `as` 重命名：

```js
// math.js
export function add(a, b) {
  return a + b;
}
```

```js
// app.js
import { add as sum } from "./math.js";
console.log(sum(2, 3)); // 5
```

静态 `import` 通常放在模块顶层，依赖关系可在执行前分析。相对路径需以 `./` 或 `../` 开头。

## 默认导出和重导出

每个模块最多有一个默认导出。导入时调用方可自选名称；具名导出则保留一致的 API 名称。大型项目常用入口模块集中重导出，但避免过度隐藏依赖来源。

```js
// greeting.js
export default function greeting(name) {
  return `你好，${name}`;
}
```

```js
import greeting from "./greeting.js";
```

## 浏览器和 Node.js

浏览器通过 `<script type="module" src="./app.js"></script>` 加载入口模块。模块默认启用严格模式，并有自己的作用域。Node.js 支持 ES 模块；`.mjs` 扩展名或 `package.json` 的 `"type": "module"` 可指定模块格式。ESM 与旧式 CommonJS 的边界需按工具和运行时文档处理。

开发阶段可使用原生模块；复杂项目可采用构建工具，但模块本身不依赖某一个打包器。npm 包管理和 `package.json` 不属于 ECMAScript 规范，按 [npm 文档](https://docs.npmjs.com/)查阅。

## 动态导入

`import()` 返回 Promise，可按需加载模块，常用于较少访问的功能或路由：

```js
const { renderReport } = await import("./report.js");
renderReport();
```

动态导入的路径受宿主和打包工具规则影响。不要把未经验证的用户输入直接作为模块路径。

## 小结与练习

- ES 模块使用 `export` 暴露功能，用 `import` 引入依赖。
- 静态导入便于分析依赖，`import()` 用于按需加载。
- 模块语法由 ECMAScript 定义，模块查找和包管理还受宿主环境影响。

练习：把格式化函数和数据分别放入模块，再创建入口文件导入并输出结果。
