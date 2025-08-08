#
# Configuration Manager API exceptions module.
#
#
# This file is a part of Typhoon HIL API library.
#
# Typhoon HIL API is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


class ConfigurationManagerAPIException(Exception):
    """
    Base exception class for the Configuration manager API
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the object
        """
        super().__init__(*args)
        self.internal_code = None
        if "internal_code" in kwargs:
            self.internal_code = kwargs["internal_code"]


class ConfigurationManagerAPIExceptionTextX(ConfigurationManagerAPIException):
    def __init__(self, msg, *args):
        msg = (
            f"An exception has occurred while parsing/checking the "
            f"integrity of files used for generating certain objects "
            f"needed in the Configuration Manager API. It is best to "
            f"make sure all files (such as .tse, .cfg, .cmp ...) are "
            f"written correctly, and that all software used while running "
            f"the current script is up to date with the latest versions. "
            f"Inner exception: [{msg}]"
        )
        super().__init__(msg, *args)


class ConfigurationManagerAPIExceptionGenerate(ConfigurationManagerAPIException):
    def __init__(self, inner_exception, *args):
        msg = (
            f"Generating the output script that creates the final schematic "
            f"failed because an exception occured. This could mean that "
            f"certain files are missing, or that the input files (the "
            f"project, the projects template, the configuration or "
            f"the configuration options) may be defined incorrectly. "
            f"Concrete inner exception: [{inner_exception.args}]"
        )
        super().__init__(msg, *args)


class ConfigurationManagerAPIExceptionSchematicAPI(ConfigurationManagerAPIException):
    def __init__(self, inner_exception, *args):
        msg = (
            f"An exception has occurred while trying to generate the "
            f"schematic based on the selected configuration. This could "
            f"have been caused by an error in defining, or a missing item"
            f" in the project definition, projects template definition, "
            f"or the configuration or any variants and options in the "
            f"configuration. This exception was raised by the Schematic "
            f"API, with the following message: [{inner_exception}]"
        )
        super().__init__(msg, *args)


class ConfigurationManagerAPIExceptionPathNotFound(ConfigurationManagerAPIException):
    def __init__(self, path, *args):
        msg = f"Path not found: {path}"
        super().__init__(msg, *args)


class ConfigurationManagerAPIExceptionItemNotFound(ConfigurationManagerAPIException):
    def __init__(self, missing_item, *args):
        msg = f"Item not found: {missing_item}"
        super().__init__(msg, *args)


class ConfigurationManagerAPIExceptionOptionNotFound(ConfigurationManagerAPIException):
    def __init__(self, pick, variant, *args):
        msg = f"Option: {pick} not found for project variant: {variant}"
        super().__init__(msg, *args)


class ConfigurationManagerAPIExceptionVariantNotFound(ConfigurationManagerAPIException):
    def __init__(self, variant, *args):
        msg = f"Variant: {variant} not found for project"
        super().__init__(
            msg, *args
        )


class ConfigurationManagerAPIExceptionOutputProjectFileDoesNotExist(
    ConfigurationManagerAPIException
):
    def __init__(self, path, *args):
        msg = f"Path to output project file {path} does not exist"
        super().__init__(msg, *args)


class ConfigurationManagerAPIExceptionOptionError(ConfigurationManagerAPIException):
    def __init__(self, option_name, project_name, *args):
        msg = (
            f"Error fetching option [{option_name}] for project [{project_name}]."
            f"This could be because the option file was not found, or the option "
            f"file/concrete option had no component defined, or there "
            f"was a general error when defining the option. Check the "
            f"project file definition, the configuration definition, "
            f"and the option definitions."
        )
        super().__init__(msg, *args)
