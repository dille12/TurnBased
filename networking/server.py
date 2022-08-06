import socket
from _thread import *
import sys
import traceback
from values import *
import time

teams = [blue_t, red_t, green_t, yellow_t]
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

            if players[conn]["username"] == "":
                players[conn]["username"] = reply
                players[conn]["team"] = teams[len(players)-1]
                print(f"Assigned player {reply} to {teams[len(players)-1].color}")

            elif reply[:6] == "PACKET":
                time.sleep(1)
                conn.send(str.encode(reply))

            elif "STARTGAME" in reply.split("/"):
                print("STARTING GAME!")
                for x in players:
                    print("Sending", players[x]["username"], "to game ")
                    players[x]["ingame"] = True
                conn.send(str.encode("ok"))

            elif reply == players[conn]["username"]:
                if players[conn]["ingame"]:
                    print("SENDING START GAME TO", players[conn]["username"])
                    conn.send(str.encode("/STARTGAME/"))
                else:
                    rep = ""
                    for x in players:
                        rep += players[x]["username"] + "-" + str(players[x]["team"].color) + "-" + str(players[x]["team"].str_team) + "/"
                    conn.send(str.encode(rep))



            elif reply == "kill":
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
            "team" : placeholder,
            "ingame" : False
        }
        print("SERVER: CREATING A THREAD TO", addr)

        start_new_thread(threaded_client, (conn,))
    stop_threads = True
    print("Server killed")
