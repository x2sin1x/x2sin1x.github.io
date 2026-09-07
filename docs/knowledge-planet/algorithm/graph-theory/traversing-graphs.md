---
title: "图的遍历"
---

# 图的遍历

## 深度优先搜索

辅助空间定义

```cpp
vector<bool> marked(G.numV); // 是否已经访问
vector<int> edgeTo(G.numV);  // 前驱顶点，便于回溯
```

深度优先搜索递归算法

```cpp
void DFS(Graph &G, int v) {
    marked[v] = true;

    for (auto w : G.adj[v]) {
        if (!marked[w]) {
            DFS(G, w);
            edgeTo[w] = v;
        }
    }
}
```

在有向图中也是同理

```cpp
void DFS(DiGraph &G, int v) {
    marked[v] = true;

    for (auto w : G.adj[v]) {
        if (!marked[w]) {
            DFS(G, w);
        }
    }
}
```

## 广度优先搜索

```cpp
void DFS(DiGraph &G, int v) {
    marked[v] = true;

    for (auto w : G.adj[v]) {
        if (!marked[w]) {
            DFS(G, w);
            edgeTo[w] = v;
        }
    }
}
```

辅助空间定义

```cpp
vector<bool> marked(G.numV);   // 是否已经访问
vector<int> edgeTo(G.numV);    // 前驱结点，便于回溯
vector<int> distTo(G.numV, 0); // 路径长度
```

广度优先搜索非递归算法（借助队列）

```cpp
void BFS(Graph &G, int s) {
    marked[s] = true;
    queue<int> q;
    q.push(s);

    while (!q.empty()) {
        int v = q.front();
        q.pop();
        for (auto w : G.adj[v]) {
            if (!marked[w]) {
                q.push(w);
                marked[w] = true;
                edgeTo[w] = v;
                distTo[w] = distTo[v] + 1;
            }
        }
    }
}
```

在有向图中也是同理

```cpp
void BFS(DiGraph &G, int s) {
    marked[s] = true;
    queue<int> q;
    q.push(s);

    while (!q.empty()) {
        int v = q.front();
        q.pop();
        for (auto w : G.adj[v]) {
            if (!marked[w]) {
                q.push(w);
                marked[w] = true;
            }
        }
    }
}
```

## 搜索算法的应用与挑战

|     问题     |        BFS         |        DFS         | 时间复杂度 |
| :----------: | :----------------: | :----------------: | :--------: |
|     可达     | :white_check_mark: | :white_check_mark: |   $E+V$    |
|   最短路径   | :white_check_mark: |                    |   $E+V$    |
|   连通分量   | :white_check_mark: | :white_check_mark: |   $E+V$    |
|  重连通分量  |                    | :white_check_mark: |   $E+V$    |
|      环      | :white_check_mark: | :white_check_mark: |   $E+V$    |
|   欧拉回路   |                    | :white_check_mark: |   $E+V$    |
| 哈密尔顿回路 |                    |                    |            |
|    二部图    | :white_check_mark: | :white_check_mark: |   $E+V$    |
|    平面图    |                    | :white_check_mark: |   $E+V$    |
|    图同构    |                    |                    |            |
