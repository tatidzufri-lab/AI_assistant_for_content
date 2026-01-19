"""
Streamlit веб-интерфейс для Vibe Assistant — Познай себя
"""
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
from typing import Optional
import html
import re


def clean_markdown(text: str) -> str:
    """Очищает текст от markdown-разметки для чистого отображения"""
    # Убираем заголовки (# ## ### и т.д.)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Убираем жирный текст **text** или __text__
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    # Убираем курсив *text* или _text_ (но не внутри слов)
    text = re.sub(r'(?<!\w)\*([^*]+?)\*(?!\w)', r'\1', text)
    text = re.sub(r'(?<!\w)_([^_]+?)_(?!\w)', r'\1', text)
    # Убираем ссылки [text](url) -> text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    # Убираем инлайн-код `code`
    text = re.sub(r'`([^`]+)`', r'\1', text)
    # Убираем горизонтальные линии ---
    text = re.sub(r'^-{3,}$', '', text, flags=re.MULTILINE)
    # Убираем лишние пустые строки
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

from config import (
    VIBES, BRAND_CONTEXT, SYSTEM_PROMPT, 
    OPENAI_API_KEY, OPENROUTER_API_KEY,
    OPENAI_MODEL, OPENROUTER_MODEL,
    TEMPERATURE, MAX_TOKENS, MAX_TOKENS_OPENROUTER
)
import requests
from prompts import PROMPT_TEMPLATES

