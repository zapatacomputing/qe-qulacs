import pytest
from qequlacs.simulator import QulacsSimulator
from zquantum.core import circuits
from zquantum.core.interfaces.backend_test import (
    QuantumSimulatorTests,
    QuantumSimulatorGatesTest,
)

import numpy as np


@pytest.fixture
def backend():
    return QulacsSimulator()


@pytest.fixture
def wf_simulator():
    return QulacsSimulator()


class TestQulacs(QuantumSimulatorTests):
    @pytest.mark.parametrize(
        "circuit, target_wavefunction",
        [
            (
                circuits.Circuit(
                    [
                        circuits.H(0),
                        circuits.H(1),
                        circuits.MultiPhaseOperation([-0.1, 0.3, -0.5, 0.7]),
                        circuits.X(0),
                        circuits.X(0),
                    ]
                ),
                np.exp(1j * np.array([-0.1, 0.3, -0.5, 0.7])) / 2,
            ),
            (
                circuits.Circuit(
                    [
                        circuits.H(0),
                        circuits.H(1),
                        circuits.MultiPhaseOperation([-0.1, 0.3, -0.5, 0.7]),
                        circuits.MultiPhaseOperation([-0.2, 0.1, -0.2, -0.3]),
                        circuits.X(0),
                        circuits.X(0),
                    ]
                ),
                np.exp(1j * np.array([-0.3, 0.4, -0.7, 0.4])) / 2,
            ),
            (
                circuits.Circuit(
                    [
                        circuits.MultiPhaseOperation([-0.1, 0.3, -0.5, 0.7]),
                    ]
                ),
                np.array([np.exp(-0.1j), 0, 0, 0]),
            ),
            (
                circuits.Circuit(
                    [
                        circuits.H(0),
                        circuits.MultiPhaseOperation([-0.1, 0.3, -0.5, 0.7]),
                    ]
                ),
                np.array([np.exp(-0.1j), 0, np.exp(-0.5j), 0]) / np.sqrt(2),
            ),
        ],
    )
    def test_get_wavefunction_works_with_multiphase_operator(
        self, backend, circuit, target_wavefunction
    ):
        wavefunction = backend.get_wavefunction(circuit)

        np.testing.assert_almost_equal(wavefunction.amplitudes, target_wavefunction)

    def test_run_circuit_and_measure_works_with_multiphase_operator(self, backend):
        params = [-0.1, 0.3, -0.5, 0.7]
        circuit = circuits.Circuit(
            [circuits.H(0), circuits.X(1), circuits.MultiPhaseOperation(params)]
        )

        measurements = backend.run_circuit_and_measure(circuit, n_samples=1000)

        assert len(measurements.bitstrings) == 1000
        assert all(
            bitstring in [(0, 1), (1, 1)] for bitstring in measurements.bitstrings
        )

    def test_get_wavefunction_uses_provided_initial_state(self):
        circuit = circuits.Circuit([circuits.H(0), circuits.H(1)])
        initial_state = np.array([0, 1, 0, 0])
        simulator = QulacsSimulator()
        np.testing.assert_allclose(
            simulator.get_wavefunction(circuit, initial_state=initial_state),
            np.array([0.5, -0.5, 0.5, -0.5])
        )
        np.testing.assert_allclose(
            simulator.get_wavefunction(circuit),
            0.5 * np.ones(4)
        )


class TestQulacsGates(QuantumSimulatorGatesTest):
    pass
