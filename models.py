from dataclasses import dataclass


@dataclass
class MasterSection:
    order: int
    title: str
    subfile: str
