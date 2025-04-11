# -*- coding: utf-8 -*-
from burp import IBurpExtender, IHttpListener, ITab
from javax.swing import (
    JPanel, JButton, JTextArea, JScrollPane, JLabel,
    BoxLayout, JTextField
)
from java.awt import Component, Color
from java.awt.event import ActionListener
import random
import os

class BurpExtender(IBurpExtender, IHttpListener, ITab, ActionListener):

    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        self._callbacks.setExtensionName("UA Rotator")

        self.enabled = False
        self.last_used = "-"
        self.storage_file = os.path.join(os.getcwd(), "uas_list.txt")

        # Load UAs from file or defaults
        self.user_agents = self.load_user_agents()

        # -- UI Setup --
        self.panel = JPanel()
        self.panel.setLayout(BoxLayout(self.panel, BoxLayout.Y_AXIS))

        self.status_label = JLabel("Status: Disabled | Active UAs: %d | Last Used: -" % len(self.user_agents))
        self.status_label.setForeground(Color.RED)
        self.status_label.setAlignmentX(Component.CENTER_ALIGNMENT)
        self.panel.add(self.status_label)

        self.toggle_button = JButton("Enable UA Rotation", actionPerformed=self.toggle_rotation)
        self.toggle_button.setAlignmentX(Component.CENTER_ALIGNMENT)
        self.panel.add(self.toggle_button)

        self.ua_area = JTextArea("\n".join(self.user_agents), 10, 60)
        self.panel.add(JScrollPane(self.ua_area))

        self.apply_button = JButton("Apply Changes", actionPerformed=self.apply_changes)
        self.reset_button = JButton("Reset to Smart Defaults", actionPerformed=self.reset_defaults)
        self.panel.add(self.apply_button)
        self.panel.add(self.reset_button)

        self._callbacks.customizeUiComponent(self.panel)
        self._callbacks.addSuiteTab(self)
        self._callbacks.registerHttpListener(self)

        print("[+] UA Rotator by [bugcrowd.com/sh0a1b] successfully loaded.")

    def getTabCaption(self):
        return "UA Rotator"

    def getUiComponent(self):
        return self.panel

    def toggle_rotation(self, event):
        self.enabled = not self.enabled
        if self.enabled:
            self.toggle_button.setText("Disable UA Rotation")
            self.status_label.setText("Status: Enabled | Active UAs: %d | Last Used: %s" % (len(self.user_agents), self.last_used))
            self.status_label.setForeground(Color.GREEN)
        else:
            self.toggle_button.setText("Enable UA Rotation")
            self.status_label.setText("Status: Disabled | Active UAs: %d | Last Used: -" % len(self.user_agents))
            self.status_label.setForeground(Color.RED)

    def apply_changes(self, event):
        raw_text = self.ua_area.getText()
        self.user_agents = [ua.strip() for ua in raw_text.split("\n") if ua.strip()]
        self.save_user_agents()
        self.status_label.setText("Status: %s | Active UAs: %d | Last Used: %s" % (
            "Enabled" if self.enabled else "Disabled",
            len(self.user_agents),
            self.last_used if self.enabled else "-"
        ))
        print("[+] UA list updated. %d entries loaded." % len(self.user_agents))

    def reset_defaults(self, event):
        self.user_agents = self.default_user_agents()
        self.ua_area.setText("\n".join(self.user_agents))
        self.save_user_agents()
        print("[*] Reset to smart defaults.")

    def processHttpMessage(self, toolFlag, messageIsRequest, messageInfo):
        if not self.enabled or not messageIsRequest:
            return

        req_info = self._helpers.analyzeRequest(messageInfo)
        headers = list(req_info.getHeaders())
        body = messageInfo.getRequest()[req_info.getBodyOffset():]

        ua = random.choice(self.user_agents)
        self.last_used = ua

        # Replace or add UA header
        new_headers = []
        ua_found = False
        for h in headers:
            if h.lower().startswith("user-agent:"):
                new_headers.append("User-Agent: " + ua)
                ua_found = True
            else:
                new_headers.append(h)
        if not ua_found:
            new_headers.append("User-Agent: " + ua)

        new_req = self._helpers.buildHttpMessage(new_headers, body)
        messageInfo.setRequest(new_req)
        messageInfo.setComment("[UA ROTATED]: " + ua)

        self.status_label.setText("Status: Enabled | Active UAs: %d | Last Used: %s" % (len(self.user_agents), ua))

    def load_user_agents(self):
        try:
            with open(self.storage_file, "r") as f:
                return [line.strip() for line in f.readlines() if line.strip()]
        except:
            return self.default_user_agents()

    def save_user_agents(self):
        try:
            with open(self.storage_file, "w") as f:
                for ua in self.user_agents:
                    f.write(ua + "\n")
        except Exception as e:
            print("[!] Failed to save UA list: %s" % e)

    def default_user_agents(self):
        return [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 Chrome/90.0.4430.210 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6) AppleWebKit/605.1.15 Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:68.0) Gecko/20100101 Firefox/68.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Trident/7.0; rv:11.0 like Gecko",
    "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 Chrome/84.0.4147.89 Mobile Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Edge/90.0.818.62",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.85 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/14.0 Mobile/8A293 Safari/6533.18.5",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Linux; Android 11; Samsung Galaxy S21) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/90.0.818.66 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; OnePlus 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0",
    "Mozilla/5.0 (Linux; Android 9; Xiaomi Mi 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; rv:107.0) Gecko/20100101 Firefox/107.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 8.0; Samsung Galaxy S8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36 Edge/87.0.664.75",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; Trident/7.0; AS; .NET4.0C; .NET4.0E; en-US) like Gecko",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36"
]

