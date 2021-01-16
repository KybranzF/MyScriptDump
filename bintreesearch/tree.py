#        1
#      /   \
#     2     3
#    / \   / \
#   4   5 6   7
#  / \		\
# 8   9		10

# als long i have a left neigbor check this neigbor
# if not depth +1

def getNb(value,stri):
	db = []
	if stri == "val":
		db.append(value[0])
		db.append(value[1])
	
	elif stri == "list":
		tmp = []
		for x in value:
			tmp.append(x[0])
			tmp.append(x[1])
		db.append(tmp)
	else:
		exit()

	return db

def getDepth(value, tree, depth):
	# depth = 0
	nb = getNb(value, "val")
	print(value, nb)
	if value[2] == 1:
		return depth+1

	if nb[0] == 0:
		depth+=1
		# print(value[2]-2) 
		print("Depth:", depth)
		return getDepth(tree[value[2]-2],tree,depth)
		
	else:
		return getDepth(tree[nb[0]-1],tree,depth)
	
tree = [[0,0,1],[0,3,2],[2,0,3],[0,5,4],[4,6,5],[5,7,6],[6,0,7],[0,9,8],[8,0,9],[9,0,10]]

print("DEPTH:",getDepth(tree[9],tree,0))
