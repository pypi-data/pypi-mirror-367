#
# Copyright (C) 2020-2025 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

from __future__ import annotations  # TODO: remove when Python3.9 support is dropped

import math
from functools import partial
from typing import TYPE_CHECKING, Any

import cv2
import numpy as np
from openvino import Input, Model, Node, Output, OVAny, Type, layout_helpers
from openvino import opset10 as opset
from openvino.utils.decorators import custom_preprocess_function

if TYPE_CHECKING:
    from collections.abc import Callable


class Layout:
    def __init__(self, layout: str = "") -> None:
        self.layout = layout

    @staticmethod
    def from_shape(shape: list[int] | tuple[int, ...]) -> str:
        """Create Layout from given shape"""
        if len(shape) == 2:
            return "NC"
        if len(shape) == 3:
            return "CHW" if shape[0] in range(1, 5) else "HWC"
        if len(shape) == 4:
            return "NCHW" if shape[1] in range(1, 5) else "NHWC"
        if len(shape) == 6:
            return "NSTHWC" if shape[5] in range(1, 5) else "NSCTHW"

        msg = f"Get layout from shape method doesn't support {len(shape)}D shape"
        raise RuntimeError(msg)

    @staticmethod
    def from_openvino(input: Input):
        """Create Layout from openvino input"""
        return layout_helpers.get_layout(input).to_string().strip("[]").replace(",", "")

    @staticmethod
    def from_user_layouts(input_names: set, user_layouts: dict):
        """Create Layout for input based on user info"""
        for input_name in input_names:
            if input_name in user_layouts:
                return user_layouts[input_name]
        return user_layouts.get("", "")

    @staticmethod
    def parse_layouts(layout_string: str) -> dict | None:
        """Parse layout parameter in format "input0:NCHW,input1:NC" or "NCHW" (applied to all inputs)"""
        if not layout_string:
            return None
        search_string = layout_string if layout_string.rfind(":") != -1 else ":" + layout_string
        colon_pos = search_string.rfind(":")
        user_layouts = {}
        while colon_pos != -1:
            start_pos = search_string.rfind(",")
            input_name = search_string[start_pos + 1 : colon_pos]
            input_layout = search_string[colon_pos + 1 :]
            user_layouts[input_name] = input_layout
            search_string = search_string[: start_pos + 1]
            if search_string == "" or search_string[-1] != ",":
                break
            search_string = search_string[:-1]
            colon_pos = search_string.rfind(":")
        if search_string != "":
            raise ValueError("Can't parse input layout string: " + layout_string)
        return user_layouts


def resize_image_letterbox_graph(input: Output, size: tuple[int, int], interpolation: str, pad_value: int) -> Node:
    if not isinstance(pad_value, int):
        msg = "pad_value must be int"
        raise RuntimeError(msg)
    if not 0 <= pad_value <= 255:
        msg = "pad_value must be in range [0, 255]"
        raise RuntimeError(msg)
    w, h = size
    h_axis = 1
    w_axis = 2
    image_shape = opset.shape_of(input, name="shape")
    iw = opset.convert(
        opset.gather(image_shape, opset.constant(w_axis), axis=0),
        destination_type="f32",
    )
    ih = opset.convert(
        opset.gather(image_shape, opset.constant(h_axis), axis=0),
        destination_type="f32",
    )
    w_ratio = opset.divide(opset.constant(w, dtype=Type.f32), iw)
    h_ratio = opset.divide(opset.constant(h, dtype=Type.f32), ih)
    scale = opset.minimum(w_ratio, h_ratio)
    nw = opset.convert(
        opset.round(opset.multiply(iw, scale), "half_to_even"),
        destination_type="i32",
    )
    nh = opset.convert(
        opset.round(opset.multiply(ih, scale), "half_to_even"),
        destination_type="i32",
    )
    new_size = opset.concat([opset.unsqueeze(nh, 0), opset.unsqueeze(nw, 0)], axis=0)
    image = opset.interpolate(
        input,
        new_size,
        scales=np.array([0.0, 0.0], dtype=np.float32),
        axes=[h_axis, w_axis],
        mode=interpolation,
        shape_calculation_mode="sizes",
    )
    dx = opset.divide(
        opset.subtract(opset.constant(w, dtype=np.int32), nw),
        opset.constant(2, dtype=np.int32),
    )
    dy = opset.divide(
        opset.subtract(opset.constant(h, dtype=np.int32), nh),
        opset.constant(2, dtype=np.int32),
    )
    dx_border = opset.subtract(
        opset.subtract(opset.constant(w, dtype=np.int32), nw),
        dx,
    )
    dy_border = opset.subtract(
        opset.subtract(opset.constant(h, dtype=np.int32), nh),
        dy,
    )
    pads_begin = opset.concat(
        [
            opset.constant([0], dtype=np.int32),
            opset.unsqueeze(dy, 0),
            opset.unsqueeze(dx, 0),
            opset.constant([0], dtype=np.int32),
        ],
        axis=0,
    )
    pads_end = opset.concat(
        [
            opset.constant([0], dtype=np.int32),
            opset.unsqueeze(dy_border, 0),
            opset.unsqueeze(dx_border, 0),
            opset.constant([0], dtype=np.int32),
        ],
        axis=0,
    )
    return opset.pad(
        image,
        pads_begin,
        pads_end,
        "constant",
        opset.constant(pad_value, dtype=np.uint8),
    )


