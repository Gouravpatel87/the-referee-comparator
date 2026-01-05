# Technology Stack & Development Guide

## Tech Stack

### Core Framework
- **Streamlit**: Python web framework for rapid prototyping and data applications
- **Python 3.x**: Primary programming language

### Key Libraries
- **pandas**: Data manipulation and analysis
- **requests**: HTTP library for API integration
- **json**: JSON data handling (built-in)

### External APIs
- **AWS Price List API**: Live pricing data (public, no authentication required)
  - Base URL: `https://pricing.us-east-1.amazonaws.com`
  - 24-hour caching implemented to avoid rate limits
  - Graceful fallback to known pricing when API fails

## Development Commands

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Or with virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Running the Application
```bash
# Start development server
streamlit run app.py

# The app will be available at http://localhost:8501
```

### Development Notes
- No build step required - Streamlit runs directly from Python source
- Hot reload enabled by default in development
- No testing framework currently configured

## Architecture Patterns

### Caching Strategy
- Use `@st.cache_data(ttl=86400)` for API responses (24-hour TTL)
- Implement fallback pricing when external APIs fail
- Cache at function level for pricing data

### Error Handling
- Always provide fallback values for pricing data
- Use try/catch blocks around external API calls
- Display user-friendly warnings when live data unavailable

### Code Organization
- Single-file application structure (`app.py`)
- Functional programming approach
- Streamlit components organized top-to-bottom in execution order