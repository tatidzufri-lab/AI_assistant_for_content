#!/usr/bin/env python3
"""
Vibe Assistant для Poznay Sebya
Интерактивный ассистент для генерации контента в фирменных вайбах бренда
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, Optional

import requests
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn

from config import (
    OPENAI_API_KEY,
    OPENROUTER_API_KEY,
    OPENAI_MODEL,
    OPENROUTER_MODEL,
    TEMPERATURE,
    MAX_TOKENS,
    MAX_TOKENS_OPENROUTER,
    SYSTEM_PROMPT,
    VIBES,
    BRAND_CONTEXT
)
from prompts import PROMPT_TEMPLATES
from utils import (
    format_output,
    save_content,
    select_vibe,
    select_task_type,
    mock_generator,
    check_duplicate,
    log_message,
    ensure_directories,
    EXAMPLES_DIR
)

console = Console()


def generate_content(
    vibe: str,
    task_type: str,
    topic: str,
    original_text: Optional[str] = None,
    use_openrouter: bool = False
) -> Dict:
    """
    Генерирует контент через OpenAI или OpenRouter (DeepSeek)
    
    Args:
        vibe: Название вайба (natural_harmony, mindful_support, etc.)
        task_type: Тип задачи (post, story, caption, ideas, email)
        topic: Тема контента
        original_text: Исходный текст для редактирования (для caption)
        use_openrouter: Использовать OpenRouter вместо OpenAI
    
    Returns:
        Словарь с результатом генерации
    """
    # Проверка наличия API ключей
    if use_openrouter and not OPENROUTER_API_KEY:
        console.print("[yellow]OPENROUTER_API_KEY не найден. Используется mock-режим.[/yellow]")
        return mock_generator(vibe, task_type, topic, original_text)
    
    if not use_openrouter and not OPENAI_API_KEY:
        console.print("[yellow]OPENAI_API_KEY не найден. Используется mock-режим.[/yellow]")
        return mock_generator(vibe, task_type, topic, original_text)
    
    # Получаем шаблон промпта
    if task_type not in PROMPT_TEMPLATES:
        console.print(f"[red]Неизвестный тип задачи: {task_type}[/red]")
        return mock_generator(vibe, task_type, topic, original_text)
    
    prompt_func = PROMPT_TEMPLATES[task_type]
    
    # Формируем промпт
    if task_type == 'caption' and original_text:
        user_prompt = prompt_func(vibe, original_text)
    else:
        user_prompt = prompt_func(vibe, topic)
    
    # Генерация через OpenRouter (DeepSeek)
    if use_openrouter:
        return generate_via_openrouter(user_prompt, vibe, task_type, topic)
    
    # Генерация через OpenAI
    return generate_via_openai(user_prompt, vibe, task_type, topic)


def generate_via_openai(user_prompt: str, vibe: str, task_type: str, topic: str) -> Dict:
    """
    Генерирует контент через OpenAI API
    """
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS
            )
            
            response_text = response.choices[0].message.content.strip()
            vibe_info = VIBES.get(vibe, {})
            
            result = {
                'vibe': vibe,
                'task_type': task_type,
                'topic': topic,
                'content': response_text,
                'emojis': vibe_info.get('emojis', ''),
                'timestamp': datetime.now().isoformat(),
                'model': OPENAI_MODEL,
                'provider': 'OpenAI',
                'mock': False
            }
            
            log_message(f"Успешная генерация через OpenAI: {vibe} + {task_type} + {topic}")
            return result
        
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2
                console.print(f"[yellow]Ошибка OpenAI (попытка {attempt + 1}/{max_retries}): {e}[/yellow]")
                console.print(f"[yellow]Повтор через {wait_time} сек...[/yellow]")
                time.sleep(wait_time)
            else:
                console.print(f"[red]Не удалось сгенерировать контент через OpenAI: {e}[/red]")
                log_message(f"Ошибка OpenAI: {e}", level='ERROR')
                return mock_generator(vibe, task_type, topic)
    
    return mock_generator(vibe, task_type, topic)


def generate_via_openrouter(user_prompt: str, vibe: str, task_type: str, topic: str) -> Dict:
    """
    Генерирует контент через OpenRouter (DeepSeek R1)
    Документация: https://openrouter.ai/deepseek/deepseek-r1-0528:free/api
    """
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
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            message = data['choices'][0]['message']
            # DeepSeek R1 возвращает контент в reasoning_content, а не в content
            response_text = message.get('content') or message.get('reasoning_content', '')
            response_text = response_text.strip() if response_text else ''
            vibe_info = VIBES.get(vibe, {})
            
            result = {
                'vibe': vibe,
                'task_type': task_type,
                'topic': topic,
                'content': response_text,
                'emojis': vibe_info.get('emojis', ''),
                'timestamp': datetime.now().isoformat(),
                'model': OPENROUTER_MODEL,
                'provider': 'OpenRouter',
                'mock': False
            }
            
            log_message(f"Успешная генерация через OpenRouter: {vibe} + {task_type} + {topic}")
            return result
        
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2
                console.print(f"[yellow]Ошибка OpenRouter (попытка {attempt + 1}/{max_retries}): {e}[/yellow]")
                time.sleep(wait_time)
            else:
                console.print(f"[red]Не удалось сгенерировать через OpenRouter: {e}[/red]")
                log_message(f"Ошибка OpenRouter: {e}", level='ERROR')
                return mock_generator(vibe, task_type, topic)
    
    return mock_generator(vibe, task_type, topic)


def run_test_mode(use_openrouter: bool = False):
    """
    Запускает автоматическое тестирование 3 вайбов
    """
    provider = "OpenRouter" if use_openrouter else "OpenAI"
    console.print(f"\n[bold cyan]🧪 Тестовый режим ({provider})[/bold cyan]\n")
    
    test_cases = [
        {
            'vibe': 'natural_harmony',
            'task_type': 'post',
            'topic': 'кофе и утренняя медитация для гармонии'
        },
        {
            'vibe': 'mindful_support',
            'task_type': 'story',
            'topic': 'эмоциональная безопасность в self-discovery'
        },
        {
            'vibe': 'transformation',
            'task_type': 'ideas',
            'topic': 'small steps to change'
        }
    ]
    
    results = []
    
    for i, test in enumerate(test_cases, 1):
        console.print(f"\n[bold]Тест {i}/3:[/bold] {VIBES[test['vibe']]['name']} + {test['task_type']}")
        console.print(f"Тема: {test['topic']}\n")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("🔄 Генерирую контент...", total=None)
            content = generate_content(
                test['vibe'],
                test['task_type'],
                test['topic'],
                use_openrouter=use_openrouter
            )
            progress.update(task, completed=True)
        
        # Сохраняем в examples
        ensure_directories()
        filepath = save_content(content, EXAMPLES_DIR, format_type='json')
        results.append(content)
        
        # Выводим результат
        formatted = format_output(content)
        console.print(Panel(Markdown(formatted), title=f"Результат теста {i}", border_style="cyan"))
        console.print(f"[green]✓ Сохранено: {filepath}[/green]\n")
        
        time.sleep(1)  # Rate limiting
    
    # Итоги
    success_count = sum(1 for r in results if not r.get('mock', False))
    console.print(f"\n[bold green]✅ Тест завершён: {success_count}/3 вайба сгенерированы успешно[/bold green]\n")
    
    if success_count < 3:
        console.print("[yellow]⚠️  Некоторые тесты использовали mock-режим. Проверьте API ключи в .env[/yellow]\n")


def run_interactive_mode(use_openrouter: bool = False):
    """
    Запускает интерактивный CLI режим
    """
    provider = "OpenRouter" if use_openrouter else "OpenAI"
    console.print(Panel.fit(
        f"[bold cyan]🎨 Vibe Assistant for Poznay Sebya[/bold cyan]\n"
        f"[dim]Know Yourself - Генерация контента ({provider})[/dim]",
        border_style="cyan"
    ))
    
    while True:
        try:
            # Выбор вайба
            vibe = select_vibe(console)
            if not vibe:
                console.print("[yellow]Выход из программы.[/yellow]")
                break
            
            # Выбор типа задачи
            task_type = select_task_type(console)
            if not task_type:
                console.print("[yellow]Выход из программы.[/yellow]")
                break
            
            # Ввод темы
            console.print("\n[bold cyan]Введите тему/задачу:[/bold cyan]")
            topic = console.input("[bold green]>[/bold green] ").strip()
            if not topic:
                console.print("[red]Тема не может быть пустой.[/red]")
                continue
            
            # Для caption - запрос исходного текста
            original_text = None
            if task_type == 'caption':
                console.print("\n[bold cyan]Введите исходный текст для редактирования:[/bold cyan]")
                original_text = console.input("[bold green]>[/bold green] ").strip()
                if not original_text:
                    console.print("[yellow]Исходный текст не указан, будет создан новый.[/yellow]")
            
            # Проверка дубликатов
            duplicate = check_duplicate(vibe, topic)
            if duplicate:
                console.print(f"\n[yellow]⚠️  Найден похожий контент: {duplicate}[/yellow]")
                reuse = console.input("Использовать существующий? (y/n): ").strip().lower()
                if reuse == 'y':
                    with open(duplicate, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            content = data[-1]
                        else:
                            content = data
                    
                    formatted = format_output(content)
                    console.print(Panel(Markdown(formatted), border_style="green"))
                    continue
            
            # Генерация контента
            console.print("\n[bold cyan]🔄 Генерирую контент...[/bold cyan]\n")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Обработка запроса...", total=None)
                content = generate_content(vibe, task_type, topic, original_text, use_openrouter=use_openrouter)
                progress.update(task, completed=True)
            
            # Вывод результата
            formatted = format_output(content)
            console.print(Panel(Markdown(formatted), title="✨ Сгенерированный контент", border_style="green"))
            
            # Сохранение
            save_choice = console.input("\n[bold cyan]Сохранить в output/? (y/n):[/bold cyan] ").strip().lower()
            if save_choice == 'y':
                filepath = save_content(content)
                console.print(f"[green]✓ Сохранено: {filepath}[/green]")
                
                # Опционально сохранить в Markdown
                md_choice = console.input("[bold cyan]Сохранить также в Markdown? (y/n):[/bold cyan] ").strip().lower()
                if md_choice == 'y':
                    md_path = save_content(content, format_type='markdown')
                    console.print(f"[green]✓ Markdown сохранён: {md_path}[/green]")
            
            # Продолжить?
            continue_choice = console.input("\n[bold cyan]Продолжить? (y/n):[/bold cyan] ").strip().lower()
            if continue_choice != 'y':
                console.print("[yellow]До свидания![/yellow]")
                break
            
            console.print("\n" + "="*50 + "\n")
        
        except KeyboardInterrupt:
            console.print("\n[yellow]Прервано пользователем. До свидания![/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Ошибка: {e}[/red]")
            log_message(f"Ошибка в интерактивном режиме: {e}", level='ERROR')
            continue_choice = console.input("\n[bold cyan]Продолжить? (y/n):[/bold cyan] ").strip().lower()
            if continue_choice != 'y':
                break


def main():
    """
    Главная функция с CLI аргументами
    """
    parser = argparse.ArgumentParser(
        description='Vibe Assistant для Poznay Sebya - генерация контента в фирменных вайбах'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Запустить автоматическое тестирование 3 вайбов'
    )
    parser.add_argument(
        '--vibe',
        type=str,
        help='Вайб для генерации (natural_harmony, mindful_support, etc.)'
    )
    parser.add_argument(
        '--type',
        type=str,
        choices=['post', 'story', 'caption', 'ideas', 'email'],
        help='Тип контента'
    )
    parser.add_argument(
        '--topic',
        type=str,
        help='Тема контента'
    )
    parser.add_argument(
        '--openrouter',
        action='store_true',
        help='Использовать OpenRouter (DeepSeek) вместо OpenAI'
    )
    
    args = parser.parse_args()
    
    # One-shot режим
    if args.vibe and args.type and args.topic:
        console.print("[bold cyan]🚀 One-shot режим[/bold cyan]\n")
        
        if args.vibe not in VIBES:
            console.print(f"[red]Неизвестный вайб: {args.vibe}[/red]")
            console.print(f"[yellow]Доступные вайбы: {', '.join(VIBES.keys())}[/yellow]")
            sys.exit(1)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("🔄 Генерирую контент...", total=None)
            content = generate_content(args.vibe, args.type, args.topic, use_openrouter=args.openrouter)
            progress.update(task, completed=True)
        
        formatted = format_output(content)
        console.print(Panel(Markdown(formatted), border_style="green"))
        
        # Автосохранение
        filepath = save_content(content)
        console.print(f"\n[green]✓ Сохранено: {filepath}[/green]")
        
        return
    
    # Тестовый режим
    if args.test:
        run_test_mode(use_openrouter=args.openrouter)
        return
    
    # Интерактивный режим
    run_interactive_mode(use_openrouter=args.openrouter)


if __name__ == '__main__':
    main()

