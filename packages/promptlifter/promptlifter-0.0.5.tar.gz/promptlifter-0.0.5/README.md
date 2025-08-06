# PromptLifter

A LangGraph-powered context extender that prioritizes custom/local LLM endpoints (like Llama, Ollama) with commercial model fallbacks, orchestrating web search and vector search to produce structured, expert-level answers from complex queries.

[![PyPI version](https://badge.fury.io/py/promptlifter.svg)](https://badge.fury.io/py/promptlifter)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/promptlifter/promptlifter/workflows/CI/badge.svg)](https://github.com/promptlifter/promptlifter/actions)

## ✨ Features

- **Subtask Decomposition**: Automatically breaks complex queries into focused research subtasks using custom/local LLMs (Llama, Ollama, etc.)
- **Parallel Processing**: Executes web search and vector search simultaneously for each subtask
- **Context-Aware Generation**: Combines web results and internal knowledge for comprehensive answers
- **Structured Output**: Produces well-organized, research-quality responses
- **LangGraph Orchestration**: Leverages LangGraph for robust workflow management

## 🚀 Quick Start

### Installation

#### From PyPI (Recommended)
```bash
pip install promptlifter
```

#### From Source
```bash
git clone https://github.com/promptlifter/promptlifter
cd promptlifter
pip install -e .
```

### Basic Usage

```python
from promptlifter import build_graph

# Build the workflow graph
graph = build_graph()

# Run a research query
result = await graph.ainvoke({
    "input": "Research quantum computing trends and applications"
})

print(result["final_output"])
```

### Command Line Usage

```bash
# Interactive mode
promptlifter --interactive

# Single query
promptlifter --query "Research AI in healthcare applications"

# Save results to file
promptlifter --query "Quantum computing research" --save results.json
```

## 🏗️ Architecture

```
promptlifter/
├── promptlifter/          # Main package
│   ├── __init__.py        # Package initialization
│   ├── main.py            # Main application entry point
│   ├── graph.py           # LangGraph workflow definition
│   ├── config.py          # Configuration and environment variables
│   ├── logging_config.py  # Logging configuration
│   └── nodes/             # Individual workflow nodes
│       ├── __init__.py    # Nodes package initialization
│       ├── split_input.py # Query decomposition
│       ├── llm_service.py # LLM service with rate limiting
│       ├── embedding_service.py # Embedding service
│       ├── run_tavily_search.py # Web search integration
│       ├── run_pinecone_search.py # Vector search integration
│       ├── compose_contextual_prompt.py # Prompt composition
│       ├── run_subtask_llm.py # LLM processing
│       ├── subtask_handler.py # Parallel subtask orchestration
│       └── gather_and_compile.py # Final result compilation
├── tests/                 # Test suite
│   ├── __init__.py        # Test package initialization
│   ├── conftest.py        # Pytest fixtures
│   ├── test_config.py     # Configuration tests
│   ├── test_graph.py      # Graph tests
│   └── test_nodes.py      # Node tests
├── setup.py               # Package setup
├── pytest.ini            # Pytest configuration
├── requirements.txt       # Dependencies
├── .env                   # Environment variables
└── README.md             # This file
```

## 🔧 Setup

### 1. Clone the Repository

```bash
git clone https://github.com/promptlifter/promptlifter
cd promptlifter
```

### 2. Install Dependencies

#### Option 1: Install from Source
```bash
pip install -e .
```

#### Option 2: Install with Development Dependencies
```bash
pip install -e ".[dev]"
```

#### Option 3: Install with Test Dependencies
```bash
pip install -e ".[test]"
```

### 3. Configure Environment Variables

Copy the example environment file and configure your API keys:

```bash
cp env.example .env
```

Edit `.env` with your configuration:

```env
# Custom LLM Configuration (Primary - Local Models or OpenAI-Compatible APIs)
CUSTOM_LLM_ENDPOINT=http://localhost:11434
CUSTOM_LLM_MODEL=llama3.1
CUSTOM_LLM_API_KEY=

# LLM Provider Configuration (Choose ONE provider)
LLM_PROVIDER=custom  # custom, openai, anthropic, google

# Embedding Configuration (Choose ONE provider)
EMBEDDING_PROVIDER=custom  # custom, openai, anthropic
EMBEDDING_MODEL=text-embedding-3-small  # Model name for embeddings

# Commercial LLM Configuration (API keys for non-custom providers)
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
GOOGLE_API_KEY=your-google-api-key-here

# Search and Vector Configuration (Optional)
TAVILY_API_KEY=your-tavily-api-key-here
PINECONE_API_KEY=your-pinecone-api-key-here
PINECONE_INDEX=your-pinecone-index-name-here
PINECONE_NAMESPACE=research

# Pinecone Search Configuration (Optional)
PINECONE_TOP_K=10                    # Number of results (default: 10)
PINECONE_SIMILARITY_THRESHOLD=0.7    # Minimum similarity (0.0-1.0)
PINECONE_INCLUDE_SCORES=true         # Show similarity scores
PINECONE_FILTER_BY_SCORE=true        # Filter by threshold
```

**Note**: PromptLifter uses a simplified configuration approach. You specify exactly which LLM and embedding providers to use, eliminating cascading fallbacks for more predictable behavior.

### 4. Set Up LLM Providers

#### Option 1: Local LLM (Recommended - No API Keys Needed)

##### Using Ollama (Easiest)
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull Llama 3.1 model
ollama pull llama3.1

# Start Ollama server
ollama serve
```

##### Using Other Local LLM Servers
- **LM Studio**: Run with OpenAI-compatible API
- **vLLM**: Fast inference server
- **Custom endpoints**: Any OpenAI-compatible API

#### Option 2: OpenAI-Compatible APIs (Requires API Keys)

##### Lambda Labs Setup
1. Get API key from https://cloud.lambdalabs.com/
2. Add to `.env`:
```env
CUSTOM_LLM_ENDPOINT=https://api.lambda.ai/v1
CUSTOM_LLM_MODEL=llama-4-maverick-17b-128e-instruct-fp8
CUSTOM_LLM_API_KEY=your-lambda-api-key-here
```

##### Together AI Setup
1. Get API key from https://together.ai/
2. Add to `.env`:
```env
CUSTOM_LLM_ENDPOINT=https://api.together.xyz/v1
CUSTOM_LLM_MODEL=meta-llama/Llama-3.1-8B-Instruct
CUSTOM_LLM_API_KEY=your-together-api-key-here
```

##### Perplexity AI Setup
1. Get API key from https://www.perplexity.ai/
2. Add to `.env`:
```env
CUSTOM_LLM_ENDPOINT=https://api.perplexity.ai
CUSTOM_LLM_MODEL=llama-3.1-8b-instruct
CUSTOM_LLM_API_KEY=your-perplexity-api-key-here
```

#### Option 3: Commercial LLM (Fallback)

##### OpenAI Setup
1. Get API key from https://platform.openai.com/api-keys
2. Add to `.env`:
```env
OPENAI_API_KEY=sk-your-actual-key-here
```

##### Anthropic Setup
1. Get API key from https://console.anthropic.com/
2. Add to `.env`:
```env
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

##### Google Setup
1. Get API key from https://makersuite.google.com/app/apikey
2. Add to `.env`:
```env
GOOGLE_API_KEY=your-actual-key-here
```

### 5. Run the Application

#### Interactive Mode
```bash
promptlifter --interactive
# or
python -m promptlifter.main --interactive
```

#### Single Query Mode
```bash
promptlifter --query "Research quantum computing trends"
# or
python -m promptlifter.main --query "Research quantum computing trends"
```

### 6. Run Tests

```bash
# Run all tests
python run_tests.py

# Run specific tests
python run_tests.py config

# Run with pytest directly
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=promptlifter --cov-report=html
```

#### Save Results
```bash
python main.py --query "AI in healthcare" --save result.json
```

## 🚀 How It Works

1. **Query Input**: User provides a complex research query
2. **Subtask Decomposition**: GPT-4 breaks the query into 3-5 focused subtasks
3. **Parallel Research**: For each subtask:
   - Tavily performs web search
   - Pinecone searches internal knowledge base
   - Results are combined into a contextual prompt
4. **LLM Processing**: Custom/local LLMs generate expert-level responses for each subtask
5. **Final Compilation**: All subtask results are compiled into a structured final response

## 📊 Example Output

```
# Research Response: Write a research summary on quantum computing trends

## Summary

This research response addresses the query: "Write a research summary on quantum computing trends"

## Detailed Findings

### Current State of Quantum Computing Hardware
[Comprehensive analysis of current quantum hardware developments...]

### Key Research Papers and Breakthroughs
[Analysis of recent quantum computing research papers...]

### Open Questions and Future Directions
[Discussion of remaining challenges and future research directions...]

## Conclusion

The above findings provide a comprehensive analysis addressing the original research query...
```

## 🔍 Node Details

### `split_input.py`
- Uses custom/local LLMs to decompose complex queries into focused subtasks
- Ensures each subtask is specific and researchable

### `run_tavily_search.py`
- Performs web search using Tavily API
- Returns relevant content from recent web sources

### `run_pinecone_search.py`
- Searches internal knowledge base using Pinecone
- Leverages vector embeddings for semantic search
- **NEW**: Configurable relevance scoring and filtering
- **NEW**: Proper text embedding using multiple providers
- **NEW**: Similarity threshold filtering and score display

### `compose_contextual_prompt.py`
- Combines web and vector search results
- Creates structured prompts for LLM processing

### `run_subtask_llm.py`
- Processes contextual prompts with custom/local LLMs
- Generates expert-level research summaries

### `subtask_handler.py`
- Orchestrates parallel processing of all subtasks
- Manages async execution for optimal performance

### `gather_and_compile.py`
- Collects all subtask results
- Compiles into structured final response

## 🎯 Simplified Configuration

PromptLifter uses a simplified configuration approach that eliminates cascading fallbacks:

### **LLM Provider Configuration**
- **`LLM_PROVIDER`**: Choose one provider: `custom`, `openai`, `anthropic`, or `google`
- **`CUSTOM_LLM_ENDPOINT`**: Your custom LLM endpoint (e.g., Lambda Labs, Ollama)
- **`CUSTOM_LLM_MODEL`**: Model name for your custom endpoint

### **Embedding Provider Configuration**
- **`EMBEDDING_PROVIDER`**: Choose one provider: `custom`, `openai`, or `anthropic`
- **`EMBEDDING_MODEL`**: Specific embedding model to use (e.g., `text-embedding-3-small`)

### **Benefits of Simplified Configuration**
- ✅ **No cascading fallbacks**: Uses only the configured provider
- ✅ **Predictable behavior**: No unexpected provider switches
- ✅ **Better error handling**: Clear failure messages for the configured provider
- ✅ **Reduced complexity**: Easier to debug and configure

## 🎯 Relevance Scoring & Configuration

PromptLifter now includes advanced Pinecone relevance scoring with configurable parameters:

### **Similarity Threshold Filtering**
- Set `PINECONE_SIMILARITY_THRESHOLD` (0.0-1.0) to filter out low-relevance results
- Default: 0.7 (70% similarity required)
- Lower values = more results, higher values = higher quality

### **Score Display Options**
- Enable `PINECONE_INCLUDE_SCORES=true` to see similarity scores in results
- Format: `[Score: 0.892] Your search result content...`

### **Result Count Control**
- Configure `PINECONE_TOP_K` to control how many results to retrieve
- Default: 10 results
- Higher values = more comprehensive search

### **Smart Filtering**
- Enable `PINECONE_FILER_BY_SCORE=true` to automatically filter by threshold
- Provides summary of filtered vs. returned results

### **Multi-Provider Embeddings**
- Automatic fallback between embedding providers:
  1. Custom LLM (Ollama, etc.)
  2. OpenAI Embeddings
  3. Anthropic Embeddings
  4. Hash-based fallback

### **Embedding Optimization**

For optimal performance, use these recommended settings:

```env
# Embedding Configuration
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small

# Pinecone Search Configuration (Optimized)
PINECONE_SIMILARITY_THRESHOLD=0.2    # Lower threshold for better results
PINECONE_FILTER_BY_SCORE=true        # Keep filtering enabled
PINECONE_INCLUDE_SCORES=true         # Show scores for debugging
```

**Expected Results:**
- ✅ Most Pinecone results will be accepted
- ✅ Better hybrid search (web + vector)
- ✅ More comprehensive research responses
- ✅ Faster processing (no fallback embeddings)

## 🛠️ Configuration

The application uses environment variables for configuration:

**Primary (Custom LLMs):**
- `CUSTOM_LLM_ENDPOINT`: Your local LLM endpoint (default: http://localhost:11434 for Ollama)
- `CUSTOM_LLM_MODEL`: Your local model name (default: llama3.1)
- `CUSTOM_LLM_API_KEY`: Optional API key for custom endpoints

**Fallback (Commercial LLMs):**
- `OPENAI_API_KEY`: Your OpenAI API key
- `ANTHROPIC_API_KEY`: Your Anthropic API key
- `GOOGLE_API_KEY`: Your Google API key

**Search and Vector:**
- `TAVILY_API_KEY`: Your Tavily search API key
- `PINECONE_API_KEY`: Your Pinecone API key
- `PINECONE_INDEX`: Your Pinecone index name
- `PINECONE_NAMESPACE`: Your Pinecone namespace (default: research)

**Pinecone Search Configuration:**
- `PINECONE_TOP_K`: Number of results to retrieve (default: 10)
- `PINECONE_SIMILARITY_THRESHOLD`: Minimum similarity score 0.0-1.0 (default: 0.7)
- `PINECONE_INCLUDE_SCORES`: Include similarity scores in output (true/false)
- `PINECONE_FILTER_BY_SCORE`: Filter results by similarity threshold (true/false)

## 🔧 Troubleshooting

### Search Issues

If you're experiencing search-related problems, use these debugging tools:

#### 1. Run the Debug Script
```bash
python debug_search.py
```
This will check your configuration and test both search services.

#### 2. Interactive Configuration Fixer
```bash
python fix_search_config.py
```
This interactive script helps you set up your API keys and configuration properly.

#### Common Issues and Solutions

**Tavily 401 Error:**
- Get a free API key from [Tavily](https://tavily.com/)
- Add to `.env`: `TAVILY_API_KEY=your-key-here`

**Pinecone Connection Issues:**
- Get a free API key from [Pinecone](https://www.pinecone.io/)
- Create an index in your Pinecone dashboard
- Add to `.env`:
  ```
  PINECONE_API_KEY=your-key-here
  PINECONE_INDEX=your-index-name
  ```

**No Search Results:**
- Lower the similarity threshold: `PINECONE_SIMILARITY_THRESHOLD=0.3`
- Disable filtering: `PINECONE_FILTER_BY_SCORE=false`
- Check if your Pinecone index has data

**Timeout Errors:**
- Increase timeout values in the code
- Check your internet connection
- Verify API service status

### Logging

Enable detailed logging to debug issues:
```python
import logging
logging.basicConfig(level=logging.INFO)
```

## 📦 Development & Release

### For Developers

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run quality checks
tox

# Run tests
pytest tests/ -v

# Format code
black promptlifter tests
```

### For Contributors

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for detailed development guidelines.

### Release Process

```bash
# Setup PyPI credentials
python scripts/setup_pypi.py

# Test release to TestPyPI
python scripts/release.py test

# Release to PyPI
python scripts/release.py release
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for detailed guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [LangGraph](https://github.com/langchain-ai/langgraph) for workflow orchestration
- [Ollama](https://ollama.ai/) for local LLM deployment
- [Meta](https://ai.meta.com/) for Llama models
- [Tavily](https://tavily.com/) for web search capabilities
- [Pinecone](https://www.pinecone.io/) for vector search infrastructure 