from setuptools import setup, find_packages

setup(
    name='lda4microbiome',
    version='0.1.1',
    author='Your Name',
    author_email='your.email@example.com',
    description='A workflow for LDA analysis of microbiome data using MALLET',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/lda4microbiome',  # Update this to your URL
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    install_requires=[
        'pandas',
        'numpy',
        'matplotlib',
        'seaborn',
        'gensim',
        'little-mallet-wrapper',
    ],
)

