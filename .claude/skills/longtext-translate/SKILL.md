---
name: longtext-translate
description: 以三种模式在不同语言之间翻译文章和文档：quick（直接翻译）、normal（先分析再翻译）和 refined（分析、翻译、审校、润色的完整流程）。支持通过 EXTEND.md 配置自定义术语表并保持术语一致。用户要求“translate”、“翻译”、“精翻”、“translate article”、“translate to Chinese/English”、“改成中文”、“改成英文”、“convert to Chinese”、“localize”、“本地化”，或有任何文档翻译需求时使用。也会在“refined translation”、“精细翻译”、“proofread translation”、“快速翻译”、“快翻”、“这篇文章翻译一下”，或用户提供 URL/文件且带有翻译意图时触发。
---

# 翻译器

三模式翻译技能：**quick** 用于直接翻译，**normal** 用于基于分析的翻译，**refined** 用于包含审校和润色的完整出版级工作流。

## 用户输入工具

当此技能需要向用户提问时，按照以下工具选择规则执行（按优先级排序）：

1. **优先使用当前 agent 运行时提供的内置用户输入工具**，例如 `AskUserQuestion`、`request_user_input`、`clarify`、`ask_user`，或任何等价工具。
2. **回退方案**：如果没有这类工具，输出编号纯文本消息，并要求用户针对每个问题回复所选编号/答案。
3. **批量提问**：如果工具支持一次调用提出多个问题，则将所有适用问题合并到一次调用中；如果只支持单问题，则按优先级逐个提问。

下文中具体的 `AskUserQuestion` 引用只是示例；在其他运行时请替换为本地等价工具。

## 脚本目录

脚本位于 `scripts/` 子目录。`{baseDir}` = 此 SKILL.md 所在目录路径。解析 `${BUN_X}` 运行时：如果已安装 `bun` → `bun`；如果可用 `npx` → `npx -y bun`；否则建议安装 bun。将 `{baseDir}` 和 `${BUN_X}` 替换为实际值。

| 脚本 | 用途 |
|--------|---------|
| `scripts/main.ts` | CLI 入口。默认行为是将 markdown 拆分为分块；也支持显式的 `chunk` 子命令 |
| `scripts/chunk.ts` | `main.ts` 使用的 Markdown 分块实现，并保持可直接调用的兼容性 |

## 偏好设置（EXTEND.md）

按优先级检查 EXTEND.md——找到的第一个生效：

| 优先级 | 路径 | 作用域 |
|----------|------|-------|
| 1 | `.longtext-translate/longtext-translate/EXTEND.md` | 项目 |
| 2 | `${XDG_CONFIG_HOME:-$HOME/.config}/longtext-translate/longtext-translate/EXTEND.md` | XDG |
| 3 | `$HOME/.longtext-translate/longtext-translate/EXTEND.md` | 用户主目录 |

| 结果 | 动作 |
|--------|--------|
| 找到 | 读取、解析并应用。会话中首次使用时，简要提醒：“正在使用来自 [path] 的偏好设置。你可以编辑 EXTEND.md 来自定义术语表、受众等。” |
| 未找到 | **必须**运行首次设置（见下文）——不要静默使用默认值 |

**EXTEND.md 支持**：默认目标语言、默认模式、目标受众、自定义术语表（内联或文件路径）、翻译风格、分块设置。

Schema：[references/config/extend-schema.md](references/config/extend-schema.md)。

### 首次设置（阻塞）

**关键**：当找不到 EXTEND.md 时，**必须**在任何翻译之前运行首次设置。这是一个**阻塞**操作。

完整参考：[references/config/first-time-setup.md](references/config/first-time-setup.md)

使用 `AskUserQuestion` 在一次调用中提出所有问题（目标语言、模式、受众、风格、保存位置）。用户回答后，在所选位置创建 EXTEND.md，确认“偏好设置已保存到 [path]”，然后继续。

## 默认值

所有可配置值集中列出。EXTEND.md 会覆盖这些值；CLI 标志会覆盖 EXTEND.md。

