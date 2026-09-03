from abc import ABC, abstractmethod
from schemas.state import ProjectState

class BaseAgent(ABC):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def run(self, state: ProjectState) -> ProjectState:
        """
        Executes the agent logic, mutates or returns an updated ProjectState.
        """
        pass

    def log(self, message: str):
        print(f"[{self.name}] {message}")
