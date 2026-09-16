---
title: JS 基础与浏览器调试
weight: 1
---

# JS 基础与浏览器调试

## 一、JS 语法速览

逆向不要求会写前端，但要能**读懂** JS。以下是与 Python 差异较大、逆向中最常遇到的部分。

### 1. 变量与数据类型

```javascript
var iNum = 123;        // 弱类型：类型由值决定；ES6 还有 let（块级变量）、const（常量）
var sTr = 'asd';
var bFlag = true;      // boolean
var unData;            // undefined：声明未初始化
var nullData = null;   // 空对象
var oObj = {           // object：数组、函数、对象都是复合类型
    name: '隔壁老王',
    age: 88,
};
typeof oObj;           // 'object'
```

### 2. 函数与作用域

```javascript
function fnAdd(a, b) {
    return a + b;      // return 后函数立即结束
}
var r = fnAdd(3, 4);

// arguments 可接收任意多个参数
function sum() { return Array.from(arguments).reduce((a, b) => a + b, 0); }

// 内部函数暴露给外部（IIFE 立即执行函数，混淆代码里极常见）
var _xl;
!(function () {
    function xl() { console.log('hello'); }
    _xl = xl;
})();
_xl();
```

- **局部变量**：函数内用 `var` 声明，函数执行完销毁
- **全局变量**：函数外声明，页面关闭才销毁
- `==` 会隐式转换类型（`'12' == 12` 为 true），`===` 不转换

### 3. 对象与类

```javascript
// 字面量创建
var obj = { uname: '张三', sayHi: function () { console.log('hi'); } };
obj.uname;                 // 或 obj['uname']

// 构造函数
function Star(name, age) {
    this.name = name;
    this.age = age;
}
var ldh = new Star('刘德华', 18);

// ES6 class（constructor 相当于 Python 的 __init__，extends 继承）
class Person {
    constructor(name) { this.name = name; }
    dance() { console.log('跳舞'); }
}
class Student extends Person {
    constructor(name, score) {
        super(name);            // 调用父类构造器
        this.score = score;
    }
}
```

**原型链**：每个对象都有隐式原型 `__proto__`，指向其构造函数的显式原型 `prototype`；查找属性时沿原型链向上找。`hasOwnProperty('x')` 判断属性是否是自有属性。补环境章节会大量用到原型链知识。

### 4. 数组常用方法

```javascript
var arr = [1, 2, 3, 4];
arr.length;              // 长度
arr.push(5); arr.pop();  // 尾部增删
arr.splice(0, 1);        // 按下标删除/插入
arr.map(x => x * 2);     // 映射
arr.filter(x => x % 2);  // 过滤
arr.sort(); arr.join('');// 排序、拼接（加密参数常先 sort 再拼接）
```

### 5. 异步：Promise 与 async/await

```javascript
function getAsyncData() {
    return new Promise(function (resolve, reject) {
        setTimeout(() => resolve('async data'), 1000);   // 成功调 resolve
    });
}

// then/catch 写法
getAsyncData().then(data => console.log(data)).catch(err => console.log(err));

// async/await 写法（ES7）
async function main() {
    var data = await getAsyncData();
    console.log(data);
}
```

逆向时若加密发生在异步代码里，调用栈中看不到来源——需要在异步起点断点粗调，再精确定位。

### 6. JSON 与 Ajax

```javascript
JSON.parse('{"a":1}');          // 字符串 → 对象
JSON.stringify({a: 1});         // 对象 → 字符串（Hook 常用点）

// jQuery 封装的 Ajax
$.ajax({
    url: 'https://api.example.com/data',
    type: 'GET',
    dataType: 'JSON',
    data: {},
    success: function (response) { console.log(response); },
    error: function () { alert('请求失败'); },
});
```

### 7. window / BOM 对象

浏览器环境的全局对象，逆向补环境时经常要伪造：

- `document`：`cookie`、`referrer`、`URL`、`getElementById()`、`createElement()`
- `navigator`：`userAgent`、`platform`、`language`（环境检测重点）
- `location`：`href`、`hostname`、`protocol`
- `window.history`、`window.screen`、定时器 `setTimeout / setInterval`

## 二、断点定位加密位置

找到「数据在哪里被加密」是逆向第一步，常用手段按效率排序：

### 1. 关键字搜索

在 Sources 面板全局搜索（`Ctrl+Shift+F`）参数名：`sign`、`sign=`、`"sign"` 等多种形态都试一下。搜不到的原因：代码被混淆、关键字被拼接（如 `'si' + 'gn'`）。

### 2. DOM 事件断点

针对「点击按钮后加密」的场景：右侧面板 `Event Listener Breakpoints` 勾选 `Mouse → click` 等，事件触发时自动断下。**特点：断得早，离加密函数较远，需要跟很多栈。**

### 3. XHR 断点

