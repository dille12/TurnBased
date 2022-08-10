from _thread import *
import time
import ast
import traceback

from game_objects.game_object import *
from game_objects.npc import *
from game_objects.building import *
from game_objects.wall import *
from game_objects.deposit import *
from game_objects.objects import *
from game_objects.cable import *
from core.map_gen import *


class DataGatherer:
    def __init__(self, game):
        self.game_ref = game
        self.gathering = False
        self.data = []

    def tick(self):
        if not self.gathering:
            start_new_thread(self.threaded_data_gather, ())

    def parse(self, data):

        print("Parsing data...")

        for individual_packet in data.split("END#"):
            for line in individual_packet.split("\n"):
                if line == "PACKET" or line == "/":
                    continue
                try:
                    print("Evaluating line", line)
                    eval(line)
                    print("SUCCESS")
                except Exception as e:
                    print(line)
                    print("Exception:",e)
                    print(traceback.print_exc())





    def threaded_data_gather(self):
        self.gathering = True
        t = time.time()
        packet = f"PACKET\n"
        for x in self.data:
            packet += x + "\n"
            self.data.remove(x)
        packet += "END#"

        #print(f"Sending from player {self.player_team.name}\n{packet}")

        reply = self.game_ref.network.send(packet)

        if reply.strip() not in ["ok", "/", "/ok", "/ok/", "ok/"]:
            print("Received packet:\n", reply)
            self.parse(reply)

        self.gathering = False
