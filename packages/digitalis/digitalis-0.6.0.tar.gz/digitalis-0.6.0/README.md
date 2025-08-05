# Digitalis 🪻

## Debug

```sh
uv run textual run --dev digitalis.app:main
```
Improve raw.py
- Remove unnecessary redraws / remove / add of children
- Keep track of the open nodes, so if new data comes it they are still open / closed (what ever the user did)
- Lazy loading of nodes, some messages can be very large (>1000 list items), adding them all to the tree view is slow
https://github.com/agmmnn/textual-filedrop
