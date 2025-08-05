#!/usr/bin/env python3
#
#  peps.py
"""
Sphinx extension which modifies the :rst:role:`sphinx:pep` role to use normal (i.e. not bold) text for custom titles.

Also adds the :rst:role:`pep621` role for referencing sections within :pep:`621`,
and the :rst:role:`core-meta` role for referencing sections in Python's core metadata`.
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
from docutils.nodes import Node, system_message, unescape
from docutils.parsers.rst.states import Inliner
from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.locale import _
from sphinx.util.docutils import ReferenceRole, SphinxRole

__all__ = ["PEP", "PEP621Section", "CoreMetadata", "setup"]


class PEP(ReferenceRole):
	"""
	Sphinx role for referencing a PEP or a section thereof.
	"""

	title: str
	target: str
	has_explicit_title: bool

	def run(self) -> Tuple[List[Node], List[system_message]]:
		"""
		Process the role.
		"""

		assert self.inliner is not None

		target_id = f"index-{self.env.new_serialno('index')}"
		entries = [("single", _("Python Enhancement Proposals; PEP %s") % self.target, target_id, '', None)]

		index = addnodes.index(entries=entries)
		target = nodes.target('', '', ids=[target_id])
		self.inliner.document.note_explicit_target(target)

		try:
			refuri = self.build_uri()
			reference = nodes.reference('', '', internal=False, refuri=refuri, classes=["pep"])
			if self.has_explicit_title:
				reference += nodes.inline(self.title, self.title)
			else:
				title = f"PEP {self.title}"
				reference += nodes.strong(title, title)
		except ValueError:
			msg = self.inliner.reporter.error(
					f"invalid PEP number {self.target}",
					line=self.lineno,
					)
			prb = self.inliner.problematic(self.rawtext, self.rawtext, msg)
			return [prb], [msg]

		return [index, target, reference], []

	def build_uri(self) -> str:
		"""
		Constrict the target URI for the reference node.
		"""

		assert self.inliner is not None

		base_url: str = self.inliner.document.settings.pep_base_url
		if base_url == "https://www.python.org/dev/peps/":  # pragma: no cover
			# Update URL
			base_url = "https://peps.python.org/"
		ret = self.target.split('#', 1)

		if len(ret) == 2:
			return f"{base_url}pep-{int(ret[0]):04d}#{ret[1]}"
		else:
			return f"{base_url}pep-{int(ret[0]):04d}"


class PEP621Section(PEP):
	"""
	Sphinx role for referencing a section within :pep:`621`.
	"""

	def __call__(  # noqa: 117
		self,
		name: str,
		rawtext: str,
		text: str,
		lineno: int,
		inliner: Inliner,
		options: Dict = {},
		content: List[str] = []
		) -> Tuple[List[Node], List[system_message]]:

		matched = self.explicit_title_re.match(text)
		if matched:
			self.has_explicit_title = True
			self.title = unescape(matched.group(1))
			self.target = f"621#{unescape(matched.group(2))}"
		else:
			self.has_explicit_title = True
			self.title = unescape(text)
			self.target = f"621#{unescape(text)}"

		if self.target in {
				f"621#dependencies",
				f"621#optional-dependencies",
				f"621#dependencies/optional-dependencies",
				}:
			self.target = f"621#dependencies-optional-dependencies"

		elif self.target in {f"621#authors", f"621#maintainers", f"621#authors/maintainers"}:
			self.target = f"621#authors-maintainers"

		return SphinxRole.__call__(self, name, rawtext, text, lineno, inliner, options, content)


class CoreMetadata(ReferenceRole):
	"""
	Sphinx role for referencing a `core metadata`_ field.

	.. _core metadata: https://packaging.python.org/specifications/core-metadata/
	"""

	title: str
	target: str
	has_explicit_title: bool

	def run(self) -> Tuple[List[Node], List[system_message]]:
		"""
		Process the role.

		:rtype:

		.. latex:clearpage::
		"""

		assert self.inliner is not None

		target_id = f"index-{self.env.new_serialno('index')}"
		entries = [("single", _("Core Metadata Field %s") % self.target, target_id, '', None)]

		index = addnodes.index(entries=entries)
		target = nodes.target('', '', ids=[target_id])
		self.inliner.document.note_explicit_target(target)

		refuri = self.build_uri()
		reference = nodes.reference('', '', internal=False, refuri=refuri, classes=["pep"])
		reference += nodes.inline(self.title, self.title)

		return [index, target, reference], []

	def build_uri(self) -> str:
		"""
		Construct the target URI for the reference node.
		"""

		base_url: str = "https://packaging.python.org/specifications/core-metadata/"
		target = re.sub(r"[\W]+", '-', self.target.lower()).strip('-')
		return f"{base_url}#{target}"


def setup(app: Sphinx) -> Dict[str, Any]:
	"""
	Setup :mod:`sphinx_packaging.peps`.

	:param app: The Sphinx application.
	"""

	# this package
	from sphinx_packaging import __version__

	app.add_role("pep", PEP(), override=True)
	app.add_role("pep621", PEP621Section())
	app.add_role("core-meta", CoreMetadata())

	return {
			"version": __version__,
			"parallel_read_safe": True,
			"parallel_write_safe": True,
			}
