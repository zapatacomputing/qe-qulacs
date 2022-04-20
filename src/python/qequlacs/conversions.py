################################################################################
# © Copyright 2021-2022 Zapata Computing Inc.
################################################################################
from numbers import Real

import numpy as np
import qulacs
from zquantum.core import circuits


def _identity(x):
    return x


def _negate(x):
    return -x


def _no_params(x):
    raise RuntimeError(
        "This gate isn't parametric, you shouldn't need to map its params"
    )


def _gate_factory_from_pauli_rotation(axes):
    def _factory(*args):
        qubit_indices = args[: len(axes)]
        params = args[len(axes) :]
        return qulacs.gate.PauliRotation(qubit_indices, axes, *params)

    return _factory


ZQUANTUM_TO_QULACS_GATES = {
    # 1-qubit, non-parametric
    "I": (qulacs.gate.Identity, _no_params),
    **{
        gate_name: (getattr(qulacs.gate, gate_name), _no_params)
        for gate_name in ["X", "Y", "Z", "H", "S", "T"]
    },
    # 1-qubit, parametric
    **{
        gate_name: (getattr(qulacs.gate, gate_name), _negate)
        for gate_name in ["RX", "RY", "RZ"]
    },
    "PHASE": (qulacs.gate.U1, _identity),
    # 2-qubit, non-parametric
    **{
        gate_name: (getattr(qulacs.gate, gate_name), _no_params)
        for gate_name in ["CNOT", "SWAP"]
    },
    # 2-qubit, parametric
    **{
        gate_name: (_gate_factory_from_pauli_rotation([ax, ax]), _negate)
        for ax, gate_name in enumerate(["XX", "YY", "ZZ"], start=1)
    },
}


def _make_cphase_gate(operation: circuits.GateOperation):
    matrix = np.diag([1.0, np.exp(1.0j * operation.gate.params[0])])  # type: ignore
    gate_to_add = qulacs.gate.DenseMatrix(operation.qubit_indices[1], matrix)
    gate_to_add.add_control_qubit(operation.qubit_indices[0], 1)
    return gate_to_add


GATE_SPECIAL_CASES = {
    "CPHASE": _make_cphase_gate,
}


def _qulacs_gate(operation: circuits.GateOperation):
    try:
        factory = GATE_SPECIAL_CASES[operation.gate.name]
        return factory(operation)
    except KeyError:
        pass

    try:
        qulacs_gate_factory, param_transform = ZQUANTUM_TO_QULACS_GATES[
            operation.gate.name
        ]
        return qulacs_gate_factory(
            *operation.qubit_indices, *map(param_transform, operation.params)
        )
    except KeyError:
        pass

    return _custom_qulacs_gate(operation)


def _custom_qulacs_gate(operation: circuits.GateOperation):
    matrix = operation.gate.matrix
    dense_matrix = np.array(matrix, dtype=complex)
    return qulacs.gate.DenseMatrix(list(operation.qubit_indices), dense_matrix)


def convert_to_qulacs(circuit: circuits.Circuit):
    qulacs_circuit = qulacs.QuantumCircuit(circuit.n_qubits)
    for operation in circuit.operations:
        qulacs_circuit.add_gate(_qulacs_gate(operation))

    return qulacs_circuit
