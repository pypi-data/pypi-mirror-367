from setuptools import find_packages, setup

setup(
    name='netbox-cvexplorer',
    version='1.0.13',
    description='CVE Explorer Plugin for NetBox',
    author='Tino Schiffel',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
