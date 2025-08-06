# Copyright © 2024 HQS Quantum Simulations GmbH. All Rights Reserved.
"""Test everything."""

import pytest
from typing import Any, List
from qoqo_tket.qoqo_tket import (
    QoqoTketBackend,
)
import numpy as np
from qoqo import Circuit, CircuitDag, QuantumProgram
from qoqo.measurements import (  # type:ignore
    PauliZProduct,
    PauliZProductInput,
    ClassicalRegister,
    CheatedPauliZProduct,
    CheatedPauliZProductInput,
    Cheated,
    CheatedInput,
)
from qoqo import operations as ops  # type: ignore
from pytket.extensions.projectq import ProjectQBackend
from pytket.extensions.qiskit import AerBackend
from pytket.circuit import BasisOrder


def test_backend_error() -> None:
    """Test for errors when creating a backend"""
    with pytest.raises(TypeError) as exc:
        backend = QoqoTketBackend("error")
    assert "The input is not a valid Tket Backend instance." in str(exc.value)


def test_compile_qoqo_tket() -> None:
    """Test compiling with qoqo_tket."""
    circuit = Circuit()
    circuit += ops.Identity(0)
    circuit += ops.PauliX(0)

    circuit_res = Circuit()
    circuit_res += ops.RotateX(0, 3.141592653589793)

    backend = ProjectQBackend()
    tket_backend = QoqoTketBackend(backend)
    compiled_circuit = tket_backend.compile_circuit(circuit)
    assert compiled_circuit == circuit_res


def test_compile_complex_qoqo_tket() -> None:
    """Test compiling with qoqo_tket."""
    circuit = Circuit()
    circuit += ops.Hadamard(0)
    circuit += ops.CNOT(0, 1)
    circuit += ops.PauliX(1)
    circuit += ops.CNOT(1, 2)
    circuit += ops.PauliZ(2)

    circuit_res = Circuit()
    circuit_res += ops.RotateZ(0, 10.995574287564276)
    circuit_res += ops.RotateX(0, 4.71238898038469)
    circuit_res += ops.RotateZ(0, 1.5707963267948966)
    circuit_res += ops.RotateZ(1, 9.42477796076938)
    circuit_res += ops.RotateX(1, 3.141592653589793)
    circuit_res += ops.RotateZ(2, 3.141592653589793)
    circuit_res += ops.CNOT(0, 1)
    circuit_res += ops.CNOT(1, 2)

    backend = ProjectQBackend()
    tket_backend = QoqoTketBackend(backend)
    compiled_circuit = tket_backend.compile_circuit(circuit)
    compiled_circuit_dag = CircuitDag()
    circuit_res_dag = CircuitDag()
    compiled_circuit_dag = compiled_circuit_dag.from_circuit(compiled_circuit)
    circuit_res_dag = circuit_res_dag.from_circuit(circuit_res)
    assert compiled_circuit_dag == circuit_res_dag


def test_compile_multiple_qoqo_tket() -> None:
    """Test compiling with qoqo_tket."""
    circuit = Circuit()
    circuit += ops.Identity(0)
    circuit += ops.PauliX(0)

    circuit_res = Circuit()
    circuit_res += ops.RotateX(0, 3.141592653589793)

    circuit_2 = Circuit()
    circuit_2 += ops.Hadamard(0)
    circuit_2 += ops.CNOT(0, 1)
    circuit_2 += ops.PauliX(1)
    circuit_2 += ops.CNOT(1, 2)
    circuit_2 += ops.PauliZ(2)

    circuit_res_2 = Circuit()
    circuit_res_2 += ops.RotateZ(0, 10.995574287564276)
    circuit_res_2 += ops.RotateX(0, 4.71238898038469)
    circuit_res_2 += ops.RotateZ(0, 1.5707963267948966)
    circuit_res_2 += ops.RotateZ(1, 9.42477796076938)
    circuit_res_2 += ops.RotateX(1, 3.141592653589793)
    circuit_res_2 += ops.RotateZ(2, 3.141592653589793)
    circuit_res_2 += ops.CNOT(0, 1)
    circuit_res_2 += ops.CNOT(1, 2)

    backend = ProjectQBackend()
    tket_backend = QoqoTketBackend(backend)
    compiled_circuits = tket_backend.compile_circuit([circuit, circuit_2])

    compiled_circuit_dag = CircuitDag()
    circuit_res_dag = CircuitDag()
    compiled_circuit_dag = compiled_circuit_dag.from_circuit(compiled_circuits[1])
    circuit_res_dag = circuit_res_dag.from_circuit(circuit_res_2)

    assert compiled_circuits[0] == circuit_res and compiled_circuit_dag == circuit_res_dag


def test_run_qoqo_tket() -> None:
    """Test compiling with qoqo_tket."""
    circuit = Circuit()
    circuit += ops.PauliX(0)
    circuit += ops.PragmaGetStateVector("statevector", Circuit())

    state_res = [0, 1]

    backend = ProjectQBackend()
    tket_backend = QoqoTketBackend(backend)
    results = tket_backend.run_circuit(circuit)

    assert np.isclose(results[2]["statevector"][0], state_res, atol=1e-5).all()


def test_run_complex_qoqo_tket() -> None:
    """Test compiling with qoqo_tket."""
    circuit = Circuit()
    circuit += ops.Hadamard(0)
    circuit += ops.CNOT(0, 1)
    circuit += ops.PauliX(1)
    circuit += ops.CNOT(1, 2)
    circuit += ops.PauliZ(2)
    circuit += ops.PragmaGetStateVector("statevector", Circuit())
    state_res = [0, 0, 0, -1 / np.sqrt(2), 1 / np.sqrt(2), 0, 0, 0]

    backend = ProjectQBackend()
    tket_backend = QoqoTketBackend(backend)
    results = tket_backend.run_circuit(circuit)
    assert np.isclose(results[2]["statevector"][0], state_res, atol=1e-5).all()


def test_run_multiple_qoqo_tket() -> None:
    """Test compiling with qoqo_tket."""
    circuit = Circuit()
    circuit += ops.PauliX(0)
    circuit += ops.PragmaGetStateVector("psi", Circuit())

    state_res = [0, 1]

    circuit_2 = Circuit()
    circuit_2 += ops.Hadamard(0)
    circuit_2 += ops.CNOT(0, 1)
    circuit_2 += ops.PauliX(1)
    circuit_2 += ops.CNOT(1, 2)
    circuit_2 += ops.PauliZ(2)
    circuit_2 += ops.PragmaGetStateVector("psi2", Circuit())

    state_res_2 = [0, 0, 0, -1 / np.sqrt(2), 1 / np.sqrt(2), 0, 0, 0]

    backend = ProjectQBackend()
    tket_backend = QoqoTketBackend(backend)
    results = tket_backend.run_circuit([circuit, circuit_2])
    assert (
        np.isclose(results[0][2]["psi"][0], state_res, atol=1e-5).all()
        and np.isclose(results[1][2]["psi2"][0], state_res_2, atol=1e-5).all()
    )


def assert_quantum_program_equal(
    quantum_program_1: QuantumProgram, quantum_program2: QuantumProgram
) -> None:
    """Assert that two quantum programs are equal.

    Args:
        quantum_program_1 (QuantumProgram): quantum program
        quantum_program2 (QuantumProgram): quantum program

    Raises:
        AssertionError: if the quantum programs are not equal
    """
    assert quantum_program_1.input_parameter_names() == quantum_program2.input_parameter_names()
    if not isinstance(quantum_program_1.measurement(), ClassicalRegister):
        assert quantum_program_1.measurement().input() == quantum_program2.measurement().input()
    assert (
        quantum_program_1.measurement().constant_circuit()
        == quantum_program2.measurement().constant_circuit()
    )
    for circuit_1, circuit_2 in zip(
        quantum_program_1.measurement().circuits(),
        quantum_program2.measurement().circuits(),
    ):
        circuit_dag_1 = CircuitDag()
        circuit_dag_2 = CircuitDag()
        circuit_dag_1 = circuit_dag_1.from_circuit(circuit_1)
        circuit_dag_2 = circuit_dag_2.from_circuit(circuit_2)
        assert circuit_dag_1 == circuit_dag_2


def test_quantum_program() -> None:
    """Test basic program conversion with a BaseGates transpiler."""
    circuit_1 = Circuit()
    circuit_1 += ops.PauliX(0)
    circuit_1 += ops.Identity(0)

    circuit_res_1 = Circuit()
    circuit_res_1 += ops.RotateX(0, 3.141592653589793)

    measurement_input = CheatedPauliZProductInput()
    measurement = CheatedPauliZProduct(
        constant_circuit=None, circuits=[circuit_1], input=measurement_input
    )
    measurement_res = CheatedPauliZProduct(
        constant_circuit=None,
        circuits=[circuit_res_1],
        input=measurement_input,
    )
    quantum_program = QuantumProgram(measurement=measurement, input_parameter_names=["x"])
    quantum_program_res = QuantumProgram(measurement=measurement_res, input_parameter_names=["x"])

    backend = ProjectQBackend()
    tket_backend = QoqoTketBackend(backend)
    transpiled_program = tket_backend.compile_program(quantum_program)

    assert_quantum_program_equal(transpiled_program, quantum_program_res)


def test_quantum_program_cheated() -> None:
    """Test basic program conversion with a BaseGates transpiler."""
    circuit_1 = Circuit()
    circuit_1 += ops.PauliX(0)
    circuit_1 += ops.Identity(0)

    circuit_res_1 = Circuit()
    circuit_res_1 += ops.RotateX(0, 3.141592653589793)

    measurement_input = CheatedInput(1)
    measurement = Cheated(constant_circuit=None, circuits=[circuit_1], input=measurement_input)
    measurement_res = Cheated(
        constant_circuit=None,
        circuits=[circuit_res_1],
        input=measurement_input,
    )
    quantum_program = QuantumProgram(measurement=measurement, input_parameter_names=["x"])
    quantum_program_res = QuantumProgram(measurement=measurement_res, input_parameter_names=["x"])

    backend = ProjectQBackend()
    tket_backend = QoqoTketBackend(backend)
    transpiled_program = tket_backend.compile_program(quantum_program)

    assert_quantum_program_equal(transpiled_program, quantum_program_res)


def test_quantum_program_no_constant_circuit() -> None:
    """Test basic program conversion with a BaseGates transpiler."""
    circuit_1 = Circuit()
    circuit_1 += ops.PauliX(0)
    circuit_1 += ops.Identity(0)

    circuit_res_1 = Circuit()
    circuit_res_1 += ops.RotateX(0, 3.141592653589793)

    circuit_2 = Circuit()
    circuit_2 += ops.Hadamard(0)
    circuit_2 += ops.CNOT(0, 1)
    circuit_2 += ops.PauliX(1)
    circuit_2 += ops.CNOT(1, 2)
    circuit_2 += ops.PauliZ(2)

    circuit_res_2 = Circuit()
    circuit_res_2 += ops.RotateZ(0, 10.995574287564276)
    circuit_res_2 += ops.RotateX(0, 4.71238898038469)
    circuit_res_2 += ops.RotateZ(0, 1.5707963267948966)
    circuit_res_2 += ops.RotateZ(1, 9.42477796076938)
    circuit_res_2 += ops.RotateX(1, 3.141592653589793)
    circuit_res_2 += ops.RotateZ(2, 3.141592653589793)
    circuit_res_2 += ops.CNOT(0, 1)
    circuit_res_2 += ops.CNOT(1, 2)

    measurement_input = PauliZProductInput(1, False)
    measurement = PauliZProduct(
        constant_circuit=None,
        circuits=[circuit_1, circuit_2],
        input=measurement_input,
    )
    measurement_res = PauliZProduct(
        constant_circuit=None,
        circuits=[circuit_res_1, circuit_res_2],
        input=measurement_input,
    )
    quantum_program = QuantumProgram(measurement=measurement, input_parameter_names=["x"])
    quantum_program_res = QuantumProgram(measurement=measurement_res, input_parameter_names=["x"])

    backend = ProjectQBackend()
    tket_backend = QoqoTketBackend(backend)
    transpiled_program = tket_backend.compile_program(quantum_program)

    assert_quantum_program_equal(transpiled_program, quantum_program_res)


