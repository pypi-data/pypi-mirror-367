from setuptools import setup, find_packages

setup(
    name='Classy-AI',
    version='0.0.15',
    packages=find_packages(),
    install_requires=[
        'torch',
        'openai',
        'numpy',
        'Search-Scrape',
        'nltk',
        'sentence-transformers'
    ],
    # other metadata
    author='eedeb',
    author_email='123scoring@gmail.com',
    description="A python module that utilizes AI to classify natural language into categories for processing with other models.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/eedeb/Classy',
    classifiers=[
        'Programming Language :: Python :: 3',
        # other classifiers
    ],
)
