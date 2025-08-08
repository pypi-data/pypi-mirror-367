# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GNU GPL v3
# This file is licensed under the terms of the GNU GPL v3.0.
# See the LICENSE file at the root of this
# repository for complete details.


import json
import random

try:
    from ..data_gp import DataGP
    from ..gradual_patterns import GI
    from .numeric_ss import NumericSS
except ImportError:
    from src.so4gp import DataGP, GI
    from src.so4gp.algorithms import NumericSS

class RandomGRAANK(DataGP):

    def __init__(self, *args, max_iter: int = 1, **kwargs):
        """Description

        Extract gradual patterns (GPs) from a numeric data source using the Random Search Algorithm (LS-GRAANK)
        approach (proposed in a published research paper by Dickson Owuor). A GP is a set of gradual items (GI), and its
        quality is measured by its computed support value. For example, given a data set with 3 columns (age, salary,
        cars) and 10 objects. A GP may take the form: {age+, salary-} with a support of 0.8. This implies that 8 out of
        10 objects have the values of column age 'increasing' and column 'salary' decreasing.

            In this approach, we assume that every GP candidate may be represented as a position that has a cost value
            associated with it. The cost is derived from the computed support of that candidate, the higher the support
             value, the lower the cost. The aim of the algorithm is to search through a group of positions and find those with
            the lowest cost as efficiently as possible.

        :param args: [required] a data source path of Pandas DataFrame, [optional] minimum-support, [optional] eq
        :param max_iter: [optional] maximum_iteration, default is 1

        >>> from so4gp.algorithms as RandomGRAANK
        >>> import pandas
        >>> import json
        >>> dummy_data = [[30, 3, 1, 10], [35, 2, 2, 8], [40, 4, 2, 7], [50, 1, 1, 6], [52, 7, 1, 2]]
        >>> dummy_df = pandas.DataFrame(dummy_data, columns=['Age', 'Salary', 'Cars', 'Expenses'])
        >>>
        >>> mine_obj = RandomGRAANK(dummy_df, 0.5, max_iter=3)
        >>> result_json = mine_obj.discover()
        >>> result = json.loads(result_json)
        >>> # print(result['Patterns'])
        >>> print(result_json) # doctest: +SKIP
        {"Algorithm": "RS-GRAANK", "Best Patterns": [[["Age+", "Salary+", "Expenses-"], 0.6]], "Invalid Count": 1,
            "Iterations": 3}
        """
        super(RandomGRAANK, self).__init__(*args, **kwargs)
        self._max_iteration: int = max_iter
        self._n_var: int = 1

    def discover(self):
        """Description

        Uses random search to find GP candidates. The candidates are validated if their computed support is greater
        than or equal to the minimum support threshold specified by the user.

        :return: JSON object
        """

        self.fit_bitmap()
        self.clear_gradual_patterns()
        if self.valid_bins is None:
            return []

        s_space = NumericSS.initialize_search_space(self.valid_bins, 1, self._max_iteration)
        if s_space is None:
            return []

        repeated, candidate = 0, NumericSS.Candidate()
        while s_space.counter < self._max_iteration:
            # while eval_count < max_evaluations:
            candidate.position = ((s_space.var_min + random.random()) * (s_space.var_max - s_space.var_min))

            # Evaluate candidate
            NumericSS.evaluate_candidate(candidate, s_space, self.valid_bins)

            # Evaluate GP
            _, repeated = NumericSS.evaluate_gradual_pattern(self._max_iteration, repeated, s_space, self)

        # Output
        out = json.dumps({"Algorithm": "RS-GRAANK", "Best Patterns": s_space.str_best_gps,
                          "Invalid Count": s_space.invalid_count, "Iterations": s_space.iter_count})
        """:type out: object"""
        for gp in s_space.best_patterns:
            self.add_gradual_pattern(gp)
        return out
