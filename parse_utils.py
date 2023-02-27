import re

def parse_text_tag(element):
    """
    Parses the text inside tags that are used to format text. It returns a string with the formatted text inside the tag.

    The actual list is: <p>, <a>, <code>, pre, <img>
    """
    if type(element) is str:
        return element

    # Check if element is a paragraph
    if element.name == 'p':
        texts = []
        for inner_tag in element.contents:
            text = parse_text_tag(inner_tag)
            texts.append(text)
        return ''.join(texts)

    # Check if element is an anchor
    if element.name == 'a':
        return f'<{element.get("href")}|{element.text}>'

    # Check if element is a code tag
    if element.name == 'code':
        return f'`{element.text}`'

    # Check if element is a formatted text tag
    if element.name == 'pre':
        return f'```\n{element.text}\n```'

    # Check if element is an image tag
    if element.name == 'img':
        return f'[IMAGE] -> ({element.get("src")})'

    return element.text

def parse_inner_tag(element):
    """
    Parses a tag that is inside another tag, generally used for <ul> and <li> tags.

    Returns a list with the strings formatted inside each inner tag of this tag.
    """
    # Check if element is a list item
    if element.name == 'li':
        texts = []
        for inner_tag in element.contents:
            parsed = parse_inner_tag(inner_tag)
            for p in parsed:
                texts.append(p)
        return texts

    # Check if element is an unordered list
    elif element.name == 'ul':
        texts = []
        for li in element.find_all('li'):
            parsed_li = ''.join(parse_inner_tag(li)).strip()
            texts.append(f"-\t _{parsed_li}_\n")
        return texts
    
    return [parse_text_tag(element)]

def parse_tag(element):
    """
    Parse a tag recursively. Returns a list of strings with the lines required to print this tag correctly.

    Currently supported tags: h1-h6, blockquote, ul, li, p, a
    """
    # Check if element belongs to the content section
    if not element.parent.name == 'div' or not element.parent.has_attr('class') or not 'content' in element.parent['class']:
        return []

    # Check if element is a heading
    if re.match(r'^h[1-6]$', element.name):
        heading_number = int(element.name[-1])
        heading_text = element.text.replace('\n', '')
        return [f"*{'-'*(4-heading_number)} {heading_text} {'-'*(4-heading_number)}*\n"]

    # Check if element is a quote
    elif element.name == 'blockquote':
        quote_text = element.text.replace('\n', ' ')
        return [f"```\n{quote_text}\n```\n"]
    
    # Check if element is an unordered list
    elif element.name == 'ul':
        texts = []
        for li in element.find_all('li', recursive=False):
            parsed_li = ''.join(parse_inner_tag(li)).strip()
            texts.append(f"- _{parsed_li}_\n")
        return texts

    # Check if element is a pararaph from the content div
    elif element.name == 'p':
        texts = []
        for parsed_tag in parse_inner_tag(element):
            texts.append(parsed_tag)
        return [f'{"".join(texts)}\n']

    # Check if element is an anchor from the content div
    elif element.name == 'a':
        return [f'[LINK] -> ({element.get("href")})\n']

    # Default case
    return []
