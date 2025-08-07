from copy import copy
from dataclasses import dataclass, field, fields
from types import GenericAlias, UnionType
from typing import Any, Tuple
from enum import StrEnum, auto
from warnings import warn


class Order(StrEnum):
    PREORDER = auto()
    INORDER = auto()
    POSTORDER = auto()
    LEVELORDER = auto()


class Visitor:
    """
    The Visitor class implements a `visit` method that acts on a `Tree` node.

    It is typically applied to each node in a tree by the `Tree.visit()` method.

    When visiting a node, the actual visitor method name is constructed from the class name
    and the lower case class name of the visitor class. For example, if the Visitor
    derived class is called Validator and the node is an instance of Person, the method
    searched for is `_do_validator_Person`.

    If that method cannot be found, a generic visitor `_do_validator()` is used,
    unless the visitor class was instantiated with `strict=True`.

    If no visitor method is found, the method resolution order is followed to search
    in superclasses.

    A visitor also manages context, which is a stack of dictionaries. When the visitor is created,
    the stack is initialized with an empty dictionary. Methods are provided to push a new context
    (a shallow copy of the top dictionary), pop the top context, and get the top context.
    The `Tree.visit()` method can use these methods manage the context.

    """
    def __init__(self, strict: bool = False) -> None:
        """
        Initialize the Visitor.

        Args:
            strict (bool): If True, require exact visitor method matches for each node type.
        """
        self.strict = strict
        self._visitor_queue: list[Tuple["Tree", int]] = []
        self._context = [{}]
        self.shortest_path = []

    def visit(self, node: "Tree", level: int = 0) -> Any:
        """
        Apply the appropriate visitor method to the given node.

        Args:
            node (Tree): The tree node to visit.
            level (int): The current depth in the tree.

        Returns:
            Any: The result of the visitor method.
        """
        return self._get_visitor(node)(node, level)

    def _get_visitor(self, tree: "Tree"):
        """
        Find the appropriate visitor method for the given tree node.

        When visiting a node, the visitor method name is constructed from the class name
        and the lower case class name of the visitor class. For example, if the Visitor
        derived class is called Validator and the node is an instance of Person, the method
        searched for is `_do_validator_Person`.

        If that method cannot be found, a generic visitor `_do_validator()` is used,
        unless the visitor class was instantiated with `strict=True`.

        If no visitor method is found, the method resolution order is followed to search
        in superclasses.

        Args:
            tree (Tree): The node to find a visitor for.

        Returns:
            Callable: The visitor method.

        Raises:
            NotImplementedError: If no suitable visitor method is found.
        """
        typename = tree.__class__.__name__
        for klass in self.__class__.__mro__:
            generic_visitor = f"_do_{klass.__name__.lower()}"
            visitor = f"{generic_visitor}_{typename}"
            if hasattr(self, visitor):
                return getattr(self, visitor)
            elif not self.strict and hasattr(self, generic_visitor):
                return getattr(self, generic_visitor)

        generic_visitor = f"_do_{self.__class__.__name__.lower()}"
        visitor = f"{generic_visitor}_{typename}"

        if self.strict:
            raise NotImplementedError(
                f"class {self.__class__.__name__} missing {visitor} method (or equivalent in super classes)."
            )
        else:
            raise NotImplementedError(
                f"class {self.__class__.__name__} missing {visitor} and {generic_visitor} methods (or equivalent in super classes)."
            )

    def push_context(self):
        """Push a shallow copy of the current context"""
        dup = {k: copy(v) for k, v in self._context[-1].items()}
        self._context.append(dup)

    def pop_context(self):
        if len(self._context) > 1:
            return self._context.pop()
        # if this happens we have a system error
        raise IndexError(  # pragma: no cover
            f"context unbalanced: more pops than pushes in {self.__class__.__name__}",
        )

    def get_context(self):
        return self._context[-1]

    def __str__(self) -> str:
        """
        Return a string representation of the path from the root to the current node.
        """
        return "/".join(node.__class__.__name__ for node in self.shortest_path)

