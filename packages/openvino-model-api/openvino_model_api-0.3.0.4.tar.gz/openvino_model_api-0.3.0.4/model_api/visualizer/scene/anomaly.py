"""Anomaly Scene."""

# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

from itertools import starmap
from typing import Union

import cv2
from PIL import Image

from model_api.models.result import AnomalyResult
from model_api.visualizer.layout import Flatten, Layout
from model_api.visualizer.primitive import BoundingBox, Label, Overlay, Polygon

from .scene import Scene


class AnomalyScene(Scene):
    """Anomaly Scene."""

    def __init__(self, image: Image, result: AnomalyResult, layout: Union[Layout, None] = None) -> None:
        super().__init__(
            base=image,
            overlay=self._get_overlays(result),
            bounding_box=self._get_bounding_boxes(result),
            label=self._get_labels(result),
            polygon=self._get_polygons(result),
            layout=layout,
        )

    def _get_overlays(self, result: AnomalyResult) -> list[Overlay]:
        if result.anomaly_map is not None:
            anomaly_map = cv2.cvtColor(result.anomaly_map, cv2.COLOR_BGR2RGB)
            return [Overlay(anomaly_map)]
        return []

    def _get_bounding_boxes(self, result: AnomalyResult) -> list[BoundingBox]:
        if result.pred_boxes is not None:
            return list(starmap(BoundingBox, result.pred_boxes))
        return []

    def _get_labels(self, result: AnomalyResult) -> list[Label]:
        labels = []
        if result.pred_label is not None and result.pred_score is not None:
            labels.append(Label(label=result.pred_label, score=result.pred_score))
        return labels

    def _get_polygons(self, result: AnomalyResult) -> list[Polygon]:
        if result.pred_mask is not None:
            return [Polygon(result.pred_mask)]
        return []

    @property
    def default_layout(self) -> Layout:
        return Flatten(Overlay, BoundingBox, Label, Polygon)
