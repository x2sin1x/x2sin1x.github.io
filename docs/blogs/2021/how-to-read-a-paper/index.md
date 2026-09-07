---
title: "How to Read a Paper"
description: "精读 SIGCOMM 上的经典论文，介绍科研文献的三遍阅读法及如何用它进行文献调研。"
---

# How to Read a Paper

<p class="page-subtitle">如何阅读一篇文献</p>

这是 2007 年发表在 SIGCOMM 上的一篇文章，作者提出了文献的三遍阅读法，并且介绍了如何利用这种方法做文献调研。

[原文链接](https://dl.acm.org/doi/abs/10.1145/1273445.1273458)

## 摘要

> Researchers spend a great deal of time reading research papers. However, this skill is rarely taught, leading to much wasted effort. This article outlines a practical and efficient three-pass method for reading research papers. I also describe how to use this method to do a literature survey.

作者认为研究人员花了很多时间阅读文献，但是缺少文献阅读方法的指导，很多时候都是在白白努力。作者在本文中概述了一种阅读科研论文实用而有效的三遍 `three-pass` 方法，还描述了如何使用这种方法进行文献调研。

## 介绍

> Researchers must read papers for several reasons: to review them for a conference or a class, to keep current in their field, or for a literature survey of a new field. A typical researcher will likely spend hundreds of hours every year reading papers.

这段话作者主要讲了研究人员阅读文献的目的，作者认为典型的研究人员每年都会花费数百小时阅读论文。

> Learning to efficiently read a paper is a critical but rarely taught skill. Beginning graduate students, therefore, must learn on their own using trial and error. Students waste much effort in the process and are frequently driven to rustration.

作者认为学会有效阅读文献是一个关键的技能，但是很少会有人来教这些技能。因此，研究生在刚刚开始科研时必须通过试错的方式来学习，浪费了很多精力。

> For many years I have used a simple approach to efficiently read papers. This paper describes the ‘three-pass’ approach and its use in doing a literature survey.

于是作者引出本文的工作：文献的三遍阅读法，以及如何使用这种方法进行文献调研。

## 文献的三遍阅读法

> The key idea is that you should read the paper in up to three passes, instead of starting at the beginning and plowing our way to the end. Each pass accomplishes specific goals and builds upon the previous pass: The first pass gives you a general idea about the paper. The second pass lets you grasp the paper’s content, but not its details. The third pass helps you understand the paper in depth.

作者认为，不能简单从头到尾阅读文献。文献的三遍阅读法的关键在于，每一遍阅读都会完成特定的目标，并且建立在上一遍阅读收获的基础之上。第一遍阅读需要了解论文的大致想法 `general idea`；第二遍阅读需要掌握论文的内容 `content`，但不是细枝末节；第三遍阅读需要深入了解论文。

### 第一遍阅读

> The first pass is a quick scan to get a bird’s-eye view of the paper. You can also decide whether you need to do any more passes. This pass should take about five to ten minutes and consists of the following steps:
> 1. Carefully read the title, abstract, and introduction
> 2. Read the section and sub-section headings, but ignore everything else
> 3. Read the conclusions
> 4. Glance over the references, mentally ticking off the ones you’ve already read

作者认为第一遍阅读文献需要快速扫描，以对论文有一个全局的把控（作者打了一个形象的比喻：鸟瞰图 `bird’s-eye view`）。然后我们就可以决定是否还需要继续进行下一遍的阅读。这大概只需要 5 到 10 分钟，包括以下步骤：

1. 仔细阅读标题，摘要和介绍
2. 阅读每个部分 `section` 的标题和子标题，但忽略其他所有内容
3. 阅读结论
4. 浏览参考文献，在大脑中勾结 `ticking off` 你已经读过的那些文献

> At the end of the first pass, you should be able to answer the five Cs:
> 1. Category: What type of paper is this? A measurement paper? An analysis of an existing system? A description of a research prototype?
> 2. Context: Which other papers is it related to? Which theoretical bases were used to analyze the problem?
> 3. Correctness: Do the assumptions appear to be valid?
> 4. Contributions: What are the paper’s main contributions?
> 5. Clarity: Is the paper well written?

文献阅读的第一遍阅读完成后，你必须能够回答下面的 5 个问题：

1. **类别**：这是什么类型的论文？测量方法的论文？对现有系统的分析？研究原型的描述？
2. **背景**：它与其他哪些文献有关？它是基于哪些理论去分析问题的？
3. **正确性**：论文的假设合理吗？
4. **贡献**：论文的主要贡献是什么？
5. **清晰度**：论文写得好吗？

> Using this information, you may choose not to read further. This could be because the paper doesn’t interest you, or you don’t know enough about the area to understand the paper, or that the authors make invalid assumptions. The first pass is adequate for papers that aren’t in your research area, but may someday prove relevant.

有了这些信息，我们可以选择不再继续阅读。这主要有三个原因：对这篇论文不感兴趣，对涉及到的研究领域不了解，作者作出无效假设。对于不了解的研究领域，只读一遍足够了，但是可能有一天你会发现它和你的研究领域相关。

> Incidentally, when you write a paper, you can expect most reviewers (and readers) to make only one pass over it. Take care to choose coherent section and subsection titles and to write concise and comprehensive abstracts. If a reviewer cannot understand the gist after one pass, the paper will likely be rejected; if a reader cannot understand the highlights of the paper after five minutes, the paper will likely never be read.

作者还建议，当您撰写论文时，您可以期待大多数审阅者（和读者）只需要阅读一遍就能掌握上述信息。因此，注意每个部分的标题和子标题的相关性，并且摘要要简洁而全面。如果审阅者在阅读一遍后无法理解论文的要点，那么该论文可能会被拒绝; 如果读者在五分钟后无法理解论文的亮点，则可能永远不会再读这篇论文。

### 第二遍阅读

> In the second pass, read the paper with greater care, but ignore details such as proofs. It helps to jot down the key points, or to make comments in the margins, as you read.
> 1. Look carefully at the figures, diagrams and other illustrations in the paper. Pay special attention to graphs. Are the axes properly labeled? Are results shown with error bars, so that conclusions are statistically significant? Common mistakes like these will separate rushed, shoddy work from the truly excellent.
> 2. Remember to mark relevant unread references for further reading (this is a good way to learn more about the background of the paper).

作者认为第二遍阅读文献需要仔细阅读，但是应该忽略掉细节部分，例如证明。在阅读时记下要点或在页边空白处作注释会有所帮助。

1. 仔细看文章中的图形、图表和其他插图。特别注意图表。坐标轴标记正确了吗？结果是否以误差条显示，从而使结论具有统计学意义？类似这样的常见错误会将匆忙的粗制滥造的工作与真正优秀的工作区分开来。
2. 记住标记相关的未读参考文献以供进一步阅读（这是了解更多关于论文背景的好方法）。

> The second pass should take up to an hour. After this pass, you should be able to grasp the content of the paper. You should be able to summarize the main thrust of the paper, with supporting evidence, to someone else. This level of detail is appropriate for a paper in which you are interested, but does not lie in your research speciality.

作者认为，第二遍阅读要花一个小时。经过这样一遍阅读，你应该能够掌握论文的内容。你应该能够将论文的主旨和支持性证据总结给其他人。这个层次的细节适合你感兴趣的论文，但不属于你的研究专业。

> Sometimes you won’t understand a paper even at the end of the second pass. This may be because the subject matter is new to you, with unfamiliar terminology and acronyms. Or the authors may use a proof or experimental technique that you don’t understand, so that the bulk of the paper is incomprehensible. The paper may be poorly written with unsubstantiated assertions and numerous forward references. Or it could just be that it’s late at night and you’re tired. You can now choose to: (a) set the paper aside, hoping you don’t need to understand the material to be successful in your career, (b) return to the paper later, perhaps after reading background material or (c) persevere and go on to the third pass.

有时你甚至在第二遍结束时也看不懂一篇论文。这可能是因为主题 `subject matter` 对您来说是新的，具有不熟悉的术语和首字母缩写。或者，作者可能会使用你不理解的证明或实验技术，所以论文的大部分内容是无法理解的。论文可能写得很差，没有证据的断言和大量的前向参考文献。也可能是深夜，你很累。现在你可以选择:

1. 把论文放在一边，希望你不需要理解这些材料就能在学术生涯中取得成功；
2. 在阅读背景材料后再重新阅读论文；
3. 坚持下去，继续第三遍阅读。

### 第三遍阅读

> To fully understand a paper, particularly if you are reviewer, requires a third pass. The key to the third pass is to attempt to virtually re-implement the paper: that is, making the same assumptions as the authors, re-create the work. By comparing this re-creation with the actual paper, you can easily identify not only a paper’s innovations, but also its hidden failings and assumptions.

作者认为，要完全理解一篇论文，尤其是当你是审稿人的时候，需要第三遍阅读。第三遍阅读的关键是尝试重新实现 `virtually re-implement` 论文：即，做出与作者相同的假设，复现 `re-create` 论文工作（这里作者用副词 `virtually` 修饰，是想表达这个复现是你头脑的想法，可能与作者本人的想法有出入）。通过将复现的工作 `re-creation` 与实际论文进行比较，你可以很容易地识别出论文的创新之处，以及它隐藏的缺点和假设。

> This pass requires great attention to detail. You should identify and challenge every assumption in every statement. Moreover, you should think about how you yourself would present a particular idea. This comparison of the actual with the virtual lends a sharp insight into the proof and presentation techniques in the paper and you can very likely add this to your repertoire of tools. During this pass, you should also jot down ideas for future work.

这一遍阅读需要非常注意细节。你应该识别并挑战每句话中的每一个假设。此外，你应该考虑自己将如何表达一个特定的想法。这种实际 `actual`（这里作者的意思是论文的实际表述）与虚拟 `virtual`（这里作者的意思是你头脑里所想的表达的方式）的比较有助于深入了解本文中的证明和表示技术，您很可能将其添加到您的工具库中。在此期间，你还应该记下未来工作的想法。

> This pass can take about four or five hours for beginners, and about an hour for an experienced reader. At the end of this pass, you should be able to reconstruct the entire structure of the paper from memory, as well as be able to identify its strong and weak points. In particular, you should be able to pinpoint implicit assumptions, missing citations to relevant work, and potential issues with experimental or analytical techniques.

对于初学者来说，这一遍阅读大约需要 4 到 5 个小时，而对于有经验的读者来说，大约需要 1 个小时。在这一段的最后，你应该能够根据记忆重建整个论文结构，以及能够识别它的优点和缺点。特别是，您应该能够精确地指出隐含的假设、相关工作的遗漏引用，以及与实验或分析技术有关的潜在问题。

## 做文献调研

> Paper reading skills are put to the test in doing a literature survey. This will require you to read tens of papers, perhaps in an unfamiliar field. What papers should you read? Here is how you can use the three-pass approach to help.

做文献调研时非常考验一个人的文献阅读技巧。这一般需要你阅读几十篇论文，而且也许是一个不熟悉的领域。那么，你应该读哪些文献？作者就指出如何使用他在本文提出的文献的三遍阅读法来帮助我们进行文献调研。

> First, use an academic search engine such as Google Scholar or CiteSeer and some well-chosen keywords to find three to five recent papers in the area. Do one pass on each paper to get a sense of the work, then read their related work sections. You will find a thumbnail summary of the recent work, and perhaps, if you are lucky, a pointer to a recent survey paper. If you can find such a survey, you are done. Read the survey, congratulating yourself on your good luck.

首先，使用学术搜索引擎（如谷歌学术或 CiteSeer）和一些精心挑选的关键词，找到该领域的三到五篇最新论文。每一篇论文都进行一遍阅读，了解一下这篇论文的工作，然后阅读相关工作部分。你会找到最近工作的缩略摘要，如果你幸运的话，可能还会找到最近调研的论文。如果你能找到这样的论文，应该为自己的好运气而庆幸。

> Otherwise, in the second step, find shared citations and repeated author names in the bibliography. These are the key papers and researchers in that area. Download the key papers and set them aside. Then go to the websites of the key researchers and see where they’ve published recently. That will help you identify the top conferences in that field because the best researchers usually publish in the top conferences.

如果找不到，在第二步中，我们可以在参考书目中找到共享的引文 `shared citations` 和重复的作者名称。这些是该领域的关键论文和研究人员。下载关键的论文并把它们放在一边。然后访问主要研究人员的网站，看看他们最近在哪里发表的文章。这将帮助你确定该领域的顶级会议，因为最优秀的研究人员通常在顶级会议上发表文章。

> The third step is to go to the website for these top conferences and look through their recent proceedings. A quick scan will usually identify recent high-quality related work. These papers, along with the ones you set aside earlier, constitute the first version of your survey. Make two passes through these papers. If they all cite a key paper that you did not find earlier, obtain and read it, iterating as necessary.

第三步是访问这些顶级会议 `top conferences` 的网站，查看它们最近的会议记录。快速扫描通常可以识别出近期高质量的相关工作。这些论文，连同你之前搁置的那些，构成了你调查的第一个版本。把这些论文翻两遍。如果他们都引用了一篇你之前没有找到的关键论文，获取并阅读它，必要时进行迭代。

## 经验

> I’ve used this approach for the last 15 years to read conference proceedings, write reviews, do background research, and to quickly review papers before a discussion. This disciplined approach prevents me from drowning in the details before getting a bird’s-eye-view. It allows me to estimate the amount of time required to review a set of papers. Moreover, I can adjust the depth of paper evaluation depending on my needs and how much time I have.

作者在过去的 15 年里，一直使用这种方法来阅读会议记录、撰写评论、做背景研究，以及在讨论前快速审阅论文。这种有规律的方法能够防止在把握全文之前就被细节淹没。它可以估算出回顾一系列论文所需的时间。此外，作者可以根据自己的需要和时间来调整论文评估的深度。
