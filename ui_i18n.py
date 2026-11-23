"""Тексты интерфейса Streamlit на двух языках и выбор языка.

Язык: ?lang=en|ru в адресе → выбор в переключателе (session_state) →
язык браузера (Accept-Language) → ru.
"""
from typing import Optional

LANGS = ("ru", "en")

TEXTS = {
    "page_title": {"ru": "Познай себя — Генератор контента", "en": "Know Yourself — Content generator"},
    "brand": {"ru": "Познай себя", "en": "Know Yourself"},
    "tagline": {"ru": "Генератор контента в фирменных вайбах", "en": "A content generator in the brand's signature vibes"},
    "choose_vibe": {"ru": "🎨 Выберите вайб", "en": "🎨 Choose a vibe"},
    "content_type": {"ru": "📝 Тип контента", "en": "📝 Content type"},
    "model": {"ru": "🤖 Модель генерации", "en": "🤖 Generation model"},
    "no_keys": {
        "ru": "❌ Не настроен ни один API ключ. Добавьте OPENAI_API_KEY или OPENROUTER_API_KEY в файл .env",
        "en": "❌ No API key is set. Add OPENAI_API_KEY or OPENROUTER_API_KEY to the .env file",
    },
    "provider_unavailable": {
        "ru": "⚠️ {provider} недоступен. Добавьте {env} в файл .env",
        "en": "⚠️ {provider} is not available. Add {env} to the .env file",
    },
    "topic": {"ru": "💭 Тема или задача", "en": "💭 Topic or task"},
    "caption_label": {"ru": "Введите исходный текст для редактирования", "en": "Enter the original text to edit"},
    "caption_placeholder": {
        "ru": "Вставьте текст, который нужно отредактировать в выбранном вайбе...",
        "en": "Paste the text you want to rewrite in the chosen vibe...",
    },
    "chars": {"ru": "знаков", "en": "characters"},
    "topic_placeholder": {"ru": "Например: Утренние ритуалы для гармонии", "en": "For example: Morning rituals for balance"},
    "generate": {"ru": "✨ Сгенерировать контент", "en": "✨ Generate content"},
    "demo_left": {
        "ru": "Демо-режим: осталось {left} из {total} генераций в этой сессии",
        "en": "Demo mode: {left} of {total} generations left in this session",
    },
    "enter_topic": {
        "ru": "⚠️ Пожалуйста, введите тему или текст для генерации",
        "en": "⚠️ Please enter a topic or text to generate from",
    },
    "generating": {"ru": "🔮 Генерирую через {provider}...", "en": "🔮 Generating with {provider}..."},
    "result": {"ru": "### ✨ Результат", "en": "### ✨ Result"},
    "copy": {"ru": "📋 Скопировать", "en": "📋 Copy"},
    "copied": {"ru": "✅ Скопировано!", "en": "✅ Copied!"},
    "download": {"ru": "📥 Скачать .md", "en": "📥 Download .md"},
    "md_vibe": {"ru": "Вайб", "en": "Vibe"},
    "md_topic": {"ru": "Тема", "en": "Topic"},
    "md_model": {"ru": "Модель", "en": "Model"},
    "md_date": {"ru": "Дата", "en": "Date"},
    "md_footer": {"ru": "Создано с помощью Познай себя — Генератор контента", "en": "Made with Know Yourself — Content generator"},
    "ready": {"ru": "✅ Контент готов! Скопируйте или скачайте результат.", "en": "✅ Your content is ready. Copy or download it."},
    "footer_sub": {"ru": "Генератор контента для осознанного маркетинга", "en": "A content generator for mindful marketing"},
    "limit_session": {
        "ru": "Вы использовали все {n} бесплатных генераций в этой сессии. Это демонстрационная версия — полноценный доступ обсуждается индивидуально.",
        "en": "You have used all {n} free generations in this session. This is a demo; full access is discussed individually.",
    },
    "limit_day": {
        "ru": "На сегодня общий лимит демонстрационных генераций исчерпан. Попробуйте, пожалуйста, завтра.",
        "en": "Today's shared demo limit is used up. Please try again tomorrow.",
    },
    "err_no_openai_key": {
        "ru": "OpenAI API ключ не настроен. Добавьте OPENAI_API_KEY в файл .env",
        "en": "The OpenAI API key is not set. Add OPENAI_API_KEY to the .env file",
    },
    "err_no_openai_lib": {
        "ru": "Библиотека OpenAI не установлена. Выполните: pip install openai",
        "en": "The OpenAI library is not installed. Run: pip install openai",
    },
    "err_no_openrouter_key": {
        "ru": "OpenRouter API ключ не настроен. Добавьте OPENROUTER_API_KEY в файл .env",
        "en": "The OpenRouter API key is not set. Add OPENROUTER_API_KEY to the .env file",
    },
    "err_unknown_type": {"ru": "Неизвестный тип контента: {t}", "en": "Unknown content type: {t}"},
    "err_generation": {"ru": "Ошибка генерации ({provider}): {e}", "en": "Generation error ({provider}): {e}"},
}

VIBE_NAMES = {
    "ru": {
        "natural_harmony": "Естественная гармония",
        "mindful_support": "Осознанная поддержка",
        "transformation": "Трансформация через действие",
        "depth_safety": "Глубина и безопасность",
        "authenticity": "Аутентичность",
    },
    "en": {
        "natural_harmony": "Natural Harmony",
        "mindful_support": "Mindful Support",
        "transformation": "Transformation through Action",
        "depth_safety": "Depth & Safety",
        "authenticity": "Authenticity",
    },
}

VIBE_DESCRIPTIONS_EN = {
    "natural_harmony": "Lightness, harmony, nature, morning rituals. An echo of natural tones.",
    "mindful_support": "Mindful support, safety, depth, gentle guidance.",
    "transformation": "Change through action, small steps, inner strength.",
    "depth_safety": "Deep insights, emotional safety, trust.",
    "authenticity": "The real self, real emotions, accepting imperfection.",
}

CONTENT_TYPES = {
    "ru": {
        "📱 Пост для Instagram": "post",
        "📖 Идея для Stories": "story",
        "✏️ Редактор подписи": "caption",
        "💡 Идеи контента (5 шт)": "ideas",
        "📧 Email-рассылка": "email",
    },
    "en": {
        "📱 Instagram post": "post",
        "📖 Stories idea": "story",
        "✏️ Caption editor": "caption",
        "💡 Content ideas (5)": "ideas",
        "📧 Email newsletter": "email",
    },
}


def lang_from_accept_language(header: Optional[str]) -> str:
    if not header:
        return "ru"
    first = header.split(",")[0].strip().lower()
    return "ru" if first.startswith(("ru", "uk", "be", "kk")) else "en"


def t(key: str, lang: str, **kw) -> str:
    text = TEXTS[key].get(lang) or TEXTS[key]["ru"]
    return text.format(**kw) if kw else text
