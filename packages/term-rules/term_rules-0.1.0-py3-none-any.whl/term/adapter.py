from __future__ import annotations

from typing import List, Optional

import numpy as np
from plotly.io import json
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier, AdaBoostClassifier ,ExtraTreesClassifier
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor, _tree
from catboost import CatBoostClassifier
import catboost as cb
from catboost import Pool
from lightgbm import LGBMClassifier
import lightgbm as lgb
import xgboost as xgb
from term.rule import Rule
from term.tree import DecisionTree, LeafNode, RandomForest, TreeNode
import json
class XGBoostClassifierAdapter:
    """
    将 xgboost.XGBClassifier 转换为 TERM.tree.RandomForest 对象的类。

    用法：
    adapter = XGBoostClassifierAdapter(model, feature_names)
    adapted_model = adapter.random_forest
    """

    def __init__(self, xgboost_forest: xgb.XGBClassifier, feature_names: List[str]):
        self.feature_names = feature_names

        # 从 XGBoost 分类器中提取必要的参数
        # 根据 XGBoost 模型的属性进行必要的调整
        self.bias = 0  # 分配偏置值
        self.weight = 1.0  # 分配权重值
        self.activation = "sigmoid"  # 分配激活函数

        # 从 XGBoost 模型中提取树
        xgboost_trees = xgboost_forest.get_booster().get_dump()
        self.xgboost_trees = xgboost_trees

        self.random_forest = self._convert()

    def parse_tree(self, tree_str):
        decision_rule = []  # 存储决策规则
        decision_support = []  # 存储决策支持
        identity = []  # 存储身份信息

        lines = tree_str.split('\n')  # 按行拆分树字符串
        node_index = 0  # 节点索引，用于生成节点身份信息

        for line in lines:
            if line.startswith('['):
                components = line.split('[')
                node_info = components[1].split(']')[0]  # 提取节点信息部分

                # 假设节点信息格式为：node_index:feature<threshold, yes=left_node, no=right_node
                node_details = node_info.split(':')
                feature_threshold = node_details[1].split('<')  # 特征和阈值信息

                # 填充规则信息到对应列表中
                decision_rule.append(f"{feature_threshold[0]} < {feature_threshold[1]}")
                decision_support.append(node_index)  # 使用节点索引作为支持信息
                identity.append(f"node_{node_index}")  # 使用节点索引作为身份信息
                node_index += 1  # 更新节点索引

        # 确保identity列表不为空
        if not identity:
            identity.append("default_identity")  # 如果为空，添加默认的身份信息

        parsed_rule = Rule(decision_rule=decision_rule, decision_support=decision_support, identity=identity)
        return parsed_rule

    def _convert(self) -> RandomForest:
        """
        从 xgboost.XGBClassifier 对象创建 TERM.tree.RandomForest 的私有方法。
        """
        decision_tree_ensemble = []
        for tree_string in self.xgboost_trees:
            # 解析 tree_string 以提取树结构
            # 你需要解析 XGBoost 树结构并将其转换为一组规则或与你的 Rule 对象兼容的结构

            rule = self.parse_tree(tree_string)
            decision_tree_ensemble.append(rule)

        return RandomForest(
            decision_tree_ensemble,
            weight=self.weight,
            bias=self.bias,
            feature_names=self.feature_names,
            activation=self.activation,
        )


class ScikitExtraTreesClassifierAdapter:
    """
    Class to convert sklearn.ensemble.ExtraTreesClassifier
    into a TERM.tree.RandomForest object.

    Usage:
    adapter = ScikitExtraTreesClassifierAdapter(model, feature_names)
    adapted_model = adapter.random_forest
    """

    def __init__(
            self, scikit_forest: ExtraTreesClassifier, feature_names: List[str]
    ):
        self.feature_names = feature_names

        n_classes = scikit_forest.n_classes_
        if n_classes != 2:
            raise ValueError("Only binary classification is supported.")

        self.bias = 0
        self.weight = 1.0

        scikit_tree_ensemble = scikit_forest.estimators_
        scikit_tree_ensemble = [dtr for dtr in scikit_tree_ensemble]
        self.scikit_tree_ensemble = scikit_tree_ensemble

        self.random_forest = self._convert()

    def _convert(self) -> RandomForest:
        """
        Private method to create the TERM.tree.RandomForest
        from the sklearn.ensemble.ExtraTreesClassifier object.
        """
        decision_tree_ensemble = []
        for scikit_tree in list(self.scikit_tree_ensemble):
            decision_tree = ScikitDecisionTreeClassifierAdapter(
                scikit_tree, self.feature_names
            ).decision_tree
            decision_tree_ensemble.append(decision_tree)

        return RandomForest(
            decision_tree_ensemble,
            weight=self.weight,
            bias=self.bias,
            feature_names=self.feature_names,
            activation="sigmoid",
        )

