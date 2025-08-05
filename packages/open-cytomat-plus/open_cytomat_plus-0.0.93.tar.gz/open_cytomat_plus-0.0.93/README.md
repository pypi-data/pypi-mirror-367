# open-cytomat-plus

## For End-User

## For Contributers

### Update the run_gui.exe file:
- open bash or shell
```bash
#change direction to open-cytomat-plus
#if virtual enviroment does not exists:
	# create venv: 
	python -m venv venv
#activate venv: 
venv\Scripts\activate
#if pyinstaller is not installed:
	pip install pyinstaller
cd src
#create .exe file: 
pyinstaller run_gui.spec
#new .exe file located in src/dist
```

### Update pip version:
- open bash shell
```bash
# change direction to open-cytomat-plus
# if virtual enviroment does not exists:
	# create venv: 
	python -m venv venv
#activate venv: 
venv\Scripts\activate
# if twine is not installed:
	pip install twine
# update the version pyproject.toml file
poetry build
twine uplaod dist\*
# enter api token
```