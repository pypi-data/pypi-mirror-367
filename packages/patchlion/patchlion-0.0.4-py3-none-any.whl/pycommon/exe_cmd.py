import subprocess
import sys


def execute_cmd(cmd: str, cwd: str = None):
    """执行命令

    Args:
        cmd (str): 要执行的命令
        cwd (str, optional): 命令执行的工作目录. Defaults to None.

    Raises:
        Exception: 命令执行失败
    """

    print(f"执行命令: {cmd}, 工作目录: {cwd}")

    pro = subprocess.run(
        cmd,
        shell=True,
        encoding=("gb2312" if sys.platform == "win32" else "utf-8"),
        text=True,
        check=True,
        cwd=cwd,
    )
    if pro.returncode != 0:
        print(f"命令执行失败: {cmd}")
        if pro.stderr:
            raise Exception(f"错误信息: {pro.stderr.strip()}")
