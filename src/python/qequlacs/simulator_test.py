from .simulator import QulacsSimulator
import unittest
import numpy as np
from zquantum.core.circuit import Circuit
from zquantum.core.interfaces.backend_test import QuantumSimulatorTests
from openfermion.ops import QubitOperator, IsingOperator
from pyquil import Program
from pyquil.gates import H, CNOT, RX, CZ

class TestQulacs(unittest.TestCase, QuantumSimulatorTests):

    def setUp(self):
        self.backends = [QulacsSimulator(n_samples=None)]
        self.wf_simulators = [QulacsSimulator(n_samples=None)]
