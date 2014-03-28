from distutils.core import setup

pip_reqs = []
with open('requirements.txt') as f:
    pip_reqs = [str(l).strip() for l in f.readlines()]
print pip_reqs

setup(
        name="pystradamus",
        version="0.1.0",
        author="Trey Stout",
        author_email="trey@handshake.com",
        packages=["pystradamus"],
        scripts=[],
        url="http://nowhere",
        license="LICENSE.txt",
        description="Evidence-based scheduling tool for Jira",
        long_description=open('README.txt').read(),
        install_requires=pip_reqs,
        entry_points = {
            'console_scripts': ['pystradamus=pystradamus.command_line:main'],
            },
    )

