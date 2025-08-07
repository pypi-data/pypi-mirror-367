from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
	long_description = f.read()

setup(
	name="logairy",
	version="0.0.2",
	author="Your Name",
	author_email="syntector@gmail.com",
	description="Reserved package name for future development.",
	long_description=long_description,
	long_description_content_type="text/markdown",
	packages=find_packages(),
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	python_requires=">=3.6",
)
