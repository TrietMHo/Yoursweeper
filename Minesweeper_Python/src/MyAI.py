# ==============================CS-171==================================
# FILE:			MyAI.py
#
# AUTHORS: 		Triet Ho, Derek Dang
#
# DESCRIPTION:	This file contains the MyAI class. You will implement your
#				agent in this file. You will write the 'getAction' function,
#				the constructor, and any additional helper functions.
#
# NOTES: 		- MyAI inherits from the abstract AI class in AI.py.
#
#				- DO NOT MAKE CHANGES TO THIS FILE.
# ==============================CS-171==================================
from AI import AI
from Action import Action
from random import random as rand


class MyAI(AI):

	def __init__(self, rowDimension, colDimension, totalMines, startX, startY):
		# Board information
		self.__rowDimension = colDimension
		self.__colDimension = rowDimension
		self.__totalMines = totalMines
		self.__startX = startY
		self.__startY = startX
		self.__target = rowDimension * colDimension - totalMines
		self.request = 1

		# Current pointer location
		self.currentX = startX
		self.currentY = startY
		self.currentFlag = totalMines

		# State of the board
		self.value = [[-1 for _col in range(self.__colDimension)] for _row in range(self.__rowDimension)]
		self.visited = [[False for _col in range(self.__colDimension)] for _row in range(self.__rowDimension)]
		self.memo = [[0 for _col in range(self.__colDimension)] for _row in range(self.__rowDimension)]
		self.edge = dict()

		self.visited[startX][startY] = True

		self.islandQueue = []
		self.mineQueue = []

		self.checkResult = dict()
		self.skipAhead = set()

		self.worldCount = 0

		self.splitFrontiers = []
		self.randPick = (startX, startY)


	# Exit condition
	###########################################################
	def targetMet(self) -> bool:
		"""Provides the condition for the program to leave"""
		return self.currentFlag == 0 and self.request == self.__target

	###########################################################


	# Current cell
	###########################################################
	def setCurrent(self, x: int, y: int):
		"""Changes current pointer location"""
		self.currentX, self.currentY = x, y

	def getCurrent(self) -> (int, int):
		"""Gets the current pointer location"""
		return self.currentX, self.currentY

	###########################################################


	# Value of cells
	###########################################################
	def setValue(self, x: int, y: int, val: int):
		"""
		Sets value of (x, y) to val
		-1 is covered,
		-2 is flagged,
		-3 is mine
		"""
		self.value[x][y] = val

	def getValue(self, x: int, y: int) -> int:
		"""Gets value of cell (x, y)"""
		return self.value[x][y]

	def isUncovered(self, x: int, y: int) -> bool:
		"""Checks if a coordinates is already covered"""
		return self.getValue(x, y) != -1

	###########################################################

	# Pattern Matching
	###########################################################
	"""
		Pattern:
			S: safe to open
			.: any value
			K: known value
			M: is definitely a mine
	"""

	def patternMatching(self) -> bool:
		"""Finds a pattern on the board. Returns True if a pattern is found."""
		for e in self.edge:

			# Pattern 1 checking (12KKM). Plants flags
			m = self.pattern1(*e)
			if m is not None:
				xy, planter = m
				self.plant(planter, *xy)
				return True

			# Pattern 2 checking (11KKK). Marks safe location
			m = self.pattern2(*e)
			if m is not None and m != []:
				for tbu in m:  # to be uncovered
					self.skipAhead.add(tbu)
				return True

		return False

	def pattern1(self, x: int, y: int) -> [(int, int)]:
		"""
		Matches Pattern
			SSS        SSS        SSS
			.1.   or   .1.   or   .1.
			.2.        .2.        .2.
			KKM        KMK        MKK
		and all of its rotations
		converting it to pattern2
		returns location of the mine and the cell with value 2
		"""
		def matching(f1: "def f", f2: "def f", f3: "def f", cx: int, cy: int) -> ((int, int), (int, int)):
			"""Local function to find match pattern with specific direction"""
			# Main direction: f2:
			mid = f2(cx, cy)
			edge1 = None if mid is None else f1(*mid)
			edge2 = None if mid is None else f3(*mid)
			n = [mid is None or self.isUncovered(*mid),
				 edge1 is None or self.isUncovered(*edge1),
				 edge2 is None or self.isUncovered(*edge2)]
			return ([mid, edge1, edge2][n.index(False)], (cx, cy)) if n.count(False) == 1 else None

		# Find the location of 1 and look around to find a 2
		# And try to match pattern if found
		if self.getValue(x, y) == 1:
			if self.topOf(x, y) is not None and self.getValue(*self.topOf(x, y)) == 2:
				return matching(self.rightOf, self.topOf, self.leftOf, *self.topOf(x, y))
			elif self.rightOf(x, y) is not None and self.getValue(*self.rightOf(x, y)) == 2:
				return matching(self.topOf, self.rightOf, self.bottomOf, *self.rightOf(x, y))
			elif self.bottomOf(x, y) is not None and self.getValue(*self.bottomOf(x, y)) == 2:
				return matching(self.leftOf, self.bottomOf, self.rightOf, *self.bottomOf(x, y))
			elif self.leftOf(x, y) is not None and self.getValue(*self.leftOf(x, y)) == 2:
				return matching(self.topOf, self.leftOf, self.bottomOf, *self.leftOf(x, y))
			else:
				return None

	def pattern2(self, x: int, y: int) -> [(int, int)]:
		"""
		Matches Pattern
			SSS
			.1.
			.1.
			KKK
		and all of its rotations
		"""
		def isWall(vert: bool, coords: (int, int)) -> bool:
			"""Verifies the safeness of the 3 cells perpendicular to the direction of inspection"""
			if coords is None:
				return True

			# Direction of inspection is vertical
			if vert:
				wallLeft = self.leftOf(*coords)
				wallRight = self.rightOf(*coords)
				if (wallLeft is None or self.isUncovered(*wallLeft)) \
					and (wallRight is None or self.isUncovered(*wallRight)):
					return True
				return False

			# Direction of inspection is horizontal
			wallTop = self.topOf(*coords)
			wallBottom = self.bottomOf(*coords)
			if (wallTop is None or self.isUncovered(*wallTop)) \
				and (wallBottom is None or self.isUncovered(*wallBottom)):
				return True
			return False

		def getWall(vert: bool, coords: (int, int)) -> [(int, int)]:
			"""Returns the 3 cells perpendicular to the direction of inspection"""
			if coords is None:
				return []
			if vert:
				return [self.leftOf(*coords), coords, self.rightOf(*coords)]
			return [self.topOf(*coords), coords, self.bottomOf(*coords)]

		def opposite(direction: "def f") -> "def f":
			"""Returns the opposite direction in the form of a function"""
			if direction == self.topOf:
				return self.bottomOf
			elif direction == self.bottomOf:
				return self.topOf
			elif direction == self.leftOf:
				return self.rightOf
			else:
				return self.leftOf

		def getSafe(direction: "def f", cx: int, cy: int) -> [(int, int)]:
			"""Returns the safe covered locations if the pattern is matched"""
			newLocation = direction(cx, cy)
			# Pattern not matched
			if newLocation is None or self.getValue(*newLocation) != 1:
				return None
			return [c for c in getWall(direction in (self.topOf, self.bottomOf), direction(*newLocation))
					if c is not None and self.isValid(*c) and not self.isUncovered(*c)]


		def walk(direction: "def f", cx: int, cy: int) -> [(int, int)]:
			"""Inspects the area around cx, cy to find the pattern"""
			wallMid = direction(cx, cy)
			if wallMid is None or self.isUncovered(*wallMid):
				if isWall(direction in (self.topOf, self.bottomOf), wallMid):
					return getSafe(opposite(direction), cx, cy)

		if self.getValue(x, y) == 1:
			for d in (self.topOf, self.leftOf, self.rightOf, self.bottomOf):
				retVal = walk(d, x, y)
				if retVal is not None:
					return retVal

	###########################################################


	# Memo for covered cells
	###########################################################
	def setMemo(self, x: int, y: int, val: int):
		"""Sets remembered value to add to covered cell"""
		self.memo[x][y] = val

	def getMemo(self, x: int, y: int) -> int:
		"""Gets remembered value to add to covered cell"""
		return self.memo[x][y]

	def applyMemo(self, x: int, y: int) -> int:
		"""Gets the memo of a cell and erase the memo because it is already applied"""
		memo = self.getMemo(x, y)
		self.setMemo(x, y, 0)
		return memo

	###########################################################


	# Visiting cells
	###########################################################
	def visit(self, x: int, y: int):
		"""Marks a cell as visited"""
		self.visited[x][y] = True

	def unvisit(self, x: int, y: int):
		"""Marks a cell as unvisited"""
		self.visited[x][y] = False

	def isVisited(self, x: int, y: int) -> bool:
		"""Checks if a cell is visited"""
		return self.visited[x][y]

	def leftOf(self, x: int, y: int) -> (int, int):
		"""Finds the cell to the left of (x, y)"""
		return (x-1, y) if self.isValid(x-1, y) else None

	def rightOf(self, x: int, y: int):
		"""Finds the cell to the right of (x,y)"""
		return (x+1, y) if self.isValid(x+1, y) else None

	def topOf(self, x: int, y: int):
		"""Finds the cell to the top of (x, y)"""
		return (x, y - 1) if self.isValid(x, y - 1) else None

	def bottomOf(self, x: int, y: int):
		"""Finds the cell to the bottom of (x, y)"""
		return (x, y + 1) if self.isValid(x, y + 1) else None

	###########################################################


	# Edges and Frontiers
	###########################################################
	def setEdge(self, coords: (int, int)):
		"""Sets cell coordinates as part of the island's edge"""
		self.edge[coords] = True

	def removeEdge(self, coords: (int, int)):
		"""Removes a coordinates from the list of the island's edge"""
		if self.isEdge(coords):
			del self.edge[coords]

	def isEdge(self, coords: (int, int)) -> bool:
		"""Checks if a coordinates belong to an island's edge"""
		return coords in self.edge

	def getFrontier(self) -> {(int, int)}:
		"""Returns the unknown cells along the edges"""
		frontier = set()
		for edge in self.edge:
			for neighbor in self.getUnknownNeighbors(*edge):
				frontier.add(neighbor)
		return frontier

	def splitFrontier(self) -> [{(int, int)}]:
		"""Returns a set of independent frontiers (set of coordinates)"""
		frontiers = []
		frontierExpanding = []
		mergedFrontier = self.getFrontier()
		while mergedFrontier != set():
			c = mergedFrontier.pop()
			newFrontier = {c, }
			frontierExpanding += [n for n in self.getNeighbors(*c) if n in mergedFrontier]
			while frontierExpanding:
				c2 = frontierExpanding.pop(0)
				newFrontier.add(c2)
				mergedFrontier.discard(c2)
				frontierExpanding += [n for n in self.getNeighbors(*c2) if n in mergedFrontier]
			frontiers.append(newFrontier)

		self.splitFrontiers = frontiers

	###########################################################


	# Island of 0 logic
	###########################################################
	def markExpandLocation(self, x: int, y: int):
		"""Adds a coordinate into the island queue to visit later"""
		self.visit(x, y)
		if self.isEdge((x, y)):
			self.removeEdge((x, y))
		self.islandQueue.append((x, y))

	def expandIsland(self):
		"""Gets the next coordinates to expand"""
		if len(self.islandQueue) == 0:
			return None
		return self.islandQueue.pop(0)

	def uncoverIsland(self, val: int) -> "Action Object" or None:
		"""Uncovers patch of 0's and their adjacent"""
		currentCell = self.getCurrent()

		# Update value of current cell

		self.setValue(*currentCell, val + self.applyMemo(*currentCell))
		# If value is not zero, it's part of the island's edge
		# Else expand island
		if self.getValue(*currentCell) != 0:
			self.edge[currentCell] = True
		else:
			for neighbor in self.getNeighbors(*currentCell):
				if not self.isVisited(*neighbor) or self.isEdge(neighbor):
					self.markExpandLocation(*neighbor)

		# Find expanding location
		expandingLocation = self.expandIsland()

		# Check if island queue is empty
		if expandingLocation is not None:
			self.setCurrent(*expandingLocation)

			# If cell already uncovered, move on
			# Else uncover the cell
			if self.isUncovered(*expandingLocation):
				return self.uncoverIsland(self.getValue(*expandingLocation))
			else:
				self.request += 1
				return Action(AI.Action.UNCOVER, *expandingLocation)

		else:
			return None

	def expandPerfectEdge(self) -> bool:
		"""
			Plant flags around a cell where its value is equal to its covered neighbor
			This means that everything around them are mines
		"""
		existsPerfectEdge = False

		for edge in self.edge.keys():
			emptyNeighbors = self.getUnknownNeighbors(*edge)
			if len(emptyNeighbors) == self.getValue(*edge):
				existsPerfectEdge = True
				for neighbor in emptyNeighbors:
					if not self.isFlagged(*neighbor):
						self.plant(edge, *neighbor)

		return existsPerfectEdge

	###########################################################


	# Neighbors
	###########################################################
	def getNeighbors(self, x: int, y: int) -> [(int, int)]:
		"""Returns all legal neighbors of cell (x, y)"""
		return [(x + rowDiff, y + colDiff)
				for rowDiff in (-1, 0, 1)
				for colDiff in (-1, 0, 1)
				if self.isValid(x + rowDiff, y + colDiff)
				and (rowDiff, colDiff) != (0, 0)]

	def getUnknownNeighbors(self, x: int, y: int) -> [(int, int)]:
		"""Returns all legal neighbors of cell (x, y) that is still covered"""
		return [coords for coords in self.getNeighbors(x, y)
				if not self.isUncovered(*coords)
				or self.isFlagged(*coords)]

	@staticmethod
	def isNeighbor(c1: (int, int), c2: (int, int)) -> bool:
		"""Checks if c1 and c2 are neighbors"""
		if c1 == c2:
			return False

		x1, y1 = c1
		x2, y2 = c2
		if abs(x1-x2) <= 1 and abs(y1-y2) <= 1:
			return True

		return False

	###########################################################


	# Working with mines
	###########################################################
	def isFlagged(self, x: int, y: int) -> bool:
		"""Checks if a coordinates contains a flag"""
		return self.getValue(x, y) == -2

	def isDefused(self, x: int, y: int) -> bool:
		"""Checks if a mine is defused"""
		return self.getValue(x, y) == -3

	def getMine(self):
		"""Pops a mine from the queue to process"""
		if len(self.mineQueue) == 0:
			return None
		return self.mineQueue.pop(0)

	def plant(self, planter: (int, int), x: int, y: int):
		"""Puts down a flag at coordinate (x, y)"""
		self.visit(x, y)
		self.setValue(x, y, -2)
		self.currentFlag -= 1
		self.mineQueue.append((x, y, planter))

	def defuse(self) -> int or None:
		"""Defuses a mine to continue expanding island"""
		mine = self.getMine()
		# If there is mine to defuse
		if mine is not None:
			x, y, planter = mine
			if self.isDefused(x, y):
				return None

			# Move pointer to planter (cell which puts the mine there)
			self.setCurrent(*planter)

			# Resets all the eligible neighbor to original condition
			for neighbor in self.getNeighbors(x, y):
				if not self.isFlagged(*neighbor) and not self.isDefused(*neighbor):
					if self.isUncovered(*neighbor):
						self.setValue(*neighbor, self.getValue(*neighbor) - 1)
						self.unvisit(*neighbor)
						if self.getValue(*neighbor) == 0:
							self.removeEdge(neighbor)
							self.islandQueue.append(neighbor)
					else:
						# But remember for those who are still covered what value they will be in the future
						self.setMemo(*neighbor, self.getMemo(*neighbor) - 1)

				self.setValue(x, y, -3)
			return self.getValue(*self.getCurrent())
		else:
			return None

	###########################################################


	# Model Checking
	###########################################################
	def modelCheck(self) -> bool:
		board = [r.copy() for r in self.value]

		#if len(self.splitFrontiers) == 0:
		#	return False

		#frontier = self.splitFrontiers.pop(0)
		frontier = self.getFrontier()

		self.checkResult = {f: 0 for f in frontier}
		self.worldCount = 0

		self.put(board, frontier, self.__totalMines, set())

		mx = 2**1000
		loc = None
		retVal = False

		for fk, fv in self.checkResult.items():
			if fv < mx:
				mx = fv
				loc = fk
				retVal = True
			elif fv == 0:
				self.skipAhead.add(fk)
			#elif fv == self.worldCount:
			#	self.plant([n for n in self.getNeighbors(*fk) if self.isValid(*n)][0], *loc)
			#	retVal = True
			if fv == mx and rand() > 0.75:
				loc = fk
                                
		self.skipAhead.add(loc)
		return retVal



	def put(self, board, frontier, mine, mineSet):
		if len(frontier) == 0 or mine == 0:
			if self.verify(board):
				self.worldCount += 1
				for m in mineSet:
					self.checkResult[m] += 1
			return

		examine = frontier.pop()

		self.put([r.copy() for r in board], frontier.copy(), mine, mineSet.copy())

		for neighborX, neighborY in self.getNeighbors(*examine):
			board[neighborX][neighborY] -= 1
			if board[neighborX][neighborY] < 0 and (neighborX, neighborY) in self.edge:
				return
		self.put([r.copy() for r in board], frontier.copy(), mine - 1, mineSet | {examine, })


	def verify(self, board):
		for e in self.edge:
			if board[e[0]][e[1]] != 0:
				return False
		return True




	###########################################################


	# General processes
	###########################################################
	def solve(self, value: int) -> "Action Object":

		if len(self.islandQueue) == 0:
			defusedValue = self.defuse()
			if defusedValue is not None:
				value = defusedValue

		action = self.uncoverIsland(value)

		if action is None:
			# Can we open more tiles?
			if self.skipAhead != set():
				openCell = self.skipAhead.pop()
				self.visit(*openCell)
				self.setCurrent(*openCell)
				return Action(AI.Action.UNCOVER, *openCell)

			# Island is set, start looking for perfect edge
			existsPerfectEdge = self.expandPerfectEdge()
			if existsPerfectEdge:
				action = self.getAction(self.getValue(*self.getCurrent()))
			else:
				# If no perfect edge is found, starts looking for known patterns
				if self.patternMatching():
					action = self.solve(self.getValue(*self.getCurrent()))
				else:
					# Model checking
					#if len(self.splitFrontiers) == 0:
					#	self.splitFrontier()
					if self.modelCheck():
						action = self.solve(self.getValue(*self.getCurrent()))
					else:
						# Don't know what to do, dip
						action = Action(AI.Action.LEAVE)

		return action

	###########################################################


	# Misc methods
	############################################################
	def isValid(self, x: int, y: int) -> bool:
		"""Checks if a coordinates is within the board"""
		return 0 <= x < self.__rowDimension and 0 <= y < self.__colDimension

	###########################################################

	# Main action method
	###########################################################
	def getAction(self, number: int) -> "Action Object":
		if self.targetMet():
			return Action(AI.Action.LEAVE)
		return self.solve(number)

	###########################################################
