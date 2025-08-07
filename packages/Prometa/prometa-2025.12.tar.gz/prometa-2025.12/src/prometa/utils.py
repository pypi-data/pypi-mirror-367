#!/usr/bin/env python3
"""
Utility functions.
"""

import logging
import textwrap

LOGGER = logging.getLogger(__name__)


def choose(items, include_none=False):
    """
    Prompt the user to choose an item from an iterable of items.

    Args:
        items:
            The iterable of items.

        include_none:
            If True, allow the user to choose None even if it is not in the
            list.

    Returns:
        The chosen item.
    """
    items = sorted(items)
    if include_none and None not in items:
        items.append(None)
    if not items:
        LOGGER.warning("No items to choose.")
        return None
    n_items = len(items)
    if n_items == 1:
        return items[0]
    while True:
        print("Choose one of the following:")
        for i, item in enumerate(items, start=1):
            print(f"{i:d} {item}")
        choice = input(f"Enter an integer in the range 1-{n_items:d} and press enter. ")
        try:
            choice = int(choice)
        except ValueError:
            LOGGER.error('"%s" is not a valid integer.', choice)
            continue
        if choice < 1 or choice > n_items:
            LOGGER.error("Invalid choice.")
            continue
        return items[choice - 1]


def format_docstring_for_cell(docstring):
    """
    Format a docstring for a table cell. This just dedents the block, replaces
    newlines and handles reStructuredText links. At the time of writting, none
    of the proposed packages for converting docstrings to Markdown worked
    reliably.

    Args:
        docstring:
            The docstring.

    Returns:
        The docstring content as a single-line Markdown string that may contain
        ``<br />`` tags.

    TODO:
        Replace this with a reliable function to convert a docstring to either
        Markdown or HTML.
    """
    content = []
    links = {}
    link_prefix = ".. _"
    link_prefix_len = len(link_prefix)
    for line in docstring.splitlines():
        line = line.rstrip()
        sline = line.lstrip()
        if sline.startswith(link_prefix):
            name, url = sline[link_prefix_len:].split(": ", 1)
            links[name] = url
        else:
            content.append(line)
    content = "\n".join(content)
    for name, url in links.items():
        content = content.replace(f"`{name}`_", f"[{name}]({url})")
    content = content.replace("``", "`").rstrip()
    return textwrap.dedent(content).strip().replace("\n", "<br />")
