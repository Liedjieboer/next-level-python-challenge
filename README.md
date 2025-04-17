# World Population Analysis Tool

This Python tool analyzes world population data using the World Population API. It demonstrates various Python programming concepts including:

- Concurrent programming with async/await
- Type annotations
- Iterators and generators
- Data processing pipelines
- Data visualization with Streamlit

## Features

- Asynchronous API data retrieval
- Population trend analysis
- Data visualization dashboard
- Memory-efficient data processing
- Rate-limited API requests

## Installation

1. Clone this repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the Streamlit dashboard:
```bash
streamlit run src/dashboard.py
```

## Project Structure

- `src/` - Source code
  - `api.py` - API client and data retrieval
  - `analysis.py` - Data analysis functions
  - `dashboard.py` - Streamlit dashboard
  - `utils.py` - Utility functions
- `data/` - Data storage
- `tests/` - Test files 