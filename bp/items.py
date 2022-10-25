from dataclasses import dataclass


@dataclass
class News:
    url: str = None
    ticker: str = None
    title: str = None
    summary: str = None
    date: int = None
    category: str = None


@dataclass
class Price:
    ticker: str = None
    price: str = None
    date: int = None
