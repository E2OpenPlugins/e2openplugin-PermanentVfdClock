from distutils.core import setup

pkg = 'Extensions.PermanentVfdClock'
setup(name='enigma2-plugin-extensions-permanentvfdclock',
	version='1.0',
	description='Show clock in VFD permanently',
	packages=[pkg],
	package_dir={pkg: 'plugin'}
)
