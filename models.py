from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint
)
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session
from datetime import datetime

# -----------------------------
# Database Configuration
# -----------------------------

DATABASE_URL = "sqlite:///habits.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

SessionFactory = sessionmaker(bind=engine, autoflush=False)
Session = scoped_session(SessionFactory)

Base = declarative_base()
Base.query = Session.query_property()


# -----------------------------
# Database Initializer
# -----------------------------

def initialize_database():
    """
    Creates all tables if they do not exist.
    Safe to call multiple times.
    """
    Base.metadata.create_all(engine)


# -----------------------------
# Habit Model
# -----------------------------

class Habit(Base):
    __tablename__ = "habits"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Habit id={self.id} name='{self.name}'>"

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at.isoformat()
        }


# -----------------------------
# Entry Model (Daily Tracking)
# -----------------------------

class Entry(Base):
    __tablename__ = "entries"

    id = Column(Integer, primary_key=True)
    habit_id = Column(Integer, ForeignKey("habits.id"), nullable=False)
    date = Column(String, nullable=False)  # YYYY-MM-DD
    count = Column(Integer, default=0, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "habit_id",
            "date",
            name="uq_habit_day"
        ),
    )

    def increment(self, value=1):
        """
        Increment habit count safely.
        """
        self.count += value

    def __repr__(self):
        return f"<Entry habit_id={self.habit_id} date={self.date} count={self.count}>"

