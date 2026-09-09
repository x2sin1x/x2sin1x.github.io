# 输出示例参考

以下是一个输出示例（以 FastAPI 为例），展示文档的最终效果参考。

> **注意**：实际生成的文档会更详尽，此示例仅展示格式和风格。

---

# FastAPI 快速入门指南

> 本文档基于 FastAPI v0.111.0，最后更新于 2026-04-30

## 一、技术简介

### 这是什么？
FastAPI 是一个现代、高性能的 Python Web 框架，专为构建 API 而生。它基于 Python 的类型提示（type hints）自动生成 API 文档，性能接近 Node.js 和 Go。

### 适用场景
- 构建 RESTful API 后端服务
- 需要自动生成 Swagger 文档的项目
- 对性能有较高要求的 Python Web 服务
- 需要请求参数自动验证的场景

### 对比
| 对比项 | FastAPI | Flask | Django |
|--------|---------|-------|--------|
| 性能 | 高 | 中 | 中 |
| 自动文档 | ✅ 内置 Swagger UI | ❌ 需扩展 | ❌ 需扩展 |
| 类型验证 | ✅ 内置 | ❌ 需扩展 | ❌ 需扩展 |
| 学习曲线 | 中低 | 低 | 中高 |

> **新手提示**：如果你熟悉 Python 类型注解，FastAPI 会让你感觉特别自然。

## 二、环境安装

> 对应官方文档：https://fastapi.tiangolo.com/#installation

### 系统要求
- Python 3.8+
- pip（Python 包管理器）

### 安装步骤

```bash
# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装 FastAPI
pip install fastapi

# 安装 uvicorn（运行服务器）
pip install uvicorn
```

### 验证安装

```bash
python -c "import fastapi; print(fastapi.__version__)"
# 输出示例：0.111.0
```

## 三、快速上手

> 对应官方文档：https://fastapi.tiangolo.com/#example

### Hello World

创建一个 `main.py`：

```python
from fastapi import FastAPI

# 创建应用实例
app = FastAPI()

# 定义根路径的 GET 接口
@app.get("/")
def read_root():
    return {"message": "Hello World"}
```

在终端运行：

```bash
uvicorn main:app --reload
```

访问浏览器：
- API 响应：http://127.0.0.1:8000 → `{"message": "Hello World"}`
- 自动文档：http://127.0.0.1:8000/docs → Swagger UI

## 四、核心概念详解

> 对应官方文档：https://fastapi.tiangolo.com/#learn

### 路径操作（Path Operations）

**通俗解释**：路径操作就是定义"当用户访问某个网址时，应该执行什么代码"。

**基本语法**：

```python
@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}
```

| 部分 | 说明 |
|------|------|
| `@app.get()` | 装饰器，声明 HTTP 方法和路径 |
| `item_id` | 路径参数，自动从 URL 中提取 |
| `: int` | 类型注解，自动验证参数类型 |

### 请求体（Request Body）

...

---

（以此类推，覆盖所有核心概念）

---

## 五、常用操作速查表

| 操作 | 代码 | 说明 |
|------|------|------|
| 创建应用 | `app = FastAPI()` | 初始化 FastAPI 应用 |
| 定义 GET | `@app.get("/path")` | 定义 GET 接口 |
| 定义 POST | `@app.post("/path")` | 定义 POST 接口 |
| 路径参数 | `def f(id: int)` | 自动提取路径参数 |
| 查询参数 | `def f(q: str = None)` | 自动提取查询参数 |

## 六、下一步学习

- [FastAPI 官方文档](https://fastapi.tiangolo.com/) — 完整权威的官方指南
- [FastAPI GitHub](https://github.com/tiangolo/fastapi) — 源码和 issues
