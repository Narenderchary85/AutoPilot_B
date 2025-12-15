class Agent:
    def __init__(self, llm, system_prompt):
        self.llm = llm
        self.system_prompt = system_prompt

    def invoke(self, message):
        return self.llm.generate(self.system_prompt, message)
