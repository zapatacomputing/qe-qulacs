import os

# It seems that qulacs has some conflict with pyquil, therefore it needs to be imported before zquantum.core.
import qulacs
import numpy as np
from qulacs.observable import create_observable_from_openfermion_text
from pyquil.wavefunction import Wavefunction
from zquantum.core.interfaces.backend import QuantumSimulator
from zquantum.core.circuit import save_circuit
from zquantum.core.measurement import (
    load_wavefunction,
    load_expectation_values,
    sample_from_wavefunction,
    ExpectationValues,
    Measurements,
    expectation_values_to_real,
)
from zquantum.core.measurement import (
    sample_from_wavefunction,
    expectation_values_to_real,
    ExpectationValues,
)
import openfermion
from .utils import convert_circuit_to_qulacs, qubitop_to_qulacspauli


class QulacsSimulator(QuantumSimulator):
    def __init__(self, n_samples=None):
        self.n_samples = n_samples

    def run_circuit_and_measure(self, circuit, **kwargs):
        """
        Run a circuit and measure a certain number of bitstrings

        Args:
            circuit (zquantum.core.circuit.Circuit): the circuit to prepare the state
            n_samples (int): the number of bitstrings to sample
        Returns:
            a list of bitstrings (a list of tuples)
        """
        wavefunction = self.get_wavefunction(circuit)
        bitstrings = sample_from_wavefunction(wavefunction, self.n_samples)
        return Measurements(bitstrings)

    def get_expectation_values(self, circuit, qubit_operator, **kwargs):
        if self.n_samples == None:
            return self.get_exact_expectation_values(circuit, qubit_operator, **kwargs)
        else:
            measurements = self.run_circuit_and_measure(circuit)
            expectation_values = measurements.get_expectation_values(qubit_operator)

            expectation_values = expectation_values_to_real(expectation_values)
            return expectation_values

    def get_exact_expectation_values(self, circuit, qubit_operator, **kwargs):
        if self.n_samples != None:
            raise Exception(
                "Exact expectation values work only for n_samples equal to None."
            )

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

    def get_wavefunction(self, circuit):
        qulacs_state = self.get_qulacs_state_from_circuit(circuit)
        amplitudes = qulacs_state.get_vector()
        return Wavefunction(amplitudes)

    def get_qulacs_state_from_circuit(self, circuit):
        qulacs_circuit = convert_circuit_to_qulacs(circuit)
        num_qubits = len(circuit.qubits)
        qulacs_state = qulacs.QuantumState(num_qubits)
        qulacs_circuit.update_quantum_state(qulacs_state)
        return qulacs_state
