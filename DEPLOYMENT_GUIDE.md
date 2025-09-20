# Hugging Face Spaces Deployment Guide

## Quick Start

1. **Create a new Space on Hugging Face**
   - Go to https://huggingface.co/new-space
   - Choose "Gradio" as the SDK
   - Name your space (e.g., "alex-product-manager")

2. **Upload Files**
   - Upload all files from this directory to your Space
   - Make sure `app.py` is in the root directory

3. **Set Environment Variables**
   - Go to Settings → Secrets in your Space
   - Add the following secrets:
     - `OPENAI_API_KEY`: Your OpenAI API key (required)
     - `SENDGRID_API_KEY`: For email notifications (optional)
     - `SERPAPI_API_KEY`: For enhanced search (optional)

4. **Deploy**
   - The Space will automatically build and deploy
   - Check the logs for any errors

## File Structure for HF Spaces

```
your-space/
├── app.py                    # Main entry point
├── requirements.txt          # Python dependencies
├── README.md                 # Space description
├── research_manager.py       # Research workflow
├── feature_agent.py         # Feature development
├── planner_agent.py         # Research planning
├── search_agent.py          # Web search
├── writer_agent.py          # Report generation
├── email_agent.py           # Email notifications
├── query_clarifying_agent.py # Question generation
└── deep_research.py         # Original app (reference)
```

## Environment Variables

### Required
- `OPENAI_API_KEY`: Your OpenAI API key for AI functionality

### Optional
- `SENDGRID_API_KEY`: For sending email reports
- `SERPAPI_API_KEY`: For enhanced web search capabilities

## Testing Locally

Before deploying, you can test locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-key-here"

# Run the test script
python test_app.py

# Run the application
python app.py
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Make sure all Python files are uploaded
   - Check that `requirements.txt` includes all dependencies

2. **API Key Issues**
   - Verify your OpenAI API key is set correctly
   - Check that the key has sufficient credits

3. **Memory Issues**
   - The application uses async operations which should be memory efficient
   - If you encounter memory issues, consider reducing the number of concurrent operations

4. **Timeout Issues**
   - Some operations (like research) can take time
   - The UI will show progress indicators during long operations

### Debug Mode

To enable debug logging, set `debug=True` in the `ui.launch()` call in `app.py`.

## Customization

### UI Customization
- Modify the HTML templates in `app.py` to change the appearance
- Update the theme by changing `gr.themes.Default(primary_hue="sky")`

### Agent Behavior
- Modify agent instructions in their respective files
- Adjust conversation flow in `Assistant_conversation()` function

### Adding New Features
- Create new agent files following the existing pattern
- Add new tools using the `@function_tool` decorator
- Update the conversation flow to include new agents

## Performance Optimization

1. **Caching**: Consider adding caching for repeated queries
2. **Rate Limiting**: Implement rate limiting for API calls
3. **Error Handling**: Add more robust error handling for production use

## Security Considerations

1. **API Keys**: Never commit API keys to version control
2. **Input Validation**: Validate user inputs before processing
3. **Rate Limiting**: Implement rate limiting to prevent abuse
4. **Error Messages**: Don't expose sensitive information in error messages

## Monitoring

- Check the Space logs regularly for errors
- Monitor API usage and costs
- Set up alerts for critical failures

## Support

If you encounter issues:
1. Check the Space logs
2. Run the test script locally
3. Verify all environment variables are set
4. Check the Hugging Face Spaces documentation
