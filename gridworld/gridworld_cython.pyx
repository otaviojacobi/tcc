# distutils: language = c++
# cython: language_level=3

cdef char UP = 0
cdef char DOWN = 1
cdef char RIGHT = 2
cdef char LEFT = 3

cdef moves = [UP, DOWN, RIGHT, LEFT]

cdef class GridWorld:
    cdef int curX
    cdef int curY
    cdef int maxX
    cdef int maxY
    cdef int goalX
    cdef int goalY
    cdef int isOver

    def __init__(self, int size, int goalX=0, int goalY=0, int startX=0, int startY=0):
        self.curX = startX
        self.curY = startY
        self.goalX = goalX
        self.goalY = goalY
        self.maxX = size
        self.maxY = size
        self.isOver = False

    cpdef step(self, char action):

        if self.isOver:
            return (self.curX, self.curY), 0.0, True

        if action == UP:
            self.curX = min(self.curX + 1, self.maxX)
        elif action == DOWN:
            self.curX = max(self.curX - 1, 0)
        elif action == RIGHT:
            self.curY = min(self.curY + 1, self.maxY)
        elif action == LEFT:
            self.curY = max(self.curY - 1, 0)

        if self.curX == self.goalX and self.curY == self.goalY:
            self.isOver = True
            return (self.curX, self.curY), 1000.0, True

        return (self.curX, self.curY), -1.0, False

    cpdef copy(self):
        g = GridWorld(self.maxX, self.goalX, self.goalY, self.curX, self.curY)
        g.set_over(self.isOver)
        return g

    cpdef is_over(self):
        return self.isOver

    cpdef set_over(self, value):
        self.isOver = value

    cpdef state(self):
        return (self.curX, self.curY)

    cpdef legal_moves(self):
        if self.curX == self.goalX and self.curY == self.goalY:
            return []
        return moves
