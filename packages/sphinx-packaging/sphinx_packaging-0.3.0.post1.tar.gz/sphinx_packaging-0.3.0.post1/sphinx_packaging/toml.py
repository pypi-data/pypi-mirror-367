#!/usr/bin/env python3
#
#  toml.py
"""
Sphinx extension which adds the :rst:role:`toml` role for referencing sections of the TOML specification.
"""
# Based on https://github.com/sphinx-doc/sphinx/blob/3.x/sphinx/roles.py
#
# Copyright (c) 2007-2021 by the Sphinx team.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

# stdlib
import re
from typing import Any, Dict, List, Tuple

# 3rd party
from docutils import nodes
from docutils.nodes import Node, system_message
from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.locale import _
from sphinx.util.docutils import ReferenceRole

__all__ = ["TOML", "setup"]


class TOML(ReferenceRole):
	"""
	Sphinx role for referencing a section of the TOML specification.
	"""

	title: str
	target: str
	has_explicit_title: bool

	def run(self) -> Tuple[List[Node], List[system_message]]:
		"""
		Process the role.
		"""

		assert self.inliner is not None

		if self.target.startswith('!'):
			xref = False
			if self.title == self.target:
				self.title = self.target = self.target.lstrip('!')
			else:
				self.target = self.target.lstrip('!')
		else:
			xref = True

		node_list: List[nodes.Node] = []

		if xref:
			target_id = f"index-{self.env.new_serialno('index')}"
			entries = [("single", _("TOML: %s") % self.target, target_id, '', None)]

			index = addnodes.index(entries=entries)
			target = nodes.target('', '', ids=[target_id])
			node_list.extend((index, target))
			self.inliner.document.note_explicit_target(target)

		refuri = self.build_uri()
		reference = nodes.reference('', '', internal=False, refuri=refuri, classes=["toml-xref"])
		reference += nodes.inline(self.title, self.title)
		node_list.append(reference)

		return node_list, []

	def build_uri(self) -> str:
		"""
		Constrict the target URI for the reference node.
		"""

		toml_spec_version = getattr(self.config, "toml_spec_version", "1.0.0").lstrip('v')

		target = re.sub(r"[^\w -]+", '', self.target.lower().replace(' ', '-')).strip('-')
		return f"https://toml.io/en/v{toml_spec_version}#{target}"


def setup(app: Sphinx) -> Dict[str, Any]:
	"""
	Setup :mod:`sphinx_packaging.toml`.

	:param app: The Sphinx application.
	"""

	# this package
	from sphinx_packaging import __version__

	app.add_config_value("toml_spec_version", default="1.0.0", rebuild="env", types=[str])
	app.add_role("toml", TOML())

	return {
			"version": __version__,
			"parallel_read_safe": True,
			"parallel_write_safe": True,
			}
