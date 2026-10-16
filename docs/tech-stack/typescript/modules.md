---
title: 模块
weight: 80
---

# 模块

> 本节目标：使用 ES 模块组织实现和类型，并理解编译器如何解析模块边界。

## 导入与导出

含有顶层 `import` 或 `export` 的文件是模块；没有这些语法的文件会被视为脚本，其声明可能进入共享全局作用域。

```ts
// src/model.ts
export interface Task {
  id: number;
  title: string;
}

export function createTask(id: number, title: string): Task {
  return { id, title };
}
```

```ts
// src/index.ts
import { createTask, type Task } from "./model.js";

const task: Task = createTask(1, "读 Handbook");
console.log(task.title);
```

在 NodeNext 配置下，源文件导入写 `.js` 是常见做法：TypeScript 能对应解析 `.ts` 源文件，生成的导入路径则能被 Node.js 使用。打包器项目通常使用 `moduleResolution: "bundler"`，遵循各自工具的解析规则。

## 默认导出、重命名与类型导入

命名导出便于一个模块提供多个能力，也便于重命名：

```ts
import { createTask as makeTask } from "./model.js";
```

默认导出每个模块只能有一个。类型可使用 `import type` 或内联 `type` 修饰符明确标识；这样可以分清编译时类型和运行时值，尤其是在 `verbatimModuleSyntax` 等选项启用时。

```ts
import type { Task } from "./model.js";
```

`export type` 同样只导出类型。类型导入会在输出 JavaScript 中擦除，不能在运行时作为构造器或变量访问。

## 模块解析与项目边界

`module` 描述输出或理解的模块格式；`moduleResolution` 描述查找导入文件的规则。现代项目常见组合包括 Node.js 的 `NodeNext` 和 bundler 的 `ESNext` + `Bundler`；应根据实际运行器选择，而不是只凭教程复制。

`package.json` 的 `type` 字段会影响 Node.js 如何解释 `.js` 文件。TypeScript 与 Node 对模块的判断需要一致。包导出映射、条件导出和路径别名涉及运行时解析，编译器的 `paths` 不会自动重写生成代码中的导入路径。

## 模块扩展与声明文件

有时需要为第三方模块补充类型，或扩展其公开类型。声明合并和 `declare module` 属于进阶参考主题；应先确认目标包本身没有类型，再采用官方声明文件指南中的模式。不要随意把未知模块声明为 `any`，这会关闭类型检查。

## 常见错误

- **模块找得到但运行时报错**：检查 Node 的 `package.json`、扩展名和编译输出路径。
- **`paths` 别名运行时找不到**：别名只影响 TypeScript 解析，需由运行器或打包器配置对应映射。
- **把类型导入当作值使用**：类型会擦除，运行时需要真实导出。

## 小结与练习

- 用显式导入导出构造模块边界，避免脚本式全局声明。
- NodeNext 与 bundler 的模块规则不同，配置应和实际执行环境一致。
- 类型导入用于静态检查，不会生成运行时值。

练习：把上一章的 `Shape` 和 `Rectangle` 放入独立模块，并从入口文件导入、实例化。接下来可以阅读[TSConfig Reference](https://www.typescriptlang.org/tsconfig/)和[模块参考](https://www.typescriptlang.org/docs/handbook/modules/reference.html)，再完成自己的小型项目。