| 设置 | 默认值 | EXTEND.md 键 | CLI 标志 | 说明 |
|---------|---------|---------------|----------|-------------|
| 目标语言 | `zh-CN` | `target_language` | `--to` | 翻译目标语言 |
| 模式 | `normal` | `default_mode` | `--mode` | 翻译模式 |
| 受众 | `general` | `audience` | `--audience` | 目标读者画像 |
| 风格 | `storytelling` | `style` | `--style` | 翻译风格偏好 |
| 分块阈值 | `4000` | `chunk_threshold` | — | 触发分块翻译的词数 |
| 分块最大词数 | `5000` | `chunk_max_words` | — | 每个分块的最大词数 |

## 模式

| 模式 | 标志 | 步骤 | 何时使用 |
|------|------|-------|-------------|
| Quick | `--mode quick` | 翻译 | 短文本、非正式内容、快速任务 |
| Normal | `--mode normal`（默认） | 分析 → 翻译 | 文章、博客、通用内容 |
| Refined | `--mode refined` | 分析 → 翻译 → 审校 → 润色 | 出版级质量、重要文档 |

**默认模式**：Normal（可通过 EXTEND.md 的 `default_mode` 设置覆盖）。

**风格预设**——控制译文的表达方式和语气（独立于受众）：

| 值 | 说明 | 效果 |
|-------|-------------|--------|
| `storytelling` | 有吸引力的叙事流（默认） | 吸引读者，过渡顺滑，措辞生动 |
| `formal` | 专业、结构化 | 语气中立，组织清晰，无口语表达 |
| `technical` | 精确、文档风格 | 简洁，术语密集，尽量少修饰 |
| `literal` | 贴近原文结构 | 尽量少重组，保留原句模式 |
| `academic` | 学术、严谨 | 正式语体，可接受复杂从句，注意引用 |
| `business` | 简洁、结果导向 | 行动导向，适合管理层，倾向要点化 |
| `humorous` | 保留并改写幽默 | 机智、轻松，在目标语言中重现喜剧效果 |
| `conversational` | 随意、口语化 | 友好、易懂，像向朋友解释 |
| `elegant` | 文学化、精致散文 | 审美上精炼，有节奏感，精心择词 |

也接受自定义风格描述，例如 `--style "poetic and lyrical"`。

**自动检测**：
- “快翻”、“quick”、“直接翻译” → quick 模式
- “精翻”、“refined”、“publication quality”、“proofread” → refined 模式
- 其他情况 → 默认模式（normal）

**升级提示**：normal 模式完成后，显示：
> 翻译已保存。若要进一步审校和润色，请回复“继续润色”或“refine”。

如果用户回应，则基于现有输出继续执行审校 → 润色步骤（与 refined-workflow.md 中 refined 模式步骤 4-6 相同）。

**受众预设**：

| 值 | 说明 | 效果 |
|-------|-------------|--------|
| `general` | 普通读者（默认） | 语言平实，对术语添加更多译注 |
| `technical` | 开发者/工程师 | 对常见技术术语少做注释 |
| `academic` | 研究人员/学者 | 正式语体，术语精确 |
| `business` | 商务人士 | 商务友好的语气，解释技术概念 |

也接受自定义受众描述，例如 `--audience "AI感兴趣的普通读者"`。

## 工作流

### 第 1 步：加载偏好设置

1.1 检查 EXTEND.md（见上文“偏好设置”部分）

1.2 如果存在对应语言对的内置术语表，则加载：
- EN→ZH：[references/glossary-en-zh.md](references/glossary-en-zh.md)

1.3 合并术语表：EXTEND.md `glossary`（内联）+ EXTEND.md `glossary_files`（外部文件，路径相对于 EXTEND.md 所在位置）+ 内置术语表 + `--glossary` 文件（CLI 覆盖全部）

### 第 2 步：具象化源内容并创建输出目录

