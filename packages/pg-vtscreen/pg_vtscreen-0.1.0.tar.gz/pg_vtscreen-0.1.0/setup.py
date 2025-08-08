from setuptools import setup, find_packages

setup(
    name="pg_vtscreen",
    version="0.1.0",
    packages=find_packages(),
    author="NHSU",
    author_email="lxp20100205@126.com",
    description="A virtual screen manager for Pygame that handles window scaling and fullscreen functionality",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pg_vtscreen",  # Replace with your actual repo URL
    install_requires=["pygame>=2.0.0"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Games/Entertainment",
        "Topic :: Software Development :: Libraries :: pygame",
    ],
    python_requires=">=3.6",
)
