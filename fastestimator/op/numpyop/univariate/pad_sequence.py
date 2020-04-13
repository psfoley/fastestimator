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
from typing import Any, Callable, Dict, Iterable, List, Union

import numpy as np

from fastestimator.op.numpyop.numpyop import NumpyOp


class PadSequence(NumpyOp):
    """Pad sequences to the same length with provided value

    Args:
        max_len: Maximum length of all sequences
        value: Padding value. Defaults to 0.
        padding: Pad before or after the sequences. Defaults to "post".
        inputs: Key(s) of sequences to be padded. Defaults to None.
        outputs: Key(s) of sequences that are padded. Defaults to None.
        mode: What execution mode (train, eval, None) to apply this operation. Defaults to None.
    """
    def __init__(self,
                 max_len: int,
                 value: Union[str, int] = 0,
                 padding: str = "post",
                 inputs: Union[None, str, Iterable[str], Callable] = None,
                 outputs: Union[None, str, Iterable[str]] = None,
                 mode: Union[None, str, Iterable[str]] = None
                 ):
        super().__init__(inputs=inputs, outputs=outputs, mode=mode)
        self.in_list, self.out_list = True, True
        self.max_len = max_len
        self.value = value
        self.padding = padding

    def forward(self, data: List[np.ndarray], state: Dict[str, Any]) -> List[np.ndarray]:
        return [self._pad_sequence(elem) for elem in data]

    def _pad_sequence(self, data: np.ndarray) -> np.ndarray:
        """Pad the input sequence to the maximum length. Sequences longer than maximum length are truncated

        Args:
            data: input sequence in the data

        Returns:
            Padded sequence
        """
        if len(data) < self.max_len:
            pad_len = self.max_len - len(data)
            pad_arr = np.full(pad_len, self.value)
            if self.padding == 'post':
                data = np.append(data, pad_arr)
            else:
                data = np.append(pad_arr, data)
        else:
            data = data[:self.max_len]
        return data
