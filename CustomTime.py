from mesa.time import RandomActivationByType
from mesa.model import Model
from mesa.agent import Agent

class RandomActivationByTypeOrdered(RandomActivationByType):
    def __init__(self, model: Model) -> None:
        super().__init__(model)

    def step(self, type_ordered_keys: list[type[Agent]], shuffle_agents: bool = True) -> None:
        """
        Executes the step of each agent type, one at a time decided by user, in possible random order.

        Args:
            type_ordered_keys: A list containing the keys ordered by wanted 
                            execution of each agent type
            shuffle_agents: If True, the order of execution of each agents in a
                            type group is shuffled.
        """
        for agent_class in type_ordered_keys:
            self.step_type(agent_class, shuffle_agents=shuffle_agents)
        self.steps += 1
        self.time += 1