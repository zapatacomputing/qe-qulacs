from .simulator import QulacsSimulator
import unittest
from zquantum.core.interfaces.backend_test import QuantumSimulatorTests

class TestQulacs(unittest.TestCase, QuantumSimulatorTests):

    def setUp(self):
        self.backends = [QulacsSimulator(n_samples=None)]
        self.wf_simulators = [QulacsSimulator(n_samples=None)]
