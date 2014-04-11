from setuptools import setup, find_packages

pip_reqs = []
with open('requirements.txt') as f:
    pip_reqs = [str(l).strip() for l in f.readlines()]

setup(
    name="pystradamus",
    version="0.1.0",
    author="Trey Stout",
    author_email="trey@handshake.com",
    scripts=[],
    url="http://nowhere",
    license=open("LICENSE.txt").read(),
    description="Evidence-based scheduling tool for Jira",
    long_description=open('README.rst').read(),
    install_requires=pip_reqs,
    packages = find_packages('.'),
    package_data = {'pystradamus': ['etc/*cfg']},
    include_package_data=True,
    entry_points = {
        'console_scripts': ['pystradamus=pystradamus.command_line:main'],
        },
)

