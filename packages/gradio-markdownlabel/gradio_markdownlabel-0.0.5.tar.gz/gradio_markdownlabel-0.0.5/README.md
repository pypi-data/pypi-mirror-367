---
tags: [gradio-custom-component, HighlightedText]
title: gradio_markdownlabel
short_description: A gradio custom component
colorFrom: blue
colorTo: yellow
sdk: gradio
pinned: false
app_file: space.py
---

# `gradio_markdownlabel`
<a href="https://pypi.org/project/gradio_markdownlabel/" target="_blank"><img alt="PyPI - Version" src="https://img.shields.io/pypi/v/gradio_markdownlabel"></a>  

Python library for easily interacting with trained machine learning models

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
        "markdown_content": """# Comprehensive Markdown Example

## Introduction
*The* quick **brown fox** jumps over the lazy dog. This is a simple quick example with various **formatting** elements.

### Lists and Items
Here are some important points:

1. **First item** - This is the primary consideration
2. *Second item* - Another important point  
3. Third item with `inline code`
4. Fourth item containing [a link](https://example.com)


""", 
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

## `MarkdownLabel`

### Initialization

<table>
<thead>
<tr>
<th align="left">name</th>
<th align="left" style="width: 25%;">type</th>
<th align="left">default</th>
<th align="left">description</th>
</tr>
</thead>
<tbody>
<tr>
<td align="left"><code>value</code></td>
<td align="left" style="width: 25%;">

```python
dict | Callable | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">Dictionary containing markdown_content and highlights array. If a function is provided, the function will be called each time the app loads to set the initial value of this component.</td>
</tr>

<tr>
<td align="left"><code>show_side_panel</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">Whether to show the detailed information side panel.</td>
</tr>

<tr>
<td align="left"><code>panel_width</code></td>
<td align="left" style="width: 25%;">

```python
str
```

</td>
<td align="left"><code>"300px"</code></td>
<td align="left">Width of the side panel (CSS value like "300px", "25%", etc.).</td>
</tr>

<tr>
<td align="left"><code>edit_mode</code></td>
<td align="left" style="width: 25%;">

```python
str
```

</td>
<td align="left"><code>"split"</code></td>
<td align="left">Layout for editing mode - "split" (side-by-side), "tabs", or "overlay".</td>
</tr>

<tr>
<td align="left"><code>show_preview</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">Whether to show live preview in edit mode.</td>
</tr>

<tr>
<td align="left"><code>markdown_editor</code></td>
<td align="left" style="width: 25%;">

```python
str
```

</td>
<td align="left"><code>"textarea"</code></td>
<td align="left">Type of markdown editor - "textarea" or "codemirror" (future).</td>
</tr>

<tr>
<td align="left"><code>label</code></td>
<td align="left" style="width: 25%;">

```python
str | I18nData | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">the label for this component. Appears above the component and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component is assigned to.</td>
</tr>

<tr>
<td align="left"><code>every</code></td>
<td align="left" style="width: 25%;">

```python
Timer | float | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.</td>
</tr>

<tr>
<td align="left"><code>inputs</code></td>
<td align="left" style="width: 25%;">

```python
Component | Sequence[Component] | set[Component] | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.</td>
</tr>

<tr>
<td align="left"><code>show_label</code></td>
<td align="left" style="width: 25%;">

```python
bool | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">if True, will display label.</td>
</tr>

<tr>
<td align="left"><code>container</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If True, will place the component in a container - providing some extra padding around the border.</td>
</tr>

<tr>
<td align="left"><code>scale</code></td>
<td align="left" style="width: 25%;">

```python
int | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.</td>
</tr>

<tr>
<td align="left"><code>min_width</code></td>
<td align="left" style="width: 25%;">

```python
int
```

</td>
<td align="left"><code>160</code></td>
<td align="left">minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.</td>
</tr>

<tr>
<td align="left"><code>visible</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If False, component will be hidden.</td>
</tr>

<tr>
<td align="left"><code>elem_id</code></td>
<td align="left" style="width: 25%;">

```python
str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.</td>
</tr>

<tr>
<td align="left"><code>elem_classes</code></td>
<td align="left" style="width: 25%;">

```python
list[str] | str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.</td>
</tr>

<tr>
<td align="left"><code>render</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.</td>
</tr>

<tr>
<td align="left"><code>key</code></td>
<td align="left" style="width: 25%;">

```python
int | str | tuple[int | str, ...] | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.</td>
</tr>

<tr>
<td align="left"><code>preserved_by_key</code></td>
<td align="left" style="width: 25%;">

```python
list[str] | str | None
```

</td>
<td align="left"><code>"value"</code></td>
<td align="left">A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.</td>
</tr>

<tr>
<td align="left"><code>interactive</code></td>
<td align="left" style="width: 25%;">

```python
bool | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">If True, the component will be editable allowing users to modify markdown content.</td>
</tr>

<tr>
<td align="left"><code>rtl</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>False</code></td>
<td align="left">If True, will display the text in right-to-left direction.</td>
</tr>
</tbody></table>


### Events

| name | description |
|:-----|:------------|
| `change` | Triggered when the value of the MarkdownLabel changes either because of user input (e.g. a user types in a textbox) OR because of a function update (e.g. an image receives a value from the output of an event trigger). See `.input()` for a listener that is only triggered by user input. |
| `select` | Event listener for when the user selects or deselects the MarkdownLabel. Uses event data gradio.SelectData to carry `value` referring to the label of the MarkdownLabel, and `selected` to refer to state of the MarkdownLabel. See EventData documentation on how to use this event data |
| `edit` | This listener is triggered when the user edits the MarkdownLabel (e.g. image) using the built-in editor. |
| `submit` | This listener is triggered when the user presses the Enter key while the MarkdownLabel is focused. |
| `clear` | This listener is triggered when the user clears the MarkdownLabel using the clear button for the component. |



### User function

The impact on the users predict function varies depending on whether the component is used as an input or output for an event (or both).

- When used as an Input, the component only impacts the input signature of the user function.
- When used as an output, the component only impacts the return signature of the user function.

The code snippet below is accurate in cases where the component is used as both an input and an output.

- **As output:** Is passed, passes the value as a dictionary with markdown_content and highlights.
- **As input:** Should return, expects a dictionary with 'markdown_content' and 'highlights' keys.

 ```python
 def predict(
     value: dict | None
 ) -> dict | None:
     return value
 ```
 
