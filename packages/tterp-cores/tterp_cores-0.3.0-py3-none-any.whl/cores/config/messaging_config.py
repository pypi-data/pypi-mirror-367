"""
Messaging configuration module - Cấu hình cho RabbitMQ và các hệ thống messaging
"""


from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

from cores.config.base_config import env_file_path

# Load các biến môi trường từ file .env
load_dotenv()


class MessagingConfig(BaseSettings):
    """Cấu hình hệ thống messaging (RabbitMQ, Kafka, v.v.)"""

    # RabbitMQ Configuration
    RABBITMQ_HOST: str = "rabbitmq"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASS: str = "guest"
    RABBITMQ_VHOST: str = ""
    RABBITMQ_EXCHANGE: str = "events"

    # Queue và Binding Key Configuration
    QUEUES: dict[str, str] = {
        "EXPLORE_NEWS": "explore_news_events_queue",
        "EXPORT": "export_events_queue",
    }

    BINDING_KEYS: dict[str, str] = {
        "EXPLORE_NEWS": "news.*",
        "EXPORT": "royalty.export.*",
    }

    model_config = SettingsConfigDict(
        env_file=env_file_path,
        extra="ignore",
    )

    def get_rabbitmq_url(self) -> str:
        """Tạo URL kết nối RabbitMQ"""
        credentials = f"{self.RABBITMQ_USER}:{self.RABBITMQ_PASS}"
        vhost_part = f"/{self.RABBITMQ_VHOST}" if self.RABBITMQ_VHOST else ""
        return f"amqp://{credentials}@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}{vhost_part}"


# Singleton instance
messaging_config = MessagingConfig()
