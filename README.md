# Multi-Agent Research System

A sophisticated multi-agent system that performs deep research and synthesis using LLM-powered agents and the Tavily search API.

## System Architecture

```
Deep Research/
├── agents/
│   ├── __init__.py
│   ├── research_agent.py   # Handles search and data collection
│   └── synthesis_agent.py  # Processes and synthesizes research
├── utils/
│   ├── __init__.py
│   └── llm_setup.py       # LLM configuration utilities
├── config.py              # System configuration
├── main.py               # CLI interface
├── requirements.txt      # Dependencies
└── .env                 # Environment variables (not tracked)
```

## Key Features

- **Dual-Agent Architecture**: Separate agents for research and synthesis
- **Flexible Search Depth**: Configurable search depth (basic/advanced)
- **Secure Configuration**: Environment-based secure configuration using Pydantic
- **Modern LLM Integration**: Uses Gemini model via LangChain's latest patterns
- **Structured Output**: JSON-formatted results with proper timestamps
- **Robust Error Handling**: Comprehensive error handling and logging
- **CLI Interface**: User-friendly command-line interface using Typer

## Technical Highlights

1. **Advanced LLM Integration**
   - Uses LangChain's latest RunnableSequence pattern
   - Implements ChatPromptTemplate for structured prompting
   - Configurable model parameters (temperature, top_p, top_k)

2. **Secure Configuration**
   - Pydantic-based settings management
   - SecretStr for API key handling
   - Environment-based configuration

3. **Robust Search Implementation**
   - Integration with Tavily API
   - Configurable search depth
   - Rate limiting and error handling

4. **Result Processing**
   - Structured JSON output
   - UTC timestamp standardization
   - Automated result storage

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/deep_research.git
cd deep_research

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

## Usage

```bash
# Basic search
python main.py "Your research query" --depth basic

# Advanced search with debug output
python main.py "Your research query" --depth advanced --debug
```

## Security Notes

- API keys are stored securely using Pydantic's SecretStr
- .env file is excluded from version control
- Results are stored with proper access controls

## Future Enhancements

1. Integration with additional search APIs
2. Enhanced result caching system
3. Web interface implementation
4. Result visualization capabilities
5. Multi-language support

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
