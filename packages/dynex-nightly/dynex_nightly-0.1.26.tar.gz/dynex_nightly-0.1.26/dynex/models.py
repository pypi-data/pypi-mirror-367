import dimod
import numpy as np
from abc import ABC

from config import DynexConfig


class DynexModel(ABC):
    """
    Abstract base class for Dynex models.
    Includes config and logger initialization, and conversion utilities.
    """

    def __init__(self, config: DynexConfig = None, logging: bool = False):
        self.config = config if config is not None else DynexConfig()
        self.logger = getattr(self.config, "logger", None)
        self.logging = logging
        self.type_str = 'Unknown'
        
    def __str__(self)-> str:
        return self.type_str

    @staticmethod
    def _max_precision(bqm: dimod.BinaryQuadraticModel) -> float:
        """
        Returns the maximum precision for BQM conversion.

        Args:
            bqm: dimod.BinaryQuadraticModel

        Returns:
            float: precision value
        """
        max_abs_coeff = np.max(np.abs(bqm.to_numpy_matrix()))
        if max_abs_coeff == 0:
            raise Exception("ERROR: AT LEAST ONE WEIGHT MUST BE > 0.0")
        precision = 10 ** (np.floor(np.log10(max_abs_coeff)) - 4)
        return precision

    def _convert_bqm_to_qubo(self, bqm: dimod.BinaryQuadraticModel, relabel: bool = True, logging: bool = True):
        """
        Converts a BQM to QUBO format.

        Args:
            bqm: dimod.BinaryQuadraticModel
            relabel: If True, relabel variables to integers
            logging: If True, log conversion info

        Returns:
            tuple: clauses, num_variables, num_clauses, mappings, precision, bqm
        """
        mappings = bqm.variables._relabel_as_integers()
        clauses = []
        Q = bqm.to_qubo()
        Q_list = list(Q[0])
        if logging and self.logger:
            self.logger.info("MODEL CONVERTED TO QUBO")

        newQ = []
        for i in range(0, len(Q_list)):
            touple = Q_list[i]
            w = Q[0][touple]
            newQ.append(w)
        max_abs_coeff = np.max(np.abs(newQ))
        if max_abs_coeff == 0:
            if self.logger:
                self.logger.error("ERROR: AT LEAST ONE WEIGHT MUST BE > 0.0")
            raise Exception("ERROR: AT LEAST ONE WEIGHT MUST BE > 0.0")

        precision = 10 ** (np.floor(np.log10(max_abs_coeff)) - 4)

        if precision > 1:
            if logging and self.logger:
                self.logger.warning(f"Precision cut from {precision} to 1")
            precision = 1

        W_add = Q[1]
        if logging and self.logger:
            self.logger.info(f"QUBO: Constant offset of the binary quadratic model: {W_add}")

        for i in range(0, len(Q_list)):
            touple = Q_list[i]
            i_val = int(touple[0]) + 1
            j_val = int(touple[1]) + 1
            w = Q[0][touple]
            w_int = int(np.round(w / precision))

            if i_val == j_val:
                if w_int > 0:
                    clauses.append([w_int, -i_val])
                if w_int < 0:
                    clauses.append([-w_int, i_val])
            else:
                if w_int > 0:
                    clauses.append([w_int, -i_val, -j_val])
                if w_int < 0:
                    clauses.append([-w_int, i_val, -j_val])
                    clauses.append([-w_int, j_val])

        num_variables = len(bqm.variables)
        num_clauses = len(clauses)
        bqm.variables._relabel(mappings)
        return clauses, num_variables, num_clauses, mappings, precision, bqm

    def _convert_bqm_to_qubo_direct(self, bqm: dimod.BinaryQuadraticModel, relabel: bool = True, logging: bool = True):
        """
        Converts a BQM directly to QUBO using fast formulation.

        Args:
            bqm: dimod.BinaryQuadraticModel
            relabel: If True, relabel variables to integers
            logging: If True, log conversion info

        Returns:
            tuple: clauses, num_variables, num_clauses, mappings, precision, bqm, wcnf_offset, precision
        """
        mappings = bqm.variables._relabel_as_integers()
        clauses = []
        linear = [v for i, v in sorted(bqm.linear.items(), key=lambda x: x[0])]
        quadratic = [[i, j, v] for (i, j), v in bqm.quadratic.items()]
        precision = self._max_precision(bqm)
        if precision > 1:
            if logging and self.logger:
                self.logger.warning(f"Precision cut from {precision} to 1")
            precision = 1
        if logging and self.logger:
            self.logger.info(f"Precision set to {precision}")
        wcnf_offset = 0
        for i, w in enumerate(linear):
            weight = np.round(w / precision)
            if weight > 0:
                clauses.append([weight, -(i + 1)])
            elif weight < 0:
                clauses.append([-weight, (i + 1)])
                wcnf_offset += weight
        num_variables = len(linear)
        if quadratic:
            quadratic_corr = np.round(np.array(quadratic)[:, 2] / precision)
            for edge, _ in enumerate(quadratic):
                i = quadratic[edge][0] + 1
                j = quadratic[edge][1] + 1
                if quadratic[edge][2] > 0:
                    v = np.abs(quadratic_corr[edge])
                    if v != 0:
                        clauses.append([v, -i, -j])
                elif quadratic[edge][2] < 0:
                    v = np.abs(quadratic_corr[edge])
                    if v != 0:
                        clauses.append([v, i, j])
                        clauses.append([v, -i, j])
                        clauses.append([v, i, -j])
                        wcnf_offset -= v
        wcnf_offset = wcnf_offset + bqm.offset / precision
        bqm.variables._relabel(mappings)
        validation_vars = [1, 0, 1, 0, 1, 0, 1, 0]
        validation_weight = 999999
        for v in range(0, len(validation_vars)):
            direction = 1 if validation_vars[v] == 1 else -1
            i = num_variables + 1 + v
            clauses.append([validation_weight, direction * i])
        num_variables += len(validation_vars)
        num_clauses = len(clauses)
        return clauses, num_variables, num_clauses, mappings, precision, bqm, wcnf_offset


