import pygame as p
import math as m

import global_values as g
import graphics as gfx
import elements
import items
import sounds

class Control(elements.Element):
    """
    Base class for all controls 
    """
    def __init__(self, rect, active_states):
        super().__init__(rect)
        self.active_states = active_states

        self.active = True
        

        self.active = False

    def update(self):
        super().update()
        self.active = not g.active_states.isdisjoint(self.active_states)

    def draw(self):
        super().draw()


class Button(Control):
    """
    Control for buttons
    """
    def __init__(self, rect, func, unpressed_gfx, highlighted_gfx, pressed_gfx, active_states):
        super().__init__(rect, active_states)

        self.unpressed_gfx = unpressed_gfx
        self.highlighted_gfx = highlighted_gfx
        self.pressed_gfx = pressed_gfx

        self.highlighted = False
        self.pressed = False

        self.func = func

    def press(self):
        sounds.play_sound("button_press")
        self.func()

    def update(self):
        super().update()
        if self.rect.collidepoint((g.mx, g.my)):
            self.highlighted = True
            
            if g.ml:
                self.pressed = True
            else:
                self.pressed = False
        else:
            self.highlighted = False
            self.pressed = False

    def draw(self):
        if self.highlighted:
            if self.pressed:
                button_gfx = self.pressed_gfx
            else:
                button_gfx = self.highlighted_gfx
        else:
            button_gfx = self.unpressed_gfx
        g.screen.blit(gfx.get_surface(button_gfx), self.rect.topleft)

class GraphicsControl(Control):
    """
    Control for showing graphics
    """
    def __init__(self, rect, control_gfx, active_states):
        super().__init__(rect, active_states)
        self.gfx = control_gfx

    def draw(self):
        super().draw()
        g.screen.blit(gfx.get_surface(self.gfx), self.rect.topleft)

class BackgroundControl(GraphicsControl):
    """
    Control for showing a background
    Essentially a graphics control but gets hidden by the end of a level
    """
    def __init__(self, background_gfx, active_states):
        super().__init__(g.screen_rect, background_gfx, active_states)

    def draw(self):
        super().draw()
        #draw borders
        left_border = g.camera.transform_point((g.current_level.rect.left,0))[0]
        right_border = g.camera.transform_point((g.current_level.rect.right,0))[0]
        
        p.draw.rect(g.screen, g.convert_colour("black"), p.Rect(0,0,left_border,g.HEIGHT))
        p.draw.rect(g.screen, g.convert_colour("black"), p.Rect(right_border,0,g.WIDTH-right_border+1,g.HEIGHT))

class MainMenuControl(GraphicsControl):
    """
    Control for showing main menu background
    """
    def __init__(self):
        super().__init__(g.screen_rect.copy(), "space_background", set(("mainmenu",)) )
        self.ship_surface = gfx.load_image("ship")

        self.offset_x = 0
        self.ship_x = self.rect.centerx - (self.ship_surface.get_width()/2)
        self.ship_y = self.rect.centery - (self.ship_surface.get_height()/2) - 8

    def draw(self):
        super().draw()
        self.offset_x = m.sin((p.time.get_ticks()/1000) * (2*m.pi) * 0.05)*8
        g.screen.blit(self.ship_surface, (self.ship_x+self.offset_x, self.ship_y))

class SlidesControl(GraphicsControl):
    """
    Control for displaying a slideshow of images
    """
    def __init__(self, rect, font_name, slides, end_func, active_states, background_colour=g.convert_colour("white"), font_colour=g.convert_colour("black")):
        self.slides = slides
        #create slides
        for i,slide in enumerate(self.slides):
            if type(slide) == str and slide.startswith("img:"):
                slide = gfx.load_image(slide[4:])
                self.slides[i] = slide

        self.slide_index = 0

        self.font_name = font_name
        self.background_colour = background_colour
        self.font_colour = font_colour

        super().__init__(rect, None, active_states)

        self.background_surface = p.Surface((self.rect.w, self.rect.h))
        self.background_surface.fill(self.background_colour)

        button_anims = g.spritesheets["button_ss"].anims


        button_rect = p.Rect(0,0,8,8)
        button_rect.bottomright = self.rect.bottomright
        self.button_progress = Button(button_rect, self.progress, button_anims[6][0], button_anims[6][1], button_anims[6][2], self.active_states)

        self.end_func = end_func

    def progress(self):
        self.slide_index += 1
        if self.slide_index >= len(self.slides):
            self.end_func()
            self.delete()

    def draw(self):
        slide = self.slides[self.slide_index]

        if type(slide) == str:
            self.gfx = self.background_surface
            #x = self.rect.centerx
            #y = 20
            
            #draw_text(self.font_name, slide, pos, cx=False, cy=False, colour="black", alpha=255):
        else:
            self.gfx = slide

        super().draw()

        if type(slide) == str:
            gfx.draw_wrapped_text(self.font_name, slide, self.rect.inflate((-4,-4)), colour=self.font_colour, spacing=10)

    def delete(self):
        super().delete()
        self.button_progress.delete()

