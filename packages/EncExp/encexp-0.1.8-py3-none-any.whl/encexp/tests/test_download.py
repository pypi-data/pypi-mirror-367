# Copyright 2024 Mario Graff (https://github.com/mgraffg)

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from dataclasses import dataclass
from os.path import isfile
import os
import numpy as np
from encexp.download import download_TextModel, download


def test_download_TextModel():
    """Test download TextModel"""
    from encexp import TextModel
    tm = TextModel(lang='es')
    download_TextModel(tm.identifier)


def test_download_path():
    """Test download path"""

    path = download('es_info', return_path=True)
    assert isfile(path)
    path = download('es_info', return_path=True)
    assert isfile(path)