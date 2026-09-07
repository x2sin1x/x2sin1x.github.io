---
title: "图论算法"
---

# 图论算法

## 图的基本概念

> TODO

## 图的表示

### 邻接矩阵

#### 无向图

```cpp
class Graph {
public:
    int numV;                // 顶点数量
    vector<vector<int>> mtr; // 邻接列表

    Graph(int numV) {
        this->numV = numV;
        this->mtr = vector<vector<int>>(numV, vector<int>(numV));
    }

    void addEdge(int s, int t) {
        this->mtr[s][t] = this->mtr[t][s] = 1; // 可以换成实际的权值
    }
};
```

#### 有向图

```cpp
class Graph {
public:
    int numV;                // 顶点数量
    vector<vector<int>> mtr; // 邻接列表

    Graph(int numV) {
        this->numV = numV;
        this->mtr = vector<vector<int>>(numV, vector<int>(numV));
    }

    void addEdge(int s, int t) {
        this->mtr[s][t] = 1; // 可以换成实际的权值
    }
};
```

### 邻接列表

#### 无向图

```cpp
class Graph {
public:
    int numV;                // 顶点数量
    vector<vector<int>> adj; // 邻接列表

    Graph(int numV) {
        this->numV = numV;
        this->adj = vector<vector<int>>(numV, vector<int>());
    }

    void addEdge(int s, int t) {
        this->adj[s].push_back(t);
        this->adj[t].push_back(s);
    }
};
```

#### 有向图

```cpp
class DiGraph {
public:
    int numV;                // 顶点数量
    vector<vector<int>> adj; // 邻接列表

    DiGraph(int numV) {
        this->numV = numV;
        this->adj = vector<vector<int>>(numV, vector<int>());
    }

    void addEdge(int s, int t) {
        this->adj[s].push_back(t);
    }
};
```
