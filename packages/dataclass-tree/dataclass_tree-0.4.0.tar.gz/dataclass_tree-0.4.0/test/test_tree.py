from copy import deepcopy
from dataclasses import dataclass
import pytest
from dataclass_tree import Tree, Visitor, LabeledTree, Order, optional_treelist


class TestTree:
    def test_tree_creation(self):
        @dataclass
        class Binary(Tree):
            left: list[Tree] = optional_treelist()
            right: list[Tree] = optional_treelist()

        root = Binary()
        a = Binary()
        b = Binary()

        # appending will work as expected
        root.left.append(a)
        root.right.append(b)

        assert root.left == [a]
        assert root.right == [b]

        # passings child groups to the constructor will work too
        root2 = Binary(left=[a], right=[b])

        assert root2.left == [a]
        assert root2.right == [b]

    def test_tree_creation_without_options(self):
        @dataclass
        class Binary(Tree):
            left: list[Tree]
            right: list[Tree]

        # fields not marked as optional are mandatory in the constructor
        with pytest.raises(TypeError):
            Binary()  # type: ignore  (typecheckers will complain too, but we have an explicit check as well)

        # they may be empty lists though
        Binary(left=[], right=[])

    def test_tree_creation_with_union(self):
        @dataclass
        class Binary(Tree):
            left: list[Tree] | None = None
            right: list[Tree] = None  # type: ignore (typecheckers will complain too, but we have an explicit fix as well)
            middle: None | list[Tree] = (
                None  # order of types in the union is not important
            )
            extra: str | None = None

        # with None as an option it is ok to use a constructor without arguments
        root = Binary()
        # but list[Tree] fields should be  initialized to [] anyway
        assert root.left == []
        assert root.right == []
        assert root.middle == []
        # and other fields with None as an option should get None
        assert root.extra is None

    def test_tree_str(self):
        node1 = Tree()
        assert str(node1) == 'Tree()'
        @dataclass
        class Node(Tree):
            ...
        node2 = Node()
        assert str(node2) == 'Node()'
        
    def test_labeled_tree_str(self):
        node1 = LabeledTree("A")
        assert str(node1) == 'LabeledTree(label="A")'

@pytest.fixture
def simple_tree():
    @dataclass
    class Node(LabeledTree):
        left: list[Tree] = optional_treelist()
        right: list[Tree] = optional_treelist()

    A = Node("A")
    B = Node("B")
    C = Node("C")
    D = Node("D")
    E = Node("E")
    F = Node("F")
    G = Node("G")
    H = Node("H")
    I = Node("I")  # noqa: E741

    F.left.append(B)
    F.right.append(G)

    B.left.append(A)
    B.right.append(D)

    D.left.append(C)
    D.right.append(E)

    G.right.append(I)
    I.left.append(H)

    return F  # See: https://en.wikipedia.org/wiki/Tree_traversal#/media/File:Sorted_binary_tree_ALL_RGB.svg


@pytest.fixture
def context_tree():
    @dataclass
    class Node(LabeledTree):
        left: list[Tree] = optional_treelist()
        right: list[Tree] = optional_treelist()
        newcontext: bool = False

    A = Node("A")
    B = Node("B")
    C = Node("C")
    D = Node("D")
    E = Node("E")
    F = Node("F")
    G = Node("G")
    H = Node("H")
    I = Node("I")  # noqa: E741

    F.left.append(B)
    F.right.append(G)

    B.left.append(A)
    B.right.append(D)
    B.newcontext = True

    D.left.append(C)
    D.right.append(E)

    G.right.append(I)
    I.left.append(H)

    return F  # See: https://en.wikipedia.org/wiki/Tree_traversal#/media/File:Sorted_binary_tree_ALL_RGB.svg


@pytest.fixture
def mixed_tree():
    @dataclass
    class Node(LabeledTree):
        left: list[Tree] = optional_treelist()
        right: list[Tree] = optional_treelist()

    @dataclass
    class Node2(LabeledTree):
        aaa: list[Tree] = optional_treelist()
        bbb: list[Tree] = optional_treelist()

    @dataclass
    class LeafNode(LabeledTree): ...

    A = LeafNode("A")
    B = Node("B")
    C = LeafNode("C")
    D = Node2("D")
    E = LeafNode("E")
    F = Node("F")
    G = Node("G")
    H = LeafNode("H")
    I = Node("I")  # noqa: E741

    F.left.append(B)
    F.right.append(G)

    B.left.append(A)
    B.right.append(D)

    D.aaa.append(C)
    D.bbb.append(E)

    G.right.append(I)
    I.left.append(H)

    return F  # See: https://en.wikipedia.org/wiki/Tree_traversal#/media/File:Sorted_binary_tree_ALL_RGB.svg


class PrintVisitor(Visitor):
    def __init__(self, strict: bool = False) -> None:
        super().__init__(strict)
        self.traversal = []

    def _do_printvisitor(self, node: LabeledTree, level: int):
        self.traversal.append(node.label)


