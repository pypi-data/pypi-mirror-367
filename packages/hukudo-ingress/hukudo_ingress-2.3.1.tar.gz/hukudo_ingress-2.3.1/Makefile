MAKEFLAGS += --always-make

default: pre-commit ty test

pre-commit:
	pre-commit run --all-files

ty:
	ty check .

test:
	pytest --doctest-modules --cov=. --cov-report=html --cov-report=term --cov-report=xml

clean:
	rm -rf build/ dist/

build:
	python -m build --installer=uv

patch_release: clean test
	bump2version patch
	make build push_with_tags upload

minor_release: clean test
	bump2version minor
	make build push_with_tags upload

major_release: clean test
	bump2version major
	make build push_with_tags upload

push_with_tags:
	git push
	git push --tags

upload:
	twine upload --repository pypi dist/*

requirements.txt:
	pip-compile
