# Copyright © 2024 HQS Quantum Simulations GmbH. All Rights Reserved.
# License details given in distributed LICENSE file.

"""package to compile and run qoqo programms with tket."""

from qoqo import Circuit, QuantumProgram
from qoqo_qasm import QasmBackend, qasm_str_to_circuit  # type: ignore
from pytket.qasm import circuit_from_qasm_str, circuit_to_qasm_str  # type: ignore
from pytket.backends import Backend  # type: ignore
from pytket.extensions.qiskit import AerBackend  # type: ignore
from typing import Any, Dict, List, Optional, Tuple, Union
from qoqo.measurements import (  # type:ignore
    PauliZProduct,
    ClassicalRegister,
    CheatedPauliZProduct,
    Cheated,
)


class QoqoTketBackend:
    """Run a Qoqo QuantumProgram or circuit  on a Tket backend."""

    def __init__(
        self,
        tket_backend: Optional[Union[Backend, AerBackend]] = None,
    ) -> None:
        """Init for Tket backend settings.

        Args:
            tket_backend (Backend): Tket backend instance to use for the simulation.

        Raises:
            TypeError: the input is not a valid Tket Backend instance.
        """
        if tket_backend is None:
            self.tket_backend: Union[AerBackend, Backend] = AerBackend()
        elif isinstance(tket_backend, Backend) or isinstance(tket_backend, AerBackend):
            self.tket_backend = tket_backend
        else:
            raise TypeError("The input is not a valid Tket Backend instance.")

    def compile_circuit(self, circuits: Union[Circuit, List[Circuit]]) -> Circuit:
        """Use a tket backend to compile qoqo circuit(s).

        Args:
            circuits (Union[Circuit, List[Circuit]]): qoqo circuit(s)

        Returns:
            Circuit: compiled qoqo circuit
        """
        circuits_is_list = isinstance(circuits, list)

        if not isinstance(circuits, Circuit) and not circuits_is_list:
            raise TypeError("The input is not a valid Qoqo Circuit instance.")

        circuits = circuits if circuits_is_list else [circuits]

        qasm_backend = QasmBackend(qasm_version="2.0")

        tket_circuits = [
            circuit_from_qasm_str(qasm_backend.circuit_to_qasm_str(circuit))
            for circuit in circuits
        ]
        compiled_tket_circuits = self.tket_backend.get_compiled_circuits(tket_circuits)

        tket_qasm = [
            circuit_to_qasm_str(compiled_tket_circuit).replace("( ", " ")
            for compiled_tket_circuit in compiled_tket_circuits
        ]

        transpiled_qoqo_circuits = [qasm_str_to_circuit(qasm_str) for qasm_str in tket_qasm]
        return transpiled_qoqo_circuits if circuits_is_list else transpiled_qoqo_circuits[0]

    def run_circuit(
        self,
        circuits: Union[Circuit, list[Circuit]],
        n_shots: Union[int, list[int], None] = None,
    ) -> Union[
        Tuple[
            Dict[str, List[List[bool]]],
            Dict[str, List[List[float]]],
            Dict[str, List[List[complex]]],
        ],
        List[
            Tuple[
                Dict[str, List[List[bool]]],
                Dict[str, List[List[float]]],
                Dict[str, List[List[complex]]],
            ]
        ],
    ]:
        """Use a tket backend to run qoqo circuit(s).

        Args:
            circuits (Union[Circuit, list[Circuit]]): qoqo circuit(s)
            n_shots (Union[int, list[int], None]): number of shots for each circuit

        Returns:
            Union[
            Tuple[
                Dict[str, List[List[bool]]],
                Dict[str, List[List[float]]],
                Dict[str, List[List[complex]]],
            ],
            List[
                Tuple[
                    Dict[str, List[List[bool]]],
                    Dict[str, List[List[float]]],
                    Dict[str, List[List[complex]]],
                ]
            ],
        ]]: Result for each circuit
        """
        circuits_is_list = isinstance(circuits, list)

        if not isinstance(circuits, Circuit) and not circuits_is_list:
            raise TypeError("The input is not a valid Qoqo Circuit instance.")

        circuits = circuits if circuits_is_list else [circuits]

        qasm_backend = QasmBackend(qasm_version="2.0")

        tket_circuits = [
            circuit_from_qasm_str(qasm_backend.circuit_to_qasm_str(circuit))
            for circuit in circuits
        ]
        compiled_tket_circuits = self.tket_backend.get_compiled_circuits(tket_circuits)
        tket_results = self.tket_backend.run_circuits(compiled_tket_circuits, n_shots)

        output = []
        for result, qoqo_circuit in zip(tket_results, circuits):
            output_bit_register: Dict[str, List[List[bool]]] = {}
            output_float_register: Dict[str, list[List[float]]] = {}
            output_complex_register: Dict[str, List[List[complex]]] = {}
            if result.contains_measured_results:
                name = result.get_bitlist()[0].reg_name
                output_bit_register = {
                    name: [[bool(bit) for bit in shot] for shot in result.get_shots()]
                }
            if result.contains_state_results:
                for op in qoqo_circuit:
                    if "PragmaGetStateVector" in op.tags():
                        output_complex_register = {op.readout(): [list(result.get_state())]}
                        break
                    elif "PragmaGetDensityMatrix" in op.tags():
                        output_complex_register = {
                            op.readout(): [list(result.get_density_matrix())]
                        }
                        break
            output.append(
                (
                    output_bit_register,
                    output_float_register,
                    output_complex_register,
                )
            )
        return output if circuits_is_list else output[0]

    def compile_program(self, quantum_program: QuantumProgram) -> QuantumProgram:
        """Use tket backend to compile a QuantumProgram.

        Args:
            quantum_program (QuantumProgram): QuantumProgram to transpile.

        Returns:
            QuantumProgram: transpiled QuantumProgram.
        """
        constant_circuit = quantum_program.measurement().constant_circuit()
        circuits = quantum_program.measurement().circuits()
        circuits = (
            circuits
            if constant_circuit is None
            else [constant_circuit + circuit for circuit in circuits]
        )
        transpiled_circuits = self.compile_circuit(circuits)

        def recreate_measurement(
            quantum_program: QuantumProgram, transpiled_circuits: List[Circuit]
        ) -> Union[PauliZProduct, ClassicalRegister, CheatedPauliZProduct, Cheated]:
            """Recreate a measurement QuantumProgram using the transpiled circuits.

            Args:
                quantum_program (QuantumProgram): quantumProgram to transpile.
                transpiled_circuits (List[Circuit]): transpiled circuits.

            Returns:
                Union[PauliZProduct, ClassicalRegister,
                CheatedPauliZProduct, Cheated]: measurement

            Raises:
                TypeError: if the measurement type is not supported.
            """
            if isinstance(quantum_program.measurement(), PauliZProduct):
                return PauliZProduct(
                    constant_circuit=None,
                    circuits=transpiled_circuits,
                    input=quantum_program.measurement().input(),
                )
            elif isinstance(quantum_program.measurement(), CheatedPauliZProduct):
                return CheatedPauliZProduct(
                    constant_circuit=None,
                    circuits=transpiled_circuits,
                    input=quantum_program.measurement().input(),
                )
            elif isinstance(quantum_program.measurement(), Cheated):
                return Cheated(
                    constant_circuit=None,
                    circuits=transpiled_circuits,
                    input=quantum_program.measurement().input(),
                )
            elif isinstance(quantum_program.measurement(), ClassicalRegister):
                return ClassicalRegister(constant_circuit=None, circuits=transpiled_circuits)
            else:
                raise TypeError("Unknown measurement type")

        return QuantumProgram(
            measurement=recreate_measurement(quantum_program, transpiled_circuits),
            input_parameter_names=quantum_program.input_parameter_names(),
        )

    def run_measurement_registers(
        self,
        measurement: Any,
    ) -> Tuple[
        Dict[str, List[List[bool]]],
        Dict[str, List[List[float]]],
        Dict[str, List[List[complex]]],
    ]:
        """Run all circuits of a measurement with the Tket backend.

        Args:
            measurement: The measurement that is run.

        Returns:
            Tuple[Dict[str, List[List[bool]]],\
                  Dict[str, List[List[float]]],\
                  Dict[str, List[List[complex]]]]
        """
        constant_circuit = measurement.constant_circuit()
        output_bit_register_dict: Dict[str, List[List[bool]]] = {}
        output_float_register_dict: Dict[str, List[List[float]]] = {}
        output_complex_register_dict: Dict[str, List[List[complex]]] = {}

        for circuit in measurement.circuits():
            if constant_circuit is None:
                run_circuit = circuit
            else:
                run_circuit = constant_circuit + circuit

            results = self.run_circuit(run_circuit)
            (
                tmp_bit_register_dict,
                tmp_float_register_dict,
                tmp_complex_register_dict,
            ) = (
                results if not isinstance(results, list) else results[0]
            )

            for key, value_bools in tmp_bit_register_dict.items():
                if key in output_bit_register_dict:
                    output_bit_register_dict[key].extend(value_bools)
                else:
                    output_bit_register_dict[key] = value_bools
            for key, value_floats in tmp_float_register_dict.items():
                if key in output_float_register_dict:
                    output_float_register_dict[key].extend(value_floats)
                else:
                    output_float_register_dict[key] = value_floats
            for key, value_complexes in tmp_complex_register_dict.items():
                if key in output_complex_register_dict:
                    output_complex_register_dict[key].extend(value_complexes)
                else:
                    output_complex_register_dict[key] = value_complexes

        return (
            output_bit_register_dict,
            output_float_register_dict,
            output_complex_register_dict,
        )

    def run_measurement(
        self,
        measurement: Any,
    ) -> Optional[Dict[str, float]]:
        """Run a circuit with the Tket backend.

        Args:
            measurement: The measurement that is run.

        Returns:
            Optional[Dict[str, float]]
        """
        (
            output_bit_register_dict,
            output_float_register_dict,
            output_complex_register_dict,
        ) = self.run_measurement_registers(measurement)

        return measurement.evaluate(
            output_bit_register_dict,
            output_float_register_dict,
            output_complex_register_dict,
        )

    def run_program(self, program: QuantumProgram, params_values: List[List[float]]) -> Optional[
        List[
            Union[
                Tuple[
                    Dict[str, List[List[bool]]],
                    Dict[str, List[List[float]]],
                    Dict[str, List[List[complex]]],
                ],
                Dict[str, float],
            ]
        ]
    ]:
        """Run a qoqo quantum program on a tket backend multiple times.

        It can handle QuantumProgram instances containing any kind of measurement. The list of
        lists of parameters will be used to call `program.run(self, params)` or
        `program.run_registers(self, params)` as many times as the number of sublists.
        The return type will change accordingly.

        If no parameters values are provided, a normal call `program.run(self, [])` call
        will be executed.

        Args:
            program (QuantumProgram): the qoqo quantum program to run.
            params_values (List[List[float]]): the parameters values to pass to the quantum
                program.

        Returns:
            Optional[
                List[
                    Union[
                        Tuple[
                            Dict[str, List[List[bool]]],
                            Dict[str, List[List[float]]],
                            Dict[str, List[List[complex]]],
                        ],
                        Dict[str, float],
                    ]
                ]
            ]: list of dictionaries (or tuples of dictionaries) containing the
                run results.
        """
        returned_results = []

        if isinstance(program.measurement(), ClassicalRegister):
            if not params_values:
                returned_results.append(program.run_registers(self, []))
            for params in params_values:
                returned_results.append(program.run_registers(self, params))
        else:
            if not params_values:
                returned_results.append(program.run(self, []))
            for params in params_values:
                returned_results.append(program.run(self, params))

        return returned_results