class SAT(DynexModel):
    """
    Creates a model, which can be used by the sampler based on a SAT problem. The Dynex sampler needs a "model" object for sampling. Based on the problem formulation, multiple model classes are supported.

        :Parameters:

        - :clauses: List of sat caluses for this model (`list`)
        - :logging: True to show model creation information, False to silence outputs (`bool`)

        :Returns:

        - class:`dynex.model`

    :Example:

    Dimod's dimod.binary.BinaryQuadraticModel (BQM) contains linear and quadratic biases for problems formulated as binary quadratic models as well as additional information such as variable labels and offset.

    .. code-block:: Python

        clauses = [[1, -2, 3], [-1, 4, 5], [6, 7, -8], [-9, -10, 11], [12, 13, -14],
           [-1, 15, -16], [17, -18, 19], [-20, 2, 3], [4, -5, 6], [-7, 8, 9],
           [10, 11, -12], [-13, -14, 15], [16, 17, -18], [-19, 20, 1], [2, -3, 4],
           [-5, 6, 7], [8, 9, -10], [-11, -12, 13], [14, 15, -16], [-17, 18, 19]]
        model =  dynex.SAT(clauses)

    """

    def __init__(self, clauses, logging=False, config: DynexConfig = None):
        super().__init__(config=config, logging=logging)
        # validation clauses
        validation_vars = [1, 0, 1, 0, 1, 0, 1, 0]
        num_variables = max(max(abs(lit) for lit in clause) for clause in clauses)
        for i in range(0, len(validation_vars)):
            if validation_vars[i] == 1:
                clauses.append([num_variables + 1 + i])
            if validation_vars[i] == 0:
                clauses.append([(num_variables + 1 + i) * -1])

        self.clauses = clauses
        self.type = 'cnf'
        self.bqm = ""
        self.logging = logging
        self.type_str = 'SAT'
        self.wcnf_offset = 0
        self.precision = 0.0001


class BQM(DynexModel):
    """
    Creates a model, which can be used by the sampler based on a Binary Quadratic Model (BQM) problem. The Dynex sampler needs a "model" object for sampling. Based on the problem formulation, multiple model classes are supported.

        :Parameters:

        - :bqm: The BQM to be used for this model (class:`dimod.BinaryQuadraticModel`)
        - :relabel: Defines if the BQM's variable names should be relabeled (`bool`)
        - :logging: True to show model creation information, False to silence outputs (`bool`)

        :Returns:

        - class:`dynex.model`

    :Example:

    Dimod's `dimod.binary.BinaryQuadraticModel` (BQM) contains linear and quadratic biases for problems formulated as binary quadratic models as well as additional information such as variable labels and offset.

    .. code-block:: Python

        bqm = dimod.BinaryQuadraticModel({'x1': 1.0, 'x2': -1.5, 'x3': 2.0},
                                 {('x1', 'x2'): 1.0, ('x2', 'x3'): -2.0},
                                 0.0, dimod.BINARY)
        model = dynex.BQM(bqm)

    """

    def __init__(self, bqm, relabel=True, logging=False, formula=2, config: DynexConfig = None):
        super().__init__(config=config, logging=logging)

        if formula == 1:
            self.clauses, self.num_variables, self.num_clauses, self.var_mappings, self.precision, self.bqm = self._convert_bqm_to_qubo(
                bqm, relabel, logging)
        elif formula == 2:
            self.clauses, self.num_variables, self.num_clauses, self.var_mappings, self.precision, self.bqm, self.wcnf_offset = self._convert_bqm_to_qubo_direct(
                bqm, relabel, logging)

        if self.num_clauses == 0 or self.num_variables == 0:
            self.logger.error('[DYNEX] ERROR: Could not initiate model - no variables & clauses')
            raise Exception('[DYNEX] ERROR: Could not initiate model - no variables & clauses')
        self.type = 'wcnf'
        self.logging = logging
        self.type_str = 'BQM'

    def __str__(self)-> str:
        return self.type_str


