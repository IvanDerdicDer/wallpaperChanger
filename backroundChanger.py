import ctypes
import os
from datetime import timedelta, date
from time import sleep, localtime, timezone, altzone
import math
from astral import Astral
from scipy.integrate import quad
from threading import Thread, Event
import json

def splitDayIntoParts(n: int, latitude: float, longitude: float) -> list[timedelta]:
    sunrise, sunset = calculateDaytime(latitude, longitude)

    dayLength = sunset - sunrise
    dayLength = dayLength.total_seconds()
    nightLength = 24*60*60 - dayLength

    interval = 2.6 / (math.floor(n / 2 - 1) if math.floor(n / 2 - 1) != 0 else 1)
    integrationNumbersDay = [-1.3 + i * interval for i in range(math.floor(n / 2 - 1))]
    a = dayLength/(12*60*60)
    modifiedGaussian = lambda x: (math.sqrt(a) / math.sqrt(2 * math.pi)) * math.exp(-a*(x**2)/2)
    daytimeIntervals = [sunrise + timedelta(seconds=(1 - quad(modifiedGaussian, integrationNumbersDay[i], math.inf)[0]) * dayLength) for i in range(len(integrationNumbersDay))]
    daytimeIntervals.append(sunset)

    interval = 2.6 / (math.floor(n / 2 - 1) if math.floor(n / 2 - 1) != 0 else 1)
    integrationNumbersNight = [-1.3 + i * interval for i in range(math.ceil(n / 2 - 1))]
    a = nightLength / (12 * 60 * 60)
    modifiedGaussian = lambda x: (math.sqrt(a) / math.sqrt(2 * math.pi)) * math.exp(-a * (x ** 2) / 2)
    nighttimeIntervals = [sunset + timedelta(seconds=(1 - quad(modifiedGaussian, integrationNumbersNight[i], math.inf)[0]) * nightLength) for i in range(len(integrationNumbersNight))]
    nighttimeIntervals.append(sunrise)

    toReturn = daytimeIntervals + [i - timedelta(days=1) if i.days > 0 else i for i in nighttimeIntervals]
    toReturn.sort()

    return toReturn

def changeWallpaper(pathToWallpaper: str):
    ctypes.windll.user32.SystemParametersInfoW(20, 0, pathToWallpaper, 0)

def getCurrentTime() -> timedelta:
    timeToReturn = localtime()
    timeToReturn = timedelta(seconds=(timeToReturn.tm_hour * 60 + timeToReturn.tm_min) * 60 + timeToReturn.tm_sec)
    return timeToReturn

def calculateDaytime(lat: float, long: float) -> tuple[timedelta, timedelta]:
    timeZoneLocal = timezone if localtime().tm_isdst == 0 else altzone
    timeZoneLocal *= -1

    sunriseInSecs = Astral().sunrise_utc(date.today(), lat, long)
    sunriseInSecs = (sunriseInSecs.hour * 60 + sunriseInSecs.minute) * 60 + sunriseInSecs.second
    sunriseInSecs += timeZoneLocal

    sunsetInSecs = Astral().sunset_utc(date.today(), lat, long)
    sunsetInSecs = (sunsetInSecs.hour * 60 + sunsetInSecs.minute) * 60 + sunsetInSecs.second
    sunsetInSecs += timeZoneLocal

    return timedelta(seconds=sunriseInSecs), timedelta(seconds=sunsetInSecs)

def chooseWallpaper(dayIntervals: list[timedelta], currentTime:timedelta) -> int:
    for intervalStart in dayIntervals:
        if currentTime < intervalStart:
            return dayIntervals.index(intervalStart) - 1
    return -1

def sortWallpapers(l: list[str]) -> list[str]:
    indexList = [int(i.split("_")[-1].split(".")[0]) for i in l]
    indexList.sort()
    sortedList = []
    #Yes its O(n^2), deal with it
    for i in indexList:
        for j in l:
            if i == int(j.split("_")[-1].split(".")[0]):
                sortedList.append(j)
                break
    return sortedList

def initialiseRelevantVariables(relativePath: str, latitude: float, longitude: float) -> tuple[list[str], list[timedelta]]:
    #Converts relative path to absolute path
    pathToWallpapers = os.path.abspath(relativePath)
    wallpapersIterator = os.scandir(pathToWallpapers)
    #List of absolute paths for each wallpaper
    pathToWallpaper = [i.path for i in wallpapersIterator]
    pathToWallpaper = sortWallpapers(pathToWallpaper)
    dayIntervals = splitDayIntoParts(len(pathToWallpaper), latitude, longitude)

    return pathToWallpaper, dayIntervals

def wallpaperChangingLoop(killThread: Event, dayIntervals: list[timedelta], pathToWallpaper: list[str]):
    previousIndex = None
    while True and not killThread.isSet():
        print("Entered loop")
        currentTime = getCurrentTime()
        currentIndex = chooseWallpaper(dayIntervals, currentTime)
        print(f"currentTime: {currentTime}, currentIndex: {currentIndex}, previousIndex: {previousIndex}")
        #Makes sure wallpaper isn't changed constantly
        if currentIndex != previousIndex:
            changeWallpaper(pathToWallpaper[currentIndex])
            print("Wallpaper changed")
            previousIndex = currentIndex
        sleep(30)

def main():
    # Relative path to wallpapers folder
    # In the future should be changed trough a GUI to select wallpaper batch
    previousRelativePath = ""
    previousLongitude = None
    previousLatitude = None
    killThread = Event()

    pathToWallpaper = None
    dayIntervals = None

    wallpaperThread = Thread(target=wallpaperChangingLoop, args=(killThread, dayIntervals, pathToWallpaper))

    while True:
        with open("config.json", "r") as config:
            configJSON = json.loads(config.read())
            relativePath = configJSON['relativePath']
            longitude = configJSON['longitude']
            latitude = configJSON['latitude']

        if relativePath != previousRelativePath or longitude != previousLongitude or latitude != previousLatitude:
            pathToWallpaper, dayIntervals = initialiseRelevantVariables(relativePath, latitude, longitude)

            if wallpaperThread.is_alive():
                killThread.set()

            if not wallpaperThread.is_alive():
                killThread.clear()
                wallpaperThread = Thread(target=wallpaperChangingLoop, args=(killThread, dayIntervals, pathToWallpaper))
                wallpaperThread.start()

            previousLatitude = latitude
            previousLongitude = longitude
            previousRelativePath = relativePath

        sleep(30)

if __name__ == '__main__':
    main()
