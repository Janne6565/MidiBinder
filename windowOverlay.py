import sys

import requests
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap, QPen, QPainter
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QGraphicsDropShadowEffect

position = (2600, 300)
padding = 20

window = None


def trunc(string, lenght):
    return string[:lenght] + (string[lenght:] and '...')


class MainWindow(QMainWindow):
    audioLevels = {
        'tabs': [
            {
                'title': 'Spotify',
                'percentage': 0.2,
                'color': 'green'
            },
            {
                'title': 'Chrome',
                'percentage': 0.4,
                'color': 'red'
            },
            {
                'title': 'Discord',
                'percentage': 0.4,
                'color': 'gray'
            },
        ],
    }

    spotifyInformations = {
        'Song Name': "Sunflower - Spider-Man: Into the Spider-Verse",
        'Artist': "Post Malone",
        'Album': "Spider-Man: Into the Spider-Verse (Soundtrack From & Inspired by the Motion Picture)",
        'Album Art': "https://i.scdn.co/image/ab67616d00001e02183a93277b6ceece310fa366"
    }

    page = "audioInfos"

    pixmap = None
    opacity = 0.9
    functionCallOnUpdate = None

    def __init__(self, callOnUpdate):
        QMainWindow.__init__(self)

        self.functionCallOnUpdate = callOnUpdate

        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.X11BypassWindowManagerHint |
            QtCore.Qt.Tool |
            QtCore.Qt.WindowTransparentForInput
        )

        self.setDimensions(300, 240)

        self.update()

        self.label = QLabel(self)
        self.setCentralWidget(self.label)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(int(1000 * 0.1))

    def setDimensions(self, width, height):
        desktop = QtWidgets.QApplication.desktop()
        screen_count = desktop.screenCount()

        if screen_count > 1:
            # If multiple screens are available, position the window on the second screen
            screen_geometry = desktop.screenGeometry(1)
        else:
            # If only one screen is available, use the available geometry of the screen
            screen_geometry = desktop.availableGeometry()

        # Set the top-left corner of the window to the (100, 100) position on the screen
        self.setGeometry(100, 100, width, height)

        shadow_effect = QGraphicsDropShadowEffect(self)
        shadow_effect.setBlurRadius(30)
        shadow_effect.setXOffset(0)
        shadow_effect.setYOffset(0)
        shadow_effect.setColor(QtGui.QColor('black'))
        shadow_effect.setBlurRadius(30)
        shadow_effect.setOffset(0, 0)

        pixmap = QPixmap(self.size())
        pixmap.fill(QtGui.QColor('transparent'))
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QtGui.QColor('red'))
        painter.drawRoundedRect(pixmap.rect(), 10, 10)
        painter.end()

        # Set the mask of the window to the pixmap
        mask = pixmap.mask()
        self.setMask(mask)

        # Set the QGraphicsDropShadowEffect as the window's graphics effect
        self.setGraphicsEffect(shadow_effect)

        self.move(screen_geometry.topLeft())
        self.move(position[0], position[1])

        self.pixmap = QPixmap(self.size())

    def mousePressEvent(self, event):
        self.update()

    lastPage = None

    def update(self):
        self.functionCallOnUpdate()

        if self.page == "audioInfos" and self.lastPage != self.page:
            self.lastPage = self.page
            self.setDimensions(300, 240)

        if self.page == "spotify" and self.lastPage != self.page:
            self.lastPage = self.page
            self.setDimensions(300, 290)

        self.pixmap.fill(QtGui.QColor('black'))
        painter = QPainter(self.pixmap)

        painter.setFont(QtGui.QFont('Decorative', 15))

        rect = self.pixmap.rect()

        if self.page == "audioInfos":
            spacing = 50
            for indexOfApplication in range(min(4, len(self.audioLevels['tabs']))):
                application = self.audioLevels['tabs'][indexOfApplication]

                painter.setPen(QPen(QtGui.QColor('lightgray'), 2))
                painter.drawLine(int(padding), int(spacing * (indexOfApplication + 1)),
                                 int(self.pixmap.width() - padding),
                                 int(spacing * (indexOfApplication + 1)))

                painter.setPen(QPen(QtGui.QColor(application['color']), 2))
                painter.drawLine(int(padding), int(spacing * (indexOfApplication + 1)),
                                 int((self.pixmap.width() - 2 * padding) * application['percentage'] + padding),
                                 int(spacing * (indexOfApplication + 1)))

                painter.setPen(QPen(QtGui.QColor('white'), 5))
                painter.drawText(int(padding), int(spacing * (indexOfApplication + 1)) - 10, application['title'])
        elif self.page == "spotify":
            rect = QtCore.QRect(0, 0, self.pixmap.width(), self.pixmap.height() + 100)
            painter.setPen(QPen(QtGui.QColor('white'), 1))
            string = trunc(self.spotifyInformations['Song Name'], 25) + "\n" + trunc(self.spotifyInformations['Artist'],
                                                                                     25) + "\n" + trunc(
                self.spotifyInformations['Album'], 25)
            # Draw text in the center of the window with auto word wrap
            painter.drawText(rect, QtCore.Qt.AlignCenter, string)

            image = QtGui.QImage()
            image.loadFromData(requests.get(self.spotifyInformations['Album Art']).content)
            image = image.scaled(100, 100, QtCore.Qt.KeepAspectRatio)
            # round corners of image
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(QtGui.QColor('white'))
            painter.drawRoundedRect(int((rect.width() - image.width()) / 2), 20, 20, 20, 60, 60)
            painter.setClipRect(int((rect.width() - image.width()) / 2), 20, 100, 100)
            painter.drawImage(int((rect.width() - image.width()) / 2), 20, image)

        rect.setHeight(rect.height() - 20)

        painter.end()
        self.setWindowOpacity(self.opacity)
        try:
            self.label.setPixmap(self.pixmap)
        except:
            pass


def instantiateEverything(callOnUpdate=None):
    global window
    app = QApplication(sys.argv)
    window = MainWindow(callOnUpdate)
    window.page = "spotify"

    window.show()
    app.exec_()
    window.update()


def setOpacity(opacity):
    global window
    if window is not None:
        window.opacity = opacity


def setInformation(information):
    global window
    if window is not None:
        window.audioLevels = information
        window.page = "audioInfos"


def setSpotifyInformations(information):
    global window
    print(information)
    if window is not None:
        window.spotifyInformations = information
        window.page = "spotify"


def setPage(page):
    global window
    if window is not None:
        window.page = page

def __init__(callOnUpdate=None):
    instantiateEverything(callOnUpdate)


if __name__ == '__main__':
    __init__()
