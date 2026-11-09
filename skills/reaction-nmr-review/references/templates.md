# 输入、共享事实与返回模板

复制后按实际资料填写；空值用 `null` 或 `unknown`，不要生成看似完整的数据。JSON 示例仅给记录形状，不代表真实样品或已执行结果。

## 用户最短输入

```text
使用 $reaction-nmr-review
样品编号：
原料（结构/SMILES或附件及对应编号）：
反应条件与后处理（已知部分）：
预期目标（结构/SMILES；有无立体/盐形式不确定）：
谱图文件与样品对应（1H/13C/DEPT/HSQC/HMBC/COSY等）：
已知采集信息（溶剂、核种、频率、温度、参考）：
MS（可留空；若有请给模式、原始m/z和加合标注）：
公开范围：哪些结构/反应已公开？是否允许外部精确结构查询？
希望重点排查的问题：
```

## 共享谱学事实（C 初始输出；主 agent 冻结）

```json
{
  "run_id": "S001-unique", "version": 1, "status": "partial",
  "source_evidence_ids": ["SP01"],
  "blindness": {
    "context_inheritance": "none", "received_paths": [], "leaks": [],
    "limitations": ["shared filesystem; protocol isolation only"]
  },
  "acquisition": [{"spectrum_id":"SP01","nucleus":"1H","solvent":"unknown","frequency_MHz":null,"temperature_K":null}],
  "extraction": [{"spectrum_id":"SP01","method":"unknown","parameters":{},"log_path":null,"success":false}],
  "observations": [{
    "id":"OBS01", "source_id":"SP01", "location":"page/region or ppm range",
    "kind":"peak", "nucleus":"1H", "delta_ppm":null,
    "intensity":null, "integral":null, "integral_basis":null,
    "multiplicity":null, "J_Hz":[], "uncertainty":null,
    "overlap":null, "coordinates_2d_ppm":null, "verbatim_annotation":null
  }],
  "interpretations": [{"id":"INT01","observation_ids":[],"claim":"unknown","confidence_basis":"unknown","alternatives":[]}],
  "uncertain_peaks": [], "mixture_indications": [],
  "missing_experiments": [], "capability_limits": []
}
```

谱学事实还应附完整峰表/二维交叉峰表路径；保留原始工具输出及人工修改记录。页码、核种和积分依据不得省略成无来源数字。主 agent 把快照的 SHA-256 存在 manifest/coordination 中，避免把文件自身哈希写进自身。

## 结构计算输入与候选登记

```json
{"structures":[
  {"id":"T","role":"target","smiles":"CCO"},
  {"id":"B1","role":"byproduct","smiles":"CC=O"}
]}
```

上面仅为结构工具格式示例，不是推荐候选。主 agent 在 `candidates-v1.json` 中另登记每个候选：确认来源、用户图位置、目标/副产物角色、形成依据、关键假设、证据类别、计算式及工具版本、渲染文件、净电荷、盐/溶剂化组分、未指定立体、人工对照状态。尚有图像歧义的候选登记 unresolved，不送入已确认结构工具。所有角色不得从这些结构的式子声称实验分子式已确定。

## 通用角色返回

```json
{
  "role":"D", "agent_id":"actual-tool-id", "run_id":"S001-unique",
  "status":"complete|partial|failed|complete_no_candidates",
  "facts_version":1, "facts_sha256":"actual-hash-or-null",
  "candidates_version":1, "candidates_sha256":"actual-hash-or-null",
  "inputs_read":[], "artifacts":[],
  "findings":[{
    "candidate_id":"T", "support":[], "key_contradictions":[],
    "unexplained_observation_ids":[], "cannot_assess":[],
    "evidence_ids":[], "provisional_judgment":"insufficient"
  }],
  "limits":[], "questions_for_coordinator":[]
}
```

A 另返回 target_assessment、byproducts（0–3）及其结构/依据/假设。B 每项返回 evidence_class、identity_differences、doi/url、compound_number、structure_locator、spectra_locator、body_access、si_access、experimental_data、search_scope。C 使用事实模板。F 另返回 raw_evidence_reopened、issues（原证据/影响/定向修正建议）、unresolved_disagreements；不可访问原证据明确列出。

## 中文报告骨架

```text
结论：<允许的结论之一；可信范围与最大未决点，几句话>

样品与数据：编号、对应关系、原始数据/图片/峰表、采集信息、缺失项、
MS有无、独立盲读及降级范围、AILSA实际运行模式与限制。

候选结构：T与0–3个副产物分别附结构图、SMILES、结构计算式、净电荷、
盐/立体状态和工具校验；不得把计算式写成由常规NMR测定。

候选证据表：候选 | 支持（证据ID与位置）| 关键矛盾 | 未解释信号 |
无法判断 | 支持的具体层级（组分/连接/相对立体/绝对构型）。

文献：exact / close_analogue / reaction_precedent分别列；DOI/原始链接、
编号、页码/位置、实际读到的正文/SI/谱学数据与不可核实部分。

交叉核查：F回看的原始证据；发现与影响；修订原因和v1→v2；
未解决分歧及当前使用的版本/hash；共享来源不重复计作独立支持。

下一步：实验 | 要区分的假设A与B | 预期可区分观察 | 局限。
优先最少而有区分力的数据；不默认补MS能解决同分异构或绝对构型。

产物：manifest、事实快照、结构图/计算、各角色结果、文献证据、修订链接。
```
