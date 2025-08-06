import os
from setuptools import setup, find_packages

# Corrigindo o caminho do README.md para o diretório correto
this_directory = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(this_directory, '../README.md')
if not os.path.exists(readme_path):
    # Tenta buscar um nível acima, caso não exista no diretório atual
    readme_path = os.path.join(this_directory, 'README.md')

with open(readme_path, encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="privacyschema",
    version="0.3.0",
    description="Pluggable framework for personal data compliance (LGPD/GDPR)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Julio Amorim",
    author_email="julio@grupojpc.com.br",
    url="https://github.com/julioamorimdev/PrivacySchema",
    packages=find_packages(),
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries",
    ],
    python_requires=">=3.6",
    install_requires=[],
    include_package_data=True,
)