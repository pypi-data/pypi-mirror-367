from setuptools import setup

with open("README.md", "r", encoding='utf-8') as arq:
    readme = arq.read()

setup(
    name='base_ouro',
    version='12.0',
    author='Gabriel Ernesto Barboza Pereira',
    author_email='ernesto.gabriel@pucpr.br',
    packages=['base_ouro'],
    description='Conversor utilizado para a geração da Base Ouro',
    long_description=readme,
    long_description_content_type='text/markdown',
    license='MIT',
    keywords='conversor base_ouro',
)
