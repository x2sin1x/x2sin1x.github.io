---
inHomePost: false
title: "Git 分支管理"
---

# Git 分支管理

## 分支的基本操作

### 创建分支

在版本回退一章中，我们知道，每次提交，**Git** 都把它们串成一条时间线，这条时间线就是一个分支。截止到目前，只有一条时间线，在 **Git** 里，这个分支叫主分支，即 `master` 分支。`HEAD` 严格来说不是指向提交，而是指向 `master`，`master` 才是指向提交的，所以，`HEAD` 指向的就是当前分支。

一开始的时候，`master` 分支是一条线，**Git** 用 `master` 指向最新的提交，再用 `HEAD` 指向 `master`，就能确定当前分支，以及当前分支的提交点。每次提交，`master` 分支都会向前移动一步，这样，随着你不断提交，`master` 分支的线也越来越长。

现在我们来创建一个新的分支 `dev`：

```sh
git checkout -b dev
```

它相当于以下两条命令：

```sh
git branch dev
git checkout dev
git branch			#可以使用此命令列出所有分支
```

### 合并分支

当我们在 `dev` 分支下进行开发时，会修改本地仓库的一些文件。此时如果切换回主分支：

```sh
git checkout master
```

会发现刚才工作编辑的文件都丢失了，因为那个提交是在 `dev` 分支上，而 `master` 分支此刻的提交点并没有变。

现在，我们把 `dev` 分支的工作成果合并到 `master` 分支上：

```sh
git merge dev		#合并指定分支到当前分支
```

**快进模式**

```
Updating d46f35e..b17d20e
Fast-forward
 readme.txt | 1 +
 1 file changed, 1 insertion(+)
```

注意到上面的 `Fast-forward` 信息，**Git** 告诉我们，这次合并是“快进模式”，也就是直接把 `master` 指向 `dev` 的当前提交，所以合并速度非常快。

当然，也不是每次合并都能 `Fast-forward`，我们后面会讲其他方式的合并。

### 删除分支

合并完成后，就可以放心地删除 `dev` 分支了：

```sh
git branch -d dev
```

### 切换分支

现在 **Git** 建议使用 `switch` 命令来切换分支，一来是为了更容易理解，二来前面讲过的撤销修改则是 `git checkout -- <file>`，同一个命令，有两种作用，确实有点令人迷惑。

```sh
git switch -c dev	#创建并切换到新的dev分支
git switch master	#直接切换到已有的master分支
```

## 解决冲突

人生不如意之事十之八九，合并分支往往也不是一帆风顺的。

现在我们的仓库下有一个文本文件 `readme.txt`，内容为：

```
Creating a new branch is quick and simple.
```

准备新的 `feature1` 分支，继续我们的新分支开发：

```sh
$ git switch -c feature1
Switched to a new branch 'feature1'
```

修改 `readme.txt` 最后一行，改为：

```
Creating a new branch is quick AND simple.
```

在 `feature1` 分支上提交：

```sh
$ git add readme.txt

$ git commit -m "AND simple"
[feature1 14096d0] AND simple
 1 file changed, 1 insertion(+), 1 deletion(-)
```

切换到 `master` 分支：

```sh
$ git switch master
Switched to branch 'master'
Your branch is ahead of 'origin/master' by 1 commit.
  (use "git push" to publish your local commits)
```

**Git** 还会自动提示我们当前 `master` 分支比远程的 `master` 分支要超前1个提交。

在 `master` 分支上把 `readme.txt` 文件的最后一行改为：

```
Creating a new branch is quick & simple.
```

提交：

```sh
$ git add readme.txt 
$ git commit -m "& simple"
[master 5dc6824] & simple
 1 file changed, 1 insertion(+), 1 deletion(-)
```

现在，`master` 分支和 `feature1` 分支各自都分别有新的提交，变成了这样：

