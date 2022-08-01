import pygame

def render_text(game, string, pos, font_size, center = False, color = [255,255,255]):
    text = game.terminal[font_size].render(str(string), False, color)
    game.screen.blit(text, pos) #


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