# Попытка импорта OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Настройка страницы
st.set_page_config(
    page_title="Познай себя — Генератор контента",
    page_icon="🌿",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Кастомные стили в цветах бренда
st.markdown("""
<style>
    /* Основные цвета бренда */
    :root {
        --bg-color: #F5F3EF;
        --accent-color: #A38DA2;
        --text-color: #4A4F46;
        --highlight-color: #8CA29B;
        --warm-color: #E3D6C4;
    }
    
    /* Фон приложения */
    .stApp {
        background-color: #F5F3EF;
    }
    
    /* Заголовки */
    h1, h2, h3, h4 {
        color: #4A4F46 !important;
        font-family: 'Georgia', serif !important;
    }
    
    /* Подзаголовки секций */
    .stMarkdown h4 {
        color: #4A4F46 !important;
        font-weight: 600 !important;
    }
    
    /* Кнопки */
    .stButton > button {
        background-color: #A38DA2 !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 0.5rem 2rem !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background-color: #8CA29B !important;
        transform: translateY(-2px) !important;
    }
    
    /* Селекторы */
    .stSelectbox > div > div {
        background-color: white !important;
        border: 2px solid #E3D6C4 !important;
        border-radius: 10px !important;
    }
    
    /* Текст внутри селекторов */
    .stSelectbox > div > div > div {
        color: #4A4F46 !important;
    }
    
    .stSelectbox [data-baseweb="select"] span {
        color: #4A4F46 !important;
    }
    
    /* Выпадающее меню селектора */
    [data-baseweb="menu"],
    [data-baseweb="popover"] > div {
        background-color: #FFFFFF !important;
        border: 2px solid #E3D6C4 !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 20px rgba(163, 141, 162, 0.15) !important;
    }
    
    /* Элементы списка в dropdown */
    [data-baseweb="menu"] li,
    [role="option"] {
        background-color: #FFFFFF !important;
        color: #4A4F46 !important;
    }
    
    /* Hover эффект для элементов списка */
    [data-baseweb="menu"] li:hover,
    [role="option"]:hover {
        background-color: #F5F3EF !important;
        color: #4A4F46 !important;
    }
    
    /* Выбранный элемент */
    [aria-selected="true"],
    [data-baseweb="menu"] li[aria-selected="true"] {
        background-color: #E3D6C4 !important;
        color: #4A4F46 !important;
    }
    
    /* Убрать тёмный фон у popover */
    div[data-baseweb="popover"] {
        background-color: transparent !important;
    }
    
    /* Текстовые поля */
    .stTextArea > div > div > textarea {
        background-color: white !important;
        border: 2px solid #E3D6C4 !important;
        border-radius: 10px !important;
        color: #4A4F46 !important;
        resize: vertical !important;
        min-height: 100px !important;
        overflow: auto !important;
    }
    
    /* Стиль ручки изменения размера */
    .stTextArea > div > div > textarea::-webkit-resizer {
        background-color: #E3D6C4;
        border-radius: 0 0 8px 0;
    }
    
    .stTextInput > div > div > input {
        background-color: white !important;
        border: 2px solid #E3D6C4 !important;
        border-radius: 10px !important;
        color: #4A4F46 !important;
    }
    
    /* Placeholder текст */
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: #A38DA2 !important;
        opacity: 0.7 !important;
    }
    
    /* Карточка результата */
    .result-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        border-left: 4px solid #A38DA2;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin: 1rem 0;
    }
    
    /* Карточка вайба */
    .vibe-card {
        background: linear-gradient(135deg, #E3D6C4 0%, #F5F3EF 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    /* Кнопка скачивания */
    .stDownloadButton > button {
        background-color: #8CA29B !important;
        color: white !important;
        border: none !important;
        border-radius: 20px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 500 !important;
        font-size: 1rem !important;
        height: 42px !important;
        transition: all 0.3s ease !important;
    }
    
    .stDownloadButton > button:hover {
        background-color: #7A928B !important;
    }
    
    /* Выравнивание колонок с кнопками */
    .stDownloadButton {
        margin-top: 0 !important;
    }
    
    /* Футер */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #A38DA2;
        font-size: 0.9rem;
    }
    
    /* Стили для предупреждений и сообщений */
    .stAlert > div {
        color: #4A4F46 !important;
    }
    
    .stAlert p, .stAlert span, .stAlert div {
        color: #4A4F46 !important;
    }
    
    /* Предупреждение (warning) */
    [data-testid="stAlert"][data-baseweb="notification"] {
        background-color: #FFF3CD !important;
        border: 1px solid #E3D6C4 !important;
    }
    
    [data-testid="stAlert"] p {
        color: #4A4F46 !important;
        font-weight: 500 !important;
    }
    
    /* Скрыть стандартный футер Streamlit */
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


def generate_content_api(vibe: str, task_type: str, topic: str, original_text: Optional[str] = None, provider: str = "OpenAI") -> dict:
    """Генерирует контент через OpenAI или OpenRouter API"""
    
    # Проверка API ключей
    if provider == "OpenAI":
        if not OPENAI_API_KEY:
            return {
                'success': False,
                'error': 'OpenAI API ключ не настроен. Добавьте OPENAI_API_KEY в файл .env',
                'content': None
            }
        if not OPENAI_AVAILABLE:
            return {
                'success': False,
                'error': 'Библиотека OpenAI не установлена. Выполните: pip install openai',
                'content': None
            }
    else:  # OpenRouter
        if not OPENROUTER_API_KEY:
            return {
                'success': False,
                'error': 'OpenRouter API ключ не настроен. Добавьте OPENROUTER_API_KEY в файл .env',
                'content': None
            }
    
    # Получаем промпт
    prompt_func = PROMPT_TEMPLATES.get(task_type)
    if not prompt_func:
        return {
            'success': False,
            'error': f'Неизвестный тип контента: {task_type}',
            'content': None
        }
    
    # Формируем промпт
    if task_type == 'caption' and original_text:
        user_prompt = prompt_func(vibe, original_text)
    else:
        user_prompt = prompt_func(vibe, topic)
    
    try:
        if provider == "OpenAI":
            # Генерация через OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
            
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS
            )
            
            content = response.choices[0].message.content.strip()
            model_used = OPENAI_MODEL
            
        else:  # OpenRouter
            # Генерация через OpenRouter
            api_url = 'https://openrouter.ai/api/v1/chat/completions'
            
            headers = {
                'Authorization': f'Bearer {OPENROUTER_API_KEY}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'https://github.com/poznay-sebya',
                'X-Title': 'Poznay Sebya Vibe Assistant'
            }
            
            payload = {
                'model': OPENROUTER_MODEL,
                'messages': [
                    {'role': 'system', 'content': SYSTEM_PROMPT},
                    {'role': 'user', 'content': user_prompt}
                ],
                'temperature': TEMPERATURE,
                'max_tokens': MAX_TOKENS_OPENROUTER  # DeepSeek R1 требует больше токенов
            }
            
            response = requests.post(api_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            message = data['choices'][0]['message']
            # DeepSeek R1 возвращает контент в reasoning_content, а не в content
            content = message.get('content') or message.get('reasoning_content', '')
            content = content.strip() if content else ''
            model_used = OPENROUTER_MODEL
        
        # Очищаем markdown-разметку для чистого отображения
        clean_content = clean_markdown(content)
        
        return {
            'success': True,
            'content': clean_content,
            'vibe': vibe,
            'task_type': task_type,
            'topic': topic,
            'provider': provider,
            'model': model_used,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Ошибка генерации ({provider}): {str(e)}',
            'content': None
        }


# Русские названия вайбов (глобально для доступа везде)
VIBE_NAMES_RU = {
    'natural_harmony': 'Естественная гармония',
    'mindful_support': 'Осознанная поддержка',
    'transformation': 'Трансформация через действие',
    'depth_safety': 'Глубина и безопасность',
    'authenticity': 'Аутентичность'
}


def main():
    # Заголовок
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1>🌿 Познай себя</h1>
        <p style="color: #A38DA2; font-size: 1.2rem; margin-top: -10px;">
            Генератор контента в фирменных вайбах
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Разделитель
    st.markdown("---")
    
    # Колонки для выбора
    col1, col2 = st.columns(2)
    
    with col1:
        # Выбор вайба
        st.markdown('<h4 style="color: #4A4F46; margin-bottom: 0.5rem;">🎨 Выберите вайб</h4>', unsafe_allow_html=True)
        
        vibe_options = {
            f"{v['emojis']} {VIBE_NAMES_RU.get(k, v['name'])}": k 
            for k, v in VIBES.items()
        }
        
        selected_vibe_display = st.selectbox(
            "Вайб",
            options=list(vibe_options.keys()),
            label_visibility="collapsed"
        )
        selected_vibe = vibe_options[selected_vibe_display]
        
        # Описание выбранного вайба
        vibe_info = VIBES[selected_vibe]
        st.markdown(f"""
        <div class="vibe-card">
            <small style="color: #4A4F46;">
                {vibe_info['description']}
            </small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Выбор типа контента
        st.markdown('<h4 style="color: #4A4F46; margin-bottom: 0.5rem;">📝 Тип контента</h4>', unsafe_allow_html=True)
        
        content_types = {
            "📱 Пост для Instagram": "post",
            "📖 Идея для Stories": "story",
            "✏️ Редактор подписи": "caption",
            "💡 Идеи контента (5 шт)": "ideas",
            "📧 Email-рассылка": "email"
        }
        
        selected_type_display = st.selectbox(
            "Тип",
            options=list(content_types.keys()),
            label_visibility="collapsed"
        )
        selected_type = content_types[selected_type_display]
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Выбор провайдера (модели)
    st.markdown('<h4 style="color: #4A4F46; margin-bottom: 0.5rem;">🤖 Модель генерации</h4>', unsafe_allow_html=True)
    
    # Формируем список всех провайдеров с пометками доступности
    openai_status = "🟢" if OPENAI_API_KEY else "⚪"
    openrouter_status = "🟢" if OPENROUTER_API_KEY else "⚪"
    
    providers_list = [
        f"{openai_status} OpenAI ({OPENAI_MODEL})",
        f"{openrouter_status} OpenRouter ({OPENROUTER_MODEL.split('/')[-1]})"
    ]
    providers_map = {
        providers_list[0]: ("OpenAI", bool(OPENAI_API_KEY)),
        providers_list[1]: ("OpenRouter", bool(OPENROUTER_API_KEY))
    }
    
    # Проверяем, есть ли хотя бы один настроенный провайдер
    if not OPENAI_API_KEY and not OPENROUTER_API_KEY:
        st.error("❌ Не настроен ни один API ключ. Добавьте OPENAI_API_KEY или OPENROUTER_API_KEY в файл .env")
        st.stop()
    
    # По умолчанию выбираем первый доступный
    default_index = 0 if OPENAI_API_KEY else 1
    
    selected_provider_display = st.selectbox(
        "Провайдер",
        options=providers_list,
        index=default_index,
        label_visibility="collapsed"
    )
    
    selected_provider, is_available = providers_map[selected_provider_display]
    
    # Предупреждение если выбран недоступный провайдер
    if not is_available:
        env_var = "OPENAI_API_KEY" if selected_provider == "OpenAI" else "OPENROUTER_API_KEY"
        st.warning(f"⚠️ {selected_provider} недоступен. Добавьте {env_var} в файл .env")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Поле для ввода темы
    st.markdown('<h4 style="color: #4A4F46; margin-bottom: 0.5rem;">💭 Тема или задача</h4>', unsafe_allow_html=True)
    
    if selected_type == "caption":
        topic = st.text_area(
            "Введите исходный текст для редактирования",
            placeholder="Вставьте текст, который нужно отредактировать в выбранном вайбе...",
            height=150,
            label_visibility="collapsed",
            key="caption_input"
        )
        # Счётчик символов с JavaScript для обновления в реальном времени
        char_count = len(topic) if topic else 0
        counter_html = f"""
        <div id="char-counter" style="text-align: right; color: #A38DA2; font-size: 0.85rem; margin-top: 0.3rem;">
            📝 <span id="count-value">{char_count}</span> знаков
        </div>
        <script>
        (function() {{
            // Находим textarea в родительском документе
            const textareas = parent.document.querySelectorAll('textarea');
            textareas.forEach(function(textarea) {{
                if (textarea.placeholder && textarea.placeholder.includes('Вставьте текст')) {{
                    // Обновляем счётчик при вводе
                    textarea.addEventListener('input', function() {{
                        const counter = document.getElementById('count-value');
                        if (counter) {{
                            counter.textContent = this.value.length;
                        }}
                    }});
                    // Инициализируем с текущим значением
                    const counter = document.getElementById('count-value');
                    if (counter) {{
                        counter.textContent = textarea.value.length;
                    }}
                }}
            }});
        }})();
        </script>
        """
        components.html(counter_html, height=30)
    else:
        topic = st.text_input(
            "Тема",
            placeholder="Например: Утренние ритуалы для гармонии",
            label_visibility="collapsed"
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Кнопка генерации
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        generate_clicked = st.button(
            "✨ Сгенерировать контент",
            use_container_width=True
        )
    
    # Генерация контента
    if generate_clicked:
        if not topic.strip():
            st.warning("⚠️ Пожалуйста, введите тему или текст для генерации")
        else:
            with st.spinner(f"🔮 Генерирую через {selected_provider}..."):
                result = generate_content_api(
                    vibe=selected_vibe,
                    task_type=selected_type,
                    topic=topic,
                    original_text=topic if selected_type == "caption" else None,
                    provider=selected_provider
                )
            
            if result['success']:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("### ✨ Результат")
                
                # Получаем русское название вайба
                vibe_name_ru = VIBE_NAMES_RU.get(selected_vibe, vibe_info['name'])
                content_type_name = selected_type_display.split(' ', 1)[1]
                
                # Карточка с результатом
                st.markdown(f"""
                <div class="result-card">
                    <div style="margin-bottom: 1rem;">
                        <span style="background: #A38DA2; color: white; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem;">
                            {vibe_info['emojis']} {vibe_name_ru}
                        </span>
                        <span style="background: #8CA29B; color: white; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem; margin-left: 0.5rem;">
                            {content_type_name}
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Сохраняем результат в session_state для доступа к кнопкам
                st.session_state['last_result'] = result['content']
                st.session_state['last_vibe'] = vibe_name_ru
                st.session_state['last_type'] = content_type_name
                st.session_state['last_topic'] = topic
                
                # Текст результата
                st.text_area(
                    "Сгенерированный контент",
                    value=result['content'],
                    height=300,
                    label_visibility="collapsed",
                    key="result_textarea"
                )
                
                # Кнопки действий
                col_copy, col_download = st.columns(2)
                
                with col_copy:
                    # Кнопка копирования через components.html
                    # Экранируем текст для безопасной вставки в JavaScript
                    escaped_content = html.escape(result['content']).replace('\n', '\\n').replace('\r', '\\r').replace("'", "\\'")
                    
                    copy_html = f"""
                    <html>
                    <body style="margin: 0; padding: 0; display: flex; align-items: center; height: 100%;">
                    <button id="copy-btn" onclick="copyToClipboard()" style="
                        background-color: #8CA29B;
                        color: white;
                        border: none;
                        border-radius: 20px;
                        padding: 0.75rem 1.5rem;
                        font-size: 1rem;
                        cursor: pointer;
                        width: 100%;
                        height: 42px;
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        font-weight: 500;
                        transition: all 0.3s ease;
                        box-sizing: border-box;
                    " onmouseover="this.style.backgroundColor='#7A928B'" onmouseout="this.style.backgroundColor='#8CA29B'">
                        📋 Скопировать
                    </button>
                    <script>
                    function copyToClipboard() {{
                        const text = '{escaped_content}';
                        navigator.clipboard.writeText(text).then(function() {{
                            document.getElementById('copy-btn').innerHTML = '✅ Скопировано!';
                            setTimeout(function() {{
                                document.getElementById('copy-btn').innerHTML = '📋 Скопировать';
                            }}, 2000);
                        }}).catch(function(err) {{
                            // Fallback для старых браузеров
                            const textarea = document.createElement('textarea');
                            textarea.value = text;
                            document.body.appendChild(textarea);
                            textarea.select();
                            document.execCommand('copy');
                            document.body.removeChild(textarea);
                            document.getElementById('copy-btn').innerHTML = '✅ Скопировано!';
                            setTimeout(function() {{
                                document.getElementById('copy-btn').innerHTML = '📋 Скопировать';
                            }}, 2000);
                        }});
                    }}
                    </script>
                    </body>
                    </html>
                    """
                    components.html(copy_html, height=42)
                
                with col_download:
                    # Определяем короткое имя модели для файла
                    model_short = result.get('model', 'unknown')
                    if '/' in model_short:
                        model_short = model_short.split('/')[-1].split(':')[0]  # deepseek-r1-0528
                    
                    # Формируем markdown контент для скачивания
                    md_content = f"""# {content_type_name}

**Вайб:** {vibe_info['emojis']} {vibe_name_ru}  
**Тема:** {topic}  
**Модель:** {result.get('provider', 'Unknown')} ({result.get('model', 'unknown')})  
**Дата:** {datetime.now().strftime('%d.%m.%Y %H:%M')}

---

{result['content']}

---

*Создано с помощью Познай себя — Генератор контента*
"""
                    # Формируем имя файла с указанием модели
                    provider_tag = result.get('provider', 'unknown').lower()
                    filename = f"content_{selected_type}_{provider_tag}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                    
                    st.download_button(
                        label="📥 Скачать .md",
                        data=md_content,
                        file_name=filename,
                        mime="text/markdown",
                        use_container_width=True
                    )
                
                st.success("✅ Контент готов! Скопируйте или скачайте результат.")
                
            else:
                st.error(f"❌ {result['error']}")
    
    # Футер
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="footer">
        <p>🌿 Познай себя — Know Yourself</p>
        <p style="font-size: 0.8rem; opacity: 0.7;">
            Генератор контента для осознанного маркетинга
        </p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
