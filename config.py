"""
Конфигурация Vibe Assistant для Poznay Sebya
"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
# API Keys
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')  # для DeepSeek через OpenRouter

# Модели
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o')
OPENROUTER_MODEL = os.getenv('OPENROUTER_MODEL', 'deepseek/deepseek-r1-0528:free')

# Для обратной совместимости
MODEL = OPENAI_MODEL
TEMPERATURE = 0.8  # creative для контента
MAX_TOKENS = 500  # для OpenAI
MAX_TOKENS_OPENROUTER = 4000  # для DeepSeek R1 (reasoning-модель требует больше токенов)

# VIBES - 5 фирменных настроений бренда
VIBES = {
    'natural_harmony': {
        'name': 'Natural Harmony',
        'description': 'Лёгкость, гармония, природа, утренние ритуалы. Эхо природных тонов.',
        'emojis': '🌿☀️🌸',
        'keywords': ['природа', 'утро', 'ритуалы', 'гармония', 'лёгкость']
    },
    'mindful_support': {
        'name': 'Mindful Support',
        'description': 'Осознанная поддержка, безопасность, глубина, мягкое сопровождение.',
        'emojis': '🕊️🤲💫',
        'keywords': ['поддержка', 'безопасность', 'осознанность', 'сопровождение']
    },
    'transformation': {
        'name': 'Transformation through Action',
        'description': 'Трансформация через действие, маленькие шаги, внутренняя сила.',
        'emojis': '✨🔥🌱',
        'keywords': ['трансформация', 'действие', 'шаги', 'сила']
    },
    'depth_safety': {
        'name': 'Depth & Safety',
        'description': 'Глубокие инсайты, эмоциональная безопасность, доверие.',
        'emojis': '🌊🛡️❤️',
        'keywords': ['глубина', 'безопасность', 'доверие', 'инсайты']
    },
    'authenticity': {
        'name': 'Authenticity',
        'description': 'Настоящее Я, реальные эмоции, принятие несовершенств.',
        'emojis': '💖🪞🌟',
        'keywords': ['аутентичность', 'реальность', 'несовершенство', 'подлинность']
    }
}

# BRAND CONTEXT - контекст бренда Poznay Sebya
BRAND_CONTEXT = {
    'name': 'Poznay Sebya',
    'tagline': 'Know Yourself',
    'audience': 'женщины 30-45 лет, self-discovery, mindful living',
    'service': 'self-discovery сессии (5-10, 30-45 мин, PDF insights)',
    'platforms': ['Instagram', 'Telegram', 'Pinterest'],
    'content_types': ['posts', 'stories', 'reels', 'email', 'captions'],
    'tone_of_voice': 'empathetic, deep, supportive, authentic, warm',
    'color_palette': {
        'bg': '#F5F3EF',
        'accent': '#A38DA2',
        'text': '#4A4F46',
        'highlight': '#8CA29B',
        'warm': '#E3D6C4'
    },
    'fonts': {
        'headings': 'Cormorant Garamond',
        'body': 'Inter'
    }
}

# System Prompt для всех запросов
SYSTEM_PROMPT = """Ты — маркетинговый ассистент Poznay Sebya (Know Yourself). 
Создавай контент в фирменном стиле: empathetic, deep, authentic, warm. 
Аудитория: женщины 30-45 лет, ищущие self-discovery и mindful living. 
Всегда предлагай actionable insights и CTA для записи на сессию self-discovery.
Избегай harsh элементов, используй gentle guidance и supportive tone.

ВАЖНО: НЕ используй markdown-разметку в ответах (никаких **, __, #, ```, --- и т.д.).
Пиши простым текстом, готовым для публикации в Instagram, Telegram или email."""

# Output directories
OUTPUT_DIR = 'output'
EXAMPLES_DIR = os.path.join(OUTPUT_DIR, 'examples')
LOGS_DIR = os.path.join(OUTPUT_DIR, 'logs')
