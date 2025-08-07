from __future__ import annotations

import logging
import math
import re
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Tuple, Set, Optional
import random

from eventlet.green import os
from mpmath import mp

import numpy as np
import pandas as pd
import sklearn
from sklearn.cluster import AgglomerativeClustering
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier ,AdaBoostClassifier,ExtraTreesClassifier
from catboost import CatBoostClassifier
from lightgbm import LGBMClassifier
from xgboost import XGBClassifier
from tqdm import tqdm

from term.adapter import (
    ScikitGradientBoostingClassifierAdapter,
    ScikitRandomForestClassifierAdapter,
    ScikitAdaBoostClassifierAdapter,
    XGBoostClassifierAdapter,

)
from term.rule import Rule
from term.tree import RandomForest

log = logging.getLogger()

class SecondOrderSystem:
    def __init__(self, initial_state=0):
        self.state = initial_state
        self.time_constant = 1  # 时间常数
        self.damping_ratio = 0.7  # 阻尼比
        self.dt = 0.01  # 时间步长

    def update(self, input_signal):
        derivative = (input_signal - self.state) / self.time_constant
        acceleration = (derivative - 2 * self.damping_ratio * np.sqrt(derivative) - self.state) / self.time_constant
        self.state += acceleration * self.dt
        return self.state