![](https://www.liaoxuefeng.com/files/attachments/919023000423040/0)

当在不同的分支中对同一个文件的同一个地方作了不同的修改，像例子中把小写的 `and` 分别改成大写的 `AND` 和 `&`，**Git** 无法执行“快速合并”，只能试图把各自的修改合并起来，但这种合并就可能会有冲突，我们试试看：

```sh
$ git merge feature1
Auto-merging readme.txt
CONFLICT (content): Merge conflict in readme.txt
Automatic merge failed; fix conflicts and then commit the result.
```

果然冲突了！ **Git** 告诉我们，`readme.txt` 文件存在冲突，必须手动解决冲突后再提交。`git status` 也可以告诉我们冲突的文件：

```sh
$ git status
On branch master
Your branch is ahead of 'origin/master' by 2 commits.
  (use "git push" to publish your local commits)

You have unmerged paths.
  (fix conflicts and run "git commit")
  (use "git merge --abort" to abort the merge)

Unmerged paths:
  (use "git add <file>..." to mark resolution)

	both modified:   readme.txt

no changes added to commit (use "git add" and/or "git commit -a")
```

我们可以直接查看 `readme.txt` 的内容：

```
 **Git**  is a distributed version control system.
 **Git**  is free software distributed under the GPL.
 **Git**  has a mutable index called stage.
 **Git**  tracks changes of files.
<<<<<<< HEAD
Creating a new branch is quick & simple.
=======
Creating a new branch is quick AND simple.
>>>>>>> feature1
```

**Git** 用 `<<<<<<<`，`=======`，`>>>>>>>` 标记出不同分支的内容，我们修改如下后保存：

```
Creating a new branch is quick and simple.
```

再提交：

```sh
$ git add readme.txt 
$ git commit -m "conflict fixed"
[master cf810e4] conflict fixed
```

现在，`master` 分支和 `feature1` 分支变成了下图所示：

![](https://www.liaoxuefeng.com/files/attachments/919023031831104/0)

用带参数的 `git log` 也可以看到分支的合并情况：

```sh
$ git log --graph --pretty=oneline --abbrev-commit
*   cf810e4 (HEAD -> master) conflict fixed
|\  
| * 14096d0 (feature1) AND simple
* | 5dc6824 & simple
|/  
* b17d20e branch test
* d46f35e (origin/master) remove test.txt
* b84166e add test.txt
* 519219b git tracks changes
* e43a48b understand how stage works
* 1094adb append GPL
* e475afc add distributed
* eaadf4e wrote a readme file
```

最后，删除 `feature1` 分支：

```sh
$ git branch -d feature1
Deleted branch feature1 (was 14096d0).
```

## 分支管理策略

### 禁用快进模式

通常，合并分支时，如果可能，**Git** 会用 `Fast forward` 模式，但这种模式下，删除分支后，会丢掉分支信息。

如果要强制禁用 `Fast forward` 模式，**Git** 就会在merge时生成一个新的commit，这样，从分支历史上就可以看出分支信息。

```sh
git merge --no-ff -m "merge with no-ff" dev
```

因为本次合并要创建一个新的commit，所以加上 `-m` 参数，把commit描述写进去。

### 新功能分支

软件开发中，总有无穷无尽的新的功能要不断添加进来。当我们在 `dev` 分支上工作时，突然项目经理下了一个新任务，要实现一个名为 `Make America Grete Again` 的新功能。

添加一个新功能时，你肯定不希望因为一些实验性质的代码，把主分支搞乱了，所以，每添加一个新功能，最好新建一个 `feature` 分支，在上面开发，完成后，合并，最后，删除该 `feature` 分支。

准备开发，创建新分支：

```sh
git switch -c feature-MAGA
```

你很牛逼，5分钟就实现了这个功能并且测试通过提交，然后你切回 `dev` 分支准备合并。突然，项目经理说经（川）费（普）不（败）足（选），新功能必须取消！

虽然白干了，但是这个包含机密资料的分支还是必须就地销毁：

```sh
git branch -d feature-MAGA
```

此时是无法删除分支的，因为 `feature-MAGA` 分支还没有被合并。如果删除，将丢失掉修改，如果要强行删除，需要使用大写的 `-D` 参数：

```sh
git branch -D feature-MAGA
```

**小结**

- 开发一个新 `feature`，最好新建一个分支；
- 如果要丢弃一个没有被合并过的分支，可以通过 `git branch -D <name>` 强行删除。

## 多人协作

### 分情况使用分支

实际的软件开发过程中一定会涉及到多人协作，每个人都负责自己开发的部分。即使软件耦合程度足够低，任何一个人的开发出现问题都会影响到整个软件开发的进度。

使用分布式版本控制系统 **Git** 是一个好办法。**Git** 提供了分支这样一个非常强大的功能，使得多人协作开发软件的效率非常之高。

分支在本地和远程可以具有对应关系，例如 `master` 分支，也可能只存在于本地。那么，哪些分支需要推送，哪些不需要呢？存在以下几个原则：

- `master` 分支是主分支，因此要时刻与远程同步；
- `dev` 分支是开发分支，团队所有成员都需要在上面工作，所以也需要与远程同步；
- bug分支只用于在本地修复bug，就没必要推到远程了，除非老板要看看你每周到底修复了几个bug；
- `feature` 分支是否推到远程，取决于你是否和你的小伙伴合作在上面开发。
- **Git** 鼓励在开发过程中使用分支，随着开发的进度逐步走向尾声，分支会逐渐合并，最后往往只剩下一个 `master` 分支。

当其他同事推送了他的工作后，正确的做法是先拉取他的修改与本地合并，然后再将自己的工作推送。

```sh
git pull origin dev
```

它相当于：

```sh
git fetch origin dev
git merge dev
```

显然，如果直接 `pull`，很可能会产生冲突，需要手动解决。

### 多人协作的工作模式

1. 首先，可以试图用 `git push origin <branch-name>` 推送自己的修改；
2. 如果推送失败，则因为远程分支比你的本地更新，需要先用 `git pull` 试图合并；
3. 如果合并有冲突，则解决冲突，并在本地提交；
4. 没有冲突或者解决掉冲突后，再用 `git push origin <branch-name>` 推送就能成功！

如果 `git pull` 提示 `no tracking information`，则说明本地分支和远程分支的链接关系没有创建，用命令 `git branch --set-upstream-to <branch-name> origin/<branch-name>`。

### 拉取请求

在远程仓库中，我们可以发起 `Pull Request`，表示远程的某一分支向当前分支合并。

这种操作通常会发生在 `dev` 分支向 `master` 分支合并的时候。一般地，`master` 分支下的项目是绝对没有任何bug的，是具有一定功能或者框架的软件。开发者们通常在 `dev` 分支上协作开发，在这个过程中会出现bug（主要是耦合上的，因为内聚上不可能推送上来）或者是冲突。在解决了这些问题之后，一般能够测试通过，于是任务进度继续向前推进，需要将 `dev` 分支合并到 `master` 分支。这样才能够绝对确保至少有一个 `master` 分支不会出现任何问题。

因此，开发团队常常将 `master` 分支设置为不可直接 `push`，也就是说任何开发人员都只能拉取主分支而不能推送自己的代码到主分支。于是，修改主分支的方法只剩下发起 `Pull Request` 一种，大大提高了安全性。一般来说，项目组的组长在开发分支测试通过后会发起 `Pull Request` 合并到主分支。如果是开源软件的多人协作，则可能由独立的个人开发者发起 `Pull Request`，然后他可以请求团队成员核查并确认。只有这些其他成员同意了才能够成功合并。

### 变基技术

多人在同一个分支上协作时，很容易出现冲突。即使没有冲突，后 `push` 的童鞋不得不先 `pull`，在本地合并，然后才能 `push` 成功。

**Git** 有没有办法让提交历史是一条干净的直线？这就是 `rebase`：

```sh
git rebase
```

`rebase` 的原理是把我们本地的提交“挪动”了位置，但是最终提交的内容是一样的。这就是 `rebase` 操作的特点：把分叉的提交历史“整理”成一条直线，看上去更直观。缺点是本地的分叉提交已经被修改过了。
