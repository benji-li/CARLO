import numpy as np
import re
import matplotlib
matplotlib.use('Agg')  # Headless backend - must be before pyplot import
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Polygon as MplPolygon, Circle as MplCircle


def convert_tk_color(color):
    """Convert Tk color names to matplotlib-compatible colors.
    
    Handles:
    - 'gray80', 'grey50', etc. -> RGB tuple
    - Standard color names -> passed through
    - Hex colors -> passed through
    """
    if color is None:
        return 'blue'
    
    # Handle grayNN / greyNN format (Tk style)
    match = re.match(r'^gr[ae]y(\d+)$', color.lower())
    if match:
        level = int(match.group(1)) / 100.0  # Convert 0-100 to 0-1
        return (level, level, level)
    
    tk_to_mpl = {
        'gray': 'gray',
        'grey': 'gray', 
        'lightgray': 'lightgray',
        'lightgrey': 'lightgray',
        'darkgray': 'darkgray',
        'darkgrey': 'darkgray',
    }
    
    if color.lower() in tk_to_mpl:
        return tk_to_mpl[color.lower()]
    
    return color


class VideoVisualizer:
    def __init__(self, width: float, height: float, ppm: int):
        """
        Args:
            width: World width in meters
            height: World height in meters  
            ppm: Pixels per meter
        """
        self.width = width
        self.height = height
        self.ppm = ppm
        self.frames = []
        self.window_created = False  # For API compatibility with Visualizer
        
    def create_window(self, bg_color: str = 'gray'):
        """API compatibility - just stores bg_color"""
        self.bg_color = bg_color
        self.window_created = True
        
    def update_agents(self, agents: list):
        """Render agents to a frame and store it."""
        # Import here to avoid circular imports
        from entities import RectangleEntity, CircleEntity, RingEntity
        
        # Figure size in inches (ppm pixels per meter, 100 dpi)
        fig_width = self.width * self.ppm / 100
        fig_height = self.height * self.ppm / 100
        
        fig, ax = plt.subplots(1, 1, figsize=(fig_width, fig_height), dpi=100)
        ax.set_xlim(0, self.width)
        ax.set_ylim(0, self.height)
        
        bg_color = convert_tk_color(self.bg_color if hasattr(self, 'bg_color') else 'gray')
        ax.set_facecolor(bg_color)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Remove margins
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
        
        for agent in agents:
            color = convert_tk_color(agent.color if hasattr(agent, 'color') else 'blue')
            
            if isinstance(agent, RingEntity):
                # Draw ring as outer circle with inner circle cut out
                outer = MplCircle((agent.center.x, agent.center.y), 
                                  agent.outer_radius, facecolor=color, edgecolor='none')
                ax.add_patch(outer)
                inner = MplCircle((agent.center.x, agent.center.y), 
                                  agent.inner_radius, 
                                  facecolor=bg_color,
                                  edgecolor='none')
                ax.add_patch(inner)
            elif isinstance(agent, CircleEntity):
                circle = MplCircle((agent.center.x, agent.center.y), 
                                   agent.radius, facecolor=color, edgecolor='none')
                ax.add_patch(circle)
            elif isinstance(agent, RectangleEntity):
                corners = [(c.x, c.y) for c in agent.corners]
                poly = MplPolygon(corners, facecolor=color, edgecolor='none', closed=True)
                ax.add_patch(poly)
        
        # Convert figure to numpy array
        fig.canvas.draw()
        frame = np.frombuffer(fig.canvas.buffer_rgba(), dtype=np.uint8)
        frame = frame.reshape(fig.canvas.get_width_height()[::-1] + (4,))
        frame = frame[:, :, :3]  # Remove alpha channel
        self.frames.append(frame.copy())
        plt.close(fig)
    
    def save_video(self, filename: str, fps: int = 24):
        """Save collected frames as video."""
        import imageio
        if not self.frames:
            print("No frames to save!")
            return
        imageio.mimsave(filename, self.frames, fps=fps)
        print(f"Saved {len(self.frames)} frames to {filename}")
        
    def save_gif(self, filename: str, fps: int = 24):
        """Save collected frames as GIF."""
        import imageio
        if not self.frames:
            print("No frames to save!")
            return
        imageio.mimsave(filename, self.frames, fps=fps)
        print(f"Saved {len(self.frames)} frames to {filename}")
        
    def close(self):
        """API compatibility with Visualizer"""
        self.window_created = False
        
    def clear_frames(self):
        """Clear stored frames"""
        self.frames = []