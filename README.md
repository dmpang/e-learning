# e-learning 自动学习程序介绍

现在很多单位都要求学习一些课程，但这些课程质量低，大多数员工不愿意学习，但与考核或绩效挂钩，又不得不学，为解决这个问题，以云端学习网站 [http://e-learning.jsnx.net](http://e-learning.jsnx.net) 为例，我在业余时间开发了自动学习程序，目的是节省你宝贵的时间。

## 功能点

1. 自动登陆，可以选择自动学习我的课程或学习地图。
2. 自动播放视频课程并执行课程评估。
3. 可以自动做题，准确率 100%。
 
可能你会问了，它是如何实现自动做题的？

## 做题原理

题目要么是选择题，要么是判断题，都可以看做是选择题。这就给自动做题提供了可能。程序采用以下步骤做题

1. 答题时优先从数据库中查询答案，如果无法找到时会去网站 [http://tiku88.com/](http://tiku88.com/) 去爬去答案, 并将答案并保存在 SQLite 数据库中。
2. 如果数据库中和网上都没有找到答案，那么等待 30s 的时间看你是否选择手工做题。
3. 如果你选择了手工做题，如果通过考试，那么请跳转到结果页面，程序会将所有正确答案自动记录在 SQlite 数据库中，方便下次使用，或帮他人使用。
4. 如果你没有做任何选择或者放弃手工做题，那么程序直接跳过本课程的做题环节，直接播放下一个课程。

## 不是 Python 程序员？

程序已经编译成可执行文件，放在在压缩包 [e-learning.rar](https://github.com/somenzz/e-learning/raw/master/e-learning.rar) 中，可以在windows 系统直接运行。

解压后直接运行这个目录中的 e-learning.exe 文件，后面加上一些参数即可。具体使用方法如下：

程序的帮助信息：

```python
e-learning.exe -h
Usage: e-learning.exe [-u] [-s] [-c] [-s] [fix]

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -u USERNAME, --username=USERNAME
                        input your account name
  -p PASSWORD, --password=PASSWORD
                        input your password
  -c COURSE, --course=COURSE
                        learn which one? [学习地图=0 我的课程=1]
  -s SKIPNUM, --skipnum=SKIPNUM
                        skip number,跳过开头多少个课程，防止卡住，一般不常用
  -n NUMBER, --number=NUMBER
                        number,学习地图中从上到下第几个要学的任务，默认为1

```

如果要学习【学习地图】可以这样执行：

```python
e-learning.exe -u xxxx -p xxxx -c 0
```
也可以这样执行：

```python
e-learning.exe --username xxxx --password xxxx --course 0
```

如果学习地图中有多个季度的任务需要学习，假如从上到下分别是第四季度、第三季度、第二季度，第一季度，对应的编号分别是 1，2，3，4
因此，默认学习第四季度，如果要学习第三季度，则执行

```python
e-learning.exe --username xxxx --password xxxx --course 0 --number 2
```
学习第二季度，则执行

```python
e-learning.exe --username xxxx --password xxxx --course 0 --number 3
```


如果因为前面的视频无法自动播放，可选择跳过前面多少个课程，比如跳过前 2 个课程

```python
e-learning.exe --username xxxx --password xxxx --course 0 --skipnum 2
#等同于
e-learning.exe -u xxxx -p xxxx -c 0 -s 2
```

如果要学习【我的课程】可以这样执行：

```python
e-learning.exe -u xxxx -p xxxx -c 1
```
其他写法同上。





## 程序源文件介绍

1、answers.db - 保存所有的题目信息和正确答案。

2、chromedriver.exe - 谷歌浏览器的驱动程序，只要你的浏览器版本较新都可以运行。比如我的是 71.0.3578.98。如果无法运行请更新谷歌浏览器。

3、e-learning.py - 程序的核心程序。

4、get_answer.py - 爬取答案的模块。

5、info.log - 日志文件。

6、insert_into_db.py - sqlite 交互的测试程序，练习用，可忽略。

7、mini_shell.py - 可以直接写 SQL 查询 sqlite 数据库中的表和数据。

8、requirements.txt - 依赖的库模块。

9、right.html - 可用于手工修复答案。

## 如何使用


程序的帮助信息：

```python
python e-learning.py -h
```

源代码可直接运行，如果要学习【学习地图】可以这样执行：

```python
python e-learning.py -u xxxx -p xxxx -c 0
```
也可以这样执行：

```python
python e-learning.py --username xxxx --password xxxx --course 0
```
如果学习地图中有多个季度的任务需要学习，假如从上到下分别是第四季度、第三季度、第二季度，第一季度，对应的编号分别是 1，2，3，4
因此，默认学习第四季度，如果要学习第三季度，则执行

```python
python e-learning.py --username xxxx --password xxxx --course 0 --number 2
```
学习第二季度，则执行

```python
python e-learning.py --username xxxx --password xxxx --course 0 --number 3
```


如果因为前面的视频无法自动播放，可选择跳过前面多少个课程，比如跳过前 2 个课程

```python
python e-learning.py --username xxxx --password xxxx --course 0 --skipnum 2
#等同于
python e-learning.py -u xxxx -p xxxx -c 0 -s 2
```

如果要学习【我的课程】可以这样执行：

```python
python e-learning.py -u xxxx -p xxxx -c 1
```
其他写法同上。


## 小提示

初次播放视频时，需要你手动允许浏览器加载 Flash,这个我有试过写代码让谷歌浏览器自动加载 Flash ，但试了多种途径都失败了。

如果你可以实现，请一定告诉我这个二流子程序员，非常感谢。

如果有类似的视频网站，你可以随意修改代码来适配。


## 最后

编码不易，如果觉得对你和身边的人有帮助，请给个 star。

请勿用于商业用途。

个人公众号 somenzz，专注于有价值的 Python 技术分享，欢迎订阅。

个人微信号 somenzz，欢迎加好友与我交流。
