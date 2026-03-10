class BaseWorkflow:
    name: str

    def run(self, **kwargs) -> dict:
        raise NotImplementedError