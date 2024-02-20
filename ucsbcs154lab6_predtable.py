# ucsbcs154lab6
# All Rights Reserved
# Copyright (c) 2023 University of California Santa Barbara
# Distribution Prohibited

import pyrtl

pyrtl.core.set_debug_mode()

# Inputs
fetch_pc = pyrtl.Input(bitwidth=32, name='fetch_pc') # current pc in fetch

update_prediction = pyrtl.Input(bitwidth=1, name='update_prediction') # whether to update prediction
update_branch_pc = pyrtl.Input(bitwidth=32, name='update_branch_pc') # previous pc (in decode/execute)
update_branch_taken = pyrtl.Input(bitwidth=1, name='update_branch_taken') # whether branch is taken (in decode/execute)

# Outputs
pred_taken = pyrtl.Output(bitwidth=1, name='pred_taken')

#two bit predictor
def update_state(current_state, taken):
    new_pred_state = pyrtl.WireVector(bitwidth=2, name='new_pred_state')

    with pyrtl.conditional_assignment:
        with taken:
            with current_state != 3:
                new_pred_state |= current_state + 1
        with taken == 0:
            with current_state != 0:
                new_pred_state |= current_state - 1

    return new_pred_state

# Write your BHT branch predictor here
branch_hist_table = pyrtl.MemBlock(bitwidth=2, addrwidth=3, name='branch_hist_table')
curr_entry = pyrtl.WireVector(bitwidth=3, name='curr_entry')
curr_entry <<= fetch_pc[2:5]
new_state = pyrtl.WireVector(bitwidth=2, name='new_state')
new_state <<= update_state(branch_hist_table[curr_entry], update_branch_taken)

with pyrtl.conditional_assignment:
    with update_prediction:
        branch_hist_table[curr_entry] <<= new_state
        with new_state == 0:
            pred_taken |= 0
        with new_state == 1:
            pred_taken |= 0
        with new_state == 2:
            pred_taken |= 1
        with new_state == 3:
            pred_taken |= 1
        





#Testing
if __name__ == "__main__":
    sim_trace = pyrtl.SimulationTrace()
    sim = pyrtl.Simulation(tracer=sim_trace)
    pcPrevious = 0
    branchTakenPrevious = 0
    isBranchPrevious = 0
    predictionPrevious = 0
    count = 0
    correct = 0
    f = open("demo_trace.txt", "r")  # Edit this line to change the trace file you read from
    for iteration,line in enumerate(f): # Read through each line in the file
        pcCurrent = int(line[0:line.find(':')],0) # parse out current pc
        branchTakenCurrent = int(line[12]) # parse out branch taken
        isBranchCurrent = int(line[16]) # parse if the current instr is a branch

        sim.step({ # Feed in input values
            'fetch_pc' : pcCurrent,
            'update_branch_pc' : pcPrevious,
            'update_prediction': isBranchPrevious,
            'update_branch_taken' : branchTakenPrevious
        })

        predictionCurrent = sim_trace.trace['pred_taken'][-1] # get the value of your prediction

        if isBranchPrevious: # check if previous instr was a branch
            if predictionPrevious == branchTakenPrevious: # if prediction was correct
                correct += 1
            count += 1


        # Update for next cycle
        pcPrevious = pcCurrent
        branchTakenPrevious = branchTakenCurrent
        isBranchPrevious = isBranchCurrent
        predictionPrevious = predictionCurrent

    # one final check
    if isBranchPrevious:
        if predictionPrevious == branchTakenPrevious:
            correct += 1 # Correct prediction
        count += 1

    print("Accuracy = ", correct/count)
    sim_trace.render_trace()
