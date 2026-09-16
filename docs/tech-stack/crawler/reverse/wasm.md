---
title: WASM 逆向
weight: 5
---

# WASM 逆向

## 一、什么是 WebAssembly

**WebAssembly**（简称 Wasm）是一种现代的低级编程语言（字节码格式），设计用于在网页上运行高性能代码。开发者可以将 C、C++、Rust 等语言编写的代码编译成 Wasm 格式，然后在浏览器中运行。

核心特点：

1. **高性能**：接近原生性能，比 JavaScript 更快地执行计算密集型任务
2. **安全性**：在沙箱环境中运行，不能直接访问主机系统
3. **跨平台**：所有现代浏览器（Chrome / Firefox / Safari / Edge）原生支持
4. **与 JS 互操作**：可以互相调用函数、共享内存

对爬虫来说，Wasm 的意义在于：**越来越多网站把加密核心算法放进 `.wasm` 文件**，JS 里只留一个调用壳。这样一来，单纯「扣 JS 代码」就拿不到算法本体了——要么把 wasm 文件拿下来直接执行，要么逆向 wasm 字节码（成本极高）。通常前者就够了。

## 二、浏览器如何加载 Wasm

一个完整的网页加载执行 wasm 的流程：

1. **创建模块**：用 C/C++/Rust 编写算法代码，通过 Emscripten / wasm-pack 等工具编译成 `.wasm` 文件
2. **加载模块**：JS 用 `fetch` 获取 wasm 文件（二进制），再调用 `WebAssembly.instantiate` 或 `WebAssembly.instantiateStreaming` 实例化
3. **调用导出函数**：通过实例的 `exports` 对象调用 wasm 内部的函数

### 1. fetch 与 instantiate

`fetch` 是现代浏览器发起网络请求的 API（基于 Promise 的「精简版 ajax」）：

```javascript
fetch('https://api.example.com/data')
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error('Error:', error));
```

`WebAssembly.instantiate(bytes, importObject)` 负责编译并实例化：

```javascript
const importObject = {
    env: {
        importedFunc: function () {
            console.log('Hello from JavaScript!');
        },
    },
};

fetch('module.wasm')
    .then(response => response.arrayBuffer())      // 拿到二进制
    .then(bytes => WebAssembly.instantiate(bytes, importObject))
    .then(({ instance, module }) => {
        console.log(instance.exports);             // 导出函数列表
        instance.exports.yourFunction();           // 调用导出函数
    });
```

两个参数与返回值：

| 项 | 说明 |
| ---- | ---- |
| `bytes` | `ArrayBuffer` / `TypedArray`，编译好的 wasm 二进制 |
| `importObject` | 提供模块所需的外部依赖（外部函数、全局变量），结构对应模块的 import 声明 |
| `instance` | 实例化后的模块实例，`instance.exports` 包含可调用的函数和变量 |
| `module` | 编译后的 `WebAssembly.Module` 对象，可用于再次实例化 |

### 2. 识别网站是否使用 wasm

- Network 面板中出现 `.wasm` 文件请求
- JS 中出现 `WebAssembly.instantiate`、`WebAssembly.Module`、`instantiateStreaming`
- 变量名如 `$wasm`、`wasm_api`、`r123` 之类

以 scrape.center 练习站为例，接口 `sign` 参数的生成代码中有 `this.$wasm` 字样，即可确认签名由 wasm 计算。

## 三、Node 调用 wasm

Node.js 内置 `WebAssembly` 支持，可以直接读本地 wasm 文件执行——这是 wasm 逆向最常用的路径：

```javascript
// node 调用，文件与 Wasm.wasm 同目录
const fs = require('fs');
const wasmCode = fs.readFileSync('Wasm.wasm');

WebAssembly.instantiate(wasmCode, {
    env: {},
    wasi_snapshot_preview1: {},
}).then(result => {
    const instance = result.instance;
    const exportedFunc = instance.exports;
    console.log(exportedFunc);                        // 查看所有导出函数
    console.log(exportedFunc.encrypt(50, 1727186733)); // 调用加密函数
});
```

::: tip
`importObject` 里的 `env`、`wasi_snapshot_preview1` 是常见的外部依赖命名空间。如果 wasm 需要导入函数而没提供，实例化会报错——按报错提示在对应命名空间下补上空函数或日志函数即可。
:::

## 四、Python 调用 wasm（pywasm）

```bash
pip install pywasm
```

```python
import pywasm
import time

t = int(time.time())
vm = pywasm.load('./Wasm.wasm', {
    'env': {},
    'wasi_snapshot_preview1': {},
})
sign = vm.exec('encrypt', [40, t])
print(sign)
```

::: warning
pywasm 是纯 Python 实现的 wasm 解释器，**兼容性一般且速度慢**。生产环境更推荐：Python 用 `subprocess` 调用 Node 脚本执行 wasm，稳定且快。
:::