def test_quantum_program_with_constant_circuit() -> None:
    """Test basic program conversion with a BaseGates transpiler."""
    constant_circuit = Circuit()
    constant_circuit += ops.Hadamard(0)
    constant_circuit += ops.Hadamard(1)

    circuit_1 = Circuit()
    circuit_1 += ops.PauliX(0)
    circuit_1 += ops.Identity(0)

    circuit_res_1 = Circuit()
    circuit_res_1 += ops.RotateZ(0, 10.995574287564276)
    circuit_res_1 += ops.RotateX(0, 1.5707963267948966)
    circuit_res_1 += ops.RotateZ(0, 1.5707963267948966)
    circuit_res_1 += ops.RotateZ(1, 1.5707963267948966)
    circuit_res_1 += ops.RotateX(1, 1.5707963267948966)
    circuit_res_1 += ops.RotateZ(1, 1.5707963267948966)

    circuit_2 = Circuit()
    circuit_2 += ops.Hadamard(0)
    circuit_2 += ops.CNOT(0, 1)
    circuit_2 += ops.PauliX(1)
    circuit_2 += ops.CNOT(1, 2)
    circuit_2 += ops.PauliZ(2)

    circuit_res_2 = Circuit()
    circuit_res_2 += ops.RotateZ(0, 3.141592653589793)
    circuit_res_2 += ops.RotateZ(1, 1.5707963267948966)
    circuit_res_2 += ops.RotateX(1, 4.71238898038469)
    circuit_res_2 += ops.RotateZ(1, 1.5707963267948966)
    circuit_res_2 += ops.RotateZ(2, 3.141592653589793)
    circuit_res_2 += ops.CNOT(0, 1)
    circuit_res_2 += ops.CNOT(1, 2)

    measurement = ClassicalRegister(
        constant_circuit=constant_circuit, circuits=[circuit_1, circuit_2]
    )
    measurement_res = ClassicalRegister(
        constant_circuit=None,
        circuits=[circuit_res_1, circuit_res_2],
    )
    quantum_program = QuantumProgram(measurement=measurement, input_parameter_names=["x"])
    quantum_program_res = QuantumProgram(measurement=measurement_res, input_parameter_names=["x"])

    backend = ProjectQBackend()
    tket_backend = QoqoTketBackend(backend)
    transpiled_program = tket_backend.compile_program(quantum_program)

    assert_quantum_program_equal(transpiled_program, quantum_program_res)


