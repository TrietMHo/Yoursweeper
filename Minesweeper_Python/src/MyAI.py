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
from queue import PriorityQueue
from Action import Action
from collections import defaultdict

class MyAI( AI ):
	def __init__(self, rowDimension, colDimension, totalMines, startX, startY):
		self.__rowDimension = rowDimension
		self.__colDimension = colDimension

		self.__totalMines = totalMines

		self.__target = (rowDimension * colDimension)

		self.__startX = startX
		self.__startY = startY

		self.__currentX = startX
		self.__currentY = startY
		self.__currentMine = totalMines

		self.__lastX, self.__lastY = 0, 0

		self.__board = {(x, y): -1 for y in range(colDimension) for x in range(rowDimension)}
		self.__board[startX, startY] = 0

		self.__visited = {(x, y): False for y in range(colDimension) for x in range(rowDimension)}
		self.__visited[(startX, startY)] = True

		self.__carry = defaultdict(int)

		self.queue = []

	def inBound(self, x: int, y: int):
		"""Checks if a cell coordinate is legal"""
		if 0 <= x < self.__rowDimension and 0 <= y < self.__colDimension:
			return True
		return False

	def neighbors(self, x: int = -1, y: int = -1) -> "Tuple Generator":
		"""Finds all legal neighbors of a cell"""
		nb = []

		if (x, y) == (-1, -1):
			x, y = self.__currentX, self.__currentY

		for i in (-1, 0, 1):
			for j in (-1, 0, 1):
				newX = x + i
				newY = y + j
				if self.inBound(newX, newY) and (i, j) != (0, 0):
					nb.append((newX, newY))

		return nb

	def getCellVal(self, x: int = -1, y: int = -1) ->int:
		"""Get the value of a cell, default value is of current cell"""
		if (x, y) == (-1, -1):
			x, y = self.__currentX, self.__currentY
		return self.__board[(x, y)]

	def setCellVal(self, val: int, x: int = -1, y: int = -1):
		"""Set the value of a cell, default value is to current cell"""
		if (x, y) == (-1, -1):
			x, y = self.__currentX, self.__currentY
		self.__board[(x, y)] = val

	def getVisited(self, x: int, y: int):
		"""Checks if a cell has been visited"""
		return self.__visited[(x, y)]

	def setVisited(self, x: int, y: int):
		"""Marks a cell as visited"""
		self.__visited[(x, y)] = True

	def unVisit(self, x: int, y: int):
		"""Marks a cell as not visited"""
		self.__visited[(x, y)] = False

	def isDefined(self, x: int, y: int):
		if self.__board[(x, y)] == -1:
			return False
		return True

	def updateCurrent(self):
		"""Changes current cell to new coordinate"""
		x, y = self.queue.pop(0)
		self.setCurrentTo(x, y)
		return x, y

	def setCurrentTo(self, x: int, y: int):
		"""Changes the location of the current cell"""
		self.__currentX, self.__currentY = x, y

	def getCarry(self):
		carry = self.__carry[(self.__currentX, self.__currentY)]
		self.__carry[(self.__currentX, self.__currentY)] = 0
		return carry

	def setCarry(self, carry, x, y):
		self.__carry[(x, y)] = carry

	def uncoverIsland(self, val: int):
		"""Uncovers all connected '0' cells and their adjacent cells"""

		if list(self.__board.values()).count(-1) == 0:
			return Action(AI.Action.LEAVE, 0, 0)

		self.setCellVal(val + self.getCarry())
		if self.getCellVal() == 0:
			for row, col in self.neighbors():
				if not self.getVisited(row, col):
					self.setVisited(row, col)
					self.queue.append((row, col))

		if (len(self.queue) == 0) \
				and (list(self.__visited.values()).count(True) != self.__target):
			return self.getIslandCorner()
		else:
			x, y = self.updateCurrent()

		if self.isDefined(x, y):
			return self.uncoverIsland(self.getCellVal(x, y))
		else:
			return Action(AI.Action.UNCOVER, x, y)

	def isCorner(self, x: int , y: int) -> (bool, int, int):
		"""Checks if a cell is a corner"""
		# finds unvisited neighbors
		neighbor = self.neighbors(x, y)
		neighbor = [(i, j) for (i, j) in neighbor if not self.getVisited(i, j)]

		# if there is more than one unvisited neighbor, it is not a corner
		if len(neighbor) != 1:
			return False, None, None

		nx, ny = neighbor[0]
		if x != nx and y != ny:
			return True, nx, ny

		return False, None, None

	def setFlag(self, x: int, y: int):
		"""Marks cell as having a mine"""
		for i, j in self.neighbors(x, y):
			self.unVisit(i, j)
			if self.isDefined(i, j):
				self.setCellVal(self.getCellVal(i, j) - 1, i, j)
			else:
				self.setCarry(-1, i, j)
		self.setVisited(x, y)
		self.setCellVal(-2, x, y)


	def getIslandCorner(self):
		""""""
		for i in range(self.__rowDimension):
			for j in range(self.__colDimension):
				if self.getCellVal(i, j) == 1:
					corner, nx, ny = self.isCorner(i, j)
					if corner:
						self.setFlag(nx, ny)
						self.setCurrentTo(i, j)
						return self.uncoverIsland(self.getCellVal(i, j))

	def printBoard(self):
		"""Prints the board"""
		for i in range(self.__rowDimension):
			[print(self.__board[i, j], end=" ") for j in range(self.__colDimension)]
			print()
		print()

	def getAction(self, number: int) -> "Action Object":
		return self.uncoverIsland(number)

