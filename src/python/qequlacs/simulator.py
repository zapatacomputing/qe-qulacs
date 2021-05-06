# It seems that qulacs has some conflict with pyquil, therefore it needs to be imported
# before zquantum.core.
import qulacs
import itertools
import numpy as np
from qulacs.observable import create_observable_from_openfermion_text
from pyquil.wavefunction import Wavefunction
from zquantum.core.interfaces.backend import QuantumSimulator
from zquantum.core.circuit import Circuit as OldCircuit
from zquantum.core.measurement import (
    sample_from_wavefunction,
    ExpectationValues,
    Measurements,
)
from zquantum.core.wip.circuits import (
    new_circuit_from_old_circuit,
    Circuit as NewCircuit,
    GateOperation,
)
from zquantum.core.wip.compatibility_tools import compatible_with_old_type
from .conversions import convert_to_qulacs
from typing import Optional


class QulacsSimulator(QuantumSimulator):

    supports_batching = False

    def __init__(self, n_samples=None):
        super().__init__(n_samples)

    @compatible_with_old_type(
        old_type=OldCircuit, translate_old_to_wip=new_circuit_from_old_circuit
    )
    def run_circuit_and_measure(
        self, circuit: NewCircuit, n_samples: Optional[int] = None, **kwargs
    ):
        """
        Run a circuit and measure a certain number of bitstrings

        Args:
            circuit: the circuit to prepare the state
            n_samples: the number of bitstrings to sample
        Returns:
            The measured bitstrings.
        """
        if n_samples is None:
            if self.n_samples is None:
                raise ValueError(
                    "n_samples needs to be specified either as backend attribute or as an function argument."
                )
            else:
                n_samples = self.n_samples
        wavefunction = self.get_wavefunction(circuit)
        bitstrings = sample_from_wavefunction(wavefunction, n_samples)
        return Measurements(bitstrings)

    @compatible_with_old_type(
        old_type=OldCircuit, translate_old_to_wip=new_circuit_from_old_circuit
    )
    def get_wavefunction(self, circuit):
        super().get_wavefunction(circuit)
        qulacs_state = self.get_qulacs_state_from_circuit(circuit)
        amplitudes = qulacs_state.get_vector()
        return Wavefunction(amplitudes)

    @compatible_with_old_type(
        old_type=OldCircuit, translate_old_to_wip=new_circuit_from_old_circuit
    )
    def get_exact_expectation_values(self, circuit, qubit_operator, **kwargs):
        if self.n_samples is not None:
            raise Exception(
                "Exact expectation values work only for n_samples equal to None."
            )
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

    @compatible_with_old_type(
        old_type=OldCircuit, translate_old_to_wip=new_circuit_from_old_circuit
    )
    def get_qulacs_state_from_circuit(self, circuit: NewCircuit):
        qulacs_state = qulacs.QuantumState(circuit.n_qubits)
        for executable, operations_group in itertools.groupby(
            circuit.operations, self.can_be_executed_natively
        ):
            if executable:
                qulacs_circuit = convert_to_qulacs(
                    NewCircuit(operations_group, circuit.n_qubits)
                )
                qulacs_circuit.update_quantum_state(qulacs_state)
            else:
                wavefunction = qulacs_state.get_vector()
                for operation in operations_group:
                    wavefunction = operation.apply(wavefunction)
                qulacs_state.load(wavefunction)
        return qulacs_state

    def can_be_executed_natively(self, operation):
        return isinstance(operation, GateOperation)
