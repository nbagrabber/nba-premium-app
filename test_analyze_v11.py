import asyncio
import os
import sys
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

# Принудительно добавляем корень проекта в путь
sys.path.insert(0, os.getcwd())

from bot.handlers import run_analysis

async def test_analyze():
    print("🚀 Запуск теста /analyze v11...")
    
    # Создаем мок Update
    update = MagicMock()
    update.effective_user.id = 5264410470
    update.message = AsyncMock()
    update.message.text = "Sacramento Kings vs San Antonio Spurs"
    
    # Мокаем сообщение для редактирования
    msg_mock = AsyncMock()
    update.message.reply_html.return_value = msg_mock
    update.callback_query = None # Имитируем текстовую команду
    
    # Контекст
    context = MagicMock()
    context.bot = AsyncMock()
    
    print("⏳ Выполняю run_analysis...")
    try:
        await run_analysis(update, context, "Sacramento Kings vs San Antonio Spurs")
        print("✅ run_analysis завершен.")
    except Exception as e:
        print(f"❌ Ошибка в run_analysis: {e}")
        import traceback
        traceback.print_exc()
        return

    # Проверяем вызовы редактирования сообщения
    print("\n--- Результаты в БОТЕ ---")
    if msg_mock.edit_text.called:
        for call in msg_mock.edit_text.call_args_list:
            args, _ = call
            content = str(args[0])
            print(f"BOT MESSAGE: {content[:500]}...")
    else:
        print("Сообщение бота не было отредактировано (edit_text не вызван)")
    
    # Проверяем отправку в канал
    print("\n--- Результаты в КАНАЛЕ ---")
    if context.bot.send_message.called:
        for call in context.bot.send_message.call_args_list:
            _, kwargs = call
            content = str(kwargs.get('text', ''))
            print(f"CHANNEL CONTENT SUMMARY: {content[:200]}...")
    else:
        print("Сообщение в канал не отправлено.")

if __name__ == "__main__":
    asyncio.run(test_analyze())
