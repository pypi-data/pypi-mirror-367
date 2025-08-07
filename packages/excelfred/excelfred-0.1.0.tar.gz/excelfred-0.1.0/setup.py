from setuptools import setup

setup(
    name='excelfred',
    version='0.0.1',
    py_modules=['excelfred'],
    author='Samuel Raj P (FRED)',
    author_email='your@email.com',
    description='A beginner-friendly Excel functions library in Python',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/excelfred',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License'
    ],
    install_requires=[
        'pandas',
        'numpy'
    ]
)
