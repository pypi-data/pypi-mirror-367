"""
Setup configuration for gradient-cache package

This file defines how the package is built and installed. It specifies
dependencies, package metadata, and entry points for the system.
"""

from setuptools import setup, find_packages
import os

# Read the README for long description
def read_readme():
    """Load README.md for use as long description."""
    if os.path.exists('README.md'):
        with open('README.md', 'r', encoding='utf-8') as f:
            return f.read()
    return ''

# Read version from package
def get_version():
    """Extract version from __init__.py."""
    init_file = os.path.join('gradient_cache', '__init__.py')
    if os.path.exists(init_file):
        with open(init_file, 'r') as f:
            for line in f:
                if line.startswith('__version__'):
                    return line.split('=')[1].strip().strip('"\'')
    return '0.1.0'

setup(
    name='gradient-cache',
    version=get_version(),
    author='Gradient Cache Contributors',
    author_email='',
    description='GPU memory-efficient training with gradient compression for PyTorch',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/gradient-cache/gradient-cache',
    project_urls={
        'Bug Tracker': 'https://github.com/gradient-cache/gradient-cache/issues',
        'Documentation': 'https://github.com/gradient-cache/gradient-cache/wiki',
        'Source Code': 'https://github.com/gradient-cache/gradient-cache',
    },
    
    # Package configuration
    packages=find_packages(exclude=['tests*', 'benchmarks*', 'examples*']),
    include_package_data=True,
    
    # Python version requirement
    python_requires='>=3.8',
    
    # Core dependencies
    install_requires=[
        'torch>=2.0.0',          # PyTorch for deep learning
        'numpy>=1.20.0',         # Numerical operations
        'metaflow>=2.7.0',       # Metaflow integration (optional but included for compatibility)
    ],
    
    # Optional dependencies for different use cases
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=3.0.0',
            'black>=22.0.0',
            'isort>=5.0.0',
            'flake8>=4.0.0',
            'mypy>=0.950',
        ],
        'benchmarks': [
            'transformers>=4.30.0',  # For GPT-2 benchmarks
            'psutil>=5.9.0',         # System monitoring
            'gputil>=1.4.0',         # GPU monitoring
            'matplotlib>=3.5.0',     # Plotting results
            'pandas>=1.4.0',         # Data analysis
        ],
        'docs': [
            'sphinx>=4.5.0',
            'sphinx-rtd-theme>=1.0.0',
            'myst-parser>=0.17.0',
        ],
    },
    
    # Classification metadata
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
        'Environment :: GPU :: NVIDIA CUDA',
    ],
    
    # Entry points for command-line tools
    entry_points={
        'console_scripts': [
            'gradient-cache-benchmark=benchmarks.run_benchmark:main',
        ],
    },
    
    # Keywords for package discovery
    keywords=[
        'deep learning',
        'pytorch',
        'gpu memory',
        'gradient compression',
        'machine learning',
        'memory optimization',
        'training efficiency',
        'neural networks',
    ],
    
    # License
    license='Apache License 2.0',
    
    # Additional package data
    package_data={
        'gradient_cache': ['py.typed'],  # Include type hints
    },
)