from collections import OrderedDict
from jtodpgutils import *
import dpgextended
import pprint  # Import the pretty-print module

DEFAULT_ALTERING_KEYWORD_FILTERS = ["add_", "create_"]
DEFAULT_NON_ALTERING_KEYWORD_FILTERS = ["draw", "load_"]
KEYWORD_IGNORE_SUBSTRINGS = ["__", "dpg"]


class Tokenizer:
    def __init__(self, dpg, plugins=[]):
        self.component_parameter_relations = OrderedDict()
        self.components = {}
        self.parameters = []
        self.plugin_references = {}
        self.plugin_instances = {}
        self.function_references = {}
        self.function_keyword_set = set()

        self.build_keyword_library(
            dpg, DEFAULT_ALTERING_KEYWORD_FILTERS, DEFAULT_NON_ALTERING_KEYWORD_FILTERS
        )
        self.add_plugins(plugins)

    @property
    def all_keywords(self):
        """Returns a set of all discovered keywords."""
        return (
            set(self.components.keys())
            | self.function_keyword_set
            | set(self.parameters)
        )

    def _add_function_reference(self, simple_name, full_name, instance, func_ref):
        """Adds a function to the reference maps and the keyword set."""
        self.plugin_references[full_name] = func_ref

        if simple_name in self.function_references:
            print(
                f"Warning: Function name '{simple_name}' is ambiguous and has been overwritten."
            )

        self.function_references[simple_name] = (instance, func_ref)
        self.function_keyword_set.add(simple_name)

    def register_controller_methods(self, controller):
        """Inspects the controller and registers all its public methods as callables."""
        for func_name in dir(controller):
            if not func_name.startswith("_"):
                func_ref = getattr(controller, func_name)
                if callable(func_ref):
                    full_func_name = f"controller.{func_name}"
                    self._add_function_reference(
                        func_name, full_func_name, controller, func_ref
                    )

    def add_plugins(self, plugins):
        for plugin in plugins:
            plugin_name = plugin.__name__.lower()

            instance = plugin() if isinstance(plugin, type) else plugin
            if isinstance(plugin, type):
                self.plugin_instances[plugin_name] = instance

            for func_name in dir(instance):
                if not func_name.startswith("_"):
                    func_ref = getattr(instance, func_name)
                    if callable(func_ref):
                        full_func_name = f"{plugin_name}.{func_name}"
                        self._add_function_reference(
                            func_name, full_func_name, instance, func_ref
                        )

    def __filter_keyword(
        self, function_name, altering_filters=[], non_altering_filters=[]
    ):
        if not altering_filters and not non_altering_filters:
            if not [sub for sub in KEYWORD_IGNORE_SUBSTRINGS if (sub in function_name)]:
                if not function_name == function_name.upper():
                    return function_name

        if altering_filters:
            filtered_keyword = check_for_substrings(
                function_name, altering_filters, return_difference=True
            )
            if filtered_keyword:
                return filtered_keyword

        if non_altering_filters:
            filtered_keyword = check_for_substrings(function_name, non_altering_filters)
            if filtered_keyword:
                return filtered_keyword

    def build_keyword_library(
        self,
        package,
        altering_filters=[],
        non_altering_filters=[],
    ):
        for function_name in dir(package):
            filtered_keyword = self.__filter_keyword(
                function_name, altering_filters, non_altering_filters
            )
            if filtered_keyword:
                filtered_keyword = clean_keyword(filtered_keyword)
                function_reference = getattr(package, function_name)
                self.components[filtered_keyword] = function_reference

                params = clean_keywords_list(
                    [
                        param
                        for param in function_reference.__code__.co_varnames
                        if not param in ["args", "kwargs"]
                    ]
                )

                self.parameters = self.parameters + [
                    param for param in params if not param in self.parameters
                ]

                self.component_parameter_relations[filtered_keyword] = params

    def write_to_file(self, file_name):
        """Writes all discovered keywords to the specified file with pretty formatting."""
        string = "# THIS FILE WAS GENERATED AUTOMATICALLY BY JSONTODPG. DO NOT EDIT.\n"
        components = sorted(list(self.components.keys()))
        parameters = sorted(list(self.parameters))
        functions = sorted(list(self.function_keyword_set))

        string += f"#--------------COMPONENTS--------------[{len(components)}]\n"
        for component in components:
            string += f'\n{component} = "{component}"'

        string += f"\n\n#--------------FUNCTIONS--------------[{len(functions)}]\n"
        for func in functions:
            string += f'\n{func} = "{func}"'

        string += f"\n\n#--------------PARAMETERS--------------[{len(parameters)}]\n"
        for param in parameters:
            string += f'\n{param} = "{param}"'

        formatted_relations = pprint.pformat(
            dict(self.component_parameter_relations), indent=4
        )
        string += f"\n\ncomponent_parameter_relations = {formatted_relations}"

        all_keywords = components + functions + parameters
        string += f"\n\n__all__ = {all_keywords}"

        write_to_py_file(file_name=file_name, data=string)
