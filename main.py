import chessmain as chess
import engine as engine
import os
import json

path = os.getcwd()
with open(path + "/config.json") as file:
    config = json.load(file)
    file.close()

WIDTH = HEIGHT = config["resolution"]
size = WIDTH, HEIGHT
title = "Chess"


def main():
	game = chess.Game(title, size)
	game.new()

if __name__ == "__main__":
	main()