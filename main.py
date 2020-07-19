from __future__ import absolute_import
from __future__ import print_function

import os
import sys
try:
    sys.path.append(os.path.join(os.path.dirname(
        __file__), '..', '..', '..', '..', "tools"))  # tutorial in tests
    sys.path.append(os.path.join(os.environ.get("SUMO_HOME", os.path.join(
        os.path.dirname(__file__), "..", "..", "..")), "tools"))  # tutorial in docs
    from sumolib import checkBinary  # noqa
except ImportError:
    sys.exit(
        "please declare environment variable 'SUMO_HOME' as the root directory of your sumo installation (it should contain folders 'bin', 'tools' and 'docs')")

import matplotlib.pyplot as plt
from TrafficGenerator import TrafficGenerator
from SimRunner import SimRunner

# sumo things - we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

# PLOT AND SAVE THE STATS ABOUT THE SESSION
def save_graphs(sim_runner, plot_path):

    plt.rcParams.update({'font.size': 24})  # set bigger font size

    # cumulative wait
    data = sim_runner.cumulative_wait_store
    plt.plot(list(data.keys()),list(data.values()))
    plt.ylabel("Cumulative delay (s)")
    plt.xlabel("Steps")
    plt.margins(0)
    min_val = min(data.values())
    max_val = max(data.values())
    plt.ylim(min_val - 0.05 * min_val, max_val + 0.05 * max_val)
    fig = plt.gcf()
    fig.set_size_inches(20, 11.25)
    fig.savefig(plot_path + 'delay.png', dpi=96)
    plt.close("all")
    with open(plot_path + 'delay_data.txt', "w") as file:
        for k,v in data.items():
                file.write("%s %s\n" % (k,v))

    # average number of cars in queue
    data = sim_runner.avg_intersection_queue_store
    plt.plot(data)
    plt.ylabel("Queue length (vehicles)")
    plt.xlabel("Steps")
    plt.margins(0)
    min_val = min(data)
    max_val = max(data)
    plt.ylim(min_val - 0.05 * min_val, max_val + 0.05 * max_val)
    fig = plt.gcf()
    fig.set_size_inches(20, 11.25)
    fig.savefig(plot_path + 'queue.png', dpi=96)
    plt.close("all")
    with open(plot_path + 'queue_data.txt', "w") as file:
        for item in data:
                file.write("%s\n" % item)


if __name__ == "__main__":

    # --- SUMO OPTIONS ---
    gui = False

    # attributes of the simulation
    max_steps = 5400  
    green_duration = 10
    yellow_duration = 4
    path = "./results/" 

    # setting the cmd mode or the visual mode
    if gui == False:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    # initializations
    traffic_gen = TrafficGenerator(max_steps)
    sumoCmd = [sumoBinary, "-c", "intersection/sim.sumocfg", "--no-step-log", "true", "--waiting-time-memory", str(max_steps)]

    
    sim_runner = SimRunner(traffic_gen, max_steps, green_duration, yellow_duration, sumoCmd)

    sim_runner.run()

    save_graphs(sim_runner,path)