具象化源内容（文件保持原样，内联文本/URL → 保存到 `translate/{slug}.md`），然后创建输出目录：`{source-dir}/{source-basename}-{target-lang}/`。如果未指定 `--from`，则检测源语言。

完整细节：[references/workflow-mechanics.md](references/workflow-mechanics.md)

**输出目录内容**（所有中间文件和最终文件都放在这里）：

| 文件 | 模式 | 说明 |
|------|------|-------------|
| `translation.md` | 全部 | 最终译文（始终使用此名称） |
| `01-analysis.md` | Normal、Refined | 内容分析（领域、语气、术语） |
| `02-prompt.md` | Normal、Refined | 组装后的翻译提示 |
| `03-draft.md` | Refined | 审校前的初稿 |
| `04-critique.md` | Refined | 批判性审校发现（仅诊断） |
| `05-revision.md` | Refined | 基于审校意见修订后的译文 |
| `chunks/` | 分块 | 源分块 + 已翻译分块 |

### 第 3 步：评估内容长度

Quick 模式不分块——无论长度如何都直接翻译。翻译前先估算词数。如果内容超过分块阈值（默认 4000 词），主动提醒：“这篇文章约 {N} 词。Quick 模式会一次性翻译且不分块——对于长内容，`--mode normal` 能通过术语一致性产出更好的结果。” 如果用户没有切换模式，则继续。

对于 normal 和 refined 模式：

| 内容 | 动作 |
|---------|--------|
| < 分块阈值 | 作为单个整体翻译 |
| >= 分块阈值 | 分块翻译（见第 3.1 步） |

**3.1 长内容准备**（仅 normal/refined 模式，且 >= 分块阈值）

翻译分块之前：

1. **提取术语**：扫描整篇文档，找出专有名词、技术术语、重复短语
2. **建立会话术语表**：将提取出的术语与已加载术语表合并，确定一致译法
3. **拆分为分块**：使用 `${BUN_X} {baseDir}/scripts/main.ts <file> [--max-words <chunk_max_words>] [--output-dir <output-dir>]`
   - 解析 markdown 块（标题、段落、列表、代码块、表格等）
   - 在 markdown 块边界拆分，以保留结构
   - 如果单个块超过阈值，则回退到按行拆分，再按词拆分
4. **组装翻译提示**：
   - 主 agent 读取 `01-analysis.md`（如果存在），并使用 [references/subagent-prompt-template.md](references/subagent-prompt-template.md) 的第 1 部分组装共享上下文——内联：目标风格、内容背景、合并术语表和翻译难点
   - 保存为输出目录中的 `02-prompt.md`（仅共享上下文，不含任务指令）
5. **通过 subagent 起草译文**（如果 Agent 工具可用）：
   - 每个分块启动一个 subagent，全部并行（模板第 2 部分）
   - 每个 subagent 读取 `02-prompt.md` 获取共享上下文，接收分块位置信息（第 N 块，共 M 块 + 该块在论证中所处位置的简要上下文），翻译自己的分块，并保存到 `chunks/chunk-NN-draft.md`
   - 一致性由共享的 `02-prompt.md` 保证（术语表、比喻语言映射、理解难点、原文声音，以及分析中的翻译难点）
   - 如果没有分块（内容低于阈值）：为整个源文件启动一个 subagent
   - 如果 Agent 工具不可用，则使用 `02-prompt.md` 内联按顺序翻译分块
6. **合并**：所有 subagent 完成后，按顺序合并已翻译分块。如果存在 `chunks/frontmatter.md`，则将其置于开头。保存为 `03-draft.md`（refined）或 `translation.md`（normal）
7. 所有中间文件（源分块 + 已翻译分块）都保留在 `chunks/` 中

**分块初稿合并后**，控制权返回主 agent，继续进行批判性审校、修订和润色（第 4 步）。

### 第 4 步：翻译与精修

**翻译原则**（适用于所有模式）：

