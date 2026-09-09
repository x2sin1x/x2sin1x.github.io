---
title: "作业"
date: 2021-12-31T20:28:39+08:00
---
# 作业

## [找到最终的安全状态](https://leetcode-cn.com/problems/find-eventual-safe-states/)

### 问题描述

在**有向图**中，以某个节点为起始节点，从该点出发，每一步沿着图中的一条有向边行走。如果到达的节点是终点（即它没有连出的有向边），则停止。

对于一个起始节点，如果从该节点出发，**无论每一步选择沿哪条有向边行走，最后必然在有限步内到达终点**，则将该起始节点称作是**安全**的。

返回一个由图中所有安全的起始节点组成的数组作为答案。答案数组中的元素应当按**升序**排列。

该有向图有 `n` 个节点，按 `0` 到 `n - 1` 编号，其中 `n` 是 `graph` 的节点数。图以下述形式给出：`graph[i]` 是编号 `j` 节点的一个列表，满足 `(i, j)` 是图的一条有向边。

依题意，此题考察的是顶点可达性的问题，涉及到 DFS 以及环的判断等知识点。

### 方法一：深度优先搜索

根据题意，若起始节点位于一个环内，或者能到达一个环，则该节点不是安全的。否则，该节点是安全的。

我们可以使用深度优先搜索来找环，并在深度优先搜索时，用三种颜色对节点进行标记，标记的规则如下：

- 白色（用 0 表示）：该节点尚未被访问；
- 灰色（用 1 表示）：该节点位于递归栈中，或者在某个环上；
- 黑色（用 2 表示）：该节点搜索完毕，是一个安全节点。

当我们首次访问一个节点时，将其标记为灰色，并继续搜索与其相连的节点。

如果在搜索过程中遇到了一个灰色节点，则说明找到了一个环，此时退出搜索，栈中的节点仍保持为灰色，这一做法可以将「找到了环」这一信息传递到栈中的所有节点上。

如果搜索过程中没有遇到灰色节点，则说明没有遇到环，那么递归返回前，我们将其标记由灰色改为黑色，即表示它是一个安全的节点。

#### 算法代码

```cpp
class Solution {
public:
    vector<int> eventualSafeNodes(vector<vector<int>> &graph) {
        int n = graph.size();
        vector<int> color(n);

        function<bool(int)> safe = [&](int x) {
            if (color[x] > 0) {
                return color[x] == 2;
            }
            color[x] = 1;
            for (int y : graph[x]) {
                if (!safe(y)) {
                    return false;
                }
            }
            color[x] = 2;
            return true;
        };

        vector<int> ans;
        for (int i = 0; i < n; ++i) {
            if (safe(i)) {
                ans.push_back(i);
            }
        }
        return ans;
    }
};
```

#### 算法分析

- 时间复杂度：$O(n+m)$，其中 $n$ 是图中的点数，$m$ 是图中的边数。
- 空间复杂度：$O(n)$。存储节点颜色以及递归栈的开销均为 $O(n)$。

### 方法二：拓扑排序

根据题意，若一个节点没有出边，则该节点是安全的；若一个节点出边相连的点都是安全的，则该节点也是安全的。

根据这一性质，我们可以将图中所有边反向，得到一个反图，然后在反图上运行拓扑排序。

具体来说，首先得到反图 $\textit{rg}$ 及其入度数组 $\textit{inDeg}$。将所有入度为 0 的点加入队列，然后不断取出队首元素，将其出边相连的点的入度减一，若该点入度减一后为 0，则将该点加入队列，如此循环直至队列为空。循环结束后，所有入度为 0 的节点均为安全的。我们遍历入度数组，并将入度为 0 的点加入答案列表。

#### 算法代码

```cpp
class Solution {
public:
    vector<int> eventualSafeNodes(vector<vector<int>> &graph) {
        int n = graph.size();
        vector<vector<int>> rg(n);
        vector<int> inDeg(n);
        for (int x = 0; x < n; ++x) {
            for (int y : graph[x]) {
                rg[y].push_back(x);
            }
            inDeg[x] = graph[x].size();
        }

        queue<int> q;
        for (int i = 0; i < n; ++i) {
            if (inDeg[i] == 0) {
                q.push(i);
            }
        }
        while (!q.empty()) {
            int y = q.front();
            q.pop();
            for (int x : rg[y]) {
                if (--inDeg[x] == 0) {
                    q.push(x);
                }
            }
        }

        vector<int> ans;
        for (int i = 0; i < n; ++i) {
            if (inDeg[i] == 0) {
                ans.push_back(i);
            }
        }
        return ans;
    }
};
```

