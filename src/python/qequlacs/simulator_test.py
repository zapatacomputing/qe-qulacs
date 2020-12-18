import pytest
from .simulator import QulacsSimulator
from zquantum.core.interfaces.backend_test import QuantumSimulatorTests


@pytest.fixture(
    params=[
        {"n_samples": None},
        {"n_samples": 1000},
    ]
)
def backend(request):
    return QulacsSimulator(**request.param)


@pytest.fixture(
    params=[
        {"n_samples": None},
    ]
)
def wf_simulator(request):
    return QulacsSimulator(**request.param)


class TestQulacs(QuantumSimulatorTests):
    pass
