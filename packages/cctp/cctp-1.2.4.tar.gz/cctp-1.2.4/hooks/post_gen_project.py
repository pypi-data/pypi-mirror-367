#!/usr/bin/env python
import pathlib
import shutil
import subprocess

if __name__ == "__main__":
    if "{{ cookiecutter.create_author_file }}" != "y":
        pathlib.Path("AUTHORS.rst").unlink()
        pathlib.Path("docs", "authors.rst").unlink()

    if "no command-line" in "{{ cookiecutter.command_line_interface|lower }}":
        pathlib.Path("src", "{{ cookiecutter.project_slug }}", "cli.py").unlink()

    for website in ["gitee", "gitcode", "github"]:
        if "{{cookiecutter.git_website}}" != website:
            shutil.rmtree(pathlib.Path(f".{website}"), True)

    if "Not open source" == "{{ cookiecutter.open_source_license }}":
        pathlib.Path("LICENSE").unlink()

    # sort pyproject.toml file
    subprocess.run(["uvx", "toml-sort", "--in-place", "pyproject.toml"])
