import socket
from _thread import *
import sys
import traceback

players = {}

running = True

stop_threads = False
map_index = 0
game_stage = "lobby"


def threaded_client(conn):
    global players, running, stop_threads, game_stage, map_index

    conn.send(str.encode("ok"))
    print(conn, "accepted")

    while running:
        try:
            data = conn.recv(2048)
            reply = data.decode("utf-8")
            if stop_threads:
                break

            if reply == "kill":
                conn.sendall(str.encode("/"))
                running = False

                for x in players:
                    x.close()
                    print(x, "closed")

                break
            conn.sendall(str.encode("/"))
        except Exception as e:
            print("SERVER ERROR", e)
            print(traceback.print_exc())
            break
    print("Connection Closed")
    del players[conn]
    conn.close()


def return_players():
    return players


def server_run():

    global players, running, stop_threads

    print("Starting host")
    print(socket.gethostbyname(socket.gethostname()))

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    print(ip_address)
    port = 5555

    print("INITTING")
    try:
        print("Trying")
        s.bind((ip_address, port))

    except socket.error as e:
        print(str(e))

    s.listen(2)
    print("Waiting for a connection")

    currentId = "0"

    while running:
        print("Server ticking...")
        conn, addr = s.accept()
        print("SERVER: Connected to: ", addr)
        players[conn] = {
            "username": "",
            "x": "0",
            "y": "0",
            "a": "0",
            "hp": "100",
            "bullets": [],
            "grenades": [],
            "zombies": [],
            "z_events": [],
            "turrets": [],
            "barricades": [],
        }
        print("SERVER: CREATING A THREAD TO", addr)

        start_new_thread(threaded_client, (conn,))
    stop_threads = True
    print("Server killed")
