from setuptools import setup, find_packages

setup(
    name="django-encrypted-fields-and-files",
    version="0.1.12",
    packages=find_packages(),
    install_requires=["Django>=4.2", "cryptography>=41.0.5,<45.0.0", "pillow>=10.0.0"],
    author="Denky",
    author_email="contato@denky.dev.br",
    description="Campos e storages criptografados para o Django com suporte a timestamp para evitar cache.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/D3NKYT0/django-encrypted-fields",
    project_urls={
        "Source": "https://github.com/D3NKYT0/django-encrypted-fields",
        "Homepage": "https://denky.dev.br/django-encrypted-fields",
        "Documentation": "https://github.com/D3NKYT0/django-encrypted-fields/wiki",
        "Issue Tracker": "https://github.com/D3NKYT0/django-encrypted-fields/issues",
    },
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Security :: Cryptography",
    ],
    python_requires=">=3.10",
    keywords="django, encryption, fields, files, timestamp, cache",
)
