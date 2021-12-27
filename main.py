import sys

from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QTabBar,
                             QFrame, QStackedLayout, QShortcut, QSplitter)
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import QWebEngineView


class AddressBar(QLineEdit):
    def __init__(self):
        super().__init__()

    def mousePressEvent(self, e):
        self.selectAll()


class App(QFrame):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Web Browser")
        self.setBaseSize(1366, 768)
        self.setMinimumSize(1366, 768)
        self.CreateApp()
        self.setWindowIcon(QIcon("icon.jpg"))

    def CreateApp(self):
        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Create Tabs
        self.tabbar = QTabBar(movable=True, tabsClosable=True)
        self.tabbar.tabCloseRequested.connect(self.CloseTab)
        self.tabbar.tabBarClicked.connect(self.SwitchTab)
        self.tabbar.setCurrentIndex(0)
        self.tabbar.setDrawBase(False)
        self.tabbar.setLayoutDirection(Qt.LeftToRight)
        self.tabbar.setElideMode(Qt.ElideLeft)

        # Shortcut for New Tab
        self.shortcutNewTab = QShortcut(QKeySequence("Ctrl+T"), self)
        self.shortcutNewTab.activated.connect(self.AddTab)

        # Shortcut for Reload the page
        self.shortcutReload = QShortcut(QKeySequence("Ctrl+R"), self)
        self.shortcutReload.activated.connect(self.ReloadPage)

        # Keep track of tabs
        self.tabCount = 0
        self.tabs = []

        # Create AddressBar
        self.Toolbar = QWidget()
        self.Toolbar.setObjectName("Toolbar")
        self.ToolbarLayout = QHBoxLayout()
        self.addressbar = AddressBar()
        self.AddTabButton = QPushButton("+")

        # Connect AddressBar + button Signals
        self.addressbar.returnPressed.connect(self.BrowseTo)
        self.AddTabButton.clicked.connect(self.AddTab)

        # Set Toolbar Buttons
        self.BackButton = QPushButton("<")
        self.BackButton.clicked.connect(self.GoBack)

        self.ForwardButton = QPushButton(">")
        self.ForwardButton.clicked.connect(self.GoForward)

        self.ReloadButton = QPushButton("Reload Page")
        self.ReloadButton.clicked.connect(self.ReloadPage)

        # Build toolbar
        self.Toolbar.setLayout(self.ToolbarLayout)
        self.ToolbarLayout.addWidget(self.BackButton)
        self.ToolbarLayout.addWidget(self.ForwardButton)
        self.ToolbarLayout.addWidget(self.ReloadButton)
        self.ToolbarLayout.addWidget(self.addressbar)
        self.ToolbarLayout.addWidget(self.AddTabButton)

        # Set main view
        self.container =QWidget()
        self.container.layout = QStackedLayout()
        self.container.setLayout(self.container.layout)

        # Construct main view from top level elements
        self.layout.addWidget(self.tabbar)
        self.layout.addWidget(self.Toolbar)
        self.layout.addWidget(self.container)
        self.setLayout(self.layout)

        self.AddTab()

        self.show()

    def CloseTab(self, i):
        if i >= 1:
            self.tabbar.removeTab(i)

    def AddTab(self):
        i = self.tabCount

        # Set self.tabs<#> = QWidget
        self.tabs.append(QWidget())
        self.tabs[i].layout = QVBoxLayout()
        self.tabs[i].layout.setContentsMargins(0, 0, 0, 0)

        # For tab switching
        self.tabs[i].setObjectName("tab" + str(i))

        # Create webview within the tabs top level widget
        self.tabs[i].content = QWebEngineView()
        self.tabs[i].content.load(QUrl.fromUserInput("http://google.com"))

        # Create splitted tab for DevTools
        #self.tabs[i].contentDevTools = QWebEngineView()
        #self.tabs[i].contentDevTools.load(QUrl.fromUserInput("http://google.com"))

        self.tabs[i].content.titleChanged.connect(lambda: self.SetTabContent(i, "title"))
        self.tabs[i].content.iconChanged.connect(lambda: self.SetTabContent(i, "icon"))
        self.tabs[i].content.urlChanged.connect(lambda: self.SetTabContent(i, "url"))

        # Add widget to tab.layout
        self.tabs[i].layout.addWidget(self.tabs[i].content)

        # Fot split the tabs for DevTools
        #self.tabs[i].splitview = QSplitter()
        #self.tabs[i].splitview.setOrientation(Qt.Horizontal)
        #self.tabs[i].layout.addWidget(self.tabs[i].splitview)
        #self.tabs[i].splitview.addWidget(self.tabs[i].contentDevTools)

        # Set tabLayout to .layout
        self.tabs[i].setLayout(self.tabs[i].layout)

        # Add and set new tabs content to stack widget
        self.container.layout.addWidget(self.tabs[i])
        self.container.layout.setCurrentWidget(self.tabs[i])

        # Create tab on tabbar, representing this tab,
        # Set tabData to tab<#> So it knows what self.tabs[#] it needs to control
        self.tabbar.addTab("New Tab")
        self.tabbar.setTabData(i, {"object": "tab" + str(i), "initial": i})

        #print("Tab Data: ", self.tabbar.tabData(i)["object"])
        self.tabbar.setCurrentIndex(i)
        #  += 1
        self.tabCount += 1

    def SwitchTab(self, i):
        # Switch to tab. Get current tabs tabData ("tab0") and find object with that name
        if self.tabbar.tabData(i):
            tab_data = self.tabbar.tabData(i)["object"]
            tab_content = self.findChild(QWidget, tab_data)
            self.container.layout.setCurrentWidget(tab_content)
            new_url = tab_content.content.url().toString()
            self.addressbar.setText(new_url)

    def BrowseTo(self):
        text = self.addressbar.text()

        i = self.tabbar.currentIndex()
        tab = self.tabbar.tabData(i)["object"]
        web_view = self.findChild(QWidget, tab).content

        if "http" not in text:
            if "." not in text:
                url = "https://www.google.com/search?q=" + text
            else:
                url = "http://" + text
        else:
            url = text

        web_view.load(QUrl.fromUserInput(url))

    def SetTabContent(self, i, type):
                                # tab1 for example
        tab_name = self.tabs[i].objectName()

        count = 0
        running = True

        current_tab = self.tabbar.tabData(self.tabbar.currentIndex())["object"]
        if current_tab == tab_name and type == "url":
            new_url = self.findChild(QWidget, tab_name).content.url().toString()
            self.addressbar.setText(new_url)
            return False

        while running:
            tab_data_name = self.tabbar.tabData(count)

            if count >= 99:
                running = False

            if tab_name == tab_data_name["object"]:
                if type == "title":
                    new_title = self.findChild(QWidget, tab_name).content.title()
                    self.tabbar.setTabText(count, new_title)
                elif type == "icon":
                    new_icon = self.findChild(QWidget, tab_name).content.icon()
                    self.tabbar.setTabIcon(count, new_icon)

                running = False
            else:
                count += 1

    def GoBack(self):
        activeIndex = self.tabbar.currentIndex()
        tab_name = self.tabbar.tabData(activeIndex)["object"]
        tab_content = self.findChild(QWidget, tab_name).content

        tab_content.back()

    def GoForward(self):
        activeIndex = self.tabbar.currentIndex()
        tab_name = self.tabbar.tabData(activeIndex)["object"]
        tab_content = self.findChild(QWidget, tab_name).content

        tab_content.forward()

    def ReloadPage(self):
        activeIndex = self.tabbar.currentIndex()
        tab_name = self.tabbar.tabData(activeIndex)["object"]
        tab_content = self.findChild(QWidget, tab_name).content

        tab_content.reload()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Enable DevTools
    #os.environ['QTWEBENGINE_REMOTE_DEBUGGING'] = "667"
    window = App()

    with open("style.css", "r") as style:
        app.setStyleSheet(style.read())

    window.show()
    sys.exit(app.exec_())
