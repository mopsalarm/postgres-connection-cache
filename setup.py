#!/usr/bin/env python3

from distutils.core import setup

setup(name="pcc",
      version="1.0.0",
      description="A simple connection cache for postgres that refreshes connections from time to time.",
      author="Mopsalarm",
      author_email="mopsalarm.pr0gramm@gmx.de",
      url="https://github.com/mopsalarm/postgres-connection-cache",
      requires=["psycopg2"],
      packages=["pcc"],

      license='MIT',
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.4',
      ])
