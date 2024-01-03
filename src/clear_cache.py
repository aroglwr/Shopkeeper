from os import path, rmdir, system, remove
from shutil import rmtree
from API.general import progressBar
from time import sleep

length = 20
print("Clearing cache...\n")
print(progressBar(length, 0))


system("cls")
print("Deleting mastery graphs...\n")
print(progressBar(length, 0.3))
rmtree("src/files/SummonerMastery")



system("cls")
print("Deleting patch data...\n")
print(progressBar(length, 0.6))
remove("src/files/lolLatestPatch.json")


system("cls")
print("Clearing Steam game list...\n")
print(progressBar(length, 0.9))
remove("src/files/gameList.json")


sleep(1)
system("cls")
print("Done!\n")
print(progressBar(length, 1))