def test_run_program() -> None:
    """Test QoqoTketBackend.run_program method."""
    backend = QoqoTketBackend()

    init_circuit = Circuit()
    init_circuit += ops.RotateX(0, "angle_0")
    init_circuit += ops.RotateY(0, "angle_1")

    z_circuit = Circuit()
    z_circuit += ops.DefinitionBit("ro_z", 1, is_output=True)
    z_circuit += ops.PragmaRepeatedMeasurement("ro_z", 1000, None)

    x_circuit = Circuit()
    x_circuit += ops.DefinitionBit("ro_x", 1, is_output=True)
    x_circuit += ops.Hadamard(0)
    x_circuit += ops.PragmaRepeatedMeasurement("ro_x", 1000, None)

    measurement_input = PauliZProductInput(1, False)
    z_basis_index = measurement_input.add_pauliz_product(
        "ro_z",
        [
            0,
        ],
    )
    x_basis_index = measurement_input.add_pauliz_product(
        "ro_x",
        [
            0,
        ],
    )
    measurement_input.add_linear_exp_val(
        "<H>",
        {x_basis_index: 0.1, z_basis_index: 0.2},
    )

    measurement = PauliZProduct(
        constant_circuit=init_circuit,
        circuits=[z_circuit, x_circuit],
        input=measurement_input,
    )

    program = QuantumProgram(
        measurement=measurement,
        input_parameter_names=["angle_0", "angle_1"],
    )

    res = backend.run_program(
        program=program,
        params_values=[[0.785, 0.238], [0.234, 0.653], [0.875, 0.612]],
    )

    assert len(res) == 3
    for el in res:
        assert float(el["<H>"])

    init_circuit += ops.DefinitionBit("ro", 1, True)
    init_circuit += ops.PragmaRepeatedMeasurement("ro", 1000, None)

    measurement = ClassicalRegister(constant_circuit=None, circuits=[init_circuit, init_circuit])

    program = QuantumProgram(measurement=measurement, input_parameter_names=["angle_0", "angle_1"])

    res = backend.run_program(
        program=program,
        params_values=[[0.785, 0.238], [0.234, 0.653], [0.875, 0.612]],
    )

    assert len(res) == 3
    assert res[0][0]
    assert not res[0][1]
    assert not res[0][2]

    measurement = ClassicalRegister(
        constant_circuit=None,
        circuits=[z_circuit, x_circuit],
    )
    program = QuantumProgram(measurement=measurement, input_parameter_names=[])
    res = backend.run_program(program=program, params_values=[])

    assert len(res) == 1
    assert res[0][0]["ro_z"]
    assert res[0][0]["ro_x"]
    assert not res[0][1]
    assert not res[0][2]

    measurement = PauliZProduct(
        constant_circuit=None,
        circuits=[z_circuit, x_circuit],
        input=measurement_input,
    )
    program = QuantumProgram(measurement=measurement, input_parameter_names=[])
    res = backend.run_program(program=program, params_values=[])

    assert len(res) == 1
    assert float(res[0]["<H>"])


@pytest.mark.parametrize(
    "operations",
    [
        [
            ops.PauliX(1),
            ops.PauliX(0),
            ops.PauliZ(2),
            ops.PauliX(3),
            ops.PauliY(4),
        ],
        [
            ops.Hadamard(0),
            ops.CNOT(0, 1),
            ops.CNOT(1, 2),
            ops.CNOT(2, 3),
            ops.CNOT(3, 4),
        ],
        [ops.RotateX(0, 0.23), ops.RotateY(1, 0.12), ops.RotateZ(2, 0.34)],
    ],
)
def test_compile_circuit_errors(operations: List[Any]) -> None:
    """Test QoqoTketBackend.run_circuit method errors."""
    backend = QoqoTketBackend()

    with pytest.raises(TypeError) as exc:
        _ = backend.compile_circuit("error")
    assert "The input is not a valid Qoqo Circuit instance." in str(exc.value)


@pytest.mark.parametrize(
    "operations",
    [
        [
            ops.PauliX(1),
            ops.PauliX(0),
            ops.PauliZ(2),
            ops.PauliX(3),
            ops.PauliY(4),
        ],
        [
            ops.Hadamard(0),
            ops.CNOT(0, 1),
            ops.CNOT(1, 2),
            ops.CNOT(2, 3),
            ops.CNOT(3, 4),
        ],
        [ops.RotateX(0, 0.23), ops.RotateY(1, 0.12), ops.RotateZ(2, 0.34)],
    ],
)
def test_run_circuit_errors(operations: List[Any]) -> None:
    """Test QoqoTketBackend.run_circuit method errors."""
    backend = QoqoTketBackend()

    with pytest.raises(TypeError) as exc:
        _ = backend.run_circuit("error")
    assert "The input is not a valid Qoqo Circuit instance." in str(exc.value)


