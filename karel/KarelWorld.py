"""
General Notes About World Construction 
- Streets run EAST-WEST (rows)
- Avenues run NORTH-SOUTH (columns)

World File Constraints:
- World file should specify one component per line in the format
  KEYWORD: PARAMETERS
- Any lines with no comma delimiter will be ignored
- The accepted KEYWORD, PARAMETER combinations are as follows:
	- Dimension: (num_avenues, num_streets)
	- Wall: (avenue, street); direction
	- Beeper: (avenue, street) count
	- Karel: (avenue, street); direction
	- Speed: delay
	- BeeperBag: num_beepers
- Multiple parameter values for the same keyword should be separated by a semicolon
- All numerical values (except delay) must be expressed as ints. The exception
  to this is that the number of beepers can also be INFINITY
- Direction is case-insensitive and can be one of the following values:
	- East
	- West
	- North 
	- South	
"""
from karel.kareldefinitions import *
import collections
import re
import copy

class KarelWorld():
	def __init__(self, world_file=None):
		"""
		Karel World constructor
		Parameters:
			world_file: Open file object containing information about the initial state of Karel's world
		"""
		self._world_file = world_file

		# Map of beeper locations to the count of beepers at that location
		self._beepers = collections.defaultdict(int)

		# Set of Wall objects placed in the world
		self._walls = set()

		# Dimensions of the world
		self._num_streets = 1
		self._num_avenues = 1

		# Initial Karel state saved to enable world reset
		self._karel_starting_location = (1, 1)
		self._karel_starting_direction = Direction.EAST
		self._karel_starting_beeper_count = 0

		# Initial speed slider setting
		self._init_speed = INIT_SPEED

		# If a world file has been specified, load world details from the file
		if self._world_file:
			self.load_from_file()

		# Save initial beeper state to enable world reset
		self._init_beepers = copy.deepcopy(self._beepers)

	@property
	def karel_starting_location(self):
		return self._karel_starting_location

	@property
	def karel_starting_direction(self):
		return self._karel_starting_direction

	@property
	def karel_starting_beeper_count(self):
		return self._karel_starting_beeper_count
	
	@property
	def init_speed(self):
		return self._init_speed

	@property
	def num_streets(self):
		return self._num_streets

	@property
	def num_avenues(self):
		return self._num_avenues
	
	@property
	def beepers(self):
		return self._beepers

	@property
	def walls(self):
		return self._walls
	
	def load_from_file(self):
		def parse_line(line):
			# Ignore blank lines and lines with no comma delineator
			if not line or ":" not in line:
				return None, None, False

			params = {}
			components = line.strip().split(KEYWORD_DELIM)
			keyword = components[0].lower()

			# only accept valid keywords as defined in world file spec
			if keyword not in VALID_WORLD_KEYWORDS:
				return None, None, False

			param_list = components[1].split(PARAM_DELIM)

			for param in param_list:
				param = param.strip().lower()

				# first check to see if the parameter is a direction value
				if param in VALID_DIRECTIONS:
					params["dir"] = DIRECTIONS_MAP[param]
				else:
					# next check to see if parameter encodes a location
					coordinate = re.match(r"\((\d+),\s*(\d+)\)", param)
					if coordinate:
						avenue = int(coordinate.group(1))
						street = int(coordinate.group(2))
						params["loc"] = (avenue, street)
					else:
						# finally check to see if parameter encodes a numerical value
						val = None
						if param.isdigit():
							val = int(param)
						elif keyword == "speed":
							# double values are only allowed for speed parameter
							try:
								val = int(100 * float(param))
							except ValueError:
								# invalid parameter value, do not process
								continue
						elif keyword == "beeperbag":
							# handle the edge case where Karel has infinite beepers
							if param == "infinity" or param == "infinite":
								val = INFINITY
						# only store non-null numerical value
						if val is not None: params["val"] = val

			return keyword.lower(), params, True


		for i, line in enumerate(self._world_file):
			keyword, params, is_valid = parse_line(line)

			# skip invalid lines (comments, incorrectly formatted, invalid keyword)
			if not is_valid:
				# print(f"Ignoring line {i} of world file: {line.strip()}")
				continue

			# TODO: add error detection for keywords with insufficient parameters

			# handle all different possible keyword cases
			if keyword == "dimension":
				# set world dimensions based on location values
				self._num_avenues, self._num_streets = params["loc"]

			elif keyword == "wall":
				# build a wall at the specified location
				avenue, street = params["loc"]
				direction = params["dir"]
				self._walls.add(Wall(avenue, street, direction))

			elif keyword == "beeper":
				# add the specified number of beepers to the world
				avenue, street = params["loc"]
				count = params["val"]
				self._beepers[(avenue, street)] += count

			elif keyword == "karel":
				# Give Karel initial state values
				avenue, street = params["loc"]
				direction = params["dir"]
				self._karel_starting_location = (avenue, street)
				self._karel_starting_direction = direction

			elif keyword == "beeperbag":
				# Set Karel's initial beeper bag count
				count = params["val"]
				self._karel_starting_beeper_count = count

			elif keyword == "speed":
				# Set delay speed of program execution
				speed = params["val"]
				self._init_speed = speed

	def add_beeper(self, avenue, street):
		self._beepers[(avenue, street)] += 1

	def remove_beeper(self, avenue, street):
		if self._beepers[(avenue, street)] == 0:
			# TODO: throw an error here
			return
		self._beepers[(avenue, street)] -= 1

	def wall_exists(self, avenue, street, direction):
		wall = Wall(avenue, street, direction)
		return wall in self._walls

	def in_bounds(self, avenue, street):
		return avenue > 0 and street > 0 and avenue <= self._num_avenues and street <= self._num_streets

	def reset_world(self):
		"""
		Reset initial state of beepers in the world
		"""
		self._beepers = copy.deepcopy(self._init_beepers)

	def reload_world(self, filename):
		"""
		TODO: Do better decomp to not just copy constructor
		"""
		self._world_file = open(filename, 'r')
		
		self._beepers = collections.defaultdict(int)
		self._walls = set()

		self._num_streets = 1
		self._num_avenues = 1

		self._karel_starting_location = (1, 1)
		self._karel_starting_direction = Direction.EAST
		self._karel_starting_beeper_count = 0

		self._init_speed = INIT_SPEED

		self.load_from_file()

		self._init_beepers = copy.deepcopy(self._beepers)
