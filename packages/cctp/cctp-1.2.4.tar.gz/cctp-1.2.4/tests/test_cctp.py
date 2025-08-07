from __future__ import annotations

import datetime
import os
import pathlib
import shlex
import shutil
import subprocess
import typing
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from typing import Generator

if typing.TYPE_CHECKING:
    from unittest.mock import MagicMock

    from pytest_cookies.plugin import Result


@contextmanager
def inside_dir(dirpath: Path) -> Generator[None, None, None]:
    """在指定目录执行测试.

    Args:
        dirpath: 目标目录.

    Yields:
        None
    """
    old_path = Path.cwd()
    try:
        os.chdir(str(dirpath))
        yield
    finally:
        os.chdir(old_path)


@contextmanager
def bake_in_temp_dir(
    cookies: MagicMock,
    *args: tuple[Any, ...],
    **kwargs: dict[Any, Any],
) -> Generator[Result, None, None]:
    """删除临时目录并执行测试.

    Args:
        cookies: 用于生成项目的 `Cookie` 对象.
        *args: 传递给 `cookies.bake()` 的参数.
        **kwargs: 传递给 `cookies.bake()` 的关键字参数.

    Yields:
        None
    """
    result = cookies.bake(*args, **kwargs)
    try:
        yield result
    finally:
        shutil.rmtree(str(result.project_path))


def run_inside_dir(command: str, dirpath: Path) -> int:
    """在指定目录执行命令.

    Args:
        command: 要执行的命令.
        dirpath: 目标目录.

    Returns:
        命令执行结果.
    """
    with inside_dir(dirpath):
        return subprocess.check_call(shlex.split(command))


def test_bake_with_defaults(cookies: MagicMock) -> None:
    """确保使用默认参数生成项目.

    Args:
        cookies: 用于生成项目的 `Cookie` 对象.
    """
    with bake_in_temp_dir(cookies) as result:
        # 确认 bake 成功
        assert result.exit_code == 0
        assert result.exception is None

        # 确认生成的项目目录存在
        assert result.project_path
        assert result.project_path.is_dir()

        # 检查特定文件是否存在
        assert (result.project_path / "README.rst").is_file()

        # 确认生成的文件或目录存在
        toplevel_files = {f.name for f in result.project_path.iterdir()}
        assert {
            "docs",
            "src",
            "tests",
            ".editorconfig",
            ".gitignore",
            ".pre-commit-config.yaml",
            "LICENSE",
            "pyproject.toml",
            "README.rst",
            "tox.ini",
        }.issubset(toplevel_files)


def test_year_compute_in_license_file(cookies: MagicMock) -> None:
    """确保许可证文件中的年份正确计算.

    Args:
        cookies: 用于生成项目的 `Cookie` 对象.
    """
    with bake_in_temp_dir(cookies) as result:
        assert result.project_path

        license_file_path = result.project_path / "LICENSE"
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        assert str(now.year) in license_file_path.read_text()


def test_bake_and_run_tests(cookies: MagicMock) -> None:
    """确保项目可以运行测试.

    Args:
        cookies: 用于生成项目的 `Cookie` 对象.
    """
    with bake_in_temp_dir(cookies) as result:
        assert result.project_path
        assert result.project_path.is_dir()

        assert run_inside_dir("mkp test", result.project_path) == 0


def test_bake_withspecialchars_and_run_tests(cookies: MagicMock) -> None:
    """确保 `full_name` 中的引号不会导致项目无法运行测试.

    Args:
        cookies: 用于生成项目的 `Cookie` 对象.
    """
    with bake_in_temp_dir(
        cookies,
        extra_context={"full_name": "name 'quote' name"},
    ) as result:
        assert result.project_path
        assert result.project_path.is_dir()
        assert run_inside_dir("mkp test", result.project_path) == 0


def test_bake_with_apostrophe_and_run_tests(cookies: MagicMock) -> None:
    """确保 `full_name` 中的单引号不会导致项目无法运行测试.

    Args:
        cookies: 用于生成项目的 `Cookie` 对象.
    """
    with bake_in_temp_dir(
        cookies,
        extra_context={"full_name": "O'connor"},
    ) as result:
        assert result.project_path
        assert result.project_path.is_dir()
        assert run_inside_dir("mkp test", result.project_path) == 0


