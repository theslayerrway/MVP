from setuptools import setup, find_packages

setup(
    name="mvp-cli",
    version="0.1.0",
    author="theslayerrway",
    author_email="noreply@github.com",
    url="https://github.com/theslayerrway/MVP",
    long_description=open("README.md").read() if __import__("os").path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.9",
    entry_points={"console_scripts": ["evolve-mvp=evolve_mvp.cli:main"]},
    license="Apache-2.0",
    keywords="mvp, ai, methodology, agent, product, lean-startup, premortem",
)
