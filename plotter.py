import matplotlib
import pygame
matplotlib.use("Agg")
import matplotlib.backends.backend_agg as agg
import pylab

class Plotter:
    def __init__(self, width, height, dpi=100):
        self.width = width
        self.height = height
        self.dpi = dpi
        self.fig = pylab.figure(figsize=[width, height], dpi=dpi)

    def plot(self, data: list):
        x = [point[0] for point in data]
        y = [point[1] for point in data]
        pylab.plot(x, y)

    def clear(self):
        self.fig.clear()

    def get_image(self):
        canvas = agg.FigureCanvasAgg(self.fig)
        canvas.draw()
        renderer = canvas.get_renderer()
        raw_data = renderer.tostring_rgb()
        size = canvas.get_width_height()
        return raw_data, size
    
    def draw(self, screen: pygame.Surface, startPoint):
        raw_data, size = self.get_image()
        surf = pygame.image.fromstring(raw_data, size, "RGB")
        screen.blit(surf, startPoint)
        