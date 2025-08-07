from setuptools import setup, find_packages

with open("README.md", "r", encoding = "utf-8") as fh:
    long_description = fh.read()

setup(
    name = 'pyclimaterisk',
    author = 'Muhsin Ciftci',
    version = '1.1.1',
    packages = find_packages(),
    author_email = 'farmer.muhsin@gmail.com',
    description = 'This package provides climate risk data derived from newspapers data',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    license = "MIT",
    url = "https://github.com/muhsinciftci/pyclimaterisk",
    keywords = ['Climate', 'Risk', 'Newspapers', 'Finance'],
    package_data = { 'pyclimaterisk': ['data/*.pq'] },
    install_requires=['polars>=1.0.0']
)

