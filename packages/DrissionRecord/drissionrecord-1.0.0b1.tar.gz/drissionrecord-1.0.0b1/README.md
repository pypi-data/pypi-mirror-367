# ⭐️ 简介

本库是一个基于 python 的工具集，用于记录数据到文件。

使用方便，代码简洁，是一个可靠、省心且实用的工具。

支持多线程同时写入文件。

**联系邮箱：** g1879@qq.com

**使用手册：** 📒[点击打开](https://DrissionPage.cn/DrissionRecord/)

# ✨️ 理念

简单，可靠，省心。

# 📕 背景

进行数据采集的时候，常常要保存数据到文件，频繁开关文件会影响效率，而如果等采集结束再写入，会有因异常而丢失数据的风险。

因此写了这些工具，只要把数据扔进去，它们能缓存到一定数量再一次写入，减少文件开关次数，且在程序崩溃或退出时尽量自动保存。

它们使用非常方便，无论何时何地，无论什么格式，只要使用`add_data()`方法把数据存进去即可，语法极其简明扼要，使程序员能更专注业务逻辑。

它们还相当可靠，作者曾一次过连续记录超过 300 万条数据，也曾 50 个线程同时运行写入数万条数据到一个文件，依然轻松胜任。

工具还对表格文件（xlsx、csv）做了很多优化，封装了实用功能，可以使用表格文件方便地实现断点续爬、批量转移数据、指定坐标填写数据等。

# 🍀 特性

- 可以缓存数据到一定数量再一次写入，减少文件读写次数，降低开销。
- 支持多线程同时写入数据。
- 写入时如文件打开，会自动等待文件关闭再写入，避免数据丢失。
- 对断点续爬提供良好支持。
- 可方便地批量转移数据。
- 可根据字典数据自动创建表头。
- 自动创建文件和路径，减少代码量。

# 🌠 概览

这里简要介绍各种工具用途，详细用法请查看使用方法章节。

各个工具有着相同的使用逻辑：创建对象 -> 添加数据 -> 记录数据。

## ⚡ 记录器`Recorder`

`Recorder`的功能强大直观高效实用。可以接收单行数据，或二维数据一次写入多行。

可指定坐标写入数据，也可为 xlsx 设置单元格格式、图片和链接等。

支持自动匹配表头，支持文件数据读取。

支持 csv、xlsx、json、jsonl、txt 四种格式文件。

```python
from DrissionRecord import Recorder

data = ((1, 2, 3, 4), 
        (5, 6, 7, 8))

r = Recorder('data.csv')
r.add_data(data)  # 一次记录多行数据
r.add_data('abc')  # 记录单行数据
```

## ⚡ 二进制数据记录器`ByteRecorder`

`ByteRecorder`用法最简单，它和`Recorder`类似，记录多个数据然后按顺序写入文件。

不一样的是它只接收二进制数据，每次`add_data()`只能输入一条数据，而且没有行的概念。

```python
from DrissionRecord import ByteRecorder

b = ByteRecorder('data.file')
b.add_data(b'*****************')  # 向文件写入二进制数据
```

## ⚡ 数据库记录器`DBRecorder`

支持 sqlite，用法和`Recorder`一致，支持自动创建数据库、数据表、数据列。

```python
from DrissionRecord import DBRecorder

d = DBRecorder('data.db')
d.add_data({'name': '张三', 'age': 25}, table='user')  # 插入数据到user表
d.record()
```

# ☕ 请我喝咖啡

如果本项目对您有所帮助，不妨请作者我喝杯咖啡 ：）

![](https://gitee.com/g1879/DrissionPageDocs/raw/master/static/img/code.jpg)
