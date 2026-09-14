---
name: markdown-cjk-spacing
description: Check and fix Chinese-English mixed Markdown typography. Use when Codex is asked to proofread, lint, normalize, or edit Markdown/plain text containing Chinese plus English/ASCII terms, especially for spacing between Chinese and English, removing spaces between English and Chinese punctuation, and wrapping bold Markdown near punctuation with zero-width space entities.
---

# Markdown CJK Spacing

## Workflow

1. Preserve Markdown structure before editing prose:
   - Do not change fenced code blocks, inline code, math, URLs, file paths, frontmatter keys, HTML tags, or existing entities unless the user explicitly asks.
   - Keep Markdown syntax intact when moving spaces around emphasis markers, links, headings, lists, and blockquotes.
2. Apply the rules below to normal prose.
3. If returning edits instead of rewriting the full document, report each issue with a concise before/after example.

## Rules

### Chinese-English spacing

Insert one ASCII space between Chinese characters and adjacent English/ASCII words, abbreviations, or product names.

Examples:

```markdown
使用OpenAI API生成文本。 -> 使用 OpenAI API 生成文本。
这是Markdown文档。 -> 这是 Markdown 文档。
在React中使用hooks。 -> 在 React 中使用 hooks。
```

Do not insert spaces inside English phrases, URLs, code spans, or Markdown syntax. Keep existing correct spaces.

### English and Chinese punctuation

Remove spaces between English/ASCII text and Chinese punctuation. Chinese punctuation should stay attached to neighboring prose.

Examples:

```markdown
OpenAI ，很好用。 -> OpenAI，很好用。
这是 API 。 -> 这是 API。
支持 Markdown ：标题、列表。 -> 支持 Markdown：标题、列表。
```

This applies to common Chinese punctuation such as `，。！？；：（）【】《》、`.

### Bold text near punctuation

When a Markdown bold span is directly adjacent to punctuation on either side, place the HTML zero-width space entity outside the bold markers: `&#8203;**bold**&#8203;`.

Examples:

```markdown
这是，**重点**。 -> 这是，&#8203;**重点**&#8203;。
(**Important**) -> (&#8203;**Important**&#8203;)
请注意：**不要删除**！ -> 请注意：&#8203;**不要删除**&#8203;！
```

Treat both Chinese and English punctuation as punctuation for this rule, including `，。！？；：（）【】《》、,.!?;:()[]{}<>`.

Keep the entity outside the bold markers, never inside the bold text:

```markdown
Correct: &#8203;**加粗的部分**&#8203;
Wrong: **&#8203;加粗的部分&#8203;**
```

## Output Style

Prefer the least disruptive edit that satisfies the rules. When uncertain whether a space is semantic, keep the original wording and mention the ambiguity instead of making a broad rewrite.
