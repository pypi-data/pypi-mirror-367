#
# Copyright (C) 2020-2025 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

from __future__ import annotations  # TODO: remove when Python3.9 support is dropped

import copy
import json
from itertools import starmap
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
from openvino import Model, Type
from openvino import opset10 as opset
from openvino.preprocess import PrePostProcessor

from model_api.models.image_model import ImageModel
from model_api.models.result import ClassificationResult, Label
from model_api.models.types import BooleanValue, ListValue, NumericalValue, StringValue
from model_api.models.utils import softmax

if TYPE_CHECKING:
    from model_api.adapters.inference_adapter import InferenceAdapter


class ClassificationModel(ImageModel):
    """Classification Model.

    Args:
        inference_adapter (InferenceAdapter): Inference adapter
        configuration (dict, optional): Configuration parameters. Defaults to {}.
        preload (bool, optional): Whether to preload the model. Defaults to False.

    Example:
        >>> from model_api.models import ClassificationModel
        >>> import cv2
        >>> model = ClassificationModel.create_model("./path_to_model.xml")
        >>> image = cv2.imread("path_to_image.jpg")
        >>> result = model.predict(image)
        ClassificationResult(
            top_labels=[(1, 'bicycle', 0.90176445), (6, 'car', 0.85433626), (7, 'cat', 0.60699755)],
            saliency_map=array([], dtype=float64),
            feature_vector=array([], dtype=float64),
            raw_scores=array([], dtype=float64)
        )
    """

    __model__ = "Classification"

    def __init__(self, inference_adapter: InferenceAdapter, configuration: dict = {}, preload: bool = False) -> None:
        super().__init__(inference_adapter, configuration, preload=False)
        self.topk: int
        self.labels: list[str]
        self.path_to_labels: str
        self.multilabel: bool
        self.hierarchical: bool
        self.hierarchical_config: str
        self.confidence_threshold: float
        self.output_raw_scores: bool
        self.hierarchical_postproc: str
        self.labels_resolver: GreedyLabelsResolver | ProbabilisticLabelsResolver

        self._check_io_number(1, (1, 2, 3, 4, 5))
        if self.path_to_labels:
            self.labels = self._load_labels(self.path_to_labels)
        if len(self.outputs) == 1:
            self._verify_single_output()

        self.raw_scores_name = _raw_scores_name
        if self.hierarchical:
            self.embedded_processing = True
            self.out_layer_names = _get_non_xai_names(self.outputs.keys())
            _append_xai_names(self.outputs.keys(), self.out_layer_names)
            if not self.hierarchical_config:
                self.raise_error("Hierarchical classification config is empty.")
            self.raw_scores_name = self.out_layer_names[0]
            self.hierarchical_info = json.loads(self.hierarchical_config)

            if self.hierarchical_postproc == "probabilistic":
                self.labels_resolver = ProbabilisticLabelsResolver(
                    self.hierarchical_info,
                )
            else:
                self.labels_resolver = GreedyLabelsResolver(self.hierarchical_info)

            if preload:
                self.load()
            return

        if self.multilabel:
            self.embedded_processing = True
            self.out_layer_names = _get_non_xai_names(self.outputs.keys())
            _append_xai_names(self.outputs.keys(), self.out_layer_names)
            self.raw_scores_name = self.out_layer_names[0]
            if preload:
                self.load()
            return

        try:
            addOrFindSoftmaxAndTopkOutputs(
                self.inference_adapter,
                self.topk,
                self.output_raw_scores,
            )
            self.embedded_topk = True
            self.out_layer_names = ["indices", "scores"]
            if self.output_raw_scores:
                self.out_layer_names.append(self.raw_scores_name)
        except (RuntimeError, AttributeError):
            # exception means we have a non-ov model, or a model behind OVMS
            # with already inserted softmax and topk
            if self.embedded_processing and len(self.outputs) >= 2:
                self.embedded_topk = True
                self.out_layer_names = ["indices", "scores"]
                self.raw_scores_name = _raw_scores_name
            else:  # likely a non-ov model
                self.embedded_topk = False
                self.out_layer_names = _get_non_xai_names(self.outputs.keys())
                self.raw_scores_name = self.out_layer_names[0]

        self.embedded_processing = True

        _append_xai_names(self.outputs.keys(), self.out_layer_names)
        if preload:
            self.load()

    def _load_labels(self, labels_file: str) -> list:
        with Path(labels_file).open() as f:
            labels = []
            for s in f:
                begin_idx = s.find(" ")
                if begin_idx == -1:
                    self.raise_error("The labels file has incorrect format.")
                end_idx = s.find(",")
                labels.append(s[(begin_idx + 1) : end_idx])
        return labels

    def _verify_single_output(self) -> None:
        layer_name = next(iter(self.outputs))
        layer_shape = self.outputs[layer_name].shape

        if len(layer_shape) != 2 and len(layer_shape) != 4:
            self.raise_error(
                "The Classification model wrapper supports topologies only with 2D or 4D output",
            )
        if len(layer_shape) == 4 and (layer_shape[2] != 1 or layer_shape[3] != 1):
            self.raise_error(
                "The Classification model wrapper supports topologies only with 4D "
                "output which has last two dimensions of size 1",
            )
        if self.labels:
            if layer_shape[1] == len(self.labels) + 1:
                self.labels.insert(0, "other")
                self.logger.warning("\tInserted 'other' label as first.")
            if layer_shape[1] > len(self.labels):
                self.raise_error(
                    "Model's number of classes must be greater then "
                    f"number of parsed labels ({layer_shape[1]}, {len(self.labels)})",
                )

    @classmethod
    def parameters(cls) -> dict:
        parameters = super().parameters()
        parameters.update(
            {
                "topk": NumericalValue(
                    value_type=int,
                    default_value=1,
                    min=1,
                    description="Number of most likely labels",
                ),
                "labels": ListValue(description="List of class labels", value_type=str),
                "path_to_labels": StringValue(
                    description="Path to file with labels. Overrides the labels, if they sets via 'labels' parameter",
                ),
                "multilabel": BooleanValue(
                    default_value=False,
                    description="Predict a set of labels per image",
                ),
                "hierarchical": BooleanValue(
                    default_value=False,
                    description="Predict a hierarchy if labels per image",
                ),
                "hierarchical_config": StringValue(
                    default_value="",
                    description="Extra config for decoding hierarchical predictions",
                ),
                "confidence_threshold": NumericalValue(
                    default_value=0.5,
                    description="Predict a set of labels per image",
                ),
                "output_raw_scores": BooleanValue(
                    default_value=False,
                    description="Output all scores for multiclass classification",
                ),
                "hierarchical_postproc": StringValue(
                    default_value="greedy",
                    choices=("probabilistic", "greedy"),
                    description="Type of hierarchical postprocessing",
                ),
            },
        )
        return parameters

    def postprocess(self, outputs: dict, meta: dict) -> ClassificationResult:
        del meta  # unused
        if self.multilabel:
            result = self.get_multilabel_predictions(
                outputs[self.out_layer_names[0]].squeeze(),
            )
        elif self.hierarchical:
            result = self.get_hierarchical_predictions(
                outputs[self.out_layer_names[0]].squeeze(),
            )
        else:
            result = self.get_multiclass_predictions(outputs)

        raw_scores = np.ndarray(0)
        if self.output_raw_scores:
            raw_scores = self.get_all_probs(outputs[self.raw_scores_name])

        return ClassificationResult(
            result,
            self.get_saliency_maps(outputs),
            outputs.get(_feature_vector_name, np.ndarray(0)),
            raw_scores,
        )

    def get_saliency_maps(self, outputs: dict) -> np.ndarray:
        """Returns saliency map model output. In hierarchical case reorders saliency maps
        to match the order of labels in .XML meta.
        """
        saliency_maps = outputs.get(_saliency_map_name, np.ndarray(0))
        if not self.hierarchical:
            return saliency_maps

        reordered_saliency_maps: list[list[np.ndarray]] = [[] for _ in range(len(saliency_maps))]
        model_classes = self.hierarchical_info["cls_heads_info"]["class_to_group_idx"]
        label_to_model_out_idx = {lbl: i for i, lbl in enumerate(model_classes.keys())}
        for batch in range(len(saliency_maps)):
            for label in self.labels:
                idx = label_to_model_out_idx[label]
                reordered_saliency_maps[batch].append(saliency_maps[batch][idx])
        return np.array(reordered_saliency_maps)

    def get_all_probs(self, logits: np.ndarray) -> np.ndarray:
        if self.multilabel:
            probs = sigmoid_numpy(logits.reshape(-1))
        elif self.hierarchical:
            logits = logits.reshape(-1)
            probs = np.copy(logits)
            cls_heads_info = self.hierarchical_info["cls_heads_info"]
            for i in range(cls_heads_info["num_multiclass_heads"]):
                logits_begin, logits_end = cls_heads_info["head_idx_to_logits_range"][str(i)]
                probs[logits_begin:logits_end] = softmax(
                    logits[logits_begin:logits_end],
                )

            if cls_heads_info["num_multilabel_classes"]:
                logits_begin = cls_heads_info["num_single_label_classes"]
                probs[logits_begin:] = sigmoid_numpy(logits[logits_begin:])
        elif self.embedded_topk:
            probs = logits.reshape(-1)
        else:
            probs = softmax(logits.reshape(-1))
        return probs

    def get_hierarchical_predictions(self, logits: np.ndarray) -> list[Label]:
        predicted_labels = []
        predicted_scores = []
        cls_heads_info = self.hierarchical_info["cls_heads_info"]
        for i in range(cls_heads_info["num_multiclass_heads"]):
            logits_begin, logits_end = cls_heads_info["head_idx_to_logits_range"][str(i)]
            head_logits = logits[logits_begin:logits_end]
            head_logits = softmax(head_logits)
            j = np.argmax(head_logits)
            label_str = cls_heads_info["all_groups"][i][j]
            predicted_labels.append(label_str)
            predicted_scores.append(head_logits[j])

        if cls_heads_info["num_multilabel_classes"]:
            logits_begin = cls_heads_info["num_single_label_classes"]
            head_logits = logits[logits_begin:]
            head_logits = sigmoid_numpy(head_logits)

            for i in range(head_logits.shape[0]):
                if head_logits[i] > self.confidence_threshold:
                    label_str = cls_heads_info["all_groups"][cls_heads_info["num_multiclass_heads"] + i][0]
                    predicted_labels.append(label_str)
                    predicted_scores.append(head_logits[i])

        predictions = list(zip(predicted_labels, predicted_scores))
        return self.labels_resolver.resolve_labels(predictions)

    def get_multilabel_predictions(self, logits: np.ndarray) -> list[Label]:
        logits = sigmoid_numpy(logits)
        scores = []
        indices = []
        for i in range(logits.shape[0]):
            if logits[i] > self.confidence_threshold:
                indices.append(i)
                scores.append(logits[i])
        labels = [self.labels[i] if self.labels else "" for i in indices]

        return list(starmap(Label, zip(indices, labels, scores)))

    def get_multiclass_predictions(self, outputs: dict) -> list[Label]:
        if self.embedded_topk:
            indicesTensor = outputs[self.out_layer_names[0]][0]
            scoresTensor = outputs[self.out_layer_names[1]][0]
            labels = [self.labels[i] if self.labels else "" for i in indicesTensor]
        else:
            scoresTensor = softmax(outputs[self.out_layer_names[0]][0])
            indicesTensor = [int(np.argmax(scoresTensor))]
            labels = [self.labels[i] if self.labels else "" for i in indicesTensor]
        return list(starmap(Label, zip(indicesTensor, labels, scoresTensor)))


