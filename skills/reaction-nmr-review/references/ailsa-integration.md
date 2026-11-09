# 复用 AILSA：发现、调用和边界

本文件说明如何调用配套技能。每次先读实际安装的 `ailsa-nmr/SKILL.md` 和本次要用的子命令帮助。

## 发现与验证依赖

1. 优先查宿主技能清单和用户指定路径。若清单没有结果，检查项目及其祖先的 `.agents/skills/ailsa-nmr`、`~/.agents/skills/ailsa-nmr`、已设置的 `$CODEX_HOME/skills/ailsa-nmr`，以及宿主明确支持的 `~/.codex/skills/ailsa-nmr`。安装时使用一个可被宿主发现的位置，避免重复安装同名技能。
2. 按 `ailsa-nmr/SKILL.md` 定位 AILSA 安装。优先用工作区或用户已验证的 wrapper，或者用配套技能的 `scripts/ailsa`。解析为绝对路径，从任意数据目录调用。核实 LSD 与 outlsd 来自结构生成器，勿误用同名程序。遇到缺失依赖时见[运行环境说明](https://github.com/RainWatcher2077/reaction-nmr-review/blob/main/docs/ailsa-runtime.md)。
3. 优先用已验证 AILSA 环境的 `.venv/bin/python` 跑结构检查，也可用其他能实际导入 RDKit 的解释器。分析任务中尊重现有运行环境及数据库，不自动安装大型依赖。
4. 记录缺失项、具体路径或错误，以及仍可做的部分。缺 AILSA 可继续视觉事实整理和受限反应/文献核对。缺 RDKit 时明确公式校验或结构渲染未完成。没有真实独立子 agent 时标明降级。仅有原始 FID 或遇到不可读取格式时，请求所需的最少导出并说明实际处理范围。

## 轻量检查（保存 stdout/stderr、退出码和 JSON 状态）

以下 `AILSA` 表示已解析并核实的绝对 wrapper 路径，不是需要安装的新命令。调用时用参数数组或正确引用路径/SMILES；不要将未经信任的 SMILES 插入可执行 shell 文本。

```text
AILSA --version
AILSA --help
AILSA lsd check
AILSA database info
AILSA predict c13 --help
AILSA predict c13 CCO --format json
AILSA detect hybridisation 130.5 --format json
```

检查内容而非只看 exit 0。检测 `has_data=false` 或缺统计表时，关闭数据库来源的杂化、邻接、HHB、环统计先验，报告 **restricted CASE, statistical priors unavailable**；缺数据不是频率零、禁止键或反证。预测/排序/查重可分别可用。报告实际检测到的数据库 schema 和来源。COCONUT 的参考移位包含预测数据，NMRShiftDB 部分来自实验，引用前分别核实。

`nus check` 仅在需 NUS 重建时运行；NMRPipe/SMILE 等 NUS 重建工具缺失时，仍可读取受支持的已处理谱。完整 CASE 仅在有可靠独立分子式及足够连接证据时，先读 ailsa-nmr 的 `references/case-codex.md`，保留它的求解前独立审查与迭代门控。别把目标计算式当未知样品的独立实验证据。C 初始阶段无此分子式时先整理约束，不强行启动 CASE；额外 CASE 若需多个审核者，由主 agent 释放名额后真实调度，不能用角色内部自审代替。

## 输入与实际命令

| 输入 | 当前接口示例（每次先查相应 --help） | 输出与限制 |
|---|---|---|
| Bruker 已处理 1D | `AILSA read 1d EXP --format json`；`AILSA pick 1d EXP --format json` | EXP需acqus及pdata/1；read给采集/轴信息，pick给ppm/intensity/SNR。强度不是积分，不自动给多重性或J |
| Bruker 已处理2D | `read 2d`、`pick 2d`、`pick hsqc`、`pick hmbc`（后接EXP和format） | 另需acqu2s等。输出交叉峰位置/强度；须核对维度、类型、相位、噪声和长程归属。不是通用FID自动处理 |
| 支持的JCAMP-DX | `AILSA jcamp INPUT_DIR --out NEW_DIR --format json`，或显式列.dx文件 | 不能混目录与文件。1D需观察核种/轴信息；2D支持相应NTUPLES。HSQC/HMBC/COSY可提峰，未识别实验可能只读不提；读取失败和QC隔离必须查看 |
| 明确的13C移位表 | `AILSA analyze grouping '44.90,45.03,129.38' --format json` | 可选实际DEPT multiplicities；分组不是归属证明。可和候选预测比较 |
| 候选SMILES | `AILSA predict c13 'CCO' --format json` | 仅13C；保留atom_index、shift、confidence、fallback半径、缺失原子与覆盖率。不是1H/J模拟，也不是身份概率。HOSE不用AddHs |
| Bruker+可靠公式查重 | `AILSA dereplicate c13 --help`后按当前接口 | 当前CLI收Bruker路径和公式，**无 --shifts**。显式列表若确需查重须读当前Python DereplicationService.dereplicate_from_shifts API和数据库加载代码，不虚构CLI参数 |
| 图片/PDF或用户峰表 | 可视查看/带页码区域的人工转录，后续仅调用适用接口 | AILSA没有通用图片/PDF原谱输入；不能声称raw-data CASE已运行，不清晰字段留unknown |

**JCAMP 特别边界**：若所用版本的 `jcamp --help` 明示无 DEPT 时，`quaternary_exclusion` QC 使用历史未解样品的五个假设季碳，`classification_source=override`，且没有关闭 flag，应将它作为历史默认值隔离。保留原始 QC 并隔离该项；PASS不能证实本样品，FAIL不能证明坏谱。回看真实 DEPT/原谱或独立提峰，不篡改 QC、不伪造 DEPT、不改引擎绕过。始终显式指定新 `--out`，避免默认写入输入目录；QC失败的 quarantine 不可说成已生成可消费结果。

## 确定性结构处理

候选需确认后才提交，JSON形状见 templates.md。用已检查可 import RDKit 的 Python 调用：

```text
<RDKit-Python> <本技能目录>/scripts/structure_check.py --input <structures.json> --out <不存在的新目录>
```

输出 `results.json`、每个结构SVG/PNG。恰1目标+0–3副产物；检查输入/逐项 status 与退出码。包括输入hash、RDKit版本、原SMILES/规范异构SMILES、formula、net_charge、fragment_formulas、potential/unspecified_stereochemistry和结构计算精确质量。盐/互变异构/电荷/立体不自动标准化；有潜在立体但未指定要保留。图像仅从SMILES渲染，必须人工对照用户原图，工具无法证明图像转录正确；不使用生成式图片画分子。

`exact_mass_da_calculated` 是结构描述符，**不是已选离子模式的理论 m/z**，也不是 MS 观测或实验证实分子式。带电结构和多电荷离子的质量要按实际离子组成/电子质量/加合形式重新算。失败记录不视为校验通过；结果目录拒绝覆盖，重试使用新目录。
