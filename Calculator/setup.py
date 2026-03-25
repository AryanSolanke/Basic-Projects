from setuptools import setup


ROOT_MODULES = [
    "calculator",
    "gui",
    "main",
    "standard",
    "scientific",
    "programmer",
    "router",
    "config",
    "exceptions",
    "utils",
]

SUBPACKAGES = [
    "converters",
    "programmer_parts",
    "scientific_parts",
]

setup(
    name="aryan-advanced-calculator",
    version="1.2.1",
    py_modules=ROOT_MODULES,
    packages=SUBPACKAGES,
    entry_points={
        "console_scripts": [
            "calculator=main:main",
        ],
    },
    python_requires=">=3.10",
    author="Aryan Solanke",
    description="Advanced modular calculator",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
)

