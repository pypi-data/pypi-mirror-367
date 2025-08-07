使用教程
==========

当你创建一个包时，系统会提示你输入这些值.

输入选项
----------------

以下选项会出现在生成项目的不同位置.

project_name
    你的新 Python 包项目的名称.这将用于文档中，因此可以包含空格和任何字符.

project_slug
    你的 Python 包的命名空间.这应该是对 Python 导入友好的. 通常，它是 project_name 的 slugified 版本. 注意：你的 PyPi 项目链接将使用 project_slug，所以在 README 中相应地修改这些链接.

username
    你的全名.

email
    你的电子邮件地址.

username
    你的 GitHub 用户名.

git_website
    你项目托管的地址，选项包括:
        - gitee
        - gitcode
        - github

project_short_description
    一句描述你的 Python 包功能的简要介绍.

version
    包的初始版本号.

选项
-------

以下包配置选项为你的项目设置了不同的特性.

use_pytest
    是否使用 `pytest <https://docs.pytest.org/en/latest/>`_ 进行测试.

theme
    主题配置, 选项包括:
        - sphinx_rtd_theme
        - alabaster
        - bizstyle
        - classic
        - press
        - piccolo_theme

command_line_interface
    是否使用 Click 创建一个控制台脚本. 控制台脚本入口点将与 project_slug 相匹配. 选项包括：
        - Typer
        - Argparse
        - No command-line interface

create_author_file
    是否创建一个作者文件.

open_source_license
    选择一个 `开源许可证 <https://choosealicense.com/>`_. 选项包括:
        - MIT license
        - BSD license
        - ISC license
        - Apache Software License 2.0
        - GNU General Public License v3
        - Not open source
