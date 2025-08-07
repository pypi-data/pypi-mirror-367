from setuptools import setup, find_packages

setup(
    name="diixscreendata",
    version="0.1.1",
    description="Biblioteca Python para coletar informações e modos de monitores via DLL Dix_ScreenInfo.dll",
    author="Dixavado",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "diixscreendata": ["dll/*.dll"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: System :: Hardware :: Hardware Drivers",
    ],
    python_requires=">=3.7",
    install_requires=[
        # Não tem dependências externas explícitas no seu código,
        # mas você pode listar aqui se precisar de algo.
    ],
    entry_points={
        # Se você quiser disponibilizar algum comando CLI, configure aqui
        # Exemplo:
        # 'console_scripts': [
        #     'diixscreen=diixscreendata.cli:main',
        # ],
    },
)
