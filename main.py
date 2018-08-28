from flask import Flask, render_template
from lxml import html
import requests
import json
import smtplib

app = Flask('__main__')

mailHost = "alexanderulrich98@gmx.de"
mailTo = ["alexanderulrich98@gmail.com", "ritschulrich@live.de"]
favoriteList = ["alexFavoriteSeries", "ritschFavoriteSeries"]


@app.route('/')
@app.route('/getSeries', methods=["GET", "POST"])
def main():
    show()
    return "HOME"


@app.route('/test', methods=["GET", "POST"])
def test():
    serien = getDataFromRenderedPage("test.html")
    titles = getTitle(serien)
    currents = getCurrent(serien)
    oldSeries = readSerienToJsonFile()

    series = buildSeries(titles, currents)

    favoriteSeries = getFavoriteSeries(series, favoriteList[0])

    seriesToSend = checkSeriesInCurrentList(oldSeries, favoriteSeries)

    # sendSeriesPerMail(seriesToSend)

    writeSerienToJsonFile(oldSeries, seriesToSend)

    return "TEST"


def sendSeriesPerMail(seriesToSend):
    if len(seriesToSend) > 0:
        print(seriesToSend)


def buildSeries(titles, currents):
    return list(map(lambda title, current: [title, current], titles, currents))


def checkSeriesInCurrentList(oldSeries, favoriteSeries):
    if oldSeries and favoriteSeries:
        return list(filter(lambda serieToSend: not serieToSend[1] in oldSeries[serieToSend[0]], favoriteSeries))


def readSerienToJsonFile():
    file = open("static/aktuelleSerien.json")
    data = file.read()
    if data.strip() != "":
        oldSeries = json.loads(data)
        return oldSeries
    return []


def writeSerienToJsonFile(oldSeries, seriesToSend):
    for serieToSend in seriesToSend:
        if oldSeries[serieToSend[0]]:
            oldSeries[serieToSend[0]].append(serieToSend[1])
        else:
            oldSeries[serieToSend[0]] = [serieToSend[1]]
    file = open("static/aktuelleSerien.json", "w")
    file.write(str(oldSeries).replace("'", '"'))


def getFavoriteSeries(series, favoriteList):
    return list(filter(lambda serie: isFavorite(serie, favoriteList), series))


def isFavorite(serie, favoriteList):
    file = open("static/" + favoriteList + ".fav")
    favoriteSeries = file.read()
    if favoriteSeries.strip() != "":
        return serie[0].lower() in favoriteSeries.lower()


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
