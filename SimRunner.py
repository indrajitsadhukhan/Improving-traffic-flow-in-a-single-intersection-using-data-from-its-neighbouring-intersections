import traci
import numpy as np
import random


# phase codes based on tlcs.net.xml
PHASE_NC_GREEN = 0  # action 0 code 00
PHASE_NC_YELLOW = 1
PHASE_EC_GREEN = 2  # action 1 code 01
PHASE_EC_YELLOW = 3
PHASE_SC_GREEN = 4  # action 2 code 10
PHASE_SC_YELLOW = 5
PHASE_WC_GREEN = 6  # action 3 code 11
PHASE_WC_YELLOW = 7

# HANDLE THE SIMULATION OF THE AGENT
class SimRunner:
    def __init__(self,traffic_gen, max_steps, green_duration, yellow_duration, sumoCmd):
        self._traffic_gen = traffic_gen
        self._steps = 0
        self._waiting_times = {}
        self._sumoCmd = sumoCmd
        self._max_steps = max_steps
        self._green_duration = green_duration
        self._yellow_duration = yellow_duration
        self._sum_intersection_queue = 0
        self._cumulative_wait_store = {}
        self._avg_intersection_queue_store = []


    # THE MAIN FUCNTION WHERE THE SIMULATION HAPPENS
    def run(self):
        # first, generate the route file for this simulation and set up sumo
        self._traffic_gen.generate_routefile(1234)
        traci.start(self._sumoCmd)

        # inits
        self._steps = 0
        old_total_wait = 0
        old_action = 6
        self._waiting_times = {}
        self._sum_intersection_queue = 0
        action = 0

        while self._steps < self._max_steps:

            # waiting time = seconds waited by a car since the spawn in the environment, cumulated for every car in incoming lanes
            current_total_wait = self._get_waiting_times()
            self._cumulative_wait_store[self._steps]=self._get_waiting_times()

            # if the chosen phase is different from the last phase, activate the yellow phase
            if self._steps != 0 and old_action != action:
                self._set_yellow_phase(old_action)
                self._simulate(self._yellow_duration)

            # execute the phase selected before
            self._set_green_phase(action)
            self._simulate(self._green_duration)

            # saving variables for later 
            old_total_wait = current_total_wait
            old_action = action
            action += 1
            if (action > 3):
                action = 0

        traci.close()

    # HANDLE THE CORRECT NUMBER OF STEPS TO SIMULATE
    def _simulate(self, steps_todo):
        if (self._steps + steps_todo) >= self._max_steps:  # do not do more steps than the maximum number of steps
            steps_todo = self._max_steps - self._steps
        self._steps = self._steps + steps_todo  # update the step counter
        while steps_todo > 0:
            traci.simulationStep()  # simulate 1 step in sumo
            steps_todo -= 1
            intersection_queue = self._get_stats()
            self._sum_intersection_queue += intersection_queue
            self._avg_intersection_queue_store.append(intersection_queue)


    # RETRIEVE THE WAITING TIME OF EVERY CAR IN THE INCOMING LANES
    def _get_waiting_times(self):
        incoming_roads = ["EtoC", "NtoC", "WtoC", "StoC"]
        for veh_id in traci.vehicle.getIDList():
            wait_time_car = traci.vehicle.getAccumulatedWaitingTime(veh_id)
            road_id = traci.vehicle.getRoadID(veh_id)  # get the road id where the car is located
            if road_id in incoming_roads:  # consider only the waiting times of cars in incoming roads
                self._waiting_times[veh_id] = wait_time_car
            else:
                if veh_id in self._waiting_times:
                    del self._waiting_times[veh_id]  # the car isnt in incoming roads anymore, delete his waiting time
        total_waiting_time = sum(self._waiting_times.values())
        return total_waiting_time

    # SET IN SUMO THE CORRECT YELLOW PHASE
    def _set_yellow_phase(self, old_action):
        yellow_phase = old_action * 2 + 1 # obtain the yellow phase code, based on the old action
        traci.trafficlight.setPhase("C", yellow_phase)

    # SET IN SUMO A GREEN PHASE
    def _set_green_phase(self, action_number):
        if action_number == 0:
            traci.trafficlight.setPhase("C", PHASE_NC_GREEN)
        elif action_number == 1:
            traci.trafficlight.setPhase("C", PHASE_EC_GREEN)
        elif action_number == 2:
            traci.trafficlight.setPhase("C", PHASE_SC_GREEN)
        elif action_number == 3:
            traci.trafficlight.setPhase("C", PHASE_WC_GREEN)

    # RETRIEVE THE STATS OF THE SIMULATION FOR ONE SINGLE STEP
    def _get_stats(self):
        halt_N = traci.edge.getLastStepHaltingNumber("NtoC")
        halt_S = traci.edge.getLastStepHaltingNumber("StoC")
        halt_E = traci.edge.getLastStepHaltingNumber("EtoC")
        halt_W = traci.edge.getLastStepHaltingNumber("WtoC")
        intersection_queue = halt_N + halt_S + halt_E + halt_W
        return intersection_queue

    @property
    def cumulative_wait_store(self):
        return self._cumulative_wait_store

    @property
    def avg_intersection_queue_store(self):
        return self._avg_intersection_queue_store