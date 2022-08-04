import core.image_transform
import core.func
import pygame

class Button:
    def __init__(self, game, obj ,slotx, sloty, team, image, activator = "", oneshot = False, oneshot_func = None, active = False, argument = None, key_press = ""):
        self.x = slotx
        self.y = sloty
        self.game_ref = game
        self.parent_ref = obj
        self.team = team
        self.image = image
        self.image2 = core.image_transform.colorize_alpha(image.copy(), pygame.Color(0,0,0), 100)
        self.active = False
        self.oneshot = oneshot
        self.oneshot_func = oneshot_func
        self.active = active
        self.argument = argument
        self.activator = activator
        self.key_press = key_press
        self.button_sizex, self.button_sizey = self.image.get_size()


    def tick(self):

        if (core.func.point_inside(self.game_ref.mouse_pos, [self.x*100*self.game_ref.qsc,self.y*100*self.game_ref.qsc], [self.button_sizex*self.game_ref.qsc,self.button_sizey*self.game_ref.qsc]) and "mouse0" in self.game_ref.keypress) or self.key_press in self.game_ref.keypress:
            print("CLICK")

            #self.game_ref.sounds["menu1"].play()
            if self.oneshot:
                self.oneshot_func(self.argument)
            else:
                if not self.active:
                    self.active = True

                    for x in self.parent_ref.buttons:
                        if x != self:
                            x.active = False
            try:

                self.parent_ref.check_mode()
            except:
                pass




        if self.active:

            self.game_ref.screen.blit(self.image,[self.x * 100*self.game_ref.qsc, self.y * 100*self.game_ref.qsc + self.parent_ref.smoothing])
            pygame.draw.rect(self.game_ref.screen, self.team, [self.x * 100*self.game_ref.qsc, self.y * 100*self.game_ref.qsc + self.parent_ref.smoothing, self.button_sizex*self.game_ref.qsc, self.button_sizey*self.game_ref.qsc],5)
        else:

            self.game_ref.screen.blit(self.image2,[self.x * 100*self.game_ref.qsc, self.y * 100*self.game_ref.qsc + self.parent_ref.smoothing])
            pygame.draw.rect(self.game_ref.screen, self.team, [self.x * 100*self.game_ref.qsc, self.y * 100*self.game_ref.qsc + self.parent_ref.smoothing, self.button_sizex*self.game_ref.qsc, self.button_sizey*self.game_ref.qsc],1)
