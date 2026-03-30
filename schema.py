from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class Subprocess(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    inputs: List[str] = Field(default_factory=list)
    activities: List[str] = Field(default_factory=list)
    outputs: List[str] = Field(default_factory=list)
    regulators: List[str] = Field(default_factory=list)
    resources: List[str] = Field(default_factory=list)
    objective: Optional[str] = None
    start_event: Optional[str] = None
    end_event: Optional[str] = None


class Process(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    objective: str
    start_event: str
    end_event: str


class GlobalElements(BaseModel):
    model_config = ConfigDict(extra="forbid")

    inputs: List[str] = Field(default_factory=list)
    outputs: List[str] = Field(default_factory=list)
    regulators: List[str] = Field(default_factory=list)
    resources: List[str] = Field(default_factory=list)


class ScopeDiagram(BaseModel):
    model_config = ConfigDict(extra="forbid")

    process: Process
    subprocesses: List[Subprocess]
    global_elements: Optional[GlobalElements] = None


def scope_diagram_json_schema() -> dict:
    return ScopeDiagram.model_json_schema()
