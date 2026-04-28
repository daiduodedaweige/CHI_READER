---
name: skill_protocol_read_pitcure
description: "从协议文档拆分页 PDF 中识别并提取 figure，自动转换为 Mermaid 代码，适用于拓扑图、事务流图、状态图等矢量协议图。"
---

# Skill: Protocol Read Picture

## 目标

将协议文档中的拆分页 PDF figure 自动提取为 Mermaid 代码，并批量写入输出目录，便于后续检索、修改、渲染和人工精修。

## 适用场景

- 输入目录中包含按章节拆分的 PDF。
- PDF 中的图是矢量图，文字和线段可以被程序提取。
- 需要把协议拓扑图、事务时序图、链路状态图等转换为 Mermaid。
- 图可能不在 PDF 第 1 页，而在该 PDF 的后续页面。

## 输入与输出

输入：

- 源 PDF 目录：`out/`
- 批处理脚本：`extract_figures_to_mermaid.py`

输出：

- Mermaid 输出目录：`out_figure/`
- 文件命名规则：`<pdf stem>__<figure id>.mmd`
- 例如：`B2.3 Transaction structure__B2.11.mmd`

## 工作流

1. 遍历 `out/` 下所有 PDF，而不是只处理单个样本文件。
2. 对每个 PDF 的所有页面逐页扫描，不能只看第 1 页。
3. 在页面文本中查找 `Figure X.Y:` 形式的图注，定位 figure 所在区域。
4. 读取该区域内的文本块、线段、填充标记等矢量对象。
5. 判断图类型：
   - 若检测到多条竖向泳道，优先生成 `sequenceDiagram`
   - 否则生成 `flowchart LR`
6. 将识别到的节点、参与者、消息、连线转换成 Mermaid 语法。
7. 将每个实际 figure 单独写入 `out_figure/`。
8. 对代表性输出做 Mermaid 语法校验和渲染预览。

## 关键识别规则

### 1. 图注定位

- 通过 `Figure <id>: <title>` 匹配真实图注。
- 图区域取图注上方的矢量绘图范围。
- 没有图注或没有绘图对象的页面直接跳过。

### 2. 多页 PDF 支持

- 拆分后的 PDF 可能包含多页正文。
- 图经常出现在第 2 页或更后面的页面。
- 因此必须遍历整份 PDF 的所有页。

### 3. 时序图识别

- 通过较长的竖直线段识别 lifeline。
- 通过顶部文本识别 participant。
- 通过水平消息线和端点附近的箭头标记判断消息方向。
- 输出为 `sequenceDiagram`。

### 4. 结构图和状态图识别

- 从文本块构造节点。
- 从线段构造连边。
- 根据端点是否存在箭头标记输出 `-->` 或 `---`。
- 输出为 `flowchart LR`。

## 已验证命令

在仓库根目录执行：

```bash
/bin/python3 extract_figures_to_mermaid.py --output-dir out_figure
```

## 已验证结果

- 当前仓库中，脚本可以对 `out/` 下的拆分页 PDF 进行批量处理。
- 已验证结构图、事务流图、复杂状态图都能生成可渲染的 Mermaid。
- 当前输出目录 `out_figure/` 已生成 115 个 `.mmd` 文件。

## 校验方法

建议至少做两类校验：

1. 语法校验
   - 用 Mermaid validator 检查 `flowchart` 和 `sequenceDiagram` 语法是否合法。

2. 渲染校验
   - 打开代表性文件预览，确认 Mermaid 能实际渲染。
   - 至少抽检一份结构图、一份事务时序图、一份复杂状态图。

## 局限与风险

- 这是基于 PDF 矢量对象的自动近似还原，不是严格语义级重建。
- 复杂状态图可能出现节点拆分过细、边吸附不准、标签挂接偏差。
- 多分支事务图虽然可以转成 `sequenceDiagram`，但语义顺序仍建议人工复核。
- 如果 PDF 是位图扫描件而不是矢量图，这条链路效果会明显下降。

## 推荐使用准则

- 先全量批处理，再人工精修关键 figure。
- 对需要高保真的图，优先检查：
  - participant 顺序是否正确
  - message 方向是否正确
  - 复杂状态图中的关键边是否缺失或误连
- 如果后续要继续扩展，可优先增强：
  - 节点聚类
  - 箭头识别
  - 多分支/分组语义恢复
  - 图例区域过滤

## 仓库内对应实现

- 脚本：`extract_figures_to_mermaid.py`
- 输入目录：`out/`
- 输出目录：`out_figure/`

## 一句话总结

这是一个“面向协议文档矢量 PDF 的 figure 到 Mermaid 批量提取 skill”，核心点是：按页扫描、按图注定位、按图类型选择 `sequenceDiagram` 或 `flowchart`、输出后再做语法与渲染抽检。