@pytest.mark.parametrize(
    "operations",
    [
        [
            ops.PauliX(1),
            ops.PauliX(0),
            ops.PauliZ(2),
            ops.PauliX(3),
            ops.PauliY(4),
        ],
        [
            ops.Hadamard(0),
            ops.CNOT(0, 1),
            ops.CNOT(1, 2),
            ops.CNOT(2, 3),
            ops.CNOT(3, 4),
        ],
        [ops.RotateX(0, 0.23), ops.RotateY(1, 0.12), ops.RotateZ(2, 0.34)],
    ],
)
def test_run_circuit_results(operations: List[Any]) -> None:
    """Test QoqoTketBackend.run_circuit method results."""
    backend = QoqoTketBackend()
    backend_state = QoqoTketBackend(ProjectQBackend())

    circuit = Circuit()
    involved_qubits = set()
    for op in operations:
        involved_qubits.update(op.involved_qubits())
        circuit += op

    circuit_1 = Circuit()
    circuit_1 += circuit
    circuit_1 += ops.DefinitionBit("ri", len(involved_qubits), True)
    circuit_1 += ops.PragmaRepeatedMeasurement("ri", 10)

    result = backend.run_circuit(circuit_1)

    assert result[0]
    assert result[0]["ri"]
    assert not result[1]
    assert not result[2]

    circuit_2 = Circuit()
    circuit_2 += circuit
    circuit_2 += ops.DefinitionComplex("ri", len(involved_qubits), True)
    circuit_2 += ops.PragmaGetStateVector("ri", None)

    result = backend_state.run_circuit(circuit_2)

    assert not result[0]
    assert not result[1]
    assert result[2]
    assert result[2]["ri"]
    assert len(result[2]["ri"][0]) == 2 ** len(involved_qubits)

    circuit_3 = Circuit()
    circuit_3 += circuit
    circuit_3 += ops.DefinitionComplex("ri", len(involved_qubits), True)
    circuit_3 += ops.PragmaGetDensityMatrix("ri", None)


@pytest.mark.parametrize(
    "operations",
    [
        [
            ops.PauliX(1),
            ops.PauliX(0),
            ops.PauliZ(2),
            ops.PauliX(3),
            ops.PauliY(4),
        ],
        [
            ops.Hadamard(0),
            ops.CNOT(0, 1),
            ops.CNOT(1, 2),
            ops.CNOT(2, 3),
            ops.CNOT(3, 4),
        ],
        [ops.RotateX(0, 0.23), ops.RotateY(1, 0.12), ops.RotateZ(2, 0.34)],
    ],
)
def test_measurement_register_classicalregister(operations: List[Any]) -> None:
    """Test QoqoTketBackend.run_measurement_registers method classical registers."""
    backend = QoqoTketBackend()

    circuit = Circuit()
    involved_qubits = set()
    for op in operations:
        involved_qubits.update(op.involved_qubits())
        circuit += op

    circuit += ops.DefinitionBit("ri", len(involved_qubits), True)
    circuit += ops.PragmaRepeatedMeasurement("ri", 10)

    measurement = ClassicalRegister(constant_circuit=None, circuits=[circuit])

    try:
        output = backend.run_measurement_registers(measurement=measurement)
    except Exception:
        AssertionError()

    assert output[0]["ri"]
    assert len(output[0]["ri"][0]) == len(involved_qubits)
    assert not output[1]
    assert not output[2]


