
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

#### Unordered Lists
- Bullet point one
- Bullet point two with **bold text**
- Final bullet point

### Code Block Example
```python
def hello_world():
    print("Hello, World!")
    return "success"
```

### Tables
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Cell 1   | Cell 2   | Cell 3   |
| Data A   | Data B   | Data C   |

### Blockquotes
> This is a blockquote with some **important** information.
> 
> It can span multiple lines and contain *emphasis*.

### Mixed Content
The document contains various **formatting** options including:

- *Italicized text* for emphasis
- **Bold text** for importance  
- `Inline code` for technical terms
- Links like [this one](https://example.com)

#### Final Section
This concludes our comprehensive example with multiple markdown elements for testing position-based highlighting accuracy.""", 
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
            },
            {
                "position": [989, 999],
                "title": "Italicized",
                "content": "Highlighting 'Italicized'",
                "category": "Position Demo", 
                "color": "#ff9800"
            },
            {
                "term": "formatting",
                "title": "formatting (Term Match)",
                "content": "Highlighted using term matching - will match anywhere this term appears.",
                "category": "Term Demo", 
                "color": "#d0167f91"
            },
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
