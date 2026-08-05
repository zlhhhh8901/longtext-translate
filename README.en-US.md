

# longtext-translate

An Agent Skill for foreign-language reading scenarios. Hand over materials of any format and length to the Agent, and receive back a native-language translation that is comfortable to read.

## What Problem Does It Solve

Translation, especially long-text translation, often faces these bottlenecks:

- If the source file is a PDF or EPUB, you first have to manually extract text, clean up formatting, and handle image paths
- As text length increases, the output quality of LLMs begins to degrade: terminology drift, increased translationese, logical breaks between paragraphs, etc.
- Even after getting the translation, you might not be able to read it with confidence—constantly checking for translation deviations while mentally correcting awkward phrasing keeps the comprehension cost high

The actual process is often a repetitive cycle of "prepare materials → translate → read with difficulty → discover issues → manually correct and polish → read again." It might take a week or two to truly absorb a single paper.

This Skill takes over the labor-intensive manual steps; you only need to intervene at key decision points.

## Workflow

<p align="center">
  <img src="assets/introduction.png" alt="工作流程" width="45%" />
</p>

## Translation Principles

- **Faithful to the Original** Completely preserve facts, data, viewpoints, logical relationships, and argument structures
- **Rewrite the Translation** Reconstruct sentences, information order, and paragraph rhythm according to the target language's conventions, rather than literal conversion
- **Register Matching** Equivalently reproduce the original's degree of colloquialism, emotional intensity, and genre style
- **Terminology Consistency** Core terms are unified throughout the text, with original terms annotated upon first mention for professional jargon
- **Format Preservation** Markdown structures such as headings, bold text, links, images, and code blocks are preserved exactly as is

## Key Features

**Locally Stored & Traceable** All key intermediate outputs are kept in the local output directory, making them traceable, debuggable, and recoverable.

**On-Demand Extraction for All Formats** Automatically normalizes PDFs, EPUBs, webpages, etc., into Markdown; PDFs and EPUBs can extract only the required pages or chapter ranges.

**Stable Quality for Long Texts** Long texts are first chunked, a shared terminology table and translation prompts are generated, and then subagents are dispatched for parallel translation, ensuring consistent terminology and style across chunks.

**Human-in-the-Loop for Key Decisions** High-risk steps and those unsuitable for pure text description, such as adjusting chunk boundaries and reviewing layout corrections, are provided with a visual interface for user confirmation before execution.

**Smart Terminology Table Filtering** Large terminology files (hundreds of entries) are not fed entirely into the context. Instead, only terms actually appearing in the source text are automatically filtered and applied. Supports common formats like TSV, CSV, and Markdown tables.

**Polished to Publication Standards** After translation, you can optionally choose proofreading (paragraph-by-paragraph comparison with the original + polishing without the original), editing & refining (highlighting key points and structure / adding annotations for potentially missing information / unifying Chinese layout and formatting), or a bilingual version.

<table>
  <tr>
    <td align="center" width="50%">
      <a href="assets/chunk-html-demo.png" target="_blank">
        <img src="assets/chunk-html-demo.png" alt="分片预览与调整页面截图" style="max-width: 480px; width: 100%; border-radius: 8px; box-shadow: 0 2px 12px #0002;"/>
      </a>
      <br>Chunk Preview & Adjustment<br>
    </td>
    <td align="center" width="50%">
      <a href="assets/polish-html-demo.png" target="_blank">
        <img src="assets/polish-html-demo.png" alt="排版修正预览与确认页面截图" style="max-width: 480px; width: 100%; border-radius: 8px; box-shadow: 0 2px 12px #0002;"/>
      </a>
      <br>Layout Correction Preview & Confirmation<br>
    </td>
  </tr>
</table>

## Quick Start

**Installation**

```bash
npx skills add zlhhhh8901/longtext-translate
```

Or simply tell the agent:

```
请帮我安装这个 skill：github.com/zlhhhh8901/longtext-translate
```

**Usage**

State your translation needs directly in the Agent conversation, and the Skill will trigger automatically. For example:

- "Translate pages 10 to 20 of this paper into Chinese: @paper.pdf"
- "The quality of this draft is not good, please proofread it. Original is at @original.md, draft is at @draft.md"

The Skill includes an accessible workflow guide; users don't need to understand the internal implementation to get started out of the box.

## Translation Quality Comparison

**Test Sample**: [Anthropic - When AI builds itself](https://www.anthropic.com/institute/recursive-self-improvement)

**Running Model**: deepseek-v4-pro (Inference Intensity: High, Runtime Environment: ClaudeCode), produced through the full workflow of "Translation + Proofreading + Editing & Refining"

**Result Comparison**: https://compare-gules.vercel.app (Translation A is directly output by the Skill, Translation B is the version published by [Digital Life Kazik](https://mp.weixin.qq.com/s/mJbuKJChVk7ktIHEtKzChg))

## Cost & Time Reference

**Test Sample**: English original of *Stein on Writing*, 228 pages, 104k words (volume is close to the English original of *Harry Potter and the Prisoner of Azkaban* at 107k words)

**Running Model**: deepseek-v4-pro (Inference Intensity: High, Runtime Environment: ClaudeCode)

| Stage | Time | Cost |
|------|------|------|
| Normalization (PDF → Markdown) | 57 sec | ¥0.16 |
| **Translation** (22 subagents parallel) | **14 min 21 sec** | **¥4.91** |
| Proofreading | 8 min 41 sec | ¥0.40 |
| Editing & Refining | 2 min 33 sec | ¥0.28 |
| Bilingual Version | 2 min 3 sec | ¥0.09 |
| **Total** | **28 min 35 sec** | **¥5.84** |

## Output Files

Translation results are stored in the directory containing the source Markdown file, with the directory named `{source_filename}-{target_language}/`. For example, the result of `article.md` will be placed in `article-zh/`.

The location of the source Markdown file depends on the input type:

- PDF / EPUB / Word / Images: Normalized files are saved in the same directory as the source file
- Inline text / URL: Saved in the `translate/` directory
- Existing text files: Used directly as source files

The actual files contained in the directory vary depending on the translation mode and subsequent options.

```
article-zh/
├── translation.md        ← Final translation (required)
├── glossary.md           ← Shared terminology table (long text mode)
├── prompt.md             ← Shared translation prompt for subagents (long text mode)
├── chunk-preview.html    ← Chunk preview page (long text mode)
├── chunks/               ← Original text and drafts for each chunk (long text mode)
├── draft.md              ← Draft snapshot before proofreading/editing
├── critique.md           ← Structured proofreading report
├── polish-preview.html   ← Layout correction preview page
└── bilingual.md          ← Bilingual comparison file
```

## Acknowledgments

This Skill is a modification of [baoyu-translate](https://github.com/baoyu-io/baoyu-translate) — the chunking strategy, the workflow skeleton for subagent parallel scheduling, and the core translation principle of "rewriting, not just translating" are all derived from that project.

Additionally, the following projects provided important references or direct support in specific implementation steps:

- [MinerU](https://github.com/opendatalab/MinerU): Normalized extraction of documents like PDFs, Word, and images; directly uses services provided by this project
- [baoyu-format-markdown](https://github.com/baoyu-io/baoyu-format-markdown): The design of "highlighting key points and structure" in the editing process is referenced from this project
- [chinese-copywriting-guidelines](https://github.com/sparanoid/chinese-copywriting-guidelines): The normative basis for "Chinese layout and formatting correction" in the editing process
- [Superpowers](https://github.com/obra/superpowers): The browser interaction design concept for chunk preview and layout correction is referenced from this project

## Links

[LINUX DO - A New Ideal Community](https://linux.do)

## License

MIT
