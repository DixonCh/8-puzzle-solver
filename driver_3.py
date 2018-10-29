from collections import deque
import time
import resource
import sys
import heapq

class State:
	goal = (0,1,2,3,4,5,6,7,8)
	node_expanded = 0
	path_to_goal = []
	max_search_depth = 0
	cost_of_path = 0
	search_depth = 0
	method = None

	directions = { 0 : "Up", 1: "Down", 2:"Left", 3: "Right"}

	def __init__(self, value, path, rootNode, depthOfNode):
		self.value = value
		#path to root
		self.path = path
		self.rootNode = rootNode
		self.depthOfNode = depthOfNode

		if(State.max_search_depth < self.depthOfNode):
			State.max_search_depth = self.depthOfNode

		self.indexOfZero = self.value.index(0)
		self.valueInTuple = tuple(self.value)
		self.child = []

	def goalTest(self):
		if (self.valueInTuple == self.goal):
			return True

	def getHeuristic(self):
		md = 0

		for tile in self.value:
			index = self.value.index(tile)
			correct_row = tile/3
			correct_col = tile%3
			current_row = index/3
			current_col = index%3			
			md += abs(correct_row - current_row) + abs(correct_col- current_col)
		return md

	def possible_moves(self):

		if(State.method == "dfs"):
			possible_directions = ([3,2,1,0])
		else:
			possible_directions = ([0,1,2,3])

		if((self.indexOfZero+1) % 3 == 0): #Right
			possible_directions.remove(3)
		if(self.indexOfZero % 3 == 0): #Left
			possible_directions.remove(2)  
		if(self.indexOfZero >= 6): #Down
			possible_directions.remove(1)	
		if(self.indexOfZero < 3): #Up
			possible_directions.remove(0)

		return (possible_directions)

	def generate_Neighbors(self):

		depth = 1
		if(self.rootNode != None):
			depth = self.depthOfNode + 1

		for d in self.possible_moves():
			if (d == 0): #swap up
				temp_state = list(self.value)
				index = self.indexOfZero
				temp_state[index], temp_state[index-3] = temp_state[index-3], temp_state[index]
				self.child.append(State(temp_state, d, self, depth))

			if (d == 1): #swap down
				temp_state = list(self.value)
				index = self.indexOfZero
				temp_state[index], temp_state[index+3] = temp_state[index+3], temp_state[index]
				self.child.append(State(temp_state, d, self, depth))

			if (d == 2): #swap left
				temp_state = list(self.value)
				index = self.indexOfZero
				temp_state[index], temp_state[index-1] = temp_state[index-1], temp_state[index]
				self.child.append(State(temp_state, d, self, depth))

			if (d == 3): #swap right
				temp_state = list(self.value)
				index = self.indexOfZero
				temp_state[index], temp_state[index+1] = temp_state[index+1], temp_state[index]
				self.child.append(State(temp_state, d, self, depth))


class Solver(State):
	def bfs(self):
		frontier = deque()
		frontier.append(self)
		explored = set()

		while(len(frontier) > 0):
			node = frontier.popleft()
			explored.add(node.valueInTuple)
			
			if(node.goalTest()):
				self.search_depth = node.depthOfNode
				while(node.rootNode != None):
					self.path_to_goal = [self.directions[node.path]] + self.path_to_goal
					node = node.rootNode

				self.cost_of_path = len(self.path_to_goal)
				return True
			explored.add(node.valueInTuple)

			self.node_expanded += 1
			node.generate_Neighbors()
			for n in (node.child):
				if n.valueInTuple not in explored:
					frontier.append(n)
					explored.add(n.valueInTuple)

	def dfs(self):
		frontier = []
		frontier.append(self)
		explored = set()

		while(len(frontier) > 0):
			node = frontier.pop()
			explored.add(node.valueInTuple)
			
			if(node.goalTest()):
				self.search_depth = node.depthOfNode
				while(node.rootNode != None):
					self.path_to_goal = [self.directions[node.path]] + self.path_to_goal
					node = node.rootNode

				self.cost_of_path = len(self.path_to_goal)
				return True
			explored.add(node.valueInTuple)

			self.node_expanded += 1
			node.generate_Neighbors()
			for n in (node.child):
				if n.valueInTuple not in explored:
					frontier.append(n)
					explored.add(n.valueInTuple)


	def ast(self):
		hashed = {}

		frontier = []
		heapq.heapify(frontier)
		key = self.getHeuristic() + self.depthOfNode

		heapq.heappush(frontier, key)
		hashed.setdefault(key, [])
		hashed[key].append(self)
		explored = set()

		while len(frontier) > 0:
			node_key = heapq.heappop(frontier)
			node = hashed[node_key][0]

			del hashed[node_key][0]

			explored.add(node.valueInTuple)
			

			if(node.goalTest()):
				self.search_depth = node.depthOfNode
				while(node.rootNode != None):
					self.path_to_goal = [self.directions[node.path]] + self.path_to_goal
					node = node.rootNode

				self.cost_of_path = len(self.path_to_goal)
				return True
			
			explored.add(node.valueInTuple)		
			self.node_expanded += 1

			node.generate_Neighbors()
			for n in (node.child):
				if n.valueInTuple not in explored:
					key = n.getHeuristic() + n.depthOfNode

					heapq.heappush(frontier, key)
					hashed.setdefault(key, [])

					hashed[key].insert(0,n)
					explored.add(n.valueInTuple)	


def main():
	start_time = time.time()

	State.method = sys.argv[1]
	board = sys.argv[2]
	board = list(map(int, board.split(',')))

	# board = [8,6,4,2,1,3,5,7,0]
	initialState = Solver(board, None, None, 0)
	if (State.method == "bfs"):
		initialState.bfs()
	elif (State.method == "dfs"):
		initialState.dfs()
	elif (State.method == "ast"):
		initialState.ast() 

	max_ram = (resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/float(1024*1024))
	
	# print("path_to_goal: {}".format(initialState.path_to_goal))
	# print("cost_of_path: %s" %(initialState.cost_of_path))
	# print("nodes_expanded: %s" %(initialState.node_expanded))
	# print("search_depth: %s" %(initialState.search_depth))
	# print("max_search_depth: %s" %(State.max_search_depth))

	# print("running_time: %.8f" %(time.time() - start_time))
	# print("max_ram_usage: %.8f" %(max_ram))#KB

	output = open("Output.txt", "w")
	output.write("path_to_goal: {}".format(initialState.path_to_goal))
	output.write("\ncost_of_path: %s" %(initialState.cost_of_path))
	output.write("\nnodes_expanded: %s" %(initialState.node_expanded))
	output.write("\nsearch_depth: %s" %(initialState.search_depth))
	output.write("\nmax_search_depth: %s" %(State.max_search_depth))

	output.write("\nrunning_time: %.8f" %(time.time() - start_time))
	output.write("\nmax_ram_usage: %.8f" %(max_ram))#KB
	output.close()

if __name__ == "__main__":
	main()