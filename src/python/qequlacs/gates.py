"""The purpose of this module is to add wrapper/substitution classes
for gates in Pyquil:
 * XX - XX=X⊗X
 * YY - YY=Y⊗Y
 * ZZ - ZZ=Z⊗Z
"""
import numpy as np

from pyquil.quilatom import (
    Addr,
    Expression,
    MemoryReference,
    MemoryReferenceDesignator,
    ParameterDesignator,
    QubitDesignator,
    unpack_classical_reg,
    unpack_qubit,
)

from pyquil.quil import DefGate
from pyquil.quilatom import Parameter, quil_sin, quil_cos, quil_exp
from pyquil.quilbase import (
    AbstractInstruction,
    Gate
)


def XX(angle: ParameterDesignator, q1: QubitDesignator, q2: QubitDesignator):
    """Produces a XX gate which is the tensor product of X with X such as XX=X⊗X::

        XX(phi) = [[cos(phi / 2), 0, 0, -1j * sin(phi / 2)],
                   [0, cos(phi / 2), -1j * sin(phi / 2), 0],
                   [0, -1j * sin(phi / 2), cos(phi / 2), 0],
                   [-1j * sin(phi / 2), 0, 0, cos(phi / 2)]]

    Args:
        angle: The angle to rotate around the x-axis on the bloch sphere.
        q1: Qubit 1.
        q2: Qubit 2.
    Returns:
        A Gate object.

    Same as: RXX in Qiskit; XXPowGate in Cirq

    Test::
        import numpy as np
        from qequlacs.gates import XX
        from pyquil import Program, get_qc
        from pyquil.gates import *
        qvm = get_qc('9q-square-qvm')
        prog = Program(X(0), CNOT(0, 1), XX(np.pi, 0, 1))
        results = qvm.run_and_measure(prog, trials=10)
    """

    # Gate definition from the matrix
    # https://github.com/rigetti/pyquil/blob/master/docs/source/basics.rst#defining-parametric-gates
    theta = Parameter('theta')
    xx = np.array([[quil_cos(theta / 2), 0, 0, -1j * quil_sin(theta / 2)],
                   [0, quil_cos(theta / 2), -1j * quil_sin(theta / 2), 0],
                   [0, -1j * quil_sin(theta / 2), quil_cos(theta / 2), 0],
                   [-1j * quil_sin(theta / 2), 0, 0, quil_cos(theta / 2)]
    ])

    DefXX = DefGate('XX', xx, [theta])
    _XX = DefXX.get_constructor()
    return [DefXX, _XX(angle)(q1, q2)]


def YY(angle: ParameterDesignator, q1: QubitDesignator, q2: QubitDesignator):
    """Produces a YY gate which is the tensor product of Y with Y such as YY=Y⊗Y::

        YY(phi) = [[cos(phi / 2), 0, 0, 1j * sin(phi / 2)],
                   [0, cos(phi / 2), -1j * sin(phi / 2), 0],
                   [0, -1j * sin(phi / 2), cos(phi / 2), 0],
                   [1j * sin(phi / 2), 0, 0, cos(phi / 2)]]

    Args:
        angle: The angle to rotate around the y-axis on the bloch sphere.
        q1: Qubit 1.
        q2: Qubit 2.
    Returns:
        A Gate object.

    Same as: RYY in Qiskit; YYPowGate in Cirq

    Test::
        from qequlacs.gates import YY
        from pyquil import Program, get_qc
        from pyquil.gates import *
        qvm = get_qc('9q-square-qvm')
        prog = Program(X(0), CNOT(0, 1), YY(0, 0, 1))
        results = qvm.run_and_measure(prog, trials=10)
    """

    theta = Parameter('theta')
    yy = np.array([[quil_cos(theta / 2), 0, 0, 1j * quil_sin(theta / 2)],
                   [0, quil_cos(theta / 2), -1j * quil_sin(theta / 2), 0],
                   [0, -1j * quil_sin(theta / 2), quil_cos(theta / 2), 0],
                   [1j * quil_sin(theta / 2), 0, 0, quil_cos(theta / 2)]
    ])

    DefYY = DefGate('YY', yy, [theta])
    _YY = DefYY.get_constructor()
    return [DefYY, _YY(angle)(q1, q2)]


def ZZ(angle: ParameterDesignator, q1: QubitDesignator, q2: QubitDesignator):
    """Produces a ZZ gate which is the tensor product of Z with Z such as ZZ=Z⊗Z::

        ZZ(phi) = [[exp(-1j * phi /2), 0, 0, 0],
                   [0, exp(1j * phi /2), 0, 0],
                   [0, 0, exp(1j * phi /2), 0],
                   [0, 0, 0, exp(-1j * phi /2)]]

    Args:
        angle: The angle to rotate around the z-axis on the bloch sphere.
        q1: Qubit 1.
        q2: Qubit 2.
    Returns:
        A Gate object.

    Same as: RZZ in Qiskit; ZZPowGate in Cirq

    Test::
        from qequlacs.gates import ZZ
        from pyquil import Program, get_qc
        from pyquil.gates import *
        qvm = get_qc('9q-square-qvm')
        prog = Program(X(0), CNOT(0, 1), ZZ(0, 0, 1))
        results = qvm.run_and_measure(prog, trials=10)
    """

    theta = Parameter('theta')
    zz = np.array([[quil_exp(-1j * theta / 2), 0, 0, 0],
                   [0, quil_exp(1j * theta / 2), 0, 0],
                   [0, 0, quil_exp(1j * theta / 2), 0],
                   [0, 0, 0, quil_exp(-1j * theta / 2)]
    ])

    DefZZ = DefGate('ZZ', zz, [theta])
    _ZZ = DefZZ.get_constructor()
    return [DefZZ, _ZZ(angle)(q1, q2)]
