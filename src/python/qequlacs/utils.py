import qulacs
from qulacs.gate import PauliRotation
from zquantum.core.circuit import Circuit, Gate
import numpy as np


def convert_circuit_to_qulacs(circuit):
    qulacs_circuit = qulacs.QuantumCircuit(len(circuit.get_qubits()))
    for gate in circuit.gates:
        qulacs_circuit = append_gate(gate, qulacs_circuit)
    return qulacs_circuit


def append_gate(gate, qulacs_circuit):
    """
    This function is based on the `_try_append_gate` function from https://github.com/qulacs/cirq-qulacs/blob/master/cirqqulacs/qulacs_simulator.py .
    """
    # One qubit gate
    if len(gate.qubits) == 1:
        index = gate.qubits[0].index
        if gate.name == "I":
            qulacs_circuit.add_gate(qulacs.gate.Identity(index))
        elif gate.name == "X":
            qulacs_circuit.add_X_gate(index)
        elif gate.name == "Y":
            qulacs_circuit.add_Y_gate(index)
        elif gate.name == "Z":
            qulacs_circuit.add_Z_gate(index)
        elif gate.name == "H":
            qulacs_circuit.add_H_gate(index)
        elif gate.name == "S":
            qulacs_circuit.add_S_gate(index)
        elif gate.name == "T":
            qulacs_circuit.add_T_gate(index)
        elif gate.name == "Rx":
            qulacs_circuit.add_RX_gate(index, -gate.params[0])
        elif gate.name == "Ry":
            qulacs_circuit.add_RY_gate(index, -gate.params[0])
        elif gate.name == "Rz":
            qulacs_circuit.add_RZ_gate(index, -gate.params[0])
        elif gate.name == "PHASE":
            qulacs_circuit.add_U1_gate(index, gate.params[0])
        else:
            unitary_matrix = gate.to_unitary()
            qulacs_circuit.add_dense_matrix_gate(index, unitary_matrix)

    # Two qubit gate
    elif len(gate.qubits) == 2:
        index_1 = gate.qubits[0].index
        index_2 = gate.qubits[1].index
        if gate.name == "CNOT":
            qulacs_circuit.add_CNOT_gate(index_1, index_2)
        elif gate.name == "SWAP":
            qulacs_circuit.add_SWAP_gate(index_1, index_2)
        elif gate.name == "XX":
            gate_to_add = PauliRotation([index_1, index_2], [1, 1], -gate.params[0] * 2)
            qulacs_circuit.add_gate(gate_to_add)
        elif gate.name == "YY":
            gate_to_add = PauliRotation([index_1, index_2], [2, 2], -gate.params[0] * 2)
            qulacs_circuit.add_gate(gate_to_add)
        elif gate.name == "ZZ":
            gate_to_add = PauliRotation([index_1, index_2], [3, 3], -gate.params[0] * 2)
            qulacs_circuit.add_gate(gate_to_add)
        elif gate.name == "XY":
            cos = np.cos(gate.params[0] * 2)
            sin = -1j * np.sin(gate.params[0] * 2)
            mat = np.array(
                [[1.0, 0.0, 0.0, 0.0], [0, cos, sin, 0], [0, sin, cos, 0], [0, 0, 0, 1]]
            )
            gate_to_add = qulacs.gate.DenseMatrix([index_1, index_2], mat)
            qulacs_circuit.add_gate(gate_to_add)

        elif gate.name == "CPHASE":
            mat = np.diag([1.0, np.exp(1.0j * gate.params[0])])
            gate_to_add = qulacs.gate.DenseMatrix(index_2, mat)
            gate_to_add.add_control_qubit(index_1, 1)
            qulacs_circuit.add_gate(gate_to_add)
        else:
            unitary_matrix = gate.to_unitary()
            qulacs_circuit.add_dense_matrix_gate([index_1, index_2], unitary_matrix)
    else:
        n_qubits = len(gate.qubits)
        Exception(str(n_qubits) + "- qubit gates not supported.")
    return qulacs_circuit


def qubitop_to_qulacspauli(qubit_operator):
    qubit_operator_str = str(qubit_operator)
    qulacs_operator = (
        qulacs.quantum_operator.create_quantum_operator_from_openfermion_text(
            qubit_operator_str
        )
    )
    return qulacs_operator