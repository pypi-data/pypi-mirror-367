import threading
import queue
from collections import defaultdict

class Controller:
    def __init__(self, jsontodpg):
        self.jsontodpg = jsontodpg
        self.model = jsontodpg.model
        self.ui_update_queue = queue.Queue()
        self.monitors = defaultdict(list)
        self.add_async_function(
            interval=1, function=self._process_ui_updates, name="UI Queue Processor"
        )

    def spawn(self, json_data, parent=None):
        """Dynamically creates new UI elements under a specified parent."""
        self.jsontodpg.parse(json_data, parent=parent)

    def add_monitor(self, store_key, ui_tag, formatter=None):
        print(f"Adding monitor: store_key='{store_key}' -> ui_tag='{ui_tag}'")
        for monitor in self.monitors[store_key]:
            if monitor["tag"] == ui_tag:
                print("Info: Monitor already exists.")
                return

        monitor_info = {"tag": ui_tag, "formatter": formatter}
        self.monitors[store_key].append(monitor_info)

        if self.store_contains(store_key):
            current_value = self.get(store_key)
            self._update_monitored_item(monitor_info, current_value)

    def remove_monitor(self, store_key, ui_tag):
        print(f"Removing monitor: store_key='{store_key}' -> ui_tag='{ui_tag}'")
        if store_key in self.monitors:
            self.monitors[store_key] = [
                m for m in self.monitors[store_key] if m.get("tag") != ui_tag
            ]
            if not self.monitors[store_key]:
                del self.monitors[store_key]

    def _update_monitored_item(self, monitor_info, value):
        tag = monitor_info["tag"]
        formatter = monitor_info["formatter"]
        if self.component_exists(tag):
            display_value = formatter(value) if formatter else value
            self.set_value(tag, display_value)

    def put(self, key_path, value):
        final_value = value() if callable(value) else value
        old_value = self.model.get(key_path)
        if old_value == final_value:
            return

        self.model[key_path] = final_value

        if key_path in self.monitors:
            for monitor_info in self.monitors[key_path]:
                self._update_monitored_item(monitor_info, final_value)

    def _process_ui_updates(self):
        while not self.ui_update_queue.empty():
            try:
                widget_tag, value = self.ui_update_queue.get_nowait()
                if self.jsontodpg.dpg.does_item_exist(widget_tag):
                    self.jsontodpg.dpg.set_value(widget_tag, value)
            except queue.Empty:
                break
            except Exception as e:
                print(f"Error processing UI update queue: {e}")

    def add_threaded_task(self, function, *args):
        thread = threading.Thread(target=function, args=args, daemon=True)
        thread.start()

    def hide(self, tag):
        if self.component_exists(tag): self.jsontodpg.dpg.hide_item(tag)

    def show(self, tag):
        if self.component_exists(tag): self.jsontodpg.dpg.show_item(tag)

    def component_exists(self, tag):
        return self.jsontodpg.dpg.does_item_exist(tag)

    def get_label_text(self, tag):
        if self.component_exists(tag): return self.jsontodpg.dpg.get_item_label(tag)

    def get_value(self, tag):
        if self.component_exists(tag): return self.jsontodpg.dpg.get_value(tag)

    def set_value(self, tag, value):
        if self.component_exists(tag): self.jsontodpg.dpg.set_value(tag, value)

    def get_state(self, tag):
        if self.component_exists(tag): return self.jsontodpg.dpg.get_item_state(tag)

    def delete_element(self, tag):
        if self.component_exists(tag): self.jsontodpg.dpg.delete_item(tag)

    def delete_all(self, tags=[]):
        for tag in tags:
            self.delete_element(tag)

    def store_contains(self, key_path):
        return key_path in self.model

    def get(self, key_path):
        return self.model.get(key_path)

    def list_to_sublists(self, main_list, sub_list_size=4):
        return [
            main_list[x : x + sub_list_size]
            for x in range(0, len(main_list), sub_list_size)
        ]

    def add_async_function(
        self,
        interval,
        function,
        end_condition=None,
        pause_condition=None,
        num_cycles=0,
        name=None,
    ):
        self.jsontodpg.add_async_function(
            interval, function, end_condition, pause_condition, num_cycles, name
        )