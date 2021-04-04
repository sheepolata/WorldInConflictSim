import pygame
import math

def arrow(surface, color, start_pos, end_pos, width=1, arrow_size=5):

    pygame.draw.line(surface, color, start_pos, end_pos, width=width)

    rad = math.pi/180.0

    rotation = (math.atan2(start_pos[1] - end_pos[1], end_pos[0] - start_pos[0])) + math.pi/2
    pygame.draw.polygon(surface, color, ((end_pos[0] + arrow_size * math.sin(rotation),
                                        end_pos[1] + arrow_size * math.cos(rotation)),
                                       (end_pos[0] + arrow_size * math.sin(rotation - 120*rad),
                                        end_pos[1] + arrow_size * math.cos(rotation - 120*rad)),
                                       (end_pos[0] + arrow_size * math.sin(rotation + 120*rad),
                                        end_pos[1] + arrow_size * math.cos(rotation + 120*rad))))