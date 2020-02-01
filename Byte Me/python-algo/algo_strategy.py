import gamelib
import random
import math
import warnings
from sys import maxsize
import json

"""
Most of the algo code you write will be in this file unless you create new
modules yourself. Start by modifying the 'on_turn' function.

Advanced strategy tips:

  - You can analyze action frames by modifying on_action_frame function

  - The GameState.map object can be manually manipulated to create hypothetical
  board states. Though, we recommended making a copy of the map to preserve
  the actual current map state.
"""

class AlgoStrategy(gamelib.AlgoCore):

    def __init__(self):
        super().__init__()
        seed = random.randrange(maxsize)
        random.seed(seed)
        gamelib.debug_write('Random seed: {}'.format(seed))

    def on_game_start(self, config):
        """
        Read in config and perform any initial setup here
        """
        gamelib.debug_write('Configuring your custom algo strategy...')
        self.config = config
        global FILTER, ENCRYPTOR, DESTRUCTOR, PING, EMP, SCRAMBLER, BITS, CORES
        FILTER = config["unitInformation"][0]["shorthand"]
        ENCRYPTOR = config["unitInformation"][1]["shorthand"]
        DESTRUCTOR = config["unitInformation"][2]["shorthand"]
        PING = config["unitInformation"][3]["shorthand"]
        EMP = config["unitInformation"][4]["shorthand"]
        SCRAMBLER = config["unitInformation"][5]["shorthand"]
        BITS = 1
        CORES = 0
        # This is a good place to do initial setup
        self.scored_on_locations = []
        self.broken_locations = []
        # Mapping:
        ##      -1 is not on the board
        ##      1 is filter
        ##      2 is destructor
        ##      3 is encryptor
        self.desired_map =  [[ 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
                [-1, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2,-1],
                [-1,-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0,-1,-1],
                [-1,-1,-1, 1, 1, 1, 1, 1, 1, 0, 0, 2, 2, 2, 2, 2, 2, 0, 0, 1, 1, 1, 1, 1, 1,-1,-1,-1],
                [-1,-1,-1,-1, 2, 2, 2, 2, 2, 0, 0, 3, 3, 3, 3, 3, 3, 0, 0, 2, 2, 2, 2, 2,-1,-1,-1,-1],
                [-1,-1,-1,-1,-1, 0, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 0,-1,-1,-1,-1,-1],
                [-1,-1,-1,-1,-1,-1, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4,-1,-1,-1,-1,-1,-1],
                [-1,-1,-1,-1,-1,-1,-1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1,-1,-1,-1,-1,-1,-1,-1],
                [-1,-1,-1,-1,-1,-1,-1,-1, 2, 2, 2, 2, 2, 0, 2, 2, 2, 2, 2, 2,-1,-1,-1,-1,-1,-1,-1,-1],
                [-1,-1,-1,-1,-1,-1,-1,-1,-1, 0, 3, 3, 3, 0, 3, 3, 3, 3, 0,-1,-1,-1,-1,-1,-1,-1,-1,-1],
                [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1, 4, 0, 0, 0, 0, 0, 0, 4,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
                [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1, 0, 0, 0, 0, 0, 0,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
                [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1, 0, 0, 0, 0,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
                [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1, 0, 0,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]]

            # priorities work as you would expect, higher priorities should be serviced first
            # 69 is the highest possible priority (as it should be), only positive priorities should be considered
            # b_priority is build priorities
        self.b_priority_map=[[69,69,69,69, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,69,69,69,69],
                [-1,69,69, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,69,69,-1],
                [-1,-1, 0, 0, 0, 0, 0, 0, 0, 0, 0,65,65,60,60,65,65, 0, 0, 0, 0, 0, 0, 0, 0, 0,-1,-1],
                [-1,-1,-1,65,65,65,65,45,45, 0, 0,69,35,60,35,35,69, 0, 0,50,50,60,60,60,60,-1,-1,-1],
                [-1,-1,-1,-1,65,65,40,40,40, 0, 0,55,55,55,55,55,55, 0, 0,50,50,50,60,60,-1,-1,-1,-1],
                [-1,-1,-1,-1,-1, 0,40,40,40, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,45,45,45, 0,-1,-1,-1,-1,-1],
                [-1,-1,-1,-1,-1,-1, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4,-1,-1,-1,-1,-1,-1],
                [-1,-1,-1,-1,-1,-1,-1,30,30,30,25,25,25, 0,20,20,20,20,35,35,35,-1,-1,-1,-1,-1,-1,-1],
                [-1,-1,-1,-1,-1,-1,-1,-1,30,30,25,25,25, 0,20,20,20,20,35,35,-1,-1,-1,-1,-1,-1,-1,-1],
                [-1,-1,-1,-1,-1,-1,-1,-1,-1, 0,15,15,15, 0,15,15,15,15, 0,-1,-1,-1,-1,-1,-1,-1,-1,-1],
                [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1, 4, 0, 0, 0, 0, 0, 0, 4,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
                [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1, 0, 0, 0, 0, 0, 0,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
                [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1, 0, 0, 0, 0,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],
                [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1, 0, 0,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]]
        self.desired_filters = findInMap(1)
        self.desired_destructors = findInMap(2)
        self.desired_encryptors = findInMap(3)

    def findInMap(value):
        result = []
        rowcounter = 0
        columncounter = 0
        for row in self.desired_map:
            for column in row:
                if(column == value):
                    result.append([columncounter, rowcounter])
                columncounter += 1
            rowcounter += 1
        return result

    def getPriority(coords):
        return this.b_priority_map[27-coords[1]][coords[0]]

    def getUnit(coords):
         return this.desired_map[27-coords[1]][coords[0]]

    def on_turn(self, turn_state):
        """
        This function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        """
        game_state = gamelib.GameState(self.config, turn_state)
        self.game_state = game_state.game_map
        self.my_health = game_state.my_health
        self.their_helath = game_state.their_health
        gamelib.debug_write("Last turn (number {}) took {} milliseconds".format(game_state.turn_number, game_state.my_time))
        gamelib.debug_write('Performing turn {} of your custom algo strategy'.format(game_state.turn_number))
        #game_state.suppress_warnings(True)  #Comment or remove this line to enable warnings.

        self.defense_strategy(game_state)
        game_state = gamelib.GameState(self.config, turn_state)
        self.offense_strategy(game_state)
        game_state.submit_turn()

    """
    NOTE: All the methods after this point are part of the sample starter-algo
    strategy and can safely be replaced for your custom algo.
    """

    def defense_strategy(self, game_state):
        """
        For defense we will use a staggered layout with filters and destructers.
        We will place destructors near locations the opponent managed to score on.
        For offense we will use long range EMPs if they place stationary units near the enemy's front.
        If there are no stationary units to attack in the front, we will send Pings to try and score quickly.
        """
        # --------------------  First, place basic defenses-------------------------------#
        # Place destructors that attack enemy units
        filter_locations = [[0, 13], [1, 13], [2, 13], [3, 13],
                                [24, 13], [25, 13], [26, 13], [27, 14]
                                [8, 11], [9, 11], [10, 11]
                                [17, 11], [18, 11], [19, 11]
                                [13, 7], [14, 7], [15, 7]]

        master_list = []
        for row in this.desired_map:
            for col in row:
                master_list.append([row, col])
        master_list.sort(key=getPriority, reverse=True)
        destructors = getInMap(2)
        filters = getInMap(1)
        encryptors = getInMap(3)
        for coords in master_list:
            unit = getUnit(coords)
            if unit == 1:
                game_state.attempt_spawn(FILTER, [[27-coords[1], coords[0]]])
            elif unit == 2:
                game_state.attempt_spawn(DESTRUCTOR, [[27-coords[1], coords[0]]])
            elif unit == 3:
                game_state.attempt_spawn(ENCRYPTOR, [[27-coords[1], coords[0]]])

    def offense_strategy(self, game_state):
       if game_state.turn_number == 0:
           return
       elif game_state.my_health <= 3:
           locations = findInMap(4)
           if locations == None:
               locations = self.get_deploy_locations(game_state)
           spawn_location_options = locations
           #will check which of the preset spawn location options have the least enemy units in the path
           best_location = self.least_damage_spawn_location(game_state, spawn_location_options)
           game_state.attempt_spawn(EMP, best_location, 2)
           #check the spawn points above and below the initial point. We will check above first and send as many pings as possible
           if best_location[0] > 14:
               other_location = best_location
               other_location[0] = best_location[0] + 1
               other_location[1] = best_location[1] + 1
               game_state.attempt_spawn(PING, other_location)
               other1_location = best_location
               other1_location[0] = best_location[0] - 1
               other1_location[1] = best_location[1] - 1
               game_state.attempt_spawn(PING, other1_location)
           else:
               other2_location = best_location
               other2_location[0] = best_location[0] + 1
               other2_location[1] = best_location[1] - 1
               game_state.attempt_spawn(PING, other2_location)
               other3_location = best_location
               other3_location[0] = best_location[0] - 1
               other3_location[1] = best_location[1] + 1
               game_state.attempt_spawn(PING, other3_location)
           #sends anything else incase all the above options fail
           newLocations = self.get_deploy_locations(game_state)
           newBestLocation = self.least_damage_spawn_location(game_state, newLocations)
           game_state.attempt_spawn(EMP, newBestLocation, 1000)
       elif bits > 15:
           locations = findInMap(4)
           if locations == None:
               locations = self.get_deploy_locations(game_state)
           spawn_location_options = locations
           #will check which of the preset spawn location options have the least enemy units in the path
           best_location = self.least_damage_spawn_location(game_state, spawn_location_options)
           game_state.attempt_spawn(EMP, best_location, 2)
           #check the spawn points above and below the initial point. We will check above first and send as many pings as possible
           if best_location[0] > 14:
               other_location = best_location
               other_location[0] = best_location[0] + 1
               other_location[1] = best_location[1] + 1
               game_state.attempt_spawn(PING, other_location)
               other1_location = best_location
               other1_location[0] = best_location[0] - 1
               other1_location[1] = best_location[1] - 1
               game_state.attempt_spawn(PING, other1_location)
           else:
               other2_location = best_location
               other2_location[0] = best_location[0] + 1
               other2_location[1] = best_location[1] - 1
               game_state.attempt_spawn(PING, other2_location)
               other3_location = best_location
               other3_location[0] = best_location[0] - 1
               other3_location[1] = best_location[1] + 1
               game_state.attempt_spawn(PING, other3_location)
           #sends anything else in case all the above options fail
           newLocations = self.get_deploy_locations(game_state)
           newBestLocation = self.least_damage_spawn_location(game_state, newLocations)
           game_state.attempt_spawn(EMP, newBestLocation, 1000)



    def stall_with_scramblers(self, game_state):
        """
        Send out Scramblers at random locations to defend our base from enemy moving units.
        """
        deploy_locations = self.get_deploy_locations(game_state)

        # While we have remaining bits to spend lets send out scramblers randomly.
        while game_state.get_resource(BITS) >= game_state.type_cost(SCRAMBLER)[BITS] and len(deploy_locations) > 0:
            # Choose a random deploy location.
            deploy_index = random.randint(0, len(deploy_locations) - 1)
            deploy_location = deploy_locations[deploy_index]

            game_state.attempt_spawn(SCRAMBLER, deploy_location)
            """
            We don't have to remove the location since multiple information
            units can occupy the same space.
            """

    def emp_line_strategy(self, game_state):
        """
        Build a line of the cheapest stationary unit so our EMP's can attack from long range.
        """
        # First let's figure out the cheapest unit
        # We could just check the game rules, but this demonstrates how to use the GameUnit class
        stationary_units = [FILTER, DESTRUCTOR, ENCRYPTOR]
        cheapest_unit = FILTER
        for unit in stationary_units:
            unit_class = gamelib.GameUnit(unit, game_state.config)
            if unit_class.cost[game_state.BITS] < gamelib.GameUnit(cheapest_unit, game_state.config).cost[game_state.BITS]:
                cheapest_unit = unit

        # Now let's build out a line of stationary units. This will prevent our EMPs from running into the enemy base.
        # Instead they will stay at the perfect distance to attack the front two rows of the enemy base.
        for x in range(27, 5, -1):
            game_state.attempt_spawn(cheapest_unit, [x, 11])

        # Now spawn EMPs next to the line
        # By asking attempt_spawn to spawn 1000 units, it will essentially spawn as many as we have resources for
        game_state.attempt_spawn(EMP, [24, 10], 1000)

    def least_damage_spawn_location(self, game_state, location_options):
        """
        This function will help us guess which location is the safest to spawn moving units from.
        It gets the path the unit will take then checks locations on that path to
        estimate the path's damage risk.
        """
        damages = []
        # Get the damage estimate each path will take
        for location in location_options:
            path = game_state.find_path_to_edge(location)
            damage = 0
            for path_location in path:
                # Get number of enemy destructors that can attack the final location and multiply by destructor damage
                damage += len(game_state.get_attackers(path_location, 0)) * gamelib.GameUnit(DESTRUCTOR, game_state.config).damage_i
            damages.append(damage)

        # Now just return the location that takes the least damage
        return location_options[damages.index(min(damages))]

    def detect_enemy_unit(self, game_state, unit_type=None, valid_x = None, valid_y = None):
        total_units = 0
        for location in game_state.game_map:
            if game_state.contains_stationary_unit(location):
                for unit in game_state.game_map[location]:
                    if unit.player_index == 1 and (unit_type is None or unit.unit_type == unit_type) and (valid_x is None or location[0] in valid_x) and (valid_y is None or location[1] in valid_y):
                        total_units += 1
        return total_units

    def filter_blocked_locations(self, locations, game_state):
        filtered = []
        for location in locations:
            if not game_state.contains_stationary_unit(location):
                filtered.append(location)
        return filtered

    def get_deploy_locations(self, game_state):
        friendly_edges = game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_LEFT) + game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_RIGHT)
        deploy_locations = self.filter_blocked_locations(friendly_edges, game_state)
        return deploy_locations

    def get_attack_locations(self, game_state):
        enemy_edges = game_state.game_map.get_edge_locations(game_state.game_map.TOP_LEFT) + game_state.game_map.get_edge_locations(game_state.game_map.TOP_RIGHT)
        attack_locations = self.filter_blocked_locations(enemy_edges, game_state)
        return attack_locations

    def on_action_frame(self, turn_string):
        """
        This is the action frame of the game. This function could be called
        hundreds of times per turn and could slow the algo down so avoid putting slow code here.
        Processing the action frames is complicated so we only suggest it if you have time and experience.
        Full doc on format of a game frame at: https://docs.c1games.com/json-docs.html
        """
        # Let's record at what position we get scored on
        state = json.loads(turn_string)
        events = state["events"]
        breaches = events["breach"]
        for breach in breaches:
            location = breach[0]
            unit_owner_self = True if breach[4] == 1 else False
            # When parsing the frame data directly,
            # 1 is integer for yourself, 2 is opponent (StarterKit code uses 0, 1 as player_index instead)
            if not unit_owner_self:
                gamelib.debug_write("Got scored on at: {}".format(location))
                self.scored_on_locations.append(location)
                gamelib.debug_write("All locations: {}".format(self.scored_on_locations))


if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
