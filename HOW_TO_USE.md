# How To Use Personal Advisor / 如何使用 Personal Advisor

## English

Personal Advisor is a local folder-based tool. It helps you collect public context about an expert/advisor, such as YouTube transcripts, blogs, publications, and notes, then ask an AI coding/chat tool to answer questions from that saved context.

You do not need to run a separate app or set up an LLM API for the basic workflow.

### 1. Get The Folder

Option A: Fork or clone the GitHub repo.

```bash
git clone https://github.com/wanshuzhang-lgtm/personal-advisor-toolkit.git "Personal Advisor"
cd "Personal Advisor"
```

Option B: Download the repo ZIP from GitHub, unzip it, and rename the folder:

```text
Personal Advisor
```

### 2. Open It In An AI Coding Tool

Open the `Personal Advisor` folder in one of these tools:

- ChatGPT Codex
- Claude Code
- Cursor
- VS Code with an AI assistant extension
- Any IDE or terminal-based AI tool that can read and run files in this folder

For Cursor or VS Code, it is recommended to use a ChatGPT/Codex or Claude extension so the AI can inspect the folder and run the Python scripts.

### 3. Ask Your Question

In the AI chat box, give the advisor name and your question.

Example:

```text
Advisor: Andrej Karpathy
Question: What are the top 3-5 risks relevant to LLM? Give me his perspective.
```

### 4. What The AI Tool Will Do

You should expect to see progress messages or tool logs, such as:

- create or inspect the advisor folder
- discover relevant sources
- find YouTube videos with title, URL, date, channel, duration, and description
- ask you to approve which YouTube videos to use
- download approved YouTube captions into `Advisor/raw_vtts/`
- clean transcripts into `Advisor/transcripts_clean.json`
- fetch public blog/article text when possible
- ask for manual copy/paste only if a source is blocked, login-gated, or LinkedIn
- generate `Advisor/context_notes.md`
- generate a question-specific context pack under `Advisor/_runs/.../context_pack.md`
- answer your question based on the saved context

If the AI asks you to approve YouTube links, you can:

- approve all
- drop old or irrelevant videos
- ask it to search for more
- add a video URL you already know is important

### 5. Example Final Answer

For:

```text
Advisor: Andrej Karpathy
Question: What are the top 3-5 risks relevant to LLM? Give me his perspective.
```

Expected answer style:

```text
Answer: from the saved Karpathy context, the top LLM risks are:

1. Hallucination
Karpathy explicitly frames hallucination as LLMs "making stuff up." His practical mitigation is tool use, especially search, when the model may not know or when information is recent/niche.

2. Overtrust / weak verification
His usage pattern implies you should not treat the model's fluent answer as automatically correct. For important claims, the user should force search, use tools, inspect results, or otherwise verify.

3. Tool-use failure
He views tools as essential because an inert LLM is just a token generator. But tool use adds a new failure layer: the model must know when to call a tool, how to call it, and how to interpret the result.

4. Adversarial or weird input behavior
The "Deep Dive" transcript discusses adversarial examples: small or strange inputs can push neural nets into nonsensical outputs. For LLMs, this maps to prompt brittleness and unexpected failure modes.

5. Uneven capability / jagged intelligence
The model can be impressive in one setting and unreliable nearby. Karpathy's practical response is to use LLMs with task decomposition, examples, tools, and human judgment instead of assuming general competence.
```

### 6. Where Files Are Saved

For each advisor, the tool creates a folder like:

```text
Andrej Karpathy/
  raw_vtts/
  transcripts_clean.json
  sources.json
  context_notes.md
  sources_todo.md
  _runs/
```

Important files:

- `raw_vtts/`: raw YouTube captions
- `transcripts_clean.json`: cleaned YouTube transcripts
- `sources.json`: saved blog/article/manual text sources
- `context_notes.md`: quick source inventory with dates and descriptions
- `_runs/.../context_pack.md`: question-specific context used for the final answer

---

## 中文

Personal Advisor 是一个在你自己电脑上运行的本地文件夹工具。它可以帮你收集某个专家/advisor 的公开资料，比如 YouTube transcript、博客、文章、论文、笔记等，然后让 AI 编程/聊天工具基于这些本地 context 回答你的问题。

