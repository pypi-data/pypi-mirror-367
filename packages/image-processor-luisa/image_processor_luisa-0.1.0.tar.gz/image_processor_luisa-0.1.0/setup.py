from setuptools import setup, find_packages

setup(
    name='image-processor-luisa',  # Nome único no PyPI
    version='0.1.0',               # Versão inicial
    author='Luísa',
    author_email='seu@email.com',
    description='Pacote simples de processamento de imagens com Pillow',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/seuusuario/image-processor',  # Substitua com o link do seu repositório, se tiver
    packages=find_packages(),
    install_requires=[
        'Pillow>=9.0.0',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
