# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GNU GPL v3
# This file is licensed under the terms of the GNU GPL v3.0.
# See the LICENSE file at the root of this
# repository for complete details.

"""
@author: Dickson Owuor
@credits: Thomas Runkler, Edmond Menya, and Anne Laurent
@license: GNU GPL v3
@email: owuordickson@gmail.com
@created: 21 July 2021
@modified: 27 October 2022

A collection of classes for pre-processing data for mining gradual patterns.
"""

import gc
import csv
import time
import numpy as np
import pandas as pd
from dateutil.parser import parse

try:
    from .gradual_patterns import GP, TGP, PairwiseMatrix
except ImportError:
    from src.so4gp import GP, TGP, PairwiseMatrix

class DataGP:

    def __init__(self, data_source, min_sup=0.5, eq=False) -> None:
        """Description of class DataGP


        A class for creating data-gp objects. A data-gp object is meant to store all the parameters required by GP
        algorithms to extract gradual patterns (GP). It takes a numeric file (in CSV format) as input and converts it
        into an object whose attributes are used by algorithms to extract GPs.

        :param data_source: [required] a data source, it can either be a 'file in csv format' or a 'Pandas DataFrame'
        :type data_source: pd.DataFrame | str

        :param min_sup: [optional] minimum support threshold, the default is 0.5
        :type min_sup: float

        :param eq: [optional] encode equal values as gradual, the default is False
        :type eq: bool

        """
        self._thd_supp: float = min_sup
        self._include_equal_values: bool = eq
        self._titles, self._data = DataGP.read(data_source)
        """:type _titles: list"""
        """:type _data: np.ndarray"""
        self._row_count: int = 0
        self._col_count: int = 0
        self._time_cols: np.ndarray = np.array([])
        self._attr_cols: np.ndarray = np.array([])
        self._valid_bins: dict | None = None
        self._valid_tids: dict | None = None
        self._attr_size: int = 0
        self._gradual_patterns = None
        """:type _gradual_patterns: list[GP] | None"""
        self._init_attributes()

    @property
    def thd_supp(self) -> float:
        return self._thd_supp

    @property
    def titles(self) -> list:
        return self._titles

    @property
    def data(self) -> np.ndarray:
        return self._data

    @property
    def row_count(self) -> int:
        return self._row_count

    @property
    def col_count(self) -> int:
        return self._col_count

    @property
    def time_cols(self) -> np.ndarray:
        return self._time_cols

    @property
    def attr_cols(self) -> np.ndarray:
        return self._attr_cols

    @property
    def valid_bins(self) -> dict | None:
        return self._valid_bins

    @property
    def valid_tids(self) -> dict | None:
        return self._valid_tids

    @property
    def attr_size(self) -> int:
        return self._attr_size

    @property
    def gradual_patterns(self) -> list | None:
        return self._gradual_patterns

    @property
    def str_gradual_patterns(self) -> list:
        str_gps = []
        for gp in self._gradual_patterns:
            str_gps.append(gp.print(self.titles))
        return str_gps

    def _init_attributes(self) -> None:
        """Initializes the attributes of the data-gp object."""

        def get_attr_cols() -> np.ndarray:
            """Description

            Returns indices of all columns with non-datetime objects

            :return: ndarray
            """
            all_cols = np.arange(self._col_count)
            attr_cols = np.setdiff1d(all_cols, self._time_cols)
            return attr_cols

        def get_time_cols() -> np.ndarray:
            """
            Tests each column's objects for date-time values. Returns indices of all columns with date-time objects

            :return: A ndarray object containing the indices of the time columns.
            """
            # Retrieve the first column only
            time_cols = list()
            n = self._col_count
            for i in range(n):  # check every column/attribute for time format
                row_data = str(self._data[0][i])
                try:
                    time_ok, t_stamp = DataGP.test_time(row_data)
                    if time_ok:
                        time_cols.append(i)
                except ValueError:
                    continue
            return np.array(time_cols)

        self._row_count, self._col_count = self._data.shape
        self._time_cols = get_time_cols()
        self._attr_cols = get_attr_cols()

    def add_gradual_pattern(self, pattern) -> None:
        if not isinstance(pattern, (GP, TGP)):
            raise Exception("Pattern must be of type GP, ExtGP, or TGP")
        self._gradual_patterns.append(pattern)

    def clear_gradual_patterns(self) -> None:
        self._gradual_patterns = list()

    def remove_subsets(self, gi_arr:set) -> None:
        """

        Remove subset GPs from the list.

        :param gi_arr: Gradual items in an array
        :return: List of GPs
        """
        for gp in self._gradual_patterns:
            result1 = set(gp.as_set).issubset(gi_arr)
            result2 = set(gp.as_swapped_set).issubset(gi_arr)
            if result1 or result2:
                self._gradual_patterns.remove(gp)

    def fit_bitmap(self, attr_data=None) -> None:
        """

        Generates bitmaps for columns with numeric objects. It stores the bitmaps in attribute valid_bins (those bitmaps
        whose computed support values are greater or equal to the minimum support threshold value).

        :param attr_data: Stepped attribute objects
        :type attr_data: np.ndarray
        :return: void
        """
        # (check) implement parallel multiprocessing
        # 1. Transpose csv array data
        if attr_data is None:
            attr_data = self._data.T
            self._attr_size = self._row_count
        else:
            self._attr_size = len(attr_data[self._attr_cols[0]])

        # 2. Construct and store 1-item_set valid bins
        # execute binary rank to calculate support of a pattern
        n = self._attr_size
        self._valid_bins = {}
        for col in self._attr_cols:
            # 2a. Generate a 1-itemset gradual items
            col_data = np.array(attr_data[col], dtype=float)
            with np.errstate(invalid='ignore'):
                if not self._include_equal_values:
                    temp_pos = np.array(col_data > col_data[:, np.newaxis])
                else:
                    temp_pos = np.array(col_data >= col_data[:, np.newaxis])
                    np.fill_diagonal(temp_pos, False)

                # 2b. Check support of each generated itemset
                supp = float(np.sum(temp_pos)) / float(n * (n - 1.0) / 2.0)
                if supp >= self._thd_supp:
                    self._valid_bins[f"{col}+"] = PairwiseMatrix(bin_mat=temp_pos, support=supp)
                    self._valid_bins[f"{col}-"] = PairwiseMatrix(bin_mat=temp_pos.T, support=supp)
        # print(self._valid_bins)
        if len(self._valid_bins) < 3:
            self._valid_bins = None
        gc.collect()

    def fit_tids(self) -> None:
        """

        Generates transaction ids (tids) for each column/feature with numeric objects. It stores the tids in attribute
        valid_tids (those tids whose computed support values are greater or equal to the minimum support threshold
        value).

        """
        self.fit_bitmap()
        if self._valid_bins is None:
            return

        n = self._row_count
        self._valid_tids = {}
        for gi_str, gi_data in self._valid_bins.items():
            arr_ij = np.transpose(np.nonzero(gi_data.bin_mat))
            set_ij = {tuple(ij) for ij in arr_ij if ij[0] < ij[1]}
            tids_len = len(set_ij)
            supp = float((tids_len*0.5) * (tids_len - 1)) / float(n * (n - 1.0) / 2.0)
            if supp >= self._thd_supp:
                self._valid_tids[gi_str] = set_ij

    @staticmethod
    def read(data_src) -> tuple[list, np.ndarray]:
        """

        Reads all the contents of a file (in CSV format) or a data-frame. Checks if its columns have numeric values. It
        separates its columns headers (titles) from the objects.

        :param data_src: A data source, it can either be a 'file in csv format' or a 'Pandas DataFrame'
        :type data_src: pd.DataFrame | str

        :return: The title, column objects
        """
        # 1. Retrieve data set from source
        if isinstance(data_src, pd.DataFrame):
            # a. DataFrame source
            # Check column names
            try:
                # Check data type
                _ = data_src.columns.astype(float)

                # Add column values
                data_src.loc[-1] = data_src.columns.to_numpy(dtype=float)  # adding a row
                data_src.index = data_src.index + 1  # shifting index
                data_src.sort_index(inplace=True)

                # Rename column names
                header_vals = ['col_' + str(k) for k in np.arange(data_src.shape[1])]
                data_src.columns = header_vals
            except ValueError:
                pass
            except TypeError:
                pass
            # print("Data fetched from DataFrame")
            return DataGP.clean_data(data_src)
        else:
            # b. CSV file
            file = str(data_src)
            try:
                with open(file, 'r') as f:
                    dialect = csv.Sniffer().sniff(f.readline(), delimiters=";,' '\t")
                    f.seek(0)
                    reader = csv.reader(f, dialect)
                    raw_data = list(reader)
                    f.close()

                if len(raw_data) <= 1:
                    raise Exception("CSV file read error. File has little or no data")
                else:
                    # print("Data fetched from CSV file")
                    # 2. Get table headers
                    keys = np.arange(len(raw_data[0]))
                    if raw_data[0][0].replace('.', '', 1).isdigit() or raw_data[0][0].isdigit():
                        header_vals = ['col_' + str(k) for k in keys]
                    else:
                        if raw_data[0][1].replace('.', '', 1).isdigit() or raw_data[0][1].isdigit():
                            header_vals = ['col_' + str(k) for k in keys]
                        else:
                            header_vals = raw_data[0]
                            del raw_data[0]
                    d_frame = pd.DataFrame(raw_data, columns=header_vals)
                    return DataGP.clean_data(d_frame)
            except Exception as error:
                raise Exception("Error: " + str(error))

    @staticmethod
    def test_time(date_str) -> None | tuple[bool, float] | tuple[bool, bool]:
        """

        Tests if a str represents a date-time variable.

        :param date_str: A string
        :type date_str: str
        :return: bool (True if it is a date-time variable, False otherwise)
        """
        # add all the possible formats
        try:
            if type(int(date_str)):
                return False, False
        except ValueError:
            try:
                if type(float(date_str)):
                    return False, False
            except ValueError:
                try:
                    date_time = parse(date_str)
                    t_stamp = time.mktime(date_time.timetuple())
                    return True, t_stamp
                except ValueError:
                    raise ValueError('no valid date-time format found')

    @staticmethod
    def clean_data(df) -> tuple[list, np.ndarray]:
        """Description

        Cleans a data-frame (i.e., missing values, outliers) before extraction of GPs
        :param df: data-frame
        :type df: pd.DataFrame
        :return: list (column titles), numpy (cleaned data)
        """
        # 1. Remove objects with Null values
        df = df.dropna()

        # 2. Remove columns with Strings
        cols_to_remove = []
        for col in df.columns:
            try:
                _ = df[col].astype(float)
            except ValueError:
                # Keep time columns
                try:
                    ok, stamp = DataGP.test_time(str(df[col][0]))
                    if not ok:
                        cols_to_remove.append(col)
                except ValueError:
                    cols_to_remove.append(col)
                pass
            except TypeError:
                cols_to_remove.append(col)
                pass
        # keep only the columns in df that do not contain string
        df = df[[col for col in df.columns if col not in cols_to_remove]]

        # 3. Return titles and data
        if df.empty:
            raise Exception("Data set is empty after cleaning.")
        return list(df.columns), df.values
