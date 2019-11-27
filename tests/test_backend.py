from backend.backend import Node, Tree, LoadBalancerConfig
import json

def test_nodes():
    tree = Tree()
    parent = Node('parent')
    child_1 = Node('child1', parent=parent)
    child_2 = Node('child2', parent=parent)
    tree.append(parent)
    tree.append(child_1)
    tree.append(child_2)

    assert tree.d3_nodes() == [
        {'name': 'parent'},
        {'name': 'child1'},
        {'name': 'child2'},
    ]

    tree.append(Node('grandchild1', parent=child_1))
    tree.append(Node('grandchild2', parent=child_1))
    tree.append(Node('grandchild3', parent=child_2))
    tree.append(Node('grandchild4', parent=child_2))

    assert tree.d3_nodes() == [
        {'name': 'parent'},
        {'name': 'child1'},
        {'name': 'child2'},
        {'name': 'grandchild1'},
        {'name': 'grandchild2'},
        {'name': 'grandchild3'},
        {'name': 'grandchild4'},
    ]