class PIDController:
    def __init__(self, kp=1, ki=0, kd=0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral = 0
        self.previous_error = 0

    def control(self, setpoint, measured_value):
        error = setpoint - measured_value
        self.integral += error
        derivative = error - self.previous_error
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        self.previous_error = error
        return output

class ModelExplainer:

    def __init__(
        self, model: sklearn.ensemble,feature_names: List[str], verbose: bool = False
    ):
        self.feature_names = feature_names
        for f in feature_names:
            if re.search("[^a-zA-Z0-9_]", f):
                raise ValueError(
                    "Only alphanumeric characters and underscores are allowed "
                    + "in feature names. But found feature name: "
                    + str(f)
                )

        if verbose is True:
            logging.basicConfig(format="%(message)s", level=logging.DEBUG)
        else:
            logging.basicConfig(format="%(message)s")

        if isinstance(model, GradientBoostingClassifier):
            self.random_forest = ScikitGradientBoostingClassifierAdapter(
                model, feature_names
            ).random_forest
        elif isinstance(model, RandomForestClassifier):
            self.random_forest = ScikitRandomForestClassifierAdapter(
                model, feature_names
            ).random_forest
        elif isinstance(model, AdaBoostClassifier):
            self.random_forest = ScikitAdaBoostClassifierAdapter(
                model,feature_names
            ).random_forest
        elif isinstance(model, XGBClassifier):
            self.random_forest = XGBoostClassifierAdapter(
                model, feature_names
            ).random_forest
        else:
            raise ValueError(
                "Only GradientBoostingClassifier and RandomForestClassifier and AdaBoostClassifier "
                + "are supported. But received "
                + str(type(model))
            )

    def explain(
        self,
        X: List[List[float]],
        y: List[int],
        num_stages: int = None,
        min_precision: float = 0.95,
    ) -> List[str]:

        if len(X) != len(y):
            raise ValueError("X and y should have the same length")
        for i in range(len(y)):
            if y[i] not in [0, 1]:
                raise ValueError("entries y should only be 0 or 1.")

        self.rule_builder = RuleBuilder(
            random_forest=self.random_forest,
            num_stages=num_stages,
            min_precision=min_precision,
        )
        rules = self.rule_builder.explain(X, y)
        rules_as_str = [str(r) for r in rules]
        return rules_as_str

    def predict(self, X: List[List[float]]) -> List[int]:
        """
        A method to apply rules found by the explain() method
        on a given input data. Any data that satisfies at least
        one rule from the rule list found by the explain() is labelled
        as belonging to the positive class. All other data is labelled
        as belonging to the negative class.

        This method can only be called after calling the explain()
        method. Otherwise, it throws AttributeError.

        Returns a List of class predictions coressponding to the data.

        Parameters
        ----------
        X: 2d numpy.array
            2 dimensional input data to apply the rules extracted by the explainer.

        Returns
        -------
        class_predictions: List[int]
            A List of class predictions coressponding to the data.

        Raises
        ------
        AttributeError:
            when called before calling explain()
        """
        try:
            df = pd.DataFrame(X, columns=self.feature_names)
            y_rules = self.rule_builder.apply(df)
        except AttributeError:
            raise AttributeError(
                "rules to explain the tree ensemble are not set. "
                + "Call explain() before calling apply()"
            )
        return y_rules

    def get_fidelity(
        self, X: List[List[float]] = None, y: List[int] = None
    ) -> Tuple[float, float, float]:
        """
        A method to evaluate the rule list extracted by the `explain` method

        Returns a fidelity on positives, negative, overall

        Parameters
        ----------
        X: 2d numpy.array, optional
            2 dimensional data with feature values used for calculating fidelity.
            Defaults to data used by the model for rule extraction.
        y: 1d numpy.array, optional
            1 dimensional model class predictions (0 or 1) from the `model` on X.
            Defaults to model class predictions on the data used
            by the model for rule extraction.

        Returns
        -------
        fidelity: [float, float, float]
            Fidelity is the fraction of data for which the rule list agrees
            with the tree ensemble. Returns the fidelity on overall data,
            positive predictions and negative predictions by the model.

        Examples
        --------
        >>> (fidelity, fidelity_pos, fidelity_neg) = model_explainer.get_fidelity()
        """
        if (X is not None) and (y is not None):
            df = pd.DataFrame(X, columns=self.feature_names)
            y_rules = self.rule_builder.apply(df)
            fidelity_positives = 0.0
            fidelity_negatives = 0.0
            positives = 0.0 + 1e-6
            negatives = 0.0 + 1e-6
            for i in range(len(y)):
                if y[i] == 1:
                    positives = positives + 1
                    if y[i] == y_rules[i]:
                        fidelity_positives = fidelity_positives + 1
                if y[i] == 0:
                    negatives = negatives + 1
                    if y[i] == y_rules[i]:
                        fidelity_negatives = fidelity_negatives + 1

            fidelity = (fidelity_positives + fidelity_negatives) / (
                positives + negatives
            )
            fidelity_positives = fidelity_positives / positives
            fidelity_negatives = fidelity_negatives / negatives
            return (fidelity, fidelity_positives, fidelity_negatives)

        return self.rule_builder.get_fidelity()


class RuleBuilder:
    """
    A class to get rules from individual trees in a tree ensemble
    and combine them together in multiple stages to explain cross-tree
    interactions within the tree ensemble. RuleBuilder consists of:
    1) The tree ensemble model, from which to extract rules
        to explain the positive class.
    2) number of stages: The rules are combined in stages starting
        from stage 1, stage 2 to all the way till stage n where n
        is the number of trees in the ensemble. The rules extracted
        in stage i, capture rules from i-tree interactions in the
        tree ensemble.
    3) minimum precision: minimum precision of extracted rules

    RuleBuilder implements the TE2Rules algorithm. Calling explain()
    explains the tree ensemble using rules for the postive class
    prediction.
    """

    def __init__(
        self,
        random_forest: RandomForest,
        num_stages: int = None,
        min_precision: float = 0.95,
    ):
        self.random_forest = random_forest
        # if num_stages not set by user, will set it to the number of trees
        # note that we neednum_stages <= num_trees
        if num_stages is not None:
            self.num_stages = min(num_stages, self.random_forest.get_num_trees())
        else:
            self.num_stages = self.random_forest.get_num_trees()
        self.min_precision = min_precision

    def explain(self, X: List[List[float]], y: List[int]) -> List[Rule]:

        self.data = X
        self.labels = y

        self.positives = []
        for i in range(len(self.labels)):
            if self.labels[i] == 1:
                self.positives.append(i)
        log.info("")
        log.info("Positives: " + str(len(self.positives)))

        log.info("")
        log.info("Rules from trees")
        self.candidate_rules = self.random_forest.get_rules(data=self.data)
        self.solution_rules: List[Rule] = []
        log.info(str(len(self.candidate_rules)) + " candidate rules")

        log.info("Deduping")
        self.candidate_rules = self._deduplicate(self.candidate_rules)
        self.solution_rules = self._deduplicate(self.solution_rules)
        log.info(str(len(self.candidate_rules)) + " candidate rules")

        self._generate_solutions()

        log.info("Simplifying Solutions")
        self.solution_rules = self._shorten(self.solution_rules)
        self.solution_rules = self._deduplicate(self.solution_rules)
        log.info(str(len(self.solution_rules)) + " solutions")

        log.info("")
        log.info("Set Cover")
        total_support: List[int] = []
        for r in self.solution_rules:
            total_support = list(set(total_support).union(set(r.decision_support)))
        self._rules_to_cover_positives(
            list(set(total_support).intersection(set(self.positives)))
        )
        log.info(str(len(self.solution_rules)) + " rules found")

        return self.solution_rules

    def _rules_to_cover_positives(self, positives: List[int]) -> None:
        """
        A method to select rules with high coverage using a
        greedy set cover on the set of positive class labels
        explained by each rule.
        """
        original_rules = {}
        positive_coverage = {}
        for r in self.solution_rules:
            positive_coverage[str(r)] = list(
                set(positives).intersection(set(r.decision_support))
            )
            original_rules[str(r)] = r

        selected_rules: List[Rule] = []
        covered_positives: List[int] = []

        while (len(covered_positives) < len(positives)) and (
            len(selected_rules) < len(self.solution_rules)
        ):
            max_coverage_rule = list(positive_coverage.keys())[0]
            for rule in list(positive_coverage.keys()):
                if len(positive_coverage[rule]) > len(
                    positive_coverage[max_coverage_rule]
                ):
                    max_coverage_rule = rule
                else:
                    if len(positive_coverage[rule]) == len(
                        positive_coverage[max_coverage_rule]
                    ):
                        if len(original_rules[rule].decision_rule) < len(
                            original_rules[max_coverage_rule].decision_rule
                        ):
                            max_coverage_rule = rule

            selected_rules.append(original_rules[max_coverage_rule])
            new_covered_positives = positive_coverage[max_coverage_rule]
            covered_positives = list(
                set(covered_positives).union(set(new_covered_positives))
            )

            for rule in list(positive_coverage.keys()):
                positive_coverage[rule] = list(
                    set(positive_coverage[rule]).difference(set(new_covered_positives))
                )
                if len(positive_coverage[rule]) == 0:
                    positive_coverage.pop(rule)

        self.solution_rules = selected_rules

    def _local_search(self, selected_rules: List[Rule], positives: List[int]) -> Optional[Rule]:
        """
        局部搜索函数，尝试改进当前选定的规则集合
        """
        # 随机选择要替换的规则
        rule_to_replace = random.choice(selected_rules)

        # 从规则集合中移除选定的规则
        selected_rules.remove(rule_to_replace)

        # 随机选择一个新的规则加入规则集合
        new_rule = random.choice(self.solution_rules)
        selected_rules.append(new_rule)

        # 计算新规则集合的覆盖情况
        covered_positives = set()
        for rule in selected_rules:
            covered_positives.update(set(rule.decision_support))

        # 如果新规则集合覆盖的正例数量增加，则返回新规则，否则返回 None
        if len(covered_positives) > len(set(positives)):
            return new_rule
        else:
            return None

    def _generate_solutions(self) -> None:
        """
        加入并行计算和PID控制
        """
        positives_to_explain = self.positives
        candidate_rules_len = len(self.candidate_rules)
        labels_len = len(self.labels)

        # 初始化二阶惯性系统和PID控制器
        system = SecondOrderSystem()
        pid_controller = PIDController(kp=1, ki=1, kd=0.5)

        for stage in range(self.num_stages):
            if len(positives_to_explain) == 0:
                continue

            log.info("")
            log.info(f"Rules from {stage + 1} trees")
            # 获取待合并规则的索引
            join_indices = self._get_join_indices(self.candidate_rules)

            def process_join_index(index_pair):
                i, j = index_pair
                joined_rule = self.candidate_rules[i].join(self.candidate_rules[j])
                if joined_rule:
                    is_solution, keep_candidate = self._filter_candidates(joined_rule, self.labels)
                    if is_solution:
                        return joined_rule, True
                    if keep_candidate:
                        return joined_rule, False
                return None, False

            # 自适应地选择线程数量
            max_workers = os.cpu_count() * 2  # 根据 CPU 核心数量来选择线程数量

            # 创建线程池，并自适应地选择线程数量
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                results = list(tqdm(executor.map(process_join_index, join_indices), total=len(join_indices)))

            new_candidates = []
            new_solutions = []
            for result in results:
                joined_rule, is_solution = result
                if joined_rule is not None:
                    if is_solution:
                        new_solutions.append(joined_rule)
                    else:
                        new_candidates.append(joined_rule)

            self.candidate_rules = new_candidates
            self.solution_rules.extend(new_solutions)

            log.info(f"{len(self.candidate_rules)} candidates")
            log.info(f"{len(self.solution_rules)} solutions")

            positives_to_explain_set = set(positives_to_explain)
            for rule in new_solutions:
                positives_to_explain_set.difference_update(rule.decision_support)
            positives_to_explain = list(positives_to_explain_set)

            log.info("Unexplained Positives")
            log.info(len(positives_to_explain))
            # 剪枝
            log.info("Pruning Candidates")
            self.candidate_rules = self._prune(self.candidate_rules, positives_to_explain)
            log.info(f"{len(self.candidate_rules)} candidates")
            # 去重
            log.info("Deduping")
            self.candidate_rules = self._deduplicate(self.candidate_rules)
            self.solution_rules = self._deduplicate(self.solution_rules)
            log.info(f"{len(self.candidate_rules)} candidates")
            log.info(f"{len(self.solution_rules)} solutions")

            fidelity, fidelity_positives, fidelity_negatives = self.get_fidelity()

            log.info("Fidelity")
            log.info(f"Total: {fidelity:.6f},"
                     f" Positive: {fidelity_positives:.6f},"
                     f" Negative: {fidelity_negatives:.6f}"
                     )
            log.info("")

            # 更新PID控制器参数
            pid_controller.kp += 0.1  # 举例增加KP参数的值
    def _score_rule_using_data(self, rule: Rule, labels: List[int]) -> List[int]:
        """
        A method to score all rules using the data in their
        support and their corresponding labels predicted by
        the tree ensemble model. This method returns list of
        class labels of the data satisfied by the rule.
        """
        decision_value = []
        for data_index in rule.decision_support:
            decision_value.append(labels[data_index])
        return decision_value

    """
    def score_rule_using_model(self, rule: Rule) -> Tuple[float, float]:
        min_score, max_score = self.random_forest.get_rule_score(rule.decision_rule)
        return min_score, max_score
    """
   #
    def _filter_candidates(self, rule: Rule, labels: List[int]) -> Tuple[bool, bool]:
        scores = self._score_rule_using_data(rule, labels)

        if not scores:
            return False, False  # No scores, not a solution and cannot become one

        max_score = max(scores)
        avg_score = sum(scores) / len(scores)

        if avg_score >= self.min_precision:
            return True, False  # Already a solution

        if max_score == 0:
            return False, False  # Cannot become a solution

        return False, True  # Can become a solution

    # 修改后的代码中，我们将条件判断简化并合并，减少了不必要的变量赋值和条件检查，使代码更为简洁清晰。

    def get_fidelity(self, use_top: int = None) -> Tuple[float, float, float]:
        if use_top is None:
            use_top = len(self.solution_rules)

        support = set().union(*(set(r.decision_support) for r in self.solution_rules[:use_top]))

        # Compute the predicted labels using the support set
        y_pred_rules = [int(i in support) for i in range(len(self.labels))]

        # Compute the overall fidelity, positive fidelity, and negative fidelity
        total = len(self.labels)
        positives = sum(self.labels)
        negatives = total - positives

        fidelity_total = sum(y_pred == label for y_pred, label in zip(y_pred_rules, self.labels)) / total
        fidelity_positives = sum(
            y_pred == 1 and label == 1 for y_pred, label in zip(y_pred_rules, self.labels)) / positives
        fidelity_negatives = sum(
            y_pred == 0 and label == 0 for y_pred, label in zip(y_pred_rules, self.labels)) / negatives

        return fidelity_total, fidelity_positives, fidelity_negatives

    def _deduplicate(self, rules: List[Rule]) -> List[Rule]:
        """
        A method to deduplicate rules generated from multiple
        source trees and combine the sources into the rule's identity.
        """
        rules_map = {}
        for rule in rules:
            key = str(rule)
            if key not in rules_map:
                # 使用字典的setdefault方法来初始化identity为集合
                rules_map[key] = rule
            else:
                # 直接使用union合并标识
                rules_map[key].identity = list(set(rules_map[key].identity).union(set(rule.identity)))

        dedup_rules = list(rules_map.values())
        return dedup_rules

    def _shorten(self, rules: List[Rule]) -> List[Rule]:
        """
        A method to shorten the rules by dropping redundant
        terms to make the rules shorter.
        """
        for i in range(len(rules)):
            pred_dict = {}
            pred_set = set()
            for pred in rules[i].decision_rule:
                f, op, val = pred.split()
                op_type = "equal"
                if op in ("<", "<="):
                    op_type = "less than"
                elif op in (">", ">="):
                    op_type = "greater than"
                if (f, op_type) not in pred_set:
                    pred_set.add((f, op_type))
                    pred_dict[(f, op_type)] = (op, val)
                else:
                    # combine rules
                    old_op, old_val = pred_dict[(f, op_type)]
                    if (old_op in ("<=", "<") and op in ("<", "<=") and val == old_val) or (
                            old_op in (">=", ">") and op in (">", ">=") and val == old_val
                    ) or (op_type == "less than" and val < old_val) or (
                            op_type == "greater than" and val > old_val
                    ):
                        pred_dict[(f, op_type)] = (op, val)
            # make shorter rule from predicate list
            final_rule = [(f, op, val) for (f, op_type), (op, val) in pred_dict.items()]
            rules[i].decision_rule = [" ".join(pred) for pred in final_rule]
        return rules

    def apply(self, df: pd.DataFrame) -> List[int]:
        """
        A method to apply rules found by the explain() method
        on a given pandas dataframe. Any data that satisfies at least
        one rule from the rule list found by the explain() is labelled
        as belonging to the positive class. All other data is labelled
        as belonging to the negative class.

        This method can only be called after calling the explain()
        method. Otherwise, it throws AttributeError.
        """
        if not hasattr(self, "solution_rules"):
            raise AttributeError("Rules to explain the tree ensemble are not set. Call explain() before calling apply()")

        # 获取所有匹配规则的索引
        coverage = set()
        for r in self.solution_rules:
            matches = df.index[df.eval(r)].tolist()
            coverage.update(matches)

        # 生成标签列表
        y_rules = [1 if i in coverage else 0 for i in range(len(df))]
        return y_rules

    def _get_join_indices(self, rules: List[Rule]) -> List[Tuple[int, int]]:
        # 使用哈希表存储标识符与索引的映射关系
        left_map: Dict[str, Set[int]] = {}
        right_map: Dict[str, Set[int]] = {}

        for i, rule in enumerate(rules):
            rule.create_identity_map()
            left_keys = list(rule.left_identity_map.keys())
            right_keys = list(rule.right_identity_map.keys())

            for key in left_keys:
                left_map.setdefault(key, set()).add(i)

            for key in right_keys:
                right_map.setdefault(key, set()).add(i)

        join_keys = set(left_map.keys()).intersection(right_map.keys())

        pairs = set()
        for key in join_keys:
            left_indices = left_map[key]
            right_indices = right_map[key]
            # 使用两个索引集合的笛卡尔积，找到可以合并的规则对
            for i in left_indices:
                for j in right_indices:
                    if i < j:
                        pairs.add((i, j))

        pairs_list = list(pairs)
        pairs_list.sort()  # 可以移除这一步，因为集合的迭代顺序不是固定的
        return pairs_list

    def _prune(self, rules: List[Rule], positives: List[int]) -> List[Rule]:
        positive_set = set(positives)
        pruned_rules = list(filter(lambda rule: set(rule.decision_support).intersection(positive_set), rules))
        return pruned_rules




