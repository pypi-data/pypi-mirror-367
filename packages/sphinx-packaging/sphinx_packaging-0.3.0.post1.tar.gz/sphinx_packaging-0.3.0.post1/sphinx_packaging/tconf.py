#!/usr/bin/env python3
#
#  tconf.py
r"""
The :rst:dir:`tconf` directive and role for configuration fields in ``pyproject.toml`` etc.
"""
#
#  Copyright © 2020-2021 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  Based on https://github.com/readthedocs/sphinx_rtd_theme/blob/master/docs/conf.py
#  Copyright (c) 2013-2018 Dave Snider, Read the Docs, Inc. & contributors
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#  DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#  OR OTHER DEALINGS IN THE SOFTWARE.
#
#  Based on https://github.com/sphinx-doc/sphinx/blob/3.x/sphinx/domains/std.py
#  and on https://github.com/sphinx-doc/sphinx/blob/3.x/sphinx/domains/python.py
#
#  Copyright (c) 2007-2021 by the Sphinx team.
#  All rights reserved.
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

# stdlib
from typing import Any, Callable, Dict, List, Mapping, Optional, Tuple, Type, cast  # noqa: F401

# 3rd party
from docutils import nodes
from docutils.nodes import Node
from docutils.parsers.rst import directives
from docutils.statemachine import StringList
from domdf_python_tools.utils import strtobool
from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.domains import ObjType
from sphinx.domains.std import GenericObject, StandardDomain
from sphinx.environment import BuildEnvironment
from sphinx.locale import __
from sphinx.roles import XRefRole
from sphinx.util import logging, ws_re
from sphinx.util.nodes import make_refnode

__all__ = ["TConfXRefRole", "TOMLConf", "resolve_xref", "setup"]

logger = logging.getLogger(__name__)


def _flag(argument: Any) -> bool:
	"""
	Check for a valid flag option (no argument) and return :py:obj:`True`.

	Used in the ``option_spec`` of directives.

	:raises: :exc:`ValueError` if an argument is given.
	"""

	if argument and argument.strip():  # pragma: no cover
		raise ValueError(f"No argument is allowed; {argument!r} supplied")
	else:
		return True


class TOMLConf(GenericObject):
	"""
	The :rst:dir:`tconf` directive.
	"""

	#: The template string for index entries.
	indextemplate: str = "pair: %s; TOML configuration field"
	doc_field_types: List = []
	content: StringList

	option_spec: Mapping[str, Callable[[str], Any]] = {  # type: ignore[assignment,misc]
		"type": directives.unchanged_required,
		"required": directives.unchanged_required,
		"default": directives.unchanged_required,
		"noindex": _flag,
		}

	def run(self) -> List[Node]:
		"""
		Process the content of the directive.
		"""

		content: List[str] = []

		if self.options and set(self.options.keys()) != {"noindex"}:
			content.extend(('', ".. raw:: latex", '', r"    \vspace{-45px}", ''))

		if "type" in self.options:
			content.append(f"| **Type:** {self.format_type(self.options['type'])}")
		if "required" in self.options:
			content.append(f"| **Required:** ``{self.format_required(self.options['required'])}``")
		if "default" in self.options:
			content.append(f"| **Default:** {self.format_default(self.options['default'])}")

		if self.content:

			content.extend((
					'',
					".. raw:: latex",
					'',
					r"    \vspace{-25px}",
					'',
					))
			content.extend(self.content)

		self.content = StringList(content)

		return super().run()

	@staticmethod
	def format_type(the_type: str) -> str:
		"""
		Formats the ``:type:`` option.

		:param the_type:
		"""

		return the_type

	@staticmethod
	def format_required(required: str) -> bool:
		"""
		Formats the ``:required:`` option.

		:param required:
		"""

		return strtobool(required)

	@staticmethod
	def format_default(default: str) -> str:
		"""
		Formats the ``:default:`` option.

		:param default:
		"""

		return default

	def handle_signature(self, sig: str, signode: addnodes.desc_signature) -> str:
		"""
		Parse the signature of the :rst:dir:`tconf` directive.

		:param sig: The name of the field.
		:param signode: The signature node created by Sphinx.

		:returns: The final component of the field path (e.g. ``foo.bar`` -> ``bar``).
		"""

		signode.clear()
		parts = sig.rsplit('.', 1)

		if len(parts) == 1:
			name = parts[0]
		else:
			addname, name = parts

			if getattr(self.env.config, "tconf_show_full_name", False):
				signode += addnodes.desc_addname(f"{addname}.", f"{addname}.")
				# signode += addnodes.desc_annotation("conf", "conf")

		signode += addnodes.desc_name(name, name)

		# normalize whitespace like XRefRole does
		return ws_re.sub(' ', sig)


