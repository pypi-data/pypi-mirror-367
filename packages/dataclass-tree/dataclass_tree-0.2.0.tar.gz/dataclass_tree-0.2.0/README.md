![Python](/python.svg)[![Test](https://github.com/varkenvarken/dataclass-tree/actions/workflows/test_all.yml/badge.svg)](https://github.com/varkenvarken/dataclass-tree/actions/workflows/test_all.yml)![Coverage](/coverage.svg)![Pypi](/pypi.svg)
# dataclass-tree

## Overview

`dataclass-tree` provides a set of base classes and utilities for building and traversing tree-like data structures using Python's `dataclass` feature. It is designed to make tree construction, traversal, and manipulation both intuitive and type-safe, with a particular emphasis on **consistent type hinting** for maximum IDE support.

## Main Classes

### `Tree`

The `Tree` class serves as the abstract base for all tree nodes. It is designed around the concept of *child groups* that can have arbitrary names and may contain any number of `Tree` items (or subclasses thereof).

It is a dataclass, so any field annotated with `list[Tree]` will treated as child groups, while other fields function like normal. Child groups are treated special in the following way:

- They are automatically initialized to empty lists, even if no default factory is specified, and even if the field is annotated as optional with `list[Tree]|None`.
- They can be initialized with the `optional_treelist()` function to clearly mark them as such when hovering over them in an IDE.
- Child groups can be traversed with the `visit()` method, with support with different orders: `PREORDER`, `POSTORDER`, `INORDER`, and `LEVELORDER`.

The `Tree` base class has no child groups defined, so you will need to subclass it (or `LabeledTree`) to use it. (See examples below). Subclasses must use the `@dataclass` [decorator](https://docs.python.org/3/library/dataclasses.html#dataclasses.dataclass),
and any fields defined in the subclass are added to those defined in the superclass. Fields with the same name will replace those in the superclass, and order is significant. (This is standard [dataclass](https://docs.python.org/3/library/dataclasses.html#) behavior).

You can create trees containing a mix of Tree subclasses, each with their own uniquely nae child groups. For example, you could have a tree representing an expression in a programming language, with a Binop class with left and right child groups, and a Unop class having just an expression child group. Even though they have different names, they would be visited in a consistent way by a visitor, regardless their names.

### `LabeledTree`

A subclass of `Tree` with an additional `label` field. This is a very common usecase, so this class is provided as a convenience to save you some typing.

### `Visitor`

The `Visitor` class is designed to process `Tree` nodes while traversing a tree. It uses a flexible dispatch mechanism that locates the appropriate visitor method for each node type and is typically used as an argument for the `Tree.visit` method. The `Visitor` class does not traverse a tree on its own, but will be called to process a node by the `Tree.visit` method.

A `Visitor` has the following features:

- Dynamically dispatches to visitor methods based on the node's class name and the visitor's class name.
- Supports strict enforcement of visitor methods, i.e. raising a `NotImplemented` exception if no suitable method is found, or it can be configured to allow a generic fallback.
- Traversal logic is separated from the operation performed on each node, making it easy to implement new behaviors with minimal boilerplate. 

## Type Hinting for IDE Support

All core classes and their fields use type annotations. For example, child groups are always annotated as `list[Tree]` or `Optional[list[Tree]]`. This clarity enables IDEs to:
- Offer autocompletion for node attributes and methods.
- Provide real-time type checking to catch mistakes early.
- Generate informative tooltips and documentation as you code.

## Example Usage

A simple example showing class with different child groups.

```python
from dataclasses import dataclass
from dataclass_tree.tree import Tree, LabeledTree, Visitor, Order, optional_treelist

@dataclass
class Unop(LabeledTree):
    expression: : list[Tree] = optional_treelist()

@dataclass
class Binop(LabeledTree):
    left: list[Tree] = optional_treelist()
    right: list[Tree] = optional_treelist()

@dataclass
class Literal(Tree):
    value: str

# Build a simple tree
root = Unop("-")
root.expression = Binop(label="+")
root.left.append(Literal("42"))
root.right.append(Literal("7"))

# Define a visitor with a single, generic method that will apply to any node
class Printer(Visitor):
    def _do_printer(self, node: Tree, level: int):
        print(" " * (2 * level) + str(node))

# Traverse the tree
root.visit(Printer(), order=Order.PREORDER)
```

## License

GPL V3

## Supported traversal methods

Preorder, postorder, inorder, and levelorder.

See https://en.wikipedia.org/wiki/Tree_traversal

