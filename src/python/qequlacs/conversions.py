import qulacs
from zquantum.core.wip import circuits
import numpy as np


def _identity(x):
    return x


def _negate(x):
    return -x


def _negate_and_double(x):
    return -x


def _no_params(*args, **kwargs):
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
        gate_name: (_gate_factory_from_pauli_rotation([ax, ax]), _negate_and_double)
        for ax, gate_name in enumerate(["XX", "YY", "ZZ"], start=1)
    },
    "XY": (_gate_factory_from_pauli_rotation([1, 2]), _negate_and_double),
    # custom gates
    # TODO: add CPHASE
}


def _qulacs_gate(operation: circuits.GateOperation):
    try:
        qulacs_gate_factory, param_transform = ZQUANTUM_TO_QULACS_GATES[operation.gate.name]
    except KeyError:
        return _custom_qulacs_gate(operation)

    return qulacs_gate_factory(
        *operation.qubit_indices, *map(param_transform, operation.gate.params)
    )


def _custom_qulacs_gate(operation: circuits.GateOperation):
    matrix = operation.gate.matrix
    dense_matrix = np.array(matrix, dtype=complex)
    return qulacs.gate.DenseMatrix(list(operation.qubit_indices), dense_matrix)


def convert_to_qulacs(circuit: circuits.Circuit):
    qulacs_circuit = qulacs.QuantumCircuit(circuit.n_qubits)
    for operation in circuit.operations:
        qulacs_circuit.add_gate(_qulacs_gate(operation))

    return qulacs_circuit
