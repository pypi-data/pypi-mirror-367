from typing import List, Literal
from inspect import getfullargspec
from collections.abc import Callable
import numpy as np

from qlauncher.base import Problem, Algorithm, Result
from qlauncher.exceptions import DependencyError
from qlauncher.routines.orca.backends import OrcaBackend

try:
    from ptseries.algorithms.binary_solvers import BinaryBosonicSolver
except ImportError as e:
    raise DependencyError(e, install_hint='orca', private=True) from e


class BBS(Algorithm):
    """
    Binary Bosonic Solver algorithm class.

    This class represents the Binary Bosonic Solver (BBS) algorithm. BBS is a quantum-inspired algorithm that
    solves optimization problems by mapping them onto a binary bosonic system. It uses a training process
    to find the optimal solution.

    Attributes:
    - learning_rate (float): The learning rate for the algorithm.
    - updates (int): The number of updates to perform during training.
    - tbi_loops (str): The type of TBI loops to use.
    - print_frequency (int): The frequency at which to print updates.
    - logger (Logger): The logger object for logging algorithm information.

    """
    _algorithm_format = 'qubo'

    def __init__(self, algorithm_format: Literal['qubo', 'qubo_fn'] = 'qubo', **kwargs) -> None:
        super().__init__()
        self._algorithm_format = algorithm_format
        self.kwargs = kwargs
        self.input_state = self.kwargs.pop('input_state', None)

    def run(self, problem: Problem, backend: OrcaBackend, formatter: Callable[[Problem], np.ndarray]) -> Result:

        objective = formatter(problem)

        # TODO: use offset somehow
        if not callable(objective):
            objective, offset = objective
            if self.input_state is None:
                self.input_state = [not i % 2 for i in range(len(objective))]

        bbs = backend.get_bbs(
            len(self.input_state),
            objective,
            self.input_state,
            **{k: v for k, v in self.kwargs.items() if k in getfullargspec(BinaryBosonicSolver.__init__)[0]}

        )
        bbs.train(**{k: v for k, v in self.kwargs.items() if k in getfullargspec(BinaryBosonicSolver.train)[0]})

        return self.construct_results(bbs)

    def get_bitstring(self, result: List[float]) -> str:
        return ''.join(map(str, map(int, result)))

    def construct_results(self, solver: BinaryBosonicSolver) -> Result:
        # TODO: add support for distribution (probably with different logger)
        best_bitstring = ''.join(
            map(str, map(int, solver.config_min_encountered)))
        best_energy = solver.E_min_encountered
        most_common_bitstring = None
        most_common_bitstring_energy = None
        distribution = None
        energy = None
        num_of_samples = solver.n_samples
        average_energy = None
        energy_std = None
        #! Todo: instead of None attach relevant info from 'results'
        # results fail to pickle correctly btw
        return Result(best_bitstring, best_energy, most_common_bitstring,
                      most_common_bitstring_energy, distribution, energy,
                      num_of_samples, average_energy, energy_std, None)
