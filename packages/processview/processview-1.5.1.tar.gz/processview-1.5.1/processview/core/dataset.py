# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2017 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "29/01/2021"


from typing import Optional
from datetime import datetime


class DatasetIdentifier:
    def __init__(self, data_builder, metadata: Optional[dict] = None):
        """
        function that can be called to build data

        :param data_builder: call back to create the Dataset from its identifier
        :param Optional[dict] metadata: some metadata that could be provided in order to sort identifier between them. For now possible keys are:
            * `name`: name to be used to sort dataset
            * `creation_time`: creation of the dataset
            * `modification_time`: modification of the dataset
        """
        self._dataset_builder = data_builder
        metadata = metadata or {}
        self.__creation_time = metadata.get("creation_time", None)
        self.__modification_time = metadata.get("modification_time", None)
        self.__name = metadata.get("name", None)

    def recreate_dataset(self):
        """Recreate the dataset from the identifier"""
        return self._dataset_builder(self)

    def long_description(self) -> str:
        """long description of the identifier"""
        return ""

    def short_description(self) -> Optional[str]:
        return None

    def creation_time(self) -> Optional[datetime]:
        return self.__creation_time

    def modification_time(self) -> Optional[datetime]:
        return self.__modification_time

    def name(self) -> Optional[str]:
        return self.__name


class Dataset:
    """Base class that class processes should inherit"""

    @staticmethod
    def from_identifier(identifier):
        """Return the Dataset from a identifier"""
        raise NotImplementedError("Base class")

    def get_identifier(self) -> DatasetIdentifier:
        """dataset unique identifier. Can be for example a hdf5 and
        en entry from which the dataset can be rebuild"""
        raise NotImplementedError("Base class")
