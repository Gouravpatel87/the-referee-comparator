# Project Structure & Organization

## Directory Layout

```
the-referee-comparator/
├── app.py              # Main Streamlit application (single-file architecture)
├── requirements.txt    # Python dependencies
├── README.md          # Basic project documentation
├── SPEC.md            # Detailed product specification
└── venv/              # Python virtual environment (local development)
```

## File Responsibilities

### `app.py` - Main Application
- **Single-file architecture**: All application logic in one file
- **Streamlit components**: UI layout, user inputs, data display
- **API integration**: AWS Price List API calls with caching
- **Business logic**: Pricing calculations and comparisons
- **Data presentation**: Tables, charts, and formatted output

### `requirements.txt` - Dependencies
- Minimal dependency list (streamlit, pandas, requests)
- No version pinning currently - uses latest compatible versions

### `SPEC.md` - Product Specification
- Comprehensive product requirements and technical specifications
- User stories and implementation phases
- Data models and API integration details

### `README.md` - Basic Documentation
- Quick start instructions
- Project context (Week 6 AI for Bharat project)

## Code Organization Patterns

### Streamlit Layout Structure
1. **Page configuration** (`st.set_page_config`)
2. **Title and description**
3. **Sidebar controls** (region selector, mode selector)
4. **Cached functions** (pricing data fetching)
5. **Main content area** (comparison tables and analysis)
6. **Footer information**

### Function Organization
- **Caching functions**: Prefixed with `@st.cache_data`
- **Helper functions**: Inline within main execution flow
- **Data processing**: Pandas DataFrames for tabular display

## Development Conventions

### File Naming
- Single main file approach (`app.py`)
- Standard Python naming conventions
- Configuration files in root directory

### Code Style
- Functional programming approach
- Streamlit-first design patterns
- Inline comments for complex pricing logic
- Clear variable naming for pricing calculations

### Data Flow
1. User input via Streamlit widgets
2. Cached API calls for live pricing
3. Calculation functions for cost estimates
4. DataFrame creation for tabular display
5. Streamlit components for output rendering