class GameOverControl(GraphicsControl):
    """
    Control for showing end screen background
    """
    def __init__(self):
        super().__init__(g.screen_rect.copy(), "gameover_background", set(("gameover",)) )
        self.slides = []

    def draw(self):
        super().draw()

class StartScreenControl(SlidesControl):
    """
    Control for showing start screen
    """
    def __init__(self):
        slides = [
            "I awoke on the station.",
            "It seems my Cyro pod had taken some damage.",
            "The station was in disrepair, something was very wrong.",
            "I put on a nearby space suit, and went to investigate."
        ]
        super().__init__(g.screen_rect, "font1_1", slides, self.finish, set(("main",)), background_colour="white", font_colour=g.convert_colour("black"))

    def update(self):
        super().update()

    def finish(self):
        self.delete()

    def draw(self):
        super().draw()


class EndScreenControl(SlidesControl):
    """
    Control for showing end screen 
    """
    def __init__(self):
        slides = [
            "As the pod departed, the planet began to transform.",
            g.spritesheets["end_ss"].anims[0][0],
            "Its evil influence became part of its physical form",
            g.spritesheets["end_ss"].anims[0][1],
            "And mine as well.",
            g.spritesheets["end_ss"].anims[0][2],
            "Thanks for playing.",
            "Credits: Baconinv: Programming Ghast: Art"
        ]
        super().__init__(g.screen_rect, "font1_1", slides, self.back_to_menu, set(("end",)), background_colour=g.convert_colour("white"), font_colour=g.convert_colour("black"))

    def back_to_menu(self):
        g.active_states = set(("mainmenu",))

    def draw(self):
        super().draw()

class HealthControl(Control):
    """
    Control for showing player health
    """
    def __init__(self, rect, active_states):
        super().__init__(rect, active_states)

    def draw(self):
        p.draw.rect(g.screen, g.convert_colour("green"), self.rect)

        health_string = str(int(g.player.health))

        gfx.draw_text("font1_1", health_string, self.rect.move(1, 0).center, cx=True, cy=True)


class ItemControl(Control):
    """
    Control for showing the current player item
    """
    def __init__(self, rect, active_states):
        super().__init__(rect, active_states)

    def draw(self):
        item = g.player.inventory.selected_item
        if item:
            g.screen.blit(item.icon, self.rect)

            #draw ammunition
            if isinstance(item, items.Gun):
                icon_width = item.icon.get_width()
                remaining_space = self.rect.w-icon_width

                if item.recharge:
                    ammunition_frac = item.ammunition % 1
                    x = int(remaining_space*ammunition_frac)
                    p.draw.rect(g.screen, g.convert_colour("blue"), p.Rect(self.rect.x+icon_width+x, self.rect.y, 1, self.rect.h))

                ticks = p.time.get_ticks()
                if item.last_fire_time and (ticks - item.last_fire_time)/1000 < item.max_cooldown:
                    cooldown_frac = (ticks - item.last_fire_time)/1000/item.max_cooldown
                    x = int(remaining_space*cooldown_frac)
                    p.draw.rect(g.screen, g.convert_colour("brown"), p.Rect(self.rect.x+icon_width+x, self.rect.y, 1, self.rect.h))

                ammunition_string = f"x{int(item.ammunition)}"
                gfx.draw_text("font1_1", ammunition_string, self.rect.move((icon_width + 1, -self.rect.h/2 + 1)).topleft)

                
