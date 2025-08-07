
# JsonToDpg

**Build [DearPyGui](https://github.com/hoffstadt/DearPyGui) user interfaces declaratively with a powerful, keyword-driven Python dictionary syntax.**

JsonToDpg is a utility that transforms the process of building GUIs. It allows you to define complex graphical user interfaces using a simple, readable data structure that separates UI layout from application logic, making your code cleaner, more modular, and easier to maintain.

## Features

*   **Fully Declarative UI:** Define your entire UI with a nested Python dictionary using clean, code-completed keywords for every component, parameter, and function call.
*   **Automatic Keyword System:** The library automatically discovers all functions from DearPyGui, the built-in controller, and your custom plugins. No more "magic strings"!
*   **Self-Healing Keywords for IDEs:** The library automatically generates a `dpgkeywords.py` file in the background if it's missing or out of date. Your script runs correctly the first time, and on subsequent edits, your IDE will provide full code completion.
*   **Reactive UI with Monitors:** A powerful "monitor" system allows your UI elements to automatically update when your underlying data changes, dramatically simplifying state management.
*   **Integrated Controller:** A rich controller gives you full access to the UI at runtime. Get/set values, show/hide items, manage application state, and even dynamically create new UI elements.
*   **Plugin Architecture:** Extend the library's capabilities by adding your own custom classes as plugins. Their public methods are automatically exposed as keywords.

## Installation

```bash
pip install jsontodpg
```

## Quick Start: The Automatic Way

This is the recommended workflow. It's a single, self-contained script that works on the first run and provides IDE benefits on the second.

**`main.py`**
```python
from jsontodpg import JsonToDpg

# 1. Initialize the library.
#    By default, this will automatically check and regenerate dpgkeywords.py
#    in the background if needed.
jtd = JsonToDpg()

# 2. Create a convenience alias for the keyword accessor.
#    This object provides access to all components, parameters, and functions.
k = jtd.keywords

# 3. Define the UI using the keyword accessor for EVERYTHING.
main_ui = {
    # SETUP PHASE: Call controller functions directly as keywords.
    "setup_calls": [
        { k.put: ["message", "Hello, Keywords!"] },
        { k.add_monitor: ["message", "monitored_text"] }
    ],

    # UI LAYOUT: Use keywords for components and their parameters.
    k.viewport: { k.width: 800, k.height: 400, k.title: "JsonToDpg Demo" },
    
    k.window: {
        k.label: "Keyword Demo",
        k.width: 780,
        k.height: 380,

        "children": [
            { k.text: { k.tag: "monitored_text" } },
            { k.separator: {} },
            {
                k.button: {
                    k.label: "Update the Monitored Text",
                    # CALLBACKS: Also use keywords for the function to call.
                    k.callback: { k.put: ["message", "The store was updated successfully!"] }
                }
            }
        ]
    }
}

# 4. Start the application.
jtd.start(main_ui)
```
*The first time you run this, you may see a message that `dpgkeywords.py` was created. Your IDE (like VS Code) will then be able to provide code completion for `k.*`.*

## Configuration

The `JsonToDpg` constructor accepts several parameters to customize its behavior.

```python
jtd = JsonToDpg(
    debug=False,
    plugins=[],
    auto_generate_keywords=True
)
```
-   `debug`: `(bool)` - If `True`, shows the DearPyGui metrics window.
-   `plugins`: `(list)` - A list of custom classes to register as plugins.
-   `auto_generate_keywords`: `(bool)` - **Defaults to `True`**. If `True`, the library will automatically create or update the `dpgkeywords.py` file. Set this to `False` in production environments or if you prefer a fully manual, static workflow.

## Core Concepts

### The Keyword Accessor (`k`)

The `jtd.keywords` object (aliased as `k`) is your entry point to the entire library. It magically returns the string name of any attribute you access, eliminating the need for string literals and enabling static analysis by your IDE. You use it for:
- **Components:** `k.window`, `k.button`, `k.slider_int`
- **Parameters:** `k.label`, `k.width`, `k.callback`, `k.tag`
- **Controller/Plugin Functions:** `k.put`, `k.add_monitor`, `k.hide`, `k.my_plugin_method`

### Reactive UI with Monitors

The monitor system creates a link between your data store and your UI.

1.  **Store Data:** Use `k.put` to store data in a central model.
    `{ k.put: ["player_level", 50] }`
2.  **Register a Monitor:** Use `k.add_monitor` to tell a UI element to watch a key in the store.
    `{ k.add_monitor: ["player_level", "level_display_tag"] }`
3.  **Update Data:** When you use `k.put` to change `player_level`, any UI element with the tag `level_display_tag` will update its value automatically.

### Plugins

Extend the library by creating your own classes. Their public methods will be automatically discovered and made available as keywords.

**`my_plugin.py`**
```python
class MyPlugin:
    def __init__(self):
        # JsonToDpg will automatically provide the controller instance here.
        self.controller = None

    def log_to_console(self, message):
        print(f"MyPlugin says: {message}")
```

**`main.py`**
```python
from jsontodpg import JsonToDpg
from my_plugin import MyPlugin

jtd = JsonToDpg(plugins=[MyPlugin])
k = jtd.keywords

main_ui = {
    k.window: {
        k.button: {
            k.label: "Call Plugin",
            # The plugin's method is now available as a keyword!
            k.callback: { k.log_to_console: ["Hello from my plugin!"] }
        }
    }
}
# ... start app ...
```

### The Optional Static Workflow

If you prefer to have a static, importable file for keywords (for example, in a large, multi-file project), you can use the explicit generation method.

**1. Create `generate_keywords.py`:**
```python
from jsontodpg import JsonToDpg
# from my_plugin import MyPlugin # Import your plugins here

# This script's only job is to create the keyword file.
jtd = JsonToDpg(plugins=[...])
jtd.generate_keywords_file("dpgkeywords")
```

**2. In your main app, import the keywords:**
```python
from jsontodpg import JsonToDpg
from dpgkeywords import * # Import the generated keywords

jtd = JsonToDpg()

# Now you can use the keywords directly without the accessor.
main_ui = {
    window: { label: "Static Keywords" },
    # ... etc
}
```