def crop_resize_graph(input: Output, size: tuple[int, int]) -> Node:
    h_axis = 1
    w_axis = 2
    desired_aspect_ratio = size[1] / size[0]  # width / height

    image_shape = opset.shape_of(input, name="shape")
    iw = opset.convert(
        opset.gather(image_shape, opset.constant(w_axis), axis=0),
        destination_type="i32",
    )
    ih = opset.convert(
        opset.gather(image_shape, opset.constant(h_axis), axis=0),
        destination_type="i32",
    )

    if desired_aspect_ratio == 1:
        # then_body
        image_t = opset.parameter([-1, -1, -1, 3], np.uint8, "image")
        iw_t = opset.parameter([], np.int32, "iw")
        ih_t = opset.parameter([], np.int32, "ih")
        then_offset = opset.unsqueeze(
            opset.divide(opset.subtract(ih_t, iw_t), opset.constant(2, dtype=np.int32)),
            0,
        )
        then_stop = opset.add(then_offset, iw_t)
        then_cropped_frame = opset.slice(
            image_t,
            start=then_offset,
            stop=then_stop,
            step=[1],
            axes=[h_axis],
        )
        then_body_res_1 = opset.result(then_cropped_frame)
        then_body = Model(
            [then_body_res_1],
            [image_t, iw_t, ih_t],
            "then_body_function",
        )

        # else_body
        image_e = opset.parameter([-1, -1, -1, 3], np.uint8, "image")
        iw_e = opset.parameter([], np.int32, "iw")
        ih_e = opset.parameter([], np.int32, "ih")
        else_offset = opset.unsqueeze(
            opset.divide(opset.subtract(iw_e, ih_e), opset.constant(2, dtype=np.int32)),
            0,
        )
        else_stop = opset.add(else_offset, ih_e)
        else_cropped_frame = opset.slice(
            image_e,
            start=else_offset,
            stop=else_stop,
            step=[1],
            axes=[w_axis],
        )
        else_body_res_1 = opset.result(else_cropped_frame)
        else_body = Model(
            [else_body_res_1],
            [image_e, iw_e, ih_e],
            "else_body_function",
        )

        # if
        condition = opset.greater(ih, iw)
        if_node = opset.if_op(condition.output(0))
        if_node.set_then_body(then_body)
        if_node.set_else_body(else_body)
        if_node.set_input(input, image_t, image_e)
        if_node.set_input(iw.output(0), iw_t, iw_e)
        if_node.set_input(ih.output(0), ih_t, ih_e)
        cropped_frame = if_node.set_output(then_body_res_1, else_body_res_1)

    elif desired_aspect_ratio < 1:
        new_width = opset.floor(
            opset.multiply(
                opset.convert(ih, destination_type="f32"),
                desired_aspect_ratio,
            ),
        )
        offset = opset.unsqueeze(
            opset.divide(
                opset.subtract(iw, new_width),
                opset.constant(2, dtype=np.int32),
            ),
            0,
        )
        stop = opset.add(offset, new_width)
        cropped_frame = opset.slice(
            input,
            start=offset,
            stop=stop,
            step=[1],
            axes=[w_axis],
        )
    elif desired_aspect_ratio > 1:
        new_hight = opset.floor(
            opset.multiply(
                opset.convert(iw, destination_type="f32"),
                desired_aspect_ratio,
            ),
        )
        offset = opset.unsqueeze(
            opset.divide(
                opset.subtract(ih, new_hight),
                opset.constant(2, dtype=np.int32),
            ),
            0,
        )
        stop = opset.add(offset, new_hight)
        cropped_frame = opset.slice(
            input,
            start=offset,
            stop=stop,
            step=[1],
            axes=[h_axis],
        )

    target_size = list(size)
    target_size.reverse()
    return opset.interpolate(
        cropped_frame,
        target_size,
        scales=np.array([0.0, 0.0], dtype=np.float32),
        axes=[h_axis, w_axis],
        mode="linear",
        shape_calculation_mode="sizes",
    )


