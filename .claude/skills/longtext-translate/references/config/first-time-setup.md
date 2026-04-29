---
name: first-time-setup
description: longtext-translate 偏好设置的首次设置流程
---

# 首次设置

## 概述

当找不到 EXTEND.md 时，引导用户完成偏好设置。

**阻塞操作**：此设置必须在任何翻译之前完成。不要：
- 开始翻译内容
- 询问文件或输出路径
- 继续执行任何工作流步骤

只询问此设置流程中的问题，保存 EXTEND.md，然后继续。

## 设置流程

```
No EXTEND.md found
        |
        v
+---------------------+
| AskUserQuestion     |
| (all questions)     |
+---------------------+
        |
        v
+---------------------+
| Create EXTEND.md    |
+---------------------+
        |
        v
    Continue translation
```

## 问题

**语言**：使用用户的输入语言或已保存的语言偏好。

使用 AskUserQuestion 在一次调用中提出所有问题：

### 问题 1：目标语言

```yaml
header: "Target Language"
question: "Default target language?"
options:
  - label: "简体中文 zh-CN (Recommended)"
    description: "Translate to Simplified Chinese"
  - label: "繁體中文 zh-TW"
    description: "Translate to Traditional Chinese"
  - label: "English en"
    description: "Translate to English"
  - label: "日本語 ja"
    description: "Translate to Japanese"
```

注意：用户可以输入自定义语言代码。

### 问题 2：翻译模式

```yaml
header: "Mode"
question: "Default translation mode?"
options:
  - label: "Normal (Recommended)"
    description: "Analyze content first, then translate"
  - label: "Quick"
    description: "Direct translation, no analysis"
  - label: "Refined"
    description: "Full workflow: analyze → translate → review → polish"
```

### 问题 3：目标受众

```yaml
header: "Audience"
question: "Default target audience?"
options:
  - label: "General readers (Recommended)"
    description: "Plain language, more translator's notes for jargon"
  - label: "Technical"
    description: "Developers/engineers, less annotation on tech terms"
  - label: "Academic"
    description: "Formal register, precise terminology"
  - label: "Business"
    description: "Business-friendly tone, explain tech concepts"
```

注意：用户可以输入自定义受众描述。

### 问题 4：翻译风格

```yaml
header: "Style"
question: "Translation style?"
options:
  - label: "Storytelling (Recommended)"
    description: "Engaging narrative flow, smooth transitions"
  - label: "Formal"
    description: "Professional, structured, neutral tone"
  - label: "Technical"
    description: "Precise, documentation-style, concise"
  - label: "Literal"
    description: "Close to original structure"
  - label: "Academic"
    description: "Scholarly, rigorous, formal register"
  - label: "Business"
    description: "Concise, results-focused, action-oriented"
  - label: "Humorous"
    description: "Preserves humor, witty, playful"
  - label: "Conversational"
    description: "Casual, friendly, spoken-like"
  - label: "Elegant"
    description: "Literary, polished, aesthetically refined"
```

注意：用户可以输入自定义风格描述。

### 问题 5：保存位置

```yaml
header: "Save"
question: "Where to save preferences?"
options:
  - label: "User (Recommended)"
    description: "$HOME/.longtext-translate/ (all projects)"
  - label: "Project"
    description: ".longtext-translate/ (this project only)"
```

## 保存位置

| 选择 | 路径 | 作用域 |
|--------|------|-------|
| User | `$HOME/.longtext-translate/longtext-translate/EXTEND.md` | 所有项目 |
| Project | `.longtext-translate/longtext-translate/EXTEND.md` | 当前项目 |

## 设置后

1. 如有需要，创建目录
2. 使用所选值写入 EXTEND.md
3. 确认：“偏好设置已保存到 [path]”
4. 提醒：“你可以随时向 EXTEND.md 添加自定义术语。格式见文件中的 `glossary` 部分。”
5. 使用已保存偏好继续翻译

## EXTEND.md 模板

```yaml
target_language: [zh-CN/zh-TW/en/ja/...]
default_mode: [quick/normal/refined]
audience: [general/technical/academic/business/custom]
style: [storytelling/formal/technical/literal/academic/business/humorous/conversational/elegant]

# 自定义术语表（可选）——在这里添加你自己的术语翻译
# glossary:
#   - from: "Term"
#     to: "翻译"
#   - from: "Another Term"
#     to: "另一个翻译"
#     note: "使用语境"
```

## 之后修改偏好

用户可以直接编辑 EXTEND.md，或删除它以再次触发设置。
