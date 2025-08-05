import re
from main import htmlcssjs as html

_css_injected = False

def markdown(md_text: str):
    global _css_injected
    if not _css_injected:
        html("""
        <style>
            pre code, code, pre, blockquote {
                border: 1px;
            }
            pre, code, pre code {
                background-color: #efefef !important;
                border: 0px solid rgba(128, 128, 128, 0.2);
                border-radius: 4px;
                font-family: monospace;
                font-size: 0.95em;
                overflow-x: auto;
            }
            .hljs {
                display: block;
                overflow-x: auto;
                padding: 10px 16px;
                background: #efefef;
                color: #333;
                border-radius: 4px;
                margin: 16px 0;
            }
            pre code {
                background-color: transparent !important;
                border: none !important;
            }
            pre {
                background-color: #efefef !important;
                margin: 0;
                margin-bottom: 17px;
                margin-top: 17px;
            }
            code {
                padding: 2px 6px;
            }
            blockquote {
                position: relative;
                padding: 12px 16px 12px 24px;
                background-color: #efefef;
                border-radius: 4px;
                color: #333;
                font-size: 17px;
                margin: 16px 0;
            }

            blockquote::before {
                content: '';
                position: absolute;
                top: 0;
                bottom: 0;
                left: 0;
                width: 6px;
                background-color: #595959;
                border-radius: 4px;
            }

            ul, p, blockquote {
                margin-bottom: 12px;
            }
        </style>
        <link rel="stylesheet"
              href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
        <script>setTimeout(() => hljs.highlightAll(), 100);</script>
        """)
        _css_injected = True

    lines = md_text.strip().split('\n')
    in_code_block = False
    in_list = False
    code_block = []
    html_out = []
    language = ''

    def close_list():
        nonlocal in_list
        if in_list:
            html_out.append('</ul>')
            in_list = False

    for line in lines:
        line = line.rstrip()

        # Code block toggle
        if line.startswith("```"):
            if not in_code_block:
                in_code_block = True
                language = line[3:].strip()
                code_block = []
            else:
                from html import escape

                code_html = escape('\n'.join(code_block))
                html_out.append(f'<pre><code class="hljs language-{language}">{code_html}</code></pre>')

                in_code_block = False
            continue

        if in_code_block:
            code_block.append(line)
            continue

        # Horizontal rules
        if re.match(r'^([\*\-_]\s?){3,}$', line.strip()):
            close_list()
            html_out.append('<hr>')
            continue

        # Headings
        if re.match(r'^#{1,6} ', line):
            close_list()
            level = len(line.split(' ')[0])
            content = line[level+1:].strip()
            html_out.append(f"<h{level}>{content}</h{level}>")
            continue

        # Blockquotes
        if line.startswith('> '):
            close_list()
            content = line[2:].strip()
            html_out.append(f"<blockquote>{content}</blockquote>")
            continue

        # Unordered Lists
        if re.match(r'^[-*+] ', line):
            if not in_list:
                in_list = True
                html_out.append('<ul>')
            item = re.sub(r'^[-*+] ', '', line)
            # Inline formatting
            item = re.sub(r'\*\*\*(.*?)\*\*\*', r'<strong><em>\1</em></strong>', item)
            item = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', item)
            item = re.sub(r'\*(.*?)\*', r'<em>\1</em>', item)
            item = re.sub(r'`(.*?)`', r'<code>\1</code>', item)
            html_out.append(f"<li>{item}</li>")
            continue
        else:
            close_list()

        # Inline formatting for normal paragraphs
        formatted = line
        formatted = re.sub(r'\*\*\*(.*?)\*\*\*', r'<strong><em>\1</em></strong>', formatted)
        formatted = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', formatted)
        formatted = re.sub(r'\*(.*?)\*', r'<em>\1</em>', formatted)
        formatted = re.sub(r'`(.*?)`', r'<code>\1</code>', formatted)

        html_out.append(f"<p>{formatted}</p>")

    close_list()
    html('\n'.join(html_out))

markdown(
    """
# Heading 1
## Heading 2
### Heading 3
#### Heading 4
##### Heading 5
###### Heading 6
This is a paragraph with **bold**, *italic*, and `inline code`.
- List item 1
- List item 2
> Blockquote
```python
print('Hello, world!')
```
```html
<h1>Hello, world!</h1>
```
    """
)