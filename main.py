import global_values as g
import graphics as gfx
import pygame as p
import os

import levels
import cameras
import players
import controls
import entities
import actions
import sounds

p.mixer.init()
sounds.load_sounds()
g.channel_list = sounds.ChannelList()

g.global_pipe = actions.Pipe("global")

g.screen = p.Surface((g.WIDTH, g.HEIGHT))
g.full_screen = p.display.set_mode((g.SCREEN_WIDTH, g.SCREEN_HEIGHT))

gfx.Spritesheet("player_ss", 16,32)
gfx.Spritesheet("basic_enemy_ss", 16,32)
gfx.Spritesheet("large_enemy_ss", 32,60)
gfx.Spritesheet("structure_16_32_ss", 16,32)
gfx.Spritesheet("corpse_ss", 32, 32)
gfx.Spritesheet("button_ss", 8,8)
gfx.Spritesheet("med_button_ss", 12,12)
gfx.Spritesheet("large_button_ss", 32,16)

p.font.init()
g.fonts = {
    "font1_1":p.font.Font(os.path.join(g.FONTS_DIR, "Lo-Res 9 Narrow.ttf"), 9)
}

g.game_clock = p.time.Clock()

for file_name in os.listdir(g.LEVELS_DIR):
    if file_name.endswith(".json"):
        levels.Level(file_name[:-5])

g.current_level = g.levels["Cryo I"]
for level in g.levels.values():
    level.linkup()

g.player = players.Player()
g.camera = cameras.Camera(g.player, (-32, -48))

#menu
def start_game():
    reset()

inv_button = None
def load_game():
    #TODO FIX THIS
    global inv_button
    reset()
    import pickle
    byte_sum = 0


    #save
    #res = pickle.dumps(g.elements)
    #print("RES:", len(res))
    #inv_button 
    #elements = pickle.loads(res)
    #g.elements = elements


    #res = pickle.dumps(g.levels)
    #print(len(res))
    #g.levels = pickle.loads(res)


    
    

controls.MainMenuControl()
rect = p.Rect(0, 0, 32, 16)
rect.centerx = g.screen_rect.centerx
rect.centery = 48
ss_anims = g.spritesheets["large_button_ss"].anims
controls.Button(rect, start_game, ss_anims[1][0], ss_anims[1][1], ss_anims[1][2], set(("mainmenu",)))

rect = rect.copy()
rect.y -= 16
#controls.Button(rect, load_game, ss_anims[0][0], ss_anims[0][1], ss_anims[0][2], set(("mainmenu",)))

#background
controls.BackgroundControl("space_background", set(("main",)))

#main
rect = p.Rect(0, 0, g.WIDTH, 8)
controls.GraphicsControl(rect, "controls_background", set(("main",)))

rect = p.Rect(0,0,15,7)
controls.MapControl(rect, set(("main",)))

rect = p.Rect(rect.right+1, 0, 32, 8)
controls.ItemControl(rect, set(("main",)))

rect = p.Rect(0, 0, 12, 8)
rect.topright = g.screen_rect.topright
controls.HealthControl(rect, set(("main",)))

rect = p.Rect(0, 0, 8, 8)
rect.bottomleft = g.screen_rect.bottomleft
def enter_inventory():
    g.active_states = set(("inventory",))
    g.player.control_locks += 1

def exit_menu():
    g.active_states = set(("main",))
    g.player.control_locks -= 1

inv_button = controls.Button(rect, enter_inventory, g.spritesheets["button_ss"].anims[0][0], g.spritesheets["button_ss"].anims[0][1], g.spritesheets["button_ss"].anims[0][2], set(("main",)))


#inventory
inventory_control = controls.InventoryControl(g.player.inventory, g.screen_rect, set(("inventory",)) )


rect = p.Rect(0, 0, 8, 8)
rect.bottomleft = g.screen_rect.bottomleft
controls.Button(rect, exit_menu, g.spritesheets["button_ss"].anims[1][0], g.spritesheets["button_ss"].anims[1][1], g.spritesheets["button_ss"].anims[1][2], set(("inventory",)))


def handle_input():
    global RUNNING
    for event in p.event.get():
        if event.type == p.QUIT:
            RUNNING = False

        if event.type == p.MOUSEBUTTONDOWN:
            if event.button == 3:

                command_triggered = False
                for structure in g.current_level.structures:
                    if structure.can_interact and structure.rect.collidepoint((g.tmx, g.tmy)):
                        structure.interact()
                        command_triggered = True
                        break

                if not command_triggered:
                    if not g.player.control_locks:
                        g.player.set_target_x(g.tmx)


            elif event.button == 1:
                button_pressed = False
                for button in reversed(g.elements["class_Button"]):
                    if button.active and button.rect.collidepoint((g.mx, g.my)):
                        button_pressed = True
                        button.press()
                        break

                if "inventory" in g.active_states:
                    if inventory_control.highlighted_slot is not None:
                        g.player.inventory.select_index(inventory_control.highlighted_slot)
                        button_pressed = True

                if not button_pressed:
                    if g.player.inventory.selected_item:
                        g.player.attack()


    g.keys = p.key.get_pressed()
    g.ml, g.mm, g.mr = p.mouse.get_pressed()
    g.mx, g.my = p.mouse.get_pos()
    g.mx *= (g.WIDTH/g.SCREEN_WIDTH)
    g.my *= (g.HEIGHT/g.SCREEN_HEIGHT)

    g.tmx = g.mx + g.camera.x
    g.tmy = g.my + g.camera.y

    if g.keys[p.K_a]:
        g.player.move(-1*0.02, 0)
    if g.keys[p.K_d]:
        g.player.move(1*0.02, 0)

def update():
    i = 0
    while i < len(g.pipe_list):
        g.pipe_list[i].update()
        i += 1

    in_main = "main" in g.active_states
    for element in g.element_list:
        if isinstance(element, entities.Entity) and (element.level != g.current_level or not in_main):
            element.update_inactive()
            continue

        if isinstance(element, controls.Control):
            if g.active_states.isdisjoint(element.active_states):
                element.active = False
                continue
                
            else:
                element.active = True
            

        element.update()

def draw():
    if g.current_level.show_space:
        for control in g.elements.get("class_BackgroundControl"):
            control.draw()

    if "main" in g.active_states:
        g.current_level.draw()

        for entity in g.elements.get("class_Entity", []):
            if entity.level != g.current_level:
                continue

            entity.draw()

    for control in g.elements.get("class_Control", []):
        if not g.active_states.isdisjoint(control.active_states) and not isinstance(control, controls.BackgroundControl):
            control.draw()

    for pipe in g.pipes.values():
        pipe.draw()

def reset():
    g.active_states = set(("main",))

g.active_states = set(("mainmenu",))

RUNNING = True
while RUNNING:
    g.screen.fill("black")
    handle_input()
    update()
    draw()

    g.dt = g.game_clock.tick()/1000
    #print(g.dt)

    #upscale and display
    g.full_screen.blit(p.transform.scale(g.screen, (g.SCREEN_WIDTH, g.SCREEN_HEIGHT)), (0,0))
    p.display.flip()


quit()

def quit():
    import sys
    sys.exit()