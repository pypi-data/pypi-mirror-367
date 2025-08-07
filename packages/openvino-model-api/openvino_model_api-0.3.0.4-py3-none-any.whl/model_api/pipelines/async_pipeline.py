#
# Copyright (C) 2020-2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

from time import perf_counter

from model_api.performance_metrics import PerformanceMetrics


class AsyncPipeline:
    def __init__(self, model):
        self.model = model
        self.model.load()

        self.completed_results = {}
        self.callback_exceptions = []
        self.model.inference_adapter.set_callback(self.callback)

        self.preprocess_metrics = PerformanceMetrics()
        self.inference_metrics = PerformanceMetrics()
        self.postprocess_metrics = PerformanceMetrics()

    def callback(self, request, callback_args):
        try:
            id, meta, preprocessing_meta, start_time = callback_args
            self.completed_results[id] = (
                self.model.inference_adapter.copy_raw_result(request),
                meta,
                preprocessing_meta,
                start_time,
            )
        except Exception as e:  # noqa: BLE001 TODO: Figure out the exact exception that might be raised
            self.callback_exceptions.append(e)

    def submit_data(self, inputs, id, meta={}):
        preprocessing_start_time = perf_counter()
        inputs, preprocessing_meta = self.model.preprocess(inputs)
        self.preprocess_metrics.update(preprocessing_start_time)

        infer_start_time = perf_counter()
        callback_data = id, meta, preprocessing_meta, infer_start_time
        self.model.infer_async_raw(inputs, callback_data)

    def get_raw_result(self, id):
        if id in self.completed_results:
            return self.completed_results.pop(id)
        return None

    def get_result(self, id):
        result = self.get_raw_result(id)
        if result:
            raw_result, meta, preprocess_meta, infer_start_time = result
            self.inference_metrics.update(infer_start_time)

            postprocessing_start_time = perf_counter()
            result = (
                self.model.postprocess(raw_result, preprocess_meta),
                {
                    **meta,
                    **preprocess_meta,
                },
            )
            self.postprocess_metrics.update(postprocessing_start_time)
            return result
        return None

    def is_ready(self):
        return self.model.is_ready()

    def await_all(self):
        if self.callback_exceptions:
            raise self.callback_exceptions[0]
        self.model.await_all()

    def await_any(self):
        if self.callback_exceptions:
            raise self.callback_exceptions[0]
        self.model.await_any()
