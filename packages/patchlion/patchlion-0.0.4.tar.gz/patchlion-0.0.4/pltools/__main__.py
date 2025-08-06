#!/usr/bin/env python3
"""
PLTools 命令行入口点
"""

import sys
import argparse
from . import gittools
from . import __version__


def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(
        prog="pltools", description="PLTools - Python 开发工具集合"
    )

    parser.add_argument("--version", action="version", version=f"PLTools {__version__}")
    parser.add_argument(
        "--set-git-local-proxy", action="store_true", help="设置 Git 本地代理"
    )
    parser.add_argument(
        "--unset-git-local-proxy", action="store_true", help="取消设置 Git 本地代理"
    )
    parser.add_argument(
        "--set-git-save-pwd", action="store_true", help="设置 Git 保存凭据"
    )
    parser.add_argument(
        "--list-cn-sources", action="store_true", help="列出常用的国内源"
    )

    args = parser.parse_args()

    if args.set_git_local_proxy:
        gittools.set_git_local_proxy()
    elif args.unset_git_local_proxy:
        gittools.unset_git_local_proxy()
    elif args.set_git_save_pwd:
        gittools.set_git_save_pwd()
    elif args.list_cn_sources:
        gittools.list_cn_sources()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
