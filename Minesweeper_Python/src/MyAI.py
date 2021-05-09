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


class MyAI(AI):

	def __init__(self, rowDimension, colDimension, totalMines, startX, startY):
		# Board information
		self.__rowDimension = rowDimension
		self.__colDimension = colDimension
		self.__totalMines = totalMines
		self.__startX = startX
		self.__startY = startY
		self.__target = rowDimension * colDimension - totalMines
		self.request = 1

		# Current pointer location
		self.currentX = startX
		self.currentY = startY
		self.currentFlag = totalMines

		# State of the board
		self.value = [[-1 for _col in range(colDimension)] for _row in range(rowDimension)]
		self.visited = [[False for _col in range(colDimension)] for _row in range(rowDimension)]
		self.memo = [[0 for _col in range(colDimension)] for _row in range(rowDimension)]
		self.edge = dict()

		self.visited[startX][startY] = True

		self.islandQueue = []
		self.mineQueue = []


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

	###########################################################


	# Edges
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
					if not self.isMine(*neighbor):
						self.plant(*neighbor, edge)

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
				or self.isMine(*coords)]

	###########################################################


	# Working with mines
	###########################################################
	def isMine(self, x: int, y: int) -> bool:
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

	def plant(self, x: int, y: int, planter: (int, int)):
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

			# Move pointer to planter (cell which puts the mine there)
			self.setCurrent(*planter)

			# Resets all the eligible neighbor to original condition
			for neighbor in self.getNeighbors(x, y):
				if not self.isMine(*neighbor) and not self.isDefused(*neighbor):
					if self.isUncovered(*neighbor):
						self.setValue(*neighbor, self.getValue(*neighbor) - 1)
						self.unvisit(*neighbor)
						self.removeEdge(neighbor)
					else:
						# But remember for those who are still covered what value they will be in the future
						self.setMemo(*neighbor, self.getMemo(*neighbor) - 1)
				self.setValue(x, y, -3)
			return self.getValue(*self.getCurrent())
		else:
			return None

	###########################################################


	# Misc methods
	###########################################################
	def isUncovered(self, x: int, y: int) -> bool:
		"""Checks if a coordinates is already covered"""
		return self.getValue(x, y) != -1

	def isValid(self, x: int, y: int) -> bool:
		"""Checks if a coordinates is within the board"""
		return 0 <= x < self.__rowDimension and 0 <= y < self.__colDimension
	###########################################################


	# General processes
	###########################################################
	def solve(self, value: int) -> "Action Object":

		if len(self.islandQueue) == 0:
			defusedValue = self.defuse() 
			if defusedValue is not None:
				value = defusedValue

		action = self.uncoverIsland(value)

		#Island is set, start looking for perfect edge
		if action is None:
			existsPerfectEdge = self.expandPerfectEdge()
			if existsPerfectEdge:
				action = self.getAction(self.getValue(*self.getCurrent()))
			else:
				action = Action(AI.Action.LEAVE)
		return action
	###########################################################


	def printb(self):
		for i in range(self.__rowDimension-1, -1, -1):
			for j in range(self.__colDimension):
				print(str(self.getValue(j, i)).rjust(3), end=" ")
			print()
			print()
		print()
		print([(i[0]+1, i[1]+1) for i in list(self.edge.keys())])
		print('-----------------')

	# Main action method
	###########################################################
	def getAction(self, number: int) -> "Action Object":
		#self.printb()
		if self.targetMet():
			return Action(AI.Action.LEAVE)
		return self.solve(number)

	###########################################################
