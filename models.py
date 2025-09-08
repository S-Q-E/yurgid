# models.py
from sqlalchemy import Integer, String, Text, DateTime, func, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    username: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now())

    # Связь: один пользователь может иметь много сессий
    sessions: Mapped[list["Session"]] = relationship(back_populates="user")


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # 👇 Указываем, что это внешний ключ, ссылающийся на поле 'id' в таблице 'users'
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    started_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now())

    # Связь для доступа к объекту User из объекта Session (session.user)
    user: Mapped["User"] = relationship(back_populates="sessions")
    # Связь: одна сессия может иметь много сообщений
    messages: Mapped[list["Message"]] = relationship(back_populates="session")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # 👇 Указываем, что это внешний ключ, ссылающийся на поле 'id' в таблице 'sessions'
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"))
    # 👇 Используем правильный тип Boolean
    is_user: Mapped[bool] = mapped_column(Boolean)  # true — user, false — bot
    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now())

    # Связь для доступа к объекту Session из объекта Message (message.session)
    session: Mapped["Session"] = relationship(back_populates="messages")