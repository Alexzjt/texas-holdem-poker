# Texas Hold'em Poker Skill (德州扑克博弈技能)

A custom Texas Hold'em poker game and simulation skill built on the [Agent Skills specification](https://agentskills.io). It allows you to play a mathematically accurate game of Texas Hold'em with human-like AI opponents in any AI assistant terminal supporting Agent Skills (such as Claude Code, Cursor, etc.). 

这是一个基于 [Agent Skills 规范](https://agentskills.io) 构建的自定义德州扑克（Texas Hold'em）对局与博弈模拟技能。它允许您在支持 Agent Skills 的 AI 终端（如 Claude Code 或 Cursor 等）中随时开启一局高数学精度、充满人性化对手的德州扑克对局。

---

## Table of Contents / 目录
- [English Version](#english-version)
  - [🌟 Features](#-features)
  - [📁 Project Structure](#-project-structure)
  - [🚀 Installation & Usage](#-installation--usage)
  - [🧪 Testing](#-testing)
  - [⚠️ Disclaimer](#-disclaimer)
- [中文版](#中文版)
  - [🌟 核心能力](#-核心能力)
  - [📁 目录结构](#-目录结构)
  - [🚀 安装与使用](#-安装与使用)
  - [🧪 运行测试](#-运行测试)
  - [⚠️ 免责声明](#-免责声明)

---

## English Version

### 🌟 Features
*   **Dynamic Table Size (5-8 Players)**: Supports varying table sizes from 5 to 8 players (including the user and 4 to 7 AI opponents). The number and names of opponents are randomized and dynamically generated for each game.
*   **Adaptive AI Personas (Internal thought only)**: Opponents are assigned strategies (loose-aggressive, tight-aggressive, tight-passive, or loose-passive) and personalities (polite, analytical, talkative, cheerful, quiet) behind the scenes, adapting and shifting gears based on game context.
*   **Side Pot & Math Accuracy**: A robust 7-card evaluator determines hand rankings (from High Card to Straight Flush) and handles split pots and complex side-pot calculations for multiple all-in situations.
*   **Strict Game Rules Enforcement**:
    *   *Confidentiality*: Opponents' hole cards are strictly confidential and never leaked before the showdown.
    *   *Silence during Play*: AI players remain silent with no spoken dialogue during active betting rounds to avoid hints or spoilers. Dialogue is only triggered after the hand is finished (Showdown).
*   **State Persistence**: Game states are auto-saved to `game_state.json`, allowing games to be paused and resumed seamlessly.

### 📁 Project Structure
```text
.
├── SKILL.md             # Main skill instructions defining AI simulation and rendering flows
├── scripts/             # Python tools and rules engine
│   ├── poker_engine.py  # Core rules engine, card evaluator, pot manager, and CLI interface
│   └── test_poker.py    # Test suite verifying hand evaluations, split pots, and side pots
├── game_state.json      # Active hand configuration and state storage (auto-saved)
└── README.md            # Project description document
```

### 🚀 Installation & Usage

#### 1. Install Skill
This skill conforms to the Agent Skills specification. You can install it into your AI Agent workspace using the `skills` CLI:
```bash
npx skills add Alexzjt/texas-holdem-poker
```
This automatically pulls `SKILL.md` and the `scripts/` directory into your Agent's config folder.

#### 2. Requirements
The backend engine is built with Python 3 standard libraries and has **no third-party dependencies**. Simply ensure Python 3 is installed.

#### 3. Playing with AI Agent
In any AI assistant terminal supporting Agent Skills, simply start the game using natural language:
> *"Play poker with 6 players."*

The AI Assistant will automatically:
1. Select random AI opponent names (e.g., Alex, Jamie, Taylor) and assign them underlying personas/strategies.
2. Initialize the game state via `poker_engine.py`.
3. Simulate AI actions and update state.
4. Render the table UI with Unicode card representations (`[A♠]`, `[10♥]`) and prompt you for input (Check / Call / Fold / Raise).

#### 4. Running CLI Engine
You can also interact directly with the CLI engine in your terminal:
*   **Initialize a game**:
    ```bash
    python3 scripts/poker_engine.py init --players "You,Alex,Jamie,Taylor,Morgan"
    ```
*   **Submit a player action**:
    ```bash
    # Alex Calls
    python3 scripts/poker_engine.py action --player "Alex" --type call
    # Raise to 50
    python3 scripts/poker_engine.py action --player "You" --type raise --amount 50
    # Taylor Folds
    python3 scripts/poker_engine.py action --player "Taylor" --type fold
    ```
*   **Start next hand**:
    ```bash
    python3 scripts/poker_engine.py next_hand
    ```
*   **Print current JSON state**:
    ```bash
    python3 scripts/poker_engine.py show
    ```

### 🧪 Testing
Run the unit tests to verify the rules engine and pot calculations:
```bash
PYTHONPATH=scripts python3 scripts/test_poker.py
```

### ⚠️ Disclaimer
*   **For Simulation Only**: This skill is intended solely for simulation and strategic practice. No real money or currency is supported or involved. **Strictly prohibited for any gambling activities.**
*   **No Investment Representation**: AI strategies do not represent financial or investment advice.

---

## 中文版

### 🌟 核心能力
*   **动态桌规模与随机玩家 (5-8人)**：支持 5 到 8 人（包括玩家 "You" 以及 4 到 7 名 AI 玩家）的弹性桌规模。每次开局，AI 对手的数量、名字均会从名字池中随机动态生成。
*   **动态策略与性格模拟 (仅限后台思考)**：AI 对手会在后台分配游戏策略（如：松激进、紧激进、紧被动、松被动等）和性格（礼貌、理性、话唠、友好、安静等），并在对局中根据筹码量、位置与局势动态切换打法（"Change Gears"）。
*   **高精度边池与规则判定**：底层采用 Python 7张牌评估算法，自动判断手牌大小级别（从高牌到同花顺）以及复杂的平分底池（Split Pot）和多重 All-in 场景下的边池（Side Pot）计算。
*   **严格的游戏规范机制**：
    *   *底牌保密*：其他玩家的底牌在摊牌（Showdown）前对您严格保密，绝无信息泄露。
    *   *静默对局*：在手牌进行中（Preflop 到 River），AI 对手均保持绝对静默，无对话，防止暗示与剧透；仅在摊牌或手牌结束后才触发趣味互动。
*   **断点存盘与状态持久化**：自动保存游戏状态于 `game_state.json`，支持随时中断、退出并完美恢复对局。

### 📁 目录结构
```text
.
├── SKILL.md             # 技能主指令文件，定义了 AI 模拟对手、发牌与渲染 UI 的核心执行流程
├── scripts/             # 自动化工具脚本
│   ├── poker_engine.py  # 德州扑克核心逻辑引擎 (负责发牌、底池/边池计算、状态流转、筹码流转及 CLI)
│   └── test_poker.py    # 规则与引擎逻辑单元测试 (覆盖边池、多重 All-in、加注判定等)
├── game_state.json      # 实时游戏状态存档文件 (自动保存/读取)
└── README.md            # 项目说明文档 (本文件)
```

### 🚀 安装与使用

#### 1. 快速安装技能
本技能采用通用的 Agent Skills 规范进行包管理。您可以通过 `npx skills` 一键安装此技能到您的 AI Agent 工作空间：
```bash
npx skills add Alexzjt/texas-holdem-poker
```
该命令会自动将本 GitHub 仓库中的 `SKILL.md` 描述文件和 `scripts/` 目录拉取到您 AI Agent 的技能配置目录中，使其能够立即识别和执行相关的扑克博弈流程。

#### 2. 本地环境准备
本技能的规则计算引擎基于 Python 3 标准库构建，**无需安装任何第三方库**。您只需确保本地安装了 Python 3 环境即可。

#### 3. 日常交互使用
当您在与支持 Agent Skills 的 AI 终端（如 Claude Code 等）对话时，您只需使用自然语言发起对局：
> *“我想玩一局德州扑克，7个人玩。”*

AI 助手将自动加载本 Skill 并完成以下动作：
1. 从名字池中随机选择 AI 对手并在后台为他们分配好隐秘的性格和策略。
2. 运行 `poker_engine.py` 初始化游戏。
3. 按照发牌顺序，在后台依次模拟 AI 玩家的行动，并调用 `action` 写入状态。
4. 轮到您的行动时，使用精美的 Unicode 卡牌字符（`[A♠]`, `[10♥]`）渲染当前桌面状态，并等待您的输入（Check / Call / Fold / Raise）。

#### 4. 命令行工具运行
您也可以脱离 AI 终端，直接在终端使用命令行操作底层扑克引擎：
*   **初始化游戏**：
    ```bash
    python3 scripts/poker_engine.py init --players "You,Alex,Jamie,Taylor,Morgan"
    ```
*   **玩家行动**：
    ```bash
    # Alex 跟注 (Call)
    python3 scripts/poker_engine.py action --player "Alex" --type call
    # 玩家加注到 50 (Raise to 50)
    python3 scripts/poker_engine.py action --player "You" --type raise --amount 50
    # Taylor 弃牌 (Fold)
    python3 scripts/poker_engine.py action --player "Taylor" --type fold
    ```
*   **开始下一手牌**：
    ```bash
    python3 scripts/poker_engine.py next_hand
    ```
*   **打印当前游戏 JSON 状态**：
    ```bash
    python3 scripts/poker_engine.py show
    ```

### 🧪 运行测试
为确保扑克规则、牌力计算及分池算法的 100% 准确性，您可以在主目录下运行单元测试：
```bash
PYTHONPATH=scripts python3 scripts/test_poker.py
```

### ⚠️ 免责声明
*   **仅供娱乐与博弈模拟**：本 Skill 及底层引擎仅用于德州扑克的技术交流与博弈模拟训练，不提供任何真实的资金结算功能，**严禁用于任何形式的真实赌博或非法活动**。
*   **策略不代表投资建议**：AI 对手基于预设策略行动，其博弈过程与现实金融市场、投资决策无关，请理性对待模拟结果。
