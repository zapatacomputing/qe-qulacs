from .simulator import QulacsSimulator
import unittest
import numpy as np
from zquantum.core.circuit import Circuit
from openfermion.ops import QubitOperator, IsingOperator
from pyquil import Program
from pyquil.gates import H, CNOT, RX, CZ

class TestQulacs(unittest.TestCase):

    def test_get_exact_expectation_values(self):
        # Given
        simulator = QulacsSimulator(n_samples=None)
        circuit = Circuit(Program(H(0), CNOT(0,1), CNOT(1,2)))
        qubit_operator = QubitOperator('[] + [Z0 Z1] + [X0 X2] ')
        # When
        expectation_values = simulator.get_exact_expectation_values(circuit, qubit_operator)
        # Then
        self.assertAlmostEqual(sum(expectation_values.values), 2.0)

    def test_get_expectation_values(self):
        # Given
        simulator = QulacsSimulator(n_samples=100)
        circuit = Circuit(Program(H(0), CNOT(0,1), CNOT(1,2)))
        qubit_operator = IsingOperator('[] + [Z0 Z1] + [Z0 Z2] ')
        target_expectation_values = np.array([1, 1, 1])
        # When
        expectation_values = simulator.get_expectation_values(circuit, qubit_operator)
        # Then
        np.testing.assert_array_equal(expectation_values.values, target_expectation_values)

    def test_get_exact_expectation_values_empty_op(self):
        # Given
        simulator = QulacsSimulator(n_samples=None)
        circuit = Circuit(Program(H(0), CNOT(0,1), CNOT(1,2)))
        qubit_operator = QubitOperator()
        # When
        expectation_values = simulator.get_exact_expectation_values(circuit, qubit_operator)
        # Then
        self.assertAlmostEqual(sum(expectation_values.values), 0.0)

    def test_run_circuit_and_measure(self):
        # Given
        simulator = QulacsSimulator(n_samples=100)
        circuit = Circuit(Program(H(0), CNOT(0,1), CNOT(1,2)))
        # When
        measurements = simulator.run_circuit_and_measure(circuit)
        # Then
        self.assertEqual(len(measurements), 100)
        self.assertEqual(len(measurements[0]), 3)
