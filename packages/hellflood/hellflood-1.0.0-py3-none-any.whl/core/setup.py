from setuptools import setup, find_packages

setup(
    name='hellflood',
    version='1.0.0',
    author='Ali Jafari',
    author_email='thealiapi@gmail.com',
    description='Advanced DDOS Stress Testing Tool (For Educational Use Only)',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/iTs-GoJo/HellFlood',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Education',
        'Topic :: Security',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    keywords='ddos stress-test network security pentest',
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'hellflood = hellflood:main',
        ],
    },
    include_package_data=True,
    install_requires=[],
)
