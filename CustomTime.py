from mesa.time import RandomActivationByType
from mesa.model import Model
from mesa.agent import Agent

class RandomActivationByTypeOrdered(RandomActivationByType):
    def __init__(self, model: Model, daily_step: int = 0) -> None:
        super().__init__(model)
        self.days = 0
        self.daily_step = daily_step
        if self.daily_step != 0 and self.steps % self.daily_step == 0:
            self.is_daily_step = True
        else: 
            self.is_daily_step = False

    def step(self, type_ordered_keys: list[type[Agent]], shuffle_agents: bool = True) -> None:
        """
        Executes the step of each agent type, one at a time decided by user, in possible random order.

        Args:
            type_ordered_keys: A list containing the keys ordered by wanted 
                            execution of each agent type
            shuffle_agents: If True, the order of execution of each agents in a
                            type group is shuffled.
            daily_step: How many steps 
        """
        for agent_class in type_ordered_keys:
            self.step_type(agent_class, shuffle_agents=shuffle_agents)
            if self.is_daily_step:
                self.daily_step_type(agent_class, shuffle_agents=shuffle_agents)
        self.steps += 1
        self.time += 1

    def daily_step_type(self, type_class: type[Agent], shuffle_agents: bool = True) -> None:
        """
        Shuffle order and run all agents of a given type.
        This method is equivalent to the NetLogo 'ask [breed]...'.

        Args:
            type_class: Class object of the type to run.
        """
        agent_keys: list[int] = list(self.agents_by_type[type_class].keys())
        if shuffle_agents:
            self.model.random.shuffle(agent_keys)
        for agent_key in agent_keys:
            self.agents_by_type[type_class][agent_key].dailyStep()

        self.days += 1