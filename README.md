# 📄 RAG 智能文档问答系统

基于 **RAG (Retrieval-Augmented Generation)** 架构的智能文档问答平台。上传 PDF/TXT/Markdown 文档后，即可用自然语言提问，AI 基于文档内容精准回答。

## 🏗 架构

```
┌─────────────────────────────────────────┐
│              用户上传文档                  │
│          PDF / TXT / Markdown            │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│           DocumentLoader                 │
│   解析文档 → 提取文本 + 元数据             │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│           TextSplitter                   │
│   递归字符分割 → Chunks (500字/块)        │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│         EmbeddingService                 │
│   sentence-transformers → 384维向量      │
└──────────────┬──────────────────────────┘
               ↓
┌──────────────┴──────────────────────────┐
│           VectorStore (ChromaDB)          │
│       持久化存储 + 余弦相似度检索          │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  用户提问 → Retriever → 检索Top-K片段     │
│     Context + Query → LLM → 精准回答      │
└─────────────────────────────────────────┘
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 安装 Python 依赖
cd server
pip install -r requirements.txt

# 配置 API Key
cp .env.example .env
# 编辑 .env，填入你的 API Key

# 安装前端依赖
cd ../client
npm install
```

### 2. 启动服务

```bash
# 终端 1：启动后端 (http://localhost:8000)
cd server
python main.py

# 终端 2：启动前端 (http://localhost:5174)
cd client
npm run dev
```

### 3. 使用

1. 打开 http://localhost:5174
2. 上传 PDF / TXT / Markdown 文档
3. 系统自动向量化并索引
4. 输入问题，AI 基于文档内容回答

## 📡 API

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/health` | 健康检查 |
| `POST` | `/api/upload` | 上传文档 |
| `POST` | `/api/documents/index` | 向量化已上传文档 |
| `GET` | `/api/documents` | 列出已上传文档 |
| `POST` | `/api/chat` | 问答（非流式） |
| `POST` | `/api/chat/stream` | 问答（SSE 流式） |

## 🛠 技术栈

| 层 | 技术 |
|----|------|
| **后端框架** | FastAPI (Python) |
| **向量数据库** | ChromaDB |
| **文本嵌入** | sentence-transformers (all-MiniLM-L6-v2) |
| **LLM** | OpenAI 兼容 API (GPT / DeepSeek / 通义千问 等) |
| **前端** | React 19 + TypeScript + Vite |
| **文档解析** | PyPDF2 |

## 📁 项目结构

```text
server/
├── main.py              # FastAPI 入口
├── server_state.py       # 全局状态管理
├── rag/
│   ├── document_loader.py  # PDF/TXT/MD 解析
│   ├── text_splitter.py    # 递归分块
│   ├── embeddings.py       # 文本向量化
│   ├── vector_store.py     # ChromaDB CRUD
│   ├── retriever.py        # 语义检索
│   └── generator.py        # LLM 生成
└── routes/
    ├── upload.py         # 文档上传
    ├── chat.py           # 问答 (流式 SSE)
    └── index_.py         # 文档管理

client/
└── src/
    ├── App.tsx           # 主界面 (聊天 + 文档管理)
    ├── api/index.ts      # API 封装 (含 SSE)
    └── index.css         # GitHub Dark 主题
```

## 🔑 支持的 LLM

| 服务 | 配置示例 |
|------|---------|
| **OpenAI** | `OPENAI_API_KEY=sk-xxx` `OPENAI_BASE_URL=` (留空) |
| **DeepSeek** | `OPENAI_API_KEY=sk-xxx` `OPENAI_BASE_URL=https://api.deepseek.com` |
| **通义千问** | `OPENAI_API_KEY=sk-xxx` `OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1` |
| **本地模型** | 使用 ollama / vllm 兼容接口 |

## 📝 License

MIT
