from operator import attrgetter
from mesa import DataCollector

class CustomDataCollector(DataCollector):

    def __init__(self, agent_types, model_reporters=None, agent_reporters=None, tables=None):
        super().__init__(model_reporters, agent_reporters, tables)
        self.agent_types = agent_types

    def _record_agents(self, model):
        """Record agents data in a mapping of functions and agents."""
        rep_funcs = self.agent_reporters.values()
        if all([hasattr(rep, "attribute_name") for rep in rep_funcs]):
            prefix = ["model.schedule.steps", "unique_id"]
            attributes = [func.attribute_name for func in rep_funcs]
            get_reports = attrgetter(*prefix + attributes)
        else:

            def get_reports(agent):
                _prefix = (agent.model.schedule.steps, agent.unique_id)
                reports = tuple(rep(agent) for rep in rep_funcs)
                return _prefix + reports

        agents = []
        for agent_type in self.agent_types:
            agents += list(model.schedule.agents_by_type[agent_type].values())
        
        agent_records = map(get_reports, agents)
        #agents_by_type[self.agent_types]
        return agent_records