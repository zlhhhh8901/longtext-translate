# longtext-translate 的 EXTEND.md Schema

## 格式

EXTEND.md 使用 YAML 格式：

```yaml
# 默认目标语言（ISO 代码或常用名称）
target_language: zh-CN

# 默认翻译模式
default_mode: normal  # quick | normal | refined

# 目标受众（影响注释深度和语体）
audience: general  # general | technical | academic | business | or custom string

# 翻译风格偏好
style: storytelling  # storytelling | formal | technical | literal | academic | business | humorous | conversational | elegant | or custom string

# 触发分块翻译的词数阈值
chunk_threshold: 4000

# 每个分块的最大词数
chunk_max_words: 5000

# 自定义术语表（与内置术语表合并）
# CLI --glossary 标志会覆盖这些配置
# 支持内联条目和/或文件路径
glossary:
  - from: "Reinforcement Learning"
    to: "强化学习"
  - from: "Transformer"
    to: "Transformer"
    note: "Keep English"

# 从外部文件加载术语表
# 支持绝对路径或相对于 EXTEND.md 所在位置的路径
# 文件格式：包含 | from | to | note | 列的 markdown 表格，
# 或 {from, to, note} 条目的 YAML 列表
glossary_files:
  - ./my-glossary.md
  - /path/to/shared-glossary.yaml

# 针对特定语言对的术语表
glossaries:
  en-zh:
    - from: "AI Agent"
      to: "AI 智能体"
  ja-zh:
    - from: "人工知能"
      to: "人工智能"
```

## 字段

| 字段 | 类型 | 默认值 | 说明 |
|-------|------|---------|-------------|
| `target_language` | string | `zh-CN` | 默认目标语言代码 |
| `default_mode` | string | `normal` | 默认翻译模式（`quick` / `normal` / `refined`） |
| `audience` | string | `general` | 目标读者画像（`general` / `technical` / `academic` / `business` / 自定义） |
| `style` | string | `storytelling` | 翻译风格（`storytelling` / `formal` / `technical` / `literal` / `academic` / `business` / `humorous` / `conversational` / `elegant` / 自定义） |
| `chunk_threshold` | number | `4000` | 触发分块翻译的词数阈值 |
| `chunk_max_words` | number | `5000` | 每个分块的最大词数 |
| `glossary` | array | `[]` | 通用术语表条目（内联） |
| `glossary_files` | array | `[]` | 外部术语表文件路径（绝对路径或相对于 EXTEND.md） |
| `glossaries` | object | `{}` | 特定语言对的术语表条目 |

## 术语表条目

| 字段 | 必填 | 说明 |
|-------|----------|-------------|
| `from` | 是 | 源术语 |
| `to` | 是 | 目标译法 |
| `note` | 否 | 用法说明（例如 “Keep English”、“Only in tech context”） |

## 术语表文件格式

外部术语表文件（`glossary_files`）支持两种格式：

**Markdown 表格**（`.md`）：
```markdown
| from | to | note |
|------|----|------|
| Reinforcement Learning | 强化学习 | |
| Transformer | Transformer | Keep English |
```

**YAML 列表**（`.yaml` / `.yml`）：
```yaml
- from: "Reinforcement Learning"
  to: "强化学习"
- from: "Transformer"
  to: "Transformer"
  note: "Keep English"
```

路径可以是绝对路径，也可以相对于 EXTEND.md 文件所在位置。

## 优先级

1. CLI `--glossary` 文件条目
2. EXTEND.md `glossaries[pair]` 条目
3. EXTEND.md `glossary` 条目（内联）
4. EXTEND.md `glossary_files` 条目（按列出顺序，后面的文件覆盖前面的文件）
5. 内置术语表（例如 `references/glossary-en-zh.md`）

对于相同源术语，后面的条目覆盖前面的条目。
