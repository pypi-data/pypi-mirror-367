class AsyncFunction:
    def __init__(
        self,
        interval,
        function_reference,
        end_condition,
        pause_condition,
        cycles=0,
        name=None,  # New optional name parameter
    ):
        self.interval = interval
        self.function_reference = function_reference
        self.cycles = cycles
        self.times_performed = 0
        self.end_condition = end_condition if end_condition else lambda: False
        self.pause_condition = pause_condition if pause_condition else lambda: False
        # Set the name from the parameter, or fall back to the function's internal name
        self.name = name or getattr(function_reference, "__name__", "lambda")

    def run(self):
        self.function_reference()
