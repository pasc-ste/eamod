format-check:
	python -m black --check eamod_spec tests;

format-diff:
	python -m black --diff eamod_spec tests;

format:
	python -m black eamod_spec tests

type-check:
	python -m mypy --follow-imports skip -p eamod_spec

code-analysis:
	python -m pylint --output-format=colorized eamod_spec --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" | tee pylint-report.txt

unit-test:
	python -m pytest -v -s tests --junitxml=pytest-report.xml

clean:
	rm -r pytest-report.xml pylint-report.txt; find . | grep -E "(__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf