# AI Code Reviewer

A simple Streamlit-based AI code reviewer for Python, C, C++, Java, JavaScript, and other languages.

## Features

- Paste or upload code to review
- Detects language automatically
- Returns:
  - language
  - time complexity
  - space complexity
  - score
  - best version of the code
- Clean, professional UI with no database required
- Optional OpenAI integration for richer review output

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. (Optional) Create a `.env` file at the project root or set a Groq/OpenAI key in the environment.

Create `.env`:

```bash
GROQ_API_KEY=your_groq_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

or set directly in your shell:

```bash
set GROQ_API_KEY=your_groq_api_key_here
```

```bash
set OPENAI_API_KEY=your_openai_api_key_here
```

3. Run the app:

```bash
streamlit run streamlit_app.py
```

## Usage

- Paste your source code or upload a file
- Click **Analyze Code**
- View the review fields and optimized best version

## Notes

- If no OpenAI key is available, the app uses a local analysis engine.
- The review output is limited to the requested fields only.
