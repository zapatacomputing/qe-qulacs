from typing import Any

import numpy as np
import qulacs
from qulacs.observable import create_observable_from_openfermion_text
from zquantum.core.circuits import Circuit, GateOperation
from zquantum.core.interfaces.backend import QuantumSimulator, StateVector
from zquantum.core.measurement import (
    ExpectationValues,
    Measurements,
    sample_from_wavefunction,
)
from zquantum.core.openfermion import QubitOperator
from zquantum.core.wavefunction import Wavefunction, flip_amplitudes, flip_wavefunction

from .conversions import convert_to_qulacs


class QulacsSimulator(QuantumSimulator):

    supports_batching = False

    def __init__(self):
        super().__init__()

    def run_circuit_and_measure(self, circuit: Circuit, n_samples: int) -> Measurements:
        """
        Run a circuit and measure a certain number of bitstrings

        Args:
            circuit: the circuit to prepare the state
            n_samples: the number of bitstrings to sample
        """
        wavefunction = self.get_wavefunction(circuit)
        bitstrings = sample_from_wavefunction(wavefunction, n_samples)
        return Measurements(bitstrings)

    def get_exact_expectation_values(
        self, circuit: Circuit, qubit_operator: QubitOperator
    ) -> ExpectationValues:
        self.number_of_circuits_run += 1
        self.number_of_jobs_run += 1

        expectation_values = []
        qulacs_state = self._get_qulacs_state(circuit)

        for op in qubit_operator:
            qulacs_observable = create_observable_from_openfermion_text(str(op))

            for term_id in range(qulacs_observable.get_term_count()):
                term = qulacs_observable.get_term(term_id)
                expectation_values.append(
                    np.real(term.get_expectation_value(qulacs_state))
                )
        return ExpectationValues(np.array(expectation_values))

    def _get_qulacs_state(
        self, circuit: Circuit, initial_state=None
    ) -> qulacs.QuantumState:
        if initial_state is None:
            initial_state = np.array(
                [1] + (2 ** circuit.n_qubits - 1) * [0], dtype=np.int8
            )
        qulacs_state = qulacs.QuantumState(circuit.n_qubits)
        qulacs_state.load(flip_amplitudes(initial_state))
        qulacs_circuit = convert_to_qulacs(circuit)
        qulacs_circuit.update_quantum_state(qulacs_state)
        return qulacs_state

    def _get_wavefunction_from_native_circuit(
        self, circuit: Circuit, initial_state: StateVector
    ) -> StateVector:
        return flip_amplitudes(
            self._get_qulacs_state(circuit, initial_state).get_vector()
        )

    def can_be_executed_natively(self, operation: Any) -> bool:
        return isinstance(operation, GateOperation)
