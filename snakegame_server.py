# imports
import socket
import pickle
from passlib.hash import pbkdf2_sha256
import threading
import time
from Crypto.Cipher import AES
from Crypto import Random

users = {}
leaderboard = {}
usersfile = "users.txt"
leaderboardfile = "leaderboard.txt"
ip = '127.0.0.1'
port = 8820
iv = Random.new().read(AES.block_size)
key = Random.new().read(AES.block_size)

# ================================================================================================#
#                                       Function Definitions                                      #
# ================================================================================================#


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


def load_users():
    # Load the users and passwords from the file into the users dictionary
    with open(usersfile) as f:
        for line in f:
            if line:
                (username, password) = line.split()
                users[username] = password


def load_leaderboard():
    # Load the users, scores and dates from the file into the leaderboard dictionary
    with open(leaderboardfile) as f:
        for line in f:
            if line:
                (username, score, date) = line.split()
                leaderboard[username] = (score, date)


def log_in(client_socket):
    # Authenticate the username and password
    (username, password) = pickle.loads(do_decrypt(client_socket.recv(50000)))
    if username in users.keys() and pbkdf2_sha256.verify(password, users[username]):
        client_socket.send(do_encrypt(pickle.dumps("True")))
        return username
    else:
        client_socket.send(do_encrypt(pickle.dumps("False")))


def sign_up(client_socket):
    global leaderboard
    (username, password) = pickle.loads(do_decrypt(client_socket.recv(50000)))
    if username in users.keys() or not pass_requirements(password):
        client_socket.send(do_encrypt(pickle.dumps("False")))
    else:
        hash = pbkdf2_sha256.hash(password)
        txt = open(usersfile, "a")
        txt.write(username + " " + hash + "\n")
        txt.close()
        users[username] = hash
        leaderboard[username] = (0, time.strftime("%d/%m/%Y"))
        client_socket.send(do_encrypt(pickle.dumps("True")))
        return username


def pass_requirements(password):
    #   At least 6 letters
    #   minimum 2 lowercase, 2 uppercase and 2 numbers
    lwc = upc = num = 0
    if len(password) < 6:
        return False
    for char in str(password):
        if char.isdigit():
            num += 1
        elif char.islower():
            lwc += 1
        elif char.isupper():
            upc += 1
    if lwc >= 2 and upc >= 2 and num >= 2:
        return True
    return False


def main(client_socket):
    global key, iv
    iv = Random.new().read(AES.block_size)
    key = Random.new().read(AES.block_size)
    client_socket.send(pickle.dumps((key, iv)))
    load_users()
    load_leaderboard()
    req = "Password requirements: \nminimum 2 lowercase, 2 uppercase and 2 numbers"
    req = req.rjust(len(req)+24)
    try:
        client_socket.send(do_encrypt(pickle.dumps(req)))
        username = None
        while username is None:
            flag = pickle.loads(do_decrypt(client_socket.recv(50000)))
            if flag == "Login":
                username = log_in(client_socket)
            elif flag == "Signup":
                username = sign_up(client_socket)
            else:
                return
        test2 = None
        while test2 != "FIN":
            (test2, score) = pickle.loads(do_decrypt(client_socket.recv(50000)))
            if int(score) > int(leaderboard[username][0]):
                date = str(time.strftime("%d/%m/%Y"))
                txt = open(leaderboardfile, "a")
                txt.write(str(username) + " " + str(score) + " " + str(date) + "\n")
                txt.close()
                leaderboard[username] = (score, date)
            if test2 == "L":
                client_socket.send(do_encrypt(pickle.dumps(leaderboard)))
    except:
        pass


def goodbye(server_socket):
    server_socket.bind((ip, port))
    server_socket.listen(1)
    print "Server is running"

    while True:
        (client_socket, client_address) = server_socket.accept()
        tr = threading.Thread(target=main, args=(client_socket,))
        tr.daemon = True
        tr.start()

# ================================================================================================#
#                                              Main                                               #
# ================================================================================================#

server_socket = socket.socket()
t = threading.Thread(target=goodbye, args=(server_socket,))
t.setDaemon(True)
t.start()

while raw_input() != "exit":
    pass

server_socket.close()
