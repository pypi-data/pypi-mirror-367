# SPDX-FileCopyrightText: © 2025 Roger Wilson
#
# SPDX-License-Identifier: MIT

import itertools as it
import pathlib
import sys
import unittest


class TestModuleStructure(unittest.TestCase):
    # Test declared in all python files.
    def test_copyright_and_license(self):
        top = pathlib.Path(__file__).resolve().parent.parent
        count = 0
        for p in it.chain((top / "src").glob("**/*.py"), (top / "tests").glob("**/*.py")):
            count += 1
            with open(p, "r", encoding='utf-8') as fh:
                lines = fh.readlines()
            self.assertEqual("# SPDX-FileCopyrightText: © 2025 Roger Wilson", lines[0][:-1],
                             f"Copyright missing in {p}.")
            self.assertEqual("#", lines[1][:-1], f"Spacer missing in {p}.")
            self.assertEqual("# SPDX-License-Identifier: MIT", lines[2][:-1], f"License missing in {p}.")
        self.assertEqual(33, count)

    def test_version(self):
        # noinspection PyUnresolvedReferences
        import yet_more_functools
        self.assertEqual('1.1.0', yet_more_functools.__version__)  # add assertion here

    def test_modules_load(self):
        # noinspection PyUnresolvedReferences
        import yet_more_functools.sow_reap

        self.assertTrue("yet_more_functools.sow_reap" in sys.modules)

        # noinspection PyUnresolvedReferences
        import yet_more_functools.throw_catch
        self.assertTrue("yet_more_functools.throw_catch" in sys.modules)


if __name__ == '__main__':
    unittest.main()
