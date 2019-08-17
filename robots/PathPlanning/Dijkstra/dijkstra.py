import numpy as np
import math

def dijkstras(occupancy_map, x_spacing, y_spacing, start, goal):

    goal_found = False


    delta = [[-1, 0],  # go up
             [0, -1],  # go left
             [1, 0],  # go down
             [0, 1]]  # go right



    # Each node on the map "costs" 1 step to reach.
    cost = 1

    # Convert numpy array of map to list of map, makes it easier to search.
    occ_map = occupancy_map.tolist()


    # Converge start and goal positions to map indices.
    x = int(math.ceil((start.item(0) / x_spacing) ))  # startingx
    y = int(math.ceil((start.item(1) / y_spacing) ))  # startingy
    goalX = int(math.ceil((goal.item(0) / x_spacing) ))
    goalY = int(math.ceil((goal.item(1) / y_spacing) ))
    print ("Start Pose: ", x, y)
    print ("Goal Pose: ", goalX, goalY)

    # Make a map to keep track of all the nodes and their cost distance values.
    possible_nodes = [[0 for row in range(len(occ_map[0]))] for col in range(len(occ_map))]
    row = y
    col = x

    # Show the starting node and goal node.
    # 5 looks similar to S and 6 looks similar to G.
    possible_nodes[row][col] = 5



    # The g_value will count the number of steps each node is from the start.
    # Since we are at the start node, the total cost is 0.
    g_value = 0
    frontier_nodes = [(g_value, col, row)] # dist, x, y
    searched_nodes = []
    parent_node = {}  # Dictionary that Maps {child node : parent node}
    loopcount = 0

    while len(frontier_nodes) != 0:

        frontier_nodes.sort(reverse=True) #sort from shortest distance to farthest
        current_node = frontier_nodes.pop()


        if current_node[1] == goalX and current_node[2] == goalY:
            print ("Goal found!")
            goal_found = True

            break
        g_value, col, row = current_node

        # Check surrounding neighbors.
        for i in delta:
            possible_expansion_x = col + i[0]
            possible_expansion_y = row + i[1]
            valid_expansion = 0 <= possible_expansion_y < len(occupancy_map[0]) and 0 <= possible_expansion_x < len(occ_map)

            if valid_expansion:
                try:
                    unsearched_node = possible_nodes[possible_expansion_y][possible_expansion_x] == 0
                    open_node = occ_map[possible_expansion_y][possible_expansion_x] == 0
                except:
                    unsearched_node = False
                    open_node = False
                if unsearched_node and open_node:
                    # Using  instead of 1 to make it easier to read This node has been searched.
                    # searched_row = possible_expansion_y
                    # searched_col = possible_expansion_x
                    possible_nodes[possible_expansion_y][possible_expansion_x] = 3
                    possible_node = (g_value + cost, possible_expansion_x, possible_expansion_y)
                    frontier_nodes.append(possible_node)



                    # This now builds parent/child relationship
                    parent_node[possible_node] = current_node

        loopcount = loopcount+1

    if goal_found == True:

        print ("Generating path...")

        route = []
        child_node = current_node

        while child_node in parent_node:
            route.append(parent_node[child_node])
            child_node = parent_node[child_node]
            route.sort()





        path = []
        position = [start.item(0), start.item(1)]  # Starting point passed in by function
        path.append(position)  # Add it to the list for the path

        for i in range(0, len(route)):
            position = [round((route[i][1])*x_spacing, 3), round((route[i][2])*y_spacing, 3)]
            path.append(position)

        # Add the goal state:

        position = [goal.item(0), goal.item(1)]
        path.append(position)
        # Convert to numpy array and return.
        path = np.array(path)
        return path

    else:
        return False


def test():


    test_map2 = np.array([
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [1, 1, 1, 1, 1, 1, 0, 1],
             [1, 0, 0, 1, 1, 0, 0, 1],
             [1, 0, 0, 1, 1, 0, 0, 1],
             [1, 0, 0, 1, 1, 0, 0, 1],
             [1, 1, 1, 1, 1, 1, 1, 1]])
    start2 = np.array([[1], [1], [1.5707963267948966]])
    goal2 = np.array([[6], [6], [-1.5707963267948966]])
    x_spacing2 = 1
    y_spacing2 = 1
    path2 = dijkstras(test_map2,x_spacing2,y_spacing2,start2,goal2)
    print(path2)



def main():
    test()

if __name__ == '__main__':
    main()