#### 算法分析

- 时间复杂度：$O(n+m)$。其中 $n$ 是图中的点数，$m$ 是图中的边数。
- 空间复杂度：$O(n+m)$。需要 $O(n+m)$ 的空间记录反图。

## [判断二分图](https://leetcode-cn.com/problems/is-graph-bipartite/)

### 问题描述

存在一个**无向图**，图中有 `n` 个节点。其中每个节点都有一个介于 `0` 到 `n - 1` 之间的唯一编号。

给定一个二维数组` graph` ，表示图，其中 `graph[u]` 是一个节点数组，由节点 `u` 的邻接节点组成。形式上，对于 `graph[u]` 中的每个 `v` ，都存在一条位于节点 `u` 和节点 `v` 之间的无向边。该无向图同时具有以下属性：

- 不存在自环（`graph[u]` 不包含 `u`）。
- 不存在平行边（`graph[u]` 不包含重复值）。
- 如果 `v` 在 `graph[u]` 内，那么 `u` 也应该在 `graph[v]` 内（该图是无向图）
- 这个图可能不是连通图，也就是说两个节点 `u` 和 `v` 之间可能不存在一条连通彼此的路径。

**二分图**定义：如果能将一个图的节点集合分割成两个独立的子集 $A$ 和 $B$，并使图中的每一条边的两个节点一个来自 $A$ 集合，一个来自 $B$ 集合，就将这个图称为**二分图**。

如果图是**二分图**，返回 `true`；否则，返回 `false`。

### 问题分析

对于图中的任意两个节点 $u$ 和 $v$，如果它们之间有一条边直接相连，那么 $u$ 和 $v$ 必须属于不同的集合。

如果给定的无向图连通，那么我们就可以任选一个节点开始，给它染成红色。随后我们对整个图进行遍历，将该节点直接相连的所有节点染成绿色，表示这些节点不能与起始节点属于同一个集合。我们再将这些绿色节点直接相连的所有节点染成红色，以此类推，直到无向图中的每个节点均被染色。

如果我们能够成功染色，那么红色和绿色的节点各属于一个集合，这个无向图就是一个二分图；如果我们未能成功染色，即在染色的过程中，某一时刻访问到了一个已经染色的节点，并且它的颜色与我们将要给它染上的颜色不相同，也就说明这个无向图不是一个二分图。

算法的流程如下：

- 我们任选一个节点开始，将其染成红色，并从该节点开始对整个无向图进行遍历；
- 在遍历的过程中，如果我们通过节点 $u$ 遍历到了节点 $v$（即 $u$ 和 $v$ 在图中有一条边直接相连），那么会有两种情况：
  - 如果 $v$ 未被染色，那么我们将其染成与 $u$ 不同的颜色，并对 $v$ 直接相连的节点进行遍历；
  - 如果 $v$ 被染色，并且颜色与 $u$ 相同，那么说明给定的无向图不是二分图。我们可以直接退出遍历并返回 `False` 作为答案。
- 当遍历结束时，说明给定的无向图是二分图，返回 `True` 作为答案。

我们可以使用 DFS 或 BFS 对无向图进行遍历，下文分别给出了这两种搜索对应的代码。

注意：题目中给定的无向图不一定保证连通，因此我们需要进行多次遍历，直到每一个节点都被染色，或确定答案为 `False` 为止。每次遍历开始时，我们任选一个未被染色的节点，将所有与该节点直接或间接相连的节点进行染色。

### 算法代码

**DFS**

```cpp
class Solution {
private:
    static constexpr int UNCOLORED = 0;
    static constexpr int RED = 1;
    static constexpr int GREEN = 2;
    vector<int> color;
    bool valid;

public:
    bool isBipartite(vector<vector<int>> &graph) {
        int n = graph.size();
        valid = true;
        color.assign(n, UNCOLORED);

        for (int i = 0; i < n; ++i) {
            if (color[i] == UNCOLORED) {
                dfs(i, RED, graph);
            }
        }

        return valid;
    }

    void dfs(int node, int c, const vector<vector<int>> &graph) {
        color[node] = c;
        int cNei = (c == RED ? GREEN : RED); // 相邻顶点颜色不能相同

        for (int neighbor : graph[node]) {
            if (color[neighbor] == UNCOLORED) {
                dfs(neighbor, cNei, graph);
                if (!valid) {
                    return;
                }
            } else if (color[neighbor] != cNei) {
                valid = false;
                return;
            }
        }
    }
};
```

