import itertools
from typing import Any

import numpy as np
import qulacs
from openfermion import QubitOperator
from qulacs.observable import create_observable_from_openfermion_text
from zquantum.core.circuits import Circuit, GateOperation
from zquantum.core.interfaces.backend import (
    QuantumSimulator,
)
from zquantum.core.measurement import (
    ExpectationValues,
    Measurements,
    sample_from_wavefunction,
)
from zquantum.core.wavefunction import Wavefunction, flip_wavefunction, flip_amplitudes

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

    def get_wavefunction(self, circuit) -> Wavefunction:
        super().get_wavefunction(circuit)
        qulacs_state = self.get_qulacs_state_from_circuit(circuit)
        amplitudes = qulacs_state.get_vector()
        return flip_wavefunction(Wavefunction(amplitudes))

    def get_exact_expectation_values(
        self, circuit: Circuit, qubit_operator: QubitOperator
    ) -> ExpectationValues:
        self.number_of_circuits_run += 1
        self.number_of_jobs_run += 1

        expectation_values = []
        qulacs_state = self.get_qulacs_state_from_circuit(circuit)

        for op in qubit_operator:
            qulacs_observable = create_observable_from_openfermion_text(str(op))

            for term_id in range(qulacs_observable.get_term_count()):
                term = qulacs_observable.get_term(term_id)
                expectation_values.append(
                    np.real(term.get_expectation_value(qulacs_state))
                )
        return ExpectationValues(np.array(expectation_values))

    def get_qulacs_state_from_circuit(self, circuit: Circuit):
        qulacs_state = qulacs.QuantumState(circuit.n_qubits)
        for executable, operations_group in itertools.groupby(
            circuit.operations, self.can_be_executed_natively
        ):
            if executable:
                qulacs_circuit = convert_to_qulacs(
                    Circuit(operations_group, circuit.n_qubits)
                )
                qulacs_circuit.update_quantum_state(qulacs_state)
            else:
                wavefunction = flip_amplitudes(qulacs_state.get_vector())
                for operation in operations_group:
                    wavefunction = operation.apply(wavefunction)
                qulacs_state.load(flip_amplitudes(wavefunction))
        return qulacs_state

    def can_be_executed_natively(self, operation: Any) -> bool:
        return isinstance(operation, GateOperation)
