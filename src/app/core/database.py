from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings


class DatabaseHelper:
    """Помощник для работы с базой данных.

    Управляет подключением к базе данных, создает асинхронные сессии
    и предоставляет методы для жизненного цикла соединений.

    Attributes:
        engine: Асинхронный движок SQLAlchemy для подключения к БД.
        session_factory: Фабрика для создания асинхронных сессий.
    """
    def __init__(
        self,
        url: str,
        echo: bool = False,
        echo_pool: bool = False,
        pool_size: int = 5,
        max_overflow: int = 10,
    ) -> None:
        """Инициализация помощника базы данных.

        Args:
            url: Строка подключения к базе данных (DSN).
            echo: Включить логирование SQL-запросов (по умолчанию False).
            echo_pool: Включить логирование операций пула (по умолчанию False).
            pool_size: Размер пула соединений (по умолчанию 5).
            max_overflow: Максимальное количество соединений сверх pool_size (по умолчанию 10).
        """
        self.engine: AsyncEngine = create_async_engine(
            url=url,
            echo=echo,
            echo_pool=echo_pool,
            pool_size=pool_size,
            max_overflow=max_overflow,
        )
        self.session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    async def dispose(self) -> None:
        """
        Освобождает ресурсы движка базы данных.
        Закрывает все соединения и освобождает ресурсы, связанные с движком.
        """
        await self.engine.dispose()

    async def session_getter(self) -> AsyncGenerator[AsyncSession]:
        """
        Возвращает асинхронную сессию базы данных.

        Создает новую сессию, возвращает её через yield, и автоматически
        закрывает после использования. Используется как зависимость FastAPI.
        """
        async with self.session_factory() as session:
            yield session


db_helper = DatabaseHelper(
    url=str(
        settings.db.url,
    )
)
