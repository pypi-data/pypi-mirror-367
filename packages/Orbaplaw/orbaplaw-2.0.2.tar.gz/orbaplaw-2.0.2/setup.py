from setuptools import setup, find_packages

__version__ = "2.0.2"

setup(
		name = "Orbaplaw",
		version = __version__,
		author = "FreemanTheMaverick",
		description = "Orbital alignment analysis for plane wave basis sets",
		long_description = open("README.md").read(),
		long_description_content_type = "text/markdown",
		url = "https://github.com/FreemanTheMaverick/Orbaplaw.git",
		packages = find_packages(),
		entry_points = { "console_scripts": [
			"orbaplaw = Orbaplaw.main:main"
		]},
		install_requires = ["numpy", "scipy", "pyscf", "Maniverse>=1.0.0", "libmwfn"],
		python_requires = ">=3.10",
		classifiers = ["Programming Language :: Python :: 3"]
)