class ScikitAdaBoostClassifierAdapter:
    """
    Class to convert sklearn.ensemble.AdaBoostClassifier
    into a TERM.tree.RandomForest object.

    Usage:
    adapter = ScikitAdaBoostClassifierAdapter(model, feature_names)
    adapted_model = adapter.random_forest
    """

    def __init__(
            self, scikit_forest: AdaBoostClassifier, feature_names: List[str]
    ):
        self.feature_names = feature_names

        n_classes = scikit_forest.n_classes_
        if n_classes != 2:
            raise ValueError("Only binary classification is supported.")

        self.bias = 0
        self.weight = scikit_forest.get_params()["learning_rate"]
        self.activation = "sigmoid"

        scikit_tree_ensemble = scikit_forest.estimators_
        scikit_tree_ensemble = [dtr for dtr in scikit_tree_ensemble]
        self.scikit_tree_ensemble = scikit_tree_ensemble

        self.random_forest = self._convert()

    def _convert(self) -> RandomForest:
        """
        Private method to create the TERM.tree.RandomForest
        from the sklearn.ensemble.AdaBoostClassifier object.
        """
        decision_tree_ensemble = []
        for scikit_tree in list(self.scikit_tree_ensemble):
            decision_tree = ScikitDecisionTreeClassifierAdapter(
                scikit_tree, self.feature_names
            ).decision_tree
            decision_tree_ensemble.append(decision_tree)

        return RandomForest(
            decision_tree_ensemble,
            weight=self.weight,
            bias=self.bias,
            feature_names=self.feature_names,
            activation=self.activation,
        )


class ScikitGradientBoostingClassifierAdapter:
    """
    Class to convert sklearn.ensemble.GradientBoostingClassifier
    into a TERM.tree.RandomForest object.

    Usage:
    adapter = ScikitGradientBoostingClassifierAdapter(model, feature_names)
    adapted_model = adapter.random_forest
    """

    def __init__(
        self, scikit_forest: GradientBoostingClassifier, feature_names: List[str]
    ):
        self.feature_names = feature_names

        n0, n1 = scikit_forest.init_.class_prior_
        self.bias = np.log(n1 / n0)
        self.weight = scikit_forest.get_params()["learning_rate"]
        self.activation = "sigmoid"

        scikit_tree_ensemble = scikit_forest.estimators_
        for dtr in scikit_tree_ensemble:
            assert len(dtr) == 1  # binary classification
        scikit_tree_ensemble = [dtr[0] for dtr in scikit_tree_ensemble]
        self.scikit_tree_ensemble = scikit_tree_ensemble

        self.random_forest = self._convert()

    def _convert(self) -> RandomForest:
        """
        Private method to create the TERM.tree.RandomForest
        from the sklearn.ensemble.GradientBoostingClassifier object.
        """
        decision_tree_ensemble = []
        for scikit_tree in list(self.scikit_tree_ensemble):
            decision_tree = ScikitDecisionTreeRegressorAdapter(
                scikit_tree, self.feature_names
            ).decision_tree
            decision_tree_ensemble.append(decision_tree)

        return RandomForest(
            decision_tree_ensemble,
            weight=self.weight,
            bias=self.bias,
            feature_names=self.feature_names,
            activation=self.activation,
        )


class ScikitRandomForestClassifierAdapter:
    """
    Class to convert sklearn.ensemble.RandomForestClassifier
    into a TERM.tree.RandomForest object.

    Usage:
    adapter = ScikitRandomForestClassifierAdapter(model, feature_names)
    adapted_model = adapter.random_forest
    """

    def __init__(self, scikit_forest: RandomForestClassifier, feature_names: List[str]):
        self.feature_names = feature_names

        self.bias = 0.0
        self.weight = 1.0 / scikit_forest.get_params()["n_estimators"]
        self.activation = "linear"

        self.scikit_tree_ensemble = scikit_forest.estimators_

        self.random_forest = self._convert()

    def _convert(self) -> RandomForest:
        """
        Private method to create the TERM.tree.RandomForest
        from the sklearn.ensemble.RandomForestClassifier object.
        """
        decision_tree_ensemble = []
        for scikit_tree in list(self.scikit_tree_ensemble):
            decision_tree = ScikitDecisionTreeClassifierAdapter(
                scikit_tree, self.feature_names
            ).decision_tree
            decision_tree_ensemble.append(decision_tree)

        return RandomForest(
            decision_tree_ensemble,
            weight=self.weight,
            bias=self.bias,
            feature_names=self.feature_names,
            activation=self.activation,
        )