class TestVisitor:
    def test_preorder(self, simple_tree):
        print_visitor = (
            PrintVisitor()
        )  # need a fresh instance with an empty traversal list, so no fixture
        simple_tree.visit(print_visitor, Order.PREORDER)
        assert print_visitor.traversal == ["F", "B", "A", "D", "C", "E", "G", "I", "H"]

    def test_postorder(self, simple_tree):
        print_visitor = (
            PrintVisitor()
        )  # need a fresh instance with an empty traversal list, so no fixture
        simple_tree.visit(print_visitor, Order.POSTORDER)
        assert print_visitor.traversal == ["A", "C", "E", "D", "B", "H", "I", "G", "F"]

    def test_inorder(self, simple_tree):
        print_visitor = (
            PrintVisitor()
        )  # need a fresh instance with an empty traversal list, so no fixture
        simple_tree.visit(print_visitor, Order.INORDER)
        assert print_visitor.traversal == ["A", "B", "C", "D", "E", "F", "G", "H", "I"]

    def test_levelorder(self, simple_tree):
        print_visitor = (
            PrintVisitor()
        )  # need a fresh instance with an empty traversal list, so no fixture
        simple_tree.visit(print_visitor, Order.LEVELORDER)
        assert print_visitor.traversal == ["F", "B", "G", "A", "D", "I", "C", "E", "H"]

    def test_unknownorder(self, simple_tree):
        print_visitor = (
            PrintVisitor()
        )  # need a fresh instance with an empty traversal list, so no fixture
        with pytest.raises(ValueError):
            simple_tree.visit(print_visitor, None)

    def test_nontree_item(self, simple_tree):
        print_visitor = (
            PrintVisitor()
        )  # need a fresh instance with an empty traversal list, so no fixture
        simple_tree.left.append("string")
        with pytest.warns(Warning):
            simple_tree.visit(print_visitor, Order.PREORDER)
        assert print_visitor.traversal == ["F", "B", "A", "D", "C", "E", "G", "I", "H"]

    def test_mixed(
        self, mixed_tree
    ):  # names of child groups should make no difference nor the subclass
        print_visitor = (
            PrintVisitor()
        )  # need a fresh instance with an empty traversal list, so no fixture
        mixed_tree.visit(print_visitor, Order.PREORDER)
        assert print_visitor.traversal == ["F", "B", "A", "D", "C", "E", "G", "I", "H"]

    def test_context(self, context_tree):
        class ContextTest(Visitor):
            def __init__(self, strict: bool = False) -> None:
                super().__init__(strict)
                self.context_at_node = {}

            def _do_contexttest(self, node, level):  # executed for every node
                self.context_at_node[node.label] = deepcopy(self._context)
                self.get_context()[node.label] = str(self)

        cv = ContextTest()
        context_tree.visit(cv, Order.PREORDER)
        # ["F", "B", "A", "D", "C", "E", "G", "I", "H"]
        #           F
        #       /      \
        #      B        G         *B has newcontext=True, so when G is visited, it will have the same toplevel context as B (but will not generate a new one itself)
        #    /  \        \
        #   A    D        I
        #       /  \     /
        #      C    E   H
        assert cv.context_at_node["F"] == [{}]
        assert cv.context_at_node["B"] == [{"F": "Node"}, {"F": "Node"}]
        assert cv.context_at_node["A"] == [
            {"F": "Node"},
            {"F": "Node", "B": "Node/Node"},
        ]
        assert cv.context_at_node["D"] == [
            {"F": "Node"},
            {"F": "Node", "B": "Node/Node", "A": "Node/Node/Node"},
        ]
        assert cv.context_at_node["C"] == [
            {"F": "Node"},
            {
                "F": "Node",
                "B": "Node/Node",
                "A": "Node/Node/Node",
                "D": "Node/Node/Node",
            },
        ]
        assert cv.context_at_node["E"] == [
            {"F": "Node"},
            {
                "F": "Node",
                "B": "Node/Node",
                "A": "Node/Node/Node",
                "D": "Node/Node/Node",
                "C": "Node/Node/Node/Node",
            },
        ]
        assert cv.context_at_node["G"] == [{"F": "Node"}]
        assert cv.context_at_node["I"] == [{"F": "Node", "G": "Node/Node"}]
        assert cv.context_at_node["H"] == [
            {"F": "Node", "G": "Node/Node", "I": "Node/Node/Node"}
        ]

        assert str(cv) == ""  # when done, the current shortest path is empty

    def test_context_hook(self):
        @dataclass
        class Node(LabeledTree):
            left: list[Tree] = optional_treelist()
            right: list[Tree] = optional_treelist()
            newcontext: bool = False

            def push_context_hook(self, context: dict, level: int):
                for k, v in context.items():
                    context[k] = v * 2

        A = Node("A")
        B = Node("B")
        C = Node("C")
        D = Node("D")
        E = Node("E")
        F = Node("F")
        G = Node("G")
        H = Node("H")
        I = Node("I")  # noqa: E741

        F.left.append(B)
        F.right.append(G)

        B.left.append(A)
        B.right.append(D)
        B.newcontext = True

        D.left.append(C)
        D.right.append(E)

        G.right.append(I)
        I.left.append(H)

        class ContextTest(Visitor):
            def __init__(self, strict: bool = False) -> None:
                super().__init__(strict)
                self.context_at_node = {}

            def _do_contexttest(self, node, level):  # executed for every node
                self.context_at_node[node.label] = deepcopy(self._context)
                self.get_context()[node.label] = str(self)

        cv = ContextTest()
        F.visit(cv, Order.PREORDER)
        assert cv.context_at_node["B"] == [{"F": "Node"}, {"F": "NodeNode"}]

    def test_visitor_with_missing_methods(self, simple_tree):
        class BrokenVisitor(Visitor): ...

        class OnlyGeneric(Visitor):
            def _do_onlygeneric(self, node, level): ...

        with pytest.raises(NotImplementedError):
            simple_tree.visit(BrokenVisitor())

        simple_tree.visit(OnlyGeneric())

        with pytest.raises(NotImplementedError):
            simple_tree.visit(OnlyGeneric(strict=True))
