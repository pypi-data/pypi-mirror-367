from setuptools import setup, find_packages

setup(
    name="ff-flagfinder",
    version="1.0.1",
    description="FF-FlagFinder: Extract flags from authenticated pages using session, cookies, or headers.",
    author="[Ph4nt01]",
    author_email="ph4nt0.84@gmail.com",
    url="https://github.com/Ph4nt01/FF-FlagFinder",
    packages=find_packages(),
    install_requires=[
        "requests",
        "colorama"
    ],
    entry_points={
        "console_scripts": [
            "ff=ff.cli:grab_flag"
        ]
    },
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Topic :: Security",
        "Intended Audience :: Developers",
        "Environment :: Console"
    ],
)

