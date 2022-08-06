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
                players[conn]["team"].name = players[conn]["username"]
                print(f"Assigned player {reply} to {teams[len(players)-1].color}")

            elif reply[:6] == "PACKET":
                time.sleep(0.1)
                for individual_packet in reply.split("END#"):
                    for line in individual_packet.split("\n"):
                        if line == "PACKET" or line == "/" or line == "":
                            continue
                        for x in players:
                            if x == conn:
                                continue
                            players[x]["data"].append(line)
                            print("Saved line for", players[x]["team"].name)
                            print(">>> ", line)

                if players[conn]["data"] != []:

                    data = "PACKET\n"
                    for line_2 in players[conn]["data"]:
                        data += line_2 + "\n"
                        players[conn]["data"].remove(line_2)
                        print("FOUND LINE:", players[conn]["username"], line_2)
                    data += "END#"
                    print(f"{data}")
                else:
                    data = "ok"
                conn.send(str.encode(data))

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
            "ingame" : False,
            "data" : []
        }
        print("SERVER: CREATING A THREAD TO", addr)

        start_new_thread(threaded_client, (conn,))
    stop_threads = True
    print("Server killed")
