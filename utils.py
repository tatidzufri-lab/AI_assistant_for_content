"""
Утилиты для Vibe Assistant: сохранение, форматирование, выбор вайба
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from config import VIBES, OUTPUT_DIR, EXAMPLES_DIR, LOGS_DIR

console = Console()


def ensure_directories():
    """Создаёт необходимые директории, если их нет"""
    for directory in [OUTPUT_DIR, EXAMPLES_DIR, LOGS_DIR]:
        Path(directory).mkdir(parents=True, exist_ok=True)


def format_output(content: Dict) -> str:
    """
    Форматирует результат генерации для красивого вывода
    """
    vibe_info = VIBES.get(content.get('vibe', ''), {})
    vibe_name = vibe_info.get('name', content.get('vibe', 'Unknown'))
    emojis = vibe_info.get('emojis', '')
    
    output = f"{emojis} **{vibe_name}** {emojis}\n\n"
    output += f"{content.get('content', '')}\n\n"
    
    # Добавляем CTA, если его нет в контенте
    if 'CTA' not in content.get('content', '').upper():
        output += "💫 **CTA:** Запишитесь на сессию self-discovery Poznay Sebya для глубоких insights.\n"
    
    return output


def save_content(content: Dict, output_dir: str = OUTPUT_DIR, format_type: str = 'json') -> str:
    """
    Сохраняет сгенерированный контент в файл
    
    Args:
        content: Словарь с контентом (vibe, task_type, topic, content, timestamp)
        output_dir: Директория для сохранения
        format_type: 'json' или 'markdown'
    
    Returns:
        Путь к сохранённому файлу
    """
    ensure_directories()
    
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M')
    vibe = content.get('vibe', 'unknown')
    task_type = content.get('task_type', 'content')
    provider = content.get('provider', 'unknown').lower()
    
    if format_type == 'json':
        filename = f"{task_type}_{vibe}_{provider}_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        # Если файл существует, загружаем и добавляем новый контент
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if not isinstance(data, list):
                data = [data]
            data.append(content)
        else:
            data = [content]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    elif format_type == 'markdown':
        filename = f"{task_type}_{vibe}_{provider}_{timestamp}.md"
        filepath = os.path.join(output_dir, filename)
        
        vibe_info = VIBES.get(vibe, {})
        vibe_name = vibe_info.get('name', vibe)
        emojis = vibe_info.get('emojis', '')
        model_name = content.get('model', 'unknown')
        provider_name = content.get('provider', 'Unknown')
        
        markdown = f"""# {emojis} {vibe_name} {emojis}

**Тип контента:** {content.get('task_type', 'N/A')}
**Тема:** {content.get('topic', 'N/A')}
**Модель:** {provider_name} ({model_name})
**Дата:** {content.get('timestamp', datetime.now().isoformat())}

---

{content.get('content', '')}

---

*Сгенерировано Vibe Assistant для Poznay Sebya*
"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown)
    
    return filepath


def select_vibe(console: Console) -> Optional[str]:
    """
    Интерактивный выбор вайба через меню
    """
    console.print("\n[bold cyan]Выберите вайб:[/bold cyan]\n")
    
    vibe_list = list(VIBES.keys())
    for idx, vibe_key in enumerate(vibe_list, 1):
        vibe_info = VIBES[vibe_key]
        console.print(f"[bold]{idx}.[/bold] {vibe_info['name']} {vibe_info['emojis']}")
        console.print(f"    {vibe_info['description']}\n")
    
    while True:
        try:
            choice = console.input("[bold green]>[/bold green] ").strip()
            
            # Проверка числового ввода
            if choice.isdigit():
                choice_num = int(choice)
                if 1 <= choice_num <= len(vibe_list):
                    return vibe_list[choice_num - 1]
                else:
                    console.print(f"[red]Пожалуйста, выберите число от 1 до {len(vibe_list)}[/red]")
                    continue
            
            # Проверка текстового ввода (название вайба)
            if choice.lower() in [v.lower() for v in vibe_list]:
                return choice.lower()
            
            # Проверка частичного совпадения
            matching_vibes = [v for v in vibe_list if choice.lower() in v.lower()]
            if len(matching_vibes) == 1:
                return matching_vibes[0]
            elif len(matching_vibes) > 1:
                console.print(f"[yellow]Найдено несколько вайбов: {', '.join(matching_vibes)}[/yellow]")
                continue
            
            console.print("[red]Неверный выбор. Попробуйте снова.[/red]")
        
        except KeyboardInterrupt:
            console.print("\n[yellow]Прервано пользователем.[/yellow]")
            return None
        except Exception as e:
            console.print(f"[red]Ошибка: {e}[/red]")
            continue


