import pygame
import random
import sqlite3
import datetime
import pandas
from inspect import currentframe, getframeinfo

pygame.init()

#Screen
scale = 50
height = 20*scale
width = 20*scale
screen = pygame.display.set_mode([width, height])

pygame.mixer.init()

debugging = False

con = sqlite3.connect("MaxMight01_Tetris.db")
cursor = con.cursor()

right_now = datetime.datetime.now()
dt_string = right_now.strftime("Tetris__%Y_%m_%d__%H_%M_%S")
dt_string2 = right_now.strftime("Tetris__%Y_%m_%d__%H_%M_%S__FrameData")

pseudofps = 60
timer = pygame.time.Clock()

pygame.display.set_caption("MaxMight01 TETRIS")

font1 = pygame.font.SysFont('videotyperegular', int(scale*0.75)) #For 'on hold' and 'up next'
font2 = pygame.font.SysFont('videotyperegular', int(scale*1.05)) #For 'score' and 'combo'
font3 = pygame.font.SysFont('videotyperegular', int(scale*3.15)) #For 'GAME OVER'
font4 = pygame.font.SysFont('videotyperegular', int(scale*1.5)) #For game over 'score' and 'combo'


#Game Functions

#p is piece number, r is rotation state
def left_right_bound(p, r):
    q = 4*p + r
    
    if q == 30:
        left = 2
    elif q == 5 or q == 9 or p == 3 or q == 17 or q == 21 or q == 25 or q == 29 or q == 31:
        left = 0
    else:
        left = 1

    if q == 28:
        right = 2
    elif q == 7 or q == 11 or q == 19 or q == 23 or q == 27 or q == 29 or q == 31:
        right = 0
    else:
        right = 1

    return left, right

#p is piece number
def piece_color(p):
    if p == 1:
        mycolor = 'red'
    elif p == 2:
        mycolor = 'lime'
    elif p == 3:
        mycolor = 'yellow'
    elif p == 4:
        mycolor = 'orange'
    elif p == 5:
        mycolor = 'blue'
    elif p == 6:
        mycolor = 'purple'
    elif p == 7:
        mycolor = 'cyan'

    return mycolor

#x is x_pos and y is y_pos
def draw_block(x, y, color):
    return pygame.draw.rect(screen, color, pygame.Rect(x*scale+1, y*scale+1, scale-1, scale-1))

#p is piece number, r is rotation state
def piece_structure(p, r):
    q = 4*p + r
    
    mylist = []
    if q in [6, 7, 8, 11, 16, 18, 20, 22, 24, 26, 27, 28, 30]:
        mylist.append(0)
    if q in [4, 11, 19, 20]:
        mylist.append(1)
    if q in [4, 7, 8, 9, 12, 13, 14, 15, 17, 19, 21, 23, 24, 25, 27, 29, 31]:
        mylist.append(2)
    if q in [5, 8, 12, 13, 14, 15, 16, 21]:
        mylist.append(3)
    if q in [4, 5, 9, 10, 12, 13, 14, 15, 16, 18, 20, 22, 24, 25, 26, 28, 30]:
        mylist.append(4)
    if q in [6, 9, 17, 22]:
        mylist.append(5)
    if q in [5, 6, 10, 11, 17, 19, 21, 23, 25, 26, 27, 29, 31]:
        mylist.append(6)
    if q in [7, 10, 18, 23]:
        mylist.append(7)
    if q == 28:
        mylist.append(10)
    elif q == 29:
        mylist.append(11)
    elif q == 30:
        mylist.append(8)
    elif q == 31:
        mylist.append(9)

    truelist = []
    if 0 in mylist:
        truelist.append([-1, 0])
    if 1 in mylist:
        truelist.append([-1, -1])
    if 2 in mylist:
        truelist.append([0, -1])
    if 3 in mylist:
        truelist.append([1, -1])
    if 4 in mylist:
        truelist.append([1, 0])
    if 5 in mylist:
        truelist.append([1, 1])
    if 6 in mylist:
        truelist.append([0, 1])
    if 7 in mylist:
        truelist.append([-1, 1])
    if 8 in mylist:
        truelist.append([-2, 0])
    if 9 in mylist:
        truelist.append([0, -2])
    if 10 in mylist:
        truelist.append([2, 0])
    if 11 in mylist:
        truelist.append([0, 2])

    if q in [0]:
        truelist = [[0, 0], [0, 0], [0, 0]]

    return truelist


