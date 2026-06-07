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

## Usage

- Paste your source code or upload a file
- Click **Analyze Code**
- View the review fields and optimized best version

## Notes

- If no OpenAI key is available, the app uses a local analysis engine.
- The review output is limited to the requested fields only.