@dataclass
class Tree:
    """
    A dataclass with zero or more fields of type list[Tree] plus any additional fields.

    Example:

        @dataclass   # don't forget this decorator!
        class MyTree(Tree):
            left: list[Tree] = optional_treelist()
            right: list[Tree] = optional_treelist()
            extra: str = "spam"

        root = MyTree()
        root.left.append(MyTree(extra="left spam"))
        root.right.append(MyTree(extra="right spam"))
    
    It has a `visit` method that takes an instance of a 'Visitor' that will be recursively applied to all children, regardless of their field names.
    """

    def __post_init__(self, *args, **kwargs):
        """
        Automatically initializes certain fields with an empty list after dataclass construction.

        For each field, if its type is either:
        - `list[Tree]`, or
        - `Optional[list[Tree]]` (i.e., `Union[list[Tree], NoneType]`),

        and if the field does not already have a suitable default or default_factory,
        then it will be set to an empty list.

        This ensures that fields representing child groups are always initialized to a list,
        avoiding mutable default argument issues and making it safe to append children immediately.

        Args:
            *args, **kwargs: Ignored, present for compatibility.
        """
        for f in fields(self):
            add_default = False
            if (
                type(f.type) is GenericAlias
                and f.type.__origin__ is list
                and [issubclass(a, Tree) for a in f.type.__args__] == [True]
            ):
                if (type(f.default_factory) is not type) or not issubclass(
                    f.default_factory, list
                ):
                    add_default = True
            elif type(f.type) is UnionType and len(f.type.__args__) == 2:
                treelist = False
                none = False
                for arg in f.type.__args__:
                    if arg is type(None):
                        none = True
                    elif (
                        type(arg) is GenericAlias
                        and arg.__origin__ is list
                        and [issubclass(a, Tree) for a in arg.__args__] == [True]
                    ):
                        treelist = True
                if treelist and none:
                    add_default = True
            if add_default:
                setattr(self, f.name, [])

    def __str__(self):
        """
        Return a string representation of the Tree node.

        Returns:
            str: The string representation.
        """
        return f"{self.__class__.__name__}()"

    def visit(self, visitor: Visitor, order: Order = Order.POSTORDER):
        """
        Traverse the tree and apply the given visitor to each node.

        The traversal order can be specified using the `order` argument:
        - POSTORDER: children first, then node
        - PREORDER: node first, then children
        - INORDER: left children, node, right children (for binary trees)
        - LEVELORDER: breadth-first traversal

        Args:
            visitor (Visitor): The visitor instance to apply to each node.
            order (Order): The traversal order (default is POSTORDER).
        """
        if order is Order.LEVELORDER:
            visitor._visitor_queue = [(self, 0)]
        self._visit(visitor, order)

    def push_context_hook(self, visitor:Visitor, level:int):
        """
        Stub. Override with your own implementation.

        Will be called by a visitor after a new context had been pushed (if any).
        """
        pass

    def pop_context_hook(self, visitor:Visitor, level:int):
        """
        Stub. Override with your own implementation.

        Will be called by a visitor before a new context will be popped (if any).
        """
        pass

    def _enqueue(self, visitor: Visitor, node: "Tree", level: int):
        """
        Enqueue all child nodes of the given node for visiting.

        Args:
            visitor (Visitor): The visitor instance that owns the queue.
            node (Tree): The node whose children to enqueue.
            level (int): The depth level for the children.

        Raises:
            Warning: If a field declared as a child group contains an item that is not an instance of Tree.
        """
        for f in fields(node):
            group = getattr(node, f.name)
            if isinstance(group, list):
                for item in group:
                    if isinstance(item, Tree):
                        visitor._visitor_queue.append((item, level))
                    else:
                        warn(
                            f"{f.name} field in {self.__class__.__name__} contains item that is not an instance of Tree"
                        )

    def _first(self):
        """
        Generator returning the children in the first child group.

        Raises: UserWarning if any child group item is not an instance of a Tree.
        """
        for f in fields(self):
            group = getattr(self, f.name)
            if isinstance(group, list):
                for item in group:
                    if isinstance(item, Tree):
                        yield item
                    else:
                        warn(
                            f"{f.name} field in {self.__class__.__name__} contains item that is not an instance of Tree"
                        )
                return  # stop after first group that is a list

    def _last(self):
        """
        Generator returning any children not in the first child group.

        Raises: UserWarning if any child group item is not an instance of a Tree.
        """

        first = True
        for f in fields(self):
            group = getattr(self, f.name)
            if isinstance(group, list):
                if first:  # skip the first group that is a list
                    first = False
                    continue
                for item in group:
                    if isinstance(item, Tree):
                        yield item
                    else:
                        warn(
                            f"{f.name} field in {self.__class__.__name__} contains item that is not an instance of Tree"
                        )

    def _visit(self, visitor: Visitor, order: Order, level: int = 0):
        """
        Internal recursive traversal method for visiting nodes in the specified order.

        Args:
            visitor (Visitor): The visitor instance.
            order (Order): The traversal order.
            level (int): the current recursion level.

        For every node visited:
        
        - a new context is pushed (if the node has an attribute newcontext == True)
        - the `visit` method of the visitor is called with the current node and level as arguments
        - the new context is popped(if the node has an attribute newcontext == True)

        When the `visit` method is called depends on the order:

        - PREORDER, called before any children are visited
        - POSTORDER, called after all children are visited
        - INORDER, called after all children in the first child group are visited
        - LEVELORDER, called for each child after all children at the same level are collected (but before any grandchildren, etc.) 
        """

        visitor.shortest_path.append(self)

        if getattr(self, "newcontext", False):
            visitor.push_context()
            if hasattr(self, "push_context_hook"):
                self.push_context_hook(visitor.get_context(), level)
                
        match order:
            case Order.POSTORDER:
                for item in self._first():
                    item._visit(visitor, order, level + 1)
                for item in self._last():
                    item._visit(visitor, order, level + 1)
                visitor.visit(self, level)
            case Order.PREORDER:
                visitor.visit(self, level)
                for item in self._first():
                    item._visit(visitor, order, level + 1)
                for item in self._last():
                    item._visit(visitor, order, level + 1)
            case Order.INORDER:
                for item in self._first():
                    item._visit(visitor, order, level + 1)
                visitor.visit(self, level)
                for item in self._last():
                    item._visit(visitor, order, level + 1)
            case Order.LEVELORDER:
                for _ in range(len(visitor._visitor_queue)):
                    node, level = visitor._visitor_queue.pop(0)
                    visitor.visit(node, level)
                    self._enqueue(visitor, node, level + 1)
                if visitor._visitor_queue:
                    self._visit(visitor, order, level + 1)
            case _:
                raise ValueError(f"{order} not in set {{POSTORDER, PREORDER, INORDER}}")

        if getattr(self, "newcontext", False):
            if hasattr(self, "pop_context_hook"):
                self.pop_context_hook(visitor.get_context(), level)
            visitor.pop_context()

        visitor.shortest_path.pop()

