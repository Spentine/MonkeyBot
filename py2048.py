import random

move2048 = {
"up": [
[4, 0], [5, 1], [6, 2], [7, 3],
[8, 4], [9, 5], [10, 6], [11, 7],
[4, 0], [5, 1], [6, 2], [7, 3],
[12, 8], [13, 9], [14, 10], [15, 11],
[8, 4], [9, 5], [10, 6], [11, 7],
[4, 0], [5, 1], [6, 2], [7, 3],
],
"right": [
[2, 3], [6, 7], [10, 11], [14, 15],
[1, 2], [5, 6], [9, 10], [13, 14],
[2, 3], [6, 7], [10, 11], [14, 15],
[0, 1], [4, 5], [8, 9], [12, 13],
[1, 2], [5, 6], [9, 10], [13, 14],
[2, 3], [6, 7], [10, 11], [14, 15],
],
"down": [
[8, 12], [9, 13], [10, 14], [11, 15],
[4, 8], [5, 9], [6, 10], [7, 11],
[8, 12], [9, 13], [10, 14], [11, 15],
[0, 4], [1, 5], [2, 6], [3, 7],
[4, 8], [5, 9], [6, 10], [7, 11],
[8, 12], [9, 13], [10, 14], [11, 15],
],
"left": [[1, 0], [5, 4], [9, 8], [13, 12],
[2, 1], [6, 5], [10, 9], [14, 13],
[1, 0], [5, 4], [9, 8], [13, 12],
[3, 2], [7, 6], [11, 10], [15, 14],
[2, 1], [6, 5], [10, 9], [14, 13],
[1, 0], [5, 4], [9, 8], [13, 12],
],
}

neighboring2048 = [
[0, 4], [1, 5], [2, 6], [3, 7], [4, 8], [5, 9], [6, 10], [7, 11], [8, 12], [9, 13], [10, 14], [11, 15],
[0, 1], [1, 2], [2, 3], [4, 5], [5, 6], [6, 7], [8, 9], [9, 10], [10, 11], [12, 13], [13, 14], [14, 15],
]

class G2048:
  def __init__(self):
    self.board = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    self.score = 0
    self.generateTile()

  def generateTile(self):
    empty = []
    for i in range(16):
      if self.board[i] == 0:
        empty.append(i)
    if len(empty) == 0:
      return None # how did we get here
    self.board[random.choice(empty)] = int(random.choice("1111111112")) # set a random index to a random tile

  def __str__(self):
    values = ["    ", "   2", "   4", "   8", "  16", "  32", "  64", " 128", " 256", " 512", "1024", "2048", "4096",
              "8192", "163_", "327_", "655_", "131_", "262_"]
    return f"{values[self.board[0]]}|{values[self.board[1]]}|{values[self.board[2]]}|{values[self.board[3]]}\n{values[self.board[4]]}|{values[self.board[5]]}|{values[self.board[6]]}|{values[self.board[7]]}\n{values[self.board[8]]}|{values[self.board[9]]}|{values[self.board[10]]}|{values[self.board[11]]}\n{values[self.board[12]]}|{values[self.board[13]]}|{values[self.board[14]]}|{values[self.board[15]]}"

  def move(self, direction):
    if not direction in ["up", "right", "down", "left"]:
      return False
    map = move2048[direction]
    original = [True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True]
    moved = False
    scores = [0, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536, 131072, 262144]
    for i in map:
      if not (self.board[i[0]] == 0 and self.board[i[1]] == 0):
        if self.board[i[1]] == 0: # if tile 1 will move to empty tile
          self.board[i[1]] = self.board[i[0]] # move tile
          original[i[1]] = original[i[0]] # move original attribute
          self.board[i[0]] = 0 # set start tile to 0
          moved = True
        elif (self.board[i[0]] == self.board[i[1]]) and original[i[0]] and original[i[1]]: # if the tiles haven't merged
          self.board[i[1]] = self.board[i[1]] + 1
          self.score += scores[self.board[i[1]]]
          original[i[1]] = False
          self.board[i[0]] = 0
          moved = True
    return moved

  def toString(self):
    conv = "0123456789abcdefghijklmnopqrstuvwxyz"
    result = ""
    for i in self.board:
      result += conv[i]
    result += "." + str(self.score)
    return result

  def fromString(self, string):
    conv = "0123456789abcdefghijklmnopqrstuvwxyz"
    j = 0
    for i in string[:string.index(".")]:
      self.board[j] = conv.index(i)
      j += 1
    self.score = int(string[string.index(".") + 1:])

  def canMove(self):
    if 0 in self.board:
      return True
    for i in neighboring2048:
      if self.board[i[0]] == self.board[i[1]]:
        return True
    return False