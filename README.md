# Alex - AI Product Manager

A Streamlit application featuring an AI-powered Product Manager that helps with market research and feature development.

## 🌐 Live Demo

**Try the app online**: [https://alexpmassistant.streamlit.app/](https://alexpmassistant.streamlit.app/)

## Features

- 🔍 **Market Research**: Conduct comprehensive market research and analysis
- 📊 **Deep Research**: In-depth product assessment and competitive analysis  
- ✍️ **Feature Development**: Generate structured MVP feature definitions
- 🤖 **AI-Powered**: Powered by OpenAI's GPT models for intelligent conversations

## Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd HF_MVP
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env_example.txt .env
   # Edit .env with your OpenAI API key
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

### Streamlit Cloud Deployment

1. **Fork this repository**
2. **Go to [Streamlit Cloud](https://share.streamlit.io)**
3. **Connect your GitHub account**
4. **Deploy the app** using this repository

## Environment Variables

Create a `.env` file with the following variables:

```env
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional
SENDGRID_API_KEY=your_sendgrid_api_key_here
SERPAPI_API_KEY=your_serpapi_key_here
FROM_EMAIL=your_email@example.com
TO_EMAIL=recipient@example.com
```

## How It Works

1. **Research Phase**: Alex conducts market research and analysis
2. **Feature Phase**: When ready, Alex generates structured MVP feature definitions
3. **Template Format**: Each feature follows a comprehensive template with:
   - User Flow
   - Technical Scope (MVP)
   - Acceptance Criteria
   - Workflow Inspiration
   - Success Metrics

## Project Structure

```
HF_MVP/
├── app.py                 # Main Streamlit application
├── feature_agent.py       # Feature definition agent
├── research_manager.py    # Research management
├── requirements.txt       # Python dependencies
├── env_example.txt        # Environment variables template
└── README.md             # This file
```

## Requirements

- Python 3.8+
- OpenAI API key
- Streamlit

## License

MIT License