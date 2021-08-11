import socket as soc
from tarring import compress
import os
from threading import Thread
from time import sleep
from random import sample
import json
from backroundChanger import getCurrentTime
from datetime import timedelta

class Server:
    serverPort: int

    def __init__(self, pathToWallpapers: str, serverIP: str, serverPort: int, bufferSize: int = 4096):
        self.serverIP = serverIP
        self.serverPort = serverPort
        self.bufferSize = bufferSize
        self.pathToWallpapers = os.path.abspath(pathToWallpapers)
        self.homeDir = os.getcwd()
        self.pathToWallpaperSetToSend = None
        self.selectWallpaperSet()


    def start(self) -> None:
        canSelect = True
        with soc.socket(soc.AF_INET, soc.SOCK_STREAM) as s:
            s.bind((self.serverIP, self.serverPort))
            print(f"Server started")
            s.listen(10)

            while True:
                if timedelta(seconds=24*60*60 - 10) < getCurrentTime() < timedelta(seconds=24*60*60):
                    if canSelect:
                        self.selectWallpaperSet()
                else:
                    canSelect = True
                clientSocket, address = s.accept()
                Thread(target=self.sendWallpaperSet, args=(clientSocket, address)).start()
                sleep(0.01)


    def sendWallpaperSet(self, clientSocket: soc.socket, address) -> None:
        compressedWallpaperSet = f"compressedWallpapers/{os.path.basename(self.pathToWallpaperSetToSend)}.tar.gz"
        compressedWallpaperSet = os.path.abspath(compressedWallpaperSet)
        if not os.path.exists("compressedWallpapers"):
            os.mkdir("compressedWallpapers")
        if not os.path.exists(compressedWallpaperSet):
            os.chdir(self.pathToWallpapers)
            compress(compressedWallpaperSet, [os.path.basename(self.pathToWallpaperSetToSend)])
            os.chdir(self.homeDir)
        print(f"{address = } connected")
        with clientSocket:
            clientSocket.sendall(f"{os.path.basename(compressedWallpaperSet.split('.')[0])}".encode())

            if not clientSocket.recv(self.bufferSize).decode() == "YES_SEND":
                clientSocket.close()
                return

            print(f"Sending {compressedWallpaperSet = }")
            with open(compressedWallpaperSet, "rb") as f:
                blockToSend = f.read(self.bufferSize)
                while blockToSend:
                    clientSocket.sendall(blockToSend)
                    blockToSend = f.read(self.bufferSize)


    def selectWallpaperSet(self) -> None:
        wallpaperSetsIterator = os.scandir(self.pathToWallpapers)
        listOfWallpaperSets: list[str] = [i.path for i in wallpaperSetsIterator]

        toReturn: list[str] = sample(listOfWallpaperSets, 1)

        self.pathToWallpaperSetToSend = toReturn[-1]


def main() -> None:
    serverIP = "127.0.0.1"
    serverPort = 5001
    with open("configServer.json", "r") as config:
        configJSON = json.loads(config.read())
        pathToWallpapers: str = configJSON["pathToWallpapers"]

    server = Server(pathToWallpapers, serverIP, serverPort)
    server.start()


if __name__ == '__main__':
    main()
