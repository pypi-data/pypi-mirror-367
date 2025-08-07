#!/usr/bin/env python3
# SPDX-License-Identifier: WTFPL

import argparse
import bisect
import sys
from dataclasses import dataclass, field
from functools import partialmethod

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.keys import Keys
from textual.screen import ModalScreen
from textual.widgets import Footer, Tree as _Tree, Input
from textual.widgets.tree import TreeNode

__version__ = "0.5.0"


@dataclass
class Node:
    value: str
    children: list["Node"] = field(default_factory=list)


def _print_nodes(node, indent=0):
    print(indent * "  ", node.value)
    for c in node.children:
        _print_nodes(c, indent + 1)


def parse_indented(text):
    ret = Node(value="")
    objs = [ret]
    levels = [-1]

    lines = text.split("\n")
    for line in lines:
        if not line.strip():
            continue

        indent = len(line) - len(line.lstrip())
        line = line.strip()

        new = Node(value=line)

        pos = bisect.bisect_left(levels, indent)
        del objs[pos:]
        del levels[pos:]

        objs[-1].children.append(new)
        objs.append(new)
        levels.append(indent)

    return ret


class Tree(_Tree):
    BINDINGS = [
        Binding(Keys.Left, "fold_current", "Collapse"),
        Binding(Keys.Right, "expand_current", "Expand"),
        Binding("shift+left", "recurse_collapse", "Collapse tree"),
        Binding("shift+right", "recurse_expand", "Expand tree"),
        Binding("shift+up", "prev_sibling", "Previous sibling"),
        Binding("shift+down", "next_sibling", "Next sibling"),
        Binding("^", "go_to_parent", "Parent"),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.nodelist = {}

    def action_go_to_parent(self):
        self.select_node(self.cursor_node.parent)
        self.scroll_to_node(self.cursor_node)

    def action_fold_current(self):
        # q(self.cursor_node.id)
        if self.cursor_node.children and self.cursor_node.is_expanded:
            self.cursor_node.collapse()
        else:
            self.select_node(self.cursor_node.parent)
            self.scroll_to_node(self.cursor_node)

    def action_expand_current(self):
        if not self.cursor_node.children:
            return

        if self.cursor_node.is_expanded:
            self.select_node(self.cursor_node.children[0])
            self.scroll_to_node(self.cursor_node)
        else:
            self.cursor_node.expand()

    def action_recurse_expand(self):
        if not self.cursor_node.children:
            return
        self.cursor_node.expand_all()

    def action_recurse_collapse(self):
        if not self.cursor_node.children:
            return
        self.cursor_node.collapse_all()

    def _action_sibling(self, direction):
        if self.cursor_node.is_root:
            return
        siblings = list(self.cursor_node.parent.children)
        pos = siblings.index(self.cursor_node)
        child = siblings[max(0, min(pos + direction, len(siblings) - 1))]
        self.select_node(child)
        self.scroll_to_node(child)

    action_prev_sibling = partialmethod(_action_sibling, direction=-1)
    action_next_sibling = partialmethod(_action_sibling, direction=+1)


class InputScreen(ModalScreen):
    BINDINGS = [
        Binding("escape", "cancel"),
    ]

    def __init__(self, value):
        super().__init__()
        self.init_value = value

    def compose(self):
        yield Input(value=self.init_value)

    def on_input_submitted(self, message):
        self.dismiss(message.value)

    def action_cancel(self):
        self.dismiss(None)


class Searcher:
    def __init__(self, app):
        self.app = app
        self.pattern = ""

    def _new_coordinates_down(self, idx):
        return (idx + 1) % len(self.app.tree.nodelist)

    def _new_coordinates_up(self, idx):
        return (idx - 1) % len(self.app.tree.nodelist)

    def _do_search(self, increment):
        if not self.pattern:
            return

        tree = self.app.tree
        idx = max(0, tree.cursor_line)
        start = idx
        while True:
            idx = (idx + increment) % (tree.last_line + 1)
            if start == idx:
                break

            node = tree.get_node_at_line(idx)
            if node is tree.root:
                continue

            _, text = tree.nodelist[node.id]
            if self.pattern in text.lower():
                tree.select_node(node)
                tree.scroll_to_node(node)
                break

    def next(self):
        self._do_search(1)

    def previous(self):
        self._do_search(-1)


class FoldApp(App):
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("q", "quit", "Quit"),
        ("/", "search", "Search"),
        ("n", "search_next", "Next"),
        ("N", "search_prev", "Previous"),
    ]

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.searcher = Searcher(self)

    @property
    def tree(self):
        return self.query_one(Tree)

    def compose(self) -> ComposeResult:
        yield Footer()
        yield Tree("root", id="tree")

    def action_quit(self):
        self.exit()

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark

    def on_mount(self):
        self.feed(self.data)

    def feed(self, data: Node):
        tree = self.tree

        def recurse(tnode: TreeNode, dnode: Node):
            for sdnode in dnode.children:
                if sdnode.children:
                    stnode = tnode.add(sdnode.value)
                    recurse(stnode, sdnode)
                else:
                    stnode = tnode.add_leaf(sdnode.value)

                tree.nodelist[stnode.id] = (stnode, sdnode.value)

        recurse(tree.root, data)
        tree.root.expand_all()

    def action_search(self):
        def on_dismiss(value):
            if not value:
                return

            self.searcher.pattern = value.lower()
            self.action_search_next()

        self.app.push_screen(InputScreen(self.searcher.pattern), on_dismiss)

    def action_search_next(self):
        self.searcher.next()

    def action_search_previous(self):
        self.searcher.previous()


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("file", type=argparse.FileType('r'), nargs="?", default=sys.stdin)
    argparser.add_argument("--version", action="version", version=__version__)
    args = argparser.parse_args()

    with args.file:
        text = args.file.read()

    if args.file is sys.__stdin__:
        # textual accesses sys.__stdin__
        # it's used for reading data input and user input
        # force textual to read user input from terminal
        sys.__stdin__ = open("/dev/tty")

    DATA = parse_indented(text)

    app = FoldApp(DATA)
    app.run()


if __name__ == "__main__":
    main()
