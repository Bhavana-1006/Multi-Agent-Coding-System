from Agents.base_agent import BaseAgent
from schemas.state import ProjectState
from retrieval.vector_store import knowledge_store

class RetrievalAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="RetrievalAgent",
            description="Retrieves relevant documentation, library specs, algorithms, and coding patterns."
        )

    def run(self, state: ProjectState) -> ProjectState:
        self.log("Retrieving relevant code examples and documentation...")
        query = state.raw_requirement
        if state.structured_requirement and state.structured_requirement.summary:
            query += f" {state.structured_requirement.summary}"
            
        retrieved_docs = knowledge_store.search(query, top_k=2)
        state.retrieved_context = retrieved_docs
        state.action_history.append(self.name)
        state.step_count += 1
        self.log("Retrieved relevant algorithmic patterns and reference context.")
        return state
