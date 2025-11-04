"""
  utils.py

Module that defines the util functions to create a quantum celular neuron.

Dependencies:
- 

Since:
- 10/2025

Authors:
- Pedro C. Delbem. <pedrodelbem@usp.br>
"""

def layer_QCelNN(qc,inputs,control_template,feedback_template,mode,dt=0.01,first_qubit_index=0):

    if mode == "hybrid":

        for qubit_index in range(len(control_template)):
            #qc.rz(control_template[qubit_index][0] * inputs[0] + control_template[qubit_index][1] * inputs[1] + control_template[qubit_index][2] * inputs[2], first_qubit_index + qubit_index)
            qc.rx(dt*(control_template[qubit_index][0] * inputs[0] + control_template[qubit_index][1] * inputs[1] + control_template[qubit_index][2] * inputs[2])/3, first_qubit_index + qubit_index)

        qc.barrier()

        qc.cry(dt*feedback_template[0][1], first_qubit_index, first_qubit_index+1)
        qc.cry(dt*feedback_template[0][2], first_qubit_index, first_qubit_index+2)

        #self interaction
        qc.ry(dt*feedback_template[0][0], first_qubit_index)

        qc.cry(dt*feedback_template[1][0], first_qubit_index+1, first_qubit_index)
        qc.cry(dt*feedback_template[1][2], first_qubit_index+1, first_qubit_index+2)

        #self interaction
        qc.ry(dt*feedback_template[1][1], first_qubit_index + 1)

        qc.cry(dt*feedback_template[2][0], first_qubit_index+2, first_qubit_index)
        qc.cry(dt*feedback_template[2][1], first_qubit_index+2, first_qubit_index+1)

        #self interaction
        qc.ry(dt*feedback_template[2][2], first_qubit_index + 2)
    
    if mode == "non-hybrid":

        for qubit_index in range(len(control_template)):
            #qc.rz(control_template[qubit_index][0] * inputs[0] + control_template[qubit_index][1] * inputs[1] + control_template[qubit_index][2] * inputs[2], first_qubit_index + qubit_index)
            qc.rx(dt*(control_template[qubit_index][0] * inputs[0] + control_template[qubit_index][1] * inputs[1] + control_template[qubit_index][2] * inputs[2])/3*(1-dt), first_qubit_index + qubit_index)

        qc.barrier()

        qc.cry(dt*feedback_template[0][1]*(1-dt), first_qubit_index, first_qubit_index+1)
        qc.cry(dt*feedback_template[0][2]*(1-dt), first_qubit_index, first_qubit_index+2)

        #self interaction
        qc.ry(dt*feedback_template[0][0]*(1-dt), first_qubit_index)

        qc.cry(dt*feedback_template[1][0]*(1-dt), first_qubit_index+1, first_qubit_index)
        qc.cry(dt*feedback_template[1][2]*(1-dt), first_qubit_index+1, first_qubit_index+2)

        #self interaction
        qc.ry(dt*feedback_template[1][1]*(1-dt), first_qubit_index + 1)

        qc.cry(dt*feedback_template[2][0]*(1-dt), first_qubit_index+2, first_qubit_index)
        qc.cry(dt*feedback_template[2][1]*(1-dt), first_qubit_index+2, first_qubit_index+1)

        #self interaction
        qc.ry(dt*feedback_template[2][2]*(1-dt), first_qubit_index + 2)

        qc.barrier()

        #non linear terms
        # dy = -dt xz
        qc.mcrx(-dt, [first_qubit_index+0, first_qubit_index+2], first_qubit_index+1) 
        # dz = dt xy
        qc.mcrx(dt, [first_qubit_index+0, first_qubit_index+1], first_qubit_index+2)
    
    qc.barrier()

    #deriative
    """
    if mode == "non_hybrid":
        qc.rx(-dt*feedback_template[0][0], first_qubit_index)
        qc.rx(-dt*feedback_template[1][1], first_qubit_index + 1)
        qc.rx(-dt*feedback_template[2][2], first_qubit_index + 2)
    """

def layer_self_decay(qc, state_vector, dt=0.01, first_qubit_index=0):
    """
    Aplica o efeito de auto-feedback (derivada = -x) em cada qubit.
    """
    x, y, z = state_vector[0], state_vector[1], state_vector[2]
    # O ângulo da rotação é dt * derivada (-x, -y, -z)
    """
    qc.rx(-x * dt, first_qubit_index)
    qc.rx(-y * dt, first_qubit_index+1)
    qc.rx(-z * dt, first_qubit_index+2)
    qc.barrier()
    """
    qc.ry(-x * dt, first_qubit_index)
    qc.ry((-y - (x * z)) * dt, first_qubit_index+1) # dy = -dt xz
    qc.ry((-z + (x * y)) * dt, first_qubit_index+2) # dz = dt xy
    qc.barrier()

def layer_hybrid(qc, inputs, control_template, feedback_template, state_vector, dt=0.01, first_qubit_index=0):
    """
    Aplica uma camada híbrida que combina os templates e a auto-derivada.
    """
    # Efeito dos Templates (Cx e Nl)
    layer_QCelNN(qc, inputs, control_template, feedback_template, mode="hybrid", first_qubit_index=first_qubit_index)
    
    # Efeito da Auto-Derivada (-x)
    layer_self_decay(qc, state_vector, dt=dt, first_qubit_index=first_qubit_index)