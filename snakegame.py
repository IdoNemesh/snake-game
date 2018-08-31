# imports
import socket
import pickle
import os
import pygame as pg
import snake as snk
import food as fd
import tkMessageBox
from colors import *
from Tkinter import *
from tkFont import *
from PIL import Image, ImageTk
from Crypto.Cipher import AES

game = False
flag = True
login = "login.png"
signup = "signup.png"
icon = "snakeicon.ico"
ip = '127.0.0.1'
port = 8820
width = 1080
height = 720
bgcolor = "#01579B"
txtcolor = "#B0BEC5"

# ================================================================================================#
#                                       Function Definitions                                      #
# ================================================================================================#


def connect():
    # Connect to the server
    my_socket = socket.socket()
    my_socket.connect((ip, port))
    print "Client is connected"
    return my_socket


def do_encrypt(message):
    message = message.ljust(len(message) * 16)
    obj = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = obj.encrypt(message)
    return ciphertext


def do_decrypt(ciphertext):
    obj2 = AES.new(key, AES.MODE_CBC, iv)
    message = obj2.decrypt(ciphertext)
    message = message.rstrip()
    return message


def log_in():
    # Login to the server
    global game
    my_socket.send(do_encrypt(pickle.dumps("Login")))
    my_socket.send(do_encrypt(pickle.dumps((E1.get(), E2.get()))))  # Send username and password to the server for authentication
    game = pickle.loads(do_decrypt(my_socket.recv(50000)))  # True if username and password match the database
    if game == "True":
        root.destroy()
    else:
        L3 = Label(root, bg=bgcolor, fg="black")  # Label if entered wrong username or password
        L3.config(text="Wrong username or password                                                        ")
        L3.place(x=700, y=290)


def sign_up():
    # Sign up to the server
    global game
    my_socket.send(do_encrypt(pickle.dumps("Signup")))
    my_socket.send(do_encrypt(pickle.dumps((E1.get(), E2.get()))))  # Send username and password to the server for authentication
    game = pickle.loads(do_decrypt(my_socket.recv(50000)))  # False if username already taken or password doesn't meet requirements
    if game == "True":
        root.destroy()
    else:
        L3 = Label(root, bg=bgcolor, fg="black")
        L3.config(text="Username already taken or password didn't meet requirements")
        L3.place(x=700, y=290)


def ask_delete():
    # If user clicked the exit button, ask for another confirmation
    t = "Confirm Exit"
    m = "Close window?"
    answer = tkMessageBox.askyesno(title=t, message=m)
    if answer:  # True if user clicked yes
        my_socket.send(pickle.dumps("Bye bye"))
        root.destroy()


def inLimits(snake):
    # Check if the snake's head is outside the limits
    headpos = snake.getHeadPos()
    return not (headpos[0] < 1 or headpos[1] < 1 or headpos[0] >= HEIGHT + 1 or headpos[1] >= WIDTH + 1)


def drawWalls(surface):
    # Draw walls
    # Left and right walls
    for y in range(HEIGHT + 1):
        surface.blit(wallblock, (0, y * snk.BLOCK_SIZE))
        surface.blit(wallblockdark, (5, y * snk.BLOCK_SIZE + 5))
        surface.blit(wallblock, ((WIDTH + 1) * snk.BLOCK_SIZE, y * snk.BLOCK_SIZE))
        surface.blit(wallblockdark, ((WIDTH + 1) * snk.BLOCK_SIZE + 5, y * snk.BLOCK_SIZE + 5))

    # Upper and bottom walls
    for x in range(WIDTH + 2):
        surface.blit(wallblock, (x * snk.BLOCK_SIZE, 0))
        surface.blit(wallblockdark, (x * snk.BLOCK_SIZE + 5, 5))
        surface.blit(wallblock, (x * snk.BLOCK_SIZE, (HEIGHT + 1) * snk.BLOCK_SIZE,))
        surface.blit(wallblockdark, (x * snk.BLOCK_SIZE + 5, (HEIGHT + 1) * snk.BLOCK_SIZE + 5))


