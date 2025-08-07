.. highlight:: shell

支持本项目
============

欢迎贡献，非常感谢您的支持！任何一点帮助都很重要，并且会给予相应的认可。

您可以通过多种方式做出贡献：

贡献类型
----------------------

报告错误
~~~~~~~~~~~

请在 {{cookiecutter.__project_home}}/issues 报告错误。

如果您正在报告一个错误，请包含以下信息：

* 您的操作系统名称和版本。
* 有助于排查问题的本地设置的任何细节。
* 重现该错误的详细步骤。

修复错误
~~~~~~~~~~

浏览 {{cookiecutter.git_website}} 上的问题列表寻找错误。任何标记有 "bug" 和 "help wanted" 的问题都开放给任何人去解决。

实现功能
~~~~~~~~~~~~~~~~~~

浏览 {{cookiecutter.git_website}} 上的功能请求。任何标记有 "enhancement" 和 "help wanted" 的请求都是开放给任何人去实现的。

撰写文档
~~~~~~~~~~~~~~~~~~

无论是在官方 {{ cookiecutter.project_name }} 文档中，在文档字符串中，还是在网络上以博客文章或文章的形式，{{ cookiecutter.project_name }} 都可以使用更多的文档。

提交反馈
~~~~~~~~~~~~~~

发送反馈的最佳方式是通过 {{cookiecutter.__project_home}}/issues 创建一个问题。

如果您正在提议一个新功能：

* 详细解释它是如何工作的。
* 尽量保持范围尽可能窄，以便更容易实现。
* 记住这是一个由志愿者驱动的项目，欢迎所有形式的贡献 :)

开始吧！
------------

准备好贡献了吗？以下是为本地开发设置 `{{ cookiecutter.project_slug }}` 的方法。

1. 在 {{cookiecutter.git_website}} 上 fork `{{ cookiecutter.project_slug }}` 仓库。
2. 克隆您的 fork 到本地::

    $ git clone git@{{cookiecutter.git_website}}.com:your_name_here/{{ cookiecutter.project_slug }}.git

3. 使用 ``uv`` 配置项目环境。假设您已安装 ``uv`` ，这是设置您的 fork 进行本地开发的方法::

    $ uv sync

4. 为本地开发创建一个分支::

    $ git checkout -b name-of-your-bugfix-or-feature

   现在您可以进行本地更改了。

5. 完成更改后，检查您的更改是否通过 ``ruff`` 并通过测试，包括使用 ``tox`` 测试其他 Python 版本::

    $ make lint
    $ make test
    或者::
    $ make test-all

   要获取 ``ruff`` 和 ``tox``，只需将它们安装到您的环境中。::

    $ uv tool install ruff
    $ uv tool install tox

6. 提交您的更改并将分支推送到 ``{{cookiecutter.git_website}}``::

    $ git add .
    $ git commit -m "您对更改的详细描述。"
    $ git push origin name-of-your-bugfix-or-feature

7. 通过 ``{{cookiecutter.git_website}}`` 网站提交拉取请求。

提示
----

运行部分测试集::

{% if cookiecutter.use_pytest == 'y' -%}
    $ pytest tests.test_{{ cookiecutter.project_slug }}
{% else %}
    $ python -m unittest tests.test_{{ cookiecutter.project_slug }}
{%- endif %}

部署
---------

提醒维护者如何部署。
确保所有更改都已提交（包括 HISTORY.rst 中的条目）。
然后运行::

$ make bump
$ git push
$ git push --tags