def addOrFindSoftmaxAndTopkOutputs(inference_adapter: InferenceAdapter, topk: int, output_raw_scores: bool) -> None:
    softmaxNode = None
    for i in range(len(inference_adapter.model.outputs)):
        output_node = inference_adapter.model.get_output_op(i).input(0).get_source_output().get_node()
        if output_node.get_type_name() == "Softmax":
            softmaxNode = output_node
        elif output_node.get_type_name() == "TopK":
            return

    if softmaxNode is None:
        logitsNode = inference_adapter.model.get_output_op(0).input(0).get_source_output().get_node()
        softmaxNode = opset.softmax(logitsNode.output(0), 1)
    k = opset.constant(topk, np.int32)
    topkNode = opset.topk(softmaxNode, k, 1, "max", "value")

    indices = topkNode.output(0)
    scores = topkNode.output(1)
    results_descr = [indices, scores]
    if output_raw_scores:
        raw_scores = softmaxNode.output(0)
        results_descr.append(raw_scores)
    for output in inference_adapter.model.outputs:
        if _saliency_map_name in output.get_names() or _feature_vector_name in output.get_names():
            results_descr.append(output)

    source_rt_info = inference_adapter.get_model().get_rt_info()
    inference_adapter.model = Model(
        results_descr,
        inference_adapter.model.get_parameters(),
        "classification",
    )

    if "model_info" in source_rt_info:
        source_rt_info = source_rt_info["model_info"]
        for k in source_rt_info:
            inference_adapter.model.set_rt_info(source_rt_info[k], ["model_info", k])

    # manually set output tensors name for created topK node
    inference_adapter.model.outputs[0].tensor.set_names({"scores"})
    inference_adapter.model.outputs[1].tensor.set_names({"indices"})
    if output_raw_scores:
        inference_adapter.model.outputs[2].tensor.set_names({_raw_scores_name})

    # set output precisions
    ppp = PrePostProcessor(inference_adapter.model)
    ppp.output("indices").tensor().set_element_type(Type.i32)
    ppp.output("scores").tensor().set_element_type(Type.f32)
    if output_raw_scores:
        ppp.output(_raw_scores_name).tensor().set_element_type(Type.f32)
    inference_adapter.model = ppp.build()