@pytest.mark.parametrize(
    "operations",
    [
        [
            ops.PauliX(1),
            ops.PauliX(0),
            ops.PauliZ(2),
            ops.PauliX(3),
            ops.PauliY(4),
        ],
        [
            ops.Hadamard(0),
            ops.CNOT(0, 1),
            ops.CNOT(1, 2),
            ops.CNOT(2, 3),
            ops.CNOT(3, 4),
        ],
        [ops.RotateX(0, 0.23), ops.RotateY(1, 0.12), ops.RotateZ(2, 0.34)],
    ],
)
def test_measurement(operations: List[Any]) -> None:
    """Test QoqoTketBackend.run_measurement method."""
    backend = QoqoTketBackend()

    circuit = Circuit()
    involved_qubits = set()
    for op in operations:
        involved_qubits.update(op.involved_qubits())
        circuit += op

    circuit += ops.DefinitionBit("ri", len(involved_qubits), True)
    circuit += ops.PragmaRepeatedMeasurement("ri", 10)

    pzpinput = PauliZProductInput(number_qubits=len(involved_qubits), use_flipped_measurement=True)

    measurement = PauliZProduct(constant_circuit=None, circuits=[circuit], input=pzpinput)

    try:
        _ = backend.run_measurement(measurement=measurement)
    except Exception:
        AssertionError()


@pytest.mark.parametrize(
    "operations",
    [
        [
            ops.PauliX(1),
            ops.PauliX(0),
            ops.PauliZ(2),
            ops.PauliX(3),
            ops.PauliY(4),
        ],
        [
            ops.Hadamard(0),
            ops.CNOT(0, 1),
            ops.CNOT(1, 2),
            ops.CNOT(2, 3),
            ops.CNOT(3, 4),
        ],
        [ops.RotateX(0, 0.23), ops.RotateY(1, 0.12), ops.RotateZ(2, 0.34)],
    ],
)
def test_measurement_register_statevector(operations: List[Any]) -> None:
    """Test QoqoTketBackend.run_measurement_registers method classical registers."""
    backend = QoqoTketBackend(ProjectQBackend())

    circuit = Circuit()
    involved_qubits = set()
    for op in operations:
        involved_qubits.update(op.involved_qubits())
        circuit += op

    circuit += ops.DefinitionComplex("ri", len(involved_qubits), True)
    circuit += ops.PragmaGetStateVector("ri", None)

    measurement = ClassicalRegister(constant_circuit=None, circuits=[circuit])

    try:
        output = backend.run_measurement_registers(measurement=measurement)
    except Exception:
        AssertionError()

    assert not output[0]
    assert not output[1]
    assert output[2]["ri"]
    assert len(output[2]["ri"][0]) == 2 ** len(involved_qubits)


@pytest.mark.parametrize(
    "operations",
    [
        [
            ops.PauliX(1),
            ops.PauliX(0),
            ops.PauliZ(2),
            ops.PauliX(3),
            ops.PauliY(4),
        ],
        [
            ops.Hadamard(0),
            ops.CNOT(0, 1),
            ops.CNOT(1, 2),
            ops.CNOT(2, 3),
            ops.CNOT(3, 4),
        ],
        [ops.RotateX(0, 0.23), ops.RotateY(1, 0.12), ops.RotateZ(2, 0.34)],
    ],
)
def test_measurement_statevector(operations: List[Any]) -> None:
    """Test QoqoTketBackend.run_measurement method."""
    backend = QoqoTketBackend(ProjectQBackend())

    circuit = Circuit()
    involved_qubits = set()
    for op in operations:
        involved_qubits.update(op.involved_qubits())
        circuit += op

    circuit += ops.DefinitionComplex("ri", len(involved_qubits), True)
    circuit += ops.PragmaGetStateVector("ri", None)

    pzpinput = PauliZProductInput(number_qubits=len(involved_qubits), use_flipped_measurement=True)

    measurement = PauliZProduct(constant_circuit=None, circuits=[circuit], input=pzpinput)

    try:
        _ = backend.run_measurement(measurement=measurement)
    except Exception:
        AssertionError()
