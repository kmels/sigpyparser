import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sigpyparser",
    version="0.0.2",
    author="Carlos Eduardo López Camey",
    author_email="carlos@kmels.net",
    description="Extract market signals from text",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kmels/sigpyparser",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Office/Business :: Financial :: Investment',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Operating System :: OS Independent',
    ],
    packages=setuptools.find_packages(exclude=['tests']),
    package_data={
        'squawk': ['Lucy/*.wav, Rachel/*.wav'],
    },
    python_requires='>=3.3',
    entry_points={'squawk': ['squawk=squawk:drive']},
    project_urls={
        'Bug Reports': 'https://github.com/kmels/sigpyparser/issues',
        'Funding': 'https://donate.pypi.org',
        'Say Thanks!': 'https://saythanks.io/to/kmels',
        'Source': 'https://github.com/kmels/sigpyparser/',
    },
    test_suite="tests"
)
