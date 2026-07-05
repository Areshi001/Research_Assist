# Research Assistant

An autonomous academic AI Research Assistant that can search papers on a given topic at arxiv.org, read papers in depth using custom PDF tools, perform comprehensive research, and compile/render a ready-to-publish research paper PDF.

## System Architecture

### Deciding Factors and Core Components

1. **Gemini 2.5 Flash**
   - **Why it was chosen**: Selected for its low latency, high context window (up to 1 million tokens), and optimized cost-efficiency. It handles structured output generation and tool schemas cleanly.

2. **LangGraph Orchestrator**
   - **Why it was chosen**: Standard stateless ReAct agents lose context across multiple turns. LangGraph provides state management, checkpointing, and conditional state routing, allowing the assistant to maintain a memory of the user's instructions across research phases.

3. **Streamlit UI**
   - **Why it was chosen**: Allows fast, single-process Python dashboard deployment. By injecting custom CSS, it functions as a lightweight state engine and frontend without the overhead of node/js setups.

4. **Tectonic TeX Engine**
   - **Why it was chosen**: A modern, self-configuring LaTeX engine that dynamically downloads missing TeX packages as needed. This eliminates the requirement to pre-install multi-gigabyte MacTeX/MikTeX environments.

---

## Agentic Flow and Streaming Architecture

The flow of messages and state updates is divided into two primary modes:

### 1. Agent Modes

#### Simple Mode (ReAct Loop)
A basic loop designed for rapid queries.
- **Workflow**: User Prompt -> LLM -> Tool Call (arXiv Search, PDF Read, or TeX Compile) -> Tool Execution -> Final LLM Answer.
- **Characteristics**: Fast, single-turn, stateless execution.

#### Advanced Mode (StateGraph with Memory)
A stateful workflow managing memory checkpoints.
- **Workflow**: 
  - The model decides whether tool invocation is required.
  - If yes, routes to the `tools` execution node, updates state, and loops back to the model.
  - If no, routes to `END` and compiles the response.
- **Characteristics**: Supports cross-turn conversation history using `MemorySaver` checkpoints keyed by a session `thread_id`.

### 2. Streaming Mechanism
To optimize latency responsiveness:
- The UI triggers `graph.stream(..., stream_mode="messages")`.
- The system intercepts raw token packets (`AIMessageChunk`) as they are produced by the LLM.
- The UI displays these tokens dynamically to the user in real-time, bypassing block-by-block node compilation delays.

---

## Getting Started

1. **Install Dependencies**:
   This project uses `uv` for package management.
   ```bash
   uv sync
   ```

2. **Set up Environment**:
   Create a `.env` file in the root directory and add your Google Gemini API key:
   ```env
   GOOGLE_API_KEY=your-api-key-here
   ```

3. **Install Tectonic**:
   Ensure `tectonic` is on your PATH or place a compiled `tectonic.exe` in the root folder.

4. **Launch the UI**:
   Run the Streamlit app:
   ```bash
   uv run streamlit run frontend.py --browser.gatherUsageStats false
   ```
