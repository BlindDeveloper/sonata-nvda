# coding: utf-8

# Copyright (c) 2023 Musharraf Omer
# This file is covered by the GNU General Public License.

import os
import sys

import wx

import core
import gui
import globalPluginHandler
from logHandler import log

import addonHandler

addonHandler.initTranslation()


_DIR = os.path.abspath(os.path.dirname(__file__))
_ADDON_ROOT = os.path.abspath(os.path.join(_DIR, os.pardir, os.pardir))
_TTS_MODULE_DIR = os.path.join(_ADDON_ROOT, "synthDrivers")
sys.path.insert(0, _TTS_MODULE_DIR)
from piper_neural_voices import helpers as helpers
from piper_neural_voices.tts_system import (
    PiperTextToSpeechSystem,
    PIPER_VOICES_DIR,
)
sys.path.remove(_TTS_MODULE_DIR)


from .voice_galary import PiperVoiceGalaryDialog


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__voice_galary_shown = False
        self._voice_checker = lambda: wx.CallLater(3000, self._perform_voice_check)
        core.postNvdaStartup.register(self._voice_checker)
        self.itemHandle = gui.mainFrame.sysTrayIcon.menu.Insert(
            4,
            wx.ID_ANY,
            # Translators: label of a menu item
            _("Piper voice &galary..."),
            # Translators: Piper's voice galary menu item help
            _("Open the voice galary to preview and download piper voices"),
        )
        gui.mainFrame.sysTrayIcon.menu.Bind(wx.EVT_MENU, self.on_galary, self.itemHandle)

    def on_galary(self, event):
        galary_dialog = PiperVoiceGalaryDialog()
        gui.runScriptModalDialog(galary_dialog)
        self.__voice_galary_shown = True

    def _perform_voice_check(self):
        if self.__voice_galary_shown:
            return
        if not any(PiperTextToSpeechSystem.load_piper_voices_from_nvda_config_dir()):
            retval = gui.messageBox(
                # Translators: message telling the user that no voice is installed
                _(
                    "No Piper voice was found.\n"
                    "You can preview and download voices from the voice galary.\n"
                    "Do you want to open the voice galary now?"
                ),
                # Translators: title of a message telling the user that no Piper voice was found
                _("Piper Neural Voices"),
                wx.YES_NO | wx.ICON_WARNING,
            )
            if retval == wx.YES:
                self.on_galary(None)

    def terminate(self):
        try:
            gui.mainFrame.sysTrayIcon.menu.DestroyItem(self.itemHandle)
        except:
            pass
