'''
Credits to Tim, visit his github page!
https://github.com/techwithtim/NEAT-Flappy-Bird
'''



import random
import neat
import pygame
import os

'''
Inputs               -> Bird.y, distance between bird and next coming pipes
Outputs              -> Jump or don't
Activation Function  -> Hyperbolic Tangent Function, squish whatever value to be between 1 or -1
Pop.Size             -> how many birds running in each gen
Fitness              -> giving scores to bird, bird that goes the furthest is the best one
Max Gen.             -> how many generations do I want this to go on 
'''

pygame.font.init()

PIPE_POSITION = 700
FLOOR_POSITION = 730
WIDTH = 500
HEIGHT = 800


# Loading images and making them double the size
def image_load(img_name):
    return pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", img_name)))


BIRD_IMGS = [image_load("bird1.png"), image_load("bird2.png"), image_load("bird3.png")]
PIPE_IMG = image_load("pipe.png")
BACKGROUND_IMG = image_load("bg.png")
BASE_IMG = image_load("base.png")
FONT = pygame.font.SysFont("comicsans", 50)


# ------------------------------------------------------- Floor Class -------------------------------------------------------
class Floor:
    SPEED = 5
    LENGTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.LENGTH

    # move first and second ground images to the left, when
    # first img completely reches end of screen move it to the back
    def move(self):
        self.x1 -= self.SPEED
        self.x2 -= self.SPEED

        if self.x1 + self.LENGTH < 0:
            self.x1 = self.x2 + self.LENGTH

        if self.x2 + self.LENGTH < 0:
            self.x2 = self.x1 + self.LENGTH

    def draw(self, window):
        window.blit(self.IMG, (self.x1, self.y))
        window.blit(self.IMG, (self.x2, self.y))


# ------------------------------------------------------- Pipe Class -------------------------------------------------------
class Pipe:
    GAP = 200  # space between pipes
    SPEED = 5  # how fast pipes are moving

    def __init__(self, x):  # because they have random heights
        self.x = x
        self.height = 0

        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)  # need to flip pipe for the bottom one
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.SPEED

    def draw(self, window):
        window.blit(self.PIPE_TOP, (self.x, self.top))
        window.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))  # ho far wy the masks are from each other
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        bottom_point = bird_mask.overlap(bottom_mask,
                                         bottom_offset)  # finds pint of overlap of the bottom pipe and bird
        top_point = bird_mask.overlap(top_mask, top_offset)

        if top_point or bottom_point:  # check if returns null or something
            return True  # colliding ith other objects
        else:
            return False


# -------------------------------------------------- Bird Class --------------------------------------------------
class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25
    ROTATION_VELOCITY = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.velocity = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.velocity = -10.5  # negative velocity to go upwards
        self.tick_count = 0  # count last jump
        self.height = self.y  # keep track of here the bird ws before lst jump

    def move(self):
        self.tick_count += 1

        displacement = (self.velocity * self.tick_count) + (
                1.5 * self.tick_count ** 2)  # how many pixels moving up or down

        if displacement >= 16:  # in case moving down more than 16
            displacement = 16

        if displacement < 0:
            displacement -= 2

        self.y = self.y + displacement  # know the change in position

        if (displacement) < 0 or (
                self.y < self.height + 50):  # checking if bird position is above its previous position
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION  # don't want to tilt to 90deg completely when going up

        else:
            if self.tilt > -90:
                self.tilt -= self.ROTATION_VELOCITY  # we want the bird to tilt completely to 90deg when falling

    def draw(self, window):
        self.img_count += 1

        if self.img_count < self.ANIMATION_TIME:  # animation less than 5 then display first flppy image
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME * 2:  # show the straight wings image
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 3:  # show the flapped wings
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME * 4:  # go back to mid position
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 4 + 1:  # go to initial position image
            self.img = self.IMGS[0]
            self.img_count = 0

        if self.tilt <= -80:  # shouldn't flap wings when bird is free falling
            self.img = self.IMGS[1]  # display image ith wings straight
            self.img_count = self.ANIMATION_TIME * 2

        rotated_image = pygame.transform.rotate(self.img, self.tilt)  # rotates image by tilt angle
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
        window.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


# ----------------------------------------------------------------------------------------------------------------------

def draw_window(window, birds, pipes, floor, score):
    window.blit(BACKGROUND_IMG, (0, 0))  # draws the bckground image

    for pipe in pipes:
        pipe.draw(window)

    text = FONT.render("Score " + str(score), 1, (255, 255, 255))
    window.blit(text, (WIDTH - 10 - text.get_width(), 10))

    floor.draw(window)

    for bird in birds:
        bird.draw(window)
    pygame.display.update()  # updated the scren


def main(genomes, config):
    nets = []
    genes = []
    birds = []

    for _, g in genomes:
        g.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        genes.append(g)

    # bird = Bird(230, 350)
    floor = Floor(FLOOR_POSITION)
    pipes = [Pipe(PIPE_POSITION)]
    run = True
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    score = 0

    while run and len(birds) > 0:
        clock.tick(30)  # slow down 30 ticks every second
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # if hit red x on window exit loop and quit
                run = False
                pygame.quit()
                quit()
                break

        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1

        for x, bird in enumerate(birds):
            genes[x].fitness += .1
            bird.move()

            output = nets[birds.index(bird)].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            if output[0] > .5:
                bird.jump()

        floor.move()

        add_pipe = False
        remove = []
        for pipe in pipes:
            pipe.move()
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    genes[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    genes.pop(x)

                if not pipe.passed and pipe.x < bird.x:  # check if pipe hs been passed
                    pipe.passed = True
                    add_pipe = True

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:  # add pipe to remove list if it hs passed certain point
                remove.append(pipe)


        if add_pipe:
            score += 1
            for g in genes:
                g.fitness += 5
            pipes.append(Pipe(PIPE_POSITION))  # add a new pipe

        for r in remove:
            pipes.remove(r)

        for x, bird in enumerate(birds) or bird.y < 0:
            if bird.y + bird.img.get_height() >= 730:  # if bird hits the ground
                birds.pop(x)
                nets.pop(x)
                genes.pop(x)

        draw_window(window, birds, pipes, floor, score)


def run(config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)

    population = neat.Population(config)

    population.add_reporter(neat.StdOutReporter(True))
    population.add_reporter(neat.StatisticsReporter())

    winner = population.run(main, 50)  # call main 50 times ith the configuration


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config")
    run(config_path)
