from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

setup(
    name="integrity_flow_custom",
    version="1.0.0",
    description="Custom ERPNext app for AAA Irrigation Service",
    author="Boatman Systems",
    author_email="info@aaairrigationservice.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires
)
