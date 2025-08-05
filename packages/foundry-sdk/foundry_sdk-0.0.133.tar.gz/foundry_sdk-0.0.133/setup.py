from pathlib import Path

from setuptools import find_packages, setup

here = Path(__file__).parent.resolve()
with (here / "requirements.txt").open() as f:
    requirements = f.read().splitlines()

setup(
    name="foundry-sdk",
    version="0.0.133",
    packages=find_packages(),
    package_dir={"": "."},
    install_requires=requirements,
)
