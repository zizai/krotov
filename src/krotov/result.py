import time
from textwrap import dedent

from .objectives import Objective
from .structural_conversions import (
    _nested_list_shallow_copy)

__all__ = ['Result']


class Result():
    """Result object for a Krotov optimization

    .. Note::

        A :class:`Result` object can be serialized via :func:`pickle.dump`,
        but the controls in the :attr:`objectives` may not be preserved in the
        serialization. After unpickling, the :attr:`objectives` should be
        overwritten with an appropriate list.

    Attributes:
        objectives (list[Objective]): The control objectives
        tlist (numpy.ndarray): The time grid values
        iters (list[int]): Iteration numbers, starting at 0.
        iter_seconds (list[int]): for each iteration number, the number of
            seconds that were spent in the optimization
        info_vals (list): For each iteration, the return value of `info_hook`,
            or None
        tau_vals (list[list[complex]): for each iteration, a list of complex
            overlaps between the forward-propagated state and the target state
            for each objective.
        guess_controls (list[numpy.ndarray]): List of the guess controls in
            array format
        optimized_controls (list[numpy.ndarray]): List of the optimized control
            fields, in the order corresponding to :attr:`guess_controls`
        controls_mapping (list): A nested list that indicates where in
            :attr:`objectives` the :attr:`guess_controls` and
            :attr:`optimized_controls` are used (as returned by
            :func:`.extract_controls_mapping`)
        all_pulses (list): If the optimization was performed with
            ``store_all_pulses=True``, for each iteration, a list of the
            optimized pulses (in the order corresponding to
            :attr:`guess_controls`).
            These pulses are defined at midpoints of the `tlist` intervals.
            Empty list if ``store_all_pulses=False``
        states (list[list[qutip.Qobj]]): for each objective, a list of states
            for each value in `tlist`, obtained from propagation under the
            final optimized control fields.
        start_local_time (time.struct_time): Time stamp of when the
            optimization started
        end_local_time (time.struct_time): Time stamp of when the optimization
            ended
    """
    time_fmt = "%Y-%m-%d %H:%M:%S"
    """Format used in :attr:`start_local_time_str` and
    :attr:`end_local_time_str`
    """

    def __init__(self):
        self.objectives = []
        self.tlist = []
        self.iters = []
        self.iter_seconds = []
        self.info_vals = []
        self.tau_vals = []
        self.guess_controls = []
        self.optimized_controls = []
        self.controls_mapping = []
        self.all_pulses = []
        self.states = []
        self.start_local_time = None
        self.end_local_time = None

    def __str__(self):
        return dedent(r'''
        Krotov Optimization Result
        --------------------------
        - Started at {start_local_time}
        - Number of objectives: {n_objectives}
        - Number of iterations: {n_iters}
        - Ended at {end_local_time}
        '''.format(
            start_local_time=self.start_local_time_str,
            n_objectives=len(self.objectives),
            n_iters=len(self.iters)-1,  # do not count zero iteration
            end_local_time=self.end_local_time_str,
        )).strip()

    def __repr__(self):
        return self.__str__()

    @property
    def start_local_time_str(self):
        """The :attr:`start_local_time` attribute formatted as a string"""
        if self.start_local_time is not None:
            return time.strftime(self.time_fmt, self.start_local_time)
        else:
            return 'n/a'

    @property
    def end_local_time_str(self):
        """The :attr:`end_local_time` attribute formatted as a string"""
        if self.end_local_time is not None:
            return time.strftime(self.time_fmt, self.end_local_time)
        else:
            return 'n/a'

    @property
    def optimized_objectives(self):
        """list[Objective]: A copy of the :attr:`objectives` with the
        :attr:`optimized_controls` plugged in"""
        objectives = []
        for (i, obj) in enumerate(self.objectives):
            H = _plug_in_optimized_controls(
                obj.H, self.optimized_controls, self.controls_mapping[i][0])
            c_ops = [
                _plug_in_optimized_controls(
                    c_op, self.optimized_controls,
                    self.controls_mapping[i][j+1])
                for (j, c_op) in enumerate(obj.c_ops)]
            objectives.append(
                Objective(
                    H=H,
                    initial_state=obj.initial_state,
                    target_state=obj.target_state,
                    c_ops=c_ops))
        return objectives


def _plug_in_optimized_controls(H, controls, mapping):
    """Auxilliary routine to :attr:`Result.optimized_objectives`"""
    H = _nested_list_shallow_copy(H)
    for (control, control_mapping) in zip(controls, mapping):
        for i in control_mapping:
            H[i][1] = control
    return H
