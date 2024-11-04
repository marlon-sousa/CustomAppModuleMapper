# -*- coding: UTF-8 -*-
# A part of the EnhancedDictionaries addon for NVDA
# Copyright (C) 2020 Marlon Sousa
# This file is covered by the GNU General Public License.
# See the file COPYING.txt for more details.

import addonHandler
import appModules
import appModuleHandler
from gui import guiHelper
import wx
import gui
import gui.settingsDialogs

addonHandler.initTranslation()


class CustomAppModuleMapperSettingPanel(gui.settingsDialogs.SettingsPanel):
    # Translators: This is the label for the Custom Application Module Mapper settings category in NVDA Settings screen. # noqa E501
    title = _("Custom Application Module Mapper")

    def makeSettings(self, settingsSizer):
        sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
        # Translators: label used to toggle the auto check update.
        self.mappingsList = sHelper.addLabeledControl(_("Mappings"), wx.ListCtrl, style=wx.LC_REPORT)
        self.mappingsList.InsertColumn(0, _("App Name"))
        self.mappingsList.InsertColumn(1, _("Module Name"))
        actionsHelper = guiHelper.BoxSizerHelper(self, orientation=wx.HORIZONTAL)
        # Translators: This is the button to check for new updates of the add-on.
        self.addButton = actionsHelper.addItem(wx.Button(self, label=_("&Add mapping")))
        # Translators: This is the label for the IBMTTS folder address.
        self.removeButton = actionsHelper.addItem(wx.Button(self, label=_("&Remove mapping")))
        sHelper.addItem(actionsHelper)
        settingsSizer.Fit(self)
        self.bindEvents()

    def bindEvents(self):
        self.addButton.Bind(wx.EVT_BUTTON, self.onAdd)
        self.removeButton.Bind(wx.EVT_BUTTON, self.onRemove)

    def _getAllAvailableAppModules(self):
        modules = list(appModuleHandler._executableNamesToAppModsAddons.values()) + \
            list(appModules.EXECUTABLE_NAMES_TO_APP_MODS.values())
        return sorted(set(modules))

    def onAdd(self, evt):
        title = _("add mapping")
        gui.mainFrame.prePopup()
        dialog = ModuleMappingDialog(self, title, self._getAllAvailableAppModules())
        if dialog.ShowModal() == wx.ID_OK:
            self.mappingsList.Append((dialog.app, dialog.appModule))
            appModuleHandler.registerExecutableWithAppModule(dialog.app, dialog.appModule)
            appModuleHandler.terminate()
            appModuleHandler.initialize()
        dialog.Destroy()
        gui.mainFrame.postPopup()

    def onRemove(self, evt):
        pass

    def onSave(self):
        pass


class ModuleMappingDialog(
    gui.contextHelp.ContextHelpMixin,
    wx.Dialog,  # wxPython does not seem to call base class initializer, put last in MRO
):

    # Translators: This is the label for the edit dictionary entry dialog.
    def __init__(self, parent, title, availableModules):
        super(ModuleMappingDialog, self).__init__(parent, title=title)
        self.app = None
        self.appModule = None
        self.availableModules = availableModules
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        sHelper = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)

        # Translators: label test for app field in add mapping dialog
        appLabelText = _("&App")
        self.AppTextCtrl = sHelper.addLabeledControl(appLabelText, wx.TextCtrl)

        # Translators: label test for app module field in add mapping dialog
        appModuleLabelText = _("App &module")
        appLabel = wx.StaticText(self, label=appModuleLabelText)
        self.appModulesComboBox = wx.ComboBox(self, choices=self.availableModules, style=wx.CB_READONLY)
        sHelper.addItem(appLabel)
        sHelper.addItem(self.appModulesComboBox)

        sHelper.addDialogDismissButtons(wx.OK | wx.CANCEL, separated=True)

        mainSizer.Add(sHelper.sizer, border=guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
        mainSizer.Fit(self)
        self.SetSizer(mainSizer)
        self.AppTextCtrl.SetFocus()
        self.Bind(wx.EVT_BUTTON, self.onOk, id=wx.ID_OK)

    def onOk(self, evt):
        self.app = self.AppTextCtrl.GetValue()
        self.appModule = self.appModulesComboBox.GetValue()
        evt.Skip()
