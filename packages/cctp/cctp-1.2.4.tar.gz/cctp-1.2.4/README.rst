cctp
=======

简介
------

用于快速搭建 `Python` 项目的 `Cookiecutter <https://www.cookiecutter.io/>`_ 模板.

**主要特性:**

- 支持 ``Python >= 3.8`` 环境
- 支持 ``uv`` 构建项目
- 支持 ``sphinx`` 文档构建工具
- 支持 ``alabaster`` / ``sphinx_rtd_theme`` / ``classic`` 等多种文档风格
- 支持 ``Typer`` / ``Argparse`` 命令行项目

快速开始
----------

安装 ``cctp``: ::

    $ pip install cctp  # 通过 pip
    $ uv tool install cctp  # 通过 uv

使用 ``cctp`` 创建 `Python` 项目模板: ::

    $ cctp  # 直接使用
    $ uvx cctp  # 通过 uv

也可使用以下方式: ::

    $ uvx cookiecutter https://gitee.com/gooker_young/cctp.git


离线模式运行
--------------

下载本项目源代码 ``zip`` 文件: ::

    $ wget https://gitee.com/gooker_young/cctp/repository/archive/develop.zip

解压到文件夹:

- windows: ``C:\Users\xxx\.cookiecutters\cctp``
- linux: ``/home/xxx/.cookiecutters/cctp``

运行命令: ::

    $ cctp --offline
