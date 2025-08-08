import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dmarc",
    author="Dusan Obradovic",
    author_email="dusan@euracks.net",
    description="DMARC library and milter module implemented in Python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    url="https://gitlab.com/duobradovic/pydmarc",
    packages=setuptools.find_packages(),
    package_data={"dmarc": ["report/schemas/*.xsd", "tests/report/data/*.xml"]},
    keywords = ['dkim', 'spf', 'dmarc', 'email', 'authentication', 'milter', 'rfc7489', 'rfc8601'],
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Communications :: Email :: Mail Transport Agents",
        "Topic :: Communications :: Email :: Filters",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires='>=3.9',
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    extras_require={
        "resolver": ['dnspython'],
        "ar": ['authres'],
        "psl": ['publicsuffix2'],
        "report": ['xmlschema'],
        "milter": ['dnspython', 'authres', 'publicsuffix2', 'purepythonmilter', 'click', 'pyspf']
    },
)
