---
layout: home
# 关闭 Teek 首页区块（横幅、文章列表、标签卡片），首页仅保留下方 hero 与 features
teekHome: false

hero:
  name: "Bowen Blog"
  text: "mi re la ti sol fa do"
  tagline: 记录技术学习与思考，沉淀知识体系
  image:
    src: /nenifindo.png
    alt: Nenifindo Logo
  actions:
    - theme: brand
      text: 博客
      link: /posts/
    - theme: alt
      text: 技术栈
      link: /tech-stack/
    - theme: alt
      text: 知识星球
      link: /knowledge-planet/

features:
  # 配置 link 后卡片渲染为 <a>，支持整卡单击进入；linkText 显示在卡片底部并带箭头
  - icon: 📝
    title: 博客
    details: 技术解读与思想随笔，按年份归档，涵盖论文精读、时事评论与个人感悟。
    link: /posts/
    linkText: 进入博客
  - icon: 🛠️
    title: 技术栈
    details: Git、Linux、Python 数据科学（NumPy、Pandas、Matplotlib）、MongoDB 等工具的学习笔记与速查手册。
    link: /tech-stack/
    linkText: 进入技术栈
  - icon: 🪐
    title: 知识星球
    details: 马列主义经典导读、凸优化、金融学、音乐理论等领域的系统性专栏笔记。
    link: /knowledge-planet/
    linkText: 进入知识星球
---
