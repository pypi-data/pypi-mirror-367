from setuptools import setup, find_packages

setup(
    name="nabeelxd",
    version="0.1.1",
    description="Fetch and run/save Python scripts from GitHub.",
    author="Nabeel",
    author_email="your-email@example.com",
    url="https://github.com/nabeelxdd/pip-nabeelxd",
    packages=find_packages(),
    install_requires=["requests"],
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.6",
)