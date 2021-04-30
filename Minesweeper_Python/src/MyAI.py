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


class MyAI( AI ):

	def __init__(self, rowDimension, colDimension, totalMines, startX, startY):
	#
		self.__rowDimension = rowDimension
		self.__colDimension = colDimension
		self.__totalMines = totalMines
		self.__startX = startX
		self.__startY = startY

		self.__currentX = startX
		self.__currentY = startY
		self.__currentMine = totalMines

		self.__board = dict()
		self.__board[startX, startY] = 0

		self.__visited = {(x, y): False for y in range(1, colDimension+1) for x in range(1, rowDimension+1)}
		self.__visited[(startX, startY)] = True;
	#

	@staticmethod
	def __inBound(x: int, high: int, low: int = 0):
	#
		return low < x < high + 1
	#

	def getAdjacent(self, x: int, y: int) -> (int, int):
	#
		for i in (-1, 0, 1):
			for j in (-1, 0, 1):
				if (x,y) != (x+i, y+j) \
					and self.__inBound(x+i, self.__rowDimension) \
					and self.__inBound(y+j, self.__colDimension):
					yield x+i, y+j
	#

	def processNode(self):
	#
		x = self.__currentX
		y = self.__currentY
		for (row, col) in tuple(self.getAdjacent(x, y)):

		return None
	#

	def getAction(self, number: int) -> "Action Object":
	#


		return None
	#