针对「Ajax 发出前加密」的场景：`XHR/fetch Breakpoints` 添加 URL 包含的关键字。**特点：断得晚，离加密函数近，配合调用栈快速定位**——但非 XHR 发出的请求断不住。

### 4. 方法栈（调用栈）

断下后在右侧 Scope / Call Stack 查看执行链。JS 调用栈是**先进后出**的：`aa → bb → cc`，栈顶（列表第一行）是当前正在执行的函数，越往下越是外层调用者。点击栈的每一帧可以跳回对应的调用位置与作用域。

读栈的实用技巧——盯住你要找的加密参数，逐帧从上往下扫：

- **该参数在当前帧还没生成**（值是 undefined/空）→ 说明加密发生在更外层的调用里，继续往下帧找；
- **到某一帧参数已经有值了** → 加密逻辑就在当前帧与上一帧之间，在这里下断点精调。

另外，网站发布时 JS 都经过压缩（变量名变 a/b/c，代码挤成一行），直接看无法下手。在 Sources 面板左下角点击 **`{}` 按钮（Pretty print，格式化）**，代码会展开成正常缩进，之后才能方便地下断点。

### 5. 网页加载时间轴

```text
加载 HTML → 加载 JS → 运行 JS 初始化 → 用户触发事件 → 调用加密函数
→ XHR 发送 → 接收数据 → 解密函数（若有）→ 渲染
```

加密一定发生在「XHR 发送」之前，解密发生在「接收数据」之后。

## 三、无限 debugger 的原理与过法

网站为了阻止调试，会在代码里疯狂插入 `debugger` 语句。常见实现：

```javascript
// 1. 定时器触发
setInterval(function () { debugger; }, 100);

// 2. 检测开发者工具（窗口宽高差）
function resize() {
    if (window.outerWidth - window.innerWidth > 200) { debugger; }
}
setInterval(resize, 100);

// 3. Function 构造器断点（最常见）
(function check() {
    function doCheck(a) {
        (function () {}['constructor']('debugger')());   // new Function('debugger')
        doCheck(++a);
    }
    try { doCheck(0); } catch (e) {}
})();
```

### 过法一：行号右键「一律不在此处暂停」

最简单，适合定时器类 debugger；构造器类会不停在新位置断下，不适用。

### 过法二：条件断点

右击 debugger 所在行号 → 添加条件断点，条件写 `1 === 0`（永假），该行永远不会真正断下。

### 过法三：函数置空

在 debugger 执行**之前**，于控制台重写触发函数：

```javascript
setInterval = function () {};        // 置空定时器
function ff() {}                     // 或重写触发 debugger 的函数
```

### 过法四：Hook Function 构造器（注入代码）

```javascript
var _constructor = constructor;
Function.prototype.constructor = function (s) {
    if (s === 'debugger') {
        return function () {};       // 吞掉 debugger
    }
    return _constructor(s);
};
```

### 过法五：替换文件

Sources 面板 → 选中 JS 文件 → 右键「替换内容（Overrides）」，把 debugger 相关代码删除或注释后保存，刷新页面即执行修改后的文件。适合 debugger 逻辑复杂的站点（如瑞数）。

## 四、调试操作速查

| 操作 | 快捷键（Windows） |
| ---- | ----------------- |
| 单步跳过（不进子函数） | F10 |
| 单步进入（进入子函数） | F11 |
| 跳出当前函数 | Shift + F11 |
| 继续执行到下个断点 | F8 |
| 屏蔽所有断点 | Ctrl + F8 |
| 查看变量 | 右侧 Scope / Watch / 控制台直接打印 |

**调试心法**：先粗后细——先在异步起点下一断点整体过一遍，对代码执行流程建立印象，锁定大致范围后再精细化单步调试。

::: tip 在哪里执行 Hook 代码
Hook 代码有三个执行入口，各有适用场景：

1. **Console 控制台直接粘贴**：最快，但刷新页面后失效，适合临时验证；
2. **Sources → 代码段（Snippets）**：保存为片段，需要时一键运行，适合反复使用；
3. **Overrides 替换文件**：把 Hook 代码追加到网站 JS 文件末尾保存，刷新自动生效，适合需要「刷新前就位」的场景（如 Hook Cookie、瑞数）。

记住顺序：**先让 Hook 代码就位 → 再刷新页面 → 再触发加密操作**。顺序反了，加密早就发生完，Hook 就白写了。
:::

## 五、小结

- 读懂 JS 的最小集：变量/函数/对象/原型链/Promise/Ajax/BOM 对象
- 定位三板斧：**关键字搜索 → XHR 断点 → Hook**（Hook 见下一章）
- 无限 debugger 五种过法按顺序尝试：不暂停 → 条件断点 → 置空 → Hook 构造器 → 替换文件
- 断点位置越靠近「XHR 发送」加密点越近；异步加密要在异步代码里断