class MapControl(Control):
    """
    Control for displaying a minimap
    """
    def __init__(self, rect, active_states):
        super().__init__(rect, active_states)
        self.pixel_size = 64

    def draw(self):
        surf = p.Surface((self.rect.w, self.rect.h))
        surf.fill(g.convert_colour("black"))
        offset_x = (g.player.level.world_x) + (g.player.rect.centerx//self.pixel_size)
        offset_y = (g.player.level.world_y)
        for level in g.levels.values():
            lx = level.world_x
            ly = level.world_y
            lw = level.rect.w//self.pixel_size
            lh = level.rect.h//self.pixel_size
            if level == g.player.level:
                colour = "blue"
            else:
                lum = int(255/lw)
                cr = max(min(int(lum*0.75), 255), 64)
                cg = max(min(int(lum*2), 255), 64)
                cb = max(min(int(lum*0.75), 255), 64)
                colour = (cr,cg,cb)

            #if level.name == "Eng I":
            #    print(lx, ly)
            #    colour = "yellow"

            # I'm ok using non-palette colors in the map - Ghast
            p.draw.rect(surf, colour, p.Rect(lx-offset_x+ (self.rect.w//2), ly-offset_y+ (self.rect.h//2), lw, lh))

            if level == g.player.level:
                px = lx+int( (g.player.x+1) //self.pixel_size)
                surf.set_at((px-offset_x+ (self.rect.w//2), ly-offset_y+ (self.rect.h//2)), "red")

            if g.power_diverted:
                for shuttle in g.elements.get("class_Shuttle",[]):
                    if shuttle in level.structures:
                        px = lx+int( (shuttle.x+1) //self.pixel_size)
                        surf.set_at((px-offset_x+ (self.rect.w//2), ly-offset_y+ (self.rect.h//2)), "red")


        g.screen.blit(surf, self.rect)

class InventoryControl(Control):
    """
    Control for displaying all inventory slots
    """
    def __init__(self, inventory, rect, active_states):
        super().__init__(rect, active_states)
        self.inventory = inventory

        self.cell_size = 10
        self.sep_h = 2
        self.sep_v = 12
        self.start_y = 10

        self.highlighted_slot = None

    def draw(self):
        self.highlighted_slot = None

        g.screen.blit(gfx.get_surface("inventory_background"), self.rect)

        x = self.sep_h
        y = self.start_y
        
        for i,cell in enumerate(self.inventory.slots):
            if cell:
                w = max(self.cell_size, cell.icon.get_width()+2)
            else:
                w = self.cell_size
            rect = p.Rect(x, y, w, self.cell_size)

            colour = "black"
            if rect.collidepoint((g.mx, g.my)):
                self.highlighted_slot = i

            if self.inventory.selected_index == i:
                colour = "red"
            elif self.highlighted_slot == i:
                colour = "brown"

            p.draw.rect(g.screen, g.convert_colour(colour), rect, 1)

            if cell:
                if cell.icon.get_width() == rect.w-2:
                    g.screen.blit(cell.icon, rect.move((1,1)))
                else:
                    p.draw.rect(g.screen, g.convert_colour("white"), rect.inflate((-2,-2)))
                    g.screen.blit(cell.icon, rect.move(( 1 + (rect.w/2) - (cell.icon.get_width()/2) , 1 + (rect.h/2) - (cell.icon.get_height()/2)  )))
                #draw amount
                if cell.amount > 1:
                    amount_string = str(cell.amount)
                    gfx.draw_text("font1_1", amount_string, rect.move((0,-self.cell_size)).center, cx=True, cy=True, colour="blue")

            x = rect.right + self.sep_h

            if x + self.cell_size >= self.rect.right:
                x = self.sep_h
                y += self.cell_size + self.sep_v

        if self.highlighted_slot is not None:
            detail_item = self.inventory.slots[self.highlighted_slot]
            if detail_item:
                x = self.rect.centery
                y = 48
                detail_string = detail_item.name
                gfx.draw_text("font1_1", detail_string, (x,y), cx=True, cy=True)

                y += 8
                extra_detail_string = ""
                if isinstance(detail_item, items.Gun):
                    extra_detail_string = f"{int(detail_item.ammunition)}/{detail_item.max_ammunition} rnds"
                elif type(detail_item) == items.HealthDrink:
                    extra_detail_string = "+3 HP"
                elif type(detail_item) == items.Medkit:
                    extra_detail_string = "+5 HP"


                gfx.draw_text("font1_1", extra_detail_string, (x,y), cx=True, cy=True)

class GraphicsScreenControl(Control):
    """
    Control for showing graphics on the whole screen
    """
    def __init__(self, control_gfx, active_states, show_exit=True):
        rect = g.screen_rect.copy()
        super().__init__(rect, active_states)
        self.gfx = control_gfx

        self.show_exit = show_exit
        if self.show_exit:
            button_anims = g.spritesheets["button_ss"].anims
            button_rect = p.Rect(0,0,8,8)
            button_rect = button_rect.copy()
            button_rect.bottomright = self.rect.bottomright
            self.button_exit = Button(button_rect, self.delete, button_anims[3][0], button_anims[3][1], button_anims[3][2], self.active_states)

    def draw(self):
        super().draw()
        g.screen.blit(gfx.get_surface(self.gfx), self.rect.topleft)

    def delete(self):
        if self.show_exit:
            self.button_exit.delete()
        super().delete()

class TextScreenControl(Control):
    """
    Control for displaying text on screen
    """
    def __init__(self, rect, font_name, text, active_states, background_gfx="text_screen_background", margin=4, scroll_space=None):
        super().__init__(rect, active_states)

        self.text = text
        self.font_name = font_name
        self.scroll = 0

        self.margin = margin
        if not scroll_space:
            scroll_space = len(text)
        self.scroll_space = scroll_space

        self.background_gfx = gfx.get_surface(background_gfx)

        #buttons
        button_anims = g.spritesheets["button_ss"].anims
        button_rect = p.Rect(0,0,8,8)
        button_rect.bottomleft = self.rect.bottomleft
        self.button_exit = Button(button_rect, self.delete, button_anims[3][0], button_anims[3][1], button_anims[3][2], self.active_states)

        button_rect = button_rect.copy()
        button_rect.bottomright = self.rect.bottomright
        self.button_down = Button(button_rect, self.scroll_down, button_anims[4][0], button_anims[4][1], button_anims[4][2], self.active_states)
        button_rect = button_rect.copy()
        button_rect.x -= 8
        self.button_up = Button(button_rect, self.scroll_up, button_anims[5][0], button_anims[5][1], button_anims[5][2], self.active_states)
        
        g.player.control_locks += 1

    def scroll_up(self):
        """
        Scroll text up
        """
        self.scroll -= 4
        if self.scroll < 0:
            self.scroll = 0

    def scroll_down(self):
        """
        Scroll text down
        """
        self.scroll += 4
        if self.scroll > self.scroll_space:
            self.scroll = self.scroll_space

    def draw(self):
        g.screen.blit(self.background_gfx, self.rect)

        text_rect = self.rect.copy()
        text_rect.x += self.margin
        text_rect.w -= self.margin*2

        text_rect.y -= self.scroll
        text_rect.h -= 8
        gfx.draw_wrapped_text(self.font_name, self.text, text_rect, colour=g.convert_colour("white"), alpha=255, spacing=10)

        header_rect = p.Rect(self.rect.x, 0, self.rect.w, self.margin)
        g.screen.blit(self.background_gfx, header_rect, header_rect)

        footer_rect = p.Rect(self.rect.x, self.rect.bottom-self.margin, self.rect.w, self.margin)
        g.screen.blit(self.background_gfx, footer_rect, footer_rect)

    def delete(self):
        super().delete()
        self.button_exit.delete()
        self.button_down.delete()
        self.button_up.delete()
        g.player.control_locks -= 1

class Popup(Control):
    """
    Control for showing popup text
    """
    def __init__(self, rect, line1, line2, func1, active_states, func2=None, show_accept=True, show_reject=True, background_gfx="prompt_background"):
        super().__init__(rect, active_states)
        sounds.play_sound("popup")

        self.line1 = line1
        self.line2 = line2

        self.background_gfx = gfx.get_surface(background_gfx)

        g.player.control_locks += 1

        if not func2:
            func2 = self.delete

        button_anims = g.spritesheets["button_ss"].anims

        self.show_accept = show_accept
        self.show_reject = show_reject

        button_rect = p.Rect(0,0,8,8)
        if self.show_accept:
            button_rect.bottomleft = self.rect.bottomleft
            self.button_accept = Button(button_rect, func1, button_anims[2][0], button_anims[2][1], button_anims[2][2], self.active_states)

        if self.show_reject:
            button_rect = button_rect.copy()
            button_rect.bottomright = self.rect.bottomright
            self.button_reject = Button(button_rect, func2, button_anims[3][0], button_anims[3][1], button_anims[3][2], self.active_states)

    def draw(self):
        g.screen.blit(self.background_gfx, self.rect)
        x = self.rect.centery
        y = self.rect.y + 8
        gfx.draw_text("font1_1", self.line1, (x,y), cx=True, cy=True)

        y += 12
        gfx.draw_text("font1_1", self.line2, (x,y), cx=True, cy=True)
        

    def delete(self):
        g.player.control_locks -= 1
        if self.show_accept:
            self.button_accept.delete()
        if self.show_reject:
            self.button_reject.delete()
        super().delete()

class Keypad_Popup(Popup):
    """
    Control for keypad
    """
    def __init__(self, locked_object):
        rect = g.screen_rect.copy()
        super().__init__(rect, "Code:", "", self.confirm, set(("main",)), background_gfx="keypad_background")

        self.locked_object = locked_object
        self.entered_code = ""
        self.max_digits = 3

        #create buttons
        self.buttons = []
        button_anims = g.spritesheets["med_button_ss"].anims

        start_x = 12
        start_y = 20
        x = start_x
        y = start_y
        button_sep = 2
        cell_size = 12
        
        button_index = 1
        for anim_x in range(3):
            for anim_y in range(3):
            
                button_rect = p.Rect(x, y, cell_size, cell_size)
                button_val = ((anim_y*3)+anim_x) + 1

                button_func = eval(f"self.add_number{button_val}")
                button = Button(button_rect, button_func, button_anims[anim_y][anim_x], button_anims[anim_y][anim_x], button_anims[anim_y][anim_x], self.active_states)

                y += cell_size + button_sep

                self.buttons.append(button)
            
            y = start_y
            x += cell_size + button_sep

        
    def add_number(self, value):
        sounds.play_sound("keypad_press")
        if len(self.entered_code) < self.max_digits:
            self.entered_code += str(value)

    #LOOK I TRIED TO GET THIS TO WORK WITH LAMBDA I REALLY DID BUT IT DIDN'T WORK
    def add_number1(self):
        self.add_number(1)
    def add_number2(self):
        self.add_number(2)
    def add_number3(self):
        self.add_number(3)
    def add_number4(self):
        self.add_number(4)
    def add_number5(self):
        self.add_number(5)
    def add_number6(self):
        self.add_number(6)
    def add_number7(self):
        self.add_number(7)
    def add_number8(self):
        self.add_number(8)
    def add_number9(self):
        self.add_number(9)

    def confirm(self):
        self.locked_object.attempt_unlock(value=self.entered_code)
        self.delete()

    def delete(self):
        for button in self.buttons:
            button.delete()
        super().delete()

    def draw(self):
        super().draw()
        x = self.rect.centerx
        y = 16
        #print(self.entered_code)
        gfx.draw_text("font1_1", self.entered_code, (x,y), cx=True, cy=True)

class Item_Popup(Popup):
    """
    Control for asking player if they want to pick up an item
    """
    def __init__(self, item, pickup=None, delete_pickup=True):
        rect = p.Rect(0, 0, 56, 32)
        rect.center = g.screen_rect.center
        self.item = item
        self.pickup = pickup
        self.delete_pickup = delete_pickup
        super().__init__(rect, "Pickup", self.item.name+str("?"), self.confirm, set(("main",)), background_gfx="popup_pickup_background")

    def confirm(self):
        if g.player.inventory.add_item(self.item):
            self.item.pickup()
            self.delete()
            sounds.play_sound("pickup")
            if self.pickup:
                if self.delete_pickup:
                    self.pickup.delete()
                else:
                    self.pickup.interaction_enabled = False

class Timer(Control):
    """
    Control for displaying a timer on screen associated with an action
    """
    def __init__(self, font_name, rect, action, active_states, colour=g.convert_colour("black"), shadow_pos=None):
        super().__init__(rect, active_states)
        self.font_name = font_name
        self.action = action
        self.colour = colour
        self.shadow_pos = shadow_pos

    def update(self):
        super().update()
        if self.action.progress >= 1:
            self.delete()

    def draw(self):
        minutes = str(int(self.action.timer // 60)).zfill(2)
        seconds = str(int(self.action.timer % 60)).zfill(2)
        seconds_decimal = int(round(self.action.timer % 1, 1)*10)
        if seconds_decimal == 10:
            seconds_decimal = 0

        timer_string = f"{minutes}:{seconds}.{seconds_decimal}"
        if self.shadow_pos:
            gfx.draw_text(self.font_name, timer_string, self.rect.move(self.shadow_pos).center, cx=True, cy=True, colour=g.colour_remaps["beige"], alpha=255)
            
        gfx.draw_text(self.font_name, timer_string, self.rect.center, cx=True, cy=True, colour=self.colour, alpha=255)

        