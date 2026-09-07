// 分页路径：博客列表每 10 篇一页（第 1 页由 docs/blogs/index.md 提供）。
// 文章数量变化导致页数增加时，在此追加对应页码。
export default {
  paths: [
    { params: { page: 2 } },
    { params: { page: 3 } },
    { params: { page: 4 } },
    { params: { page: 5 } },
    { params: { page: 6 } }
  ]
}
