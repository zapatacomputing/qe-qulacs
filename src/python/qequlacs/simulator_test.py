import unittest
import numpy as np
from pyquil import Program, get_qc
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
        n_samples = 1000
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
        n_samples = 1000
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
        n_samples = 1000
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
        n_samples = 1000
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
        self.qvm = get_qc('9q-square-qvm')

    def test_gate_XX(self):
        def_gate, gate = XX(0, 0, 1)
        self.assertEqual(gate.name, "XX")
        self.assertEqual(len(gate.qubits), 2)
        self.assertEqual(len(gate.params), 1)
        self.assertEqual(def_gate.name, "XX")

    def test_append_circuit_XX(self):
        # Given
        n_samples = 1000
        # XX with Pi will -> both qubits to 0 in ~100% cases
        prog1 = Program(X(0), CNOT(0, 1), XX(np.pi, 0, 1))
        # XX with Pi/2 will -> both qubits to 0 in ~50% cases
        prog2 = Program(X(0), CNOT(0, 1), XX(np.pi/2, 0, 1))
        circuit1 = Circuit(prog1)
        circuit2 = Circuit(prog2)
        # When
        results1 = self.qvm.run_and_measure(prog1, trials=n_samples)
        self.assertTrue(1 not in results1[0])
        self.assertTrue(1 not in results1[1])

        results2 = self.qvm.run_and_measure(prog2, trials=n_samples)
        self.assertTrue(1 in results2[0])
        self.assertTrue(0 in results2[0])

        qulacs_circuit = convert_circuit_to_qulacs(circuit1)
        self.assertEqual(qulacs_circuit.get_gate_count(), 3)
        self.assertEqual(qulacs_circuit.get_gate(2).get_name(), "Pauli-rotation")

        for backend in self.backends:
            backend.n_samples = n_samples
            measurements = backend.run_circuit_and_measure(circuit1)
            counts = measurements.get_counts()
            self.assertEqual(counts['00'], 1000)


        for backend in self.backends:
            backend.n_samples = n_samples
            measurements = backend.run_circuit_and_measure(circuit2)
            counts = measurements.get_counts()
            self.assertTrue(counts['00'] > 0)
            self.assertTrue(counts['11'] > 0)

    def test_gate_YY(self):
        def_gate, gate = YY(0, 0, 1)
        self.assertEqual(gate.name, "YY")
        self.assertEqual(len(gate.qubits), 2)
        self.assertEqual(len(gate.params), 1)
        self.assertEqual(def_gate.name, "YY")

    def test_append_circuit_YY(self):
        # Given
        n_samples = 1000
        circuit = Circuit(Program(H(0), CNOT(0, 1), YY(np.pi, 0, 1)))
        # When
        qulacs_circuit = convert_circuit_to_qulacs(circuit)
        self.assertEqual(qulacs_circuit.get_gate_count(), 3)
        self.assertEqual(qulacs_circuit.get_gate(2).get_name(), "Pauli-rotation")

        for backend in self.backends:
            backend.n_samples = n_samples
            measurements = backend.run_circuit_and_measure(circuit)
            counts = measurements.get_counts()
            self.assertTrue(counts['00'] > 0)
            self.assertTrue(counts['11'] > 0)

    def test_gate_ZZ(self):
        def_gate, gate = ZZ(0, 0, 1)
        self.assertEqual(gate.name, "ZZ")
        self.assertEqual(len(gate.qubits), 2)
        self.assertEqual(len(gate.params), 1)
        self.assertEqual(def_gate.name, "ZZ")    

    def test_append_circuit_ZZ(self):
        # Given
        n_samples = 1000
        circuit = Circuit(Program(H(0), CNOT(0, 1), ZZ(np.pi, 0, 1)))
        # When
        qulacs_circuit = convert_circuit_to_qulacs(circuit)
        self.assertEqual(qulacs_circuit.get_gate_count(), 3)
        self.assertEqual(qulacs_circuit.get_gate(2).get_name(), "Pauli-rotation")

        for backend in self.backends:
            backend.n_samples = n_samples
            measurements = backend.run_circuit_and_measure(circuit)
            counts = measurements.get_counts()
            self.assertTrue(counts['00'] > 0)
            self.assertTrue(counts['11'] > 0)
