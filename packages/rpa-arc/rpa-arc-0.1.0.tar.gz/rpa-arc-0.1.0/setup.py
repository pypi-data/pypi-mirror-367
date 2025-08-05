from setuptools import setup, find_packages


setup(
    name="rpa-arc",
    version="0.1.0",
    description="CLI para gerar estrutura de projetos RPA com padrão definido",
    author="Seu Nome",
    author_email="seu@email.com",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    install_requires=[
        "requests",
        "python-dotenv",
        "selenium",
        "webdriver-manager"
    ],
    entry_points={
        "console_scripts": [
            "rpa-arc = src.rpa_arc.cli:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)