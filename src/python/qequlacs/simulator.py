import os
# It seems that qulacs has some conflict with pyquil, therefore it needs to be imported before zquantum.core.
import qulacs
from pyquil.wavefunction import Wavefunction
from zquantum.core.interfaces.backend import QuantumSimulator
from zquantum.core.circuit import save_circuit
from zquantum.core.measurement import (load_wavefunction, load_expectation_values, sample_from_wavefunction,
                                        ExpectationValues, get_expectation_values_from_measurements, expectation_values_to_real)
from zquantum.core.measurement import sample_from_wavefunction
import openfermion
from qeopenfermion import reverse_qubit_order
from .utils import convert_circuit_to_qulacs, qubitop_to_qulacspauli

class QulacsSimulator(QuantumSimulator):
    def __init__(self, n_samples=None):
        self.n_samples = n_samples

    def run_circuit_and_measure(self, circuit, **kwargs):
        '''
        Run a circuit and measure a certain number of bitstrings

        Args:
            circuit (zquantum.core.circuit.Circuit): the circuit to prepare the state
            n_samples (int): the number of bitstrings to sample
        Returns:
            a list of bitstrings (a list of tuples)
        '''
        wavefunction = self.get_wavefunction(circuit)
        return sample_from_wavefunction(wavefunction, self.n_samples)

    def get_expectation_values(self, circuit, qubit_operator, use_coefficients=True, **kwargs):
        if self.n_samples==None:
            return self.get_exact_expectation_values(circuit, qubit_operator, **kwargs)
        else:
            measurements = self.run_circuit_and_measure(circuit)
            expectation_values = get_expectation_values_from_measurements(
                                    measurements, qubit_operator, use_coefficients=use_coefficients)

            expectation_values = expectation_values_to_real(expectation_values)
            return expectation_values

    def get_exact_expectation_values(self, circuit, qubit_operator, **kwargs):
        if self.n_samples != None:
            raise Exception("Exact expectation values work only for n_samples equal to None.")

        # Qubit operators in openfermion use different index ordering than wavefunction.
        qubit_operator = reverse_qubit_order(qubit_operator)

        expectation_values = []
        n_qubits = openfermion.utils.count_qubits(qubit_operator)

        amplitudes = self.get_wavefunction(circuit).amplitudes
        for term, coeff in qubit_operator.terms.items():
            term_op = openfermion.QubitOperator(term, coeff)
            term_sparse = openfermion.utils.qubit_operator_sparse(term_op, n_qubits)
            expectation_value = openfermion.utils.expectation(term_sparse, amplitudes)
            expectation_values.append(expectation_value)
        return ExpectationValues(expectation_values)

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
