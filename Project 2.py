# Importing modules
import math
import pygame
import pygame.freetype
import random
import os
import time
import neat
import pickle
from numpy import cos, sin
import numpy as np
from numpy import array
from numpy import deg2rad
from numpy import linalg


#Pygame setup
pygame.init()
pygame.freetype.init()
#Pygame display setup
win = pygame.display.set_mode((1000, 1000))
pygame.display.set_caption("LIFE")
smallfont = pygame.freetype.Font(None,30)
bigfont = pygame.freetype.Font(None,60)

# WIP Map size modifer (Default at 1, larger the number bigger the map)
MAP_SIZE = 1

# Button size
BUTTON_WIDTH = 300
BUTTON_HEIGHT = 100

#Creature default values
SIZE = 3.0
MUTATION_RATE = 5.0  # 1 out of x chance of mutation
SENSE = 40.0
SPEED = 3.0
REPRODUCTION = 1.0
GENERATION = 0

HEIGHT = 1080
WIDTH = 1920


# Helper function for collison
def distance(position, position2):
    a = position2[0] - position[0]
    b = position2[1] - position[1]
    c = math.sqrt(a ** 2 + b ** 2)
    return c


# Class for Character
class Creature:
    global live

    def __init__(self, position, velocity, radius, energy, sense, reproduction, speed):
        self.pos = position
        self.vel = velocity
        self.rad = radius  # Size
        self.energy = energy  # Energy
        self.sense = sense  # Sense
        self.speed = speed  # Speed
        self.reproduction = reproduction

        self.energy_cap = (self.rad ** 3) * 3  # Energy_Capcity
        self.alive = True

        # Draw and collison attributes
        self.draw_pos = [position[0] / MAP_SIZE, position[1] / MAP_SIZE]
        self.draw_vel = [velocity[0] / MAP_SIZE, velocity[1] / MAP_SIZE]
        self.draw_rad = radius / MAP_SIZE
        self.draw_sense = sense / MAP_SIZE
        self.draw_speed = speed / MAP_SIZE

    # Draw handler for Character
    def draw(self):
        if self.alive:
            pygame.draw.circle(win, (133,253,43), (int(self.pos[0]), int(self.pos[1])), int(self.sense))
            pygame.draw.circle(win, (0,0,0), (int(self.pos[0]), int(self.pos[1])), int(self.sense-1))

            pygame.draw.circle(win,(216,0,89),(int(self.pos[0]),int(self.pos[1])), int(self.rad))
            smallfont.render_to(win, (int(self.pos[0]),int(self.pos[1])), str(int(self.energy)), (251,251,155))

            #pygame.draw.circle(win, (255, 0, 0), self.pos, 1, 1)

            for ray in self.rays:
                ray.display(win)

    # Update function
    def update(self):
        if self.alive:
            # use the x velocity to change the x position
            self.pos[0] += self.vel[0]
            # use the y velocity to change the y position
            self.pos[1] += self.vel[1]
            # Make the character stay in frame
            if self.pos[1] <= 0 + self.rad:
                self.pos[1] = 0 + self.rad
                self.vel[1] = -self.vel[1]
            if self.pos[1] > 766 - self.rad:
                self.pos[1] = 766 - self.rad
                self.vel[1] = -self.vel[1]
            if self.pos[0] < 0 + self.rad:
                self.pos[0] = 0 + self.rad
                self.vel[0] = -self.vel[0]
            if self.pos[0] >= 985 - self.rad:
                self.pos[0] = 985 - self.rad
                self.vel[0] = -self.vel[0]
            #Making sure energy is not above the cap
            if self.energy > self.energy_cap:
                self.energy = self.energy_cap
            #Energy consumption of creature
            self.energy -= ((self.rad ** 3) * (self.speed ** 2) + (self.sense)) / (600.0 * 10)  # 10000 For normal speed


    # Collison function
    def hascollided(self, obj):
        dist = distance(self.pos, obj.pos)
        return dist < self.rad + obj.rad


    # Default path finding
    def movetorwards(self, obj):
        dist = distance(self.pos, obj.pos)
        if dist <= self.sense + obj.rad:
            if (obj.pos[0] - self.pos[0]) > 0:
                x_posdif = 1 * self.speed
            if (obj.pos[0] - self.pos[0]) < 0:
                x_posdif = -1 * self.speed
            if (obj.pos[0] - self.pos[0]) == 0:
                x_posdif = 0
            if (obj.pos[1] - self.pos[1]) > 0:
                y_posdif = 1 * self.speed
            if (obj.pos[1] - self.pos[1]) < 0:
                y_posdif = -1 * self.speed
            if (obj.pos[1] - self.pos[1]) == 0:
                y_posdif = 0

            self.vel = [x_posdif, y_posdif]
            return True


    #Ray casting
    def look(self, screen, walls):
        self.rays = []
        for i in range(0,90):
            self.rays.append(Ray(self.pos[0], self.pos[1], deg2rad(i*4)))

        for ray in self.rays:
            closest = 10000000
            closestpt = None
            for wall in walls:
                pt = ray.cast(wall)

                if pt is not None:
                    dis = linalg.norm(pt - self.pos)
                    if (dis < closest):
                        closest = dis
                        closestpt = pt

            if closestpt is not None:
                pygame.draw.line(screen, (255, 255, 255), self.pos, array(closestpt, int), 2)


    # Reproduction function, creates a copy of the creature
    def reproduce(self):
        global creatures
        thing = random.randint(1, MUTATION_RATE)
        if thing == 1:
            self.rad = self.rad * (random.choice([1.2, 0.8]))
        elif thing == 2:
            self.sense = self.sense * (random.choice([1.2, 0.8]))
        elif thing == 3:
            self.speed = self.speed * (random.choice([1.2, 0.8]))
        #elif thing == 4:
            #self.reproduction = self.reproduction * 1

        #self.energy = (((self.rad ** 3) * (self.speed ** 2) + (self.sense)) / 15) * (1 / self.reproduction)
        creatures.append(Creature(self.pos, self.vel, self.rad, 30, self.sense, self.reproduction, self.speed))



