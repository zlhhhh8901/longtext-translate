# 工作流机制

源材料具象化、输出目录创建和冲突解决的细节。

## 具象化源内容

| 输入类型 | 动作 |
|------------|--------|
| 文件 | 原样使用（无需复制） |
| 内联文本 | 保存到 `translate/{slug}.md` |
| URL | 抓取内容，保存到 `translate/{slug}.md` |

`{slug}`：根据内容主题生成的 2-4 个词 kebab-case slug。

## 创建输出目录

在源文件旁边创建子目录：`{source-dir}/{source-basename}-{target-lang}/`

示例：
- `posts/article.md` → `posts/article-zh/`
- `translate/ai-future.md` → `translate/ai-future-zh/`

## 冲突解决

如果输出目录已经存在，在创建新目录前将现有目录重命名为 `{name}.backup-YYYYMMDD-HHMMSS/`。绝不覆盖已有结果。
