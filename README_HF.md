# Alex - Product Manager AI Agent

A sophisticated AI-powered product management assistant that helps with market research, deep analysis, and feature development.

## Features

- **Market Research**: Comprehensive market and competitive analysis
- **Deep Research**: AI-powered research with multiple search strategies
- **Feature Development**: Create detailed product feature specifications
- **Conversational Interface**: Natural language interaction with context awareness

## How to Use

1. **Start a Conversation**: Type your product idea or question in the chat interface
2. **Research Phase**: Alex will conduct market research and analysis
3. **Feature Development**: After research, Alex can help create detailed feature specifications
4. **Iterative Refinement**: Work with Alex to refine and improve your product concepts

## Environment Variables

Set these in your Hugging Face Spaces secrets:

- `OPENAI_API_KEY`: Your OpenAI API key for AI functionality
- `SENDGRID_API_KEY`: (Optional) For email notifications
- `SERPAPI_API_KEY`: (Optional) For enhanced web search capabilities

## Technical Details

- Built with Gradio for the web interface
- Uses OpenAI Agents framework for AI capabilities
- Supports async operations for better performance
- Modular architecture with specialized agents for different tasks

## File Structure

- `app.py`: Main application entry point
- `deep_research.py`: Original application (for reference)
- `research_manager.py`: Manages the research workflow
- `feature_agent.py`: Handles feature development
- `planner_agent.py`: Plans research strategies
- `search_agent.py`: Performs web searches
- `writer_agent.py`: Generates reports
- `email_agent.py`: Sends email notifications
- `query_clarifying_agent.py`: Asks clarifying questions

## Deployment

This application is designed to run on Hugging Face Spaces. Simply upload the files and set the required environment variables.
