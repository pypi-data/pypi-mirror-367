欢迎访问 `{{ cookiecutter.project_name }}`_ 手册!
==================================================

.. _{{ cookiecutter.project_name }}: {{ cookiecutter.__project_home }}

.. toctree::
   :maxdepth: 2

   readme
   installation
   tutorial
   modules
   contributing
   {% if cookiecutter.create_author_file == 'y' -%}authors
   {% endif -%}history

导航 & 索引
=============
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
