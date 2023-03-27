import tornado.web
from mesa.visualization.ModularVisualization import ModularServer

class CustomModularServer(ModularServer):
    """Main visualization application."""

    EXCLUDE_LIST = ("width", "height")

    def __init__(
        self,
        model_cls,
        visualization_elements,
        name="Mesa Model",
        model_params=None,
        port=None,
        verbose = True,
        max_steps = 100000
    ):
        """
        Args:
            model_cls: Mesa model class
            visualization_elements: visualisation elements
            name: A String for the model name
            port: Port the webserver listens to (int)
                Order of configuration:
                1. Parameter to ModularServer.launch
                2. Parameter to ModularServer()
                3. Environment var PORT
                4. Default value (8521)
            model_params: A dict of model parameters
        """
        super().__init__(model_cls, visualization_elements, name, model_params, port)
        self.verbose = verbose
        self.max_steps = max_steps