#!/usr/bin/env python3
#
#  __init__.py
"""
A collection of Sphinx utilities related to Python packaging.
"""
#
#  Copyright © 2021 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#  HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#

# stdlib
from typing import Any, Dict

# 3rd party
from sphinx.application import Sphinx

__all__ = ["setup"]

__author__: str = "Dominic Davis-Foster"
__copyright__: str = "2021 Dominic Davis-Foster"
__license__: str = "BSD License"
__version__: str = "0.3.0.post1"
__email__: str = "dominic@davis-foster.co.uk"


def setup(app: Sphinx) -> Dict[str, Any]:
	"""
	Setup :mod:`sphinx_packaging`.

	:param app: The Sphinx application.
	"""

	app.setup_extension("sphinx_packaging.peps")
	app.setup_extension("sphinx_packaging.tconf")
	app.setup_extension("sphinx_packaging.toml")

	return {
			"version": __version__,
			"parallel_read_safe": True,
			"parallel_write_safe": True,
			}