def rotation_check(active_gameboard, ghost_gameboard, passive_gameboard, rdirection):
    x_pos = active_gameboard.x_pos
    y_pos = active_gameboard.y_pos
    new_rstate = (active_gameboard.rstate+rdirection)%4

    rotation_denied = False
    newx_pos = x_pos
    newy_pos = y_pos

    left_overlap = False
    right_overlap = False
    bottom_overlap = False
    top_overlap = False
    
    
    structure_list = piece_structure(active_gameboard.piecenumber, new_rstate)
    
    for minilist in structure_list:
        
        if x_pos+minilist[0] < 0:
            left_overlap = True
        elif minilist[0] < 0 and x_pos+minilist[0] >= 0:
            if passive_gameboard.gameboard[y_pos+minilist[1]][x_pos+minilist[0]] > 0:
                left_overlap = True
                
        if x_pos+minilist[0] > 9:
            right_overlap = True
        elif minilist[0] > 0 and x_pos+minilist[0] <= 9:
            if passive_gameboard.gameboard[y_pos+minilist[1]][x_pos+minilist[0]] > 0:
                right_overlap = True

        if y_pos+minilist[1] > 19:
            bottom_overlap = True
        elif minilist[1] > 0:
            if passive_gameboard.gameboard[y_pos+minilist[1]][x_pos+minilist[0]] > 0:
                bottom_overlap = True

    
    if left_overlap and not right_overlap:
        newx_pos += 1
    elif right_overlap and not left_overlap:
        newx_pos -= 1
    elif left_overlap and right_overlap:
        rotation_denied = True

    if top_overlap and not bottom_overlap:
        newy_pos += 1
    elif bottom_overlap and not top_overlap:
        newy_pos -= 1
    elif top_overlap and bottom_overlap:
        rotation_denied = True

    if not rotation_denied:
        if passive_gameboard.gameboard[newy_pos][newx_pos] > 0:
            rotation_denied = True
            
        for minilist in structure_list:
            if newx_pos+minilist[0] < 0 or newx_pos+minilist[0] > 9:
                rotation_denied = True
            elif newy_pos+minilist[1] >= 0:
                if passive_gameboard.gameboard[newy_pos+minilist[1]][newx_pos+minilist[0]] > 0:
                    rotation_denied = True
                
        if not rotation_denied:
            active_gameboard.x_pos = newx_pos
            active_gameboard.y_pos = newy_pos
            ghost_gameboard.x_pos = newx_pos
            ghost_gameboard.y_pos = newy_pos

    return rotation_denied




def draw_text(text, font, color, x, y):
    text_image = font.render(text, True, color)
    textRect = text_image.get_rect()
    textRect.midleft = (x, y)
    screen.blit(text_image, textRect)

def draw_text_gameover(text, font, color, x, y):
    text_image = font.render(text, True, color)
    textRect = text_image.get_rect()
    textRect.center = (x, y)
    screen.blit(text_image, textRect)

def draw_text_midright(text, font, color, x, y):
    text_image = font.render(text, True, color)
    textRect = text_image.get_rect()
    textRect.midright = (x, y)
    screen.blit(text_image, textRect)

#Gameboard objects

class ActiveGameboard:
    #rstate is rotation state
    def __init__(self, x_pos, y_pos, piecenumber, rstate, scale):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.piecenumber = piecenumber
        self.rstate = rstate
        self.scale = scale
        self.leftbound, self.rightbound = left_right_bound(self.piecenumber, self.rstate)
        self.color = piece_color(self.piecenumber)
        self.gameboard = [[0 for _ in range(10)] for __ in range(20)]

    def gameboard_update(self):
        self.gameboard = [[0 for _ in range(10)] for __ in range(20)]
        structure_list = piece_structure(self.piecenumber, self.rstate)
        
        self.gameboard[self.y_pos][self.x_pos] = self.piecenumber
        for minilist in structure_list:
            if self.y_pos+minilist[1] >= 0 and self.x_pos+minilist[0] >= 0 and self.x_pos+minilist[0] <= 9:
                self.gameboard[self.y_pos+minilist[1]][self.x_pos+minilist[0]] = self.piecenumber
        
    
    def draw(self):
        for j in range(len(self.gameboard)):
            for i in range(len(self.gameboard[0])):
                if self.gameboard[j][i] > 0:
                    pygame.draw.rect(screen, self.color, pygame.Rect(i*self.scale+1, j*self.scale+1, self.scale-1, self.scale-1))

  
class GhostGameboard:
    def __init__(self, x_pos, y_pos, piecenumber, rstate, scale):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.piecenumber = piecenumber
        self.rstate = rstate
        self.scale = scale
        self.color = piece_color(self.piecenumber)
        self.gameboard = [[0 for _ in range(10)] for __ in range(20)]

    def gameboard_update(self):
        self.gameboard = [[0 for _ in range(10)] for __ in range(20)]
        structure_list = piece_structure(self.piecenumber, self.rstate)
        
        self.gameboard[self.y_pos][self.x_pos] = self.piecenumber
        for minilist in structure_list:
            if self.y_pos+minilist[1] >= 0 and self.x_pos+minilist[0] >= 0 and self.x_pos+minilist[0] <= 9:
                self.gameboard[self.y_pos+minilist[1]][self.x_pos+minilist[0]] = self.piecenumber

    def draw(self):
        for j in range(len(self.gameboard)):
            for i in range(len(self.gameboard[0])):
                if self.gameboard[j][i] > 0:
                    pygame.draw.rect(screen, self.color, pygame.Rect(i*self.scale+1, j*self.scale+1, self.scale-1, self.scale-1), 2)


