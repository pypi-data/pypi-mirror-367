from tokenizer import Tokenizer
from asyncfunction import AsyncFunction
from controller import Controller
import dearpygui.dearpygui as dpg
import dpgextended as dpg_extended
import importlib
from functools import partial  # Import the correct tool for the job


class KeywordAccessor:
    def __getattr__(self, name):
        return name


class JsonToDpg:
    def __init__(
        self, debug=False, async_functions={}, plugins=[], auto_generate_keywords=True
    ):
        self.dpg = dpg
        self.parse_history = []
        self.debug = debug
        self.async_functions = async_functions
        self.model = {}
        self.tokenizer = Tokenizer(
            dpg=self.dpg, plugins=[dpg_extended] + (plugins if plugins else [])
        )
        self.controller = Controller(self)
        self.tokenizer.register_controller_methods(self.controller)
        self._inject_dependencies()
        self.keywords = KeywordAccessor()
        if auto_generate_keywords:
            self._check_and_generate_keywords()
        self.__is_debug(debug)
        self.item_creation_counter = 0

    def _check_and_generate_keywords(self, filename="dpgkeywords"):
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
            print("INFO: dpgkeywords.py is missing or out of date. Regenerating...")
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
            final_function = self._create_callable_for_param(
                function, is_dpg_callback=False
            )
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

    def parse(self, json_object, parent=None):
        self._parse_and_create(json_object, parent=parent)

    def __run_async_functions(self, ticks):
        for interval, function_set in self.async_functions.items():
            if ticks % interval == 0:
                for func in list(function_set):
                    if not func.pause_condition():
                        func.run()

    def __start_async_loop(self):
        ticks = 0
        while dpg.is_dearpygui_running():
            ticks += 1
            self.dpg.render_dearpygui_frame()
            self.__run_async_functions(ticks)
            if ticks > 86400:
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
        instance, func_ref = self.tokenizer.function_references.get(
            func_key, (None, None)
        )
        if instance and func_ref:
            bound_method = getattr(instance, func_key)
            args, kwargs = self._extract_args_kwargs(call_data)
            bound_method(*args, **kwargs)
        else:
            print(f"Warning: Could not find target function for key: {func_key}")

    def _create_callable_for_param(self, call_data, is_dpg_callback=True):
        func_key, call_dict = self._get_func_key_from_dict(call_data)
        if not func_key:
            return None

        instance, func_ref = self.tokenizer.function_references.get(
            func_key, (None, None)
        )
        if instance and func_ref:
            bound_method = getattr(instance, func_key)
            args, kwargs = self._extract_args_kwargs(call_dict)

            partial_func = partial(bound_method, *args, **kwargs)

            if is_dpg_callback:
                return lambda sender, app_data, user_data: partial_func()
            else:
                return partial_func

        print(f"Warning: Could not create callable for target: {func_key}")
        return None

    def _extract_args_kwargs(self, call_data):
        if isinstance(call_data, list):
            return call_data, {}
        if isinstance(call_data, dict):
            args = call_data.get("args", [])
            kwargs = call_data.get("kwargs", {})
            return args if isinstance(args, list) else [], (
                kwargs if isinstance(kwargs, dict) else {}
            )
        return [], {}

    def _get_func_key_from_dict(self, data_dict):
        if not isinstance(data_dict, dict):
            return None, None
        for key, value in data_dict.items():
            if key in self.tokenizer.function_references:
                return key, value
        return None, None


    def _parse_and_create(self, _object, parent=None):
        if isinstance(_object, list):
            for item in _object:
                self._parse_and_create(item, parent=parent)
            return

        if not isinstance(_object, dict):
            return

        # Handle imperative function calls like `put` or `add_monitor`
        func_key, call_data = self._get_func_key_from_dict(_object)
        if func_key:
            self._create_and_call_function(func_key, _object[func_key])
            return

        # Process each key-value pair in the dictionary.
        for key, value in _object.items():
            if key in self.tokenizer.components:
                # The key is a component (e.g., "window", "button").
                self._create_component(key, value, parent)
            else:
                # The key is not a component, so it's an arbitrary grouping key (e.g., "ui_elements").
                # We recurse on its value, passing the same parent down.
                self._parse_and_create(value, parent=parent)

    def _create_component(self, component_key, definition_dict, parent):
        kwargs = {}
        children = []
        component_params = self.tokenizer.component_parameter_relations.get(
            component_key, []
        )

        # Handle simple cases like { "separator": {} } or { "separator": null }
        if not isinstance(definition_dict, dict):
            definition_dict = {}

        for key, value in definition_dict.items():
            if key in component_params:
                # This key is a valid parameter for the component.
                is_dpg_callback = key in (
                    "callback",
                    "drag_callback",
                    "drop_callback",
                    "delink_callback",
                    "on_close",
                )
                is_async_func = (
                    component_key == "add_async_function" and key == "function"
                )

                if (is_dpg_callback or is_async_func) and isinstance(value, dict):
                    kwargs[key] = self._create_callable_for_param(
                        value, is_dpg_callback=is_dpg_callback
                    )
                else:
                    kwargs[key] = value
            else:
                # This key is not a parameter, so it must define children.
                children.append(value)

        # Assign the parent from the recursive call.
        if parent and "parent" in component_params:
            kwargs["parent"] = parent

        # Ensure a tag exists if the component supports it.
        if "tag" not in kwargs and "tag" in component_params:
            self.item_creation_counter += 1
            kwargs["tag"] = f"auto_gen_{self.item_creation_counter}_{component_key}"

        try:
            # Create the component immediately.
            component_func = self.tokenizer.components[component_key]
            new_parent_id = component_func(**kwargs)
        except Exception as e:
            print(f"\n--- JSONTODPG CREATION ERROR ---")
            print(f"Failed to create component: '{component_key}'")
            print(f"With arguments: {kwargs}")
            print(f"Intended parent: {parent}")
            print(f"Original DPG Error: {e}")
            print("---------------------------------\n")
            raise

        # Determine the parent for the next level of recursion.
        effective_parent_id = new_parent_id or kwargs.get("tag") or parent

        # Now that the parent exists, recursively create its children.
        if children:
            self._parse_and_create(children, parent=effective_parent_id)

    # --- END REWRITTEN PARSING ENGINE ---
