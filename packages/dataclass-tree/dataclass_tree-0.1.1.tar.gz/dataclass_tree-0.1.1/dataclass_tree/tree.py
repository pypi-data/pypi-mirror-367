from dataclasses import dataclass, field, fields
from types import GenericAlias, UnionType
from typing import Any, Tuple
from enum import StrEnum, auto


class Order(StrEnum):
    PREORDER = auto()
    INORDER = auto()
    POSTORDER = auto()
    LEVELORDER = auto()


class Visitor:
    def __init__(self, strict: bool = False) -> None:
        """
        Initialize the Visitor.

        Args:
            strict (bool): If True, require exact visitor method matches for each node type.
        """
        self.strict = strict
        self.visitor_queue: list[Tuple["Tree", int]] = []

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


@dataclass
class Tree:
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
        visitor.visitor_queue = [(self, 0)]
        self._visit(visitor, order)

    def _enqueue(self, visitor: Visitor, node: "Tree", level: int):
        """
        Enqueue all child nodes of the given node for visiting.

        Args:
            visitor (Visitor): The visitor instance.
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
                        visitor.visitor_queue.append((item, level + 1))
                    else:
                        raise Warning(
                            f"{f.name} field in {self.__class__.__name__} contains item that is not an instance of Tree"
                        )

    def _enqueue_one_by_one(self, visitor: Visitor, node: "Tree", level: int):
        """
        Enqueue child nodes one by one and yield each child.

        Args:
            visitor (Visitor): The visitor instance.
            node (Tree): The node whose children to enqueue.
            level (int): The depth level for the children.

        Yields:
            Tree: Each child node.
        """
        for f in fields(node):
            group = getattr(node, f.name)
            if isinstance(group, list):
                for item in group:
                    if isinstance(item, Tree):
                        visitor.visitor_queue.append((item, level + 1))
                        yield item
                    else:
                        raise Warning(
                            f"{f.name} field in {self.__class__.__name__} contains item that is not an instance of Tree"
                        )

    def _enqueue_first(self, visitor: Visitor, node: "Tree", level: int):
        """
        Enqueue only the first child group of the node.

        Args:
            visitor (Visitor): The visitor instance.
            node (Tree): The node whose first child group to enqueue.
            level (int): The depth level for the children.
        """
        for f in fields(node):
            group = getattr(node, f.name)
            if isinstance(group, list):
                for item in group:
                    if isinstance(item, Tree):
                        visitor.visitor_queue.append((item, level + 1))
                    else:
                        raise Warning(
                            f"{f.name} field in {self.__class__.__name__} contains item that is not an instance of Tree"
                        )
                return

    def _enqueue_last(self, visitor: Visitor, node: "Tree", level: int):
        """
        Enqueue all child groups except the first one.

        Args:
            visitor (Visitor): The visitor instance.
            node (Tree): The node whose child groups to enqueue.
            level (int): The depth level for the children.
        """
        first = True
        for f in fields(node):
            group = getattr(node, f.name)
            if isinstance(group, list):
                if first:
                    first = False
                    continue
                for item in group:
                    if isinstance(item, Tree):
                        visitor.visitor_queue.append((item, level + 1))
                    else:
                        raise Warning(
                            f"{f.name} field in {self.__class__.__name__} contains item that is not an instance of Tree"
                        )
                return

    def _visit(self, visitor: Visitor, order: Order):
        """
        Internal recursive traversal method for visiting nodes in the specified order.

        Args:
            visitor (Visitor): The visitor instance.
            order (Order): The traversal order.
        """
        if order is Order.LEVELORDER:
            for _ in range(len(visitor.visitor_queue)):
                node, level = visitor.visitor_queue.pop(0)
                visitor.visit(node, level)
                self._enqueue(visitor, node, level + 1)
            if visitor.visitor_queue:
                self._visit(visitor, order)
        elif visitor.visitor_queue:
            node, level = visitor.visitor_queue.pop(0)
            match order:
                case Order.POSTORDER:
                    self._enqueue(visitor, node, level + 1)
                    node._visit(visitor, order)
                    visitor.visit(node, level)
                case Order.PREORDER:
                    visitor.visit(node, level)
                    for child in self._enqueue_one_by_one(visitor, node, level + 1):
                        node._visit(visitor, order)
                case Order.INORDER:
                    self._enqueue_first(visitor, node, level + 1)
                    node._visit(visitor, order)
                    visitor.visit(node, level)
                    self._enqueue_last(visitor, node, level + 1)
                    node._visit(visitor, order)
                case _:
                    raise ValueError(
                        f"{order} not in set {{POSTORDER, PREORDER, INORDER}}"
                    )


@dataclass
class LabeledTree(Tree):
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