class PassiveGameboard:
    def __init__(self, scale):
        self.scale = scale
        self.gameboard = [[0 for _ in range(10)] for __ in range(20)]
        self.gameboard.append([8 for _ in range(10)])

    def gameboard_update(self, ghost_gameboard):
        for index1 in range(len(self.gameboard)-1):
            for index2 in range(len(self.gameboard[0])):
                if ghost_gameboard[index1][index2] > 0:
                    self.gameboard[index1][index2] = ghost_gameboard[index1][index2]

    def draw(self):
        for j in range(len(self.gameboard)-1):
            for i in range(len(self.gameboard[0])):
                if self.gameboard[j][i] > 0:
                    pygame.draw.rect(screen, piece_color(self.gameboard[j][i]), pygame.Rect(i*self.scale+1, j*self.scale+1, self.scale-1, self.scale-1))


class UpNextBoard:
    def __init__(self, scale):
        self.scale = scale
        self.gameboard = [[0 for _ in range(4)] for __ in range(11)]
        self.piece_number_list = [random.randint(1, 7) for _ in range(4)]

    def gameboard_update(self):
        self.gameboard = [[0 for _ in range(4)] for __ in range(11)]
        y_pos = 1
        for i in range(4):
            piecenumber = self.piece_number_list[i]
            structure_list = piece_structure(piecenumber, 0)

            self.gameboard[y_pos][1] = piecenumber
            for minilist in structure_list:
                self.gameboard[y_pos+minilist[1]][1+minilist[0]] = piecenumber

            y_pos += 3

    def draw(self):
        for j in range(len(self.gameboard)):
            for i in range(len(self.gameboard[0])):
                if self.gameboard[j][i] > 0:
                    pygame.draw.rect(screen, piece_color(self.gameboard[j][i]), pygame.Rect((i+13)*self.scale+1, (j+5)*self.scale+1, self.scale-1, self.scale-1))


class OnHoldBoard:
    def __init__(self, scale):
        self.scale = scale
        self.gameboard = [[0 for _ in range(4)] for __ in range(2)]
        self.hold_piece = 0

    def gameboard_update(self):
        self.gameboard = [[0 for _ in range(4)] for __ in range(2)]
        structure_list = piece_structure(self.hold_piece, 0)
        
        self.gameboard[1][1] = self.hold_piece
        for minilist in structure_list:
            self.gameboard[1+minilist[1]][1+minilist[0]] = self.hold_piece

    def draw(self):
        for j in range(len(self.gameboard)):
            for i in range(len(self.gameboard[0])):
                if self.gameboard[j][i] > 0:
                    pygame.draw.rect(screen, piece_color(self.gameboard[j][i]), pygame.Rect((i+13)*self.scale+1, (j+17.5)*self.scale+1, self.scale-1, self.scale-1))


class HypoGameboard:
    def __init__(self):
        self.gameboard = [[0 for _ in range(10)] for __ in range(20)]

    def gameboard_update(self, piecenumber, rstate, x_pos, y_pos):
        self.gameboard = [[0 for _ in range(10)] for __ in range(20)]
        structure_list = piece_structure(piecenumber, rstate)
        
        self.gameboard[y_pos][x_pos] = piecenumber
        for minilist in structure_list:
            self.gameboard[y_pos+minilist[1]][x_pos+minilist[0]] = piecenumber



#Menu loop variables

#[0] is read, [1] is write
menu_choices = ['yellow', 'white']
next_menu = False
read_game = False
write_game = False
game_quit = False

