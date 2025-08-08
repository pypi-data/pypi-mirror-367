# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GNU GPL v3
# This file is licensed under the terms of the GNU GPL v3.0.
# See the LICENSE file at the root of this
# repository for complete details.


import json
import numpy as np

try:
    from ..data_gp import DataGP
    from ..gradual_patterns import GI, GP
    from .numeric_ss import NumericSS
except ImportError:
    from src.so4gp import DataGP, GI, GP
    from src.so4gp.algorithms import NumericSS

class GeneticGRAANK(DataGP):

    def __init__(self, *args, max_iter=1, n_pop=5, pc=0.5, gamma=1.0, mu=0.9, sigma=0.9, **kwargs):
        """Description

        Extract gradual patterns (GPs) from a numeric data source using the Genetic Algorithm approach (proposed
        in a published paper by Dickson Owuor). A GP is a set of gradual items (GI), and its quality is measured by
        its computed support value. For example, given a data set with 3 columns (age, salary, cars) and 10 objects.
        A GP may take the form: {age+, salary-} with a support of 0.8. This implies that 8 out of 10 objects have the
        values of column age 'increasing' and column 'salary' decreasing.

             In this approach, we assume that every GP candidate may be represented as a binary gene (or individual)
             that has a unique position and cost. The cost is derived from the computed support of that candidate, the
             higher the support value, the lower the cost. The aim of the algorithm is to search through a population of
             individuals (or candidates) and find those with the lowest cost as efficiently as possible.

        :param args: [required] a data source path of Pandas DataFrame, [optional] minimum-support, [optional] eq
        :param max_iter: [optional] maximum_iteration, default is 1
        :type max_iter: int

        :param n_pop: [optional] initial individual population, default is 5
        :type n_pop: int

        :param pc: [optional] children proportion, default is 0.5
        :type pc: float

        :param gamma: [optional] cross-over gamma ratio, default is 1
        :type gamma: float

        :param mu: [optional] mutation mu ratio, default is 0.9
        :type mu: float

        :param sigma: [optional] mutation sigma ratio, default is 0.9
        :type sigma: float

        >>> from so4gp.algorithms as GeneticGRAANK
        >>> import pandas
        >>> import json
        >>> dummy_data = [[30, 3, 1, 10], [35, 2, 2, 8], [40, 4, 2, 7], [50, 1, 1, 6], [52, 7, 1, 2]]
        >>> dummy_df = pandas.DataFrame(dummy_data, columns=['Age', 'Salary', 'Cars', 'Expenses'])
        >>>
        >>> mine_obj = GeneticGRAANK(dummy_df, 0.5, max_iter=3, n_pop=10)
        >>> result_json = mine_obj.discover()
        >>> result = json.loads(result_json)
        >>> # print(result['Patterns'])
        >>> print(result_json) # doctest: +SKIP
        {"Algorithm": "GA-GRAANK", "Best Patterns": [[["Age+", "Salary+", "Expenses-"], 0.6]], "Invalid Count": 12,
            "Iterations": 2}
        """
        super(GeneticGRAANK, self).__init__(*args, **kwargs)
        self._max_iteration: int = max_iter
        self._parent_pop: int = n_pop
        self._children_pop: float = pc
        self._gamma: float = gamma
        self._mu: float = mu
        self._sigma: float = sigma

    def _crossover(self, p1: NumericSS.Candidate, p2: NumericSS.Candidate) -> tuple[NumericSS.Candidate, NumericSS.Candidate]:
        """
        Crosses over the genes of 2 parents (an individual with a specific position and cost) to generate 2
        different offsprings.

        :param p1: The parent 1 individual
        :param p2: The parent 2 individuals
        :return: Two offsprings (children)
        """
        c1 = NumericSS.Candidate()
        c2 = NumericSS.Candidate()
        alpha = np.random.uniform(0, self._gamma, 1)
        c1.position = alpha * p1.position + (1 - alpha) * p2.position
        c2.position = alpha * p2.position + (1 - alpha) * p1.position
        return c1, c2

    def _mutate(self, x: NumericSS.Candidate):
        """

        Mutates an individual's position to create a new and different individual.

        :param x: The existing individual
        :return: A new individual
        """
        y = NumericSS.Candidate(position=x.position, cost=x.cost)
        str_x = str(int(y.position))
        flag = np.random.rand(*(len(str_x),)) <= self._mu
        ind = np.argwhere(flag)
        str_y = "0"
        for i in ind:
            val = float(str_x[i[0]])
            val += self._sigma * np.random.uniform(0, 1, 1)
            if i[0] == 0:
                str_y = "".join(("", "{}".format(int(val)), str_x[1:]))
            else:
                str_y = "".join((str_x[:i[0] - 1], "{}".format(int(val)), str_x[i[0]:]))
            str_x = str_y
        y.position = int(str_y)
        return y

    def discover(self):
        """Description

        Uses genetic algorithm to find GP candidates. The candidates are validated if their computed support is greater
        than or equal to the minimum support threshold specified by the user.

        :return: JSON object
        """

        # Prepare data set
        self.fit_bitmap()
        self.clear_gradual_patterns()
        if self.valid_bins is None:
            return []

        # Initialize search space
        s_space = NumericSS.initialize_search_space(self.valid_bins, self._parent_pop, self._max_iteration)
        if s_space is None:
            return []

        num_children = int(np.round(self._children_pop * self._parent_pop / 2) * 2)  # Number of children np.round is used to get an even number
        repeated = 0
        while s_space.counter < self._max_iteration:
            # while eval_count < max_evaluations:
            # while repeated < 1:

            c_pop = []  # Children population
            for _ in range(num_children // 2):
                # Select Parents
                q = np.random.permutation(self._parent_pop)
                p1 = s_space.pop[q[0]]
                p2 = s_space.pop[q[1]]

                # a. Perform Crossover
                c1, c2 = self._crossover(p1, p2)
                NumericSS.evaluate_candidate(c1, s_space, self.valid_bins)
                NumericSS.evaluate_candidate(c2, s_space, self.valid_bins)

                # b. Perform Mutation
                c1 = self._mutate(c1)
                c2 = self._mutate(c2)
                NumericSS.evaluate_candidate(c1, s_space, self.valid_bins)
                NumericSS.evaluate_candidate(c2, s_space, self.valid_bins)

                # c. Add Offsprings to c_pop
                c_pop.append(c1)
                c_pop.append(c2)

            # Merge, Sort and Select
            s_space.pop += c_pop
            s_space.pop = sorted(s_space.pop, key=lambda x: x.cost)
            s_space.pop = s_space.pop[0:self._parent_pop]

            # Evaluate GP
            _, repeated = NumericSS.evaluate_gradual_pattern(self._max_iteration, repeated, s_space, self)

        # Output
        out = json.dumps({"Algorithm": "GA-GRAANK", "Best Patterns": s_space.str_best_gps,
                          "Invalid Count": s_space.invalid_count, "Iterations": s_space.iter_count})
        """:type out: object"""
        for gp in s_space.best_patterns:
            self.add_gradual_pattern(gp)
        return out
