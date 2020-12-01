import unittest
import numpy as np
from pyquil import Program
from pyquil.gates import X, S, T, CZ, CSWAP, CCNOT
from openfermion import QubitOperator, IsingOperator

from zquantum.core.interfaces.backend_test import QuantumSimulatorTests
from zquantum.core.circuit import Circuit

from .simulator import QulacsSimulator
from .utils import convert_circuit_to_qulacs


class TestQulacs(unittest.TestCase, QuantumSimulatorTests):

    def setUp(self):
        self.backends = [QulacsSimulator(n_samples=None)]
        self.wf_simulators = [QulacsSimulator(n_samples=None)]


class TestGates(unittest.TestCase):
    """
    Tests newly added gates - S, T, XX, YY, ZZ, CZ, CSWAP, CCNOT (Toffoli)
    """

    def setUp(self):
        self.backends = [QulacsSimulator(n_samples=None)]
        self.wf_simulators = [QulacsSimulator(n_samples=None)]

    def test_run_circuit_1qubit_gates(self):
        # Given
        circuit = Circuit(Program(S(0), T(1)))
        n_samples = 100
        # When
        qulacs_circuit = convert_circuit_to_qulacs(circuit)
        self.assertEqual(qulacs_circuit.get_gate_count(), 2)
        self.assertEqual(qulacs_circuit.get_gate(0).get_name(), "S")
        self.assertEqual(qulacs_circuit.get_gate(1).get_name(), "T")

        for backend in self.backends:
            backend.n_samples = n_samples
            measurements = backend.run_circuit_and_measure(circuit)

            counts = measurements.get_counts()
            self.assertEqual(max(counts, key=counts.get), "00")

    def test_run_circuit_2qubit_gates(self):
        # Given
        circuit = Circuit(Program(X(0), CZ(0, 1)))
        n_samples = 100
        # When
        qulacs_circuit = convert_circuit_to_qulacs(circuit)
        self.assertEqual(qulacs_circuit.get_gate_count(), 2)
        self.assertEqual(qulacs_circuit.get_gate(1).get_name(), "CZ")

        for backend in self.backends:
            backend.n_samples = n_samples
            measurements = backend.run_circuit_and_measure(circuit)

            counts = measurements.get_counts()
            self.assertEqual(max(counts, key=counts.get), "10")

    def test_run_circuit_3qubit_gates_toffoli(self):
        # Given
        circuit = Circuit(Program(X(0), X(1), CCNOT(0, 1, 2)))
        n_samples = 100
        # When
        qulacs_circuit = convert_circuit_to_qulacs(circuit)
        self.assertEqual(qulacs_circuit.get_gate_count(), 3)
        self.assertEqual(qulacs_circuit.get_gate(2).get_name(), "DenseMatrix")

        for backend in self.backends:
            backend.n_samples = n_samples
            measurements = backend.run_circuit_and_measure(circuit)

            counts = measurements.get_counts()
            self.assertEqual(max(counts, key=counts.get), "111")

    def test_run_circuit_3qubit_gates_fredkin(self):
        # Given
        circuit = Circuit(Program(X(0), X(2), CSWAP(0, 1, 2)))
        n_samples = 100
        # When
        qulacs_circuit = convert_circuit_to_qulacs(circuit)
        self.assertEqual(qulacs_circuit.get_gate_count(), 3)
        self.assertEqual(qulacs_circuit.get_gate(2).get_name(), "DenseMatrix")

        for backend in self.backends:
            backend.n_samples = n_samples
            measurements = backend.run_circuit_and_measure(circuit)

            counts = measurements.get_counts()
            self.assertEqual(max(counts, key=counts.get), "110")


# import pdb; pdb.set_trace()
