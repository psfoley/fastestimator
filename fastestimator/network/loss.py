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
import tensorflow as tf
from fastestimator.util.op import TensorOp


class Loss(TensorOp):
    """
    A base class for loss operations. It can be used directly to perform value pass-through (see the adversarial 
    training showcase for an example of when this is useful)
    """


class SparseCategoricalCrossentropy(Loss):
    def __init__(self, y_true=None, y_pred=None, inputs=None, outputs=None, mode=None, **kwargs):
        """Calculate sparse categorical cross entropy, the rest of the keyword argument will be passed to 
           tf.losses.SparseCategoricalCrossentropy
        
        Args:
            y_true: ground truth label key
            y_pred: prediction label key
            inputs: A tuple or list like: [<y_true>, <y_pred>]
            outputs: Where to store the computed loss value (not required under normal use cases)
            mode: 'train', 'eval', 'test', or None
            kwargs: Arguments to be passed along to the tf.losses constructor
        """
        inputs = validate_loss_inputs(inputs, y_true, y_pred)
        super().__init__(inputs=inputs, outputs=outputs, mode=mode)
        self.loss_obj = tf.losses.SparseCategoricalCrossentropy(**kwargs)

    def forward(self, data, state):
        true, pred = data
        return self.loss_obj(true, pred)


class BinaryCrossentropy(Loss):
    def __init__(self, y_true=None, y_pred=None, inputs=None, outputs=None, mode=None, **kwargs):
        """Calculate binary cross entropy, the rest of the keyword argument will be passed to 
                  tf.losses.BinaryCrossentropy

       Args:
           y_true: ground truth label key
           y_pred: prediction label key
           inputs: A tuple or list like: [<y_true>, <y_pred>]
           outputs: Where to store the computed loss value (not required under normal use cases)
           mode: 'train', 'eval', 'test', or None
           kwargs: Arguments to be passed along to the tf.losses constructor
       """
        inputs = validate_loss_inputs(inputs, y_true, y_pred)
        super().__init__(inputs=inputs, outputs=outputs, mode=mode)
        self.loss_obj = tf.losses.BinaryCrossentropy(**kwargs)

    def forward(self, data, state):
        true, pred = data
        return self.loss_obj(true, pred)


class MixUpLoss(Loss):
    """
    This class should be used in conjunction with MixUpBatch to perform mix-up training, which helps to reduce
    over-fitting, stabilize GAN training, and harden against adversarial attacks (https://arxiv.org/abs/1710.09412)
    """
    def __init__(self, loss, lam=None, y_true=None, y_pred=None, inputs=None, outputs=None, mode=None):
        """
        Args:
            loss (func): A loss object (tf.losses) which can be invoked like "loss(true, pred)"
            lam: The key of the lambda value generated by MixUpBatch
            y_true: ground truth label key
            y_pred: prediction label key
            inputs: A tuple or list like: [<lam>, <y_true>, <y_pred>]
            outputs: Where to store the computed loss value (not required under normal use cases)
            mode: 'train', 'eval', 'test', or None
        """
        inputs = validate_loss_inputs(inputs, lam, y_true, y_pred)
        super().__init__(inputs=inputs, outputs=outputs, mode=mode)
        self.loss_obj = loss

    def forward(self, data, state):
        lam, true, pred = data
        loss1 = self.loss_obj(true, pred)
        loss2 = self.loss_obj(tf.roll(true, shift=1, axis=0), pred)
        return lam * loss1 + (1.0 - lam) * loss2


def validate_loss_inputs(inputs, *args):
    """
    A method to ensure that either the inputs array or individual input arguments are specified, but not both
    Args:
        inputs: None or a tuple/list of arguments
        *args: a tuple of arguments or Nones
    Returns:
        either 'inputs' or the args tuple depending on which is populated
    """
    if inputs is None:  # Using args
        assert all(map(lambda x: x is not None, args)), \
            "If the 'inputs' field is not provided then all individual input arguments must be specified"
        inputs = args
    else:  # Using Inputs
        assert all(map(lambda x: x is None, args)), \
            "If the 'inputs' field is provided then individual input arguments may not be specified"
        assert len(inputs) == len(args), \
            "{} inputs were provided, but {} were required".format(len(inputs), len(args))
    return inputs