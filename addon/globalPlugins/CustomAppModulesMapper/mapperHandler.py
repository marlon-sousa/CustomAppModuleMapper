# -*- coding: UTF-8 -*-
# A part of the CustomModulesMapper addon for NVDA
# Copyright (C) 2024 Marlon Sousa
# This file is covered by the MIT License.
# See the file COPYING.txt for more details.

import os
import pickle
import addonHandler
import appModules
import appModuleHandler
from logHandler import log
from dataclasses import dataclass
from typing import List


@dataclass
class Mapping:
	app: str
	appModule: str
	appOriginalModule: str


customModulesMapping: List[Mapping]


def getCustomModulesMapping():
	global customModulesMapping
	return customModulesMapping


def getAllConfiguredMappings() -> dict[str, str]:
	return appModules.EXECUTABLE_NAMES_TO_APP_MODS | appModuleHandler._executableNamesToAppModsAddons


def getAllAvailableAppModules() -> set[str]:
	mappings = getAllConfiguredMappings()
	return sorted(set(mappings.values()))


def associateAppModule(appName: str, moduleName: str):
	appModuleHandler.registerExecutableWithAppModule(appName, moduleName)


def disassociateAppModule(appName: str):
	appModuleHandler.unregisterExecutable(appName)


def restart():
	appModuleHandler.terminate()
	appModuleHandler.initialize._alreadyInitialized = False
	appModuleHandler.initialize()


def getCustomMappingsFilePath():
	addon = addonHandler.getCodeAddon()
	addonMainFolder = addon.path
	return os.path.join(addonMainFolder, "customModulesMapping.pickle")


def persist():
	with open(getCustomMappingsFilePath(), "wb") as f:
		pickle.dump(customModulesMapping, f)
	log.info("Custom mappings saved to file")


def loadCustomMappings():
	global customModulesMapping
	try:
		with open(getCustomMappingsFilePath(), "rb") as f:
			customModulesMapping = pickle.load(f)
		log.info("Custom mappings loaded from file")
		mustRestart = False
		for mapping in customModulesMapping:
			log.info(f"Associating {mapping.app} app with {mapping.appModule} module")
			associateAppModule(mapping.app, mapping.appModule)
			mustRestart = True
		if mustRestart:
			restart()
			log.info("Custom mappings applied")
	except FileNotFoundError:
		customModulesMapping = []
		log.info("Custom mappings created")
	except Exception as e:
		customModulesMapping = []
		log.error(f"Error loading custom mappings: {e}")
