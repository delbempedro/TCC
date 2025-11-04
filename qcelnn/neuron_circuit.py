"""
  neuron_circuit.py

Module that defines the quantum neuron circuit.

Dependencies:
- Uses qiskit module to define a quantum circuit
- Uses qiskit.quantum_info module to define the observable
- Uses qiskit_aer.primitives module to run the quantum circuit

Since:
- 10/2025

Authors:
- Pedro C. Delbem. <pedrodelbem@usp.br>
"""
#do general necessary imports
import numpy as np

#do qiskit necessary imports
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp
from qiskit_aer.primitives import Estimator

#do my necessary imports
from neuron_utils import layer_QCelNN, layer_hybrid

class neuron_circuit():
    
    def __init__(self,num_of_qbits,num_of_classical_bits):
        """
        Create a new quantum circuit.
        """

        self._num_of_qbits = num_of_qbits
        self._num_of_classical_bits = num_of_classical_bits
        self._qc = QuantumCircuit(self._num_of_qbits)

        #initialize the estimator
        self._estimator = Estimator()

    
    def get_current_circuit(self):
        """
        Get the current quantum circuit.
        
        Returns:
        The current quantum circuit (QuantumCircuit).
        """

        return self._qc

    def get_num_of_qbits(self):
        """
        Get the number of qbits in the quantum circuit.
        
        Returns:
        The number of qbits in the quantum circuit (int).
        """

        return self._num_of_qbits

    def get_num_of_classical_bits(self):
        """
        Get the number of classical bits in the quantum circuit.
        
        Returns:
        The number of classical bits in the quantum circuit (int).
        """

        return self._num_of_classical_bits
    
    def print_current_circuit(self,output='text',style='ascii'):
        """
        Print the current quantum circuit.
        """

        print(self._qc.draw(output=output,style=style,fold=-1))

    def evaluate_observable_evolution(self, inputs, inputs_normalized, control_template, feedback_template, total_layers, mode='non-hybrid', dt=0.01, first_qubit_index=0, first=0):
        """
        Evaluate the evolution of the observable magnitude of each qubit.

        Parameters:
        inputs (list of floats): The inputs to the neuron.
        control_template (list of floats): The control template for the neuron.
        feedback_template (list of floats): The feedback template for the neuron.
        total_layers (int): The total number of layers to evaluate.

        Returns:
        A dictionary with the labels of the observables as keys and the values of the observables as values.
        """

        #define the observables
        observables = [
            SparsePauliOp("ZII"),
            SparsePauliOp("IZI"),
            SparsePauliOp("IIZ")
        ]
        observable_labels = ["x", "y", "z"]

        #encodes the inputs as rotations so that the measure of rz is equal to the input
        results = {label: [] for label in observable_labels}
        layer_range = range(1, total_layers + 1)

        #codify the inputs as angles of the ry gates for each qubit 
        for i in range(len(inputs)):
            self._qc.ry(np.arccos(inputs[i]), i)

        #principal loop for the analysis
        if mode == 'non-hybrid':
            for i in layer_range:

                #applies the layer
                layer_QCelNN(self._qc, inputs_normalized, control_template, feedback_template, mode=mode, first_qubit_index=first_qubit_index)
                
                #runs the observables
                job_result = self._estimator.run(circuits=[self._qc] * len(observables), observables=observables).result()
                
                #saves the results
                for j, label in enumerate(observable_labels):
                    results[label].append(job_result.values[j])

        elif mode == 'hybrid':

            dt = dt
            classical_state = np.array(inputs, dtype=float)

            for i in layer_range:

                #applies the layer
                layer_hybrid(qc=self._qc, inputs=inputs_normalized, control_template=control_template, feedback_template=feedback_template, state_vector=classical_state, dt=dt, first_qubit_index=first_qubit_index)
                
                #runs the observables
                job_result = self._estimator.run(circuits=[self._qc] * len(observables), observables=observables).result()
                
                classical_state = np.array(job_result.values)
                
                for j, label in enumerate(observable_labels):
                    results[label].append(job_result.values[j])

        #returns the results
        return results