import unittest
import numpy as np
from pyquil import Program
from pyquil.gates import H, CNOT, X, S, T, CZ, CSWAP, CCNOT
from openfermion import QubitOperator, IsingOperator

from zquantum.core.interfaces.backend_test import QuantumSimulatorTests
from zquantum.core.circuit import Circuit

from .simulator import QulacsSimulator
from .utils import convert_circuit_to_qulacs
from .gates import XX, YY, ZZ


class TestQulacs(unittest.TestCase, QuantumSimulatorTests):

    def setUp(self):
        self.backends = [QulacsSimulator(n_samples=None)]
        self.wf_simulators = [QulacsSimulator(n_samples=None)]


class TestPyquilGates(unittest.TestCase):
    """
    Tests newly added gates conversions - S, T, CZ, CSWAP, CCNOT (Toffoli)
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


class TestGateDefs(unittest.TestCase):
    """
    Tests gates XX, YY, ZZ
    """

    def setUp(self):
        self.backends = [QulacsSimulator(n_samples=None)]
        self.wf_simulators = [QulacsSimulator(n_samples=None)]

    def test_gate_XX(self):
        def_gate, gate = XX(0, 0, 1)
        self.assertEqual(gate.name, "XX")
        self.assertEqual(len(gate.qubits), 2)
        self.assertEqual(len(gate.params), 1)
        self.assertEqual(def_gate.name, "XX")

    def test_append_circuit_XX(self):
        # Given
        circuit = Circuit(Program(H(0), CNOT(0, 1), XX(0, 0, 1)))
        # When
        qulacs_circuit = convert_circuit_to_qulacs(circuit)
        self.assertEqual(qulacs_circuit.get_gate_count(), 3)
        self.assertEqual(qulacs_circuit.get_gate(2).get_name(), "Pauli-rotation")

    def test_gate_YY(self):
        def_gate, gate = YY(0, 0, 1)
        self.assertEqual(gate.name, "YY")
        self.assertEqual(len(gate.qubits), 2)
        self.assertEqual(len(gate.params), 1)
        self.assertEqual(def_gate.name, "YY")

    def test_append_circuit_YY(self):
        # Given
        circuit = Circuit(Program(H(0), CNOT(0, 1), YY(0, 0, 1)))
        # When
        qulacs_circuit = convert_circuit_to_qulacs(circuit)
        self.assertEqual(qulacs_circuit.get_gate_count(), 3)
        self.assertEqual(qulacs_circuit.get_gate(2).get_name(), "Pauli-rotation")

    def test_gate_ZZ(self):
        def_gate, gate = ZZ(0, 0, 1)
        self.assertEqual(gate.name, "ZZ")
        self.assertEqual(len(gate.qubits), 2)
        self.assertEqual(len(gate.params), 1)
        self.assertEqual(def_gate.name, "ZZ")    

    def test_append_circuit_YY(self):
        # Given
        circuit = Circuit(Program(H(0), CNOT(0, 1), ZZ(0, 0, 1)))
        # When
        qulacs_circuit = convert_circuit_to_qulacs(circuit)
        self.assertEqual(qulacs_circuit.get_gate_count(), 3)
        self.assertEqual(qulacs_circuit.get_gate(2).get_name(), "Pauli-rotation")
