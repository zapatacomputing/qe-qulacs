import qulacs
from zquantum.core.wip import circuits


def _identity(x):
    return x


def _negate(x):
    return -x


def _no_params(*args, **kwargs):
    raise RuntimeError("This gate isn't parametric, you shouldn't need to map its params")


ZQUANTUM_TO_QULACS_GATES = {
    "I": (qulacs.gate.Identity, _no_params),
    **{
        gate_name: (getattr(qulacs.gate, gate_name), _no_params)
        for gate_name in ["X", "Y", "Z", "H", "S", "T"]
    },
    **{
        gate_name: (getattr(qulacs.gate, gate_name), _negate)
        for gate_name in ["RX", "RY", "RZ"]
    },
    "PHASE": (qulacs.gate.U1, _identity),
    # TODO: add two-qubit gates
    # TODO: add custom gates
}


def _qulacs_gate(operation: circuits.GateOperation):
    qulacs_gate_factory, param_transform = ZQUANTUM_TO_QULACS_GATES[operation.gate.name]
    return qulacs_gate_factory(
        *operation.qubit_indices, *map(param_transform, operation.gate.params)
    )


def convert_to_qulacs(circuit: circuits.Circuit):
    qulacs_circuit = qulacs.QuantumCircuit(circuit.n_qubits)
    for operation in circuit.operations:
        qulacs_circuit.add_gate(_qulacs_gate(operation))

    return qulacs_circuit