#Initial menu loop
initial_menu = True
while initial_menu:
    timer.tick(pseudofps)
    screen.fill('black')

    
    draw_text_gameover("Read", font3, menu_choices[0], int(width/2), int(height/3))
    draw_text_gameover("Write", font3, menu_choices[1], int(width/2), int(2*height/3))


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_quit = True
            initial_menu = False
            
        if event.type == pygame.KEYDOWN:
            
            if event.key == pygame.K_UP:
                for i in range(2):
                    if menu_choices[i] == 'yellow':
                        menu_choices[i] = 'white'
                        menu_choices[(i-1)%2] = 'yellow'
                        pygame.mixer.Channel(5).set_volume(0.3)
                        pygame.mixer.Channel(5).play(pygame.mixer.Sound(r'SFX\Move.mp3'))
                        break

            if event.key == pygame.K_DOWN:
                for i in range(2):
                    if menu_choices[i] == 'yellow':
                        menu_choices[i] = 'white'
                        menu_choices[(i+1)%2] = 'yellow'
                        pygame.mixer.Channel(5).set_volume(0.3)
                        pygame.mixer.Channel(5).play(pygame.mixer.Sound(r'SFX\Move.mp3'))
                        break

            if event.key == pygame.K_SPACE:
                pygame.mixer.Channel(2).play(pygame.mixer.Sound(r'SFX\HardDrop.mp3'))
                initial_menu = False
                next_menu = True

    pygame.display.flip()

if not game_quit:
    if menu_choices[0] == 'yellow':
        read_game = True
    elif menu_choices[1] == 'yellow':
        write_game = True


if next_menu:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    rows = cursor.fetchall()
    file_names = [row[0] for row in rows]
    for i in range(len(file_names)-1, -1, -1):
        if 'FrameData' in file_names[i]:
            file_names.pop(i)
    file_names.sort(reverse = True)
    while len(file_names) < 5:
        file_names.append("Unavailable")


    menu2_choices = ['yellow', 'white', 'white', 'white', 'white']


while next_menu and read_game:
    timer.tick(pseudofps)
    screen.fill('black')

    for i in range(5):
        if file_names[i] != "Unavailable":
            draw_text_gameover(file_names[i][8:], font4, menu2_choices[i], int(width/2), int((i+1)*height/6))
        else:
            draw_text_gameover(file_names[i], font4, menu2_choices[i], int(width/2), int((i+1)*height/6))
        

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            next_menu = False
            read_game = False
            write_game = False
            
        if event.type == pygame.KEYDOWN:
            
            if event.key == pygame.K_UP:
                for i in range(5):
                    if menu2_choices[i] == 'yellow':
                        menu2_choices[i] = 'white'
                        menu2_choices[(i-1)%5] = 'yellow'
                        pygame.mixer.Channel(5).set_volume(0.3)
                        pygame.mixer.Channel(5).play(pygame.mixer.Sound(r'SFX\Move.mp3'))
                        break

            if event.key == pygame.K_DOWN:
                for i in range(5):
                    if menu2_choices[i] == 'yellow':
                        menu2_choices[i] = 'white'
                        menu2_choices[(i+1)%5] = 'yellow'
                        pygame.mixer.Channel(5).set_volume(0.3)
                        pygame.mixer.Channel(5).play(pygame.mixer.Sound(r'SFX\Move.mp3'))
                        break

            if event.key == pygame.K_SPACE:
                for i in range(5):
                    if menu2_choices[i] == 'yellow' and file_names[i] == 'Unavailable':
                        pygame.mixer.Channel(4).set_volume(0.3)
                        pygame.mixer.Channel(4).play(pygame.mixer.Sound(r'SFX\Unable.mp3'))
                    elif menu2_choices[i] == 'yellow' and file_names[i] != 'Unavailable':
                        pygame.mixer.Channel(2).play(pygame.mixer.Sound(r'SFX\HardDrop.mp3'))
                        file_selected = file_names[i]
                        next_menu = False

    pygame.display.flip()


if read_game:
    cursor.execute(f"SELECT Pieces FROM {file_selected}__FrameData;")
    read_pieces_list = cursor.fetchone()[0]
    read_pieces_list = read_pieces_list.strip('][').split(', ')
    for i in range(len(read_pieces_list)):
        read_pieces_list[i] = int(read_pieces_list[i])

    cursor.execute(f"SELECT KeyboardInput FROM {file_selected}__FrameData;")
    read_keyboard_input_list = cursor.fetchone()[0]
    read_keyboard_input_list = read_keyboard_input_list.strip('][').split(', ')


if write_game:
    cursor.execute(f"CREATE TABLE {dt_string}(SrNo, ActionPerformed, PieceNumber, PassiveGameboard)")
    cursor.execute(f"CREATE TABLE {dt_string2}(KeyboardInput, Pieces)")


#Main loop variables
                    
newblock = True
gravitycooldown = 0
move_ticker = 0
passive_gameboard = PassiveGameboard(scale)
upnext_board = UpNextBoard(scale)
onhold_board = OnHoldBoard(scale)
combo = 0
combo_continued = False
score = 0
lines_cleared = 0
check_move = False
space_pressed = False
held_this_turn = False
left_pressed = False
right_pressed = False
shift_pressed = False
left_right_on_cooldown = 0
game_over = False
highest_combo = 0
score_milestone = 0
gravity_speed = int(57/(1 + (0.037*score_milestone)**2) + 3)
score_milestone += 1

