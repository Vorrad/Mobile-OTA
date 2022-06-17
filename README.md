# 安全OTA升级系统

本项目旨在搭建安全的车载OTA升级系统，用以完成对于uptane这一开源OTA框架的可实践项目的搭建。项目目标在于模拟服务器端和车端，完成OTA完整的升级流程。

云服务器前端依托于Django+uwsgi+nginx，实现服务器端升级包可视化展示与管理。

后端服务器依托于Flask+gunicorn，完成OTA核心的升级功能。

目前，项目已经部署在云服务器上，地址：[139.196.40.15](139.196.40.15/image/)

- 访问前端服务器主页URL：http://139.196.40.15/image/

## 参考项目

1. Uptane：Securing Software Updates for Automobiles
   - 项目网址：[https://uptane.github.io/](https://uptane.github.io/)
   - 代码仓库：[https://github.com/uptane/obsolete-reference-implementation](https://github.com/uptane/obsolete-reference-implementation)

2. TUF: A Framework for Securing Software Update Systems, Adapted for Uptane's Purposes
   - 代码仓库：[https://github.com/awwad/tuf](https://github.com/awwad/tuf)

## 目录结构

- APIs/：在阅读Uptane项目过程中成员一起编写的API文档
- Django/：前端服务器工程目录
  - djangoProject/：Django配置目录
  - OTA/views.py：前端视图文件
  - media/files/：用户上传的文件保存目录
- Flask/：后端服务器和车辆客户端工程目录（由Uptane仓库改造）
  - requirement/：环境配置文件，具体环境配置流程见docs/部署文档.pdf
  - demo/：包含后端服务器与车辆客户端的入口程序
  - postman_api.json：测试用接口（可导入postman）
- docs/：项目文档目录
- Demo/：演示文件目录
  - 项目演示.pptx：部分演示截图（详细过程见测试文档）
  - 项目展示*.mp4：完整的测试过程录像（未剪辑）

## 其他文档

- [项目进度管理文档（更新至5.10）](https://notes.sjtu.edu.cn/cpWctnImQk-LVpGwyGdn3g)
- [Uptane学习笔记](https://notes.sjtu.edu.cn/zZO5swNHRL-Iu9MiBYcIbA)