def sigmoid_numpy(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


class GreedyLabelsResolver:
    def __init__(self, hierarchical_config: dict) -> None:
        self.label_to_idx = hierarchical_config["cls_heads_info"]["label_to_idx"]
        self.label_relations = hierarchical_config["label_tree_edges"]
        self.label_groups = hierarchical_config["cls_heads_info"]["all_groups"]

        self.label_tree = SimpleLabelsGraph(list(self.label_to_idx.keys()))
        for child, parent in self.label_relations:
            self.label_tree.add_edge(parent, child)

    def resolve_labels(self, predictions: list[tuple]) -> list[Label]:
        """Resolves hierarchical labels and exclusivity based on a list of ScoredLabels (labels with probability).
        The following two steps are taken:
        - select the most likely label from each label group
        - add it and it's predecessors if they are also most likely labels (greedy approach).

        Args:
            predictions: a list of tuples (label name, score)
        """

        def get_predecessors(lbl: str, candidates: list[str]) -> list:
            """Return all predecessors.

            Returns all the predecessors of the input label or an empty list if one of the predecessors is not a
            candidate.
            """
            predecessors = []

            last_parent = self.label_tree.get_parent(lbl)
            while last_parent is not None:
                if last_parent not in candidates:
                    return []
                predecessors.append(last_parent)
                last_parent = self.label_tree.get_parent(last_parent)
            predecessors.append(lbl)
            return predecessors

        label_to_prob = dict.fromkeys(self.label_to_idx.keys(), 0.0)
        for lbl, score in predictions:
            label_to_prob[lbl] = score

        candidates = []
        for g in self.label_groups:
            if len(g) == 1 and label_to_prob[g[0]] > 0.0:
                candidates.append(g[0])
            else:
                max_prob = 0.0
                max_label = None
                for lbl in g:
                    if label_to_prob[lbl] > max_prob:
                        max_prob = label_to_prob[lbl]
                        max_label = lbl
                if max_label is not None:
                    candidates.append(max_label)

        output_labels = []
        for lbl in candidates:
            if lbl in output_labels:
                continue
            labels_to_add = get_predecessors(lbl, candidates)
            for new_lbl in labels_to_add:
                if new_lbl not in output_labels:
                    output_labels.append(new_lbl)

        return [Label(self.label_to_idx[lbl], lbl, label_to_prob[lbl]) for lbl in sorted(output_labels)]


class ProbabilisticLabelsResolver(GreedyLabelsResolver):
    def __init__(self, hierarchical_config: dict, warmup_cache: bool = True) -> None:
        super().__init__(hierarchical_config)
        if warmup_cache:
            self.label_tree.get_labels_in_topological_order()

    def resolve_labels(self, predictions: list[tuple[str, float]]) -> list[Label]:
        """Resolves hierarchical labels and exclusivity based on a list of ScoredLabels (labels with probability).

        The following two steps are taken:

        - selects the most likely label from an exclusive (multiclass) group
        - removes children of "not-most-likely" (non-max) parents in an exclusive group (top-down approach)

        Args:
            predictions: a list of tuples (label name, score)
        """
        label_to_prob = {}
        for lbl, score in predictions:
            label_to_prob[lbl] = score

        return self.__resolve_labels_probabilistic(label_to_prob)

    def __resolve_labels_probabilistic(
        self,
        label_to_probability: dict[str, float],
    ) -> list[Label]:
        """Resolves hierarchical labels and exclusivity based on a probabilistic label output.

        - selects the most likely (max) label from an exclusive group
        - removes children of non-max parents in an exclusive group

        See `resolve_labels_probabilistic` for parameter descriptions

        Args:
            label_to_probability : map from label to float.

        Returns:
            List of labels with probability
        """
        # add (potentially) missing ancestors labels for children with probability 0
        # this is needed so that suppression of children of non-max exclusive labels works when the exclusive
        # group has only one member
        label_to_probability = self._add_missing_ancestors(label_to_probability)

        hard_classification = self._resolve_exclusive_labels(label_to_probability)

        # suppress the output of children of parent nodes that are not the most likely label within their group
        resolved = self._suppress_descendant_output(hard_classification)

        result = []
        for lbl, probability in sorted(resolved.items()):
            if probability > 0:  # only return labels with non-zero probability
                result.append(
                    Label(
                        self.label_to_idx[lbl],
                        lbl,
                        # retain the original probability in the output
                        probability * label_to_probability.get(lbl, 1.0),
                    ),
                )
        return result

    def _suppress_descendant_output(
        self,
        hard_classification: dict[str, float],
    ) -> dict[str, float]:
        """Suppresses outputs in `label_to_probability`.

        Sets probability to 0.0 for descendants of parents that have 0 probability in `hard_classification`.
        """
        # Input: Conditional probability of each label given its parent label
        # Output: Marginal probability of each label

        # We recursively compute the marginal probability of each node by multiplying the conditional probability
        # with the marginal probability of its parent. That is:
        # P(B) = P(B|A) * P(A)
        # The recursion is done a topologically sorted list of labels to ensure that the marginal probability
        # of the parent label has been computed before trying to compute the child's probability.

        all_labels = self.label_tree.get_labels_in_topological_order()

        for child in all_labels:
            if child in hard_classification:
                # Get the immediate parents (should be at most one element; zero for root labels)
                parent = self.label_tree.get_parent(child)
                if parent is not None and parent in hard_classification:
                    hard_classification[child] *= hard_classification[parent]

        return hard_classification

    def _resolve_exclusive_labels(
        self,
        label_to_probability: dict[str, float],
    ) -> dict[str, float]:
        """Resolve exclusive labels.

        For labels in `label_to_probability` sets labels that are most likely (maximum probability) in their exclusive
        group to 1.0 and other (non-max) labels to probability 0.
        """
        # actual exclusive group selection should happen when extracting initial probs
        # (apply argmax to exclusive groups)
        hard_classification = {}
        for label, probability in label_to_probability.items():
            hard_classification[label] = float(probability > 0.0)
        return hard_classification

    def _add_missing_ancestors(
        self,
        label_to_probability: dict[str, float],
    ) -> dict[str, float]:
        """Adds missing ancestors to the `label_to_probability` map."""
        updated_label_to_probability = copy.deepcopy(label_to_probability)
        for label in label_to_probability:
            for ancestor in self.label_tree.get_ancestors(label):
                if ancestor not in updated_label_to_probability:
                    updated_label_to_probability[ancestor] = 0.0  # by default missing ancestors get probability 0.0
        return updated_label_to_probability


class SimpleLabelsGraph:
    """Class representing a tree. It implements basic operations
    like adding edges, getting children and parents.
    """

    def __init__(self, vertices: list[str]) -> None:
        self._v = vertices
        self._adj: dict[str, list] = {v: [] for v in vertices}
        self._topological_order_cache: list | None = None
        self._parents_map: dict[str, str] = {}

    def add_edge(self, parent: str, child: str) -> None:
        self._adj[parent].append(child)
        self._parents_map[child] = parent
        self.clear_topological_cache()

    def get_children(self, label: str) -> list:
        return self._adj[label]

    def get_parent(self, label: str) -> str | None:
        return self._parents_map.get(label, None)

    def get_ancestors(self, label: str) -> list[str]:
        """Returns all the ancestors of the input label, including self."""
        predecessors = [label]
        last_parent = self.get_parent(label)
        if last_parent is None:
            return predecessors

        while last_parent is not None:
            predecessors.append(last_parent)
            last_parent = self.get_parent(last_parent)

        return predecessors

    def get_labels_in_topological_order(self) -> list:
        if self._topological_order_cache is None:
            self._topological_order_cache = self.topological_sort()

        return self._topological_order_cache

    def topological_sort(self) -> list:
        in_degree: dict[str, int] = dict.fromkeys(self._v, 0)

        for node_adj in self._adj.values():
            for j in node_adj:
                in_degree[j] += 1

        nodes_deque = []
        for node in self._v:
            if in_degree[node] == 0:
                nodes_deque.append(node)

        ordered = []
        while nodes_deque:
            u = nodes_deque.pop(0)
            ordered.append(u)

            for node in self._adj[u]:
                in_degree[node] -= 1
                if in_degree[node] == 0:
                    nodes_deque.append(node)

        if len(ordered) != len(self._v):
            msg = "Topological sort failed: input graph has been changed during the sorting or contains a cycle"
            raise RuntimeError(msg)

        return ordered

    def clear_topological_cache(self) -> None:
        self._topological_order_cache = None


_saliency_map_name = "saliency_map"
_feature_vector_name = "feature_vector"
_raw_scores_name = "raw_scores"


def _get_non_xai_names(output_names: list[str]) -> list[str]:
    return [
        output_name
        for output_name in output_names
        if _saliency_map_name != output_name and _feature_vector_name != output_name
    ]


def _append_xai_names(outputs: dict, output_names: list[str]) -> None:
    if _saliency_map_name in outputs:
        output_names.append(_saliency_map_name)
    if _feature_vector_name in outputs:
        output_names.append(_feature_vector_name)
