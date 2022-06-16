# 汽车OTA

## 项目工作目录

Web/

## 分支管理tips

- 现阶段的改动均在Uptane_Demo分支上进行
- 每次工作前，先从Uptane_Demo分支上把最新修改merge到自己的分支上，更新完成后再merge到Uptane_Demo分支上，并通知大家
- commit的时候尽可能详细地描述本次提交的改动



## Django 相关

1. html文件可以存放在与views.py文件同级的目录下的templates/文件夹里，以供views通过默认路径调用
2. 鼓励写尽可能详细的注释和API，可以自建目录和文件。在commit提交信息中体现即可

API文件没有固定书写规范，原则是简洁、易懂。存放位置尽量和对应的源代码相同，文件名也易于识别

如：`director.py`文件和`views.py`的交互接口可以用`director.api`命名
