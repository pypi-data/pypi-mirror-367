from setuptools import setup, find_packages

setup(
    name="klefki-gen",  # use sempre letras minúsculas aqui para evitar problemas no PyPI
    version="1.0.5",
    description="Secure and customizable password generator.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Matheus Girardi",
    author_email="girardimatheus27@gmail.com",
    packages=find_packages(),
    install_requires=[
        "pyperclip"
    ],
    entry_points={
        "console_scripts": [
            "klefki=klefki_gen.__main__:cli"
        ]
    },
    python_requires=">=3.6",
    include_package_data=True,
    license="MIT",
    url="https://github.com/GirardiMatheus/Klefki",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Topic :: Security :: Cryptography",
        "Topic :: Utilities",
    ]
)