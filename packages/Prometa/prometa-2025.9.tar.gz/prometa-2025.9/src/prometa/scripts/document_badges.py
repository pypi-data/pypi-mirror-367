#!/usr/bin/env python3
"""\
Print documentation of all recognized badges.\
"""

import logging
import textwrap

# Import it from badges instead of badges.base to ensure that all subclasses are
# registered.
from ..git.gitlab.badges import BadgeManager

LOGGER = logging.getLogger(__name__)


def _format_docstring_for_cell(docstring):
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


def document_badges():
    """
    Document all recognized badges in a table using their corresponding manager
    class docstrings.
    """
    badges = dict(BadgeManager.list_registered_with_classes())
    print("|Name|Description|Condition|")
    print("|:- |:- |:- |")
    for name, cls in sorted(badges.items()):
        desc = _format_docstring_for_cell(cls.__doc__).replace("NAME", name)
        cond = _format_docstring_for_cell(cls.enabled.__doc__).replace("NAME", name)
        print(f"|{name}|{desc}|{cond}|")
