.PHONY: hello
hello:
	@pipenv run echo hello, are you looking for test?

.PHONY: deps
deps:
	pipenv install --dev

.PHONY: test
test:
	pipenv run pytest -vv --cov=edge_auth --cov-report=term --cov-report=xml
