from dataclasses import dataclass
import pytest
from dataclass_tree.tree import Tree, Visitor, LabeledTree, Order, optional_treelist


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
            root = Binary()

        # they may be empty lists though
        root = Binary(left=[], right=[])

    def test_tree_creation_with_union(self):
        @dataclass
        class Binary(Tree):
            left: list[Tree] | None = None
            right: list[Tree] = None          # typecheckers will complain 
            middle: None | list[Tree] = None  # order of types in the union is not important
            extra: str | None = None

        # with None as an option it is ok to use a constructor without arguments
        root = Binary()
        # but list[Tree] fields should be  initialized to [] anyway
        assert root.left == []
        assert root.right == []
        assert root.middle == []
        # and other fields with None as an option should get None
        assert root.extra is None
        
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
    I = Node("I")

    F.left.append(B)
    F.right.append(G)

    B.left.append(A)
    B.right.append(D)

    D.left.append(C)
    D.right.append(E)

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
        print_visitor = PrintVisitor()  # need a fresh instance with an empty traversal list, so no fixture
        simple_tree.visit(print_visitor, Order.PREORDER)
        assert print_visitor.traversal == ["F", "B", "A", "D", "C", "E", "G", "I", "H"]

    def test_postorder(self, simple_tree):
        print_visitor = PrintVisitor()  # need a fresh instance with an empty traversal list, so no fixture
        simple_tree.visit(print_visitor, Order.POSTORDER)
        assert print_visitor.traversal == ["A", "C", "E", "D", "B", "H", "I", "G", "F"]

    def test_inorder(self, simple_tree):
        print_visitor = PrintVisitor()  # need a fresh instance with an empty traversal list, so no fixture
        simple_tree.visit(print_visitor, Order.INORDER)
        assert print_visitor.traversal == ["A", "B", "C", "D", "E", "F", "G", "H", "I"]

    def test_levelorder(self, simple_tree):
        print_visitor = PrintVisitor()  # need a fresh instance with an empty traversal list, so no fixture
        simple_tree.visit(print_visitor, Order.LEVELORDER)
        assert print_visitor.traversal == ["F", "B", "G", "A", "D", "I", "C", "E", "H"]

    def test_unknownorder(self, simple_tree):
        print_visitor = PrintVisitor()  # need a fresh instance with an empty traversal list, so no fixture
        with pytest.raises(ValueError):
            simple_tree.visit(print_visitor, None)

    def test_nontree_item(self, simple_tree):
        print_visitor = PrintVisitor()  # need a fresh instance with an empty traversal list, so no fixture
        simple_tree.left.append("string")
        with pytest.warns(Warning):
            simple_tree.visit(print_visitor, Order.PREORDER)
        assert print_visitor.traversal == ["F", "B", "A", "D", "C", "E", "G", "I", "H"]
