import pygame
import random


def print_s(game, text_str,slot, color = [255,255,255]):
    text = game.terminal[30].render(str(text_str), False, color)
    game.screen.blit(text, (game.resolution[0] - 10 - text.get_rect().size[0], slot*30)) #

def render_text(game, string, pos, font_size, centerx = False, centery = False, color = [255,255,255]):
    text = game.terminal[font_size].render(str(string), False, color)

    if centerx:
        pos[0] -= text.get_size()[0]/2
    if centery:
        pos[1] -= text.get_size()[1]/2

    game.screen.blit(text, pos) #

def list_play(list):
    for y in list:
        y.stop()
    pick_random_from_list(list).play()


def pick_random_from_list(list):
    return list[random.randint(0,len(list)-1)]

def rot_center(image, angle, x, y):

    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(center = (x, y)).center)

    return rotated_image, new_rect


def minus(list1,list2, op = "+"):
    try:
        list_1 = list1.copy()
        list_2 = list2.copy()
    except:
        list_1 = list1
        list_2 = list2
    for x in range(len(list1)):
        if op == "+":
            list_1[x] += list_2[x]
        elif op == "/":
            list_1[x] /= list_2[x]
        elif op == "*":
            list_1[x] *= list_2[x]
        else:
            list_1[x] -= list_2[x]
    return list_1


def mult(list1, am):
    try:
        list_1 = list1.copy()
    except:
        list_1 = list1

    for x in range(len(list1)):
        list_1[x] *= am
    return list_1


def point_inside(point, point2, tolerance):
    boolean = point2[0] < point[0] < point2[0] + tolerance[0] and point2[1] < point[1] < point2[1] + tolerance[1]
    return boolean


def get_shortest_route(point, routes):
    complete_route = [0,0,0,0,0,0,9,0,0,0,0,0]
    for route in routes:
        if point in route:

            temp = []

            for x in route:
                temp.append(x)
                if x == point:
                    if len(complete_route) > len(temp):
                        complete_route = temp
                        print(temp)
                    break


    return complete_route
