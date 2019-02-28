from setuptools import setup

setup(
    name='notification-system',
    version='0.1',
    author='CZ.NIC, z.s.p.o. (http://www.nic.cz/)',
    author_email='packaging@turris.cz',
    packages=['notifylib'],
    url='https://gitlab.labs.nic.cz/turris/notification-system',
    license='COPYING',
    description='Notification system NG',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    package_data={
        '': [
            "plugins/**/*.yml",
            "plugins/**/templates/*.j2",
        ]
    },
    install_requires=[
        'Jinja2',
        'PyYAML',
    ],
    setup_requires=[
        'babel',
    ],
    entry_points={
        "console_scripts": [
            "notify-cli = notifylib.__main__:main",
            "create_notification = notifylib.legacy_create:main",
            "list_notifications = notifylib.legacy_list:main",
        ]
    },
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries',
    ],
    zip_safe=False,
)