def leaderboard():
    leaderboard = pickle.loads(do_decrypt(my_socket.recv(50000)))
    master = Tk()
    x = master.winfo_screenwidth() / 2 - width / 2
    y = master.winfo_screenheight() / 2 - height / 2
    master.wm_title("Leaderboard")
    master.geometry("+{}+{}".format(x, y))
    master.focus_force()
    w2 = Frame(master)
    w2.pack_propagate(True)
    scrollbar = Scrollbar(w2)
    scrollbar.pack(side=RIGHT, fill=Y)
    helv16 = Font(family="Helvetica", size=16)
    mylist = Text(w2, width=30, bg="#40c4ff", font=helv16, yscrollcommand=scrollbar.set, height=10)
    for key in sorted(leaderboard, reverse=True, key=lambda k: int(leaderboard[k][0])):
        a = str(leaderboard[key]).replace("(", "").replace(")", "").replace("'", "").replace('"', "").replace(",", "")
        mylist.insert(END, str(key) + " " + a + "\n")
    mylist.config(state=DISABLED)
    scrollbar.config(command=mylist.yview)
    w2.pack(expand=True, fill=BOTH)
    mylist.pack(side=LEFT, fill=BOTH, expand=True)
    master.iconbitmap(icon)
    master.mainloop()


my_socket = connect()
key, iv = pickle.loads(my_socket.recv(50000))
root = Tk()
root.wm_title("Snake Homepage")
x = root.winfo_screenwidth() / 2 - width / 2
y = root.winfo_screenheight() / 2 - height / 2
root.geometry("+{}+{}".format(x, y))
w = Frame(root, width=width, height=height, bg=bgcolor)
L1 = Label(root, text="User Name", bg=bgcolor, fg=txtcolor)  # Username label
L1.place(x=425, y=290)
E1 = Entry(root, bd=2)  # Input box to enter username
E1.place(x=500, y=290)
E1.focus_set()  # Set focus on the input box

L2 = Label(root, text="Password", bg=bgcolor, fg=txtcolor)  # Password label
L2.place(x=425, y=340)
E2 = Entry(root, bd=2, show='*')  # Input box to enter password
E2.place(x=500, y=340)

photo1 = ImageTk.PhotoImage(Image.open(login))  # Login button image
photo2 = ImageTk.PhotoImage(Image.open(signup))  # Signup button image

helv28 = Font(family="Helvetica", size=28, weight="bold")  # Font
# Welcome text
welcome = Text(root, bg=bgcolor, font=helv28, bd=0, width=40, height=3)
wts = "Welcome to Snake"
rankup = "and rank up in the leaderboard"
welcome.insert(END, wts.rjust(34) + "\nFirst, login or sign up to save your scores\n" + rankup.rjust(39))
welcome.config(state=DISABLED)
welcome.place(x=200, y=100)

root.bind('<Return>', lambda e: log_in())  # When user hits the enter key, same as clicking the login button
b1 = Button(root, bd=0, bg=bgcolor, activebackground=bgcolor, image=photo1, command=log_in)  # Login button
b1.place(x=500, y=390)
b2 = Button(root, bd=0, bg=bgcolor, activebackground=bgcolor, image=photo2, command=sign_up)  # Signup button
b2.place(x=500, y=440)

req = pickle.loads(do_decrypt(my_socket.recv(50000)))  # Receive the current password requirements from the server
helv12 = Font(family="Helvetica", size=12, weight="bold")  # Font
pass_req = Text(w, fg="black", bg=bgcolor, bd=0, width=50, font=helv12, height=5)  # Display the password requirements
pass_req.insert(END, str(req))
pass_req.config(state=DISABLED)
pass_req.place(x=370, y=500)
w.pack()

