# longtext-translate

**AI agent 翻译 skill**，处理任意长度、任意格式的文本——从一段话到整本书，从纯文本到 PDF、EPUB、Word、图片。告诉 Agent 你想翻译什么，剩下的由它完成。

## 解决什么问题

直接用 LLM 翻译存在几个短板：

- **长文本质量衰减**：超出上下文窗口后，后半程翻译质量明显下降——术语前后不一致、论证逻辑丢失、段落之间语气不连贯。
- **翻译腔影响阅读**：句子看似通顺，但行文仍受原文语序和表达习惯束缚，读者需要反复揣摩才能理解，阅读负担并未真正消除。
- **非文本材料处理繁琐**：源文件是 PDF 或 EPUB 时，需要手动提取文字、清洗排版、处理图片路径，准备工作本身就很耗时。
- **审校和精编缺乏流程支撑**：翻译完成后想进一步打磨，缺少系统的诊断框架、修正流程和排版规范，难以保证审校质量。

## 工作流程

<img src="assets/introduction.png" alt="introduction" style="zoom:50%;" />

## 主要特性

**多格式输入**　支持 PDF、EPUB、Word、图片、纯文本、Markdown 和 URL，统一转为干净的 Markdown 后再翻译，格式转换细节由 Agent 自动处理。

**先理解再翻译**　Agent 会先通读材料，理解内容、语域和翻译难点，然后一次性提出完整的翻译方案——包括目标语言、读者定位和术语策略。用户确认后才开始执行。

**长文本一致性**　长文本模式下，分片前先生成共享术语表和翻译简报，每个并行 subagent 均以这两份文件为基准执行翻译，确保跨分片的术语和风格统一。

**按需深入打磨**　质量门禁之后，可按需选择后续处理。审校：逐段对照原文，产出可证伪的结构化诊断报告。精编：将译文作为独立的目标语言文章做最终打磨，包括显化论证结构、补充背景说明和统一中文排版。双语版：原文与译文按段落对齐、交替排列，便于对照阅读。三项可全选也可只选其一。

**关键决策由人把关**　分片边界调整、排版修正审阅等高风险且不适合纯文本描述的环节，通过本地服务启动 HTML 页面在浏览器中交互完成——长文本翻译前可预览分片方案，查看每片的起止位置和词数，手动调整分片边界后再执行，避免切分位置不当影响翻译质量；精编阶段的排版修正同样提供浏览器预览，用户确认后才落地文件。

## 快速开始

**安装**

```bash
npx skills add zlhhhh8901/longtext-translate
```

或直接告诉 agent：

```
请帮我安装这个 skill：github.com/zlhhhh8901/longtext-translate
```

**使用**

在 Agent 对话中直接说出你的翻译需求，Skill 会自动触发。比如：

- “把这篇论文翻译成中文：/path/to/paper.pdf”
- “帮我翻译一下这段英文，目标读者是非技术背景的管理者”
- “这份译稿质量不太好，帮我审校一下，原文在 original.md，译稿在 draft.md”

Skill 内置了无障碍流程引导，使用者无需知道其内部实现。

## 产出文件

所有产出都放在源文件旁边的同名输出目录里（例如 `article.md` → `article-zh/`）：

```
article-zh/
├── translation.md        ← 译文（必有）
├── glossary.md           ← 共享术语表（长文本模式）
├── prompt.md             ← 翻译简报（长文本模式）
├── chunk-preview.html    ← 分片预览页面（长文本模式）
├── chunks/               ← 各分片的原文和译稿（长文本模式）
├── draft.md              ← 审校/精编前的译稿快照
├── critique.md           ← 结构化审校报告
├── polish-preview.html   ← 排版修正预览页面
└── bilingual.md          ← 双语对照版
```

短文本翻译只有 `translation.md` 一个产出。

## 运行依赖

Agent 会自动按需安装：

- **Python 3**（必需）
- `markdown-it-py >= 4.0, < 5`（分片、双语对齐、精编预览需要）
- `autocorrect-py`（精编预览——中文排版规范化，仅精编流程需要）
- [MinerU CLI](https://github.com/opendatalab/MinerU)（处理 PDF/Word/图片时需要）

Agent 会引导安装与配置：`MinerU API Token`。

## 费用参考

**测试样本**：Stein on Writing.pdf - 776 KB，5070 行，104378 词，604552 字符
**运行模型**：deepseek-v4-pro（推理强度：High，运行环境：ClaudeCode）

| 阶段 | 耗时 | 费用 |
|------|------|------|
| 规范化（PDF → Markdown） | 57 秒 | ¥0.16 |
| 翻译（22 个 subagent 并行） | 14 分 21 秒 | ¥4.91 |
| 审校 | 8 分 41 秒 | ¥0.40 |
| 精编 | 2 分 33 秒 | ¥0.28 |
| 双语版 | 2 分 3 秒 | ¥0.09 |
| **合计** | **28 分 35 秒** | **¥5.84** |

## 致谢

本 Skill 在 [baoyu-translate](https://github.com/baoyu-io/baoyu-translate) 的基础上修改而来——分片策略、subagent 并行调度、增强路由等流程骨架均建立在该项目的基础之上。

此外，以下项目在具体实现环节提供了重要参考或直接支撑：

- [Superpowers](https://github.com/obra/superpowers)：分片预览与排版修正的浏览器交互设计思路参考自该项目。
- [MinerU](https://github.com/opendatalab/MinerU)：PDF、Word 与图片等文档的规范化提取，直接使用该项目提供的服务。
- [baoyu-format-markdown](https://github.com/baoyu-io/baoyu-format-markdown)：精编流程中“重点与结构显化”的设计参考自该项目。
- [chinese-copywriting-guidelines](https://github.com/sparanoid/chinese-copywriting-guidelines)：精编流程中“中文排版与格式修正”的规范依据来源。

## 许可证

MIT