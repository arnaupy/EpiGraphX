# How to contribute?
There are two main fields in which you can contribute:

* Code -> [https://github.com/arnaupy/EpiGraphX/tree/develop/app](https://github.com/arnaupy/EpiGraphX/tree/develop/app)
* Documentation -> [https://github.com/arnaupy/EpiGraphX/tree/develop/docs](https://github.com/arnaupy/EpiGraphX/tree/develop/docs)

By default, you should work on an existing branch making pull request, but feel free to create your own branch from `develop`. In fact, links above redirect to the develop branch.

See the workflow for this project -> [Workflow](./dev-guide/Workflow.md)

## Clone repository and create environment
* Clone the project repository in you machine:
```
git clone https://github.com/arnaupy/EpiGraphX.git
```

* Set your `virtual environment`:
```
python -m venv env

# In mac you can use
python3 -m venv env
```

* Activate the virtual enviroment:
```
source ./env/bin/activate
```
* Install all the `requirements` for the app, documentation and testing:
```
pip install -r requirements.txt
```

## Contribute with code
First take a look at the code [arquitecture](./dev-guide/Architecture.md) that's been followed to develop code.

## Contribute with documentation
This project uses [mkdocs](https://www.mkdocs.org/) to work on the documentation. In specific it uses [material theme](https://squidfunk.github.io/mkdocs-material/). 

There are two main documentation fields:

* Developer -> [Developer Guide](./dev-guide/)
* User -> [User Guide](./user-guide/)

!!! warning
    At the moment user documentation is not available :pensive:

To see the changes your are making on the documentation, simply run the following comand, from the `root directory`, and access [http://127.0.0.1:8000/EpiGraphX/](http://127.0.0.1:8000/EpiGraphX/).
```
mkdocs serve
```



