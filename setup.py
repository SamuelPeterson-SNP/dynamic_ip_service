import setuptools
import os

HERE = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(HERE,"README.rst"),"r") as f:
    long_description = f.read()

setuptools.setup(
    name = "IP Updater",

    version = "0.1.0",

    description = "Ip updater for simple home server hosted by godaddy",

    long_description = long_description,

    author = "Samuel Peterson",

    author_email = "sam.houston.peterson@gmail.com",

    license = "MIT",

    include_package_data = True,

    classifiers = [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Schmaaa!",
        "Topic :: Dynamic IP Hosting",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.5"
    ],

    keywords = "dynamic-ip godaddy",

    packages = setuptools.find_packages(),

    entry_points = {
        'console_scripts': [
            'ip_update=dynamic_ip.ip_lookup:main',
            'ip_init_db=dynamic_ip.ip_lookup:initialize_db'
        ]
    }


)


