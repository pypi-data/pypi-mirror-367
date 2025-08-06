"""Registry for SCMTools.

Version Added:
    5.0
"""

from __future__ import annotations

import logging
from importlib import import_module
from typing import (Dict, Iterator, List, Optional, TYPE_CHECKING, Tuple,
                    Type, cast)

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from djblets.registries.registry import (ALREADY_REGISTERED, LOAD_ENTRY_POINT,
                                         NOT_REGISTERED)

from reviewboard.registries.registry import EntryPointRegistry
from reviewboard.scmtools.core import SCMTool
from reviewboard.scmtools.models import Tool

if TYPE_CHECKING:
    from importlib_metadata import EntryPoint
    from typing_extensions import TypeAlias

    _ConflictingTools: TypeAlias = List[Tuple[Type[SCMTool], Tool]]


logger = logging.getLogger(__name__)


class SCMToolRegistry(EntryPointRegistry[Type[SCMTool]]):
    """A registry for managing SCMTools.

    Version Added:
        5.0
    """

    entry_point = 'reviewboard.scmtools'

    lookup_attrs = [
        'class_name',
        'lookup_name',
        'scmtool_id',
    ]
    errors = {
        ALREADY_REGISTERED: _('"%(item)s" is already a registered SCMTool.'),
        LOAD_ENTRY_POINT: _(
            'Unable to load SCMTool %(entry_point)s: %(error)s'),
        NOT_REGISTERED: _(
            '"%(attr_value)s" is not a registered SCMTool.'),
    }

    ######################
    # Instance variables #
    ######################

    #: A list of registered tools that conflict.
    conflicting_tools: _ConflictingTools

    #: Whether initial population of the registry is done.
    _initial_populate_name: bool

    def __init__(self) -> None:
        """Initialize the registry."""
        super().__init__()

        self._initial_populate_done = False
        self.conflicting_tools = []

    def on_populated(self) -> None:
        """Perform initial population tracking after the registry is populated.

        Version Added:
            7.0
        """
        if not self._initial_populate_done:
            self._initial_populate_done = True

            # Avoid populating the Tool entries by default when running unit
            # tests, so we can continue to have tests opt into new entries.
            # This avoids side effects and extra unnecessary test time.
            if not settings.RUNNING_TEST:
                self.populate_db()

    def populate_db(self) -> None:
        """Populate the database with missing Tool entries.

        For backwards-compatibility, this will ensure that there's a matching
        :py:class:`~reviewboard.scmtools.models.Tool` in the database for
        every registered SCMTool.

        This will be called automatically when the registry is first set up,
        and in response to any failed database queries for tools.

        It should not be called outside of Review Board.
        """
        # If there are any tools present that don't exist in the Tool
        # table, create those now. This obsoletes the old registerscmtools
        # management command.
        tools = list(Tool.objects.all())
        new_tools: List[Tool] = []
        registered_by_class: Dict[str, Tool] = {}
        registered_by_name: Dict[str, Tool] = {}

        for tool in tools:
            registered_by_name[tool.name] = tool
            registered_by_class[tool.class_name] = tool

        conflicting_tools: _ConflictingTools = []

        # If the user has a modified setup, they may have pointed a tool
        # to a different class path. We want to catch this and warn.
        for scmtool_cls in self:
            lookup_name = scmtool_cls.lookup_name
            class_name = scmtool_cls.class_name

            assert lookup_name
            assert class_name

            tool_by_name = registered_by_name.get(lookup_name)
            tool_by_class = registered_by_class.get(class_name)

            if tool_by_name is None and tool_by_class is None:
                # This is a brand-new Tool. Schedule it for population in the
                # database.
                new_tools.append(Tool(name=lookup_name,
                                      class_name=class_name))
            elif (tool_by_class is not None and
                  tool_by_class.name != lookup_name):
                # This tool matches another by class name, but isn't the same
                # tool.
                conflicting_tools.append((scmtool_cls, tool_by_class))
            elif (tool_by_name is not None and
                  tool_by_name.class_name != class_name):
                # This tool matches another by name, but isn't the same tool.
                conflicting_tools.append((scmtool_cls, tool_by_name))
            else:
                # This is already in the database, so skip it.
                pass

        conflicting_tools = sorted(
            conflicting_tools,
            key=lambda pair: (pair[0].name or ''))
        self.conflicting_tools = conflicting_tools

        if conflicting_tools:
            for scmtool_cls, conflict_tool in conflicting_tools:
                logger.warning(
                    'Tool ID %d (name=%r, class_name=%r) conflicts with '
                    'SCMTool %r (lookup_name=%r, class_name=%r)',
                    conflict_tool.pk,
                    conflict_tool.name,
                    conflict_tool.class_name,
                    scmtool_cls.scmtool_id,
                    scmtool_cls.lookup_name,
                    scmtool_cls.class_name)

        if new_tools:
            Tool.objects.bulk_create(new_tools)

    def get_defaults(self) -> Iterator[Type[SCMTool]]:
        """Yield the built-in SCMTools.

        Yields:
            type:
            The :py:class:`~reviewboard.scmtools.core.SCMTool` subclasses.
        """
        for _module, _scmtool_class_name in (
                ('bzr', 'BZRTool'),
                ('clearcase', 'ClearCaseTool'),
                ('cvs', 'CVSTool'),
                ('git', 'GitTool'),
                ('hg', 'HgTool'),
                ('perforce', 'PerforceTool'),
                ('plastic', 'PlasticTool'),
                ('svn', 'SVNTool'),
            ):
            mod = import_module(f'reviewboard.scmtools.{_module}')
            yield getattr(mod, _scmtool_class_name)

        yield from super().get_defaults()

    def process_value_from_entry_point(
        self,
        entry_point: EntryPoint,
    ) -> Type[SCMTool]:
        """Load the class from the entry point.

        The ``scmtool_id`` attribute will be set on the class from the entry
        point's name.

        Args:
            entry_point (importlib.metadata.EntryPoint):
                The entry point.

        Returns:
            type:
            The :py:class:`~reviewboard.scmtools.core.SCMTool` subclass.
        """
        cls = cast(Type[SCMTool], entry_point.load())
        cls.scmtool_id = entry_point.name
        return cls

    def on_item_registering(
        self,
        scmtool_class: Type[SCMTool],
    ) -> None:
        """Prepare a SCMTool class for registration.

        This will set attributes on the SCMTool class needed for lookup and
        registration.

        Version Added:
            7.0

        Args:
            scmtool_class (type):
                The :py:class:`~reviewboard.scmtools.core.SCMTool` subclass
                being registered.
        """
        class_name = '%s.%s' % (scmtool_class.__module__,
                                scmtool_class.__name__)
        scmtool_class.class_name = class_name

    def on_item_registered(
        self,
        scmtool_class: Type[SCMTool],
    ) -> None:
        """Handle database registration after an SCMTool is registered.

        If the tool does not have an existing Tool model instance in the
        database, this will create it. This will only occur if the initial
        population is complete.

        Version Added:
            7.0

        Args:
            scmtool_class (type):
                The :py:class:`~reviewboard.scmtools.core.SCMTool` subclass
                that was registered.
        """
        if self._initial_populate_done:
            # Make sure the new tool exists in the Tool table as well.
            class_name = scmtool_class.class_name

            if not Tool.objects.filter(class_name=class_name).exists():
                Tool.objects.create(name=scmtool_class.lookup_name,
                                    class_name=class_name)

    def get_by_id(
        self,
        scmtool_id: str,
    ) -> Optional[Type[SCMTool]]:
        """Return the SCMTool with the given ID.

        Args:
            scmtool_id (str):
                The ID of the SCMTool to fetch.

        Returns:
            reviewboard.scmtools.core.SCMTool:
            The SCMTool subclass.
        """
        return self.get('scmtool_id', scmtool_id)

    def get_by_name(
        self,
        name: str,
    ) -> Optional[Type[SCMTool]]:
        """Return the SCMTool with the given lookup name.

        Args:
            name (str):
                The lookup name of the SCMTool to fetch.

        Returns:
            reviewboard.scmtools.core.SCMTool:
            The SCMTool subclass.
        """
        return self.get('lookup_name', name)

    def get_by_class_name(
        self,
        class_name: str,
    ) -> Optional[Type[SCMTool]]:
        """Return the SCMTool with the given class name.

        Args:
            class_name (str):
                The class name of the SCMTool to fetch.

        Returns:
            reviewboard.scmtools.core.SCMTool:
            The SCMTool subclass.
        """
        return self.get('class_name', class_name)
