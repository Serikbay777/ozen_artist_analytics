import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from openai import APIConnectionError, APIError
import logging

logger = logging.getLogger(__name__)

class LLMManager:
    def __init__(self):
        # Используем Alem.ai API с моделью Qwen3
        self.api_key = os.getenv("ALEMAI_API_QWEN3_KEY")
        if not self.api_key:
            raise ValueError("ALEMAI_API_QWEN3_KEY not found in environment variables")
        
        # Получаем base_url из переменной окружения
        base_url = os.getenv("ALEMAI_BASE_URL", "https://llm.alem.ai/v1")
        
        # Инициализируем ChatOpenAI с Alem.ai endpoint
        # LangChain's ChatOpenAI совместим с OpenAI-like API
        llm_kwargs = {
            "model": "qwen3",  # Модель Qwen3 на Alem.ai
            "temperature": 0,
            "api_key": self.api_key,
            "base_url": base_url,
            "timeout": 30.0,  # Таймаут в секундах
            "max_retries": 2,  # Количество повторных попыток
        }
            
        self.llm = ChatOpenAI(**llm_kwargs)
        logger.info(f"✅ LLMManager инициализирован с моделью qwen3 (Alem.ai)")

    def invoke(self, prompt: ChatPromptTemplate, **kwargs) -> str:
        try:
            # Форматируем промпт в сообщения
            messages = prompt.format_messages(**kwargs)
            
            logger.info(f"  → Вызов LLM (модель: {self.llm.model_name})")
            
            # Логируем запрос
            logger.info("  📤 Запрос к LLM:")
            for i, msg in enumerate(messages):
                role = msg.__class__.__name__.replace("Message", "")
                content = msg.content
                # Обрезаем слишком длинные сообщения
                if len(content) > 500:
                    content_preview = content[:250] + "\n...\n" + content[-250:]
                else:
                    content_preview = content
                logger.info(f"    [{i+1}] {role}:")
                for line in content_preview.split('\n'):
                    logger.info(f"      {line}")
            
            # Вызываем OpenAI через LangChain
            response = self.llm.invoke(messages)
            
            # Логируем ответ
            logger.info("  📥 Ответ от LLM:")
            response_content = response.content
            if len(response_content) > 1000:
                response_preview = response_content[:500] + "\n...\n" + response_content[-500:]
            else:
                response_preview = response_content
            for line in response_preview.split('\n'):
                logger.info(f"    {line}")
            
            # Возвращаем содержимое ответа
            return response.content
                
        except APIConnectionError as e:
            raise RuntimeError(
                f"Failed to connect to Alem.ai API. Please check:\n"
                f"1. Your internet connection\n"
                f"2. DNS settings\n"
                f"3. Firewall/proxy settings\n"
                f"4. API endpoint: {self.llm.openai_api_base}\n"
                f"Original error: {str(e)}"
            )
        except APIError as e:
            raise RuntimeError(f"Alem.ai API error: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Error generating answer with Alem.ai (Qwen3): {str(e)}")