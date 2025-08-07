
from __future__ import annotations

from typing import Dict, List, Optional

from concurrent.futures import ThreadPoolExecutor
from term.rule import Rule


class Node:
    """
    Base class of nodes in decision trees.
    These nodes may or may not be leaf nodes.
    """

    def __init__(self, is_leaf: bool):
        self.is_leaf = is_leaf


class TreeNode(Node):
    def __init__(self, node_name: str, threshold: float):
        super().__init__(is_leaf=False)
        self.node_name = node_name
        self.threshold = threshold

    def __str__(self) -> str:
        return self.node_name

    def get_left_clause(self) -> str:
        return self.node_name + " <= " + str(self.threshold)

    def get_right_clause(self) -> str:
        return self.node_name + " > " + str(self.threshold)


class LeafNode(Node):
    """
    Class of terminal (leaf) nodes in decision trees.
    Each leaf node has a value assigned to data reaching the leaf.
    """

    def __init__(self, value: float):
        super().__init__(is_leaf=True)
        self.value = value

    def __str__(self) -> str:
        return str(self.value)

    def get_leaf_clause(self) -> str:
        return "value: " + str(self.value)


class DecisionTree:

    def __init__(
        self,
        node: Node,
        left: Optional[DecisionTree] = None,
        right: Optional[DecisionTree] = None,
        feature_index: Optional[int] = None,
        threshold: Optional[float] = None,
        left_value: Optional[float] = None,
        right_value: Optional[float] = None,
    ):
        self.node = node
        self.left = left
        self.right = right
        self.feature_index = feature_index
        self.threshold = threshold
        self.left_value = left_value
        self.right_value = right_value

    def __str__(self) -> str:
        return self._str_recursive(num_indent=0)

    def _str_recursive(self, num_indent: int) -> str:
        indentation = "|   " * num_indent + "|---"
        if isinstance(self.node, LeafNode):
            string_rep = indentation + self.node.get_leaf_clause()
        elif isinstance(self.node, TreeNode):
            if (self.left is None) or (self.right is None):
                raise ValueError("TreeNode cannot have None as children")
            else:
                string_rep = indentation + self.node.get_left_clause() + "\n"
                string_rep += self.left._str_recursive(num_indent=num_indent + 1) + "\n"
                string_rep += indentation + self.node.get_right_clause() + "\n"
                string_rep += self.right._str_recursive(num_indent=num_indent + 1)
        else:
            raise ValueError("Node has to be LeafNode or TreeNode")
        return string_rep

    def _propagate_decision_rule(self, decision_rule: List[str]) -> None:
        self.decision_rule = decision_rule
        if isinstance(self.node, LeafNode):
            pass
        elif isinstance(self.node, TreeNode):
            if (self.left is None) or (self.right is None):
                raise ValueError("TreeNode cannot have None as children")
            else:
                left_decision_rule = decision_rule + [self.node.get_left_clause()]
                self.left._propagate_decision_rule(left_decision_rule)
                right_decision_rule = decision_rule + [self.node.get_right_clause()]
                self.right._propagate_decision_rule(right_decision_rule)
        else:
            raise ValueError("Node has to be LeafNode or TreeNode")

    def _propagate_decision_support(
        self,
        data: List[List[float]],
        feature_names: List[str],
        decision_support: List[int],
    ) -> None:
        self.decision_support = decision_support
        if isinstance(self.node, LeafNode):
            pass
        elif isinstance(self.node, TreeNode):
            if (self.left is None) or (self.right is None):
                raise ValueError("TreeNode cannot have None as children")
            else:
                feature_index = feature_names.index(self.node.node_name)
                left_decision_support = []
                right_decision_support = []
                for index in self.decision_support:
                    if data[index][feature_index] <= self.node.threshold:
                        left_decision_support.append(index)
                    else:
                        right_decision_support.append(index)
                self.left._propagate_decision_support(
                    data, feature_names, left_decision_support
                )
                self.right._propagate_decision_support(
                    data, feature_names, right_decision_support
                )
        else:
            raise ValueError("Node has to be LeafNode or TreeNode")

    def get_rules(
        self, data: List[List[float]], feature_names: List[str], tree_id: int
    ) -> List[Rule]:
        support = [i for i in range(len(data))]
        # self.aggregate_min_decision_value()
        # self.aggregate_max_decision_value()
        self._propagate_decision_rule(decision_rule=[])
        self._propagate_decision_support(data, feature_names, support)
        rules = self._collect_rules(tree_id=tree_id, node_id=0, rules=[])
        return rules

    def _collect_rules(self, tree_id: int, node_id: int, rules: List[Rule]) -> List[Rule]:
        collected_rules = []

        def traverse_tree(node, current_tree_id, current_node_id):
            if node is None:
                return

            # 收集规则
            collected_rules.append(
                Rule(
                    decision_rule=sorted(node.decision_rule),
                    decision_support=node.decision_support,
                    identity=[str(current_tree_id) + "_" + str(current_node_id)],
                )
            )

            # 递归遍历左右子树
            traverse_tree(node.left, current_tree_id, 2 * current_node_id + 1)
            traverse_tree(node.right, current_tree_id, 2 * current_node_id + 2)

        # 调用递归遍历函数
        traverse_tree(self, tree_id, node_id)

        return collected_rules

    def get_scores(self, scores: Dict[int, float]) -> Dict[int, float]:
        if isinstance(self.node, LeafNode):
            if not hasattr(self, "decision_support"):
                raise AttributeError(
                    "Support of nodes in the decision trees not found, "
                    + "since no data has been supplied to the model. "
                    + "Call get_rules() with data, before calling get_scores()."
                )
            for i in self.decision_support:
                if i not in scores:
                    scores[i] = self.node.value
                else:
                    scores[i] = scores[i] + self.node.value
        elif isinstance(self.node, TreeNode):
            if (self.left is None) or (self.right is None):
                raise ValueError("TreeNode cannot have None as children")
            else:
                scores = self.left.get_scores(scores)
                scores = self.right.get_scores(scores)
        else:
            raise ValueError("Node has to be LeafNode or TreeNode")
        return scores