def select_task_type(console: Console) -> Optional[str]:
    """
    Интерактивный выбор типа задачи
    """
    task_types = {
        '1': ('post', 'Instagram Post'),
        '2': ('story', 'Stories Idea'),
        '3': ('caption', 'Caption Editor'),
        '4': ('ideas', 'Content Ideas (5)'),
        '5': ('email', 'Email Newsletter')
    }
    
    console.print("\n[bold cyan]Выберите тип контента:[/bold cyan]\n")
    for key, (_, name) in task_types.items():
        console.print(f"[bold]{key}.[/bold] {name}")
    
    while True:
        try:
            choice = console.input("\n[bold green]>[/bold green] ").strip()
            
            if choice in task_types:
                return task_types[choice][0]
            
            # Проверка текстового ввода
            for key, (task_key, name) in task_types.items():
                if choice.lower() in task_key.lower() or choice.lower() in name.lower():
                    return task_key
            
            console.print("[red]Неверный выбор. Попробуйте снова (1-5).[/red]")
        
        except KeyboardInterrupt:
            console.print("\n[yellow]Прервано пользователем.[/yellow]")
            return None
        except Exception as e:
            console.print(f"[red]Ошибка: {e}[/red]")
            continue


def mock_generator(vibe: str, task_type: str, topic: str, original_text: Optional[str] = None) -> Dict:
    """
    Генерирует mock-контент, если API недоступен
    """
    vibe_info = VIBES.get(vibe, {})
    vibe_name = vibe_info.get('name', vibe)
    emojis = vibe_info.get('emojis', '')
    
    mock_content = f"""[MOCK CONTENT - API недоступен]

Вайб: {vibe_name} {emojis}
Тип: {task_type}
Тема: {topic}

Пример контента для Poznay Sebya:

Дорогие читательницы, {topic} — это важная часть вашего пути к себе. 

В вайбе {vibe_name} мы предлагаем вам глубокие insights и поддерживающее пространство для self-discovery.

💫 Запишитесь на сессию Poznay Sebya для получения персональных PDF-insights и практических инструментов трансформации.

*Это mock-контент. Для реальной генерации настройте OPENAI_API_KEY или PROXY_API_KEY в .env файле.*
"""
    
    if task_type == 'caption' and original_text:
        mock_content = f"""[MOCK EDITED CAPTION]

Исходный текст: {original_text}

Отредактированный текст в вайбе {vibe_name} {emojis}:

{original_text}

С добавлением глубины и поддержки в стиле Poznay Sebya. Включите мягкий CTA для записи на сессию.

💫 *Mock-контент. Настройте API для реальной генерации.*
"""
    
    return {
        'vibe': vibe,
        'task_type': task_type,
        'topic': topic,
        'content': mock_content,
        'emojis': emojis,
        'timestamp': datetime.now().isoformat(),
        'mock': True
    }


def check_duplicate(vibe: str, topic: str, output_dir: str = OUTPUT_DIR) -> Optional[str]:
    """
    Проверяет наличие дубликатов по vibe+topic
    Возвращает путь к существующему файлу, если найден
    """
    if not os.path.exists(output_dir):
        return None
    
    for filename in os.listdir(output_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(output_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if not isinstance(data, list):
                        data = [data]
                    
                    for item in data:
                        if (item.get('vibe') == vibe and 
                            item.get('topic', '').lower() == topic.lower()):
                            return filepath
            except:
                continue
    
    return None


def log_message(message: str, level: str = 'INFO'):
    """
    Логирует сообщение в файл
    """
    ensure_directories()
    log_file = os.path.join(LOGS_DIR, f"vibe_assistant_{datetime.now().strftime('%Y-%m-%d')}.log")
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] [{level}] {message}\n"
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(log_entry)




