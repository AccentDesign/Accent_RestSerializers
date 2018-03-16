.PHONY: test

test:
	flake8
	coverage erase
	PYTHONPATH=. coverage run ./manage.py test
	coverage combine
	coverage html
	coverage report