# Testing
As well as the app, test are run in docker containers. In these case, volumes are deleted once the containers are run. To test it is used the [pytest](https://docs.pytest.org/en/7.4.x/contents.html) tool. You can see in the [Makefile](Makefile.md) the following comand to run the tests:

```bash
make tests
```