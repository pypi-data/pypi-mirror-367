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
"""Schematic Editor API module."""

import os
import time

from typhoon.api.schematic_editor.const import (
    CONTEXT_REAL_TIME,
    DIRECTION_OUT,
    ERROR_GENERAL,
    FLIP_NONE,
    FQN_SEP,
    ICON_ROTATE,
    ICON_TEXT_LIKE,
    ITEM_ANY,
    KIND_PE,
    ROTATION_UP,
    SP_TYPE_REAL,
    TAG_SCOPE_GLOBAL,
    WARNING_GENERAL,
    WIDGET_EDIT,
)
from typhoon.api.schematic_editor.exception import SchApiException
from typhoon.api.schematic_editor.stub import clstub
from typhoon.api.utils import determine_path


class NotSupportedModule(Exception):
    # custom exception
    pass


__all__ = ["model"]


class SchematicAPI:
    """
    Class models schematic model and provide methods to manipulate schematic
    model.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize schematic model instance.

        Arguments:
            None
        """
        super().__init__(*args, **kwargs)

        # Indicator if messages are written to standard error
        self.debug = True

        # Flag used to tell if compiling should be aborted
        self.abort_compiling = False

    def raise_exceptions(self, value):
        clstub().raise_exceptions = value

    def _reconnect(self):
        """Reconnects client to Typhoon HIL Control Center.

        This is used in cases where Typhoon HIL Control Center needs to be
        restarted, to reestablish the connection between the client and THCC.
        """
        clstub().reconnect()

    @staticmethod
    def _generate_model_name():
        """
        Generate model name.
        """
        time_stamp = time.strftime("%d-%b-%Y@%H-%M-%S")
        return f"New schematic {time_stamp}"

    def print_message(self, message):
        """
        Prints provided message if debug mode is activated.

        Args:
            message (str): Message to print.

        Returns:
            None
        """
        if self.debug:
            print(message)

    def create_new_model(self, name=None):
        """
        Creates new model.

        Args:
            name(str): Optional model name, if not specified it will be
                automatically generated.

        Returns:
            None

        **Example:**

        .. literalinclude:: sch_api_examples/create_model_close.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/create_model_close.example
        """
        return clstub().create_new_model(name=name)

    def model_to_api(self, variants=(), prop_mappings=None):
        """Generates string with API commands that recreate the current
        state of the model.

        .. note:: This function cannot be used in handlers.

        Args:
            variants(sequence): Sequence of variant components
                (component fully qualified names).
            prop_mappings(dict): Mapping of property values for specified
                components(used by configuration management).

        Returns:
            str

        **Example:**

        .. literalinclude:: sch_api_examples/model_to_api.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/model_to_api.example
        """
        return clstub().model_to_api(variants=variants, prop_mappings=prop_mappings)

    def add_library_path(self, library_path, add_subdirs=False, persist=False):
        """
        Add path where library files are located (to the library search path).
        Addition of library path is temporary (process which calls this
        function will see change but after it's finished added path will not
        be saved).

        Args:
            library_path(str): Directory path where library files are located.
            add_subdirs(bool): Search in subdirectories for library files.
            persist(bool): Make library path change permanent.

        Returns:
            None

        **Example:**

        .. literalinclude:: sch_api_examples/add_remove_reload_lib_path.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/add_remove_reload_lib_path.example
        """
        return clstub().add_library_path(
            library_path=determine_path(library_path),
            add_subdirs=add_subdirs,
            persist=persist,
        )

    def remove_library_path(self, library_path, persist=False):
        """
        Remove path from library search path.

        Args:
            library_path(str): Library path to remove.
            persist(bool): Make library path change permanent.

        Returns:
            None

        Raises:
            SchApiItemNotFoundException when there is no provided
            library path in existing paths.

        **Example:**

        .. literalinclude:: sch_api_examples/add_remove_reload_lib_path.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/add_remove_reload_lib_path.example
        """
        return clstub().remove_library_path(
            library_path=determine_path(library_path), persist=persist
        )

    def get_library_paths(self):
        """
        Get a list of the library search paths.

        Args:
            None

        returns:
            list with user library paths

        **Example:**

        .. literalinclude:: sch_api_examples/add_remove_reload_lib_path.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/add_remove_reload_lib_path.example
        """
        return clstub().get_library_paths()

    def _save_library_paths(self):
        """
        Save and persist current library paths

        Args:
            None

        Returns:
            None
        """
        return clstub()._save_library_paths()

    def reload_libraries(self):
        """
        Reload libraries which are found in library path.
        Libraries means a user added library (not the core one shipped with
        software installation).

        Args:
            None

        Returns:
            List with names of reloaded libraries or None when libraries
                are not reloaded.

        Raises:
            SchApiException when there is error during library reloading.

        **Example:**

        .. literalinclude:: sch_api_examples/add_remove_reload_lib_path.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/add_remove_reload_lib_path.example
        """
        return clstub().reload_libraries()

    def close_model(self):
        """
        Closes model.

        Args:
            None

        Returns:
            None

        **Example:**

        .. literalinclude:: sch_api_examples/create_model_close.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/create_model_close.example
        """
        return clstub().close_model()

    def load(self, filename, debug=True):
        """
        Loads model from file.

        .. note:: This function cannot be used in handlers.

        Args:
            filename (str): Filename in which model is located.

            debug (bool): Indicate to print messages or not.

        Returns:
            ``True`` if load was successful, ``False`` otherwise.

        **Example:**

        .. literalinclude:: sch_api_examples/load.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/load.example
        """
        return clstub().load(filename=determine_path(filename), debug=debug)

    def save(self):
        """
        Save a loaded model into same file from which it is loaded.

        .. note:: This function cannot be used in handlers.

        Args:
            None

        Returns:
            ``True`` if model is saved successfully, ``False`` otherwise.

        **Example:**

        .. literalinclude:: sch_api_examples/save_save_as.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/save_save_as.example
        """
        return clstub().save()

    def save_as(self, filename):
        """
        Save schematic model under different name.

        .. note:: This function cannot be used in handlers.

        Args:
            filename (str): Save schematic model using filename as new file
                name.

        Returns:
            ``True`` if model is saved or ``False`` if some error occurs.

        **Example:**

        .. literalinclude:: sch_api_examples/save_save_as.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/save_save_as.example
        """
        return clstub().save_as(filename=determine_path(filename))

    def is_model_changed(self):
        """
        Returns True if any modification has been made to the model after it was
        loaded.

        Args:
            None

        Returns:
            Boolean that indicates the model change status.

        **Example:**

        .. literalinclude:: sch_api_examples/is_model_changed.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/is_model_changed.example
        """
        return clstub().is_model_changed()

    def _handle_error_message(self, code, context, msg):
        self.abort_compiling = True

    def compile(self, conditional_compile=False):  # noqa: A003
        """
        Compile schematic model.
        If conditional_compile is set to True, and model
        together with it's dependencies is unchanged,
        compilation won't be executed.

        .. note:: This function cannot be used in handlers.

        Args:
            conditional_compile (bool): When true, compilation should be
             skipped if model is unchanged

        Returns:
            ``True`` if compilation was successful, ``False`` otherwise.

        **Example:**

        .. literalinclude:: sch_api_examples/compile.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/compile.example
        """
        return clstub().compile(conditional_compile=conditional_compile)

    # TODO: This function should be revised once we have official name, currently we need it for automated testing
    def _start_offline_simulation(self):
        """
        Starts Offline Simulation.

        .. note:: This function cannot be used in handlers.

        Args:

        Returns:
            None

        **Example:**

        .. literalinclude:: sch_api_examples/start_offline_simulation.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/start_offline_simulation.example
        """
        return clstub()._start_offline_simulation()

    def _get_offline_simulation_results(self, scope_names=None):
        """
        Returns results of offline simulation from scopes

        Args:
            List of scope fully qualified names from which to pull results or None
        Returns:
            TBD

        **Example:**

        .. literalinclude:: sch_api_examples/get_offline_simulation_results.example
            :language: python
            :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_offline_simulation_results.example
        """
        return clstub()._get_offline_simulation_results(scope_names=scope_names)

    def set_hw_settings(self, product, revision, conf_id):
        """
        .. deprecated:: 2.0
            Use ``set_model_property_value`` instead.

        .. note:: This function cannot be used in handlers.

        Sets new hardware settings.

        Args:
            product (str): Product name (HIL 400, HIL 600 and so on).

            revision (str): Product revision (1, 2, ...).

            conf_id (str): Configuration id.

        Returns:
            ``True`` if operation was successful, ``False`` otherwise.
        """
        return clstub().set_hw_settings(
            product=product, revision=revision, conf_id=conf_id
        )

    def detect_hw_settings(self):
        """
         Detect and set hardware settings by querying hardware device.

         .. note:: This function cannot be used in handlers.

         Args:
             None

         Returns:
             tuple (hw_product_name, hw_revision, configuration_id) or
             ``False`` if auto-detection failed.

        **Example:**

        .. literalinclude:: sch_api_examples/detect_hw_settings.example
           :language: python
           :lines: 2-

        """
        return clstub().detect_hw_settings()

    def get_hw_settings(self):
        """
        Get hardware settings from device without changing model configuration.

        .. note:: This function cannot be used in handlers.

        Args:
            None

        Returns:
            Tuple (hw_product_name, hw_revision, configuration_id) of the type
            (str, int, int).
            For example ('HIL604', 3, 1), note that in string 'HIL604' there is no
            space between string 'HIL' and model number.

            If auto-detection fails, ``False`` is returned.

        **Example:**

        .. literalinclude:: sch_api_examples/get_hw_settings.example
           :language: python
           :lines: 2-
        """
        return clstub().get_hw_settings()

    def set_simulation_method(self, simulation_method):
        """
        .. deprecated:: 2.0
            Use ``set_model_property_value`` instead (``simulation_method`` field
            in configuration object).

        Set simulation method.

        .. note:: This function cannot be used in handlers.

        Args:
            simulation_method (str): Method used for simulation.

        Returns:
            ``True`` if successful, ``False`` otherwise.

        **Example:**

        .. literalinclude:: sch_api_examples/set_simulation.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/set_simulation.example
        """
        return clstub().set_simulation_method(simulation_method=simulation_method)

    def set_simulation_time_step(self, time_step):
        """
        .. deprecated:: 2.0
            Use ``set_model_property_value`` instead (``simulation_time_step`` field in
            configuration object).

        Set schematic model simulation time time_step.

        .. note:: This function cannot be used in handlers.

        Args:
            time_step (str): Time step used for simulation.

        Returns:
            ``True`` if successful, ``False`` otherwise.

        **Example:**

        .. literalinclude:: sch_api_examples/set_simulation.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/set_simulation.example
        """
        return clstub().set_simulation_time_step(time_step=time_step)

    # def set_server_configuration(self, ip=None, port=None):
    #     return _CL_STUB.set_server_config(ip,port)

    def set_component_property(self, component, property, value):  # noqa: A002
        """
        .. deprecated:: 2.0
            Use :func:`set_property_value` instead.

        Sets component property value to provided value.

        .. note:: This function cannot be used in handlers.

        Args:
            component (str): Component name.

            property (str): Property name (code name of property, can be viewed
                in tooltip over property widget in component property dialog).

            value (object): New property value.

        Returns:
            ``True`` if property value was successfully applied,
            ``False`` otherwise.
        """
        return clstub().set_component_property(
            component=component, property=property, value=value
        )

    def set_property_attribute(
        self,
        component,
        property,  # noqa: A002
        attribute,
        value,  # noqa: A002
    ):
        """
        NOTE: This function is deprecated.
        It is kept here, because some code exists which uses it.

        :param component: component name.
        :param property: property name.
        :param attribute: attribute name.
        :param value: new value for property.
        :return: True if successful, False otherwise.
        """
        return clstub().set_property_attribute(
            component=component, property=property, attribute=attribute, value=value
        )

    def set_model_property_value(self, prop_code_name, value):
        """
        Sets model property to specified value.

        Args:
            prop_code_name (str): Model property code name.

            value (object): Value to set.

        Returns:
            None

        Raises:
            SchApiItemNotFoundException when specified model property doesn't
            exists.

        **Example:**

        .. literalinclude:: sch_api_examples/get_set_model_property.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_set_model_property.example
        """
        return clstub().set_model_property_value(
            prop_code_name=prop_code_name, value=value
        )

    def get_model_property_value(self, prop_code_name):
        """
        Return value for specified model property (model configuration).
        Model property is identified by its code name which can be found
        in schematic editor schematic settings dialog when tooltip is shown
        over desired setting option.

        Args:
            prop_code_name (str): Model property code name.

        Returns:
            Value for model property.

        Raises:
            SchApiItemNotFoundException if specified model property can't be
            found.

        **Example:**

        .. literalinclude:: sch_api_examples/get_set_model_property.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_set_model_property.example
        """
        return clstub().get_model_property_value(prop_code_name=prop_code_name)

    def get_component_type_name(self, comp_handle):
        """
        Return component type name.

        Args:
            comp_handle(ItemHandle): Component handle.

        Returns:
            Component type name as string, empty string if component has not
            type (e.g. component is user subsystem).

        Raises:
            SchApiItemNotFoundException if specified component  can't be found.

        **Example:**

        .. literalinclude:: sch_api_examples/get_component_type_name.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_component_type_name.example
        """
        return clstub().get_component_type_name(comp_handle=comp_handle)

    def get_item(self, name, parent=None, item_type=ITEM_ANY):
        """
        Get item handle for item named ``name`` from parent ``parent_handle``.

        .. note::
            ``parent`` is optional if not specified root scheme
            will be used.

        .. note::
            ``item_type`` is optional parameter, it can be used to
            specify type of item to get handle of. It accepts constant
            which defines item type (See `Schematic API constants`_)

        Args:
            name(str): Item name.
            parent(ItemHandle): Parent handle.
            item_type(str): Item type constant.

        Returns:
            Item handle (ItemHandle) if found, None otherwise.

        Raises:
            SchApiException
            1. if there is multiple items found, for example
            component has sub-component named exactly the same as component
            terminal. In that case specify ``item_type`` to remove ambiguity.
            2. if items from locked component are requested.

        **Example:**

        .. literalinclude:: sch_api_examples/get_item.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_item.example
        """
        return clstub().get_item(name=name, parent=parent, item_type=item_type)

    def info(self, msg, context=None):
        """
        Function signals informative messages.

        Args:
            msg (str): Message string.

            context (ItemHandle): Handle for context item.

        Returns:
            None

        **Example:**

          .. literalinclude:: sch_api_examples/info.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/info.example
        """
        return clstub().info(msg=msg, context=context)

    def warning(self, msg, kind=WARNING_GENERAL, context=None):
        """
        Signals some warning condition.

        Args:
            msg (str): Message string.

            kind (str): Kind of warning.

            context (ItemHandle): Handle for context item.

        Returns:
            None

        Raises:
            SchApiItemNotFoundException if context item can't be found.

        **Example:**

          .. literalinclude:: sch_api_examples/warning.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/warning.example
        """
        return clstub().warning(msg=msg, kind=kind, context=context)

    def error(self, msg, kind=ERROR_GENERAL, context=None):
        """
        Signals some error condition.

        Args:
            msg (str): Message string.

            kind (str): Error kind constant.

            context (ItemHandle): Handle for context item.

        Returns:
            None

        **Example:**

        .. literalinclude:: sch_api_examples/error.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/error.example
        """
        return clstub().error(msg=msg, kind=kind, context=context)

    def get_parent(self, item_handle):
        """
        Returns parent handle for provided handle.

        Args:
            item_handle(ItemHandle): Item handle object.

        Returns:
            Parent ItemHandle object.

        Raises:
            SchApiException if provided handle is not valid or if item
            represented by handle doesn't have parent.

        **Example:**

        .. literalinclude:: sch_api_examples/get_parent.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_parent.example
        """
        return clstub().get_parent(item_handle=item_handle)

    @staticmethod
    def fqn(*args):
        """
        Joins multiple provided arguments using FQN separator between them.

        Args:
            *args: Variable number of string arguments.

        Returns:
            Joined string.

        **Example:**

        .. literalinclude:: sch_api_examples/fqn.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/fqn.example
        """
        parts = (p for arg in args for p in arg.split(FQN_SEP) if p)
        return FQN_SEP.join(parts)

    def get_name(self, item_handle):
        """
        Get name of item specified by ``item_handle``.

        Args:
            item_handle (ItemHandle): Item handle.

        Returns:
            Item name.

        **Example:**

        .. literalinclude:: sch_api_examples/get_name.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_name.example
        """
        return clstub().get_name(item_handle=item_handle)

    def set_name(self, item_handle, name):
        """
        Set name for item.

        Args:
            item_handle (ItemHandle): Item handle.

            name (str): Name to set.

        Returns:
            None

        Raises:
            SchApiItemNameExistsException if another item already has
            provided name.
            SchApiException in case when item pointed by item_handle doesn't
            have name attribute or if some other item already has provided name.

        **Example:**

        .. literalinclude:: sch_api_examples/set_name.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/set_name.example
        """
        return clstub().set_name(item_handle=item_handle, name=name)

    def show_name(self, item_handle):
        """
        Makes the schematic item's name visible.
        Args:
            item_handle (ItemHandle): ItemHandle object.

        Returns:
            None

        Raises:
            SchApiException if the item associated with the passed ItemHandle
            is not a NameableMixin object.

        **Example:**

        .. literalinclude:: sch_api_examples/show_hide_name.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/show_hide_name.example
        """
        return clstub().show_name(item_handle=item_handle)

    def hide_name(self, item_handle):
        """
        Makes the schematic item's name invisible.

        Args:
            item_handle (ItemHandle): ItemHandle object.

        Returns:
            None

        Raises:
            SchApiException if the item associated with the passed ItemHandle
            is not a NameableMixin object.

        **Example:**

        .. literalinclude:: sch_api_examples/show_hide_name.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/show_hide_name.example
        """
        return clstub().hide_name(item_handle=item_handle)

    def is_name_visible(self, item_handle):
        """
        Get the current name visibility of the schematic item.
        Args:
            item_handle (ItemHandle): ItemHandle object.

        Returns:
            bool

        Raises:
            SchApiException if the item associated with the passed ItemHandle
            is not a NameableMixin object.

        **Example:**

        .. literalinclude:: sch_api_examples/show_hide_name.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/show_hide_name.example
        """
        return clstub().is_name_visible(item_handle=item_handle)

    def set_description(self, item_handle, description):
        """
        Set description for item specified by ``item_handle``.

        Args:
            item_handle(ItemHandle): ItemHandle object.

            description(str): Item description.

        Returns:
            None

        Raises:
            SchApiItemNotFoundException when item can't be found.
            SchApiException in case when item pointed by item_handle doesn't
            have description attribute, or provided item handle is invalid.

        **Example:**

        .. literalinclude:: sch_api_examples/get_set_description.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_set_description.example
        """
        return clstub().set_description(
            item_handle=item_handle, description=description
        )

    def get_description(self, item_handle):
        """
        Returns description for item specified by ``item_handle``.

        Args:
            item_handle(ItemHandle): ItemHandle object.

        Returns:
            Item description.

        Raises:
            SchApiItemNotFoundException when item can't be found.
            SchApiException in case when item pointed by item_handle doesn't
            have description attribute, or provided item handle is invalid.

        **Example:**

        .. literalinclude:: sch_api_examples/get_set_description.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_set_description.example
        """
        return clstub().get_description(item_handle=item_handle)

    def get_model_file_path(self):
        """
        Args:
            None

        Returns:
            Model file path as a string (empty string if
             model is not yet saved).

        **Example:**

        .. literalinclude:: sch_api_examples/get_model_file_path.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_model_file_path.example
        """
        return clstub().get_model_file_path()

    def get_items(self, parent=None, item_type=None):
        """
        Return handles for all items contained in parent component
        specified using ``parent`` handle, optionally filtering items based
        on type, using ``item_type``. ``item_type`` value is constant, see
        `Schematic API constants`_ for details.

        .. note::
            Properties and terminals are also considered child items of
            parent component. You can get collection of those if ``item_type``
            is specified to respective constants.

        .. note::
            If parent is not specified top level scheme will be used as
            parent.

        .. note::
            Items are not recursively returned.

        Args:
            parent(ItemHandle): Parent component handle.
            item_type(str): Constant specifying type of items. If not
                provided, all items are included.

        Returns:
            List of item handles.

        Raises:
            SchApiException, if items from locked component are requested.

        **Example:**

        .. literalinclude:: sch_api_examples/get_items.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_items.example
        """
        return clstub().get_items(parent=parent, item_type=item_type)

    def get_mask(self, item_handle):
        """
        Returns the mask of the component specified by ``item_handle``.

        Args:
            item_handle (ItemHandle): component's ItemHandle

        Returns:
            Mask item handle (if present on the component) or None.

        Raises:
            SchApiException if the passed item_handle (ItemHandle) is not
            an ItemHandle of a component, or if the component is locked.

        **Example:**

          .. literalinclude:: sch_api_examples/get_mask.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_mask.example
        """
        return clstub().get_mask(item_handle=item_handle)

    def set_handler_code(self, item_handle, handler_name, code):
        """
        Sets handler code ``code`` to handler named ``handler_name``
        on item ``item_handle``.

        Args:
            item_handle(ItemHandle): ItemHandle object.

            handler_name(str): Handler name -
                constant HANDLER_* from schematic api const module.

            code(str): Handle code.

        Returns:
            None

        Raises:
            SchApiItemNotFound if item can't be found or handler can't
            be found (by name).
            SchApiException if item handle is invalid, or handler can't be set
            for specified item (for example if handler setting is forbidden).

        **Example:**

        .. literalinclude:: sch_api_examples/get_set_handler_code.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_set_handler_code.example
        """
        return clstub().set_handler_code(
            item_handle=item_handle, handler_name=handler_name, code=code
        )

    def get_handler_code(self, item_handle, handler_name):
        """
        Returns handler code for a handler named ``handler_name`` defined
        on item specified by ``item_handle``.

        Args:
            item_handle(ItemHandle): ItemHandle object.
            handler_name(str): Handler name -
                constant HANDLER_* from schematic api const module.

        Returns:
            Handler code as a string.

        Raises:
            SchApiItemNotFound if item can't be found or handler can't
            be found (by name).
            SchApiException if item handle is invalid, or handler code
            can't be read from specified item.

        **Example:**

        .. literalinclude:: sch_api_examples/get_set_handler_code.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_set_handler_code.example
        """
        return clstub().get_handler_code(
            item_handle=item_handle, handler_name=handler_name
        )

    def set_model_init_code(self, code):
        """
        Sets model initialization code.

        Args:
            code(str): Model initialization code as string.

        Returns:
            None

        Raises:
            SchApiException if there is no active model.

        **Example:**

        .. literalinclude:: sch_api_examples/set_model_init_code.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/set_model_init_code.example
        """
        return clstub().set_model_init_code(code=code)

    def create_property(
        self,
        item_handle,
        name,
        label="",
        widget=WIDGET_EDIT,
        combo_values=(),
        evaluate=True,
        enabled=True,
        supported=True,
        visible=True,
        serializable=True,
        tab_name="",
        unit="",
        button_label="",
        previous_names=(),
        description="",
        require="",
        type="",  # noqa: A002
        default_value=None,
        min_value=None,
        max_value=None,
        keepline=False,
        ignored=False,
        skip=None,
        skip_step=None,
        section=None,
        vector=False,
        tunable=False,
        index=None,
        allowed_values=None,
        context_typhoonsim=None,
        context_real_time=None,
    ):
        """
        Create property on item specified by ``item_handle``.

        Parameter ``property_widget`` expects constants as value.
        (See `Schematic API constants`_).

        Args:
            item_handle(ItemHandle): ItemHandle object.
            name(str): Name of property.
            label(str): Optional label for property.
            widget(str): String constant, specifies which type
                of GUI widget will represent property.
            combo_values(tuple): When widget is set to WIDGET_COMBO,
                this parameter specifies allowed combo values.
            evaluate(bool): Specify if property will be evaluated.
            enabled(bool): Specify if this property is enabled
                (grayed out or not on GUI).
            supported(bool): Specify if property is supported.
            visible(bool): Specify if property will be visible.
            serializable(bool): Specify if property will be included during
                serialization to json.
            tab_name:(str): Optional name for tab where property will
                be displayed (on GUI).
            unit(str): Optional unit for property.
            button_label(str): Defines label if property widget is button.
            previous_names(tuple): Tuple containing previous names of the property.
            description(str): Description for the property.
            require(str): Specify require string, that is, on which toolbox
                this property relies.
            type(str): Type of the property. (noqa: A002)
            default_value: Default value for the property.
            min_value: Minimum value for the property.
            max_value: Maximum value for the property.
            keepline(bool): Specify if the property should keep its line in the GUI.
            ignored(bool): Specify if the property is ignored.
            skip(str): Specify if the property should be skipped.
            skip_step: Specify the step to skip.
            section: The section of this property within a tab.
            vector(bool): Specify if the property is a vector.
            tunable(bool): Specify if the property is tunable.
            index(int): Specify index (position) of new property in a
                list of all properties. Property position is 0 index based.
                If index is negative, property will be placed on 0th position.
                Otherwise, if index is larger than last index, property index
                will be set after the last one.
            allowed_values(tuple): Tuple of allowed values for the property.
                If current value is among allowed, require string won't be
                evaluated during validation.
            context_typhoonsim(dict): Context dict for typhoonsim context.
                It can contain given keys: require (str), visible (str),
                nonsupported(bool), nonvisible(bool), ignored(bool) and
                allowed_values(tuple).
            context_real_time(dict): Context dict for typhoonsim context.
                It can contain given keys: require (str), visible (str),
                nonsupported(bool), nonvisible(bool), ignored(bool) and
                allowed_values(tuple).

        Returns:
            Property handle for newly created property.

        Raises:
            SchApiItemNotFound if item can't be found.
            SchApiException if item handle is invalid, item handle doesn't
            support property creation on it.
            SchApiItemNameExistsException if  property with same name already
            exists.

        **Example:**

        .. literalinclude:: sch_api_examples/create_remove_property.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/create_remove_property.example
        """
        return clstub().create_property(
            item_handle=item_handle,
            name=name,
            label=label,
            widget=widget,
            combo_values=combo_values,
            evaluate=evaluate,
            enabled=enabled,
            supported=supported,
            visible=visible,
            serializable=serializable,
            tab_name=tab_name,
            unit=unit,
            button_label=button_label,
            previous_names=previous_names,
            description=description,
            require=require,
            type=type,
            default_value=default_value,
            min_value=min_value,
            max_value=max_value,
            keepline=keepline,
            ignored=ignored,
            skip=skip,
            skip_step=skip_step,
            vector=vector,
            tunable=tunable,
            index=index,
            allowed_values=allowed_values,
            context_typhoonsim=context_typhoonsim,
            context_real_time=context_real_time,
        )

    def remove_property(self, item_handle, name):
        """
        Remove property named by ``name`` from item specified
        by ``item_handle``.

        Args:
            item_handle(ItemHandle): ItemHandle object.

            name(str): Property name.

        Returns:
            None

        Raises:
            SchApiItemNotFound if item or property can't be found.
            SchApiException if item handle is invalid.

        **Example:**

        .. literalinclude:: sch_api_examples/create_remove_property.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/create_remove_property.example
        """
        return clstub().remove_property(item_handle=item_handle, name=name)

    def get_label(self, item_handle):
        """
        Get label for item specified by ``item_handle``.

        Args:
            item_handle(ItemHandle): Item handle.

        Returns:
            Item label as string.

        Raises:
            SchApiItemNotFoundException if item can't be found.
            SchApiException if provided item doesn't have label.

        **Example:**

        .. literalinclude:: sch_api_examples/get_set_label.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_set_label.example
        """
        return clstub().get_label(item_handle=item_handle)

    def set_label(self, item_handle, label):
        """
        Set label for item specified by ``item_handle``.

        Args:
            item_handle(ItemHandle): Item handle.

            label(str): Label string to set.

        Returns:
            None

        Raises:
            SchApiItemNotFoundException if item can't be found.
            SchApiException if provided item doesn't have label attribute.

        **Example:**

        .. literalinclude:: sch_api_examples/get_set_label.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_set_label.example
        """
        return clstub().set_label(item_handle=item_handle, label=label)

    def get_fqn(self, item_handle):
        """
        Get fully qualified name for item specified by ``item_handle``.

        Args:
            item_handle (ItemHandle): Item handle.

        Returns:
            Fully qualified name as string.

        **Example:**

        .. literalinclude:: sch_api_examples/get_fqn.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_fqn.example
        """
        return clstub().get_fqn(item_handle=item_handle)

    def get_sub_level_handle(self, item_handle):
        """
        Returns the handle that is one level below in hierarchy in relation
        to given ``item_handle``.

        Args:
            item_handle(ItemHandle): ItemHandle object.

        Returns:
            ItemHandle object.

        Raises:
            SchApiException if there is some error.

        **Example:**

        .. literalinclude:: sch_api_examples/get_sub_level_handle.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_sub_level_handle.example
        """
        raise SchApiException(
            "get_sub_level_handle(): Calling of this method is not"
            " supported from client side."
        )

    def term(self, comp_handle, term_name):
        """
        Make a unique identity handle for some terminal. Used in place where
        terminal fqn is expected.

        Args:
            comp_handle (ItemHandle): Component handle.

            term_name (str): Terminal name.

        Returns:
            Terminal handle.

        **Example:**

        .. literalinclude:: sch_api_examples/term.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/term.example
        """
        return clstub().term(comp_handle=comp_handle, term_name=term_name)

    def prop(self, item_handle, prop_name):
        """
        Create property handle.

        Args:
            item_handle(ItemHandle): Handle object representing property
                container (e.g. mask or component).

            prop_name(str): Property name.

        Returns:
            Property handle.

        **Example:**

        .. literalinclude:: sch_api_examples/prop.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/prop.example
        """
        return clstub().prop(item_handle=item_handle, prop_name=prop_name)

    def find_connections(self, connectable_handle1, connectable_handle2=None):
        """
        Return all connection handles which are connected to
        ``connectable_handle1``.

        If ``connectable_handle2`` is also specified then return handles
        for shared connections (ones that are connecting ``connectable_handle1``
        and ``connectable_handle2`` directly.

        Args:
            connectable_handle1 (ItemHandle): ConnectableMixin handle.

            connectable_handle2 (ItemHandle): Other connectable handle.

        Returns:
            List of connection handles.

        Raises:
            SchApiItemNotFound if one or both connectables can't be found.

        **Example:**

        .. literalinclude:: sch_api_examples/find_connections.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/find_connections.example

        """
        return clstub().find_connections(
            connectable_handle1=connectable_handle1,
            connectable_handle2=connectable_handle2,
        )

    def is_subsystem(self, comp_handle):
        """
        Returns whether component specified by ``comp_handle`` is a
        subsystem (composite) component.

        .. note::
            Component is an atomic component if it's not composite.

        Args:
            comp_handle (ItemHandle): Component handle.

        Returns:
            ``True`` if component is subsystem, ``False`` otherwise.

        Raises:
            SchApiItemNotFoundException if component is not found.

        **Example:**

        .. literalinclude:: sch_api_examples/is_subsystem.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/is_subsystem.example
        """
        return clstub().is_subsystem(comp_handle=comp_handle)

    # * * *  * * * * * * * * * * * * * * * * * * *
    #                Component                   *
    # * * *  * * * * * * * * * * * * * * * * * * *
    def create_component(
        self,
        type_name,
        parent=None,
        name=None,
        rotation=ROTATION_UP,
        flip=FLIP_NONE,
        position=None,
        size=(None, None),
        hide_name=False,
        require="",
        visible="",
        layout="dynamic",
        context_typhoonsim=None,
        context_real_time=None,
    ):
        """
        Creates component using provided type name inside the container
        component specified by `parent`. If `parent` is not
        specified top level parent (scheme) will be used as parent.

        Parameters ``rotation`` and ``flip`` expects respective constants as
        value (See `Schematic API constants`_).

        Args:
            type_name (str): Component type name, specifies which component to
                create.

            parent (ItemHandle): Container component handle.

            name (str): Component name.

            rotation (str): Rotation of the component.

            flip(str): Flip state of the component.

            position (sequence): X and Y coordinates of component.

            size (sequence): Width and height of component.

            hide_name (bool): component name will be hidden if this flag is
                set to True.

            require(str): Specify require string, that is, on which toolbox
                this property relies. Ignored for library components.

            visible(str): Specify visible string, that is, on which toolbox
                this property relies. Ignored for library components.

            layout(str): Specify layout string, which can be static or dynamic.
                Ignored for library components.

            context_typhoonsim(dict): Context dict for typhoonsim context.
                It can contain given keys: require (str), visible (str),
                nonsupported(bool), nonvisible(bool), ignored(bool) and
                allowed_values(tuple).

            context_real_time(dict): Context dict for typhoonsim context.
                It can contain given keys: require (str), visible (str),
                nonsupported(bool), nonvisible(bool), ignored(bool) and
                allowed_values(tuple).

        Returns:
            Handle for created component.

        Raises:
            SchApiException in case when component creation fails.

        **Example:**

        .. literalinclude:: sch_api_examples/create_component.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/create_component.example
        """
        return clstub().create_component(
            type_name=type_name,
            parent=parent,
            name=name,
            rotation=rotation,
            flip=flip,
            position=position,
            size=size,
            hide_name=hide_name,
            require=require,
            visible=visible,
            layout=layout,
            context_typhoonsim=context_typhoonsim,
            context_real_time=context_real_time,
        )

    def replace_component(
        self,
        comp_handle,
        new_comp_type_name,
        port_mapping=None,
        visual_attributes=None,
        property_values=None,
    ):
        """
        Replaces a component of the model while keeping the original connections if
        possible.
        In case the new component doesn't match the number of terminals of the original
        component on each side, a dictionary (port_mapping) must be provided to map the
        original terminals to the new ones.

        new_comp_type_name (str): the library component to replace the original with

        port_mapping (dict): Maps terminals on the original component to terminals
            on the new one. Entries are
                {original_terminal_name: new_terminal_name}
            for each terminal

        visual_attributes (dict): contains the visual information of the new component.
            For missing entries in the dictionary, the original component values
            will be used instead. Keys:
            {
                "name" (str): The name of the new component
                "rotation" (str): Rotation of the component
                "flip" (str): Flip state of the component
                "offset" (float tuple):
                    Position offset from the original component position
            }

        property_values (dict): contains property values to be set on the new component.
            Entries must have the format {property_name: value}.

        Returns:
            Handle for the new component.

        Raises:
            SchApiException in case the component replacement fails.

        **Example:**

        .. literalinclude:: sch_api_examples/replace_component.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/replace_component.example

        """
        return clstub().replace_component(
            comp_handle=comp_handle,
            new_comp_type_name=new_comp_type_name,
            port_mapping=port_mapping,
            visual_attributes=visual_attributes,
            property_values=property_values,
        )

    def create_port(
        self,
        name=None,
        parent=None,
        label=None,
        kind=KIND_PE,
        direction=DIRECTION_OUT,
        dimension=(1,),
        sp_type=SP_TYPE_REAL,
        terminal_position=("left", "auto"),
        rotation=ROTATION_UP,
        flip=FLIP_NONE,
        hide_name=False,
        position=None,
    ):
        """
        Create port inside the container component specified by `parent`.

        Parameters ``kind``, ``direction``, ``sp_type and``, ``rotation`` and
        ``flip`` expects respective constants as values.
        (See `Schematic API constants`_).

        Args:
            name (str): Port name.

            parent (ItemHandle): Container component handle.

            label(str): Optional label to use as a terminal name instead of
                port name.

            kind (str): Port kind (signal processing or power electronic kind).

            direction (str): Port direction (applicable only for signal
                processing ports)

            dimension(tuple): Specify dimension.

            sp_type (str): SP type for port.

            terminal_position (tuple): Specify position of port based terminal
                on component.

            rotation (str): Rotation of the port.

            flip(str): Flip state of the port.

            hide_name (bool): Indicate if label for terminal (created on
                component as a result of this port) should be hidden.

            position (sequence): X and Y coordinates of port.

        Returns:
            Handle for created port.

        Raises:
            SchApiException in case port creation fails (for example when
            port is created at the top level parent or any other cause of
            error).

        **Example:**

        .. literalinclude:: sch_api_examples/create_port.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/create_port.example
        """
        return clstub().create_port(
            name=name,
            parent=parent,
            label=label,
            kind=kind,
            direction=direction,
            dimension=dimension,
            sp_type=sp_type,
            terminal_position=terminal_position,
            rotation=rotation,
            flip=flip,
            hide_name=hide_name,
            position=position,
        )

    def set_port_properties(
        self, item_handle, terminal_position=None, hide_term_label=None, term_label=""
    ):
        """
        Set port properties (as seen in port properties dialog).

        Args:
            item_handle(ItemHandle): Port item handle.

            terminal_position(tuple): Specify position of terminal based on
                this port.

            hide_term_label(bool): Indicate if port terminal label is shown.

            term_label(str): Specify alternate terminal label.

        Returns:
            None

        Raises:
            SchApiException in case when provided item_handle is not for port.

        **Example:**

        .. literalinclude:: sch_api_examples/set_port_properties.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/set_port_properties.example
        """
        return clstub().set_port_properties(
            item_handle=item_handle,
            terminal_position=terminal_position,
            hide_term_label=hide_term_label,
            term_label=term_label,
        )

    def set_tag_properties(self, item_handle, value=None, scope=None):
        """
        Set tag properties (like scope and value).

        Args:
            item_handle(ItemHandle): Tag item handle.

            value(str): Tag value.

            scope(str): Tag scope.

        Returns:
            None

        Raises:
            SchApiException in case when provided item_handle is not for tag.

        **Example:**

        .. literalinclude:: sch_api_examples/set_tag_properties.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/set_tag_properties.example
        """
        return clstub().set_tag_properties(
            item_handle=item_handle,
            value=value,
            scope=scope,
        )

    def create_connection(self, start, end, name=None, breakpoints=None):
        """
        Create connection with specified start and end connectable handles.
        ConnectableMixin can be component terminal, junction, port or tag.

        .. note::
            Both start and end must be of same kind and they both must be
            located in same parent.

        Args:
            start (ItemHandle): Handle for connection start.

            end (ItemHandle): Handle for connection end.

            name (str): Connection name.

            breakpoints(list): List of coordinate tuples (x, y), used to
                represent connection breakpoints.

        Returns:
            Handle for created connection.

        Raises:
            SchApiException in case when connection creation fails.
            SchApiDuplicateConnectionException in case when provided
            connectables is already connected.

        **Example:**

        .. literalinclude:: sch_api_examples/create_connection.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/create_connection.example
        """
        return clstub().create_connection(
            start=start, end=end, name=name, breakpoints=breakpoints
        )

    def get_breakpoints(self, item_handle):
        """
        Returns a list of breakpoint coordinates for a given item handle.

        Args:
            item_handle (ItemHandle): Item handle.

        Returns:
            list

        Raises:
            SchApiItemNotFoundException when specified item can't be found.

        **Example:**

        .. literalinclude:: sch_api_examples/get_breakpoints.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_breakpoints.example
        """
        return clstub().get_breakpoints(item_handle=item_handle)

    def create_junction(self, name=None, parent=None, kind=KIND_PE, position=None):
        """
        Create junction inside container component specified by `parent`.

        Parameter ``kind`` expects respective constants as
        value (See `Schematic API constants`_).

        Args:
            name (str): Junction name.

            parent (ItemHandle): Container component handle.

            kind (str): Kind of junction (can be signal processing or
                power electronic kind)

            position (sequence): X and Y coordinates of junction in the
                container.

        Returns:
            Handle for created junction.

        Raises:
            SchApiException in case when junction creation fails.

        **Example:**

        .. literalinclude:: sch_api_examples/create_junction.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/create_junction.example
        """
        return clstub().create_junction(
            name=name, parent=parent, kind=kind, position=position
        )

    def create_tag(
        self,
        value,
        name=None,
        parent=None,
        scope=TAG_SCOPE_GLOBAL,
        kind=KIND_PE,
        direction=None,
        rotation=ROTATION_UP,
        flip=FLIP_NONE,
        position=None,
        hide_name=False,
    ):
        """
        Create tag inside container component specified by `parent` handle..

        Parameters ``scope``, ``kind``, ``direction``, ``rotation``
        expects respective constants as values (See `Schematic API constants`_).

        Args:
            value (str): Tag value, used to match with other tags.

            name (str): Tag name.

            parent (ItemHandle): Container component handle.

            scope (str): Tag scope, specifies scope in which matching tag is
             searched.

            kind (str): Kind of tag (can be either KIND_SP or KIND_PE).

            direction (str): Tag direction (for signal processing tags). When signal
                processing tag is created, this parameter will get a value of
                DIRECTION_IN if no value was provided.

            rotation (str): Rotation of the tag, can be one of following:
                ROTATION_UP, ROTATION_DOWN, ROTATION_LEFT and ROTATION_RIGHT.
            flip(str): Flip state of the tag.

            position (sequence): X and Y coordinates of tag in the container.

            hide_name (bool): tag name will be hidden if this flag is
                set to True.
        Returns:
            Handle for created tag.

        Raises:
            SchApiException in case when tag creation fails.

        **Example:**

        .. literalinclude:: sch_api_examples/create_tag.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/create_tag.example
        """
        return clstub().create_tag(
            value=value,
            name=name,
            parent=parent,
            scope=scope,
            kind=kind,
            direction=direction,
            rotation=rotation,
            flip=flip,
            position=position,
            hide_name=hide_name,
        )

    def create_comment(self, text, parent=None, name=None, position=None):
        """
        Create comment with provided text inside the container component
        specified by `parent`.

        Args:
            text (str): Comment text.

            parent (ItemHandle): Parent component handle.

            name (str): Comment's name.

            position (sequence): X and Y coordinates of tag in the container.

        Returns:
            Handle for created comment.

        Raises:
            SchApiException in case when connection creation fails.

        **Example:**

        .. literalinclude:: sch_api_examples/create_comment.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/create_comment.example
        """
        return clstub().create_comment(
            text=text, parent=parent, name=name, position=position
        )

    def get_comment_text(self, comment_handle):
        """
        Get comment text for a given comment handle.

        Args:
            comment_handle(ItemHandle): item handle for a comment.

        Returns:
            str

        Raises:
            SchApiException in case comment_handle is not a handle for a
                component.

        **Example:**

        .. literalinclude:: sch_api_examples/get_comment_text.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_comment_text.example
        """
        return clstub().get_comment_text(comment_handle=comment_handle)

    def create_mask(self, item_handle):
        """
        Create a mask on item specified by ``item_handle``.

        Args:
            item_handle(ItemHandle): ItemHandle object.

        Returns:
            Mask handle object.

        Raises:
            SchApiException if item doesn't support mask creation (on it) or
            item_handle is invalid.
            SchApiItemNotFoundException when item can't be found.

        **Example:**

        .. literalinclude:: sch_api_examples/create_mask.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/create_mask.example
        """
        return clstub().create_mask(item_handle=item_handle)

    def remove_mask(self, item_handle):
        """
        Removes mask from item denoted by ``item_handle``.

        Args:
            item_handle:(ItemHandle): ItemHandle object.

        Returns:
            None

        Raises:
            SchApiItemNotFoundException when item can't be found or if item
            doesn't have a mask.

            SchApiException if:
            1) item doesn't support mask creation (on it).
            2) item_handle is invalid.
            3) Mask can't be removed because of protection.

        **Example:**

        .. literalinclude:: sch_api_examples/remove_mask.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/remove_mask.example
        """
        return clstub().remove_mask(item_handle=item_handle)

    def set_position(self, item_handle, position):
        """
        Sets item (specified by ``item_handle``) position.

        .. note::
            Position coordinates are rounded to nearest value which
            are divisible by grid resolution (this is done because graphical
            representation of scheme assume that positions respect this behavior).


        Args:
            item_handle (ItemHandle): Item handle.

            position (sequence): Position to set.

        Returns:
            None

        Raises:
            SchApiItemNotFoundException when specified item can't be found.

        **Example:**

        .. literalinclude:: sch_api_examples/get_set_position.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_set_position.example
        """
        return clstub().set_position(item_handle=item_handle, position=position)

    def get_position(self, item_handle):
        """
        Gets item position.

        Args:
            item_handle (ItemHandle): Item handle.

        Returns:
            Position in tuple form (x, y).

        Raises:
            SchApiItemNotFoundException when specified item can't be found.

        **Example:**

        .. literalinclude:: sch_api_examples/get_set_position.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_set_position.example
        """
        return clstub().get_position(item_handle=item_handle)

    def set_size(self, item_handle, width=None, height=None):
        """
        Sets the size (width/height) of the passed item.
        Args:
            item_handle (ItemHandle): item handle object.
            width (int, float): new width of the item.
            height (int, float): new height of the item.

        Returns:
            None

        Raises:
            SchApiException if the passed width or height are
            below the minimum values.

        **Example:**

        .. literalinclude:: sch_api_examples/get_set_size.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_set_size.example
        """
        return clstub().set_size(item_handle=item_handle, width=width, height=height)

    def get_size(self, item_handle):
        """
        Gets the size (width/height) of the item specified by ``item_handle``.

        Args:
            item_handle (ItemHandle): Item handle object..

        Returns:
            list

        **Example:**

        .. literalinclude:: sch_api_examples/get_set_size.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_set_size.example
        """
        return clstub().get_size(item_handle=item_handle)

    def set_rotation(self, item_handle, rotation):
        """
        Sets the rotation of the item (specified by ``item_handle``).

        Args:
            item_handle (ItemHandle): Item handle.
            rotation (string): one of ("up", "right", "left", "down")

        Returns:
            None

        Raises:
            SchApiItemNotFoundException when specified item can't be found.
            SchApiException when the provided item type is not valid.

        **Example:**

        .. literalinclude:: sch_api_examples/get_set_rotation.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_set_rotation.example
        """

        return clstub().set_rotation(item_handle=item_handle, rotation=rotation)

    def get_rotation(self, item_handle):
        """
        Gets the rotation of the item (specified by ``item_handle``).

        Args:
            item_handle (ItemHandle): Item handle.

        Returns:
            rotation (string): one of ("up", "right", "left", "down")

        Raises:
            SchApiItemNotFoundException when specified item can't be found.
            SchApiException when the provided item type is not valid.

        **Example:**

        .. literalinclude:: sch_api_examples/get_set_rotation.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_set_rotation.example
        """

        return clstub().get_rotation(item_handle=item_handle)

    def set_flip(self, item_handle, flip):
        """
        Gets the flip status of the item (specified by ``item_handle``).

        Args:
            item_handle (ItemHandle): Item handle.
            flip (string):
                one of ("flip_none", "flip_horizontal", "flip_vertical", "flip_both")

        Returns:
            None

        Raises:
            SchApiItemNotFoundException when specified item can't be found.
            SchApiException when the provided item type or the flip value are invalid.

        **Example:**

        .. literalinclude:: sch_api_examples/get_set_flip.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_set_flip.example
        """

        return clstub().set_flip(item_handle=item_handle, flip=flip)

    def get_flip(self, item_handle):
        """
        Gets the flip status of the item (specified by ``item_handle``).

        Args:
            item_handle (ItemHandle): Item handle.

        Returns:
            flip (string):
                one of ("flip_none", "flip_horizontal", "flip_vertical", "flip_both")

        Raises:
            SchApiItemNotFoundException when specified item can't be found.
            SchApiException when the provided item type is not valid.

        **Example:**

        .. literalinclude:: sch_api_examples/get_set_flip.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_set_flip.example
        """

        return clstub().get_flip(item_handle=item_handle)

    def get_calculated_terminal_position(self, item_handle):
        """
        Gets the X and Y values of the terminal referenced to the center point
        of the parent component.

        Args:
            item_handle (ItemHandle): Item handle of a port or a terminal.

        Returns:
            Calculated position coordinates in list format [x, y]

        Raises:
            SchApiItemNotFoundException when specified item can't be found.
            SchApiException when the provided item type is not valid.

        **Example:**

        .. literalinclude:: sch_api_examples/get_calculated_terminal_position.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_calculated_terminal_position.example
        """

        return clstub().get_calculated_terminal_position(item_handle=item_handle)

    def delete_item(self, item_handle):
        """
        Delete item named specified by ``item_handle``.

        Args:
            item_handle (ItemHandle): Item handle.

        Returns:
            None

        Raises:
            SchApiException in case when deletion fails.

        **Example:**

        .. literalinclude:: sch_api_examples/delete_item.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/delete_item.example
        """
        return clstub().delete_item(item_handle=item_handle)

    def exists(self, name, parent=None, item_type=ITEM_ANY):
        """
        Checks if item named ``name`` is container in parent component
        specified by ``parent`` handle. If parent handle is not provided
        root scheme is used as parent.

        .. note ::
            ``item_type`` is a constant which specify which item type to
            look for. See `Schematic API constants`_.

        Args:
            name (str): Item name to check.

            parent (ItemHandle): Parent handle.

            item_type (str): Item type constant.

        Returns:
            True if item with provided name exists in parent, False otherwise.

        **Example:**

        .. literalinclude:: sch_api_examples/exists.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/exists.example
        """
        return clstub().exists(name=name, parent=parent, item_type=item_type)

    # * * *  * * * * * * * * * * * * * * * * * * *
    #                Properties                  *
    # * * *  * * * * * * * * * * * * * * * * * * *
    def enable_property(self, prop_handle):
        """Sets property as editable.


        .. note ::
            The effect of this function is only visible on the
            Schematic Editor's UI.

        When the property is enabled, it is possible to change its value in
        the dialog. To disable property, use :func:`disable_property`
        function.

        Args:
            prop_handle (ItemHandle): Property handle.

        Returns:
            None

        Raises:


        **Example:**

        .. literalinclude:: sch_api_examples/enable_property.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/enable_property.example
        """
        return clstub().enable_property(prop_handle=prop_handle)

    def disable_property(self, prop_handle):
        """
        Sets property as non-editable.

        .. note::
            The effect of this function is visible only on the Schematic
            Editor's UI.

        When the property is disabled, it is not possible to change its
        value in the dialog. To enable property, use :func:`enable_property`
        function.

        Args:
            prop_handle (ItemHandle): Property handle.

        Returns:
            None

        **Example:**

        .. literalinclude:: sch_api_examples/enable_property.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/enable_property.example
        """
        return clstub().disable_property(prop_handle=prop_handle)

    def is_property_enabled(self, prop_handle):
        """
        Returns True if property is enabled, False otherwise.

        Args:
            prop_handle (ItemHandle): Property handle.

        Returns:
            bool

        **Example:**

        .. literalinclude:: sch_api_examples/enable_property.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/enable_property.example
        """
        return clstub().is_property_enabled(prop_handle=prop_handle)

    def show_property(self, prop_handle):
        """
        Makes component property visible in the component's dialog.

        .. note::
            The effect of this function is visible only on the Schematic
            Editor's UI.

        When this function is called, property will become visible in the
        component's dialog. To hide a property, use :func:`hide_property`
        function.


        Args:
            prop_handle (ItemHandle): Property handle.

        Returns:
            None

        **Example:**

        .. literalinclude:: sch_api_examples/show_hide_property.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/show_hide_property.example
        """
        return clstub().show_property(prop_handle=prop_handle)

    def hide_property(self, prop_handle):
        """
        Makes component property invisible on the component's dialog.

        .. note::
            The effect of this function is visible only in the Schematic
            Editor's UI.

        When this function is called, property will become invisible in the
        component's dialog. To show a property, use :func:`show_property`
        function.

        Args:
            prop_handle (ItemHandle): Property handle.

        **Example:**

        .. literalinclude:: sch_api_examples/show_hide_property.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/show_hide_property.example
        """
        return clstub().hide_property(prop_handle=prop_handle)

    def is_property_visible(self, prop_handle):
        """
        Returns True if component property is visible on the component's
        dialog, False otherwise.

        Args:
            prop_handle (ItemHandle): Property handle.

        Returns:
            ``True`` if property is visible, ``False`` otherwise.

        **Example:**

        .. literalinclude:: sch_api_examples/show_hide_property.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/show_hide_property.example
        """
        return clstub().is_property_visible(prop_handle=prop_handle)

    def enable_property_serialization(self, prop_handle):
        """
        Enable component property serialization to json.

        When this function is called, a property becomes serializable.
        That property will be included in serialized json file
        (during compilation, for example). To disable property serialization,
        use :func:`disable_property_serialization` function.


        Args:
            prop_handle (ItemHandle): Property handle.

        Returns:
            None

        **Example:**

        .. literalinclude:: sch_api_examples/enable_disable_serialization.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/enable_disable_serialization.example
        """
        return clstub().enable_property_serialization(prop_handle=prop_handle)

    def disable_property_serialization(self, prop_handle):
        """
        Disable component property serialization to json.

        When this function is called, a property becomes non-serializable.
        That property will not be included in serialized json file
        (during compilation, for example). To enable property serialization,
        use :func:`enable_property_serialization` function.

        Args:
            prop_handle (ItemHandle): Property handle.

        **Example:**

        .. literalinclude:: sch_api_examples/enable_disable_serialization.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/enable_disable_serialization.example
        """
        return clstub().disable_property_serialization(prop_handle=prop_handle)

    def is_property_serializable(self, prop_handle):
        """
        Returns True if component property is serializable.

        Args:
            prop_handle (ItemHandle): Property handle.

        Returns:
            ``True`` if property is serializable, ``False`` otherwise.

        **Example:**

        .. literalinclude:: sch_api_examples/enable_disable_serialization.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/enable_disable_serialization.example
        """
        return clstub().is_property_serializable(prop_handle=prop_handle)

    def get_conv_prop(self, prop_handle, value=None):
        """
        Converts provided `value` to type which is specified in property
        type specification. If value is not provided property display value
        is used instead.

        Args:
            prop_handle (ItemHandle): Property handle.

            value (str): Value to convert.

        Returns:
            Python object, converted value.

        Raises:
            SchApiException if value cannot be converted.

        **Example:**

        .. literalinclude:: sch_api_examples/get_conv_prop.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_conv_prop.example
        """
        return clstub().get_conv_prop(prop_handle=prop_handle, value=value)

    def get_property_value(self, prop_handle):
        """
        Returns the value of a property.

        Args:
            prop_handle (ItemHandle): Property handle.

        Returns:
            object

        **Example:**

        .. literalinclude:: sch_api_examples/set_get_property_value.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/set_get_property_value.example
        """
        return clstub().get_property_value(prop_handle=prop_handle)

    def get_property_values(self, item_handle):
        """
        Returns all property values for provided component handle
        (in dictionary form).

        Args:
            item_handle(ItemHandle): Component handle.

        Returns:
            dict, where keys are property names, values are property values.

        **Example:**

        .. literalinclude:: sch_api_examples/set_get_property_values.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/set_get_property_values.example
        """
        return clstub().get_property_values(item_handle=item_handle)

    def get_property_default_value(self, prop_handle):
        """
        Returns property default value.

        Args:
            prop_handle (ItemHandle): Property handle.

        Returns:
            Property default value as string.

        Raises:
            SchApiItemNotFoundException if property can't be found.

        **Example:**

        .. literalinclude:: sch_api_examples/get_property_default_value.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_property_default_value.example
        """
        return clstub().get_property_default_value(prop_handle=prop_handle)

    def get_property_type_attributes(self, prop_handle):
        """
        Returns property type attributes.

        Args:
            prop_handle (ItemHandle): Property handle.

        Returns: function will return a dictionary
                 of property type attributes.

        **Example:**

        .. literalinclude:: sch_api_examples/get_property_type_attributes.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_property_type_attributes.example
        """
        return clstub().get_property_type_attributes(prop_handle=prop_handle)

    def _set_property_type_attributes(self, prop_handle, attr_dict):
        """
        NOTE: Private function, when published re-enable examples and output below.
        Set property type attributes by providing a dict where one or more new attribute
        values are assigned.

        Args:
            prop_handle(ItemHandle): Property handle.
            attr_dict(dict): Dictionary where keys are attribute names, and values are one of
              allowed values for each attribute.
        """
        return clstub()._set_property_type_attributes(
            prop_handle=prop_handle, attr_dict=attr_dict
        )

    def set_property_value(self, prop_handle, value):
        """
        Set a new value to the property.

        Args:
            prop_handle (ItemHandle): Property handle.

            value (object): New value.

        **Example:**

        .. literalinclude:: sch_api_examples/set_get_property_value.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/set_get_property_value.example
        """
        return clstub().set_property_value(prop_handle=prop_handle, value=value)

    def set_property_values(self, item_handle, values):
        """
        Sets multiple property values for a provided component.

        Args:
            item_handle(ItemHandle): Component handle.
            values(dict): Dictionary where keys are property names,
                while values are new property values.

        **Example:**

        .. literalinclude:: sch_api_examples/set_get_property_values.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/set_get_property_values.example
        """
        return clstub().set_property_values(item_handle=item_handle, values=values)

    def get_property_disp_value(self, prop_handle):
        """
        Return the display value of the property.

        Args:
            prop_handle (ItemHandle): Property handle.

        Returns:
            str

        **Example:**

        .. literalinclude:: sch_api_examples/set_prop_display_value.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/set_prop_display_value.example
        """
        return clstub().get_property_disp_value(prop_handle=prop_handle)

    def set_property_disp_value(self, prop_handle, value):
        """
        Set property display value.

        Args:
            prop_handle (ItemHandle): Property handle.

            value (str): Value.

        Returns:
            None

        **Example:**

        .. literalinclude:: sch_api_examples/set_prop_display_value.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/set_prop_display_value.example
        """
        return clstub().set_property_disp_value(prop_handle=prop_handle, value=value)

    def get_property_combo_values(self, prop_handle):
        """
        Returns combo_values list for property specified by ``prop_handle``.

        .. note::
            This function works for properties which have widget
            set to combo.

        Args:
            prop_handle (ItemHandle): Property handle.

        Returns:
            Sequence of property combo values.

        Raises:
            SchApiException if property widget is not combo.

        **Example:**

        .. literalinclude:: sch_api_examples/get_set_prop_combo_values.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_set_prop_combo_values.example
        """
        return clstub().get_property_combo_values(prop_handle=prop_handle)

    def set_property_combo_values(self, prop_handle, combo_values):
        """
        Sets property combo values to provided one.

        .. note::
            Property specified by ``prop_handle`` must have widget set
            to combo.

        Args:
            prop_handle (ItemHandle): Property handle.

            combo_values (sequence): Sequence of new combo values.

        Returns:
            None

        Raises:
            SchApiException when functions is called with property handle
            where property widget is not combo.

        **Example:**

        .. literalinclude:: sch_api_examples/get_set_prop_combo_values.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_set_prop_combo_values.example
        """
        return clstub().set_property_combo_values(
            prop_handle=prop_handle, combo_values=combo_values
        )

    def set_property_value_type(self, prop_handle, new_type):
        """
        Set a new value type to the property.

        Args:
            prop_handle (ItemHandle): Property handle.

        Returns:
            None

        Raises:
            SchApiException if new type is invalid

        **Example:**

        .. literalinclude:: sch_api_examples/get_set_prop_value_type.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_set_prop_value_type.example
        """
        return clstub().set_property_value_type(
            prop_handle=prop_handle, new_type=new_type
        )

    def get_property_value_type(self, prop_handle):
        """
        Returns the property value type.

        Args:
            prop_handle (ItemHandle): Property handle.

        Returns:
            str

        Raises:
            SchApiException if property handle is invalid

        **Example:**

        .. literalinclude:: sch_api_examples/get_set_prop_value_type.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_set_prop_value_type.example
        """
        return clstub().get_property_value_type(prop_handle=prop_handle)

    def get_item_visual_properties(self, item_handle):
        """
        Returns available visual properties for the provided item.
        Supported item types and returned properties are:

        Component: position, rotation, flip, size
        Tag: position, rotation, flip, size
        Port: position, rotation, flip, terminal_position, calulated_terminal_position
        Terminal: terminal_position, calulated_terminal_position

        Args:
            item_handle(ItemHandle): Schematic item handle.

        Returns:
            A dictionary with the visual properties.

        Raises:
            SchApiItemNotFoundException when item can't be found.
            SchApiException when the passed item_handle is invalid.

        **Example:**

        .. literalinclude:: sch_api_examples/get_set_item_visual_properties.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_set_item_visual_properties.example
        """
        return clstub().get_item_visual_properties(item_handle=item_handle)

    def set_item_visual_properties(self, item_handle, prop_dict):
        """
        Sets visual properties defined on prop_dict for the provided item.
        The following entries are accepted, depending on the item type:

        Component: position, rotation, flip, size
        Tag: position, rotation, flip, size
        Port: position, rotation, flip, terminal_position

        Args:
            item_handle(ItemHandle): Schematic item handle.

        Returns:
           None.

        Raises:
            SchApiItemNotFoundException when item can't be found.
            SchApiException when the type is not supported or at least one
            of the properties cannot be set.

        **Example:**

        .. literalinclude:: sch_api_examples/get_set_item_visual_properties.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_set_item_visual_properties.example
        """
        return clstub().set_item_visual_properties(
            item_handle=item_handle, prop_dict=prop_dict
        )

    def set_icon_drawing_commands(self, item_handle, drawing_commands):
        """
        Set provided drawing commands (``drawing_commands``) to item denoted
        by ``item_handle``.
        Drawing commands will be used to draw icon over target item.

        Args:
            item_handle(ItemHandle): ItemHandle object.

            drawing_commands(str): String with drawing commands.

        Returns:
            None

        Raises:
            SchApiItemNotFoundException when item can't be found.
            SchApiException when item handle is invalid or when
            target item doesn't support setting of drawing commands.

        **Example:**

        .. literalinclude:: sch_api_examples/get_set_icon_drawing_commands.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_set_icon_drawing_commands.example
        """
        return clstub().set_icon_drawing_commands(
            item_handle=item_handle, drawing_commands=drawing_commands
        )

    def get_icon_drawing_commands(self, item_handle):
        """
        Returns icon drawing commands from provided items.

        Args:
            item_handle:

        Returns:
            Drawing commands.

        Raises:
            SchApiItemNotFoundException when item can't be found.
            SchApiException when item handle is invalid or when
            target item doesn't support setting of drawing commands in
            first place.

        **Example:**

        .. literalinclude:: sch_api_examples/get_set_icon_drawing_commands.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_set_icon_drawing_commands.example
        """
        return clstub().get_icon_drawing_commands(item_handle=item_handle)

    # * * * * * * * * * * * * * * * * * * *
    # Icons
    # * * * * * * * * * * * * * * * * * * * * * * *  * *

    def set_component_icon_image(self, item_handle, image_filename, rotate=ICON_ROTATE):
        """
        Specify image to be used in icon.

        Args:
            item_handle(ItemHandle): Item handle.

            image_filename (str): Image filename.

            rotate (str): Constant describing icon rotation
                behavior (See `Schematic API constants`_).

        Returns:
            None

        **Example:**

        .. literalinclude:: sch_api_examples/icon.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/icon.example
        """
        return clstub().set_component_icon_image(
            item_handle=item_handle, image_filename=image_filename, rotate=rotate
        )

    def disp_component_icon_text(
        self,
        item_handle,
        text,
        rotate=ICON_TEXT_LIKE,
        size=10,
        relpos_x=0.5,
        relpos_y=0.5,
        trim_factor=1.0,
    ):
        """
        Specify text to be displayed inside icon.

        Args:
            item_handle(ItemHandle): Item handle object.

            text (str): Text to display.

            rotate (str): Constant specifying icon rotation behavior,
                (See `Schematic API constants`_).

            size (int): Size of text.

            relpos_x (float): Center of text rectangle (on X axis).

            relpos_y (float): Center of text rectangle (on Y axis).

            trim_factor (float): Number in range (0.0 .. 1.0) which specifies
                at which relative width of text rectangle width to shorten text.

        Returns:
            None

        **Example:**

        .. literalinclude:: sch_api_examples/icon.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/icon.example
        """
        return clstub().disp_component_icon_text(
            item_handle=item_handle,
            text=text,
            rotate=rotate,
            size=size,
            relpos_x=relpos_x,
            relpos_y=relpos_y,
            trim_factor=trim_factor,
        )

    def set_color(self, item_handle, color):
        """
        Set color to be used in all subsequent icon API operations.
        Color name is specified as a string in format understood by Qt
        framework.

        Args:
            item_handle(ItemHandle): Item handle.

            color (str): Color name.

        Returns:
            None

        **Example:**

        .. literalinclude:: sch_api_examples/icon.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/icon.example
        """
        return clstub().set_color(item_handle=item_handle, color=color)

    def refresh_icon(self, item_handle):
        """
        Refresh icon.

        Args:
            item_handle(ItemHandle): Item handle.

        Returns:
            None

        **Example:**

        .. literalinclude:: sch_api_examples/icon.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/icon.example
        """
        return clstub().refresh_icon(item_handle=item_handle)

    # * * *  * * * * * * * * * * * * * * * * * * *
    #                Terminals                   *
    # * * *  * * * * * * * * * * * * * * * * * * *
    def get_terminal_dimension(self, terminal_handle):
        """
        Returns the dimension of the component terminal.

        Args:
            terminal_handle (ItemHandle): Terminal handle.

        Returns:
            Terminal dimension as list.

        **Example:**

        .. literalinclude:: sch_api_examples/get_set_term_dimension.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_set_term_dimension.example
        """
        return clstub().get_terminal_dimension(terminal_handle=terminal_handle)

    def set_terminal_dimension(self, terminal_handle, dimension):
        """
        Set component terminal dimension.

        Args:
            terminal_handle (ItemHandle): Terminal handle.

            dimension (tuple): Terminal new dimension.

        **Example:**

        .. literalinclude:: sch_api_examples/get_set_term_dimension.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_set_term_dimension.example
        """
        return clstub().set_terminal_dimension(
            terminal_handle=terminal_handle, dimension=dimension
        )

    def sync_dynamic_terminals(
        self,
        comp_handle,
        term_name,
        term_num,
        labels=None,
        sp_types=None,
        feedthroughs=None,
        names=None,
    ):
        """
        Synchronize number of dynamic terminals on component with given name.

        Args:
            comp_handle (ItemHandle): Component handle.

            term_name (str): Terminal name.

            term_num (int): Number of terminal to synchronize to.

            labels (list): List of labels for new terminals.

            sp_types (list): List of SP types for new terminals.

            feedthroughs (list): List of feedthrough values for new terminals.

            names(iterable): List of names for new terminals.

        **Example:**

        .. literalinclude:: sch_api_examples/sync_dyn_terms.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/sync_dyn_terms.example
        """
        return clstub().sync_dynamic_terminals(
            comp_handle=comp_handle,
            term_name=term_name,
            term_num=term_num,
            labels=labels,
            sp_types=sp_types,
            feedthroughs=feedthroughs,
        )

    def get_terminal_sp_type(self, terminal_handle):
        """
        Return component terminal SP type.

        SP type can be one of the following: SP_TYPE_INHERIT, SP_TYPE_INT,
        SP_TYPE_UINT, SP_TYPE_REAL or the expression that can be evaluated into
        those values.

        Args:
            terminal_handle (ItemHandle): Terminal handle.

        Returns:
            Terminal SP type as string.

        **Example:**

        .. literalinclude:: sch_api_examples/get_term_sp_type.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_term_sp_type.example
        """
        return clstub().get_terminal_sp_type(terminal_handle=terminal_handle)

    def set_terminal_sp_type(self, terminal_handle, sp_type):
        """
        Set component terminal SP (Signal processing) type.

        SP type can be one of the constants for SP type
        (See `Schematic API constants`_) or the expression that can be evaluated
        into those values.

        Args:
            terminal_handle (ItemHandle): Terminal handle.

            sp_type (str): SP (Signal processing) type.

        **Example:**

        .. literalinclude:: sch_api_examples/set_term_sp_type.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/set_term_sp_type.example
        """
        return clstub().set_terminal_sp_type(
            terminal_handle=terminal_handle, sp_type=sp_type
        )

    def get_terminal_sp_type_value(self, terminal_handle):
        """
        Return component terminal calculated SP type (calculated based on value
        of SP type for that terminal).

        If calculated, returned value can be either SP_TYPE_INT, SP_TYPE_UINT,
        SP_TYPE_REAL.
        Calculation of the SP type value is performed during the compilation
        of the schematic.

        Args:
            terminal_handle (ItemHandle): Terminal handle.

        Returns:
            Terminal SP type as string.

        **Example:**

        .. literalinclude:: sch_api_examples/get_term_sp_type.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_term_sp_type.example
        """
        return clstub().get_terminal_sp_type_value(terminal_handle=terminal_handle)

    def set_terminal_sp_type_value(self, terminal_handle, sp_type_value):
        """
        Set component terminal SP type directly.

        Args:
            terminal_handle (ItemHandle): Terminal handle.

            sp_type_value (str): New SP type value, must be constant for
                SP Type (See `Schematic API constants`_).

        **Example:**

        .. literalinclude:: sch_api_examples/set_term_sp_type.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/set_term_sp_type.example
        """
        return clstub().set_terminal_sp_type_value(
            terminal_handle=terminal_handle, sp_type_value=sp_type_value
        )

    def is_terminal_feedthrough(self, terminal_handle):
        """
        Determine if terminal is feedthrough.

        Args:
            terminal_handle (ItemHandle): Terminal handle.

        Returns:
            ``True`` if terminal is feedthrough, ``False`` otherwise.

        **Example:**

        .. literalinclude:: sch_api_examples/term_feedthrough.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/term_feedthrough.example
        """
        return clstub().is_terminal_feedthrough(terminal_handle=terminal_handle)

    def set_terminal_feedthrough(self, terminal_handle, feedthrough):
        """
        Set terminal feedthrough value.

        Args:
            terminal_handle (ItemHandle): Terminal handle.

            feedthrough (bool): Terminal feedthrough value.

        Returns:
            None

        **Example:**

        .. literalinclude:: sch_api_examples/term_feedthrough.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/term_feedthrough.example
        """
        return clstub().set_terminal_feedthrough(
            terminal_handle=terminal_handle, feedthrough=feedthrough
        )

    def get_connectable_direction(self, connectable_handle):
        """
        Returns direction of connectable object.

        ConnectableMixin can be either terminal, or port. Direction is either
        DIRECTION_IN or DIRECTION_OUT.

        Args:
            connectable_handle (ItemHandle): Terminal handle.

        Returns:
            str

        Raises:
            SchApiException if `connectable_handle` is not of ConnectableMixin type

        **Example:**

        .. literalinclude:: sch_api_examples/get_connectable_direction.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_connectable_direction.example
        """
        return clstub().get_connectable_direction(connectable_handle=connectable_handle)

    def get_connectable_kind(self, connectable_handle):
        """
        Returns kind of connectable object.

        ConnectableMixin can be either terminal, junction or port. Kind is either
        KIND_SP or KIND_PE.

        Args:
            connectable_handle (ItemHandle): Terminal handle.

        Returns:
            str

        Raises:
            SchApiException if `connectable_handle` is not of ConnectableMixin type

        **Example:**

        .. literalinclude:: sch_api_examples/get_connectable_kind.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_connectable_kind.example
        """
        return clstub().get_connectable_kind(connectable_handle=connectable_handle)

    # * * *  * * * * * * * * * * * * * * * * * * *
    #                Namespace                   *
    # * * *  * * * * * * * * * * * * * * * * * * *
    def set_ns_var(self, var_name, value):
        """
        Set namespace variable named ``var_name`` to ``value``.
        If variable doesn't exists in namespace, it will be created
        and value set.

        Args:
            var_name (str): Namespace variable name.

            value (object): Value to be set.

        Returns:
            None

        **Example:**

        .. literalinclude:: sch_api_examples/get_set_ns_var.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_set_ns_var.example
        """
        return clstub().set_ns_var(var_name=var_name, value=value)

    def get_ns_var(self, var_name):
        """
        Return value of namespace variable named ``var_name``.

        Args:
            var_name (str): Namespace variable name.

        Returns:
            Python object.

        Raises:
            SchApiException if variable with given name doesn't exist in
            the namespace.

        **Example:**

        .. literalinclude:: sch_api_examples/get_set_ns_var.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_set_ns_var.example
        """
        return clstub().get_ns_var(var_name=var_name)

    def get_ns_vars(self):
        """
        Get names of all variables in namespace.

        Args:
            None

        Returns:
            List of variable names in namespace.

        **Example:**

        .. literalinclude:: sch_api_examples/get_ns_vars.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_ns_vars.example
        """
        return clstub().get_ns_vars()

    def is_require_satisfied(self, require_string):
        """
        Checks if provided ``require_string`` is satisfied against current
        configuration (model configuration).

        Args:
            require_string(str): Requirement string.

        Returns:
            True if requirement string is satisfied against
            current model configuration, False otherwise.

        **Example:**

        .. literalinclude:: sch_api_examples/is_require_satisfied.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/is_require_satisfied.example
        """
        return clstub().is_require_satisfied(require_string=require_string)

    def get_hw_property(self, prop_name):
        """
        Get value of hardware property specified by ``prop_name`` against
        the model current configuration.

        Args:
            prop_name(str): Fully qualified name of hardware property.

        Returns:
            Value for specified hardware property.

        Raises:
            SchApiItemNotFoundException if specified hardware property doesn't
            exists.

        **Example:**

        .. literalinclude:: sch_api_examples/get_hw_property.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_hw_property.example
        """
        return clstub().get_hw_property(prop_name=prop_name)

    def unlink_component(self, item_handle):
        """
        Unlinks component, breaking link from component to its library
        implementation.
        This allows model with this component to be shared freely without
        providing thatt particular library, as component implementaion is
        transfered from library to model component.

        Args:
            item_handle(ItemHandle): Component item handle object.

        Returns:
            None

        Raises:
            SchApiException - when some of following occurs:
            Component is an atomic component.
            Component is already unlinked.
            One or more component parent are linked.
            Component is locked or some parent/s are locked.

            SchApiItemNotFoundException when component can't be found.

        **Example:**

        .. literalinclude:: sch_api_examples/unlink_component.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/unlink_component.example
        """
        return clstub().unlink_component(item_handle=item_handle)

    def get_available_library_components(
        self, library_name="", context=CONTEXT_REAL_TIME
    ):
        """
        Returns iterable over available component names from library specified
        by ``library_name``.

        If library name is ommited, then all available libraries are
        searched.

        Args:
            library_name(str): Name of the library from which to get available
            component names.

        Returns:
            Iterable over available library component names in
            form "library_name/component name".

        Raises:
            SchApiException if library is explicitly specified and it
            doesn't exists.

        **Example:**

        .. literalinclude:: sch_api_examples/get_available_library_components.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_available_library_components.example
        """
        return clstub().get_available_library_components(
            library_name=library_name, context=context
        )

    def get_compiled_model_file(self, sch_path):
        """
        Return path to .cpd file based on schematic .tse file path.
        This function does not compile the model, only returns the
        path to the file generated by the `compile()` function.

        Args:
            sch_path (string): Path to .tse schematic file

        Returns:
            string: Path to to-be-generated .cpd file.

        **Example:**

        .. literalinclude:: sch_api_examples/get_compiled_model_file.example
           :language: python
           :lines: 2-
        """
        # For this function, we are not sending request to the server to support
        # relative paths.
        sch_path = os.path.abspath(sch_path)
        directory, filename = os.path.split(sch_path)
        model, ext = os.path.splitext(filename)
        if ext != ".tse":
            raise ValueError(f"Expected path to a .tse file. Got {sch_path} instead.")

        cpd_folder = f"{model} Target files"
        cpd_file = f"{model}.cpd"

        return os.path.join(directory, cpd_folder, cpd_file)

    def get_library_resource_dir_path(self, item_handle):
        """
        Get directory path where resource files for library is expected/searched.
        Parameter item_handle specifies some element which can be traced
        back to the originating library.

        Args:
            item_handle(ItemHandle): Item handle object.

        Returns:
            Directory path as string where resource files are expected/searched.

        Raises:
            SchApiException if library is explicitly specified and it
            doesn't exists.

        **Example:**

        .. literalinclude:: sch_api_examples/get_library_resource_dir_path.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_library_resource_dir_path.example
        """
        return clstub().get_library_resource_dir_path(item_handle=item_handle)

    def export_c_from_subsystem(self, comp_handle, output_dir=None):
        """
        Exports C code from a given subsystem. C code exporter is still in
        `beta` phase.

        .. note:: This function is not recommended for use in handlers.

        Args:
            comp_handle (ItemHandle): Component item handle object.
            output_dir (str): Path to a directory where code will be exported

        Returns:
            None

        Raises:
            SchApiException - when some of following occurs:
            Provided ItemHandle is not component.
            Component is an atomic component.

            SchApiItemNotFoundException when component can't be found.

        **Example:**

        .. literalinclude:: sch_api_examples/export_c_from_subsystem.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/export_c_from_subsystem.example
        """
        return clstub().export_c_from_subsystem(
            comp_handle=comp_handle, output_dir=output_dir
        )

    def export_c_from_model(self, output_dir=None):
        """
        Exports C code from the model's root. Performs as a shortcut for
        creating an empty subsystem from the root's content, and exporting the
        C code from that subsystem. C code exporter is still in `beta` phase.

        .. note:: This function is not recommended for use in handlers.

        Args:
            output_dir (str): Path to a directory where code will be exported

        Returns:
            None

        **Example:**

        .. literalinclude:: sch_api_examples/export_c_from_model.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/export_c_from_model.example
        """
        return clstub().export_c_from_model(output_dir=output_dir)

    def export_c_from_selection(self, comp_handles, output_dir):
        """
        .. deprecated:: 1.10.1
            This function is no longer supported, and will raise an error.
            Use ``export_c_from_subsystem`` instead.

        Exports C code from a selection of components. C code exporter is still
        in `beta` phase.

        .. note:: This function cannot be used in handlers.

        Args:
            comp_handles (list): list of component item handle objects.
            output_dir (str): Path to a directory where code will be exported

        Returns:
            None

        Raises:
            Exception

        """
        raise Exception(
            "Function 'export_c_from_selection' is no longer "
            "supported and will be removed in future versions of "
            "API. Please, use 'export_c_from_subsystem' instead."
        )

    def export_model_to_json(self, output_dir=None, recursion_strategy=None):
        """
        Exports model to json representation.

        Args:
            output_dir (str): path to output dir folder,
             if no path is specified the file will be shipped to
             Target Files folder
            recursion_strategy(str): constant specifying the
             hierarchy model traversal.
             Constants RECURSE_* defined in
             'Schematic API constants' are expected.

        **Example:**

        .. literalinclude:: sch_api_examples/export_model_to_json.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/export_model_to_json.example
        """
        if output_dir:
            output_dir = determine_path(output_dir)
        return clstub().export_model_to_json(
            output_dir=output_dir, recursion_strategy=recursion_strategy
        )

    def get_model_information(self):
        """
        Returns model information in a form of key value.

        Args:
            None

        Returns:
            dict, where possible keys are "model", which value correspondents
             to model name and another key is "required_toolboxes" which
             value is a list of required toolboxes for current model.

        **Example:**

        .. literalinclude:: sch_api_examples/get_model_information.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_model_information.example
        """
        return clstub().get_model_information()

    def create_library_model(self, lib_name, file_name):
        """
        Creates new library (.tlib) model.

        Args:
            lib_name (str): Actual library name
            file_name (str): The name of the file

        Returns:
            None

        **Example:**

        .. literalinclude:: sch_api_examples/create_library_model.example
            :language: python
            :lines: 2-

        Output

        .. program-output:: python sch_api_examples/create_library_model.example
        """
        return clstub().create_library_model(lib_name=lib_name, file_name=file_name)

    def enable_items(self, item_handles):
        """
        Enable items using the provided ``item_handles``.

        Args:
            item_handles (iterable): Iterable over scheme items.

        Returns:
            List of items affected by the operation.


        **Example:**

        .. literalinclude:: sch_api_examples/enable_items.example
            :language: python
            :lines: 2 -

        Output

        .. program-output:: python sch_api_examples/enable_items.example
        """
        return clstub().enable_items(item_handles=item_handles)

    def disable_items(self, item_handles):
        """
        Disables items using the provided ``item_handles``.

        Args:
            item_handles (iterable): Iterable over scheme items to be disabled.

        Returns:
            List of items affected by the operation.


        **Example:**

        .. literalinclude:: sch_api_examples/disable_items.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/disable_items.example
        """
        return clstub().disable_items(item_handles=item_handles)

    def bypass_component(self, item_handle):
        """
        Disables a component and bypasses its terminals if their number is the same
        on opposite sides.

        Returns:
            None

        **Example:**

        .. literalinclude:: sch_api_examples/bypass_component.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/bypass_component.example
        """

        return clstub().bypass_component(item_handle=item_handle)

    def is_enabled(self, item_handle):
        """
        Returns whether or not the provided item is enabled.

        Args:
            item_handle (SchemeItemMixin): Scheme item.

        Returns:
            bool


        **Example:**

        .. literalinclude:: sch_api_examples/is_enabled.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/is_enabled.example
        """
        return clstub().is_enabled(item_handle=item_handle)

    def is_bypassed(self, item_handle):
        """
        Returns whether the provided component is bypassed.

        Args:
            item_handle (SchemeItemMixin): Scheme item.

        Returns:
            bool


        **Example:**

        .. literalinclude:: sch_api_examples/bypass_component.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/bypass_component.example
        """
        return clstub().is_bypassed(item_handle=item_handle)

    def is_tunable(self, item_handle):
        """
        Returns whether or not the provided item is tunable.

        Args:
            item_handle (ItemHandle): Either component handle or property
                handle

        Returns:
            bool


        **Example:**

        .. literalinclude:: sch_api_examples/is_enabled.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/set_tunable.example
        """
        return clstub().is_tunable(item_handle=item_handle)

    def set_tunable(self, item_handle, value):
        """
        Sets item as tunable. Item handle can be either component or property.
        If component handle is provided, all properties that can be tunable
        will become tunable.

        Args:
            item_handle (ItemHandle): Either component handle or property
                handle
            value (bool): True or False
        Returns:
            bool


        **Example:**

        .. literalinclude:: sch_api_examples/set_tunable.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/set_tunable.example
        """
        return clstub().set_tunable(item_handle=item_handle, value=value)

    def export_library(
        self,
        output_file,
        resource_paths=(),
        dependency_paths=(),
        lock_top_level_components=True,
        exclude_from_locking=(),
        encrypt_library=True,
        encrypt_resource_files=True,
        exclude_from_encryption=(),
    ):
        """
        Exports a library to specified output file path. The core model must
        be a scm.core.Library object.

        Args:
            output_file (str): Path where to export the library (.atlib auto-appended)
            resource_paths (tuple): tuple of required resource paths for exporting this library
            dependency_paths (tuple): tuple of required dependency paths for exporting this library
            lock_top_level_components (bool): True or False
            exclude_from_locking (tuple): tuple of component fqns that will be excluded in top level component locking process
            encrypt_library (bool): True or False
            encrypt_resource_files (bool): True or False
            exclude_from_encryption (tuple): tuple of resource paths that will be excluded in encryption process
        Returns:
            bool


        **Example:**

        .. literalinclude:: sch_api_examples/export_library.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/export_library.example
        """
        return clstub().export_library(
            output_file=output_file,
            resource_paths=resource_paths,
            dependency_paths=dependency_paths,
            lock_top_level_components=lock_top_level_components,
            exclude_from_locking=exclude_from_locking,
            encrypt_library=encrypt_library,
            encrypt_resource_files=encrypt_resource_files,
            exclude_from_encryption=exclude_from_encryption,
        )

    def get_connected_items(self, item_handle):
        """
        Returns a collection of item handles connected to item
        specified by ``item_handle``. Item handle can be reference
        to a 'connectable object' (which is terminal, junction, port and tag)
        or to a component which holds terminals on it's own.

        Args:
            item_handle(ItemHandle): Reference to a schematic item.

        Returns:
            Collection of connected item handles.

        **Example:**

        .. literalinclude:: sch_api_examples/get_connected_items.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_connected_items.example
        """
        return clstub().get_connected_items(self, item_handle=item_handle)

    def set_model_dependencies(self, dependencies_list):
        """
        Sets list of files/directories as dependencies of a model.
        Files and directories are passed as a list of stings.
        It represents the data that affects model compilation.
        If model itself and depending files aren't changed between
        two compilations, second one will be skipped.

        Args:
            dependencies_list(list): List of strings representing file or directory.

        Returns:
            None

        **Example:**

        .. literalinclude:: sch_api_examples/set_model_dependencies.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/set_model_dependencies.example
        """
        return clstub().set_model_dependencies(
            self, dependencies_list=dependencies_list
        )

    def get_model_dependencies(self):
        """
        Returns list of files/directories that are dependencies of a model.
        Files and directories are returned as a list of stings.
        It represents the data that affects model compilation.
        If model itself and depending files aren't changed between
        two compilations, second one will be skipped.

        Args:
            None

        Returns:
            Collection of strings representing file or directory model depends on.

        **Example:**

        .. literalinclude:: sch_api_examples/get_model_dependencies.example
           :language: python
           :lines: 2-

        Output

        .. program-output:: python sch_api_examples/get_model_dependencies.example
        """
        return clstub().get_model_dependencies(self)

    def precompile_fmu(
        self, fmu_file_path, precompiled_file_path=None, additional_definitions=None
    ):
        """
        Creates a new precompiled FMU zip file.
        Source files are compiled and linked into a static library.
        All source and header files from the original FMU zip are deleted.

        Args:
            fmu_file_path: path where the FMU is located
            precompiled_file_path: path where the new FMU will be saved.
                    If the argument is not specified,
                    the file will be saved at the same path as the original FMU file with the suffix "_precompiled"
            additional_definitions: additional definitions to be passed to the compiler

        Returns:
            None
        """
        return clstub().precompile_fmu(
            self,
            fmu_file_path=fmu_file_path,
            precompiled_file_path=precompiled_file_path,
            additional_definitions=additional_definitions,
        )

    def create_c_library(
        self,
        source_files,
        compiler_options=None,
        platform="HIL",
        library_type="static",
        output_lib_path=None,
    ):
        """
        Creates a static library file from provided source files.

        Args:
            source_files (list): list of source files
            compiler_options (dictionary): additional parameters for compiling process
            platform (str): what device will the library be used (HIL, Windows, Linux)
            library_type (str): type of library to be created (static or dynamic)
            output_lib_path (str): path where the static library will be saved.
                    If the argument is not specified,
                    the file will be saved at the same path as the source files.
        Returns:
            None

        """
        return clstub().create_c_library(
            self,
            source_files=source_files,
            compiler_options=compiler_options,
            platform=platform,
            library_type=library_type,
            output_lib_path=output_lib_path,
        )

    def _click_button(self, prop_handle):
        """Private function DO NOT USE."""
        return clstub()._click_button(self, prop_handle=prop_handle)


model: SchematicAPI = SchematicAPI()
