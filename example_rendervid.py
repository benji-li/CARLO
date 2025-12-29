"""
Example: Circular road with video output (headless mode).
No display required - renders directly to video file.
"""
import numpy as np
from world import World
from agents import Car, RingBuilding, CircleBuilding, Painting, Pedestrian
from geometry import Point

dt = 0.1  # time steps in terms of seconds. In other words, 1/dt is the FPS.
world_width = 120  # in meters
world_height = 120
inner_building_radius = 30
num_lanes = 2
lane_marker_width = 0.5
num_of_lane_markers = 50
lane_width = 3.5

# Create world in HEADLESS mode - no display required
w = World(dt, width=world_width, height=world_height, ppm=6, headless=True)

# Add circular road structure
cb = CircleBuilding(Point(world_width/2, world_height/2), inner_building_radius, 'gray80')

rb = RingBuilding(
    Point(world_width/2, world_height/2), 
    inner_building_radius + num_lanes * lane_width + (num_lanes - 1) * lane_marker_width, 
    1 + np.sqrt((world_width/2)**2 + (world_height/2)**2), 
    'gray80'
)
w.add(rb)
w.add(cb)

# Add lane markers
for lane_no in range(num_lanes - 1):
    lane_markers_radius = inner_building_radius + (lane_no + 1) * lane_width + (lane_no + 0.5) * lane_marker_width
    lane_marker_height = np.sqrt(2*(lane_markers_radius**2)*(1-np.cos((2*np.pi)/(2*num_of_lane_markers))))
    for theta in np.arange(0, 2*np.pi, 2*np.pi / num_of_lane_markers):
        dx = lane_markers_radius * np.cos(theta)
        dy = lane_markers_radius * np.sin(theta)
        w.add(Painting(
            Point(world_width/2 + dx, world_height/2 + dy), 
            Point(lane_marker_width, lane_marker_height), 
            'white', 
            heading=theta
        ))

# Add a car
c1 = Car(Point(91.75, 60), np.pi/2)
c1.max_speed = 30.0  # max 30 m/s (108 km/h)
c1.velocity = Point(0, 3.0)
w.add(c1)

# Simple driving policy
desired_lane = 1
num_steps = 300  # Reduced for faster rendering

print(f"Rendering {num_steps} frames...")
for k in range(num_steps):
    if k % 50 == 0:
        print(f"  Frame {k}/{num_steps}")
    
    # Simple lane-keeping policy
    lp = 0.
    if c1.distanceTo(cb) < desired_lane*(lane_width + lane_marker_width) + 0.2:
        lp += 0.
    elif c1.distanceTo(rb) < (num_lanes - desired_lane - 1)*(lane_width + lane_marker_width) + 0.3:
        lp += 1.
    
    v = c1.center - cb.center
    v = np.mod(np.arctan2(v.y, v.x) + np.pi/2, 2*np.pi)
    if c1.heading < v:
        lp += 0.7
    else:
        lp += 0.
    
    if np.random.rand() < lp:
        c1.set_control(0.2, 0.1)
    else:
        c1.set_control(-0.1, 0.1)
    
    w.tick()
    w.render()  # This captures frames instead of displaying
    
    if w.collision_exists():
        print('Collision detected!')
        break

# Save the video
print("Saving video...")
w.save_video('circular_road_rollout.mp4', fps=int(1/dt))
print("Done!")

w.close()