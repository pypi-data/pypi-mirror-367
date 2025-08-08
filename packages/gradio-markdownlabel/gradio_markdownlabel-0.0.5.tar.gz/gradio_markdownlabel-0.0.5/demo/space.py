
import gradio as gr
from app import demo as app
import os

_docs = {'MarkdownLabel': {'description': 'Displays markdown-formatted text with interactive term highlighting and detailed side panel.\n\nThis component allows for rich markdown content with clickable term highlights that display\ndetailed information in a side panel.', 'members': {'__init__': {'value': {'type': 'dict | Callable | None', 'default': 'None', 'description': 'Dictionary containing markdown_content and highlights array. If a function is provided, the function will be called each time the app loads to set the initial value of this component.'}, 'show_side_panel': {'type': 'bool', 'default': 'True', 'description': 'Whether to show the detailed information side panel.'}, 'panel_width': {'type': 'str', 'default': '"300px"', 'description': 'Width of the side panel (CSS value like "300px", "25%", etc.).'}, 'edit_mode': {'type': 'str', 'default': '"split"', 'description': 'Layout for editing mode - "split" (side-by-side), "tabs", or "overlay".'}, 'show_preview': {'type': 'bool', 'default': 'True', 'description': 'Whether to show live preview in edit mode.'}, 'markdown_editor': {'type': 'str', 'default': '"textarea"', 'description': 'Type of markdown editor - "textarea" or "codemirror" (future).'}, 'label': {'type': 'str | I18nData | None', 'default': 'None', 'description': 'the label for this component. Appears above the component and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component is assigned to.'}, 'every': {'type': 'Timer | float | None', 'default': 'None', 'description': 'Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.'}, 'inputs': {'type': 'Component | Sequence[Component] | set[Component] | None', 'default': 'None', 'description': 'Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.'}, 'show_label': {'type': 'bool | None', 'default': 'None', 'description': 'if True, will display label.'}, 'container': {'type': 'bool', 'default': 'True', 'description': 'If True, will place the component in a container - providing some extra padding around the border.'}, 'scale': {'type': 'int | None', 'default': 'None', 'description': 'relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.'}, 'min_width': {'type': 'int', 'default': '160', 'description': 'minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.'}, 'visible': {'type': 'bool', 'default': 'True', 'description': 'If False, component will be hidden.'}, 'elem_id': {'type': 'str | None', 'default': 'None', 'description': 'An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.'}, 'elem_classes': {'type': 'list[str] | str | None', 'default': 'None', 'description': 'An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.'}, 'render': {'type': 'bool', 'default': 'True', 'description': 'If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.'}, 'key': {'type': 'int | str | tuple[int | str, ...] | None', 'default': 'None', 'description': "in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render."}, 'preserved_by_key': {'type': 'list[str] | str | None', 'default': '"value"', 'description': "A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor."}, 'interactive': {'type': 'bool | None', 'default': 'None', 'description': 'If True, the component will be editable allowing users to modify markdown content.'}, 'rtl': {'type': 'bool', 'default': 'False', 'description': 'If True, will display the text in right-to-left direction.'}}, 'postprocess': {'value': {'type': 'dict | None', 'description': "Expects a dictionary with 'markdown_content' and 'highlights' keys"}}, 'preprocess': {'return': {'type': 'dict | None', 'description': 'Passes the value as a dictionary with markdown_content and highlights.'}, 'value': None}}, 'events': {'change': {'type': None, 'default': None, 'description': 'Triggered when the value of the MarkdownLabel changes either because of user input (e.g. a user types in a textbox) OR because of a function update (e.g. an image receives a value from the output of an event trigger). See `.input()` for a listener that is only triggered by user input.'}, 'select': {'type': None, 'default': None, 'description': 'Event listener for when the user selects or deselects the MarkdownLabel. Uses event data gradio.SelectData to carry `value` referring to the label of the MarkdownLabel, and `selected` to refer to state of the MarkdownLabel. See EventData documentation on how to use this event data'}, 'edit': {'type': None, 'default': None, 'description': 'This listener is triggered when the user edits the MarkdownLabel (e.g. image) using the built-in editor.'}, 'submit': {'type': None, 'default': None, 'description': 'This listener is triggered when the user presses the Enter key while the MarkdownLabel is focused.'}, 'clear': {'type': None, 'default': None, 'description': 'This listener is triggered when the user clears the MarkdownLabel using the clear button for the component.'}}}, '__meta__': {'additional_interfaces': {}, 'user_fn_refs': {'MarkdownLabel': []}}}

