from setuptools import find_packages, setup
setup(
    name="mysite",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
    ],
)

#packages tells python what directories we need
#find_packages() does this automatically so you don't have to type it all out
#include_package_data includes other files like static and template directories

#need another file called MANIFEST.in to tell what the other data is