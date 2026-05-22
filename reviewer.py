import json
import os
import re
from typing import Dict, Optional

try:
    import openai
    _OPENAI_AVAILABLE = True
except ImportError:
    _OPENAI_AVAILABLE = False

try:
    import requests
    _REQUESTS_AVAILABLE = True
except ImportError:
    _REQUESTS_AVAILABLE = False

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

_LANGUAGE_EXTENSIONS = {
    ".py": "Python",
    ".c": "C",
    ".cpp": "C++",
    ".cc": "C++",
    ".h": "C/C++",
    ".java": "Java",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".go": "Go",
}


def has_openai_key() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))


def has_groq_key() -> bool:
    return bool(os.getenv("GROQ_API_KEY"))


def review_code(code: str, filename: Optional[str] = None) -> Dict[str, str]:
    if has_groq_key() and _REQUESTS_AVAILABLE:
        try:
            return groq_review(code, filename)
        except Exception:
            pass
    if has_openai_key() and _OPENAI_AVAILABLE:
        try:
            return openai_review(code, filename)
        except Exception:
            pass
    return simple_review(code, filename)


def openai_review(code: str, filename: Optional[str] = None) -> Dict[str, str]:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    system_message = (
        "You are a precise code reviewer. Review the submitted code and return valid JSON only. "
        "Do not include explanations outside the JSON object. "
        "The JSON object must include these keys: language, time_complexity, space_complexity, score, best_version."
    )
    user_message = (
        f"Analyze the following code and return only JSON with keys language, time_complexity, space_complexity, score, best_version."
        f"\nFilename: {filename or 'unknown'}\n\n{code}"
    )
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ],
        temperature=0,
        max_tokens=500,
    )
    content = _extract_json(response.choices[0].message.content)
    return json.loads(content)


def groq_review(code: str, filename: Optional[str] = None) -> Dict[str, str]:
    api_key = os.getenv("GROQ_API_KEY")
    endpoint = "https://api.groq.com/v1/models/groq-llm-preview/complete"
    prompt = (
        "You are a precise code reviewer. Review the submitted code and return valid JSON only. "
        "Do not include explanations outside the JSON object. "
        "The JSON object must include these keys: language, time_complexity, space_complexity, score, best_version.\n\n"
        f"Filename: {filename or 'unknown'}\n\n{code}"
    )
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "prompt": prompt,
        "max_output_tokens": 500,
        "temperature": 0,
    }
    response = requests.post(endpoint, headers=headers, json=payload, timeout=20)
    response.raise_for_status()
    data = response.json()
    content = data.get("completion") or data.get("text") or ""
    if not content and isinstance(data.get("output"), list):
        output = data["output"]
        if output and isinstance(output[0], dict):
            content = output[0].get("content", [{}])[0].get("text", "")
    content = _extract_json(content)
    return json.loads(content)


def _extract_json(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    json_start = text.find("{")
    json_end = text.rfind("}")
    if json_start != -1 and json_end != -1:
        return text[json_start: json_end + 1]
    return text


def simple_review(code: str, filename: Optional[str] = None) -> Dict[str, str]:
    language = detect_language(code, filename)
    time_complexity = estimate_time_complexity(code)
    space_complexity = estimate_space_complexity(code)
    score = estimate_score(time_complexity, space_complexity, code)
    best_version = generate_best_version(code, language)
    return {
        "language": language,
        "time_complexity": time_complexity,
        "space_complexity": space_complexity,
        "score": str(score),
        "best_version": best_version,
    }


def detect_language(code: str, filename: Optional[str] = None) -> str:
    if filename:
        ext = os.path.splitext(filename)[1].lower()
        if ext in _LANGUAGE_EXTENSIONS:
            return _LANGUAGE_EXTENSIONS[ext]
    patterns = [
        (r"\bimport\b|\bdef\b|\bprint\(|\bfrom\b", "Python"),
        (r"#include\b|\bprintf\(|\bscanf\(|\bmalloc\b", "C"),
        (r"std::|using namespace std|\bcout\b|\bcin\b", "C++"),
        (r"System\.out\.println|public static void main|class .*\{", "Java"),
        (r"console\.log|function\b|var\b|let\b|const\b", "JavaScript"),
    ]
    for pattern, lang in patterns:
        if re.search(pattern, code):
            return lang
    return "Unknown"


def estimate_time_complexity(code: str) -> str:
    code = code.lower()
    loops = len(re.findall(r"\bfor\b|\bwhile\b", code))
    nested = bool(re.search(r"\b(for|while)\b[\s\S]{1,120}?\b(for|while)\b", code))
    recursion = bool(re.search(r"def\s+(\w+)\(|function\s+(\w+)\(|\b(\w+)\s*\([^\)]*\):", code) and re.search(r"\b(\w+)\s*\([^\)]*\)", code))
    if nested or re.search(r"\bfor\b[\s\S]{1,120}?\bfor\b", code):
        return "O(n^2)"
    if recursion and re.search(r"\breturn\b.*\b(\w+)\s*\(", code):
        return "O(2^n)" if re.search(r"\b(1<<|2\^n|pow\(2|2\*2\)|fib|factorial)\b", code) else "O(n)"
    if loops >= 1:
        return "O(n)"
    if re.search(r"\blog\b|\bexp\b|\bpow\(|\bmath\.log\b", code):
        return "O(log n)"
    return "O(1)"


def estimate_space_complexity(code: str) -> str:
    if re.search(r"\b(vector|list|dict|map|set|array|malloc|new|std::vector)\b", code, re.IGNORECASE):
        return "O(n)"
    if re.search(r"\breturn\b.*\b(\w+)\s*\(", code) and re.search(r"\bdef\b|\bfunction\b", code):
        return "O(n)"
    return "O(1)"


def estimate_score(time_complexity: str, space_complexity: str, code: str) -> int:
    score = 90
    if time_complexity in {"O(n^2)", "O(2^n)"}:
        score -= 25
    elif time_complexity == "O(n)":
        score -= 5
    elif time_complexity == "O(log n)":
        score += 3
    if space_complexity == "O(n)":
        score -= 5
    line_count = len([line for line in code.splitlines() if line.strip()])
    if line_count > 40:
        score -= min(20, (line_count - 40) // 2)
    return max(40, min(100, score))


def generate_best_version(code: str, language: str) -> str:
    code = code.strip()
    if language == "Python":
        one_line_assignments = re.findall(r"^([a-zA-Z_][\w]*)\s*=\s*([^\n]+)$", code, re.MULTILINE)
        if one_line_assignments and len(one_line_assignments) <= 4 and all(re.match(r"^\s*\d+\s*$", value) for _, value in one_line_assignments):
            names = ", ".join(name for name, _ in one_line_assignments)
            values = ", ".join(value.strip() for _, value in one_line_assignments)
            lines = [f"{names} = {values}"]
            rest = [line for line in code.splitlines() if not re.match(r"^([a-zA-Z_][\w]*)\s*=\s*\d+\s*$", line)]
            lines.extend(rest)
            return "\n".join(lines).strip()
    return code
