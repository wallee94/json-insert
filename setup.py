import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="json_insert",
    version="0.1.0",
    author="Walther Lee",
    author_email="walthere.lee@gmail.com",
    description="Add new keys to a json stream without storing it in memory.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wallee94/json-insert",
    packages=setuptools.find_packages(),
    install_requires=[],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