class TConfXRefRole(XRefRole):
	"""
	Customised XRef role for :rst:role:`tconf` roles.
	"""

	def process_link(
			self,
			env: BuildEnvironment,
			refnode: nodes.Element,
			has_explicit_title: bool,
			title: str,
			target: str,
			) -> Tuple[str, str]:
		r"""
		Construct a link from the parsed content of the role.

		:param env: The Sphinx build environment.
		:param refnode: The reference node.
		:param has_explicit_title: Whether the role has an explicit title.
		:param title: The title of the XRef role.
		:param target: The target of the XRef role. (:samp:`:tconf:\`title <target>\``)

		:returns: A tuple of ``(title, target)``.

		.. latex:clearpage::
		"""

		if not has_explicit_title:
			title = title.lstrip('.')  # only has a meaning for the target
			target = target.lstrip('~')  # only has a meaning for the title

			# if the first character is a tilde, don't display the module/class parts of the contents
			if title[0:1] == '~':
				title = title[1:]
				dot = title.rfind('.')
				if dot != -1:
					title = title[dot + 1:]

		# if the first character is a dot, search more specific namespaces first
		# else search builtins first
		if target[0:1] == '.':
			target = target[1:]
			refnode["refspecific"] = True

		return title, target


def resolve_xref(
		app: Sphinx,
		env: BuildEnvironment,
		node: nodes.Node,
		contnode: nodes.Node,
		) -> Optional[nodes.reference]:
	"""
	Resolve as-yet-unresolved XRefs for :rst:role:`tconf` roles.

	:param app: The Sphinx application.
	:param env: The Sphinx build environment.
	:param node: The cross reference node which has not yet been.
	:param contnode: The child node of the reference node, which provides the formatted text.
	"""

	if not isinstance(node, nodes.Element):  # pragma: no cover
		return None

	if node.get("refdomain", None) != "std":  # pragma: no cover
		return None
	elif node.get("reftype", None) != "tconf":  # pragma: no cover
		return None
	elif not node.get("reftarget"):  # pragma: no cover
		return None

	std_domain = cast(StandardDomain, env.get_domain("std"))
	objtypes = std_domain.objtypes_for_role("tconf") or []
	reftarget = node["reftarget"]
	candidates = []

	for (obj_type, obj_name), (docname, labelid) in std_domain.objects.items():
		if not docname:  # pragma: no cover
			continue

		if obj_type in objtypes:
			if obj_name.endswith(f".{reftarget}"):
				candidates.append((docname, labelid, obj_name))

	if not candidates:
		return None  # pragma: no cover
	elif len(candidates) > 1:
		logger.warning(
				__("more than one target found for cross-reference %r: %s"),
				reftarget,
				", ".join(c[2] for c in candidates),
				type="ref",
				subtype="tconf",
				location=node,
				)

	return make_refnode(
			app.builder,
			env.docname,
			candidates[0][0],  # docname
			candidates[0][1],  # labelid
			contnode,
			)


def setup(app: Sphinx) -> Dict[str, Any]:
	"""
	Setup :mod:`sphinx_packaging.tconf`.

	:param app: The Sphinx application.
	"""

	# this package
	from sphinx_packaging import __version__

	if "std" not in app.registry.domains:
		app.add_domain(StandardDomain)  # pragma: no cover

	name = "tconf"

	app.registry.add_directive_to_domain("std", name, TOMLConf)
	app.registry.add_role_to_domain("std", name, TConfXRefRole())

	object_types = app.registry.domain_object_types.setdefault("std", {})
	object_types[name] = ObjType(name, name)

	app.connect("missing-reference", resolve_xref, priority=250)

	app.add_config_value("tconf_show_full_name", True, "env", [bool])

	return {
			"version": __version__,
			"parallel_read_safe": True,
			"parallel_write_safe": True,
			}
