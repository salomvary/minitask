requirements.txt: pyproject.toml
	# --without-hashes is necessary as long as there is any dependency
	# not installed from PyPI: https://stackoverflow.com/a/50695493/759162
	poetry export --without-hashes > requirements.txt
