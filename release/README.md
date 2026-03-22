# Release Pipeline

这套发布流水线面向 Windows，输出两种产物：
- 便携版目录：`release/dist/portable/TypingGame/`
- 安装包：`release/dist/installer/TypingGame-Setup-<version>.exe`

## 前置条件

1. 使用 Windows（建议与目标用户相同架构）。
2. 已创建 `.venv`（脚本优先使用 `.venv\\Scripts\\python.exe`）。
3. 如果需要安装包，安装 Inno Setup 并确保 `iscc` 可在命令行使用。

## 一键构建

在项目根目录执行：

```powershell
.\release\build.ps1 -Clean
```

可选参数：

```powershell
# 指定版本号（否则优先取最新 git tag，如 v0.1.1 -> 0.1.1）
.\release\build.ps1 -Version 0.1.2

# 只构建便携版，不生成安装包
.\release\build.ps1 -SkipInstaller
```

## 文件说明

- `release/build.ps1`：发布入口脚本（安装依赖、打包、可选生成安装器）。
- `release/TypingGame.spec`：PyInstaller 配置（GUI 模式，输出 `TypingGame.exe`）。
- `release/TypingGame.iss`：Inno Setup 脚本（生成 `setup.exe`）。

## 常见问题

- 未找到 `iscc`：脚本会自动跳过安装包步骤，只输出便携版。
- 字体差异：当前程序使用系统字体回退链，不同机器显示略有差异属正常。
- 杀软误报：打包后可增加签名流程（代码签名证书）降低误报。