@dataclass
class LabeledTree(Tree):
    """
    Convenience class for a `Tree` with a label field.
    """
    label: str

    def __str__(self):
        return f'{self.__class__.__name__}(label="{self.label}")'


def optional_treelist():
    """
    Syntactic sugar to make type hints more readable.
    """
    return field(default_factory=list)


if __name__ == "__main__":  # pragma: no cover

    @dataclass
    class Binop(LabeledTree):
        left: list[Tree] = optional_treelist()
        right: list[Tree] = optional_treelist()

    @dataclass
    class Unop(LabeledTree):
        expr: list[Tree] = optional_treelist()

    @dataclass
    class Literal(Tree):
        value: str

        def __str__(self):
            return f'{self.__class__.__name__}(value="{self.value}")'

    b = Binop(label="+")

    a = Unop(label="-")

    v = Literal("42")
    v2 = Literal("2")
    v3 = Literal("10")

    b2 = Binop(label="*", left=[v2], right=[v3])

    a.expr.append(v)

    b.left.append(a)
    b.right.append(b2)

    class Counter(Visitor):
        def __init__(self, strict: bool = False) -> None:
            super().__init__(strict)
            self.count = 0

        def _do_counter(self, node: Tree, level: int):
            self.count += 1

    counter = Counter()
    b.visit(counter)
    print(counter.count)

    class NestedPrinter(Visitor):
        def _do_nestedprinter(self, node: Tree, level: int):
            indent = "    " * level
            print(f"{indent} {node}")

    print(">>>> PREORDER")
    b.visit(NestedPrinter(), order=Order.PREORDER)
    print(">>>> POSTORDER")
    b.visit(NestedPrinter(), order=Order.POSTORDER)
    print(">>>> INORDER")
    b.visit(NestedPrinter(), order=Order.INORDER)
    print(">>>> LEVELORDER")
    b.visit(NestedPrinter(), order=Order.LEVELORDER)