root.iconbitmap(icon)  # Set window icon
root.wm_protocol("WM_DELETE_WINDOW", ask_delete)  # When clicking the exit button, ask the user if he's sure
root.mainloop()

if game == "True":  # If login or signup succeeded
    play = True
    while play:
        # screen size and game speed
        WIDTH = 25
        HEIGHT = 25
        SPEED = 8
        SPEED_TICK = 2
        SPEED_INC = 5
        SHORT = 12
        LONG = 1

        # defining the outer wall blocks
        wallblock = pg.Surface((snk.BLOCK_SIZE, snk.BLOCK_SIZE))
        wallblock.set_alpha(255)  # set the pixels to be opaque
        wallblock.fill(BLUE)  # fill the outer wall block to blue defined in colors
        wallblockdark = pg.Surface((snk.BLOCK_SIZE_INNER, snk.BLOCK_SIZE_INNER))
        wallblockdark.set_alpha(255)
        wallblockdark.fill(BLUE_DARK)  # fill the inner wall block to dark blue defined in colors

        # ================================================================================================#
        #                                       Main Game Part                                           #
        # ================================================================================================#

        # initialize pygame, clock for game speed and screen to draw
        pg.init()
        # will increase game speed every 5 times we eat
        eaten = 0
        # initializing mixer, sounds, clock and screen
        pg.display.set_icon(pg.image.load(icon))
        pg.mixer.init()
        eatsound = pg.mixer.Sound("snakeeat.wav")
        crashsound = pg.mixer.Sound("snakecrash.wav")
        clock = pg.time.Clock()
        os.environ['SDL_VIDEO_CENTERED'] = '1'  # center the pygame window
        screen = pg.display.set_mode(((WIDTH + 2) * snk.BLOCK_SIZE, (HEIGHT + 2) * snk.BLOCK_SIZE))  # set resolution
        pg.display.set_caption("Snake")
        font = pg.font.SysFont(pg.font.get_default_font(), 40)
        gameovertext = font.render("GAME OVER", 1, WHITE)
        pressesc = font.render("PRESS ESC TO EXIT", 1, WHITE)
        leaderboardtext = font.render("OR L TO VIEW LEADERBOARD", 1, WHITE)
        playagaintext = font.render("PRESS ANY KEY TO PLAY AGAIN", 1, WHITE)
        starttext = font.render("PRESS ANY KEY TO START", 1, WHITE)
        font2 = pg.font.SysFont(pg.font.get_default_font(), 28)
        scoretext = font2.render("SCORE: "+str(eaten), 1, WHITE)
        screen.fill(BLACK)

        # we need a snake and something to eat
        snake = snk.snake(screen, WIDTH / 2, HEIGHT / 2)  # middle of the screen
        food = fd.food(screen, 1, HEIGHT + 1, 1, WIDTH + 1)

        # food should not appear where the snake is
        while food.getPos() in snake.getPosList():
            food.__init__(screen, 1, HEIGHT + 1, 1, WIDTH + 1)

        pg.event.set_blocked(pg.MOUSEMOTION)
        pg.mouse.set_visible(False)
        pg.event.set_grab(True)  # all input goes to pygame window

        # press any key to start!!!
        drawWalls(screen)
        screen.blit(starttext, ((WIDTH - 10) * snk.BLOCK_SIZE / 2, HEIGHT * snk.BLOCK_SIZE / 2))
        pg.display.flip()
        waiting = True
        while waiting:
            event = pg.event.wait()
            if event.type == pg.KEYDOWN:
                waiting = False
        screen.fill(BLACK)

        # main loop
        running = True
        while running:
            # check crash or move outside the limits
            if not inLimits(snake) or snake.crashed:
                running = False
                crashsound.play()
            else:
                # draw screen with snake and foods
                food.draw()
                drawWalls(screen)
                screen.blit(scoretext, ((WIDTH - 20) * snk.BLOCK_SIZE / 2, (HEIGHT - 24.5) * snk.BLOCK_SIZE / 2))
                snake.draw()
                pg.display.flip()

                # check if snake eates
                if food.getPos() == snake.getHeadPos():
                    eaten += 1
                    scoretext = font2.render("SCORE: " + str(eaten), 1, WHITE)
                    screen.blit(scoretext, ((WIDTH - 20) * snk.BLOCK_SIZE / 2, (HEIGHT - 24.5) * snk.BLOCK_SIZE / 2))
                    eatsound.play()
                    snake.grow()
                    # food should not appear where the snake is
                    food.__init__(screen, 1, HEIGHT + 1, 1, WIDTH + 1)
                    while food.getPos() in snake.getPosList():
                        food.__init__(screen, 1, HEIGHT + 1, 1, WIDTH + 1)
                    # increase game speed
                    if eaten % SPEED_INC == 0:
                        SPEED += SPEED_TICK

                # game speed control
                clock.tick(SPEED)

                # get the next event on queue
                event = pg.event.poll()  # get a single event from the queue
                if event.type == pg.QUIT:
                    sys.exit()
                elif event.type == pg.KEYDOWN:
                    actmotdir = snake.getMotionDir()
                    if event.key == pg.K_ESCAPE:
                        my_socket.send(do_encrypt(pickle.dumps(("FIN", eaten))))  # send score and date
                        pg.quit()
                        flag = False
                        break
                    elif event.key == pg.K_UP and actmotdir != snk.DOWN:
                        snake.setMotionDir(snk.UP)
                    elif event.key == pg.K_DOWN and actmotdir != snk.UP:
                        snake.setMotionDir(snk.DOWN)
                    elif event.key == pg.K_RIGHT and actmotdir != snk.LEFT:
                        snake.setMotionDir(snk.RIGHT)
                    elif event.key == pg.K_LEFT and actmotdir != snk.RIGHT:
                        snake.setMotionDir(snk.LEFT)

                # remove the snake and make movement
                snake.remove()
                snake.move()

        if flag:
            # if crashed print "game over" and wait for esc key
            clock.tick(LONG)
            snake.draw()
            drawWalls(screen)
            scoretext = font2.render("SCORE: " + str(eaten), 1, WHITE)
            screen.blit(scoretext, ((WIDTH - 20) * snk.BLOCK_SIZE / 2, (HEIGHT - 24.5) * snk.BLOCK_SIZE / 2))
            snakeposlist = snake.getPosList()
            blackblock = snake.backblock
            for pos in snakeposlist[1:]:
                screen.blit(blackblock, (pos[1] * snk.BLOCK_SIZE, pos[0] * snk.BLOCK_SIZE))
                pg.display.flip()
                clock.tick(SHORT)

            screen.blit(gameovertext, ((WIDTH - 4) * snk.BLOCK_SIZE / 2, (HEIGHT - 4) * snk.BLOCK_SIZE / 2))  # game over
            screen.blit(playagaintext, ((WIDTH - 12.5) * snk.BLOCK_SIZE / 2, (HEIGHT - 1.5) * snk.BLOCK_SIZE / 2))  # play again
            screen.blit(leaderboardtext, ((WIDTH - 11.5) * snk.BLOCK_SIZE / 2, (HEIGHT + 0.6) * snk.BLOCK_SIZE / 2))
            screen.blit(pressesc, ((WIDTH - 7.5) * snk.BLOCK_SIZE / 2, (HEIGHT + 3) * snk.BLOCK_SIZE / 2))
            pg.display.flip()
            pg.event.clear()
            event = pg.event.wait()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    my_socket.send(do_encrypt(pickle.dumps(("FIN", eaten))))  # send score
                    pg.quit()
                    play = False
                elif event.key == pg.K_l:
                    my_socket.send(do_encrypt(pickle.dumps(("L", eaten))))  # send score
                    leaderboard()
                else:
                    my_socket.send(do_encrypt(pickle.dumps((None, eaten))))  # send score
        else:
            break

my_socket.close()
