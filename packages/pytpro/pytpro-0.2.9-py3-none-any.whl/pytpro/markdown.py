import re
from .main import htmlcssjs as html
import html as html_lib

_css_injected = False

def markdown(md_text: str):
    global _css_injected
    if not _css_injected:
        html("""
        <style>
            pre code, code, pre, blockquote, table, th, td {
                border: 1px solid #ccc;
            }
            pre, code, pre code {
                background-color: #efefef !important;
                border-radius: 4px;
                font-family: monospace;
                font-size: 0.95em;
                overflow-x: auto;
                border: none !important;
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
            pre {
                background-color: #efefef !important;
                margin: 0 0 17px 0;
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
            ul, ol, p, blockquote, table {
                margin-bottom: 12px;
            }
            table {
                border-collapse: collapse;
                width: 100%;
            }
            th, td {
                padding: 6px 12px;
                text-align: left;
            }
        </style>
        <link rel="stylesheet"
              href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
        <script>setTimeout(() => hljs.highlightAll(), 100);</script>
        """)
        _css_injected = True

    # --- Sanitize Input ---
    md_text = html_lib.unescape(md_text)

    # Remove dangerous tags and attributes (same as before)
    md_text = re.sub(r'<\s*script[^>]*?>.*?<\s*/\s*script\s*>', '', md_text, flags=re.DOTALL | re.IGNORECASE)
    md_text = re.sub(r'<\s*/?\s*script[^>]*?>', '', md_text, flags=re.IGNORECASE)
    md_text = re.sub(r'<\s*(iframe|object|embed|svg)[^>]*?>.*?<\s*/\s*\1\s*>', '', md_text, flags=re.DOTALL | re.IGNORECASE)
    md_text = re.sub(r'<\s*/?\s*(iframe|object|embed|svg)[^>]*?>', '', md_text, flags=re.IGNORECASE)
    md_text = re.sub(r'\son\w+\s*=\s*"[^"]*"', '', md_text, flags=re.IGNORECASE)
    md_text = re.sub(r"\son\w+\s*=\s*'[^']*'", '', md_text, flags=re.IGNORECASE)
    md_text = re.sub(r'(["\'])\s*javascript:[^"\']*\1', r'\1\1', md_text, flags=re.IGNORECASE)
    md_text = re.sub(r'(["\'])\s*data:[^"\']*\1', r'\1\1', md_text, flags=re.IGNORECASE)

    lines = md_text.strip('\n').split('\n')

    # States
    in_code_block = False
    code_block = []
    language = 'plaintext'

    list_stack = []  # stack of ('ul' or 'ol', indent_level)
    table_rows = []
    in_table = False
    html_out = []

    def close_all_lists(min_indent=0):
        # Close lists in stack with indent >= min_indent
        while list_stack and list_stack[-1][1] >= min_indent:
            tag, _ = list_stack.pop()
            html_out.append(f'</{tag}>')

    def close_table():
        nonlocal in_table, table_rows
        if in_table:
            if len(table_rows) > 1:
                header = table_rows[0]
                align_line = table_rows[1]

                aligns = []
                # Parse alignment row
                for cell in [c.strip() for c in align_line.split('|')]:
                    if cell.startswith(':') and cell.endswith(':'):
                        aligns.append('center')
                    elif cell.startswith(':'):
                        aligns.append('left')
                    elif cell.endswith(':'):
                        aligns.append('right')
                    else:
                        aligns.append(None)

                table_rows.pop(1)  # Remove align row

                # Build table html
                html_out.append('<table>')
                html_out.append('<thead><tr>')
                header_cells = [c.strip() for c in header.split('|')]
                for i, cell in enumerate(header_cells):
                    align_attr = f' style="text-align:{aligns[i]}"' if i < len(aligns) and aligns[i] else ''
                    html_out.append(f'<th{align_attr}>{cell}</th>')
                html_out.append('</tr></thead><tbody>')

                for row in table_rows[1:]:
                    html_out.append('<tr>')
                    cells = [c.strip() for c in row.split('|')]
                    # Pad cells if missing
                    while len(cells) < len(header_cells):
                        cells.append('')
                    for i, cell in enumerate(cells):
                        align_attr = f' style="text-align:{aligns[i]}"' if i < len(aligns) and aligns[i] else ''
                        html_out.append(f'<td{align_attr}>{cell}</td>')
                    html_out.append('</tr>')
                html_out.append('</tbody></table>')
            else:
                # Not a valid table, output rows as paragraphs
                for row in table_rows:
                    html_out.append(f'<p>{row}</p>')
            table_rows = []
            in_table = False

    def inline_format(text):
        # Escape HTML
        from html import escape
        text = escape(text)

        # Escaping markdown chars with backslash
        text = re.sub(r'\\([\\`\*_\{\}\[\]\(\)#\+\-\.\!~>])', r'\1', text)

        # Links: [text](url "optional title")
        # Support optional title in quotes
        def repl_link(m):
            text, url, title = m.group(1), m.group(2), m.group(4)
            title_attr = f' title="{escape(title)}"' if title else ''
            url = url.strip()
            return f'<a href="{escape(url)}"{title_attr} target="_blank" rel="noopener noreferrer">{text}</a>'

        text = re.sub(r'\[([^\]]+)\]\(\s*([^\s\)]+)(\s+"([^"]+)")?\s*\)', repl_link, text)

        # Images: ![alt](url "optional title")
        def repl_img(m):
            alt, url, title = m.group(1), m.group(2), m.group(4)
            title_attr = f' title="{escape(title)}"' if title else ''
            return f'<img src="{escape(url.strip())}" alt="{escape(alt)}"{title_attr} />'

        text = re.sub(r'!\[([^\]]*)\]\(\s*([^\s\)]+)(\s+"([^"]+)")?\s*\)', repl_img, text)

        # Strikethrough
        text = re.sub(r'~~(.*?)~~', r'<del>\1</del>', text)

        # Bold + Italic (***text***)
        text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', text)

        # Bold (**text**)
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)

        # Italic (*text*)
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)

        # Inline code (`code`)
        text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)

        # Convert two spaces at line end into <br>
        text = re.sub(r'  $', r'<br>', text)

        return text
    blockquote_level = 0
    paragraph_lines = []

    def flush_paragraph():
        nonlocal paragraph_lines
        if paragraph_lines:
            html_out.append(f'<p>{" ".join(paragraph_lines)}</p>')
            paragraph_lines = []

    for idx, line in enumerate(lines):
        line_rstrip = line.rstrip('\r\n')

        # Code block toggle
        if line_rstrip.startswith("```"):
            flush_paragraph()
            close_all_lists()
            close_table()
            if not in_code_block:
                in_code_block = True
                language = line_rstrip[3:].strip()
                code_block = []
            else:
                from html import escape
                code_html = escape('\n'.join(code_block))
                html_out.append(f'<pre><code class="hljs language-{language}">{code_html}</code></pre>')
                in_code_block = False
            continue
        # Inside your main loop, replace this blockquote handling part:

        m = re.match(r'^(>+)\s+(.*)', line)
        if m:
            flush_paragraph()
            close_all_lists()
            close_table()
            new_level = len(m.group(1))
            content = inline_format(m.group(2).strip())

            # Adjust blockquote level:
            while blockquote_level < new_level:
                html_out.append('<blockquote>')
                blockquote_level += 1
            while blockquote_level > new_level:
                html_out.append('</blockquote>')
                blockquote_level -= 1
            
            html_out.append(content)
            continue
        else:
            # Close all blockquotes if we leave blockquote lines
            while blockquote_level > 0:
                html_out.append('</blockquote>')
                blockquote_level -= 1
        # Tables
        if re.match(r'^\s*\|.*\|\s*$', line):
            flush_paragraph()
            if not in_table:
                close_all_lists()
                in_table = True
                table_rows = []
            table_rows.append(line.strip())
            continue
        else:
            if in_table:
                flush_paragraph()
                close_table()

        # Horizontal rules
        if re.match(r'^([\*\-_]\s?){3,}$', line.strip()):
            flush_paragraph()
            close_all_lists()
            close_table()
            html_out.append('<hr>')
            continue

        # Headings
        m = re.match(r'^(#{1,6})\s+(.*)', line)
        if m:
            flush_paragraph()
            close_all_lists()
            close_table()
            level = len(m.group(1))
            content = inline_format(m.group(2).strip())
            html_out.append(f'<h{level}>{content}</h{level}>')
            continue

        # Ordered list detection with indentation for nesting
        m = re.match(r'^(\s*)(\d+)\.\s+(.*)', line)
        if m:
            flush_paragraph()
            close_table()
            indent = len(m.group(1).replace('\t', '    '))
            # Close lists with indent >= current
            close_all_lists(min_indent=indent)
            if not list_stack or list_stack[-1][0] != 'ol' or list_stack[-1][1] < indent:
                html_out.append('<ol>')
                list_stack.append(('ol', indent))
            item_text = inline_format(m.group(3).strip())
            html_out.append(f'<li>{item_text}</li>')
            continue

        # Unordered list detection with indentation for nesting
        m = re.match(r'^(\s*)[-*+]\s+(.*)', line)
        if m:
            flush_paragraph()
            close_table()
            indent = len(m.group(1).replace('\t', '    '))
            close_all_lists(min_indent=indent)
            if not list_stack or list_stack[-1][0] != 'ul' or list_stack[-1][1] < indent:
                html_out.append('<ul>')
                list_stack.append(('ul', indent))

            item_text = inline_format(m.group(2).strip())

            # Task list support
            task_match = re.match(r'^\[( |x|X)\]\s+(.*)', item_text)
            if task_match:
                checked = 'checked' if task_match.group(1).lower() == 'x' else ''
                item_text = task_match.group(2)
                html_out.append(f'<li><input type="checkbox" disabled {checked}/> {item_text}</li>')
            else:
                html_out.append(f'<li>{item_text}</li>')
            continue

        # Not list, close any open lists at this indent
        close_all_lists()

        # ... inside your main loop, instead of the old paragraph handling:

        if not line.strip():
            flush_paragraph()
        else:
            paragraph_lines.append(inline_format(line.strip()))

        # Also, before any block elements (headings, lists, blockquotes, code blocks, tables, horizontal rules),
        # call flush_paragraph() to close any open paragraph.

        # At the very end of the loop, after processing all lines, call:
    flush_paragraph()
    close_all_lists()
    close_table()

    html('\n'.join(html_out))