- **重写，而不只是翻译**：将内容重写为自然、有吸引力的目标语言，好像由熟练的母语作者从零写成。质量测试：“读起来是否像原本就是用目标语言写的？”
- **准确第一**：事实、数据和逻辑必须与原文完全一致
- **自然流畅**：使用符合目标语言习惯的语序。将原文长句拆成更短、更自然的句子。按意图理解隐喻和习语，而不是逐字翻译
- **术语**：一致使用标准译法。专业术语首次出现时：用括号标注原文
- **保留格式**：保留所有 markdown 格式（标题、粗体、斜体、图片、链接、代码块）
- **主动解释**：对于目标受众可能缺少背景的行话或概念，添加简洁解释，格式为**粗体括号** `（**解释**）`。注释要少——只在真正有助于理解时添加
- **Frontmatter**：如果源文有 YAML frontmatter，将源元数据字段加上 `source` 前缀并重命名（camelCase：`url`→`sourceUrl`、`title`→`sourceTitle` 等），将翻译后的值作为新的顶层字段加入（如果正文已有 H1，则跳过 `title`），其他字段保持不变

#### Quick 模式

直接翻译 → 保存到 `translation.md`。应用上文所有翻译原则。

#### Normal 模式

1. **分析** → `01-analysis.md`（领域、语气、术语、翻译难点）
2. **组装提示** → `02-prompt.md`（包含上下文、术语表、难点的翻译指令）
3. **翻译**（遵循 `02-prompt.md`）→ `translation.md`

完成后提示用户：“翻译已保存。若要进一步审校和润色，请回复 **继续润色** 或 **refine**。”

如果用户继续，则进入批判性审校 → 修订 → 润色（与下方 refined 模式步骤 4-6 相同），保存 `03-draft.md`（将当前 `translation.md` 重命名）、`04-critique.md`、`05-revision.md`，以及更新后的 `translation.md`。

#### Refined 模式

用于出版级质量的完整工作流。每个步骤的详细指南见 [references/refined-workflow.md](references/refined-workflow.md)。

subagent（如果在第 3.1 步使用）只负责初稿。所有后续步骤（批判性审校、修订、润色）由主 agent 处理；主 agent 可自行决定是否委派给 subagent。

步骤和保存文件（全部位于输出目录）：
1. **分析** → `01-analysis.md`（领域、语气、术语、翻译难点）
2. **组装提示** → `02-prompt.md`（内联上下文的翻译指令）
3. **起草** → `03-draft.md`（包含译者注的初始译文；如果分块，则来自 subagent）
4. **批判性审校** → `04-critique.md`（仅诊断：准确性、欧化语言、策略执行、表达问题）
5. **修订** → `05-revision.md`（应用所有审校发现，产出修订译文）
6. **润色** → `translation.md`（最终出版级译文）

每一步都读取上一步的文件并在其基础上继续。

### 第 5 步：输出

最终译文始终位于输出目录中的 `translation.md`。

写入最终译文后，对图片语言做一次轻量检查：

1. 收集译文文章中的图片引用
2. 识别可能含有大量文字的图片，例如封面、截图、图示、图表、框架图和信息图
3. 如果任何图片的主要文字语言可能与译文语言不一致，主动提醒用户
4. 提醒必须只使用列表。除非用户要求，否则不要自动本地化这些图片

提醒格式（使用文章中已有的图片语法——标准 markdown 或 wikilink）：
```text
可能需要图片本地化：
- ![example cover](attachments/example-cover.png)：文章已翻译为目标语言，但此图片可能仍包含源语言文字
- ![example diagram](attachments/example-diagram.png)：可能是文字较多的框架图，请检查标签是否需要翻译
```

显示摘要：
```
**翻译完成**（{mode} 模式）

源文件：{source-path}
语言：{from} → {to}
输出目录：{output-dir}/
最终译文：{output-dir}/translation.md
已应用术语数：{count}
```

如果发现图片语言不匹配的候选项，则在摘要后附一条简短说明，告诉用户某些嵌入图片可能仍需进行图片文字本地化，并附上候选列表。

## 扩展支持

通过 EXTEND.md 进行自定义配置。路径和支持选项见 **偏好设置** 部分。
