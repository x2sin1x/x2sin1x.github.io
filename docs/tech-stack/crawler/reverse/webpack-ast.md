---
title: Webpack、混淆与 AST
weight: 4
---

# Webpack、混淆与 AST

当代码不是「一个加密函数」而是「半个 JS 文件」时，通常意味着网站用了 **Webpack 打包**或**代码混淆**。本章讲三种对抗手段：Webpack 扣代码、OB 混淆还原、AST 自动化解混淆。

## 一、Webpack 打包原理

### 1. 识别特征

Webpack 是 JS 模块打包器：把所有资源当模块，最终打包成一个自执行函数。特征：

- 页面大部分逻辑在一个大 JS 文件里
- 结构为「**自执行函数 + 加载器（分发器）+ 模块集合**」
- 加载器函数通常叫 `n`、`c`、`__webpack_require__`

```javascript
!function (e) {                    // e 是模块集合
    var c = {};                    // 模块缓存
    function n(t) {                // 加载器：根据模块 id 取模块并执行
        var a = c[t] = { i: t, l: !1, exports: {} };
        return e[t].call(a.exports, a, a.exports, n),
               a.l = !0,
               a.exports;
    }
    n.m = e;
    n(2);                          // 入口
}([
    function () { console.log('负责登录'); },   // 模块 0
    function () { console.log('负责注册'); },   // 模块 1
    function () { console.log('负责爬数据'); }, // 模块 2
]);
```

模块集合有两种形式：

- **数组形式**：按下标取模块 `n(2)`
- **对象形式**：按 key 取模块 `n('xialuo')`

### 2. webpackJsonp 多文件打包

模块很多时会被拆成多个 JS 文件，用一个全局数组动态加载：

```javascript
window['webpackJsonp'] = [];
// push 被重写为 webpackJsonpCallback(模块ID, 模块对象, 入口)
window['webpackJsonp'].push([[2], { '769': function () {...} }]);
```

逆向时需要把散落各文件的模块都收集起来（见下文批量收集技巧）。

## 二、Webpack 扣代码实战

以 36kr 登录 `password` 加密为例（`Object(i.b)` 加密 → 内部调用 webpack 加载器 `n('769')` 拿到 RSA 模块）。

### 1. 通用步骤

1. 定位到加密函数，确认其内部通过加载器取模块（看到 `n(xxx)` 形式即可确认是 Webpack）
2. 把**加载器**整个抄下来，把**需要的模块**抄进模块集合
3. 在加载器位置暴露接口：`bc = n;`，随后 `bc('769')` 即可调用任意模块
4. 按网站逻辑组装加密函数

### 2. 还原后的代码骨架

```javascript
window = global;
navigator = { appName: 'Netscape' };
var bc;     // 用于外部调用加载器

!function (e) {
    var n = {};
    function c(t) {
        var r = n[t] = { i: t, l: !1, exports: {} };
        return e[t].call(r.exports, r, r.exports, c), r.l = !0, r.exports;
    }
    bc = c;    // 暴露加载器
}({
    // 从网站抄来的模块（此处示意）
    '769': function (e, t, n) {
        /* JSEncrypt / RSA 实现 */
    },
});

// 组装加密函数
var publicKey = 'MIGfMA0GCSqGSIb3DQEBAQUAA4GN...';
function encrypt(e) {
    var t = bc('769');
    var r = new t.JSEncrypt();
    r.setPublicKey(publicKey);
    return r.encrypt(e);
}
console.log(encrypt('1234'));
```

### 3. 批量收集模块技巧

模块分散在多个 chunk 文件时，逐个抠太累。在加载器内部下**条件断点**（条件写 `0`，只执行不暂停）把模块登记到全局对象，最后在控制台一次性导出：

```javascript
// 断点条件里执行（断点位置：加载器注册模块处）
aaa[n] = e[n], 0;    // 把每个模块函数收进 aaa

// 收集完毕后控制台执行，拼接成模块对象源码
result = '{';
for (let x of Object.keys(aaa)) { result += '"' + x + '":' + aaa[x] + ','; }
result += '}';
copy(result);
```

把导出的对象填进上面的骨架即可。注意复制下来的代码要清理 `\n` 与格式问题。

## 三、OB 混淆

### 1. 什么是混淆

| 手段 | 说明 |
| ---- | ---- |
| 代码压缩 | 去掉空格换行，压缩为几行 |
| 变量混淆 | 有意义的名字变成 `_0x` 开头的乱码 |
| 字符串混淆 | 字符串抽取到大数组，加密存储，杜绝全局搜索 |
| 控制流平坦化 | 用 `switch-case` 打乱执行顺序 |
| 僵尸代码 / 死代码注入 | 插入无用的函数与分支 |
| 调试保护 | 无限 debugger、反格式化、检测控制台 |