from typing import List, Dict

class RandomForest:
    def __init__(
        self,
        decision_tree_ensemble: List[DecisionTree],
        weight: float,
        bias: float,
        feature_names: List[str],
        activation: str,
    ):
        self.decision_tree_ensemble = decision_tree_ensemble
        self.weight = weight
        self.bias = bias
        self.feature_names = feature_names
        if activation not in ["sigmoid", "linear"]:
            raise ValueError("Activation of forest can only be sigmoid or linear")
        self.activation = activation

    def get_num_trees(self) -> int:
        return len(self.decision_tree_ensemble)

    def get_rules(self, data: List[List[float]]) -> List[Rule]:
        feature_names = self.feature_names

        # 可能的批处理
        # batch_size = 适当的批次大小

        rules_from_tree = []
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(
                    tree.get_rules,
                    data,
                    feature_names,
                    tree_id
                )
                for tree_id, tree in enumerate(self.decision_tree_ensemble)
            ]

            # 收集结果
            for future in futures:
                rules_from_tree.extend(future.result())

        return rules_from_tree

    def get_scores(self) -> List[float]:
        scores: Dict[int, float] = {}
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(tree.get_scores, scores) for tree in self.decision_tree_ensemble]
            for future in futures:
                try:
                    scores = future.result()
                except AttributeError:
                    raise AttributeError("Support of nodes in the decision trees not found. "
                                         "Call get_rules() with data before calling get_scores().")
        scores = {i: self._activation_function(scores[i] * self.weight + self.bias)
                  for i in range(max(scores.keys()) + 1)}
        return [scores[i] for i in range(max(scores.keys()) + 1)]

    def _activation_function(self, value: float) -> float:
        if self.activation == "linear":
            return value
        elif self.activation == "sigmoid":
            return 1 / (1 + 2.71828 ** (-value))
        raise ValueError("Activation of forest can only be sigmoid or linear")

    def __str__(self) -> str:
        string_rep = ""
        for i, decision_tree in enumerate(self.decision_tree_ensemble):
            string_rep += f"Tree {i}\n{decision_tree.__str__()}\n\n"
        return string_rep