#Ray casting
class Ray:
    def __init__(self, x, y, radius):
        self.pos = array([x, y])
        self.dir = array([cos(radius), sin(radius)])

    def display(self, screen):
        pygame.draw.line(screen, (255, 255, 255), self.pos, self.pos + self.dir, 1)

    #def lookAt(self, x, y):
    #     #set the diretion
    #     self.dir[0] = x - self.pos[0]
    #     self.dir[1] = y - self.pos[1]
    #     self.dir = self.dir / linalg.norm(self.dir)

    def cast(self, wall):
        # start point
        x1 = wall.a[0]
        y1 = wall.a[1]
        # end point
        x2 = wall.b[0]
        y2 = wall.b[1]

        # position of the ray
        x3 = self.pos[0]
        y3 = self.pos[1]
        x4 = self.pos[0] + self.dir[0]
        y4 = self.pos[1] + self.dir[1]

        # denominator
        den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        # numerator
        num = (x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)
        if den == 0:
            return None

        # formulars
        t = num / den
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / den

        if t > 0 and t < 1 and u > 0:
            # Px, Py
            x = x1 + t * (x2 - x1)
            y = y1 + t * (y2 - y1)
            pot = array([x, y])
            return pot



# Food Class
class Food:
    def __init__(self, position, velocity, radius):
        self.pos = position
        self.vel = velocity
        self.rad = radius

        self.draw_pos = [position[0] / MAP_SIZE, position[1] / MAP_SIZE]
        self.draw_vel = [velocity[0] / MAP_SIZE, velocity[1] / MAP_SIZE]
        self.draw_rad = radius / MAP_SIZE

    # Draw handler for food
    def draw(self):
        pygame.draw.circle(win, (251,251,155), (self.pos[0], self.pos[1]), self.rad)

    # Update function for food
    def update(self):
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        if self.pos[1] > 990:
            obstacles.remove(self)



class Wall:
    def __init__(self, x1, y1, x2, y2):
        self.a = [x1, y1]
        self.b = [x2, y2]

    def display(self, screen):
        #pygame.draw.rect(screen, (255, 0, 0), (self.a[0], self.a[1], self.b[0] - self.a[0], self.b[1] - self.a[1]))
        pygame.draw.line(screen, (255, 255, 255), self.a, self.b, 2)



class Square:
    def __init__ (self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        walls.append(Wall(self.x, self.y, self.x + self.width, self.y))
        walls.append(Wall(self.x, self.y, self.x, self.y + self.height))
        walls.append(Wall(self.x + self.width, self.y + self.height, self.x, self.y + self.height))
        walls.append(Wall(self.x + self.width, self.y, self.x + self.width, self.y + self.height))


    def draw(self, screen):
        '''


        '''
        pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y, self.width, self.height))



