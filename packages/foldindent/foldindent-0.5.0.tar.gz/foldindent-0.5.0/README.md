# foldindent - indented text viewer with folding

`foldindent` is a terminal user interface (TUI) for viewing indented text files with the possibility to fold parts based on indentation.
`foldindent` can view arbitrary text files.

`foldindent` can be seen as pager dedicated to indented text data.

Each time lines are more indented than previous lines, a foldable point is added in the UI.

## Samples

### Sample: indented JSON data

![foldindent screenshot of indented JSON](https://github.com/hydrargyrum/foldindent/blob/main/samples/sample-json.png?raw=true)

### Sample: indented python AST dump

(Source sample text generated with `python3 -m ast samples/example.py`)

![foldindent screenshot of indented AST](https://github.com/hydrargyrum/foldindent/blob/main/samples/sample-ast.png?raw=true)

## Keyboard usage

- `Enter`: fold/expand a node
- `Up/Down`: navigate cursor one node above/below
- `^`: jump to parent node

## Install

[`pipx install foldindent`](https://pypi.org/project/foldindent/)

## Keybindings

- `left`: collapse/go to parent
- `right` : expand/go to first child
- `up`: go up
- `down`: go down
- `enter`: toggle expand/collapse
- `^`: go to parent
- `shift-left`: collapse all children
- `shift-right`: expand all children
- `shift-up`: go to previous sibling
- `shift-down`: go to next sibling
- `/`: search
- `n`: previous search result
- `N`: next search result
- `q`: quit
