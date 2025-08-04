from setuptools import setup, find_packages

setup(
    name='chronolog-service',
    version='1.0.1',
    author='Lucas Simopoulos',
    author_email='lucas@loopcv.com',
    description='Chronolog: Log microservice version to Redis at startup',
    long_description=open("README.md").read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/chronolog',
    packages=find_packages(),
    install_requires=['redis>=4.0.0'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.7',
)
