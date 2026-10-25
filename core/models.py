from dataclasses import dataclass
from datetime import datetime


@dataclass
class Article:
    title: str
    link: str = ""
    source: str = ""
    published: datetime | None = None
    description: str = ""
