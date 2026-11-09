# Reaction NMR Review for Codex

用反应信息和实验 NMR 核对目标产物，提出最多三个值得检验的副产物。流程将反应推理、文献检索与盲读谱分开，冻结同一份谱学事实供候选评估，并安排独立复核回看原谱。报告分别列出支持证据、矛盾、未解释信号和仍需补充的实验。没有足够证据时，可以保留零个候选。

| 技能 | 用途 |
| --- | --- |
| [`reaction-nmr-review`](skills/reaction-nmr-review/SKILL.md) | 主工作流，负责资料对应、独立审查、候选核对及中文报告 |
| [`ailsa-nmr`](skills/ailsa-nmr/SKILL.md) | **必装配套技能**，指导 Codex 使用本地 AILSA 读取受支持的谱图、预测 ¹³C 化学位移及开展有条件的 CASE |

两个技能随仓库一起提供。AILSA 工具、原生 LSD、参考数据库和 RDKit 属于本地运行环境，另见[运行环境安装说明](docs/ailsa-runtime.md)。

## 安装

### 交给 Agent 安装

把下面整段发给 Codex 或有终端权限的 Agent。

> 请从 https://github.com/RainWatcher2077/reaction-nmr-review 安装 NMR 核对技能。克隆仓库并按根目录的 AGENTS.md 执行双技能安装脚本。确认 `reaction-nmr-review` 和必需的 `ailsa-nmr` 都已安装在当前宿主可发现的位置。再按运行环境说明复用或配置本地 AILSA，分别报告两个技能的安装路径、运行环境的实际检查结果及缺项。遇到不同版本的同名技能时，保留已有文件并报告冲突。

### 手动安装

在 macOS 或 Linux 的终端运行以下命令。需要 Git 和 Bash。

```bash
git clone https://github.com/RainWatcher2077/reaction-nmr-review.git
cd reaction-nmr-review
bash scripts/install-skills.sh
```

默认写入 `~/.agents/skills`。若已设置 `CODEX_HOME`，默认写入 `$CODEX_HOME/skills`。可传入一个由宿主实际发现的目录，例如 `bash scripts/install-skills.sh "$HOME/.agents/skills"`。脚本复用内容相同的副本，遇到不同版本会在安装前停止。请在一个位置安装两个技能。

如果仅能使用技能导入界面，请分别导入 `skills/ailsa-nmr` 和 `skills/reaction-nmr-review`，确认两个技能都已注册。技能列表未更新时，开启新的 Codex 会话再查看。[Codex Skills 文档](https://learn.chatgpt.com/docs/build-skills)

随后按[运行环境安装说明](docs/ailsa-runtime.md)验证 CLI、LSD、参考数据库、¹³C 预测和 RDKit。没有完整运行环境时，仍可用已有谱图开展受限的人工读谱和证据核对，并在报告中说明缺项。

## 使用

在 Codex 会话中调用 `$reaction-nmr-review`，提供原料、已知反应条件、预期结构，以及谱图与样品的对应关系。质谱如有可一并提供。可直接使用下面的指令。

> 使用 `$reaction-nmr-review` 核对附件中的目标产物。请分别检查两份样品，保留原始谱图，列出支持证据、关键矛盾和最能区分候选的补充实验。

AILSA 支持已处理 Bruker 数据和部分 JCAMP-DX。仅有原始 FID/ser 时需先处理，图片或 PDF 可供人工判读。完整 CASE 需要独立的分子式证据与足够的谱学连接约束。候选排序提供比较依据，结构鉴定还需与实测证据核对。

## 上游与引用

`ailsa-nmr` 是配套的 Codex 操作技能，调用 Christoph Steinbeck 的 [AILSA](https://github.com/steinbeck/ailsa) 和 Jean-Marc Nuzillard 的 [LSD](https://nuzillard.github.io/LSD/)。用于研究时，请遵循 [AILSA 的引用说明](https://github.com/steinbeck/ailsa/blob/0557c37097d5ed95674e81e80b9a2cdfb3e30a63/README.md#license--citation)，同时引用 LSD。参考数据库由上游发布。[Figshare 参考数据库](https://doi.org/10.6084/m9.figshare.31073554)
