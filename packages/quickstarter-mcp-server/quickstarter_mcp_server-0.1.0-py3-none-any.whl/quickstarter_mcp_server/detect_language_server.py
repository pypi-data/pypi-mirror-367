from mcp.server.fastmcp import FastMCP
from .guidelines import LANGUAGE_PATTERNS, LANGUAGE_KEYWORDS, LANGUAGE_INFO
import re
import os

mcp = FastMCP("language_detection_server")

@mcp.tool()
def get_language_info(language: str) -> str:
    if language in LANGUAGE_INFO:
        info = LANGUAGE_INFO[language]
        info_text = f"""
        - Language Information: {info['name']} ({info['english_name']})
        - Writing System: {info['writing_system']}
        - Formality: {info['formality']}
        - Cultural Notes: {info['cultural_notes']}
        This information can help you communicate more effectively in {info['english_name']}.
        """.strip()
        return info_text
    else:
        return f"❌ Language information not available for: {language}"


@mcp.tool()
def detect_language(text: str) -> str:
    if not text:
        return "korean"
    
    text_lower = text.lower()
    scores = {}
    
    for lang, pattern in LANGUAGE_PATTERNS.items():
        matches = len(pattern.findall(text))
        if matches > 0:
            scores[lang] = scores.get(lang, 0) + matches * 3
    
    for lang, keywords in LANGUAGE_KEYWORDS.items():
        keyword_count = sum(1 for keyword in keywords if keyword in text_lower)
        if keyword_count > 0:
            scores[lang] = scores.get(lang, 0) + keyword_count
    
    if 'chinese' in scores and 'japanese' in scores:
        japanese_chars = len(re.findall(r'[ひらがなカタカナ]', text))
        if japanese_chars > 0:
            scores['japanese'] += japanese_chars * 2
        chinese_keywords = sum(1 for kw in LANGUAGE_KEYWORDS.get('chinese', []) if kw in text)
        if chinese_keywords > 0:
            scores['chinese'] += chinese_keywords * 2
    
    if scores:
        detected = max(scores, key=scores.get)
        return detected
    
    return "english"
    

def main():
    print("Starting MCP server...")
    mcp.run(transport="streamable-http") 


if __name__ == "__main__":
    main()