first_time = True

keyboard_input_list = []
pieces_list = []

string_this_frame = ''
read_current_keyboard_input = 'N'

if read_game:
    upnext_board.piece_number_list = read_pieces_list

#Database variables

SrNo = 1
ActionPerformed = "NoAction"
append_this_frame = False



#Main game loop
read_index = 0

while (write_game or read_game) and not game_over:

    timer.tick(pseudofps)
    screen.fill('black')

    lines_cleared = 0
    
    if read_game:
        read_current_keyboard_input = read_keyboard_input_list[read_index]

    Move_SFX = False
    HardDrop_SFX = False
    Combo_SFX = False
    Unable_SFX = False
    GameOver_SFX = False
    Hold_SFX = False
    

    if newblock:
        piecenumber = upnext_board.piece_number_list[0]
        upnext_board.piece_number_list.pop(0)
        active_gameboard = ActiveGameboard(4, 0, piecenumber, 0, scale)
        ghost_gameboard = GhostGameboard(4, 19, piecenumber, 0, scale)

        if len(upnext_board.piece_number_list) < 5:
            upnext_board.piece_number_list.append(random.randint(1, 7))
        
        pieces_list.append(active_gameboard.piecenumber)
        
        newblock = False


    upnext_board.gameboard_update()
    upnext_board.draw()

    onhold_board.gameboard_update()
    onhold_board.draw()

    passive_gameboard.draw()

    ghost_gameboard.x_pos = active_gameboard.x_pos
    ghost_gameboard.gameboard_update()

    active_gameboard.gameboard_update()
    active_gameboard.draw()


    if first_time and write_game:
        data_to_append = [(SrNo, ActionPerformed, active_gameboard.piecenumber, str(passive_gameboard.gameboard[0:20]))]
        insert_string = "INSERT INTO " + dt_string + " VALUES(?, ?, ?, ?)"
        cursor.executemany(insert_string, data_to_append)
        con.commit()
        first_time = False
    

    for i in range(active_gameboard.y_pos, len(active_gameboard.gameboard)+1):
        overlap = False
        test_gameboard = [[0 for _ in range(10)] for __ in range(21)]
        structure_list = piece_structure(active_gameboard.piecenumber, active_gameboard.rstate)
        test_gameboard[i][active_gameboard.x_pos] = active_gameboard.piecenumber
        for minilist in structure_list:
            if i+minilist[1] >= 0 and active_gameboard.x_pos+minilist[0] >= 0 and active_gameboard.x_pos+minilist[0] <= 9:
                test_gameboard[i+minilist[1]][active_gameboard.x_pos+minilist[0]] = active_gameboard.piecenumber

        for j in range(len(active_gameboard.gameboard)+1):
            for k in range(len(active_gameboard.gameboard[0])):
                if test_gameboard[j][k] > 0:
                    if passive_gameboard.gameboard[j][k] > 0:
                        overlap = True
        if overlap:
            ghost_gameboard.y_pos = i-1
            break


    ghost_gameboard.gameboard_update()
    ghost_gameboard.draw()


    
    if gravitycooldown == 0:
        if active_gameboard.gameboard != ghost_gameboard.gameboard:
            gravitycooldown += gravity_speed
            active_gameboard.y_pos += 1
        else:
            check_move = True
            gravitycooldown += gravity_speed
        
    elif gravitycooldown > 0:
        gravitycooldown -= 1

    if move_ticker > 0:
        move_ticker -= 1

    

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cursor.execute(f"DROP TABLE IF EXISTS {dt_string}")
            cursor.execute(f"DROP TABLE IF EXISTS {dt_string2}")
            write_game = False
            read_game = False

        if event.type == pygame.KEYDOWN and write_game:
            left_bound, right_bound = left_right_bound(active_gameboard.piecenumber, active_gameboard.rstate)
            
            if event.key == pygame.K_LEFT:
                string_this_frame = string_this_frame + '-Ld'
                left_pressed = True

                
            if event.key == pygame.K_RIGHT:
                string_this_frame = string_this_frame + '-Rd'
                right_pressed = True


            if event.key == pygame.K_UP:
                string_this_frame = string_this_frame + '-C'

                rotation_allowed = not rotation_check(active_gameboard, ghost_gameboard, passive_gameboard, 1)
                if rotation_allowed:
                    active_gameboard.rstate = (active_gameboard.rstate+1)%4
                    ghost_gameboard.rstate = (ghost_gameboard.rstate+1)%4
                    Move_SFX = True
                elif not rotation_allowed:
                    Unable_SFX = True

                ghost_gameboard.y_pos = active_gameboard.y_pos
                    

            if event.key == pygame.K_f:
                string_this_frame = string_this_frame + '-c'

                rotation_allowed = not rotation_check(active_gameboard, ghost_gameboard, passive_gameboard, -1)
                if rotation_allowed:
                    active_gameboard.rstate = (active_gameboard.rstate-1)%4
                    ghost_gameboard.rstate = (ghost_gameboard.rstate-1)%4
                    Move_SFX = True
                elif not rotation_allowed:
                    Unable_SFX = True

                ghost_gameboard.y_pos = active_gameboard.y_pos

            if event.key == pygame.K_SPACE:
                string_this_frame = string_this_frame + '-D'
                
                active_gameboard.y_pos = ghost_gameboard.y_pos
                active_gameboard.gameboard_update()
                space_pressed = True

            if event.key == pygame.K_LSHIFT:
                string_this_frame = string_this_frame + '-dd'
                
                shift_pressed = True

            if event.key == pygame.K_w and not held_this_turn:
                string_this_frame = string_this_frame + '-H'
                
                if onhold_board.hold_piece == 0:
                    onhold_board.hold_piece = active_gameboard.piecenumber
                    newblock = True
                else:
                    active_gameboard = ActiveGameboard(4, 1, onhold_board.hold_piece, 0, scale)
                    onhold_board.hold_piece = ghost_gameboard.piecenumber
                    ghost_gameboard = GhostGameboard(4, 19, active_gameboard.piecenumber, 0, scale)
                    active_gameboard.gameboard_update()
                    ghost_gameboard.gameboard_update()
                held_this_turn = True
                Hold_SFX = True
                append_this_frame = True
                ActionPerformed = "Hold"

        if event.type == pygame.KEYUP and write_game:

            if event.key == pygame.K_LEFT:
                string_this_frame = string_this_frame + '-Lu'
                
                left_pressed = False
                left_right_on_cooldown = 0

            if event.key == pygame.K_RIGHT:
                string_this_frame = string_this_frame + '-Ru'
                
                right_pressed = False
                left_right_on_cooldown = 0

            if event.key == pygame.K_LSHIFT:
                string_this_frame = string_this_frame + '-du'
                
                shift_pressed = False
                if gravitycooldown == 0:
                    gravitycooldown += gravity_speed


    if read_game:
        if 'Ld' in read_current_keyboard_input:
            left_pressed = True
            
        if 'Rd' in read_current_keyboard_input:
            right_pressed = True
            
        if 'C' in read_current_keyboard_input:
            rotation_allowed = not rotation_check(active_gameboard, ghost_gameboard, passive_gameboard, 1)
            if rotation_allowed:
                active_gameboard.rstate = (active_gameboard.rstate+1)%4
                ghost_gameboard.rstate = (ghost_gameboard.rstate+1)%4
                Move_SFX = True
            elif not rotation_allowed:
                Unable_SFX = True
            ghost_gameboard.y_pos = active_gameboard.y_pos

        if 'c' in read_current_keyboard_input:
            rotation_allowed = not rotation_check(active_gameboard, ghost_gameboard, passive_gameboard, -1)
            if rotation_allowed:
                active_gameboard.rstate = (active_gameboard.rstate-1)%4
                ghost_gameboard.rstate = (ghost_gameboard.rstate-1)%4
                Move_SFX = True
            elif not rotation_allowed:
                Unable_SFX = True
            ghost_gameboard.y_pos = active_gameboard.y_pos

        if 'D' in read_current_keyboard_input:         
            active_gameboard.y_pos = ghost_gameboard.y_pos
            active_gameboard.gameboard_update()
            space_pressed = True

        if 'dd' in read_current_keyboard_input:
            shift_pressed = True

        if 'H' in read_current_keyboard_input and not held_this_turn:
            if onhold_board.hold_piece == 0:
                onhold_board.hold_piece = active_gameboard.piecenumber
                newblock = True
            else:
                active_gameboard = ActiveGameboard(4, 1, onhold_board.hold_piece, 0, scale)
                onhold_board.hold_piece = ghost_gameboard.piecenumber
                ghost_gameboard = GhostGameboard(4, 19, active_gameboard.piecenumber, 0, scale)
                active_gameboard.gameboard_update()
                ghost_gameboard.gameboard_update()
            held_this_turn = True
            Hold_SFX = True
            append_this_frame = True
            ActionPerformed = "Hold"
            current_keyboard_input = "H"

        if 'Lu' in read_current_keyboard_input:
            left_pressed = False
            left_right_on_cooldown = 0

        if 'Ru' in read_current_keyboard_input:
            right_pressed = False
            left_right_on_cooldown = 0

        if 'du' in read_current_keyboard_input:
            shift_pressed = False
            if gravitycooldown == 0:
                gravitycooldown += gravity_speed


    left_bound, right_bound = left_right_bound(active_gameboard.piecenumber, active_gameboard.rstate)

    if left_pressed and active_gameboard.x_pos > left_bound and move_ticker == 0:
        overlap = False
        if passive_gameboard.gameboard[active_gameboard.y_pos][active_gameboard.x_pos-1] > 0:
            overlap = True
        else:
            structure_list = piece_structure(active_gameboard.piecenumber, active_gameboard.rstate)
            for minilist in structure_list:
                if active_gameboard.y_pos+minilist[1] >= 0 and active_gameboard.x_pos-1+minilist[0] >= 0 and active_gameboard.x_pos-1+minilist[0] <= 9:
                    if passive_gameboard.gameboard[active_gameboard.y_pos+minilist[1]][active_gameboard.x_pos-1+minilist[0]] > 0:
                        overlap = True
        if not overlap and left_right_on_cooldown not in [1, 2, 3]:
            active_gameboard.x_pos -= 1
            Move_SFX = True
        move_ticker += 3
        left_right_on_cooldown += 1

    if right_pressed and active_gameboard.x_pos < 9 - right_bound and move_ticker == 0:
        overlap = False
        if passive_gameboard.gameboard[active_gameboard.y_pos][active_gameboard.x_pos+1] > 0:
            overlap = True
        else:
            structure_list = piece_structure(active_gameboard.piecenumber, active_gameboard.rstate)
            for minilist in structure_list:
                if active_gameboard.y_pos+minilist[1] >= 0 and active_gameboard.x_pos+1+minilist[0] >= 0 and active_gameboard.x_pos+1+minilist[0] <= 9:
                    if passive_gameboard.gameboard[active_gameboard.y_pos+minilist[1]][active_gameboard.x_pos+1+minilist[0]] > 0:
                        overlap = True
        if not overlap and left_right_on_cooldown not in [1, 2, 3]:
            active_gameboard.x_pos += 1
            Move_SFX = True
        move_ticker += 3
        left_right_on_cooldown += 1

        
    if shift_pressed and move_ticker == 0:
        overlap = False
        if passive_gameboard.gameboard[active_gameboard.y_pos+1][active_gameboard.x_pos] > 0:
            overlap = True
        else:
            structure_list = piece_structure(active_gameboard.piecenumber, active_gameboard.rstate)
            for minilist in structure_list:
                if active_gameboard.y_pos+1+minilist[1] >= 0 and active_gameboard.x_pos+minilist[0] >= 0 and active_gameboard.x_pos+minilist[0] <= 9:
                    if passive_gameboard.gameboard[active_gameboard.y_pos+1+minilist[1]][active_gameboard.x_pos+minilist[0]] > 0:
                        overlap = True
        if not overlap:
            move_ticker += 2
            active_gameboard.y_pos += 1
            Move_SFX = True


    if active_gameboard.gameboard == ghost_gameboard.gameboard and (check_move or space_pressed):
        passive_gameboard.gameboard_update(ghost_gameboard.gameboard)
        newblock = True
        append_this_frame = True
        ActionPerformed = "Drop"
        
        for i in range(len(passive_gameboard.gameboard)-1):
            filled = 0
            for j in range(len(passive_gameboard.gameboard[0])):
                if passive_gameboard.gameboard[i][j] > 0:
                    filled += 1
            if filled == len(passive_gameboard.gameboard[0]):
                lines_cleared += 1
                for k in range(i, 0, -1):
                    passive_gameboard.gameboard[k] = passive_gameboard.gameboard[k-1]
                passive_gameboard.gameboard[0] = [0 for _ in range(10)]
                combo_continued = True
                
        check_move = False
        space_pressed = False
        held_this_turn = False

        for top_row_number in passive_gameboard.gameboard[0]:
            if top_row_number > 0:
                game_over = True

        if newblock:
            HardDrop_SFX = True
        


        if combo_continued:
            combo += 1
            Combo_SFX = True
            if combo > highest_combo:
                highest_combo = combo
        else:
            combo = 0

        if lines_cleared == 1:
            score += 100
        elif lines_cleared == 2:
            score += 300
        elif lines_cleared == 3:
            score += 500
        elif lines_cleared == 4:
            score += 800
        score += 50*combo

        
        combo_continued = False


    if append_this_frame and write_game:
        SrNo += 1
        data_to_append = [(SrNo, ActionPerformed, active_gameboard.piecenumber, str(passive_gameboard.gameboard[0:20]))]
        insert_string = "INSERT INTO " + dt_string + " VALUES(?, ?, ?, ?)"
        cursor.executemany(insert_string, data_to_append)
        con.commit()
        append_this_frame = False

    if score >= 1000*score_milestone:
        score_milestone += 1
        gravity_speed = int(57/(1 + (0.037*score_milestone)**2) + 3)

    if write_game:
        keyboard_input_list.append(string_this_frame)
        string_this_frame = ''


    if Combo_SFX:
        if combo < 5:
            combo_file = combo
        elif combo >= 5:
            combo_file = 5

        pygame.mixer.Channel(0).set_volume(0.4)
        pygame.mixer.Channel(0).play(pygame.mixer.Sound('SFX\Combo'+str(combo_file)+'.mp3'))
        pygame.mixer.Channel(1).play(pygame.mixer.Sound('SFX\Lines'+str(lines_cleared)+'.mp3'))

    elif Hold_SFX:
        pygame.mixer.Channel(3).play(pygame.mixer.Sound(r'SFX\Hold.mp3'))

    elif HardDrop_SFX:
        pygame.mixer.Channel(2).play(pygame.mixer.Sound(r'SFX\HardDrop.mp3'))

    #elif Unable_SFX: #and not pygame.mixer.Channel(4).get_busy:
        #pygame.mixer.Channel(4).set_volume(0.2)
        #pygame.mixer.Channel(4).play(pygame.mixer.Sound(r'SFX\Unable.mp3'))

    #elif Move_SFX: #and not pygame.mixer.Channel(5).get_busy:
        #pygame.mixer.Channel(5).set_volume(0.2)
        #pygame.mixer.Channel(5).play(pygame.mixer.Sound(r'SFX\Move.mp3'))



    score_string = "Score: " + str(score)
    combo_string = "Combo: x" + str(combo)

    draw_text(score_string, font2, 'white', int(10.5*scale), int(1*scale+1))
    draw_text(combo_string, font2, 'white', int(10.5*scale), int(2.5*scale+1))

    draw_text("Up next:", font1, 'white', int(10.5*scale), int(4*scale+1))
    if onhold_board.hold_piece > 0:
        draw_text("On hold:", font1, 'white', int(10.5*scale), int(16.75*scale+1))

    if debugging:
        for j in range(len(passive_gameboard.gameboard)-1):
            for i in range(len(passive_gameboard.gameboard[0])):
                draw_text_gameover(str(passive_gameboard.gameboard[j][i]), font1, 'white', int((i+0.5)*scale), int((j+0.5)*scale))

    pygame.display.flip()


    if active_gameboard.y_pos == 19 and ghost_gameboard.y_pos < 19:
        newblock = True

    if read_game:
        read_index += 1