def test_bake_without_author_file(cookies: MagicMock) -> None:
    """测试创建 `AUTHORS.rst` 文件.

    Args:
        cookies: 用于生成项目的 `Cookie` 对象.
    """
    with bake_in_temp_dir(
        cookies,
        extra_context={"create_author_file": "n"},
    ) as result:
        assert result.project_path
        toplevel_files = [f.name for f in result.project_path.iterdir()]
        assert "AUTHORS.rst" not in toplevel_files
        doc_files = [f.name for f in (result.project_path / "docs").iterdir()]
        assert "authors.rst" not in doc_files

        # Assert there are no spaces in the toc tree
        docs_index_path = result.project_path / "docs" / "index.rst"
        assert "contributing\n   history" in docs_index_path.read_text()

        # Check that
        manifest_path = result.project_path / "MANIFEST.in"
        assert "AUTHORS.rst" not in manifest_path.read_text()


def check_output_inside_dir(command: str, dirpath: Path) -> bytes:
    """执行命令并返回输出.

    Args:
        command: 要执行的命令.
        dirpath: 要在其中执行命令的目录.

    Returns:
        命令输出.
    """
    with inside_dir(dirpath):
        return subprocess.check_output(shlex.split(command))


def test_bake_selecting_license(cookies: MagicMock) -> None:
    license_strings = {
        "MIT license": "MIT ",
        "BSD license": "Redistributions of source code must retain the "
        "above copyright notice, this",
        "ISC license": "ISC License",
        "Apache Software License 2.0": "Licensed under the Apache License, Version 2.0",  # noqa: E501
        "GNU General Public License v3": "GNU GENERAL PUBLIC LICENSE",
    }
    for license_, target_string in license_strings.items():
        with bake_in_temp_dir(
            cookies,
            extra_context={"open_source_license": license_},
        ) as result:
            assert result.project_path
            assert (
                target_string in (result.project_path / "LICENSE").read_text()
            )


def test_bake_not_open_source(cookies: MagicMock) -> None:
    """确保当选择非开源许可证时不会生成 LICENSE 文件.

    Args:
        cookies: 用于生成项目的 `Cookie` 对象.
    """
    with bake_in_temp_dir(
        cookies,
        extra_context={"open_source_license": "Not open source"},
    ) as result:
        assert result.project_path
        toplevel_files = [f.name for f in result.project_path.iterdir()]
        assert "LICENSE" not in toplevel_files
        assert "License" not in (result.project_path / "README.rst").read_text(
            encoding="utf8",
        )


def test_using_pytest(cookies: MagicMock) -> None:
    """Ensure that pytest is not generated by default.

    Args:
        cookies: 用于生成项目的 `Cookie` 对象.
    """
    with bake_in_temp_dir(cookies, extra_context={"use_pytest": "y"}) as result:
        assert result.project_path
        assert result.project_path.is_dir()
        test_file_path = (
            result.project_path / "tests" / "test_python_boilerplate.py"
        )
        assert "import pytest" in test_file_path.read_text()
        assert run_inside_dir("mkp test", result.project_path) == 0


def test_not_using_pytest(cookies: MagicMock) -> None:
    with bake_in_temp_dir(cookies, extra_context={"use_pytest": "n"}) as result:
        assert result.project_path
        assert result.project_path.is_dir()
        test_file_path = (
            result.project_path / "tests" / "test_python_boilerplate.py"
        )
        texts = test_file_path.read_text()
        assert "import unittest" in texts
        assert "import pytest" not in texts


def project_info(result: Result) -> tuple[pathlib.Path, str]:
    """Get toplevel dir, project_slug, and project dir from baked cookies.

    Args:
        result: 用于生成项目的 `Result` 对象.

    Returns:
        项目路径, 项目名称, 项目目录.
    """
    assert result.exception is None
    assert result.project_path
    assert result.project_path.is_dir()

    project_path = result.project_path
    project_slug = project_path.name
    return project_path, project_slug


def test_bake_with_no_console_script(cookies: MagicMock) -> None:
    context = {"command_line_interface": "No command-line interface"}
    result = cookies.bake(extra_context=context)
    project_path, project_slug = project_info(result)
    project_files = [f.name for f in project_path.rglob("*")]
    assert "cli.py" not in project_files

    project_config_path = project_path / "pyproject.toml"
    project_config = project_config_path.read_text(encoding="utf8")
    assert "[project.scripts]" not in project_config
    assert f"{project_slug}.cli:app" not in project_config


def test_bake_with_console_script_files(cookies: MagicMock) -> None:
    context = {"command_line_interface": "Typer"}
    result = cookies.bake(extra_context=context)
    project_path, project_slug = project_info(result)
    project_files = [f.name for f in project_path.rglob("*")]
    assert "cli.py" in project_files

    project_config_path = project_path / "pyproject.toml"
    project_config = project_config_path.read_text(encoding="utf8")
    assert "[project.scripts]" in project_config
    assert f"{project_slug}.cli:app" in project_config