def resize_image_graph(
    input: Output,
    size: tuple[int, int],
    keep_aspect_ratio: bool,
    interpolation: str,
    pad_value: int,
) -> Node:
    if not isinstance(pad_value, int):
        msg = "pad_value must be int"
        raise RuntimeError(msg)
    if not 0 <= pad_value <= 255:
        msg = "pad_value must be in range [0, 255]"
        raise RuntimeError(msg)
    h_axis = 1
    w_axis = 2
    w, h = size

    target_size = list(size)
    target_size.reverse()

    if not keep_aspect_ratio:
        return opset.interpolate(
            input,
            target_size,
            scales=np.array([0.0, 0.0], dtype=np.float32),
            axes=[h_axis, w_axis],
            mode=interpolation,
            shape_calculation_mode="sizes",
        )
    image_shape = opset.shape_of(input, name="shape")
    iw = opset.convert(
        opset.gather(image_shape, opset.constant(w_axis), axis=0),
        destination_type="f32",
    )
    ih = opset.convert(
        opset.gather(image_shape, opset.constant(h_axis), axis=0),
        destination_type="f32",
    )
    w_ratio = opset.divide(np.float32(w), iw)
    h_ratio = opset.divide(np.float32(h), ih)
    scale = opset.minimum(w_ratio, h_ratio)
    nw = opset.convert(
        opset.round(opset.multiply(iw, scale), "half_to_even"),
        destination_type="i32",
    )
    nh = opset.convert(
        opset.round(opset.multiply(ih, scale), "half_to_even"),
        destination_type="i32",
    )
    new_size = opset.concat([opset.unsqueeze(nh, 0), opset.unsqueeze(nw, 0)], axis=0)
    image = opset.interpolate(
        input,
        new_size,
        scales=np.array([0.0, 0.0], dtype=np.float32),
        axes=[h_axis, w_axis],
        mode=interpolation,
        shape_calculation_mode="sizes",
    )
    dx_border = opset.subtract(opset.constant(w, dtype=np.int32), nw)
    dy_border = opset.subtract(opset.constant(h, dtype=np.int32), nh)
    pads_begin = np.array([0, 0, 0, 0], np.int32)
    pads_end = opset.concat(
        [
            opset.constant([0], dtype=np.int32),
            opset.unsqueeze(dy_border, 0),
            opset.unsqueeze(dx_border, 0),
            opset.constant([0], dtype=np.int32),
        ],
        axis=0,
    )
    return opset.pad(
        image,
        pads_begin,
        pads_end,
        "constant",
        opset.constant(pad_value, dtype=np.uint8),
    )


def resize_image(size: tuple[int, int], interpolation: str, pad_value: int) -> Callable:
    return custom_preprocess_function(
        partial(
            resize_image_graph,
            size=size,
            keep_aspect_ratio=False,
            interpolation=interpolation,
            pad_value=pad_value,
        ),
    )


def resize_image_with_aspect(size: tuple[int, int], interpolation: str, pad_value: int) -> Callable:
    return custom_preprocess_function(
        partial(
            resize_image_graph,
            size=size,
            keep_aspect_ratio=True,
            interpolation=interpolation,
            pad_value=pad_value,
        ),
    )


def crop_resize(size: tuple[int, int], interpolation: str, pad_value: int) -> Callable:
    return custom_preprocess_function(partial(crop_resize_graph, size=size))


def resize_image_letterbox(size: tuple[int, int], interpolation: str, pad_value: int) -> Callable:
    return custom_preprocess_function(
        partial(
            resize_image_letterbox_graph,
            size=size,
            interpolation=interpolation,
            pad_value=pad_value,
        ),
    )


def load_parameters_from_onnx(onnx_model: Any) -> dict[str, Any]:
    parameters: dict[str, Any] = {}

    def insert_hierarchical(keys, val, root_dict):
        if len(keys) == 1:
            root_dict[keys[0]] = val
            return
        if keys[0] not in root_dict:
            root_dict[keys[0]] = {}
        insert_hierarchical(keys[1:], val, root_dict[keys[0]])

    for prop in onnx_model.metadata_props:
        keys = prop.key.split()
        if "model_info" in keys:
            insert_hierarchical(keys, prop.value, parameters)

    return parameters


