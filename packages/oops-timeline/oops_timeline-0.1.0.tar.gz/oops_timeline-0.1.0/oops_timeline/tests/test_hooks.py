# Copyright (c) 2010, 2011, Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, version 3 only.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Tests for the various hooks included in oops-timeline."""


from oops import Config
from testtools import TestCase
from timeline import Timeline

from oops_timeline import install_hooks
from oops_timeline.hooks import flatten_timeline


class TestInstallHooks(TestCase):

    def test_install_hooks_installs_defaults(self):
        config = Config()
        install_hooks(config)
        self.assertIn(flatten_timeline, config.on_create)


class TestHooks(TestCase):

    def test_flatten_timeline(self):
        timeline = Timeline()
        action = timeline.start("foo", "bar")
        action.finish()
        context = dict(timeline=timeline)
        report = {}
        flatten_timeline(report, context)
        self.assertIn("timeline", report)
        self.assertEqual([action.logTuple()], report["timeline"])
