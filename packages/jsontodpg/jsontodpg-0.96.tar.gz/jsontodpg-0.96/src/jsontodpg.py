from tokenizer import Tokenizer
from asyncfunction import AsyncFunction
from controller import Controller
import dearpygui.dearpygui as dpg
import dpgextended as dpg_extended
import importlib

FUNCTION_NAME = "name"
REFERENCE = "function reference"
ARGS = "args"
LEVEL = "level"
PARENT = "parent"
TAG = "tag"
MAX_TICK = 86400

PARENT_IGNORE_LIST = ["viewport"]


class KeywordAccessor:
    """A helper object that dynamically returns the string name of any attribute requested."""

    def __getattr__(self, name):
        return name


class JsonToDpg:
    def __init__(
        self,
        debug=False,
        async_functions={},
        plugins=[],
        auto_generate_keywords=True,  # The new toggle, defaulting to True
    ):
        self.dpg = dpg
        self.parse_history = []
        self.debug = debug
        self.async_functions = async_functions
        self.model = {}

        self.tokenizer = Tokenizer(
            dpg=self.dpg,
            plugins=[dpg_extended] + (plugins if plugins else []),
        )

        self.controller = Controller(self)
        self.tokenizer.register_controller_methods(self.controller)
        self._inject_dependencies()

        self.keywords = KeywordAccessor()

        # The file generation is now controlled by the toggle.
        if auto_generate_keywords:
            self._check_and_generate_keywords()

        self.canceled_asycn_functions = []
        self.__is_debug(debug)
        self.parent_stack = []

    def _check_and_generate_keywords(self, filename="dpgkeywords"):
        """Checks if the keywords file is missing or outdated and regenerates it."""
        discovered_keywords = self.tokenizer.all_keywords
        existing_keywords = set()

        try:
            module = importlib.import_module(filename)
            importlib.reload(module)
            existing_keywords = {
                name for name in dir(module) if not name.startswith("_")
            }
        except ImportError:
            pass

        if discovered_keywords != existing_keywords:
            print(f"INFO: dpgkeywords.py is missing or out of date. Regenerating...")
            self.tokenizer.write_to_file(filename)
            print(
                "INFO: Keywords file regenerated successfully. Your IDE will now have code completion."
            )

    def _inject_dependencies(self):
        for instance in self.tokenizer.plugin_instances.values():
            if hasattr(instance, "controller"):
                instance.controller = self.controller

    def __is_debug(self, debug):
        if debug:
            dpg.show_metrics()

    def add_async_function(
        self,
        interval,
        function,
        end_condition=None,
        pause_condition=None,
        num_cycles=0,
        name=None,
    ):
        if isinstance(function, dict):
            final_function = self._create_callable_for_param(function)
            if not final_function:
                return
        else:
            final_function = function

        if not interval in self.async_functions:
            self.async_functions[interval] = []
        self.async_functions[interval].append(
            AsyncFunction(
                interval,
                final_function,
                end_condition,
                pause_condition,
                num_cycles,
                name,
            )
        )

    def __build_and_run(self, json_object):
        self.build_function_stack(json_object)

        for function in self.function_stack:
            if self.debug:
                print(f"Current function: {function[FUNCTION_NAME]}")
                print(f"Arguments: {function[ARGS]}")
            function[REFERENCE](**function[ARGS])

    def parse(self, json_object, check_for_existing=False):
        self.function_stack = []
        self.parent_stack = []
        self.parse_history.append(json_object)
        self.__build_and_run(json_object)

    def __remove_canceled_async_functions(self):
        tasks_to_remove = []
        for interval, funcs in self.async_functions.items():
            for i, func in enumerate(funcs):
                if func.end_condition():
                    tasks_to_remove.append((interval, i))

        for interval, i in sorted(tasks_to_remove, reverse=True):
            del self.async_functions[interval][i]

    def __run_async_functions(self, ticks):
        self.__remove_canceled_async_functions()

        for interval, function_set in self.async_functions.items():
            if ticks % interval == 0:
                for func in list(function_set):
                    if not func.pause_condition():
                        func.run()
                        func.times_performed += 1

    def __start_async_loop(self):
        ticks = 0
        while dpg.is_dearpygui_running():
            ticks += 1
            self.dpg.render_dearpygui_frame()
            self.__run_async_functions(ticks)
            if ticks > MAX_TICK:
                ticks = 0
        dpg.stop_dearpygui()

    def start(self, json_object):
        dpg.create_context()
        self.parse(json_object)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        self.__start_async_loop()
        dpg.destroy_context()

    def _create_and_call_function(self, func_key, call_data):
        """Finds and executes an imperative setup function."""
        _, func_ref = self.tokenizer.function_references.get(func_key, (None, None))
        if func_ref:
            args, kwargs = self._extract_args_kwargs(call_data)
            func_ref(*args, **kwargs)
        else:
            print(f"Warning: Could not find target function for key: {func_key}")

    def _create_callable_for_param(self, call_data):
        """Creates a deferred callable (lambda) for a parameter like 'callback'."""
        func_key, call_dict = self._get_func_key_from_dict(call_data)
        if not func_key:
            return None

        _, func_ref = self.tokenizer.function_references.get(func_key, (None, None))
        if func_ref:
            args, kwargs = self._extract_args_kwargs(call_dict)
            return lambda: func_ref(*args, **kwargs)

        print(f"Warning: Could not create callable for target: {func_key}")
        return None

    def _extract_args_kwargs(self, call_data):
        """Helper to safely extract args and kwargs from different data shapes."""
        if isinstance(call_data, list):
            return call_data, {}
        if isinstance(call_data, dict):
            args = call_data.get("args", [])
            kwargs = call_data.get("kwargs", {})
            return args, kwargs
        return [], {}

    def _get_func_key_from_dict(self, data_dict):
        """Finds the function key within a dictionary."""
        for key, value in data_dict.items():
            if key in self.tokenizer.function_references:
                return key, value
        return None, None

    def build_function_stack(self, _object, level=0):
        if isinstance(_object, list):
            for item in _object:
                self.build_function_stack(item, level)
            return

        if isinstance(_object, dict):
            func_key, call_data = self._get_func_key_from_dict(_object)
            if func_key and len(_object) <= 2:
                self._create_and_call_function(func_key, _object[func_key])
                return

            for key, value in _object.items():
                self.build_function_stack((str(key), value), level)
            return

        if not (isinstance(_object, tuple) and len(_object) == 2):
            return

        key, value = _object

        if key in self.tokenizer.components:
            tag_name = f"{len(self.parse_history)}-{len(self.function_stack)}-{key}"
            current_parent = self.parent_stack[-1] if self.parent_stack else ""

            args = {}
            valid_params = self.tokenizer.component_parameter_relations.get(key, [])

            if "parent" in valid_params and current_parent:
                if key not in PARENT_IGNORE_LIST:
                    args["parent"] = current_parent
            if "tag" in valid_params:
                args["tag"] = tag_name

            self.function_stack.append(
                {
                    FUNCTION_NAME: key,
                    REFERENCE: self.tokenizer.components[key],
                    TAG: tag_name,
                    LEVEL: level,
                    ARGS: args,
                }
            )

            self.parent_stack.append(tag_name)
            if isinstance(value, (dict, list, tuple)):
                self.build_function_stack(value, level + 1)
            self.parent_stack.pop()

        elif key in self.tokenizer.parameters:
            if self.function_stack:
                current_component = self.function_stack[-1][FUNCTION_NAME]
                valid_params = self.tokenizer.component_parameter_relations.get(
                    current_component, []
                )

                if key in valid_params:
                    is_callable_dict = (
                        isinstance(value, dict)
                        and self._get_func_key_from_dict(value)[0] is not None
                    )
                    final_value = (
                        self._create_callable_for_param(value)
                        if is_callable_dict
                        else value
                    )
                    self.function_stack[-1][ARGS][key] = final_value

                if not (
                    isinstance(value, dict)
                    and self._get_func_key_from_dict(value)[0] is not None
                ):
                    if isinstance(value, (dict, list, tuple)):
                        self.build_function_stack(value, level)
        else:
            if isinstance(value, (dict, list, tuple)):
                self.build_function_stack(value, level)
