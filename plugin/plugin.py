from Components.config import config, ConfigSubsection, getConfigListEntry, ConfigBoolean, ConfigInteger
from Components.Sources.StaticText import StaticText
from Components.ConfigList import ConfigListScreen
from enigma import eTimer, iPlayableService
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen

gTimer = ''

config.plugins.PermanentVfdClock = ConfigSubsection()
config.plugins.PermanentVfdClock.enabled = ConfigBoolean(default = False)
config.plugins.PermanentVfdClock.timeonly = ConfigBoolean(default = False)
config.plugins.PermanentVfdClock.refreshrate = ConfigInteger(default = 15, limits = (1,60))
config.plugins.PermanentVfdClock.holdofftime = ConfigInteger(default = 5, limits = (1,60))

VFD_PATH = '/dev/dbox/oled0'

class PermanentVfdClock(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		from Components.ServiceEventTracker import ServiceEventTracker
		self.__event_tracker = ServiceEventTracker(screen = self, eventmap =
		{
			iPlayableService.evStart: self.serviceChanged,
		})
		global gTimer
		gTimer = eTimer()
		gTimer.callback.append(self.timeCallback)
		self.startTimer(config.plugins.PermanentVfdClock.refreshrate.value)

	def startTimer(self, val):
		global gTimer
		gTimer.start((val * 1000), True)

	def timeCallback(self):
		from Screens.Standby import inStandby
		if not inStandby:
			if config.plugins.PermanentVfdClock.enabled.value is True:
				from time import localtime
				t = localtime()
				vfd = open(VFD_PATH, "w")
				if config.plugins.PermanentVfdClock.timeonly.value is True:
					vfd.write("   %2d:%02d" % (t.tm_hour, t.tm_min))
				else:
					vfd.write("%2d:%02d %d/%d" % (t.tm_hour, t.tm_min, t[2], t[1]))
				vfd.close()
		self.startTimer(config.plugins.PermanentVfdClock.refreshrate.value)

	def serviceChanged(self):
		self.startTimer(config.plugins.PermanentVfdClock.holdofftime.value)

class PermanentVfdClockMenu(Screen, ConfigListScreen):
	skin = """
	<screen position="c-300,c-100" size="600,200" title="Permanent VFD clock config">
		<widget name="config" position="25,25" size="e-50,e-50" />
		<ePixmap pixmap="skin_default/buttons/red.png" position="20,e-45" size="140,40" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/green.png" position="160,e-45" size="140,40" alphatest="on" />
		<widget source="key_red" render="Label" position="20,e-45" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
		<widget source="key_green" render="Label" position="160,e-45" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
	</screen>"""

	def __init__(self, session):
		self.skin = PermanentVfdClockMenu.skin
		self.session = session
		Screen.__init__(self, session)
		from Components.ActionMap import ActionMap
		from Components.Button import Button
		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("OK"))
		self["actions"] = ActionMap(["SetupActions", "ColorActions"],
		{
			"ok": self.keyGo,
			"save": self.keyGo,
			"cancel": self.keyCancel,
			"green": self.keyGo,
			"red": self.keyCancel,
		}, -2)
		self.list = []
		ConfigListScreen.__init__(self, self.list, session = self.session)
		self.list.append(getConfigListEntry(_("Activate permanent VFD clock"), config.plugins.PermanentVfdClock.enabled))
		self.list.append(getConfigListEntry(_("Show time only"), config.plugins.PermanentVfdClock.timeonly))
		self.list.append(getConfigListEntry(_("VFD clock refresh interval time"), config.plugins.PermanentVfdClock.refreshrate))
		self.list.append(getConfigListEntry(_("VFD clock holdoff time"), config.plugins.PermanentVfdClock.holdofftime))
		self["config"].list = self.list
		self["config"].l.setList(self.list)

	def keyLeft(self):
		ConfigListScreen.keyLeft(self)

	def keyRight(self):
		ConfigListScreen.keyRight(self)

	def keyGo(self):
		for x in self["config"].list:
			x[1].save()
		self.close()

	def keyCancel(self):
		for x in self["config"].list:
			x[1].cancel()
		self.close()


def autostart(reason, **kwargs):
	PermanentVfdClock(kwargs["session"])


def main(session, **kwargs):
	session.open(PermanentVfdClockMenu)

def Plugins(**kwargs):
	from os import path
	if path.exists(VFD_PATH):
		return [PluginDescriptor(where = [PluginDescriptor.WHERE_SESSIONSTART], fnc = autostart), \
				PluginDescriptor(name = _("Permanent VFD Clock"), description = _("Show permanent clock in VFD"), where = PluginDescriptor.WHERE_PLUGINMENU, icon = "plugin.png",fnc = main) ]
