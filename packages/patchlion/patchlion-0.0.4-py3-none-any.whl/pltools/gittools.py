from pycommon.exe_cmd import execute_cmd


def set_git_local_proxy(proxy: str = "http://127.0.0.1:7890") -> None:
    """设置 Git 本地代理

    Args:
        proxy (str, optional): 代理地址. Defaults to "http://127.0.0.1:7890".
    """
    try:
        execute_cmd(f"git config --global http.proxy {proxy}")
    except Exception as e:
        print(f"设置 http.proxy 时出错: {e}")
    try:
        execute_cmd(f"git config --global https.proxy {proxy}")
    except Exception as e:
        print(f"设置 https.proxy 时出错: {e}")


def unset_git_local_proxy() -> None:
    """取消设置 Git 本地代理"""
    try:
        execute_cmd("git config --global --unset http.proxy")
    except Exception as e:
        print(f"取消设置 http.proxy 时出错: {e}")
    try:
        execute_cmd("git config --global --unset https.proxy")
    except Exception as e:
        print(f"取消设置 https.proxy 时出错: {e}")

def set_git_save_pwd() -> None:
    """设置 Git 保存凭据"""
    try:
        execute_cmd("git config --global credential.helper store")
    except Exception as e:
        print(f"设置凭据存储时出错: {e}")
        
        
def list_cn_sources() -> None:
    """列出常用的国内源"""
    sources = [
        "https://mirrors.tuna.tsinghua.edu.cn/git/",
        "https://mirrors.aliyun.com/git/",
        "https://mirrors.cloud.tencent.com/git/",
        "https://mirrors.huaweicloud.com/repository/toolkit/git/",
    ]
    print("常用的国内源:")
    for source in sources:
        print(source)