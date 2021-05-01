# ==============================CS-199==================================
# FILE:			MyAI.py
#
# AUTHOR: 		Justin Chung
#
# DESCRIPTION:	This file contains the MyAI class. You will implement your
#				agent in this file. You will write the 'getAction' function,
#				the constructor, and any additional helper functions.
#
# NOTES: 		- MyAI inherits from the abstract AI class in AI.py.
#
#				- DO NOT MAKE CHANGES TO THIS FILE.
# ==============================CS-199==================================

from AI import AI
from Action import Action


class MyAI(AI):

	def __init__(self, rowDimension, colDimension, totalMines, startX, startY):
		# Board information
		self.__rowDimension = rowDimension
		self.__colDimension = colDimension
		self.__totalMines = totalMines
		self.__startX = startX
		self.__startY = startY

		# Current pointer location
		self.currentX = startX
		self.currentY = startY
		self.currentFlag = totalMines

		# State of the board
		self.value = [[-1 for _col in colDimension] for _row in rowDimension]
		self.visited = [[False for _col in colDimension] for _row in rowDimension]
		self.memo = [[0 for _col in colDimension] for _row in rowDimension]
		self.edge = dict()

		self.visited[startX][startY] = True

		self.islandQueue = []

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
		"""Sets value of (x, y) to val"""
		self.value[x][y] = val

	def getValue(self, x: int, y: int) -> int:
		"""Gets value of cell (x, y)"""
		return self.value[x][y]

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

	###########################################################

	# Edges of island
	###########################################################
	def setEdge(self, coords: (int, int)):
		"""Sets cell coordinates as part of the island's edge"""
		self.edge[coords] = True

	def removeEdge(self, coords: (int, int)):
		"""Removes a coordinates from the list of the island's edge"""
		del self.edge[coords]

	###########################################################

	# Island expansion
	###########################################################
	def markExpandLocation(self, x: int, y: int):
		"""Adds a coordinate into the island queue to visit later"""
		self.islandQueue.append((x, y))

	def expandIsland(self):
		"""Gets the next coordinates to expand"""
		if len(self.islandQueue) == 0:
			return None
		return self.islandQueue.pop(0)
	###########################################################

	def isValid(self, x: int, y: int) -> bool:
		"""Checks if a coordinates is within the board"""
		return 0 <= x < self.__rowDimension and 0 <= y < self.__colDimension

	def getNeighbors(self, x: int, y: int) -> [(int, int)]:
		"""Returns all legal neighbors of cell (x, y)"""
		return [(x + rowDiff, y + colDiff)
				for rowDiff in (-1, 0, 1)
				for colDiff in (-1, 0, 1)
				if self.isValid(x + rowDiff, y + colDiff)
				and (rowDiff, colDiff) != (0, 0)]

	def isUncovered(self, x: int, y: int):
		return self.getValue(x, y) != -1

	def uncoverIsland(self, val: int):
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
				if not self.isVisited(*neighbor):
					self.markExpandLocation(*neighbor)

		# Find expanding location
		expandingLocation = self.expandIsland()
		if expandingLocation is not None:
			self.setCurrent(*expandingLocation)
			if self.isUncovered(*expandingLocation):
				return self.uncoverIsland(self.getValue(*expandingLocation))
			else:
				return Action(AI.Action.UNCOVER, *expandingLocation)
		else:
			return Action(AI.Action.LEAVE)


def getAction(self, number: int) -> "Action Object":
	if self.currentFlag == 0:
		return Action(AI.Action.LEAVE)
	return self.uncoverIsland(number)
