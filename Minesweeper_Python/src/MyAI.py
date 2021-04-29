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

		self.__rowDimension = rowDimension
		self.__colDimension = colDimension
		self.__totalMines = totalMines
		self.__startX = startX
		self.__startY = startY

		self.__currentX = startX
		self.__currentY = startY

		self.

		
	def getAction(self, number: int) -> "Action Object":

		########################################################################
		#							YOUR CODE BEGINS						   #
		########################################################################
		return Action(AI.Action.LEAVE)
		########################################################################
		#							YOUR CODE ENDS							   #
		########################################################################