abs_path = os.path.join(os.path.dirname(__file__), "css.css")

with gr.Blocks(
    css=abs_path,
    theme=gr.themes.Default(
        font_mono=[
            gr.themes.GoogleFont("Inconsolata"),
            "monospace",
        ],
    ),
) as demo:
    gr.Markdown(
"""
# `gradio_markdownlabel`

<div style="display: flex; gap: 7px;">
<a href="https://pypi.org/project/gradio_markdownlabel/" target="_blank"><img alt="PyPI - Version" src="https://img.shields.io/pypi/v/gradio_markdownlabel"></a>  
</div>

Python library for easily interacting with trained machine learning models
""", elem_classes=["md-custom"], header_links=True)
    app.render()
    gr.Markdown(
"""
## Installation

```bash
pip install gradio_markdownlabel
```

## Usage

```python

import gradio as gr
from gradio_markdownlabel import MarkdownLabel

with gr.Blocks(title="Markdown Label Demo") as demo:
    gr.Markdown("# MarkdownLabel Component Demo")
    
    # Simple position-based example
    example = {
        "markdown_content": \"\"\"# Comprehensive Markdown Example

## Introduction
*The* quick **brown fox** jumps over the lazy dog. This is a simple quick example with various **formatting** elements.

### Lists and Items
Here are some important points:

1. **First item** - This is the primary consideration
2. *Second item* - Another important point  
3. Third item with `inline code`
4. Fourth item containing [a link](https://example.com)
\"\"\", 
        "highlights": [
            {
                "position": [56, 61],  # "quick" in "The quick brown fox", note the 2nd quick is not highlighted
                "title": "Quick",
                "content": "Highlighted using exact character positions.",
                "category": "Position Demo",
                "color": "#ffeb3b"
            },
            {
                "term": "brown fox",
                "title": "Brown Fox (Term Match)",
                "content": "Highlighted using term matching - will match anywhere this term appears.",
                "category": "Term Demo", 
                "color": "#e3f2fd"
            },
            {
                "position": [91, 95],  # "lazy" in "the lazy dog"
                "title": "Lazy", 
                "content": "Position-based highlight",
                "category": "Position Demo",
                "color": "#ffeb3b"
            }
        ]
    }
    
    gr.Markdown("## Position vs Term Highlighting Comparison")
    gr.Markdown("This example shows the difference between position-based (yellow) and term-based (blue) highlighting.")
    MarkdownLabel(
        value=example,
        label="Simple Position vs Term Example",
        show_side_panel=True,
        panel_width="300px",
        interactive=True
    )

if __name__ == "__main__":
    demo.launch()

```
""", elem_classes=["md-custom"], header_links=True)


    gr.Markdown("""
## `MarkdownLabel`

### Initialization
""", elem_classes=["md-custom"], header_links=True)

    gr.ParamViewer(value=_docs["MarkdownLabel"]["members"]["__init__"], linkify=[])


    gr.Markdown("### Events")
    gr.ParamViewer(value=_docs["MarkdownLabel"]["events"], linkify=['Event'])




    gr.Markdown("""

### User function

The impact on the users predict function varies depending on whether the component is used as an input or output for an event (or both).

- When used as an Input, the component only impacts the input signature of the user function.
- When used as an output, the component only impacts the return signature of the user function.

The code snippet below is accurate in cases where the component is used as both an input and an output.

- **As input:** Is passed, passes the value as a dictionary with markdown_content and highlights.
- **As output:** Should return, expects a dictionary with 'markdown_content' and 'highlights' keys.

 ```python
def predict(
    value: dict | None
) -> dict | None:
    return value
```
""", elem_classes=["md-custom", "MarkdownLabel-user-fn"], header_links=True)




    demo.load(None, js=r"""function() {
    const refs = {};
    const user_fn_refs = {
          MarkdownLabel: [], };
    requestAnimationFrame(() => {

        Object.entries(user_fn_refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}-user-fn`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })

        Object.entries(refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })
    })
}

""")

demo.launch()
