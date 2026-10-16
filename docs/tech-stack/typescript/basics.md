---
title: 基础：理解 TypeScript 如何检查 JavaScript
weight: 10
---

# 基础：理解 TypeScript 如何检查 JavaScript

> 本节目标：解释 TypeScript 的编译与检查过程，并建立一个启用严格检查的最小项目。

## 类型检查发生在运行之前

JavaScript 的值在运行时具有行为；TypeScript 在编译前分析代码，判断这些操作是否合理。它不会给 JavaScript 值附加一套运行时类型，也不会自动验证 JSON、表单或网络响应。多数类型注解在输出 JavaScript 时会被擦除。

```ts
function repeat(text: string, count: number): string {
  return text.repeat(count);
}

console.log(repeat("TS", 2));
// repeat("TS", "2"); // 编译错误：第二个参数不是 number
```

类型系统能发现传参错误，但不能保证逻辑符合业务要求，例如数量应大于零仍需代码显式检查。

## 推断优先，必要时标注

根据初始值，检查器通常能推断变量类型：

```ts
let course = "TypeScript"; // 推断为 string
course = "JavaScript";
// course = 42; // 类型错误

const lessonCount = 8; // 常量可保留更精确的字面量类型 8
```

函数边界和复杂数据结构适合显式标注，简单局部变量通常让推断处理。这样代码既保留清晰契约，也不充斥重复信息。

## 使用 tsconfig.json

在项目根目录创建 `tsconfig.json` 后，`npx tsc` 会按项目配置检查文件。新项目建议启用 `strict`，并明确输入输出目录：

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "rootDir": "src",
    "outDir": "dist",
    "strict": true,
    "noEmitOnError": true
  },
  "include": ["src/**/*.ts"]
}
```

`strict` 打开一组更严格的检查，其中包括空值检查和函数参数检查。`target` 决定输出 JavaScript 语法目标；`module` 与 `moduleResolution` 应根据运行环境或打包器选择。不要把浏览器、Node.js 与 bundler 的配置机械混用，按[模块参考](https://www.typescriptlang.org/docs/handbook/modules/reference.html)核对。

## 检查、编译和运行

```shell
npx tsc --noEmit   # 只检查，不生成文件
npx tsc            # 按配置生成 JavaScript
node dist/index.js # 用 Node.js 执行生成文件
```

编译输出目录通常应加入 `.gitignore`。如果只有类型错误，先修正类型契约；不要把 `any` 或断言当作通用消错开关。

## TypeScript 6.0 提示

官方 6.0 发布说明记录了若干默认值变化，包括 `strict` 默认开启、`module` 默认 `esnext`、`target` 指向当前 ECMAScript 版本。项目显式写出关键选项，可避免升级编译器后依赖默认值而改变行为。Node 项目还应明确所需的 Node 类型，例如安装 `@types/node` 并设置 `types`。

## 常见错误

- **把类型检查当作输入校验**：类型注解会擦除；解析外部数据时仍要检查实际值。
- **用 `tsc file.ts` 检查整个项目**：命令行直接给文件名会采用命令行参数模式，可能不读取预期的项目配置。项目检查使用 `npx tsc --noEmit`。
- **默认关闭严格选项**：短期少报错，长期会把空值等问题留到运行时。

## 小结与练习

- TypeScript 静态检查 JavaScript 程序，运行时仍是 JavaScript。
- 注解用于表达契约；可推断的局部类型通常不必重复声明。
- 用 `tsconfig.json` 固定编译与检查策略。

练习：给 `sum` 函数添加参数和返回值类型；再故意传入字符串，确认检查器给出诊断。下一节：[日常类型](everyday-types.md)，学习描述值和数据结构的常用语法。