class CQM(DynexModel):
    """
    Creates a model, which can be used by the sampler based on a Constraint Quadratic Model (CQM) problem. The Dynex sampler needs a "model" object for sampling. Based on the problem formulation, multiple model classes are supported.

        :Parameters:

        - :cqm: The CQM to be used for this model (class:`dimod.ConstraintQuadraticModel`)
        - :relabel: Defines if the BQM's variable names should be relabeled (`bool`)
        - :logging: True to show model creation information, False to silence outputs (`bool`)

        :Returns:

        - class:`dynex.model`

    :Example:

    Dimod's `dimod.ConstrainedQuadraticModel` (CQM) contains linear and quadratic biases for problems formulated as constrained quadratic models as well as additional information such as variable labels, offsets, and equality and inequality constraints.

    .. code-block:: Python

        num_widget_a = dimod.Integer('num_widget_a', upper_bound=7)
        num_widget_b = dimod.Integer('num_widget_b', upper_bound=3)
        cqm = dimod.ConstrainedQuadraticModel()
        cqm.set_objective(-3 * num_widget_a - 4 * num_widget_b)
        cqm.add_constraint(num_widget_a + num_widget_b <= 5, label='total widgets')
        model = dynex.CQM(cqm)
        sampler = dynex.DynexSampler(model, mainnet=False)
        sampleset = sampler.sample(num_reads=1000, annealing_time = 10)


    """

    def __init__(self, cqm, relabel=True, logging=False, formula=2, config: DynexConfig = None):
        super().__init__(config=config, logging=logging)

        bqm, self.invert = dimod.cqm_to_bqm(cqm)
        if formula == 1:
            self.clauses, self.num_variables, self.num_clauses, self.var_mappings, self.precision, self.bqm = self._convert_bqm_to_qubo(
                bqm, relabel, logging)
        if formula == 2:
            self.clauses, self.num_variables, self.num_clauses, self.var_mappings, self.precision, self.bqm, self.wcnf_offset = self._convert_bqm_to_qubo_direct(
                bqm, relabel, logging)

        if self.num_clauses == 0 or self.num_variables == 0:
            raise Exception('[DYNEX] ERROR: Could not initiate model - no variables & clauses')
            return
        self.type = 'wcnf'
        self.logging = logging
        self.type_str = 'CQM'
        self.cqm = cqm


class DQM(DynexModel):
    """
    Creates a model, which can be used by the sampler based on a Discrete Quadratic Model (DQM) problem. The Dynex sampler needs a "model" object for sampling. Based on the problem formulation, multiple model classes are supported.

        :Parameters:

        - :dqm: The DQM to be used for this model (class:`dimod.DiscreteQuadraticModel`)
        - :relabel: Defines if the BQM's variable names should be relabeled (`bool`)
        - :logging: True to show model creation information, False to silence outputs (`bool`)

        :Returns:

        - class:`dynex.model`

    :Example:

    Dimod's `dimod.ConstrainedQuadraticModel` (CQM) contains linear and quadratic biases for problems formulated as constrained quadratic models as well as additional information such as variable labels, offsets, and equality and inequality constraints.

    .. code-block:: Python

        cases = ["rock", "paper", "scissors"]
        win = {"rock": "scissors", "paper": "rock", "scissors": "paper"}
        dqm = dimod.DiscreteQuadraticModel()
        dqm.add_variable(3, label='my_hand')
        dqm.add_variable(3, label='their_hand')

        for my_idx, my_case in enumerate(cases):
            for their_idx, their_case in enumerate(cases):
                if win[my_case] == their_case:
                    dqm.set_quadratic('my_hand', 'their_hand',
                            {(my_idx, their_idx): -1})
                if win[their_case] == my_case:
                    dqm.set_quadratic('my_hand', 'their_hand',
                            {(my_idx, their_idx): 1})

        model = dynex.DQM(dqm)
        sampler = dynex.DynexSampler(model, mainnet=False)
        sampleset = sampler.sample(num_reads=1000, annealing_time = 10)
        print(sampleset)

        print("{} beats {}".format(cases[sampleset.first.sample['my_hand']],
                            cases[sampleset.first.sample['their_hand']]))

    """

    def __init__(self, dqm, relabel=True, logging=False, formula=2, config: DynexConfig = None ):
        super().__init__(config=config, logging=logging)

        # convert dqm->cqm
        cqm = dimod.ConstrainedQuadraticModel.from_discrete_quadratic_model(dqm)
        # convert cqm->bqm
        bqm, self.invert = dimod.cqm_to_bqm(cqm)

        if formula == 1:
            self.clauses, self.num_variables, self.num_clauses, self.var_mappings, self.precision, self.bqm = self._convert_bqm_to_qubo(
                bqm, relabel, logging)
        if formula == 2:
            self.clauses, self.num_variables, self.num_clauses, self.var_mappings, self.precision, self.bqm, self.wcnf_offset, self.precision = self._convert_bqm_to_qubo_direct(
                bqm, relabel, logging)

        if self.num_clauses == 0 or self.num_variables == 0:
            raise Exception('[DYNEX] ERROR: Could not initiate model - no variables & clauses')
            return
        self.type = 'wcnf'
        self.logging = logging
        self.type_str = 'DQM'
        self.dqm = dqm
