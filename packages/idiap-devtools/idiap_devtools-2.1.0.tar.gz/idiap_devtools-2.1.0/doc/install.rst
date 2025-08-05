.. Copyright © 2022 Idiap Research Institute <contact@idiap.ch>
..
.. SPDX-License-Identifier: BSD-3-Clause

.. _idiap-devtools.install:

==============
 Installation
==============

Installation may follow one of two paths: deployment or development. Choose the
relevant tab for details on each of those installation paths.


.. tab:: Deployment (pixi)

   Use pixi_ to add this package as a dependence:

   .. code:: sh

      pixi add idiap-devtools


.. tab:: Development

   Checkout the repository, and then use pixi_ to setup a full development
   environment:

   .. code:: sh

      git clone git@gitlab.idiap.ch:software/idiap-devtools
      pixi install --frozen

   .. tip::

      The ``--frozen`` flag will ensure that the latest lock-file available
      with sources is used.  If you'd like to update the lock-file to the
      latest set of compatible dependencies, remove that option.

      If you use `direnv to setup your pixi environment
      <https://pixi.sh/latest/features/environment/#using-pixi-with-direnv>`_
      when you enter the directory containing this package, you can use a
      ``.envrc`` file similar to this:

      .. code:: sh

         watch_file pixi.lock
         export PIXI_FROZEN="true"
         eval "$(pixi shell-hook)"


.. _idiap-devtools.install.running:

Running
-------

This package contains a single command-line executable named ``devtool``, which
in turn contains subcommands with various actions.  To run the main
command-line tool, use ``pixi run``:

.. code-block:: sh

   pixi run devtool --help


.. _idiap-devtools.install.setup:

Setup
-----

.. _idiap-devtools.install.setup.gitlab:

Automated GitLab interaction
============================

Some of the commands in the ``devtool`` command-line application require access
to your GitLab private token, which you can pass at every iteration, or setup
at your ``~/.python-gitlab.cfg``.  Please note that in case you don't set it
up, it will request for your API token on-the-fly, what can be cumbersome and
repeatitive.  Your ``~/.python-gitlab.cfg`` should roughly look like this
(there must be an "idiap" section on it, at least):

.. code-block:: ini

   [global]
   default = idiap
   ssl_verify = true
   timeout = 15

   [idiap]
   url = https://gitlab.idiap.ch
   private_token = <obtain token at your settings page in gitlab>
   api_version = 4


We recommend you set ``chmod 600`` to this file to avoid prying eyes to read
out your personal token. Once you have your token set up, communication should
work transparently between the built-in GitLab client and the server.

.. include:: links.rst