**BFS**

```cpp
class Solution {
private:
    static constexpr int UNCOLORED = 0;
    static constexpr int RED = 1;
    static constexpr int GREEN = 2;
    vector<int> color;

public:
    bool isBipartite(vector<vector<int>>& graph) {
        int n = graph.size();
        vector<int> color(n, UNCOLORED);
        for (int i = 0; i < n; ++i) {
            if (color[i] == UNCOLORED) {
                queue<int> q;
                q.push(i);
                color[i] = RED;
                while (!q.empty()) {
                    int node = q.front();
                    int cNei = (color[node] == RED ? GREEN : RED);
                    q.pop();
                    for (int neighbor: graph[node]) {
                        if (color[neighbor] == UNCOLORED) {
                            q.push(neighbor);
                            color[neighbor] = cNei;
                        }
                        else if (color[neighbor] != cNei) {
                            return false;
                        }
                    }
                }
            }
        }
        return true;
    }
};
```

### 算法分析

|      | 时间复杂度 | 空间复杂度 |
| :--: | :--------: | :--------: |
| DFS  |  $O(V+E)$  |   $O(V)$   |
| BFS  |  $O(V+E)$  |   $O(V)$   |

## [最小高度树](https://leetcode-cn.com/problems/minimum-height-trees/)

### 问题描述

树是一个无向图，其中任何两个顶点只通过一条路径连接。 换句话说，一个任何没有简单环路的连通图都是一棵树。

给你一棵包含 `n` 个节点的树，标记为 `0` 到 `n - 1`。给定数字 `n` 和一个有 `n - 1` 条无向边的 `edges` 列表（每一个边都是一对标签），其中 `edges[i] = [ai, bi]` 表示树中节点 `ai` 和 `bi` 之间存在一条无向边。

可选择树中任何一个节点作为根。当选择节点 `x` 作为根节点时，设结果树的高度为 `h`。在所有可能的树中，具有最小高度的树（即，`min(h)`）被称为**最小高度树**。

请你找到所有的**最小高度树**并按**任意顺序**返回它们的根节点标签列表。

树的**高度**是指根节点和叶子节点之间最长向下路径上边的数量。

### 问题分析

我们知道，树是一种特殊的图。树的叶子结点的度必然为 `1`。因此，虽然我们并不知道最小高度树的根结点在哪里，但是我们可以确定其叶子结点一定是图中度为 `1` 的结点。

从这些叶子结点开始，不断地进行广度优先搜索。在搜索过程中删除那些已经遍历过的叶子结点，一层一层地“剥皮”。最后会出现两种情况：

- 只剩下一个结点。显然其度为 `0`，而它恰恰是最小高度树的根结点。
- 剩下两个结点，彼此之间有边相连。显然这两个结点的度均为 `1`，而不论选择它们之中的任何一个作为根结点都可以得到最小高度树。

### 算法代码

```cpp
class Solution {
public:
    vector<int> findMinHeightTrees(int n, vector<vector<int>> &edges) {
        if (n == 1) {
            return {0};
        }
        // 建立邻接列表表示的无向图
        vector<vector<int>> graph(n, vector<int>());
        for (auto &edge : edges) {
            graph[edge[0]].push_back(edge[1]);
            graph[edge[1]].push_back(edge[0]);
        }
        // 度为 1 的顶点（叶子结点）入队
        vector<int> degree(n, 0);
        queue<int> q;
        for (int i = 0; i < n; ++i) {
            degree[i] = graph[i].size();
            if (degree[i] == 1) {
                q.push(i);
            }
        }
        vector<int> roots;
        while (!q.empty()) {
            roots.clear();
            int sz = q.size();
            // 处理当前全部叶子结点并删除
            for (int i = 0; i < sz; ++i) {
                int t = q.front();
                q.pop();
                roots.push_back(t);
                // 加入 t 的邻接叶子结点
                degree[t]--;
                for (auto v : graph[t]) {
                    degree[v]--;
                    if (degree[v] == 1) {
                        q.push(v);
                    }
                }
            }
        }
        return roots;
    }
};
```

### 算法分析

- 时间复杂度：$O(V+E)$
- 空间复杂度：$O(V)$
