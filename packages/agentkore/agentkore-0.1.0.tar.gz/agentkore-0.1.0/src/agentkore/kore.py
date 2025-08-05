class Agent:
    """
    A minimal LLM-based agent scaffold.
    """

    def __init__(self, name: str):
        self.name = name

    def run(self, prompt: str) -> str:
        """
        Execute the agent’s main logic on the given prompt.
        """
        # TODO: wire up your LLM call (e.g. OpenAI, LangChain, etc.)
        return f"[{self.name}] would process: {prompt}"
