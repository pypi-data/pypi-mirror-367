import re


LANGUAGE_PATTERNS = {
    'korean': re.compile(r'[가-힣]'),                    
    'english': re.compile(r'[a-zA-Z]'),                  
    'chinese': re.compile(r'[一-龯]'),                   
    'japanese': re.compile(r'[ひらがなカタカナ一-龯]'),    
    'russian': re.compile(r'[а-я ё]', re.IGNORECASE),    
    'thai': re.compile(r'[ก-๙]'),                       
}

LANGUAGE_KEYWORDS = {
    'korean': [
        '안녕', '하세요', '입니다', '습니다', '있습니다', '에서', '그리고', '하지만',
        '때문에', '것입니다', '수있습니다', '되었습니다', '이것', '저것', '무엇',
        '이다', '하다', '되다', '있다', '없다', '같다', '다른', '많다', '적다'
    ],
    'english': [
        'hello', 'thank you', 'not', 'can', 'what', 'how', 'this', 'that', 'we',
        'they', 'when', 'where', 'because', 'so', 'but', 'if', 'or', 'should',
        'thank you', 'this', 'that', 'when', 'should', 'problem', 'no', 'compare', 'very'
    ],
    'chinese': [
        '你好', '谢谢', '不是', '可以', '什么', '怎么', '这个', '那个', '我们',
        '他们', '时候', '地方', '因为', '所以', '但是', '如果', '或者', '应该',
        '謝謝', '這個', '那個', '時候', '應該', '問題', '沒有', '比較', '非常'
    ],
    'japanese': [
        'こんにちは', 'ありがとう', 'です', 'ます', 'でした', 'ました', 'だった',
        'という', 'ている', 'ください', 'すみません', 'はじめまして', 'よろしく',
        'コンピュータ', 'システム', 'サービス', 'ユーザー', 'データ', 'ファイル',
        '時間', '問題', '方法', '場合', '必要', '可能', '重要', '簡単', '便利'
    ],
    'russian': [
        'привет', 'спасибо', 'пожалуйста', 'извините', 'здравствуйте', 'хорошо',
        'плохо', 'очень', 'много', 'мало', 'большой', 'маленький', 'новый', 'старый',
        'это', 'что', 'как', 'где', 'когда', 'почему', 'который', 'может',
        'быть', 'иметь', 'делать', 'говорить', 'идти', 'видеть', 'знать', 'думать'
    ],
    'thai': [
        'สวัสดี', 'ขอบคุณ', 'ขอโทษ', 'ครับ', 'ค่ะ', 'แล้ว', 'ได้', 'ไม่', 'มาก', 'น้อย',
        'ใหญ่', 'เล็ก', 'ดี', 'เสีย', 'อะไร', 'ที่ไหน', 'เมื่อไหร่', 'ทำไม', 'อย่างไร',
        'เป็น', 'มี', 'ทำ', 'พูด', 'ไป', 'เห็น', 'รู้', 'คิด', 'ใช้', 'เอา'
    ]
}

LANGUAGE_INFO = {
    "korean": {
        "name": "한국어",
        "english_name": "Korean", 
        "formality": "Uses honorifics (존댓말/반말)",
        "writing_system": "Hangul (한글)",
        "cultural_notes": "Respect hierarchy, use appropriate honorifics, indirect communication preferred",
        "greetings": ["안녕하세요", "반갑습니다", "처음 뵙겠습니다"],
        "polite_endings": ["-습니다", "-세요", "-시겠습니까"]
    },
    "english": {
        "name": "English",
        "english_name": "English",
        "formality": "Moderate formality spectrum (formal/informal distinction)",
        "writing_system": "Latin alphabet (A-Z, a-z)",
        "cultural_notes": "Direct communication style, individualistic, value efficiency and clarity",
        "greetings": ["Hello", "Hi", "Good morning", "Good afternoon", "Good evening"],
        "polite_phrases": ["Please", "Thank you", "You're welcome", "Excuse me", "I'm sorry"]
    },
    "chinese": {
        "name": "中文",
        "english_name": "Chinese",
        "formality": "Formal vs informal registers, 您/你 distinction",
        "writing_system": "Simplified/Traditional Chinese characters (汉字/漢字)",
        "cultural_notes": "Context-dependent politeness, harmony-oriented communication",
        "greetings": ["你好", "您好", "早上好", "晚上好"],
        "polite_phrases": ["请", "谢谢", "不客气", "对不起"]
    },
    "japanese": {
        "name": "日本語",
        "english_name": "Japanese",
        "formality": "Complex keigo system (敬語): 尊敬語, 謙譲語, 丁寧語", 
        "writing_system": "Hiragana (ひらがな), Katakana (カタカナ), Kanji (漢字)",
        "cultural_notes": "Extremely polite, indirect communication, reading the atmosphere (空気を読む)",
        "greetings": ["こんにちは", "はじめまして", "よろしくお願いします"],
        "polite_endings": ["-です", "-ます", "-ております"]
    },
    "russian": {
        "name": "Русский",
        "english_name": "Russian",
        "formality": "Formal (Вы) vs informal (ты), patronymic names important",
        "writing_system": "Cyrillic alphabet (Кириллица)",
        "cultural_notes": "Direct communication, appreciate intellectual discussions, formal introductions",
        "greetings": ["Здравствуйте", "Привет", "Доброе утро", "Добрый день"],  # ← 수정
        "polite_phrases": ["Пожалуйста", "Спасибо", "Извините", "Простите"]
    },
    "thai": {
        "name": "ภาษาไทย",
        "english_name": "Thai",
        "formality": "Polite particles (ครับ/ค่ะ), royal/religious language levels",
        "writing_system": "Thai alphabet (อักษรไทย), no spaces between words",
        "cultural_notes": "Very polite society, smile culture, avoid confrontation, respect for elders",
        "greetings": ["สวัสดี", "สบายดีไหม", "ยินดีที่ได้รู้จัก"],
        "polite_phrases": ["ครับ", "ค่ะ", "นะครับ", "นะค่ะ"]  # ← polite_particles → polite_phrases로 통일
    }
}