基础使用不需要单独搭 app，也不需要配置 LLM API。

### 1. 获取这个文件夹

方式 A：Fork 或 clone GitHub repo。

```bash
git clone https://github.com/wanshuzhang-lgtm/personal-advisor-toolkit.git "Personal Advisor"
cd "Personal Advisor"
```

方式 B：从 GitHub 下载 ZIP，解压后把文件夹改名为：

```text
Personal Advisor
```

### 2. 用 AI 工具打开这个文件夹

用下面任意一种工具打开 `Personal Advisor` 文件夹：

- ChatGPT Codex
- Claude Code
- Cursor
- VS Code + AI assistant extension
- 其他可以读取并运行本地文件的 AI/IDE 工具

如果你用 Cursor 或 VS Code，建议安装 ChatGPT/Codex 或 Claude 相关 extension，这样 AI 可以直接看这个 folder，并运行里面的 Python scripts。

### 3. 在对话框里提问

在 AI chat box 里告诉它 advisor 和 question。

例如：

```text
Advisor: Andrej Karpathy
Question: What are the top 3-5 risks relevant to LLM? Give me his perspective.
```

### 4. AI 工具中间会做什么

你应该会看到一些过程提示或 tool logs，例如：

- 创建或检查 advisor folder
- 搜索相关 sources
- 找到 YouTube 视频，并展示 title、URL、date、channel、duration、description
- 让你 approve 哪些 YouTube 视频要用
- 把 approve 的 YouTube captions 下载到 `Advisor/raw_vtts/`
- 清理 transcript，保存到 `Advisor/transcripts_clean.json`
- 尝试自动抓取公开 blog/article 的正文
- 只有在 source 被 block、需要 login、或者是 LinkedIn 时，才提示你手动 copy/paste
- 生成 `Advisor/context_notes.md`
- 在 `Advisor/_runs/.../context_pack.md` 里生成本次问题对应的 context pack
- 最后基于保存好的 context 回答你的问题

如果 AI 让你 approve YouTube links，你可以：

- 全部 approve
- 删除太旧或不 relevant 的视频
- 让它继续 search more
- 补充你自己知道的重要 video URL

### 5. 示例最终回答

对于：

```text
Advisor: Andrej Karpathy
Question: What are the top 3-5 risks relevant to LLM? Give me his perspective.
```

期望回答风格：

```text
Answer: from the saved Karpathy context, the top LLM risks are:

1. Hallucination
Karpathy explicitly frames hallucination as LLMs "making stuff up." His practical mitigation is tool use, especially search, when the model may not know or when information is recent/niche.

2. Overtrust / weak verification
His usage pattern implies you should not treat the model's fluent answer as automatically correct. For important claims, the user should force search, use tools, inspect results, or otherwise verify.

3. Tool-use failure
He views tools as essential because an inert LLM is just a token generator. But tool use adds a new failure layer: the model must know when to call a tool, how to call it, and how to interpret the result.

4. Adversarial or weird input behavior
The "Deep Dive" transcript discusses adversarial examples: small or strange inputs can push neural nets into nonsensical outputs. For LLMs, this maps to prompt brittleness and unexpected failure modes.

5. Uneven capability / jagged intelligence
The model can be impressive in one setting and unreliable nearby. Karpathy's practical response is to use LLMs with task decomposition, examples, tools, and human judgment instead of assuming general competence.
```

### 6. 文件会保存在哪里

每个 advisor 会有自己的文件夹，例如：

```text
Andrej Karpathy/
  raw_vtts/
  transcripts_clean.json
  sources.json
  context_notes.md
  sources_todo.md
  _runs/
```

重要文件：

- `raw_vtts/`：原始 YouTube captions
- `transcripts_clean.json`：清理后的 YouTube transcripts
- `sources.json`：保存的 blog/article/manual text sources
- `context_notes.md`：带日期和简短描述的 source inventory
- `_runs/.../context_pack.md`：某一次具体问题使用的 context pack

