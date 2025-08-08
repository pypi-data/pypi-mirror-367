from setuptools import setup, find_packages

setup(
    name='niksms',
    version='0.1.2',
    description='Python SDK for Kendez.NikSms SMS Web Service (REST & gRPC)',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Kendez',
    author_email='info@kendez.com',
    url='https://webservice.niksms.com',
    packages=find_packages(),
    install_requires=[
        'requests',
        'grpcio',
        'protobuf',
    ],
    python_requires='>=3.7',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    include_package_data=True,
) 