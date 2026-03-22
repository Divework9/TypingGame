# TypingGame

## 主要功能
- 双模式打字玩法：支持英文单词模式与中文拼音模式。
- 核心游戏循环：下落词生成、输入匹配、消除得分、漏词扣命、等级提升、连击统计。
- 菜单与状态流转：菜单 / 游戏中 / 结束页完整流程。
- 可视化键盘反馈：按等级切换键盘展示层级（letters / letters_numbers / full），并支持按键闪烁。
- 配置模块化：速度、词库、键盘配置与全局常量拆分到 `conf/` 目录，降低主文件耦合。
- 缩放自适应：通过 `TYPING_GAME_SCALE_RATIO` 统一控制界面比例，支持边界缩放（50% / 200%）验证。
- 回归测试体系：包含运行期 bug 回归测试与布局边界测试，覆盖光标、输入框、菜单、键盘、顶部信息栏与红心 UI。

## 运行方式
- 创建并激活虚拟环境后安装依赖（主要为 `pygame-ce`）。
- 启动游戏：`python typing_game.py`
- 运行测试：`python -m unittest discover test`

## 目录树与当前程序结构

```text
TypingGame/  项目根目录，包含主程序与测试。
├─ typing_game.py  游戏主逻辑与渲染入口。
├─ test_typing_game.py  早期基础测试入口文件。
├─ conf/  配置目录，集中管理参数与词库。
│  ├─ game_constants.py  全局常量与缩放配置。
│  ├─ keyboard.py  键盘布局与显示配置。
│  ├─ speed.py  速度与生成节奏参数。
│  └─ word_bank.py  英文词库与拼音词库。
└─ test/  自动化测试目录。
  ├─ common.py  测试基类与公共初始化。
  ├─ core/  核心功能与回归测试集合。
  │  ├─ test_core_layout_bounds.py  布局与缩放边界测试。
  │  └─ test_runtime_bug_regressions.py  运行期问题回归测试。
  ├─ version/  版本一致性相关测试。
  ├─ version_specs/  历史版本功能说明文档。
  └─ visual/  轻量可视化检查脚本目录。
    └─ cursor_visual_snapshot.py  光标对齐可视检查脚本。
```

### 当前程序主要模块功能
- `typing_game.py`：主程序入口与核心玩法（状态流转、渲染、输入匹配、计分、升级、粒子特效、键盘反馈）。
- `conf/game_constants.py`：全局常量与缩放策略（`TYPING_GAME_SCALE_RATIO`），统一管理 UI 尺寸和行为阈值。
- `conf/keyboard.py`：键盘布局与分层显示配置（letters / letters_numbers / full）及对应视觉参数。
- `conf/speed.py`：下落速度、生成间隔等难度节奏参数。
- `conf/word_bank.py`：英文词库与拼音词库数据来源。
- `test/core/test_runtime_bug_regressions.py`：运行中发现的真实 bug 回归测试。
- `test/core/test_core_layout_bounds.py`：缩放与布局边界测试（含 50% / 200% 边界）。
- `test/visual/cursor_visual_snapshot.py`：光标与文本对齐的轻量可视检查脚本（默认用于本地比对）。

## 版本更新（倒序）

### v0.1.1
- 修复并增强缩放适配：
  - 红心绘制改为稳定几何结构（上双圆 + 下三角），缩放下形状更一致。
  - 输入光标改为与输入文字底部对齐，解决缩放后光标偏高/偏低问题。
  - 顶部信息栏元素（分数/Lv/Combo/模式提示/红心）在边界缩放下的重叠风险修正。
- 新增测试：
  - `test/core/test_runtime_bug_regressions.py`：补充运行期回归用例（重复词清除、键帽裁切、红心几何等）。
  - `test/core/test_core_layout_bounds.py`：补充 50% / 200% 缩放边界测试与光标对齐测试。
- 测试现状：全量 `74` 项通过。

### v0.1build
- 提取非颜色类 magic number 到 `conf/game_constants.py` 并加注释。
- 统一全局常量入口，减少主逻辑中的硬编码。

### v0.1
- 新增底部键盘可视化与按键闪烁反馈。
- 配置模块化拆分：`conf/keyboard.py`、`conf/speed.py`、`conf/word_bank.py`。
- 测试目录拆分为 `test/core` 与 `test/version`，补齐词库覆盖与版本测试规范。

### v0.0
- 建立基础打字消除玩法。
- 支持英文/拼音双模式。
- 完成分数、生命值、等级、连击等核心机制。
- 完成基础菜单、游戏中与结束状态流程。
