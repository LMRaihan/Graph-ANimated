import random
import heapq
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.animation as animation

height = 7
width = 10
steps = 15

def initialize_env():
    return [[0 for i in range(width)] for i in range(height)]

def random_start_position(grid):
    while True:
        pos = (random.randint(1, height - 2), random.randint(1, width - 2))  # Exclude boundary
        if grid[pos[0]][pos[1]] == 0:
            return pos

def random_object_positions(num_objects):
    object_positions = set()
    while len(object_positions) < num_objects:
        pos = random_start_position(initialize_env())
        object_positions.add(pos)
    return object_positions

def place_objects(grid, object_positions):
    for pos in object_positions:
        y, x = pos
        grid[y][x] = 2  # Mark position with an object

def is_at_boundary(position):
    y, x = position
    return y == 0 or y == height - 1 or x == 0 or x == width - 1

def place_hurdles(grid, num_hurdles):
    total_locations = height * width
    max_hurdles = total_locations // 8
    for _ in range(min(num_hurdles, max_hurdles)):
        hurdle_position = random_start_position(grid)
        while grid[hurdle_position[0]][hurdle_position[1]] != 0:
            hurdle_position = random_start_position(grid)
        grid[hurdle_position[0]][hurdle_position[1]] = 999  # Mark position with a hurdle

def manhattan_distance(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def find_closest_object(position, object_positions):
    return min(object_positions, key=lambda obj_pos: manhattan_distance(position, obj_pos))

def a_star(start, goal, grid, last_position):
    def reconstruct_path(came_from, current):
        path = []
        while current in came_from:
            path.append(current)
            current = came_from[current]
        path.reverse()
        return path

    open_set = []
    heapq.heappush(open_set, (0, start))  # (priority, position)

    came_from = {}
    g_score = {start: 0}

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:
            return reconstruct_path(came_from, current)

        y, x = current
        neighbors = [(y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)]
        for ny, nx in neighbors:
            if 0 <= ny < height and 0 <= nx < width and grid[ny][nx] != 999:  # Valid move and not a hurdle
                if (ny, nx) == last_position or is_at_boundary((ny, nx)):  # Avoid last visited and boundary
                    continue

                tentative_g_score = g_score[current] + 1
                neighbor = (ny, nx)

                if tentative_g_score < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score = tentative_g_score + manhattan_distance(neighbor, goal)
                    heapq.heappush(open_set, (f_score, neighbor))

    return []

def update_grid_visual(grid, position):
    """Update the visual representation of the grid for animation."""
    data = [[1 if cell == 0 else 2 if cell == 2 else 3 if cell == 999 else 0 for cell in row] for row in grid]
    y, x = position
    data[y][x] = 4  # Mark the current position of the agent
    return data

def run_simulation(steps):
    total_actions = 0
    total_collects = 0
    total_extra_moves = 0
    frames = []

    for step in range(steps):
        action = 0
        collect = 0
        extra_moves = 0
        env = initialize_env()

        num_objects = random.randint(1, 5)
        object_positions = random_object_positions(num_objects)
        place_objects(env, object_positions)
        place_hurdles(env, num_hurdles=height * width // 8)

        track_path = []
        cur_position = random_start_position(env)
        last_position = None
        track_path.append(cur_position)
        frames.append(update_grid_visual(env, cur_position))

        while len(object_positions) > 0:
            y, x = cur_position

            if is_at_boundary(cur_position):
                print("Agent touched the border. Terminating simulation.")
                break

            if (y, x) in object_positions:
                collect += 1
                object_positions.remove((y, x))
                env[y][x] = 0

            if object_positions:
                closest_object = find_closest_object(cur_position, object_positions)
                path = a_star(cur_position, closest_object, env, last_position)

                if path:
                    for new_position in path:
                        if new_position == cur_position:  # If no new position to move, break
                            break
                        if env[new_position[0]][new_position[1]] == 999:
                            extra_moves += 1
                        action += 1
                        last_position = cur_position  # Update last position
                        cur_position = new_position
                        track_path.append(cur_position)
                        frames.append(update_grid_visual(env, cur_position))
                        # Check again if the current position touches the border
                        if is_at_boundary(cur_position):
                            print("Agent touched the border during movement. Terminating simulation.")
                            break  # Terminate if touching the border
                        if (new_position[0], new_position[1]) == closest_object:
                            break  # Reached the object
                else:
                    break  # No path found
            else:
                break  # No more objects to collect

        total_actions += action
        total_collects += collect
        total_extra_moves += extra_moves

    performance = total_actions / (total_collects + total_extra_moves) if total_collects > 0 else 0
    return frames, performance, total_actions, total_collects, total_extra_moves

def visualize_simulation(frames):
    """Visualize the simulation using matplotlib."""
    # Updated colormap: light green for empty spaces, blue for objects, red for hurdles, yellow for agent
    cmap = colors.ListedColormap(['lightgreen', 'blue', 'red', 'darkgray', 'yellow'])
    bounds = [0, 1, 2, 3, 4, 5]
    norm = colors.BoundaryNorm(bounds, cmap.N)

    fig, ax = plt.subplots(figsize=(8, 6))

    def update(frame):
        ax.clear()
        ax.imshow(frame, cmap=cmap, norm=norm)
        ax.set_xticks([])
        ax.set_yticks([])
        # Draw a thick border around the grid
        for spine in ax.spines.values():
            spine.set_edgecolor('black')
            spine.set_linewidth(3)

        # Set the title
        plt.title("Utility-based Simulation", fontsize=16, fontweight='bold')

    ani = animation.FuncAnimation(fig, update, frames=frames, interval=500, repeat=False)
    plt.show()

frames, performance, total_actions, total_collects, total_extra_moves = run_simulation(steps)

print(f"Total Actions: {total_actions}")
print(f"Total Objects Collected: {total_collects}")
print(f"Extra Moves Due to Hurdles: {total_extra_moves}")
print(f"Performance Metric: {performance:.2f}")

visualize_simulation(frames)