def get_rt_info_from_dict(rt_info_dict: dict[str, Any], path: list[str]) -> OVAny:
    value = rt_info_dict
    try:
        value = rt_info_dict
        for item in path:
            value = value[item]
        return OVAny(value)
    except KeyError:
        msg = "Cannot get runtime attribute. Path to runtime attribute is incorrect."
        raise RuntimeError(msg)


def resize_image_ocv(
    image: np.ndarray,
    size: tuple[int, int],
    keep_aspect_ratio: bool = False,
    is_pad: bool = False,
    pad_value: int = 0,
    interpolation: int = cv2.INTER_LINEAR,
) -> np.ndarray:
    if keep_aspect_ratio:
        h, w = image.shape[:2]
        scale = min(size[1] / h, size[0] / w)
        image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=interpolation)
        if is_pad:
            nh, nw = image.shape[:2]
            ph, pw = max(0, size[1] - nh), max(0, size[0] - nw)
            image = np.pad(
                image,
                ((0, ph), (0, pw), (0, 0)),
                mode="constant",
                constant_values=pad_value,
            )
        return image
    return cv2.resize(image, size, interpolation=interpolation)


def resize_image_with_aspect_ocv(
    image: np.ndarray,
    size: tuple[int, int],
    interpolation: int = cv2.INTER_LINEAR,
) -> np.ndarray:
    return resize_image_ocv(
        image,
        size,
        keep_aspect_ratio=True,
        is_pad=True,
        pad_value=0,
        interpolation=interpolation,
    )


def resize_image_letterbox_ocv(
    image: np.ndarray,
    size: tuple[int, int],
    interpolation: int = cv2.INTER_LINEAR,
    pad_value: int = 0,
) -> np.ndarray:
    ih, iw = image.shape[0:2]
    w, h = size
    scale = min(w / iw, h / ih)
    nw = round(iw * scale)
    nh = round(ih * scale)
    image = cv2.resize(image, (nw, nh), interpolation=interpolation)
    dx = (w - nw) // 2
    dy = (h - nh) // 2
    return np.pad(
        image,
        ((dy, h - nh - dy), (dx, w - nw - dx), (0, 0)),
        mode="constant",
        constant_values=pad_value,
    )


def crop_resize_ocv(image: np.ndarray, size: tuple[int, int]) -> np.ndarray:
    desired_aspect_ratio = size[1] / size[0]  # width / height
    if desired_aspect_ratio == 1:
        if image.shape[0] > image.shape[1]:
            offset = (image.shape[0] - image.shape[1]) // 2
            cropped_frame = image[offset : image.shape[1] + offset]
        else:
            offset = (image.shape[1] - image.shape[0]) // 2
            cropped_frame = image[:, offset : image.shape[0] + offset]
    elif desired_aspect_ratio < 1:
        new_width = math.floor(image.shape[0] * desired_aspect_ratio)
        offset = (image.shape[1] - new_width) // 2
        cropped_frame = image[:, offset : new_width + offset]
    elif desired_aspect_ratio > 1:
        new_height = math.floor(image.shape[1] / desired_aspect_ratio)
        offset = (image.shape[0] - new_height) // 2
        cropped_frame = image[offset : new_height + offset]

    return cv2.resize(cropped_frame, size)


RESIZE_TYPES: dict[str, Callable] = {
    "crop": crop_resize_ocv,
    "standard": resize_image_ocv,
    "fit_to_window": resize_image_with_aspect_ocv,
    "fit_to_window_letterbox": resize_image_letterbox_ocv,
}


INTERPOLATION_TYPES: dict[str, int] = {
    "LINEAR": cv2.INTER_LINEAR,
    "CUBIC": cv2.INTER_CUBIC,
    "NEAREST": cv2.INTER_NEAREST,
    "AREA": cv2.INTER_AREA,
}


class InputTransform:
    def __init__(
        self,
        reverse_input_channels: bool = False,
        mean_values: list[float] | None = None,
        scale_values: list[float] | None = None,
    ):
        self.reverse_input_channels = reverse_input_channels
        self.is_trivial = not (reverse_input_channels or mean_values or scale_values)
        self.means = np.array(mean_values, dtype=np.float32) if mean_values else np.array([0.0, 0.0, 0.0])
        self.std_scales = np.array(scale_values, dtype=np.float32) if scale_values else np.array([1.0, 1.0, 1.0])

    def __call__(self, inputs):
        if self.is_trivial:
            return inputs
        if self.reverse_input_channels:
            inputs = cv2.cvtColor(inputs, cv2.COLOR_BGR2RGB)
        return (inputs - self.means) / self.std_scales
