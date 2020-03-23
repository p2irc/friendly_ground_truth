"""
File Name: test_version_info.py

Authors: Kyle Seidenthal

Date: 13-03-2020

Description: Tests for version info

"""
import pytest
import friendly_ground_truth.version_info as vi

from friendly_ground_truth.version_info import VersionInfo


class TestVersionInfo:

    def test_get_version_string(self):
        """
        Test getting the version string

        :test_condition:  The version string matches a string version of the
                          current version number

        :returns: None
        """
        info = VersionInfo()

        correct_string = "v" + str(info.VERSION_MAJOR) + '.' +\
                         str(info.VERSION_MINOR) + '.' +\
                         str(info.VERSION_PATCH)

        assert info.get_version_string() == correct_string

    def test_check_newer_version_new_maj(self):
        """
        Test checking a newer version when the input strings v_maj > the
        current VERSION_MAJOR

        :test_condition: Returns True

        :returns: None
        """

        info = VersionInfo()

        v_maj = info.VERSION_MAJOR + 1
        v_min = 0
        v_patch = 0

        version_string = 'v' + str(v_maj) + '.' + str(v_min) + '.' +\
                         str(v_patch)

        assert info.check_newer_version(version_string) is True

    def test_check_newer_version_new_min(self):
        """
        Test checking a newer version when the input strings v_maj == the
        current VERSION_MAJOR and the input v_min > the current VERSION_MINOR

        :test_condition: Returns True

        :returns: None
        """

        info = VersionInfo()

        v_maj = info.VERSION_MAJOR
        v_min = info.VERSION_MINOR + 1
        v_patch = 0

        version_string = 'v' + str(v_maj) + '.' + str(v_min) + '.' +\
                         str(v_patch)

        assert info.check_newer_version(version_string) is True

    def test_check_newer_version_new_min_less(self):
        """
        Test checking a newer version when the input v_maj == VERSION_MAJOR and
        v_min < VERSION_MINOR

        :test_condition: Returns False

        :returns: None
        """

        info = VersionInfo()

        if info.VERSION_MINOR == 0:
            info.VERSION_MINOR = 1

        v_maj = info.VERSION_MAJOR
        v_min = info.VERSION_MINOR - 1
        v_patch = 0

        version_string = 'v' + str(v_maj) + '.' + str(v_min) + '.' +\
                         str(v_patch)

        assert info.check_newer_version(version_string) is False

    def test_check_newer_version_new_patch(self):
        """
        Test checking a newer version when the input strings v_maj == the
        current VERSION_MAJOR and the input v_min == the current VERSION_MINOR
        and the input v_patch > the current VERSION_PATCH

        :test_condition: Returns True

        :returns: None
        """

        info = VersionInfo()

        v_maj = info.VERSION_MAJOR
        v_min = info.VERSION_MINOR
        v_patch = info.VERSION_PATCH + 1

        version_string = 'v' + str(v_maj) + '.' + str(v_min) + '.' +\
                         str(v_patch)

        assert info.check_newer_version(version_string) is True

    def test_check_newer_version_no_new_patch(self):
        """
        Test checking a newer version when the input strings v_maj == the
        current VERSION_MAJOR and the input v_min == the current VERSION_MINOR
        and the input v_patch < the current VERSION_PATCH

        :test_condition: Returns False

        :returns: None
        """

        info = VersionInfo()

        v_maj = info.VERSION_MAJOR
        v_min = info.VERSION_MINOR
        v_patch = 0

        version_string = 'v' + str(v_maj) + '.' + str(v_min) + '.' +\
                         str(v_patch)

        assert info.check_newer_version(version_string) is False


    def test_check_newer_version_false(self):
        """
        Test checking a newer version when the v_maj <  the current
        VERSION_MAJOR

        :test_condition: Returns False

        :returns: None
        """

        info = VersionInfo()

        if info.VERSION_MAJOR == 0:
            info.VERSION_MAJOR = 1

        v_maj = info.VERSION_MAJOR - 1
        v_min = 0
        v_patch = 0

        version_string = 'v' + str(v_maj) + '.' + str(v_min) + '.' +\
                         str(v_patch)

        assert info.check_newer_version(version_string) is False

    def test_main_not_enough_args(self):
        """
        Test main with less than 2 args

        :test_condition: sys.exit(1)

        :returns: None
        """

        with pytest.raises(SystemExit) as e:
            vi.main(['x'])
            assert e.value.code == 1

    def test_main_invalid_version_string(self):
        """
        Test main with a version string not in format 'x.y.z'

        :test_condition: sys.exit(1)

        :returns: None
        """

        with pytest.raises(SystemExit) as e:
            vi.main(['x', '1-1-1'])

            assert e.value_code == 1

            vi.main(['x', 'v2.1-3'])

            assert e.value_code == 1

            vi.main(['x', 'spaghetti'])

            assert e.value_code == 1

    def test_main_with_update(self):
        """
        Test main when the given version number is newer

        :test_condition: sys.exit(0)

        :returns: None
        """
        info = VersionInfo()

        v_maj = info.VERSION_MAJOR + 1
        v_min = 0
        v_patch = 0

        version_string = 'v' + str(v_maj) + '.' + str(v_min) + '.' +\
                         str(v_patch)

        with pytest.raises(SystemExit) as e:
            vi.main(['x', version_string])

            assert e.value_code == 0

            version_string = version_string.strip('v')

            vi.main(['x', version_string])

            assert e.value_code == 0

    def test_main_no_update(self):
        """
        Test main when the given version number is older

        :test_condition: sys.exit(2)

        :returns: None
        """

        info = VersionInfo()

        if info.VERSION_MAJOR == 0:
            info.VERSION_MAJOR = 1

        v_maj = info.VERSION_MAJOR - 1
        v_min = 0
        v_patch = 0

        version_string = 'v' + str(v_maj) + '.' + str(v_min) + '.' +\
                         str(v_patch)

        with pytest.raises(SystemExit) as e:
            vi.main(['x', version_string])

            assert e.value_code == 2

            version_string = version_string.strip('v')

            vi.main(['x', version_string])

            assert e.value_code == 2
