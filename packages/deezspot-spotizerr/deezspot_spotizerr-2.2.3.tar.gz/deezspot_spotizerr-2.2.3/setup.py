from setuptools import setup, find_packages

README = open("README.md", "r")
readmed = README.read()
README.close()

setup(
	name = "deezspot-spotizerr",
    version = "2.2.3",
	description = "Spotizerr's implementation of deezspot",
	long_description = readmed,
	long_description_content_type = "text/markdown",
	license = "GNU Affero General Public License v3",
	python_requires = ">=3.10",
	author = "jakiepari",
	author_email = "farihmuhammad75@gmail.com",
	url = "https://github.com/jakiepari/deezspot",

	packages = find_packages(include=["deezspot", "deezspot.*"]),

        install_requires = [
                "mutagen", "pycryptodome", "requests",
                "spotipy", "tqdm", "fastapi",
                "uvicorn[standard]",
                "spotipy-anon",
                "librespot-spotizerr"
         ],
)