**OB 混淆**（[obfuscator.io](https://obfuscator.io/)）是最常见的一种。

### 2. OB 混淆的结构

```javascript
// 1. 大数组：存放被抽取的字符串
var _0x3ed0 = ['Hello\x20World!', '1241023ikpdYM', ...];

// 2. 解密函数：按下标取数组并解密（可能带 RC4/Base64）
function _0x4ed9(a, b) { ... }

// 3. 自执行函数：数组移位（push/shift），对齐下标
(function (_0xa942b4, _0x57410c) { ... }(_0x3ed0, 0xb3f61));

// 4. 真实业务代码：函数名变成 _0x 开头，字符串都变成 _0x4ed9(0x9f)
function hi() {
    console.log(_0x4ed9(0x9f));
}
```

**还原思路**：整体是「运行时解密」——只要把前 3 部分原样保留，让解密函数能正常执行，第 4 部分的调用就可以在本地跑出真实值；或者直接用 AST 把混淆结构还原。

## 四、AST 解混淆

### 1. AST 是什么

**抽象语法树**（Abstract Syntax Tree）是源代码的树状结构表示，是编译器的中间产物。可以类比语文课给句子划成分：`var a = 1` 这句「话」会被拆成一棵树——根是「变量声明」，左枝是名字 `a`，右枝是初始值 `1`。有了这棵树，代码就不再是不可拆改的字符串，而是可以**程序化定位、修改、重建**的结构——混淆与解混淆本质上都是在树上做手脚。V8 执行 JS 的流程：

```text
Parse（源码 → AST）→ Ignition（AST → 字节码）→ TurboFan（优化为机器码）→ Orinoco（GC）
```

AST 本不是为了逆向而生（IDE 高亮、压缩、转译都靠它），但掌握了它，解混淆可以**批量、自动化**进行。在线体验：[astexplorer.net](https://astexplorer.net/)。

编译器的转换流程：词法分析（拆成 token）→ 语法分析（生成 AST）→ 语义分析 → 代码生成 → 链接 → 执行。

### 2. babel 工具链

```bash
npm install @babel/core @babel/parser @babel/traverse @babel/generator @babel/types --save-dev
```

| 包 | 作用 |
| ---- | ---- |
| `@babel/parser` | JS 源码 → AST |
| `@babel/traverse` | 遍历 / 修改节点 |
| `@babel/types` | 判断节点类型、构建新节点 |
| `@babel/generator` | AST → JS 代码 |

节点属性速查：`type`（节点类型）、`start/end`（源码位置）、`loc`（行列）、`program.body`（程序主体）、`id`（名称）、`init`（初始化值）。常用节点类型：`VariableDeclarator`、`BinaryExpression`、`CallExpression`、`StringLiteral`、`NumericLiteral`、`UnaryExpression`。

### 3. path 对象

```javascript
path.node             // 当前节点
path.toString()       // 当前节点对应的源码
path.parentPath       // 父路径（判断上下文类型）
path.container        // 兄弟节点（含自身）
path.get('init')      // 取子路径
path.stop()           // 停止遍历
```

### 4. 还原案例一：常量折叠（数字相加、字符串拼接）

```javascript
const parse = require('@babel/parser');
const traverse = require('@babel/traverse').default;
const types = require('@babel/types');
const generator = require('@babel/generator').default;

let ast = parse.parse(`var b = 1 + 2; var c = "coo" + "kie"; var d = "1" + 1;`);

traverse(ast, {
    BinaryExpression(path) {
        const { left, operator, right } = path.node;
        if (operator !== '+') return;
        // 两侧都是字面量才折叠
        if ((types.isNumericLiteral(left) || types.isStringLiteral(left)) &&
            (types.isNumericLiteral(right) || types.isStringLiteral(right))) {
            path.replaceWith(types.valueToNode(left.value + right.value));
        }
    },
});

console.log(generator(ast).code);
// var b = 3; var c = "cookie"; var d = "11";
```

### 5. 还原案例二：方法调用求值

```javascript
// '3,4,0,5,1,2'['split'](',') → ["3", "4", "0", "5", "1", "2"]
traverse(ast, {
    CallExpression(path) {
        const { callee, arguments } = path.node;
        // callee 必须是「字符串字面量.方法」形式
        if (types.isStringLiteral(callee.object) && types.isStringLiteral(callee.property)) {
            const res = callee.object.value[callee.property.value](...arguments.map(a => a.value));
            path.replaceWithMultiple(types.valueToNode(res));
        }
    },
});
```

### 6. 还原案例三：自执行函数展开

```javascript
traverse(ast, {
    UnaryExpression(path) {
        const { argument } = path.node;
        if (!types.isFunctionExpression(argument)) return;
        const { body, id, params } = argument;
        if (id != null || params.length !== 0) return;
        path.replaceWithMultiple(body.body);   // 用函数体替换调用
    },
});
```

### 7. 解混淆通用模板

```javascript
const parse = require('@babel/parser');
const traverse = require('@babel/traverse').default;
const generator = require('@babel/generator').default;

const jscode = require('fs').readFileSync('./ob.js', 'utf-8');
let ast = parse.parse(jscode);

traverse(ast, {
    /* 在这里挂多个还原插件 */
});

require('fs').writeFileSync('./decode.js', generator(ast).code);
```

::: warning
OB 混淆的**大数组、移位自执行、解密函数**三部分有内存泄漏风险，**不要格式化**这部分代码，原样保留并在插件执行前先 `eval` 让解密函数可用。
:::

## 五、小结

- 看到「自执行 + 加载器 + 模块集合」就是 Webpack：抄加载器、收模块、暴露 `bc = n`
- 模块分散用条件断点批量收集；复制注意清理格式
- OB 混淆五段式：大数组 → 解密函数 → 移位自执行 → 真实代码 → 垃圾代码；前三段原样保留
- AST 三板斧：`parse → traverse(挂插件) → generator`，插件本质是「匹配节点类型 + `path.replaceWith`」
