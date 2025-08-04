# AgentFather

A comprehensive AI agent framework with email, file, and voice processing capabilities built on top of LangChain.

## Features

- 🤖 **AI Agent Framework**: Built on LangChain for intelligent automation
- 📧 **Email Processing**: Advanced email handling and automation
- 📁 **File Management**: Comprehensive file operations and processing
- 🎤 **Voice Processing**: Speech recognition and text-to-speech capabilities
- 🔧 **Modular Design**: Easy to extend and customize
- 🚀 **Production Ready**: Includes testing, documentation, and deployment tools

## Installation

### From PyPI (Recommended)

```bash
pip install agentfather
```

### From Source

```bash
git clone https://github.com/yourusername/agentfather.git
cd agentfather
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/yourusername/agentfather.git
cd agentfather
pip install -e ".[dev,test,docs]"
```

## Quick Start

### Basic Usage

```python
from agentfather import AgentFather

# Initialize the agent
agent = AgentFather()

# Process an email
result = agent.process_email("user@example.com", "Hello, I need help with my order")

# Process a file
result = agent.process_file("document.pdf")

# Process voice input
result = agent.process_voice("audio.wav")
```

### Command Line Interface

```bash
# Run the agent interactively
agentfather

# Process specific tasks
agentfather email --input "user@example.com"
agentfather file --input "document.pdf"
agentfather voice --input "audio.wav"
```

## Project Structure

```
agentfather/
├── agentfather/              # Main package
│   ├── __init__.py
│   ├── core/                 # Core functionality
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   └── config.py
│   ├── email/                # Email processing
│   │   ├── __init__.py
│   │   ├── email_functions.py
│   │   └── Email.py
│   ├── files/                # File processing
│   │   ├── __init__.py
│   │   ├── path_functions.py
│   │   └── path.py
│   ├── voice/                # Voice processing
│   │   ├── __init__.py
│   │   ├── voice_functions.py
│   │   ├── Vosk.py
│   │   └── eleven_labs.py
│   ├── utils/                # Utilities
│   │   ├── __init__.py
│   │   ├── langchain_imports.py
│   │   ├── rag_functions.py
│   │   └── file_functions.py
│   └── cli.py                # Command line interface
├── DummyData/                # Sample data
├── tests/                    # Test suite
├── docs/                     # Documentation
├── setup.py                  # Package setup
├── pyproject.toml           # Modern package configuration
├── README.md                # This file
├── LICENSE                  # License file
├── CHANGELOG.md             # Version history
├── .gitignore               # Git ignore rules
├── requirements.txt         # Dependencies
├── requirements-dev.txt     # Development dependencies
└── MANIFEST.in              # Package manifest
```

## Configuration

Create a `.env` file in your project root:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password

# Voice Configuration
ELEVENLABS_API_KEY=your_elevenlabs_api_key
VOSK_MODEL_PATH=/path/to/vosk/model

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost/dbname

# Redis Configuration
REDIS_URL=redis://localhost:6379
```

## Usage Examples

### Email Processing

```python
from agentfather.email import EmailProcessor

processor = EmailProcessor()

# Process incoming emails
emails = processor.fetch_emails()
for email in emails:
    response = processor.process_email(email)
    processor.send_response(email.sender, response)
```

### File Processing

```python
from agentfather.files import FileProcessor

processor = FileProcessor()

# Process different file types
processor.process_pdf("document.pdf")
processor.process_docx("document.docx")
processor.process_image("image.png")
```

### Voice Processing

```python
from agentfather.voice import VoiceProcessor

processor = VoiceProcessor()

# Speech to text
text = processor.speech_to_text("audio.wav")

# Text to speech
processor.text_to_speech("Hello, world!", "output.wav")
```

### RAG (Retrieval-Augmented Generation)

```python
from agentfather.utils import RAGProcessor

rag = RAGProcessor()

# Add documents to knowledge base
rag.add_documents(["doc1.pdf", "doc2.txt"])

# Query the knowledge base
response = rag.query("What is the main topic?")
```

## Development

### Setting up Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/agentfather.git
cd agentfather

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev,test,docs]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=agentfather

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m "not slow"
```

### Code Quality

```bash
# Format code
black agentfather/
isort agentfather/

# Lint code
flake8 agentfather/
mypy agentfather/

# Security check
bandit -r agentfather/
safety check
```

### Building Documentation

```bash
# Build docs
cd docs
make html

# Serve docs locally
python -m http.server 8000
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Write comprehensive tests for new features
- Update documentation for any API changes
- Use type hints for all function parameters and return values
- Write clear commit messages

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📧 Email: support@agentfather.com
- 💬 Discord: [Join our community](https://discord.gg/agentfather)
- 📖 Documentation: [Read the docs](https://agentfather.readthedocs.io/)
- 🐛 Issues: [Report a bug](https://github.com/yourusername/agentfather/issues)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes and version history.

## Acknowledgments

- [LangChain](https://github.com/langchain-ai/langchain) for the AI framework
- [OpenAI](https://openai.com/) for language models
- [ElevenLabs](https://elevenlabs.io/) for voice synthesis
- [Vosk](https://alphacephei.com/vosk/) for speech recognition

## Roadmap

- [ ] Web UI interface
- [ ] Mobile app support
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Plugin system
- [ ] Cloud deployment templates
- [ ] Enterprise features 