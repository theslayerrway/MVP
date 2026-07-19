from setuptools import setup, find_packages

setup(
    name="evolve-mvp",
    version="0.1.0",
    description="Turn any project into a shipped MVP. Self-evolving, regression-gated methodology engine. Model-agnostic.",
    long_description=open("README.md").read() if __import__("os").path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.9",
    entry_points={"console_scripts": ["evolve-mvp=evolve_mvp.cli:main"]},
    license="MIT",
    keywords="mvp, ai, methodology, agent, product, lean-startup, premortem",
)
