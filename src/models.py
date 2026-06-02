from dataclasses import dataclass, field, asdict


@dataclass
class Job:
    title: str
    url: str
    source: str
    country: str = ""
    region: str = ""
    description: str = ""
    score: int = 0
    specialties: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)