#Main function for the game
def eval_genomes(genomes, config):
    global nets, ge, obstacles, creatures, time, GENERATION, walls

    GENERATION += 1
    time = 0
    obstacles = []
    walls = []
    squares = []
    '''
    walls.append(Wall(0, 0, WIDTH, 0))
    walls.append(Wall(0, 0, 0, HEIGHT))
    walls.append(Wall(0, HEIGHT, WIDTH, HEIGHT))
    walls.append(Wall(WIDTH, 0, WIDTH, HEIGHT))
    '''

    #Map construction happens here
    RawMap = open("Map1.txt","r")
    RawMap = RawMap.read().splitlines()
    finalMap = []   
    #Parse new data
    for i in RawMap:
        tempTab = i.split(",")
        newTab  = []
        for i in tempTab:
            if i != '':
                newTab.append(int(i))
        finalMap.append(newTab)
    #Lastly, reload squares
    for i in finalMap:
        try:
            squares.append(Square(i[0],i[1],i[2],i[3]))
        except:
            None
    #squares.append(Square(300, 300, 200, 200))

    #Creates a list of genomes and associating it with the creature object
    for genome_id, genome in genomes:
        genome.fitness = 0  # start with fitness level of 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        ge.append(genome)
        if not creatures:
            for i in range(len(genomes)):
                creatures.append(Creature([98 * genome_id, 10], [random.randint(1, 5), random.randint(1, 5)], SIZE, 20.0, SENSE, REPRODUCTION, SPEED))

    #Reproduction
    for x, creature in enumerate(creatures):
        if creature.energy > (((creature.rad ** 3.0) * (creature.speed ** 2.0) + (creature.sense)) / 15.0) * (1.0 / creature.reproduction) * 3.0:
            creature.energy -= (((creature.rad ** 3.0) * (creature.speed ** 2.0) + (creature.sense)) / 15.0) * (1.0 / creature.reproduction) * 3.0
            creature.reproduce()
            ge.append(ge[x])
            ge[x].fitness += 100
            # print "Reproduce"
            # print creature.energy_cap
        creature.pos = [(980 / len(creatures)) * (creatures.index(creature)), 10]

    #Food spawning
    for i in range(100):
        obstacles.append(Food([random.randint(0, 980), random.randint(0, 765)], [0, 0], 3))

    #Varaibles for the loop
    clock = pygame.time.Clock()
    run = True
    #The main loop (runs at 60fps)
    while run and time < 600:
        clock.tick(1000)

        #Event handler
        for event in pygame.event.get():  # This will loop through a list of any keyboard or mouse events.
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break

            # Click Handler
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_position = pygame.mouse.get_pos()
                if newgamebutton.is_selected(mouse_position):
                    new_game()
                if newroundbutton.is_selected(mouse_position):
                    round_start()

        #Background color
        win.fill((0, 0, 0))

        #Drawing obstacles
        for obs in obstacles:
            obs.draw()
            obs.update()

        for square in squares:
            square.draw(win)
        for wall in walls:
            wall.display(win)

        #Creature's main loop
        for x, creature in enumerate(creatures):
            #Die
            if creature.energy <= 0:
                creature.alive = False
                creatures.remove(creature)
                ge.remove(ge[x])
                break

            creature.look(win, walls)

            #Objects within sense range
            nearest_objects = [(creature.sense, creature.pos[0], creature.pos[1], 0)]
            nearest_creatures = [(creature.sense, creature.pos[0], creature.pos[1], 0)]

            #Creature update
            ge[x].fitness += 0.1
            creature.draw()
            creature.update()

            #NEAT output
            output = nets[creatures.index(creature)].activate(
                (creature.pos[0], creature.pos[1], creature.speed, creature.rad, creature.sense,
                 (nearest_creatures[-1][1]), (nearest_creatures[-1][2]), (nearest_creatures[-1][3]),
                 (nearest_objects[-1][1]), (nearest_objects[-1][2]), (nearest_objects[-1][3])))

            #AI controlling actions
            if output[0] > 0.5:
                creature.vel[0] = creature.speed
            if output[1] > 0.5:
                creature.vel[1] = creature.speed
            if output[2] > 0.5:
                creature.vel[0] = -creature.speed
            if output[3] > 0.5:
                creature.vel[1] = -creature.speed

            #Collison
            for obs in obstacles:
                dist = distance(creature.pos, obs.pos)
                if dist <= nearest_objects[-1][0]:
                    nearest_objects.append((dist, obs.pos[0], obs.pos[1], obs.rad))
                #creature.movetorwards(obs)
                if creature.hascollided(obs):
                    obstacles.remove(obs)
                    creature.energy += 100
                    ge[x].fitness += 20

            for creature1 in creatures:
                dist = distance(creature.pos, obs.pos)
                if dist <= nearest_creatures[-1][0]:
                    nearest_creatures.append((dist, creature1.pos[0], creature1.pos[1], creature1.rad))
                if creature.rad > creature1.rad:
                    if creature.hascollided(creature1):
                        creature.energy += creature1.energy
                        creatures.remove(creature1)
                        ge[x].fitness += 100

        # Timer
        time += 1

        #Counters
        smallfont.render_to(win, (0, 20), "There is x creatures:" + str(len(creatures)), (255, 255, 255))
        smallfont.render_to(win, (0, 50), "This round lasted: " + str(time // 60) + " seconds", (255, 255, 255))
        smallfont.render_to(win, (0, 80), "Current GEN: " + str(GENERATION), (255, 255, 255))

        pygame.display.update()

#Run function for NEAT
def run(config_file):
    global nets, ge, obstacles, creatures

    #Config file
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    #p.add_reporter(neat.Checkpointer(5))

    nets = []
    ge = []

    creatures = []
    # Run for up to 50 generations.
    winner = p.run(eval_genomes, 9999999999999999999999999999999999)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))

#Check configuration path
if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)






