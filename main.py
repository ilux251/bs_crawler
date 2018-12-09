from flask import Flask, render_template, request
from lxml import html
import requests
import json
import smtplib
import os

app = Flask('__main__')

mailHost = "alexanderulrich98@gmx.de"
mailTo = ["alexanderulrich98@gmail.com", "ritschulrich@live.de"]
favoriteList = ["alex_favorite", "ritsch_favorite"]


@app.route('/')
@app.route('/getSeries', methods=["GET", "POST"])
def main():
    show()
    return "HOME"


@app.route('/setFavorite')
def defineFavorites():
    return render_template("favorite.html")


@app.route('/getFavorite', methods=["POST"])
def writeFavoritesToList():
    user = request.form.get("user")
    favoriteSerie = request.form.get("title")
    path = "static/" + user + "_favorite.json"
    favoritesList = []
    if os.path.exists(path):
        readFavoriteFile = open(path, "r")
        favorites = readFavoriteFile.read()
        favoritesList = favorites.split(",")
        print(favoritesList)
    if not (favoriteSerie in favoritesList):
        favoriteFile = open(path, "a+")
        favoriteFile.write(favoriteSerie)
        print("Favorite %s is not in list" % favoriteSerie)
    return render_template("favorite.html")


@app.route('/test', methods=["GET", "POST"])
def test():
    serien = getDataFromRenderedPage("test.html")
    titles = getTitle(serien)
    currents = getCurrent(serien)
    oldSeries = readSerienToJsonFile()
    series = buildSeries(titles, currents)
    favoriteSeries = getFavoriteSeries(series, favoriteList[0])
    seriesToSend = checkSeriesInCurrentList(oldSeries, favoriteSeries)
    msgToSend = getMsgToSend(seriesToSend)

    print(msgToSend)

    if sendSeriesPerMail(mailHost, mailTo[0], msgToSend, "Favorite Series"):
        writeSerienToJsonFile(oldSeries, seriesToSend)

    return "TEST"


def getMsgToSend(seriesToSend):
    seriesToString = ""

    if isinstance(seriesToSend, type(None)):
        return ""

    for serie in seriesToSend:
        seriesToString += "Serie: " + serie[0] + " - aktuelle Folge: " + serie[1] + '\n'
    return seriesToString


def sendSeriesPerMail(fromAdresse, toAdresse, message, betreff):
    if message == "":
        return

    try:
        server = smtplib.SMTP('mail.gmx.com', 587)
        server.starttls()
        header = 'To:' + toAdresse + '\n' + 'From: ' + fromAdresse + '\n' + "Subject: " + betreff + '\n'
        msg = header + '\n' + message
        server.login(fromAdresse, "<PASSWORT>")
        server.sendmail(fromAdresse, toAdresse, msg)
        server.quit()
        print("Success: Email sent!")
        return True
    except Exception as e:
        print(e)

    return False


def buildSeries(titles, currents):
    return list(map(lambda title, current: [title, current], titles, currents))


def checkSeriesInCurrentList(oldSeries, favoriteSeries):
    if oldSeries and favoriteSeries:
        return list(filter(lambda serieToSend: not isSerieInOldList(oldSeries, serieToSend), favoriteSeries))


def isSerieInOldList(oldSeries, serieToSend):
    if serieToSend[0] in oldSeries:
        if serieToSend[1] in oldSeries[serieToSend[0]]:
            return serieToSend


def readSerienToJsonFile():
    file = open("static/aktuelleSerien.json")
    data = file.read()
    if data.strip() != "":
        oldSeries = json.loads(data)
        return oldSeries
    return []


def writeSerienToJsonFile(oldSeries, seriesToSend):
    for serieToSend in seriesToSend:
        if serieToSend[0] in oldSeries:
            oldSeries[serieToSend[0]].append(serieToSend[1])
        else:
            oldSeries[serieToSend[0]] = [serieToSend[1]]
            print("Serie %s nicht vorhanden" % serieToSend)
    file = open("static/aktuelleSerien.json", "w")
    file.write(str(oldSeries).replace("'", '"'))


def getFavoriteSeries(series, favoriteList):
    return list(filter(lambda serie: isFavorite(serie, favoriteList), series))


def isFavorite(serie, favoriteList):
    file = open("static/" + favoriteList + ".fav")
    favoriteSeries = file.read()
    splitedList = favoriteSeries.split(",")
    print(splitedList)
    if splitedList:
        print("xxxxxxxxx")
        for s in splitedList:
            print(s)
            return serie[0].lower() in s.lower()


def getTitle(data):
    return data[0::2]


def getCurrent(data):
    return data[1::2]


def show():
    print(mailHost)
    print(mailTo)


def getDataFromRenderedPage(pageToRender):
    website = render_template(pageToRender)
    response = html.fromstring(website)
    serien = response.xpath("//div/section/div/section/div/ul/li/a/div/text()")
    return serien


def getDataFromWebsite(websiteUrl):
    page = requests.get(websiteUrl)
    response = html.fromstring(page.content)
    serien = response.xpath("//div/section/div/section/div/ul/li/a/div/text()")
    return serien


if __name__ == '__main__':
    app.run(debug=True)
