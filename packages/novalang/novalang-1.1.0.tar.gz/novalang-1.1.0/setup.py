from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='novalang',
    version='1.1.0',
    description='NovaLang - The Full-Stack Programming Language with Universal IDE Support',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='martinmaboya',
    author_email='martinmaboya@gmail.com',
    url='https://github.com/martinmaboya/novalang',
    packages=find_packages(),
    py_modules=[
        'main',
        'lexer', 
        'parser',
        'interpreter',
        'stdlib',
        'array_assign_node',
        'array_nodes',
        'for_node',
        'nova'
    ],
    entry_points={
        'console_scripts': [
            'novalang = main:main',
            'nova = nova:main',
            'novalang-lsp = novalang.lsp_server:main'
        ]
    },
    install_requires=[
        'argparse>=1.4.0',
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Interpreters",
        "Topic :: Software Development :: Compilers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    keywords="programming-language full-stack enterprise web mobile desktop interpreter compiler lsp language-server ide-support universal-ide",
    project_urls={
        "Bug Reports": "https://github.com/martinmaboya/novalang/issues",
        "Source": "https://github.com/martinmaboya/novalang",
        "Documentation": "https://martinmaboya.github.io/novalang",
        "VS Code Extension": "https://marketplace.visualstudio.com/items?itemName=martinmaboya.novalang",
        "Language Server": "https://github.com/martinmaboya/novalang/tree/master/extensions/language-server",
    }
)
