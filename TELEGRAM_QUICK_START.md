# Telegram Bot - Быстрый старт

## 🎯 Главное

**URL:** `http://localhost:8000/query`  
**Метод:** `POST`  
**Content-Type:** `application/json`

---

## 📤 Запрос

```json
{
  "question": "Как верифицироваться в Spotify?",
  "uuid": "telegram_123456"
}
```

## 📥 Ответ

```json
{
  "answer": "🎵 **Верификация в Spotify...**",
  "agent_used": "verification",
  "routing_confidence": "high"
}
```

---

## 🐍 Код для бота (aiogram)

```python
import aiohttp

async def ask_agent(question: str, user_id: int) -> str:
    url = "http://localhost:8000/query"
    payload = {
        "question": question,
        "uuid": f"telegram_{user_id}"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, timeout=60) as response:
            data = await response.json()
            return data["answer"]

# Использование в хендлере
@dp.message(F.text)
async def handle_message(message: types.Message):
    answer = await ask_agent(message.text, message.from_user.id)
    await message.answer(answer, parse_mode="Markdown")
```

---

## ✅ Готово!

1. Запустите API: `uvicorn app.main:app --port 8000`
2. Используйте функцию `ask_agent()` в боте
3. Ответ приходит в Markdown формате

---

## 📋 Примеры вопросов

- "Как верифицироваться в Spotify?"
- "Какие документы нужны для Apple Music?"
- "Сколько времени занимает верификация?"

---

⚠️ **Важно:** Timeout минимум 60 секунд!
