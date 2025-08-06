# PyCommon

一个Python通用工具库，提供常用的实用函数。

## 功能模块

### exe_cmd.py - 命令执行工具

提供跨平台的命令执行功能，支持自动编码处理。

#### 主要功能

- `execute_cmd(cmd, cwd=None)`: 执行系统命令
  - 自动处理Windows和Linux下的编码差异
  - 支持指定工作目录
  - 提供详细的错误信息
  - 命令执行失败时抛出异常

## 安装

将此库克隆到本地：

```bash
git clone <repository-url>
cd pycommon
```

## 使用示例

### 命令执行

```python
from exe_cmd import execute_cmd

# 执行简单命令
execute_cmd("ls -la")  # Linux/Mac
execute_cmd("dir")     # Windows

# 在指定目录执行命令
execute_cmd("git status", cwd="/path/to/git/repo")

# 处理异常
try:
    execute_cmd("some-invalid-command")
except Exception as e:
    print(f"命令执行失败: {e}")
```

## 特性

- **跨平台兼容**: 自动检测操作系统并使用合适的编码
- **错误处理**: 完善的错误信息反馈
- **灵活配置**: 支持自定义工作目录
- **详细日志**: 显示执行的命令和工作目录信息

## 系统要求

- Python 3.6+
- 支持Windows、Linux、macOS

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 许可证

[在此添加许可证信息]

## 更新日志

### v1.0.0
- 初始版本
- 添加`execute_cmd`函数
- 支持跨平台命令执行
