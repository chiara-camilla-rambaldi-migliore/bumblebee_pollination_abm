import mesa

class TreeAgent(mesa.Agent):
    def __init__(self, id, model):
        super().__init__(f"tree_{id}", model)

    def __del__(self):
        pass#self.logger.debug(f"Tree {self.unique_id} died")

    def step(self):
        pass