if game_over:
    passive_gameboard.gameboard_update(ghost_gameboard.gameboard)
    passive_gameboard.draw()
    
    '''
    for j in range(len(passive_gameboard.gameboard)-1):
            for i in range(len(passive_gameboard.gameboard[0])):
                if passive_gameboard.gameboard[j][i] > 0:
                    pygame.draw.rect(screen, 'grey52', pygame.Rect(i*scale+1, j*scale+1, scale-1, scale-1))
    '''

    if write_game:
        cursor.execute("SELECT * FROM " + dt_string)
        rows = cursor.fetchall()

        column_names = [description[0] for description in cursor.description]
        mydataframe = pandas.DataFrame(rows, columns = column_names)

        mydataframe.to_csv(f"GamesCSV\{dt_string}", index = False)
        print("Dataframe exported!")

        data_to_append = [(str(keyboard_input_list), str(pieces_list))]
        insert_string = "INSERT INTO " + dt_string2 + " VALUES(?, ?)"
        cursor.executemany(insert_string, data_to_append)
        con.commit()

        cursor.execute("SELECT * FROM " + dt_string2)
        rows = cursor.fetchall()

        column_names = [description[0] for description in cursor.description]
        mydataframe2 = pandas.DataFrame(rows, columns = column_names)

        mydataframe2.to_csv(f"GamesCSV\{dt_string2}", index = False)
        print("Dataframe2 exported!")

    
    GameOver_SFX = True
    game_over_screen_fade = pygame.Surface((width, height))
    game_over_screen_fade.fill((0, 0, 0))
    game_over_screen_fade.set_alpha(200)
    screen.blit(game_over_screen_fade, (0, 0))
    
    draw_text_gameover("GAME OVER!", font3, 'white', int(width/2), int(8*scale))
    draw_text_midright("Score: ", font4, 'white', int(11*scale), int(11*scale))
    draw_text_midright("Max combo: ", font4, 'white', int(11*scale), int(12.5*scale))
    draw_text(str(score), font4, 'white', int(11*scale), int(11*scale))
    draw_text("x"+str(highest_combo), font4, 'white', int(11*scale), int(12.5*scale))

    pygame.mixer.Channel(6).play(pygame.mixer.Sound(r'SFX\GameOver.mp3'))

    pygame.display.flip()

while game_over:
    timer.tick(pseudofps)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = False

    pygame.display.flip()

pygame.quit()
