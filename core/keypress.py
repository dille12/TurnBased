import pygame
import core.func


def key_press_manager(obj):

    obj.mouse_pos = core.func.minus(list(pygame.mouse.get_pos()),obj.size_conv,op="*")
    #obj.mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    keys = pygame.key.get_pressed()

    for key, sign in [
    [pygame.K_w, "w"],
    [pygame.K_a, "a"],
    [pygame.K_s, "s"],
    [pygame.K_d, "d"],
    [pygame.K_ESCAPE, "esc"]
    ]:
        if keys[key]:
            if sign in obj.keypress:
                obj.keypress.remove(sign)
            elif sign not in obj.keypress_held_down:
                obj.keypress.append(sign)


            if sign not in obj.keypress_held_down:
                obj.keypress_held_down.append(sign)
        else:
            if sign in obj.keypress:
                obj.keypress.remove(sign)
            if sign in obj.keypress_held_down:
                obj.keypress_held_down.remove(sign)

    for x in range(3):
        sign = "mouse" + str(x)
        if pygame.mouse.get_pressed()[x]:
            if sign in obj.keypress:
                obj.keypress.remove(sign)
            elif sign not in obj.keypress_held_down:
                obj.keypress.append(sign)


            if sign not in obj.keypress_held_down:
                obj.keypress_held_down.append(sign)
        else:
            if sign in obj.keypress:
                obj.keypress.remove(sign)
            if sign in obj.keypress_held_down:
                obj.keypress_held_down.remove(sign)
