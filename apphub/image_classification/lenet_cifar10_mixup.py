# Copyright 2019 The FastEstimator Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
import tempfile

import tensorflow as tf
from tensorflow.python.keras.losses import SparseCategoricalCrossentropy as KerasCrossentropy

import fastestimator as fe
from fastestimator.architecture import LeNet
from fastestimator.estimator.trace import Accuracy, ConfusionMatrix, ModelSaver
from fastestimator.network.loss import MixUpLoss, SparseCategoricalCrossentropy
from fastestimator.network.model import FEModel, ModelOp
from fastestimator.pipeline.augmentation import MixUpBatch
from fastestimator.pipeline.processing import Minmax
from fastestimator.util.schedule import Scheduler


def get_estimator(epochs=2, batch_size=32, alpha=1.0, warmup=0):
    (x_train, y_train), (x_eval, y_eval) = tf.keras.datasets.cifar10.load_data()
    data = {"train": {"x": x_train, "y": y_train}, "eval": {"x": x_eval, "y": y_eval}}
    num_classes = 10
    pipeline = fe.Pipeline(batch_size=batch_size, data=data, ops=Minmax(inputs="x", outputs="x"))

    model = FEModel(model_def=lambda: LeNet(input_shape=x_train.shape[1:], classes=num_classes),
                    model_name="LeNet",
                    optimizer="adam")

    mixup_map = {warmup: MixUpBatch(inputs="x", outputs=["x", "lambda"], alpha=alpha, mode="train")}
    mixup_loss = {
        0: SparseCategoricalCrossentropy(y_true="y", y_pred="y_pred", mode="train"),
        warmup: MixUpLoss(KerasCrossentropy(), lam="lambda", y_true="y", y_pred="y_pred", mode="train")
    }
    network = fe.Network(ops=[
        Scheduler(mixup_map),
        ModelOp(inputs="x", model=model, outputs="y_pred"),
        Scheduler(mixup_loss),
        SparseCategoricalCrossentropy(y_true="y", y_pred="y_pred", mode="eval")
    ])

    traces = [
        Accuracy(true_key="y", pred_key="y_pred"),
        ConfusionMatrix(true_key="y", pred_key="y_pred", num_classes=num_classes),
        ModelSaver(model_name="LeNet", save_dir=tempfile.mkdtemp(), save_best=True)
    ]

    estimator = fe.Estimator(network=network, pipeline=pipeline, epochs=epochs, traces=traces)
    return estimator


if __name__ == "__main__":
    est = get_estimator()
    est.fit()
