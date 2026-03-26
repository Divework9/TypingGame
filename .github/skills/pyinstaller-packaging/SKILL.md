---
name: pyinstaller-packaging
description: PyInstaller + Inno Setup 打包发布检查清单。
---

# PyInstaller 打包发布检查清单

## 0. 安全与环境预检（非常重要！）

在执行打包命令前或获取代码变更前，**务必确保打包的输出目录（如 `build/`、`dist/`）已被加入 `.gitignore`**。
**拦截机制**：如果你在代码存在大量生成后的二进制产物（`.exe`, `.dll`, 图片等）时错误调用了 `get_changed_files` 或完整的变更差异获取工具，大段二进制乱码会致使 AI 侧的多模态 API payload 校验出现致死性错误（400 invalid_request_body），导致对话进程强制中断报错！

- **操作指南**：如果需要在打包后执行 Git 操作，先执行 `git status --short` 和 `git diff --name-only` 确认不会加载二进制代码片段。

## When to Use

- 使用 PyInstaller 将 Python 项目打包为 Windows exe
- 构建便携版或 Inno Setup 安装包
- 排查打包后 exe 无法运行的问题

## .spec 文件编写注意事项

### 1. 不要在 .spec 文件中使用 `__file__`

PyInstaller 通过 `exec()` 执行 `.spec` 文件，上下文中**没有 `__file__`**。

```python
# 错误
project_root = os.path.dirname(os.path.abspath(__file__))

# 正确
project_root = os.path.abspath(os.getcwd())
```

### 2. 使用绝对路径引用源文件

`.spec` 文件执行时的工作目录可能不是项目根目录（例如从 `release/` 子目录运行），因此所有路径必须是绝对路径。

```python
# 错误
a = Analysis(['typing_game.py'], ...)

# 正确
a = Analysis([os.path.join(project_root, 'typing_game.py')], ...)
```

### 3. `--specpath` 不能和 `.spec` 文件一起使用

PyInstaller 在命令行传入 `.spec` 文件时，`--specpath` 参数会报错。只在从 `.py` 生成 `.spec` 时才需要 `--specpath`。

## DLL 依赖检查

### 4. 手动添加 `python3.dll`（关键）

PyInstaller 会自动打包 `pythonXYZ.dll`（如 `python314.dll`），但**不会自动打包 `python3.dll`**（Python 稳定 ABI 垫片）。缺少此文件会导致：

> **"failed to load python dll"**

修复方法 — 在 `.spec` 中手动加入：

```python
import sys
python_base = sys.base_prefix
extra_binaries = [(os.path.join(python_base, 'python3.dll'), '.')]

exe = EXE(
    ...
    extra_binaries=extra_binaries,
    ...
)
```

### 5. 设置 `contents_directory='.'`

PyInstaller 6.x 默认将运行时文件放到 `_internal/` 子目录，可能导致 DLL 加载路径错误。设置此项让所有文件与 exe 同级：

```python
exe = EXE(
    ...
    contents_directory='.',
    ...
)
```

## 构建输出目录

### 6. 区分 build 目录和 dist 目录

| 目录 | 用途 | 能否分发 |
|------|------|---------|
| `release/build/` | 临时构建中间产物 | **不能** |
| `release/dist/portable/` | 最终便携版输出 | **可以** |
| `release/dist/installer/` | Inno Setup 安装包 | **可以** |

**常见错误**：从 `build/` 目录拿 exe 测试，该目录内容不完整，必然运行失败。

## 打包前检查清单

- [ ] `.spec` 中没有使用 `__file__`，改用 `os.getcwd()`
- [ ] 所有源文件路径为绝对路径（`os.path.join(project_root, ...)`）
- [ ] `python3.dll` 已加入 `extra_binaries`
- [ ] `contents_directory='.'` 已设置（PyInstaller 6.x）
- [ ] 构建命令中没有 `--specpath`（使用 `.spec` 文件时）
- [ ] 从 `dist/` 目录（而非 `build/`）取最终产物
- [ ] `console=False` 已设置（GUI 应用不显示黑窗口）

## 打包后验证清单

- [ ] `dist/` 目录下存在 `python3.dll`
- [ ] `dist/` 目录下存在 `pythonXYZ.dll`（如 `python314.dll`）
- [ ] `dist/` 目录下存在 `VCRUNTIME140.dll` 和 `VCRUNTIME140_1.dll`
- [ ] exe 文件大小合理（不应只有几 KB）
- [ ] 在**没有 Python 环境**的机器上测试运行