class ScikitDecisionTreeRegressorAdapter:
    """
    Class to convert sklearn.tree.DecisionTreeRegressor
    into a TERM.tree.DecisionTree object.

    Usage:
    adapter = ScikitDecisionTreeRegressorAdapter(model, feature_names)
    adapted_model = adapter.decision_tree
    """

    def __init__(self, scikit_tree: DecisionTreeRegressor, feature_names: List[str]):
        self.feature_names = feature_names
        self.feature_indices = scikit_tree.tree_.feature
        self.threshold = scikit_tree.tree_.threshold
        self.children_left = scikit_tree.tree_.children_left
        self.children_right = scikit_tree.tree_.children_right
        self.LEAF_INDEX = _tree.TREE_UNDEFINED

        self.value = scikit_tree.tree_.value
        for i in range(len(scikit_tree.tree_.value)):
            assert len(scikit_tree.tree_.value[i]) == 1  # regressor
            assert len(scikit_tree.tree_.value[i][0]) == 1  # regressor
        self.value = [val[0][0] for val in self.value]

        self.decision_tree = self._convert()

    def _convert(self) -> DecisionTree:
        """
        Private method to create the TERM.tree.DecisionTree
        from the sklearn.tree.DecisionTreeRegressor object.
        """
        nodes: List[DecisionTree] = []

        # Create Tree Nodes
        for i in range(len(self.feature_indices)):
            node_index = self.feature_indices[i]
            if node_index != self.LEAF_INDEX:
                node_name = self.feature_names[node_index]
                nodes = nodes + [
                    DecisionTree(
                        TreeNode(node_name=node_name, threshold=self.threshold[i])
                    )
                ]
            else:
                value = self.value[i]
                nodes = nodes + [DecisionTree(LeafNode(value=value))]

        # Connect Tree Nodes with each other
        for i in range(len(self.feature_indices)):
            node_index = self.feature_indices[i]
            if node_index != self.LEAF_INDEX:
                left_node = nodes[self.children_left[i]]
                nodes[i].left = left_node
                right_node = nodes[self.children_right[i]]
                nodes[i].right = right_node

        root_node = nodes[0]
        return root_node


class ScikitDecisionTreeClassifierAdapter:
    """
    Class to convert sklearn.tree.DecisionTreeClassifier
    into a TERM.tree.DecisionTree object.

    Usage:
    adapter = ScikitDecisionTreeClassifierAdapter(model, feature_names)
    adapted_model = adapter.decision_tree
    """

    def __init__(self, scikit_tree: DecisionTreeClassifier, feature_names: List[str]):
        self.feature_names = feature_names

        self.feature_indices = scikit_tree.tree_.feature
        self.threshold = scikit_tree.tree_.threshold
        self.children_left = scikit_tree.tree_.children_left
        self.children_right = scikit_tree.tree_.children_right
        self.LEAF_INDEX = _tree.TREE_UNDEFINED

        value = []
        for i in range(len(scikit_tree.tree_.value)):
            assert len(scikit_tree.tree_.value[i]) == 1  # binary classification
            assert len(scikit_tree.tree_.value[i][0]) == 2  # binary classification

            prob_0 = scikit_tree.tree_.value[i][0][0]
            prob_1 = scikit_tree.tree_.value[i][0][1]
            value.append(prob_1 / (prob_0 + prob_1))
        self.value = value

        self.decision_tree = self._convert()

    def _convert(self) -> DecisionTree:
        """
        Private method to create the TERM.tree.DecisionTree
        from the sklearn.tree.DecisionTreeClassifier object.
        """
        nodes: List[DecisionTree] = []

        # Create Tree Nodes
        for i in range(len(self.feature_indices)):
            node_index = self.feature_indices[i]
            if node_index != self.LEAF_INDEX:
                node_name = self.feature_names[node_index]
                nodes = nodes + [
                    DecisionTree(
                        TreeNode(node_name=node_name, threshold=self.threshold[i])
                    )
                ]
            else:
                value = self.value[i]
                nodes = nodes + [DecisionTree(LeafNode(value=value))]

        # Connect Tree Nodes with each other
        for i in range(len(self.feature_indices)):
            node_index = self.feature_indices[i]
            if node_index != self.LEAF_INDEX:
                left_node = nodes[self.children_left[i]]
                nodes[i].left = left_node
                right_node = nodes[self.children_right[i]]
                nodes[i].right = right_node

        root_node = nodes[0]
        return root_node