## 五、实战案例一：scrape.center 的 sign 参数

**目标**：`https://spa14.scrape.center/api/movie/?limit=10&offset=10&sign=575796940`，解析 `sign` 查询参数。

**分析**：

1. 关键字搜索定位到 `this.$wasm` 生成位置；
2. 异步代码中通过条件断点确定 `sign` 在第几次生成时被计算（在 `var u = t[o](c)` 等位置下断点观察）；
3. 确认 wasm 的加载与调用位置，下载 `.wasm` 文件。

**Node 侧复现**：

```javascript
// demo.js
const fs = require('fs');
const wasmCode = fs.readFileSync('Wasm.wasm');

function aa(page) {
    WebAssembly.instantiate(wasmCode, {
        env: {},
        wasi_snapshot_preview1: {},
    }).then(result => {
        const exportedFunc = result.instance.exports;
        // sign = encrypt(offset, 秒级时间戳)
        console.log(exportedFunc.encrypt(
            page,
            parseInt(Math.round(new Date().getTime() / 1e3).toString())
        ));
    });
}
aa(process.argv[2]);
```

**Python 侧接入**：

```python
import subprocess
import requests

headers = {
    'Referer': 'https://spa14.scrape.center/page/7',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...',
}
url = 'https://spa14.scrape.center/api/movie/'

for i in range(7, 10):
    sign = subprocess.run(['node', 'demo.js', str(i * 10)],
                          capture_output=True, text=True)
    params = {'limit': '10', 'offset': str(i * 10), 'sign': sign.stdout.strip()}
    response = requests.get(url, headers=headers, params=params)
    print(response.text)
```

要点：**签名 = wasm 导出函数(业务参数, 时间戳)**，时间戳每次重新生成。

## 六、实战案例二：wasm + webpack 组合

更复杂的场景：wasm 藏在 Webpack 打包的模块里，JS 壳负责字符串与 wasm 内存之间的转换。以某注册接口请求头 `x-api-xxx` 为例：

**分析**：

1. 定位请求头赋值位置 → 加密函数 → 发现返回值来自 wasm 模块；
2. 网站用 Webpack 打包：加载器为 `c`，模块 `88867` 是 JS 壳（负责字符串编解码、调用 `r123.sign`），模块 `38464` 引用 wasm 实例 `r123`。

**还原思路**：

1. 把加载器抄下来并暴露 `bc = c`（Webpack 扣代码套路，见 [Webpack 一章](/tech-stack/crawler/reverse/webpack-ast)）；
2. 下载 wasm 文件，用 `WebAssembly.instantiate` 实例化得到 `r123`；
3. 补齐 wasm 需要的导入对象（wasm-bindgen 生成的模块需要 `__wbg_now_*`、`__wbg_random_*` 等回调，从网站 JS 里对照抄或用 `bc.c[88867].exports` 补上）；
4. 按网站逻辑调用：先 `__wbindgen_add_to_stack_pointer(-16)` 申请栈空间，把字符串写入 wasm 内存（`__wbindgen_malloc/realloc`），调用 `sign`，再从内存读回结果。

```javascript
// 核心调用逻辑（还原自模块 88867 的 b 函数）
function sign(path, env) {
    const u = r123.__wbindgen_add_to_stack_pointer(-16);      // 栈顶指针 -16
    const c = writeStr(path, r123.__wbindgen_malloc, r123.__wbindgen_realloc);
    const d = len;
    const _ = writeStr(env, r123.__wbindgen_malloc, r123.__wbindgen_realloc);
    const l = len;
    r123.sign(u, c, d, _, l);                                  // 调用 wasm 导出函数
    const t = readInt32()[u / 4 + 0];                          // 结果指针
    const o = readInt32()[u / 4 + 1];                          // 结果长度
    return decodeStr(t, o);                                    // 从内存读回字符串
}
```

::: tip
wasm-bindgen（Rust 工具链）生成的模块都遵循这套「栈指针 + malloc + 内存读写」模式。看到 `__wbindgen_*` 系列导出函数，照着网站 JS 壳的逻辑组装即可，无需真懂 wasm 字节码。
:::

## 七、小结

| 步骤 | 操作 |
| ---- | ---- |
| 1. 识别 | Network 找 `.wasm`，JS 搜 `WebAssembly.instantiate` |
| 2. 下载 | 把 `.wasm` 文件保存到本地 |
| 3. 执行 | Node `WebAssembly.instantiate` 直接调导出函数；补齐 importObject |
| 4. 组合 | wasm + webpack：抄加载器暴露调用入口，按 JS 壳逻辑组装 |
| 5. 接入 | Python 用 subprocess 调 Node（首选）或 pywasm |

真正硬逆向 wasm 字节码（用 wasm2wat 反汇编分析）成本极高，绝大多数场景用「下载下来直接执行」即可通关。
