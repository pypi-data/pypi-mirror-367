from setuptools import setup, find_packages

setup(
    name='jafrt',
    version='0.1.0',
    author='نام شما',
    author_email='email@example.com',
    description='کتابخانه که توسط hetx زده شده',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/ندارم/jafrt',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    keywords='python example library',
)