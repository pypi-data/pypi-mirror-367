<!--
 * @Description: 
 * @Date: 2023-02-09 18:18:16
 * @LastEditTime: 2023-02-15 14:42:18
 * @FilePath: /m-git-master/yhgit.md
-->
# yhgit

<!-- <div style="background-color: lightgreen; color: white; padding: 0 30px; height: 40px; line-height: 40px; display: inline-block; width: auto; font-size: 20px; font-weight: bold;">run success</div> -->




yhgit 是一款基于 Python 封装的关于 Git 的多仓库管理工具，可以高效，方便的对多个 Git 仓库执行 Git 命令。
适合于在多个仓库中进行关联开发的项目，提高 Git 操作的效率，避免逐个项目执行 Git 命令带来的误操作风险。

- **易用的命令**
封装 Git 命令，命令和参数均由 Git 衍生而来，会使用 Git 就可以成本低上手 MGit。

- **直观高效的执行命令**
提供图表化的结果展示，开发者可以快速查看命令在多个仓库的执行结果；
提供进度展示，开发者可以直观看到当前执行到哪个仓库；

- **安全的执行命令**
在执行命令前对多仓库状态进行安全检查：分支是否异常，工作区是否未提交代码，是否有冲突，等；

## 快速开始

1. &#9888; 确保Python版本最低为 3.7
2. &#9888; 手动创建PodfileModule; 确保按[PodfileModule文件介绍](md/podfilemodule.md)配置文件PodfileModule
3. &#9888; 自动创建PodfileModule; 请执行[yhgit init](md/common-commands.md)
4. &#9888; 确保按[配置podfile](md/podfile.md) 配置Podfile文件

#### 1、安装 yhgit 工具


```ruby
$ pip3 install yhgit
```
 &#9888; 注意第一次安装使用以上命令，要想安装最新版本请使用[Pypi](https://pypi.org/)或者`pip install --upgrade yhgit`安装最新版本
#### 2、准备

- 用Git 将项目 Clone 到本地

- 在根目录下，执行[yhgit init](md/common-commands.md)或者新建PodfileModule.yaml 文件，格式如下

```yaml

version: 1.0.0
branch:
dependencies:
- module: A
  pod: A
  version:
  git: git@xxx.xxx.cn:xxx/a.git
  branch:
  tag: 1.0.0
  configurations:
  path:
  inhibit_warnings: false
  ```

- 修改Podfile文件
  [配置Podfile](md/podfile.md)


#### 2、初始化多仓库 

初始化多仓库使用 `yghit install` 命令;

类似于 Git 从远程 clone 新仓库, 会将多个仓库 clone 到本地;

下面通过一个 demo 体验一下 yhgit 命令：

```ruby
# 2.1 根据PodfileModule.yaml中组件A配置的git，tag或者branch，新建开发分支 test
$ yhgit install -b test A

# 2.2 体验一下mgit命令
$ yhgit init -b xxx.git       切新的开发分支，并自动创建yaml文件
$ yhgit status                查看多个仓库状态
$ yhgit commit -m '提交信息'   提交多仓库的代码
$ yhgit pull                  拉取远端代码
$ yhgit push                  推送代码
$ yhgit release               自动release代码
$ yhgit merge -b master A     merge分支master到当前的开发分支
```


#### 3、已有多仓库如何迁移到 yhgit 管理

- 根据文档[配置 PodfileModule.yaml](md/podfilemodule.md)

  将要管理的仓库都配置到 PodfileModule.yaml 中
  
- 根据文档[配置 Podfile](md/podfile.md)

     
- 使用 `yhgit install -b test A B` 初始化多仓库

  - 新建modules文件
  - 基于`PodfileModule.yaml`中组件组件`A`, `B`的配置信息, 新建开发分支`test`
  - 更新`PodfileModule.yaml`中组件组件`A`, `B`的配置信息, 依赖信息branch为`test`
  - 更新`PodfileLocal.yaml`中组件组件`A`, `B`的配置信息，依赖为path分别为`modules/A`及`modules/B`

  

#### 4、进一步了解 yhgit

[常用命令](md/common-commands.md)

[PodfileModule文件介绍](md/podfilemodule.md)

[配置podfile](md/podfile.md) 






