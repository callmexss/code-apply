==========
Code Apply
==========


.. image:: https://img.shields.io/pypi/v/code_apply.svg
        :target: https://pypi.python.org/pypi/code_apply

.. image:: https://img.shields.io/travis/callmexss/code_apply.svg
        :target: https://travis-ci.com/callmexss/code_apply

.. image:: https://readthedocs.org/projects/code-apply/badge/?version=latest
        :target: https://code-apply.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status


.. image:: https://pyup.io/repos/github/callmexss/code_apply/shield.svg
     :target: https://pyup.io/repos/github/callmexss/code_apply/
     :alt: Updates



Apply code content based on name.


* Free software: MIT license
* Documentation: https://code-apply.readthedocs.io.


Features
--------

* Command-line interface for applying code from source to target
* Support for copying individual files or entire directories
* Dry-run mode to preview changes without making them
* Verbose output option for detailed logging

Usage
-----

Install the package:

.. code-block:: bash

    pip install code_apply

Basic usage:

.. code-block:: bash

    # Apply a single file
    code-apply apply source_file.txt target_file.txt

    # Apply a directory recursively
    code-apply apply source_directory/ target_directory/

    # Dry run to preview changes
    code-apply apply source/ target/ --dry-run

    # Verbose output
    code-apply apply source/ target/ --verbose

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

Use with below prompt:


.. code-block:: bash
        请帮重构上面的代码，如果有文件需要修改，请生成该文件的完整代码，并严格按照以下格式:


        ---FILE_PATH: [文件路径]
        ```[语言]
        [文件代码内容]
        ```
        ---END_FILE

        示例:
        ---FILE_PATH: src/main.js
        ```javascript
        console.log('Hello World');
        ```
        ---END_FILE
