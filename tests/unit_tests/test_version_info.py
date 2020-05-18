"""
File Name: test_version_info.py

Authors: Kyle Seidenthal

Date: 13-03-2020

Description: Tests for version info

"""
import pytest
import friendly_ground_truth.version_info as vi

from friendly_ground_truth.version_info import VersionInfo

from mock import MagicMock


class TestVersionString:
    """
    Tests for checking that version strings work properly

    """

    def test_get_version_string(self):
        """
        Test that the correct version string is returned

        Test Conditiion:
            The value from get_version_string() is the properly formatted
            string from the VERSION_MAJOR, VERSION_MINOR, and VERSION_PATCH
            attributes, in the form
            "vVERSION_MAJOR.VERSION_MINOR.VERSION_PATCH".
        """
        info = VersionInfo()

        correct_string = "v" + str(info.VERSION_MAJOR) + '.' +\
                         str(info.VERSION_MINOR) + '.' +\
                         str(info.VERSION_PATCH)

        assert info.get_version_string() == correct_string

    def test_check_newer_version_new_maj(self):
        """
        Test checking for a newer version when there is a new version
        available, and its major version is greater than the current major
        version.

        Test Condition:
            check_newer_version returns True
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
        Test checking for a newer version when there is a new version
        available, and its minor verison is greater than the current minor
        version.


        Test Condition:
            check_newer_version() returns True
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
        Test checking for a newer version when there is not a new version
        available, and its minor verison is less than the current minor
        version.


        Test Condition:
            check_newer_version() returns False
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
        Test checking for a newer version when there is a new version
        available, and its patch verison is greater than the current patch
        version.


        Test Condition:
            check_newer_version() returns True
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
        Test checking for a newer version when there is not a new version
        available, and its patch verison is less than the current patch
        version.


        Test Condition:
            check_newer_version() returns False
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
        Test when there is not a new version


        Test Condition:
            check_newer_version returns False
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
        Test calling the main function with fewer command line arguments than
        are required.


        Test Condition:
            Exit with code 1
        """

        with pytest.raises(SystemExit) as e:
            vi.main(['x'])
            assert e.value.code == 1

    def test_main_invalid_version_string(self):
        """
        Test calling the script with an invalid version string.


        Test Condition:
            Exit with code 1
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
        Test calling the script when an update is available


        Test Condition:
            Exit with code 0
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
        Test calling the script when there is not an update.


        Test Condition:
            Exit code 2
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


class TestGithubRelease():
    """
    Tests related to getting the newest version from Github
    """

    @pytest.fixture
    def response_mock(self, mocker):
        """
        A mock for the response module returning a version string from Github

        Args:
            mocker: The mock module
        """
        response_mock = MagicMock()
        response_mock.json.return_value = {"name": "Release v0.1.1"}
        mocker.patch('requests.get', return_value=response_mock)

    def test_get_newest_release_info(self, response_mock):
        """
        Test getting the newest version string from Github

        Args:
            response_mock: Mock for the request to Github

        Test Condition:
            v0.1.1 is returned from get_newest_release_info()
        """

        info = VersionInfo()

        assert "v0.1.1" == info.get_newest_release_info()

    def test_check_for_update_true(self, response_mock, mocker):
        """
        Test checking for an update when there is a new version.

        Args:
            response_mock: Mock for the request to Github
            mocker: The mocker module interface

        Test Condition:
            check_for_update returns "There is a new version, v0.1.1"
        """

        info = VersionInfo()

        mocker.patch.object(info, "check_newer_version", return_value=True)

        result = info.check_for_update()

        assert result == "There is a new version, v0.1.1."

    def test_check_for_update_false(self, response_mock, mocker):
        """
        Test checking for an update when there is not a new version

        Args:
            response_mock: Mock for the request to GitHub
            mocker: The mocker module interface

        Test Condition:
            check_for_update() return "There are no updates."
        """

        info = VersionInfo()

        mocker.patch.object(info, "check_newer_version", return_value=False)

        result = info.check_for_update()

        assert result == "There are no updates."
