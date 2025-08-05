from typing import Any

from pydantic import BaseModel


class Entity(BaseModel):
    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="python")

    def to_json(self) -> str:
        return self.model_dump_json()