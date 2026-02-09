"""
Пример минимального Telegram бота для интеграции с API
"""

import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

# ============================================================================
# КОНФИГУРАЦИЯ
# ============================================================================

TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"  # Замените на ваш токен
API_URL = "http://localhost:8000/query"  # URL вашего API

# ============================================================================
# ИНИЦИАЛИЗАЦИЯ БОТА
# ============================================================================

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()


# ============================================================================
# ФУНКЦИЯ ДЛЯ ОБРАЩЕНИЯ К API
# ============================================================================

async def ask_agent(question: str, user_id: int) -> dict:
    """
    Отправляет вопрос к агенту и возвращает ответ
    
    Args:
        question: Вопрос пользователя
        user_id: Telegram user ID
    
    Returns:
        dict с полями: answer, agent_used, routing_confidence
    """
    payload = {
        "question": question,
        "uuid": f"telegram_{user_id}",
        "artist_name": None
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                API_URL, 
                json=payload, 
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {
                        "answer": f"❌ Ошибка API: {response.status}",
                        "agent_used": "error",
                        "routing_confidence": "low"
                    }
    except asyncio.TimeoutError:
        return {
            "answer": "⏱ Превышено время ожидания. Попробуйте еще раз.",
            "agent_used": "error",
            "routing_confidence": "low"
        }
    except Exception as e:
        return {
            "answer": f"❌ Ошибка: {str(e)}",
            "agent_used": "error",
            "routing_confidence": "low"
        }


# ============================================================================
# ОБРАБОТЧИКИ КОМАНД
# ============================================================================

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    await message.answer(
        "👋 **Привет! Я бот лейбла õzen.**\n\n"
        "Я могу ответить на вопросы о верификации артистов на платформах:\n"
        "• 🎵 Spotify for Artists\n"
        "• 🍎 Apple Music for Artists\n"
        "• 🎶 Яндекс Музыка (через BandLink)\n"
        "• 📱 VK Studio\n\n"
        "Просто напиши свой вопрос!\n\n"
        "**Примеры вопросов:**\n"
        "• Как верифицироваться в Spotify?\n"
        "• Какие документы нужны для Apple Music?\n"
        "• Сколько времени занимает верификация?",
        parse_mode="Markdown"
    )


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    """Обработчик команды /help"""
    await message.answer(
        "❓ **Помощь**\n\n"
        "Я отвечаю на вопросы о верификации артистов.\n\n"
        "**Доступные платформы:**\n"
        "• Spotify for Artists\n"
        "• Apple Music for Artists\n"
        "• Яндекс Музыка\n"
        "• VK Studio\n\n"
        "**Команды:**\n"
        "/start - Начать работу\n"
        "/help - Эта справка\n\n"
        "Просто напиши свой вопрос!",
        parse_mode="Markdown"
    )


# ============================================================================
# ОБРАБОТЧИК ТЕКСТОВЫХ СООБЩЕНИЙ
# ============================================================================

@dp.message(F.text)
async def handle_question(message: types.Message):
    """Обработчик всех текстовых сообщений"""
    
    # Показываем что бот думает
    thinking_msg = await message.answer("🤔 Думаю...")
    
    try:
        # Отправляем вопрос к агенту
        result = await ask_agent(
            question=message.text,
            user_id=message.from_user.id
        )
        
        answer = result.get("answer", "Не удалось получить ответ")
        agent_used = result.get("agent_used", "unknown")
        
        # Удаляем сообщение "Думаю..."
        await thinking_msg.delete()
        
        # Отправляем ответ
        await message.answer(answer, parse_mode="Markdown")
        
        # Логируем (опционально)
        print(f"User {message.from_user.id}: {message.text[:50]}...")
        print(f"Agent: {agent_used}")
        
    except Exception as e:
        # Если что-то пошло не так
        await thinking_msg.edit_text(
            f"❌ Произошла ошибка: {str(e)}\n\n"
            "Попробуйте еще раз или обратитесь к администратору."
        )
        print(f"Error: {e}")


# ============================================================================
# ЗАПУСК БОТА
# ============================================================================

async def main():
    """Главная функция запуска бота"""
    print("=" * 60)
    print("🤖 Telegram бот запущен!")
    print("=" * 60)
    print(f"API URL: {API_URL}")
    print("Ожидание сообщений...")
    print("=" * 60)
    
    # Запускаем polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    # Запускаем бота
    asyncio.run(main())
