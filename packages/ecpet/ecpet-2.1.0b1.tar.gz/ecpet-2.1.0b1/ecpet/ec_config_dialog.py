#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
EC-PeT Configuration Dialog

A comprehensive configuration dialog for EC-PeT with themed tabs,
visual editing of flagging rules, and plausibility checks.

This extends the existing ecmain.py with a new configuration dialog.
"""

import logging
from copy import deepcopy
import os
import re
from collections import OrderedDict

import wx
import wx.grid
import wx.lib.scrolledpanel as scrolled

from . import ecconfig
from .ecdefaults import defaults
from .ecutils import APPARATUS_TYPES, metvar, flx, str_to_bool

logger = logging.getLogger(__name__)

# Configuration categories and their display names
CONFIG_CATEGORIES = OrderedDict([
    ('general', 'General Settings'),
    ('files', 'Files & Directories'),
    ('time', 'Time Selection'),
    ('site', 'Site Information'),
    ('devices', 'Device Calibration'),
    ('format', 'Data Format'),
    ('processing', 'Processing Settings'),
    ('qc_pre', 'Quality Control - Preprocessing'),
    ('qc_post', 'Quality Control - Postprocessing'),
    ('flags', 'Flagging Rules'),
])

# Device types mapping
DEVICE_TYPES = {k: v['desc'] for k, v in APPARATUS_TYPES.items()}

# Despiking methods
DESPIKING_METHODS = [
    ('', 'No despiking'),
    ('spk', 'Vickers & Mahrt (standard deviation)'),
    ('chr', 'Change rate based'),
    ('mad', 'Median Absolute Deviation (MAD)')
]

# QC test codes and descriptions
QC_TESTS = {
    'spk': 'Spikes (Vickers & Mahrt)',
    'res': 'Amplitude resolution',
    'drp': 'Dropouts',
    'lim': 'Absolute limits',
    'mom': 'Higher moments',
    'dis': 'Discontinuities',
    'nst': 'Nonstationarity',
    'lag': 'Lag correlation',
    'chr': 'Change rate spikes',
    'mad': 'MAD spikes',
    'fws': 'Stationarity (Foken & Wichura)',
    'cot': 'Covariance trends',
    'bet': 'Beta distribution',
    'vst': 'Variance stationarity',
    'ftu': 'Fraction of turbulence',
    'srv': 'Surviving values',
    'cmx': 'Complex analysis',
    'mnw': 'Mean vertical wind',
    'itc': 'Integrated turb. characteristics',
    'exs': 'Excluded sectors',
    'fkm': 'Footprint model',
    'exe': 'Excessive error'
}

# Variable codes for flagging rules
VARIABLE_CODES = metvar
FLUX_CODES = flx


class ValidatedTextCtrl(wx.TextCtrl):
    def __init__(self, parent, config_key='', expected_type='str',
                 *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.config_key = config_key
        self.expected_type = expected_type

class ConfigurationDialog(wx.Dialog):
    """
    Main configuration dialog with tabbed interface
    """

    def __init__(self, parent, config=None, title="EC-PeT Configuration"):
        super().__init__(parent, title=title, size=(1024, 700),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        self.config = config if config is not None else {}
        self.modified = False

        self.init_ui()
        self.load_config()
        self.setup_validation()

    def init_ui(self):
        """Initialize the user interface"""
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Create notebook for tabs
        self.notebook = wx.Notebook(self)

        # Create tab pages
        self.pages = {}
        for key, title in CONFIG_CATEGORIES.items():
            page = self.create_page(key, title)
            self.pages[key] = page
            self.notebook.AddPage(page, title)

        self.banner = wx.StaticText(
            self, label="Note: this dialog still in experimental code. "
                        "Use with care.",
            style=wx.ALIGN_CENTRE)
        self.banner.SetForegroundColour(wx.Colour(255, 0, 0))
        self.banner.SetFont(self.banner.GetFont().Bold())

        main_sizer.Add(self.banner, 0, wx.EXPAND | wx.ALL, 10)
        main_sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 5)

        # Button panel
        btn_panel = wx.Panel(self)
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Create buttons with minimum sizes to prevent GTK warnings
        self.validate_btn = wx.Button(btn_panel, wx.ID_ANY, "Validate",
                                      size=(80, 30))
        self.reset_btn = wx.Button(btn_panel, wx.ID_ANY, "Reset",
                                   size=(80, 30))
        self.ok_btn = wx.Button(btn_panel, wx.ID_OK, "OK", size=(80, 30))
        self.cancel_btn = wx.Button(btn_panel, wx.ID_CANCEL, "Cancel",
                                    size=(80, 30))

        btn_sizer.Add(self.validate_btn, 0, wx.ALL, 5)
        btn_sizer.AddStretchSpacer()
        btn_sizer.Add(self.reset_btn, 0, wx.ALL, 5)
        btn_sizer.Add(self.ok_btn, 0, wx.ALL, 5)
        btn_sizer.Add(self.cancel_btn, 0, wx.ALL, 5)

        btn_panel.SetSizer(btn_sizer)
        main_sizer.Add(btn_panel, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(main_sizer)

        # Bind events
        self.Bind(wx.EVT_BUTTON, self.on_validate, self.validate_btn)
        self.Bind(wx.EVT_BUTTON, self.on_reset, self.reset_btn)
        self.Bind(wx.EVT_BUTTON, self.on_ok, self.ok_btn)

    def create_page(self, key, title):
        """Create a configuration page"""
        if key == 'general':
            return GeneralPage(self.notebook, self)
        elif key == 'files':
            return FilesPage(self.notebook, self)
        elif key == 'time':
            return TimePage(self.notebook, self)
        elif key == 'site':
            return SitePage(self.notebook, self)
        elif key == 'devices':
            return DevicesPage(self.notebook, self)
        elif key == 'format':
            return FormatPage(self.notebook, self)
        elif key == 'processing':
            return ProcessingPage(self.notebook, self)
        elif key == 'qc_pre':
            return QCPrePage(self.notebook, self)
        elif key == 'qc_post':
            return QCPostPage(self.notebook, self)
        elif key == 'flags':
            return FlagsPage(self.notebook, self)
        else:
            return wx.Panel(self.notebook, self)

    def load_config(self):
        """Load configuration into dialog"""
        for page in self.pages.values():
            if hasattr(page, 'load_config'):
                page.load_config(self.config)

    def save_config(self):
        """Save configuration from dialog"""
        new_config = ecconfig.Config()
        for page in self.pages.values():
            if hasattr(page, 'save_config'):
                page.save_config(new_config)
        return new_config

    def setup_validation(self):
        """Setup validation rules"""
        self.validation_rules = []

        # Add validation rules
        self.validation_rules.append(self.validate_despiking_consistency)
        self.validation_rules.append(self.validate_device_positions)
        self.validation_rules.append(self.validate_time_range)
        self.validation_rules.append(self.validate_paths)
        self.validation_rules.append(self.validate_position)
        self.validation_rules.append(self.validate_qc_conflicts)

    def validate_despiking_consistency(self, config):
        """Validate that selected despiking method is not disabled"""
        errors = []

        despiking = config.pull('Despiking', '')
        disabled_tests = config.pull('QCdisable', '')

        if despiking and despiking in disabled_tests:
            errors.append(
                f"Despiking method '{despiking}' is disabled in QC tests")

        return errors

    def validate_device_positions(self, config):
        """Validate device position coordinates"""
        errors = []

        device_prefixes = ['SonCal', 'CoupCal', 'HygCal', 'Co2Cal']
        for prefix in device_prefixes:
            device_type = int(float(
                config.pull(f'{prefix}.QQType', 0)))
            if device_type > 0:  # Device is present
                for coord in ['QQX', 'QQY', 'QQZ']:
                    key = f'{prefix}.{coord}'
                    if key in config.tokens:
                        try:
                            value = float(config.pull(key, kind='float'))
                            if coord == 'QQZ' and value <= 0:
                                errors.append(
                                    f"Height ({key}) must be positive")
                        except (ValueError, TypeError):
                            errors.append(
                                f"Invalid coordinate value for {key}")

        return errors

    def validate_time_range(self, config):
        """Validate time range settings"""
        errors = []

        begin = config.pull('DateBegin', '')
        end = config.pull('DateEnd', '')

        if begin and end:
            # Simple validation - more sophisticated parsing would be better
            if begin >= end:
                errors.append("DateBegin must be earlier than DateEnd")

        avg_interval = config.pull('AvgInterval', 0)
        try:
            interval = int(avg_interval)
            if interval <= 0:
                errors.append("AvgInterval must be positive")
        except (ValueError, TypeError):
            errors.append("AvgInterval must be a number")

        return errors

    def validate_paths(self, config):
        """Validate file paths"""
        errors = []

        path_keys = ['RawDir', 'DatDir', 'OutDir', 'Parmdir']
        for key in path_keys:
            path = config.pull(key, '')
            if path and not os.path.exists(path):
                errors.append(f"Path does not exist: {key} = {path}")

        return errors

    def validate_position(self, config):
        """Validate file paths"""
        errors = []

        position_keys = ['InstLatLon']
        for key in position_keys:
            fields = config.pull(key, '')
            if len(fields) != 2:
                errors.append(f'Position {key} must have 2 fields')
            else:
                for x, y in zip(fields, ['latitude', 'longitude']):
                    e = validate_coordinate(x, y)
                    if e:
                        errors.append(f"Position error: {e}")
        return errors


    def validate_qc_conflicts(self, config):
        """Validate QC conflicts by calling existing QCDisablePanel validation"""
        errors = []

        # Get the general page which contains the QC disable panel
        if 'general' in self.pages:
            general_page = self.pages['general']
            if hasattr(general_page, 'qc_disable_panel'):
                # Call the existing validation logic and get errors
                qc_errors = general_page.qc_disable_panel.validate_conflicts()
                errors.extend(qc_errors)

        return errors

    def on_validate(self, event):
        """Validate current configuration"""
        config = self.save_config()
        errors = []

        for rule in self.validation_rules:
            errors.extend(rule(config))

        if errors:
            error_msg = "Configuration validation errors:\n\n" + "\n".join(
                f"• {error}" for error in errors)
            wx.MessageBox(error_msg, "Validation Errors",
                          wx.OK | wx.ICON_WARNING)
        else:
            wx.MessageBox("Configuration is valid!", "Validation Success",
                          wx.OK | wx.ICON_INFORMATION)

    def on_reset(self, event):
        """Reset configuration to defaults"""
        if wx.MessageBox("Reset all settings to defaults?",
                         "Confirm Reset",
                         wx.YES_NO | wx.ICON_QUESTION) == wx.YES:
            self.config = ecconfig.Config()
            self.load_config()

    def on_ok(self, event):
        """OK button handler with validation"""
        config = self.save_config()
        errors = []

        for rule in self.validation_rules:
            errors.extend(rule(config))

        if errors:
            if wx.MessageBox(
                    "Configuration has validation errors.\n" +
                    "\n".join(errors) +
                    "\nContinue anyway?",
                    "Validation Errors",
                    wx.YES_NO | wx.ICON_WARNING) != wx.YES:
                return

        self.config = config
        self.modified = True
        self.EndModal(wx.ID_OK)


class ConfigPageBase(scrolled.ScrolledPanel):
    """Base class for configuration pages"""
    top_dialog = None

    def __init__(self, parent, top_dialog):
        super().__init__(parent)
        self.SetupScrolling()
        self.controls = {}
        self.top_dialog = top_dialog
        
    def add_section(self, sizer, title):
        """Add a section header"""
        section_box = wx.StaticBox(self, label=title)
        section_sizer = wx.StaticBoxSizer(section_box, wx.VERTICAL)
        sizer.Add(section_sizer, 0, wx.EXPAND | wx.ALL, 5)
        return section_sizer

    def add_text_field(self, parent_sizer, label, key, default='',
                       tooltip='', expected_type=None):
        """Add a text input field with validation coloring"""
        field_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Get label and tooltip from defaults if not provided
        if not label and key in defaults:
            label = defaults[key].get('short', key)
        if not tooltip and key in defaults:
            comment = defaults[key].get('comment', '')
            tooltip = f"{key} - {comment}" if comment else key

        # Get default value from defaults if not provided
        if not default and key in defaults:
            default = defaults[key].get('value', '')

        label_ctrl = wx.StaticText(self, label=label, size=(150, -1))
        text_ctrl = ValidatedTextCtrl(self, value=str(default), size=(200, -1))

        if tooltip:
            text_ctrl.SetToolTip(tooltip)

        # Store expected type for validation - auto-detect from defaults if not specified
        if expected_type is None and key in defaults:
            expected_type = defaults[key].get('type', 'str')
        elif expected_type is None:
            expected_type = 'str'

        text_ctrl.expected_type = expected_type
        text_ctrl.config_key = key

        # Bind validation events
        text_ctrl.Bind(wx.EVT_TEXT, self.on_text_change)
        text_ctrl.Bind(wx.EVT_KILL_FOCUS, self.on_text_change)

        field_sizer.Add(label_ctrl, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        field_sizer.Add(text_ctrl, 1, wx.EXPAND | wx.ALL, 5)

        parent_sizer.Add(field_sizer, 0, wx.EXPAND)
        self.controls[key] = text_ctrl

        # Perform initial validation
        self.validate_text_field(text_ctrl)

        return text_ctrl

    def on_text_change(self, event):
        """Handle text change events for validation"""
        control = event.GetEventObject()
        self.validate_text_field(control)
        event.Skip()

    def validate_text_field(self, control):
        """Validate text field and set background color accordingly"""
        if not hasattr(control, 'config_key'):
            return

        value = control.GetValue().strip()
        config_key = control.config_key
        is_valid = True

        # Get expected type from defaults or control attribute
        if hasattr(control, 'expected_type'):
            expected_type = control.expected_type
        elif config_key in defaults:
            expected_type = defaults[config_key].get('type', 'str')
        else:
            expected_type = 'str'

        # Allow empty values for most types
        if value == '':
            # Check if this parameter has a default or is required
            if config_key in defaults:
                default_value = str(defaults[config_key].get('value', ''))
                # If default is empty, empty input is valid
                is_valid = (default_value == '')
            else:
                is_valid = True
        else:
            # Validate based on expected type
            if expected_type == 'int':
                try:
                    # Allow float representations that are integers
                    float_val = float(value)
                    int_val = int(float_val)
                    is_valid = (float_val == int_val)
                except (ValueError, OverflowError):
                    is_valid = False
            elif expected_type == 'float':
                try:
                    float(value)
                    is_valid = True
                except (ValueError, OverflowError):
                    is_valid = False
            elif expected_type == 'bool':
                try:
                    str_to_bool(value)
                    is_valid = True
                except (ValueError, TypeError):
                    is_valid = False
            elif expected_type == 'str':
                # Strings are always valid
                is_valid = True
            elif expected_type == 'coordinate':
                fields = value.strip().split()
                if len(fields) != 2:
                    is_valid = False
                elif all([validate_coordinate(x,y) is None
                  for x,y in zip(fields, ['latitude', 'longitude'])]):
                    is_valid = True
                else:
                    is_valid = False
            else:
                # Unknown type, assume valid
                is_valid = True

        # Set background color based on validation
        if is_valid or not control.IsEnabled():
            control.SetBackgroundColour(
                wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
        else:
            control.SetBackgroundColour(
                wx.Colour(255, 200, 200))  # Light red

        control.Refresh()

    def add_choice_field(self, parent_sizer, label, key, choices,
                         default=0, tooltip=''):
        """Add a choice/dropdown field"""
        field_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Get label and tooltip from defaults if not provided
        if not label and key in defaults:
            label = defaults[key].get('short', key)
        if not tooltip and key in defaults:
            comment = defaults[key].get('comment', '')
            tooltip = f"{key} - {comment}" if comment else key

        label_ctrl = wx.StaticText(self, label=label, size=(150, -1))
        choice_ctrl = wx.Choice(self, choices=[str(choice) for choice in choices],
                                size=(200, -1))
        if 0 <= default < len(choices):
            choice_ctrl.SetSelection(default)

        if tooltip:
            choice_ctrl.SetToolTip(tooltip)

        field_sizer.Add(label_ctrl, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        field_sizer.Add(choice_ctrl, 1, wx.EXPAND | wx.ALL, 5)

        parent_sizer.Add(field_sizer, 0, wx.EXPAND)
        self.controls[key] = choice_ctrl
        return choice_ctrl

    def add_bool_field(self, parent_sizer, label, key, default=False,
                       tooltip=''):
        """Add a boolean checkbox field"""
        # Get label and tooltip from defaults if not provided
        if not label and key in defaults:
            label = defaults[key].get('short', key)
        if not tooltip and key in defaults:
            comment = defaults[key].get('comment', '')
            tooltip = f"{key} - {comment}" if comment else key

        check_ctrl = wx.CheckBox(self, label=label, size=(-1, 25))
        check_ctrl.SetValue(default)

        if tooltip:
            check_ctrl.SetToolTip(tooltip)

        parent_sizer.Add(check_ctrl, 0, wx.ALL, 5)
        self.controls[key] = check_ctrl
        return check_ctrl

class GeneralPage(ConfigPageBase):
    """General settings page"""

    def __init__(self, parent, top):
        super().__init__(parent, top)
        self.init_ui()

    def init_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Project settings
        project_sizer = self.add_section(main_sizer, "Project Settings")
        self.add_text_field(project_sizer, "", "ConfName")

        # Processing settings
        proc_sizer = self.add_section(main_sizer, "Processing Settings")
        self.add_text_field(proc_sizer, "", "nproc")

        despiking_choices = [desc for _, desc in DESPIKING_METHODS]
        despiking = self.add_choice_field(proc_sizer, "", "Despiking",
                              despiking_choices, 0)
        despiking.Bind(wx.EVT_CHOICE, self.on_choice_change)

        # QC disable list
        qc_sizer = self.add_section(main_sizer, "Quality Control")
        self.qc_disable_panel = QCDisablePanel(self)
        self.qc_disable_panel.top_dialog = self.top_dialog
        qc_sizer.Add(self.qc_disable_panel, 1, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(main_sizer)

    def on_choice_change(self, event):
        """Handle checkbox state changes and validate conflicts"""
        if hasattr(self, 'qc_disable_panel'):
            # Small delay to allow UI to update, then validate
            wx.CallAfter(self.qc_disable_panel.validate_conflicts)


    def load_config(self, config):
        """Load configuration values"""
        for key, control in self.controls.items():
            value = config.pull(key, '')
            if isinstance(control, wx.TextCtrl):
                control.SetValue(str(value))
            elif isinstance(control, wx.Choice):
                if key == 'Despiking':
                    # Find the despiking method
                    for i, (code, _) in enumerate(DESPIKING_METHODS):
                        if code == value:
                            control.SetSelection(i)
                            break

        # Load QC disable settings
        if hasattr(self, 'qc_disable_panel'):
            disabled_tests = config.pull('QCdisable', '').split()
            self.qc_disable_panel.set_disabled_tests(disabled_tests)

    def save_config(self, config):
        """Save configuration values"""
        for key, control in self.controls.items():
            if isinstance(control, wx.TextCtrl):
                config.push(key, control.GetValue())
            elif isinstance(control, wx.Choice):
                if key == 'Despiking':
                    sel = control.GetSelection()
                    if 0 <= sel < len(DESPIKING_METHODS):
                        config.push(key, DESPIKING_METHODS[sel][0])

        # Save QC disable settings
        if hasattr(self, 'qc_disable_panel'):
            disabled_tests = self.qc_disable_panel.get_disabled_tests()
            config.push('QCdisable', ' '.join(disabled_tests))


class QCDisablePanel(wx.Panel):
    """Panel for selecting disabled QC tests with conflict detection"""

    def __init__(self, parent):
        super().__init__(parent)
        self.top_dialog = None  # Will be set to reference the main dialog
        self.checkboxes = {}
        self.init_ui()

    def init_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        label = wx.StaticText(self,
                              label="Disabled Quality Control Tests:")
        main_sizer.Add(label, 0, wx.ALL, 5)

        # Create checkboxes in a grid
        grid_sizer = wx.FlexGridSizer(cols=3, hgap=10, vgap=5)

        for code, description in QC_TESTS.items():
            checkbox = wx.CheckBox(self, label=f"{code} - {description}",
                                   size=(-1, 25))  # Set minimum height
            checkbox.Bind(wx.EVT_CHECKBOX, self.on_checkbox_change)
            grid_sizer.Add(checkbox, 0, wx.EXPAND)
            self.checkboxes[code] = checkbox

        main_sizer.Add(grid_sizer, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(main_sizer)

    def on_checkbox_change(self, event):
        """Handle checkbox state changes and validate conflicts"""
        # Small delay to allow UI to update, then validate
        wx.CallAfter(self.validate_conflicts)

    def get_tests_used_in_rules(self):
        """Get set of test codes that are used in flagging rules"""
        if not self.top_dialog:
            return set()

        used_tests = set()

        # Get the flags page from the parent dialog
        if 'flags' in self.top_dialog.pages:
            flags_page = self.top_dialog.pages['flags']

            # Check each flux rule panel
            for flux_code, rule_panel in flags_page.rule_panels.items():
                # Get current rules from the grid
                for row in range(rule_panel.grid.GetNumberRows()):
                    test = rule_panel.grid.GetCellValue(row,
                                                        1)  # Test is in column 1
                    if test and test in QC_TESTS:
                        used_tests.add(test)

        if 'general'  in self.top_dialog.pages:
            general_page = self.top_dialog.pages['general']

            selection = general_page.controls['Despiking'].GetCurrentSelection()
            test = DESPIKING_METHODS[selection][0]
            used_tests.add(test)

        return used_tests

    def validate_conflicts(self):
        """Check for conflicts between disabled tests and flagging rules"""
        used_tests = self.get_tests_used_in_rules()

        errors = []
        for test_code, checkbox in self.checkboxes.items():
            if checkbox.GetValue() and test_code in used_tests:
                # Test is disabled but used in rules - show conflict
                checkbox.SetBackgroundColour(
                    wx.Colour(255, 200, 200))  # Light red
                tooltip = f"{test_code} - This test is disabled but used in flagging rules!"
                errors.append(tooltip)
            else:
                # No conflict - normal background
                checkbox.SetBackgroundColour(
                    wx.SystemSettings.GetColour(
                        wx.SYS_COLOUR_APPWORKSPACE))
                description = QC_TESTS.get(test_code, test_code)
                tooltip = f"{test_code} - {description}"

            checkbox.SetToolTip(tooltip)
            checkbox.Refresh()

        return errors
    def set_disabled_tests(self, disabled_tests):
        """Set which tests are disabled"""
        for code, checkbox in self.checkboxes.items():
            checkbox.SetValue(code in disabled_tests)

        # Validate conflicts after setting values
        wx.CallAfter(self.validate_conflicts)

    def get_disabled_tests(self):
        """Get list of disabled tests"""
        return [code for code, checkbox in self.checkboxes.items()
                if checkbox.GetValue()]

class FilesPage(ConfigPageBase):
    """Files and directories page"""

    def __init__(self, parent, top):
        super().__init__(parent, top)
        self.init_ui()

    def init_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Directories
        dir_sizer = self.add_section(main_sizer, "Directories")
        self.add_path_field(dir_sizer, "", "RawDir")
        self.add_path_field(dir_sizer, "", "DatDir")
        self.add_path_field(dir_sizer, "", "OutDir")
        self.add_path_field(dir_sizer, "", "Parmdir")

        # Input files
        input_sizer = self.add_section(main_sizer, "Input Data Files")
        self.add_text_field(input_sizer, "", "RawFastData")
        self.add_text_field(input_sizer, "", "RawSlowData")

        format_choices = ["toa5", "netcdf", "ascii"]
        self.add_choice_field(input_sizer, "", "RawFormat",
                              format_choices, 0)

        # Output files
        output_sizer = self.add_section(main_sizer, "Output Files")
        self.add_text_field(output_sizer, "", "FluxName")
        self.add_text_field(output_sizer, "", "QCOutName")
        self.add_text_field(output_sizer, "", "InterName")

        self.SetSizer(main_sizer)

    def add_path_field(self, parent_sizer, label, key, default=''):
        """Add a path field with browse button"""
        field_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Get label and tooltip from defaults if not provided
        if not label and key in defaults:
            label = defaults[key].get('short', key)

        # Generate tooltip from defaults
        tooltip = ''
        if key in defaults:
            comment = defaults[key].get('comment', '')
            tooltip = f"{key} - {comment}" if comment else key

        # Get default value from defaults if not provided
        if not default and key in defaults:
            default = defaults[key].get('value', '')

        label_ctrl = wx.StaticText(self, label=label, size=(150, -1))
        text_ctrl = wx.TextCtrl(self, value=default, size=(200, -1))
        browse_btn = wx.Button(self, label="Browse...", size=(80, 30))

        if tooltip:
            text_ctrl.SetToolTip(tooltip)

        browse_btn.Bind(wx.EVT_BUTTON,
                        lambda evt: self.on_browse_path(text_ctrl))

        field_sizer.Add(label_ctrl, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL,
                        5)
        field_sizer.Add(text_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        field_sizer.Add(browse_btn, 0, wx.ALL, 5)

        parent_sizer.Add(field_sizer, 0, wx.EXPAND)
        self.controls[key] = text_ctrl
        return text_ctrl

    def on_browse_path(self, text_ctrl):
        """Browse for directory path"""
        with wx.DirDialog(self, "Choose directory") as dialog:
            if dialog.ShowModal() == wx.ID_OK:
                text_ctrl.SetValue(dialog.GetPath())

    def load_config(self, config):
        """Load configuration values"""
        for key, control in self.controls.items():
            value = config.pull(key, '')
            if isinstance(control, wx.TextCtrl):
                control.SetValue(str(value))
            elif isinstance(control, wx.Choice):
                # Handle choice controls
                control.SetStringSelection(str(value))

    def save_config(self, config):
        """Save configuration values"""
        for key, control in self.controls.items():
            if isinstance(control, wx.TextCtrl):
                config.push(key, control.GetValue())
            elif isinstance(control, wx.Choice):
                config.push(key, control.GetStringSelection())


class FlagsPage(ConfigPageBase):
    """Flagging rules page with notebook for different flux types"""

    def __init__(self, parent, top):
        super().__init__(parent, top)
        self.flag_rules = {}
        self.inter_rules = []
        self.init_ui()

    def init_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Create notebook for different rule types
        self.notebook = wx.Notebook(self)

        # Individual flux rule pages
        self.rule_panels = {}
        for flux_code in FLUX_CODES:
            page = FluxRulePage(self.notebook, flux_code)
            self.notebook.AddPage(page, f"{flux_code.upper()} Rules")
            self.rule_panels[flux_code] = page

        # Inter-rules page
        self.inter_panel = InterRulePage(self.notebook)
        self.notebook.AddPage(self.inter_panel, "Inter-flag Dependencies")

        main_sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(main_sizer)

    def load_config(self, config):
        """Load flag rules from configuration"""
        # Load flag rules for each flux
        for flux_code, panel in self.rule_panels.items():
            rules_str = config.pull(f'qcconf.flag_{flux_code}')
            if rules_str:
                panel.set_rules(rules_str)

        # Load inter-rules
        inter_rules_str = config.pull('qcconf.interrule', '')
        if inter_rules_str:
            self.inter_panel.set_rules(inter_rules_str)

    def save_config(self, config):
        """Save flag rules to configuration"""
        # Save flag rules for each flux
        for flux_code, panel in self.rule_panels.items():
            rules_str = panel.get_rules()
            if rules_str:
                rules_key = f'qcconf.flag_{flux_code}'
                config.push(rules_key, rules_str)

        # Save inter-rules
        inter_rules_str = self.inter_panel.get_rules()
        if inter_rules_str:
            config.push('qcconf.interrule', inter_rules_str)


class FluxRulePage(scrolled.ScrolledPanel):
    """Page for editing flag rules for a specific flux type"""

    def __init__(self, parent, flux_code):
        super().__init__(parent)
        self.SetupScrolling()
        self.flux_code = flux_code
        self.rules = []
        self.init_ui()

    def init_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Add explanation for this flux type
        explanation = wx.StaticText(self, label=
            f"Define flagging rules for {self.flux_code.upper()} flux.\n"
            "Format: variable_test[action][level], where:\n"
            "• action: u=use, i=increase, s=soft, h=hard\n"
            "• level: minimum flag level to trigger action")
        explanation.Wrap(700)
        main_sizer.Add(explanation, 0, wx.ALL, 10)

        # Create grid for rules directly on this page
        self.grid = wx.grid.Grid(self, size=(600, 200))
        self.grid.CreateGrid(5, 4)  # Start with fewer rows

        # Set column labels
        self.grid.SetColLabelValue(0, "Variable")
        self.grid.SetColLabelValue(1, "Test")
        self.grid.SetColLabelValue(2, "Action")
        self.grid.SetColLabelValue(3, "Level")

        # Set column widths
        self.grid.SetColSize(0, 80)
        self.grid.SetColSize(1, 80)
        self.grid.SetColSize(2, 80)
        self.grid.SetColSize(3, 60)

        # Set minimum row height to prevent negative content height
        self.grid.SetDefaultRowSize(25)

        # Create choice editors
        self.setup_grid_editors()

        main_sizer.Add(self.grid, 1, wx.EXPAND | wx.ALL, 5)

        # Add/remove buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        add_btn = wx.Button(self, label="Add Rule", size=(80, 30))
        remove_btn = wx.Button(self, label="Remove Rule", size=(80, 30))

        add_btn.Bind(wx.EVT_BUTTON, self.on_add_rule)
        remove_btn.Bind(wx.EVT_BUTTON, self.on_remove_rule)

        btn_sizer.Add(add_btn, 0, wx.ALL, 5)
        btn_sizer.Add(remove_btn, 0, wx.ALL, 5)

        main_sizer.Add(btn_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        self.SetSizer(main_sizer)

    def setup_grid_editors(self):
        """Setup choice editors for grid cells"""
        # Apply editors to columns
        for row in range(self.grid.GetNumberRows()):
            self.grid.SetCellEditor(row, 0, wx.grid.GridCellChoiceEditor(
                VARIABLE_CODES))
            self.grid.SetCellEditor(row, 1, wx.grid.GridCellChoiceEditor(
                list(QC_TESTS.keys())))
            self.grid.SetCellEditor(row, 2, wx.grid.GridCellChoiceEditor(
                ['u', 'i', 's', 'h']))
            self.grid.SetCellEditor(row, 3, wx.grid.GridCellChoiceEditor(
                ['0', '1', '2']))

    def on_add_rule(self, event):
        """Add a new rule row"""
        if self.grid.GetNumberRows() < 20:  # Limit number of rows
            current_rows = self.grid.GetNumberRows()
            self.grid.AppendRows(1)
            self.setup_row_editors(current_rows)

    def on_remove_rule(self, event):
        """Remove selected rule row"""
        selected_rows = self.grid.GetSelectedRows()
        if selected_rows:
            # Remove rows in reverse order to maintain indices
            for row in sorted(selected_rows, reverse=True):
                if self.grid.GetNumberRows() > 1:  # Keep at least one row
                    self.grid.DeleteRows(row, 1)
        elif self.grid.GetNumberRows() > 1:
            # Remove last row if none selected
            self.grid.DeleteRows(self.grid.GetNumberRows() - 1, 1)

    def setup_row_editors(self, row):
        """Setup editors for a specific row"""
        test_choices = list(QC_TESTS.keys())
        action_choices = ['u', 'i', 's', 'h']
        level_choices = ['0', '1', '2']

        self.grid.SetCellEditor(row, 0, wx.grid.GridCellChoiceEditor(
            VARIABLE_CODES))
        self.grid.SetCellEditor(row, 1,
                                wx.grid.GridCellChoiceEditor(test_choices))
        self.grid.SetCellEditor(row, 2, wx.grid.GridCellChoiceEditor(
            action_choices))
        self.grid.SetCellEditor(row, 3, wx.grid.GridCellChoiceEditor(
            level_choices))

    def set_rules(self, rules_str):
        """Parse and set rules from string"""
        if isinstance(rules_str, list):
            rules = rules_str.copy()
        else:
            if not rules_str.strip():
                # empty string - empty list
                rules = []
            else:
                # Parse rules - handle different formats
                rules = [x.strip() for x in rules_str.split()]
                if not rules:
                    rules = []

        # Clear existing rules first
        current_rows = self.grid.GetNumberRows()
        if current_rows > 0:
            self.grid.DeleteRows(0, current_rows)

        # Check if first element is flux code - if so, skip it
        start_idx = 0
        if rules and rules[0].lower() in [code.lower() for code in
                                          FLUX_CODES]:
            start_idx = 1

        rule_count = 0
        for i in range(start_idx, len(rules)):
            rule = rules[i]
            if rule_count >= 20:  # Limit number of rules
                break

            # Add a new row
            self.grid.AppendRows(1)
            row = self.grid.GetNumberRows() - 1
            self.setup_row_editors(row)

            # Parse rule format: variable_test[action][level]
            # Examples: "ux__spk", "uy__spks", "h2o_spkh2"
            if '_' in rule and len(rule) >= 7:

                # extract rule parts
                var_part = rule[0:3]
                test_part = rule[4:]

                # # treat multiple _ as one (var code is filled with "_")
                # parts = re.sub('_+', '_', rule).split('_', 1)
                # var_part = parts[0]
                # test_part = parts[1] if len(parts) > 1 else ''

                # var code is filled with "_"
                variable = var_part.replace('_', '')

                # Set variable
                if variable in VARIABLE_CODES:
                    self.grid.SetCellValue(row, 0, variable)
                else:
                    # Try to match partial names
                    for var_code in VARIABLE_CODES:
                        if variable.lower() in var_code.lower():
                            self.grid.SetCellValue(row, 0, var_code)
                            break
                    else:
                        self.grid.SetCellValue(row, 0,
                                               variable)  # Use as-is

                if test_part:
                    # Extract test, action, and level
                    test = test_part[0:3]
                    if len(test_part) > 3:
                        action = test_part[3:4]
                    else:
                        action = 'u'
                    if len(test_part) > 3:
                        level = test_part[4:5]
                    else:
                        level = '0'

                    # Set test - try exact match first, then partial
                    if test in QC_TESTS:
                        self.grid.SetCellValue(row, 1, test)
                    else:
                        # Try to match partial test names
                        for test_code in QC_TESTS.keys():
                            if test.lower() in test_code.lower() or test_code.lower().startswith(
                                    test.lower()):
                                self.grid.SetCellValue(row, 1, test_code)
                                break
                        else:
                            self.grid.SetCellValue(row, 1,
                                                   test)  # Use as-is

                    self.grid.SetCellValue(row, 2, action)
                    self.grid.SetCellValue(row, 3, level)

                rule_count += 1
            else:
                logger.warning(f"Invalid flux rule: {rule}")

        # Ensure we have at least one empty row for new entries
        if self.grid.GetNumberRows() == 0:
            self.grid.AppendRows(1)
            self.setup_row_editors(0)

    def get_rules(self):
        """Generate rules string from grid"""
        rules = []

        for row in range(self.grid.GetNumberRows()):
            var = self.grid.GetCellValue(row, 0)
            test = self.grid.GetCellValue(row, 1)
            action = self.grid.GetCellValue(row, 2)
            level = self.grid.GetCellValue(row, 3)

            # fill var code with "_"
            var = var + '_' * (3 - len(var))

            if var and test:
                rule = f"{var}_{test}"
                if action and action != 'u':
                    rule += action
                if level and level != '0':
                    rule += level
                rules.append(rule)

        return ' '.join(rules) if len(rules) > 1 else ''


class InterRulePage(scrolled.ScrolledPanel):
    """Page for editing inter-flag dependency rules"""

    def __init__(self, parent):
        super().__init__(parent)
        self.SetupScrolling()
        self.init_ui()

    def init_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Add explanation for inter-rules
        explanation = wx.StaticText(self, label=
            "Define dependencies between different flux flags.\n"
            "Format: target_flux + action + condition_fluxes\n"
            "• action: i=increase, d=delete\n"
            "• Applied when all condition fluxes are flagged as bad (2)")
        explanation.Wrap(700)
        main_sizer.Add(explanation, 0, wx.ALL, 10)

        # Create grid for inter-rules directly on this page
        self.grid = wx.grid.Grid(self, size=(500, 150))
        self.grid.CreateGrid(3, 3)  # Start with fewer rows

        # Set column labels
        self.grid.SetColLabelValue(0, "Target Flux")
        self.grid.SetColLabelValue(1, "Action")
        self.grid.SetColLabelValue(2, "Condition Fluxes")

        # Set column widths
        self.grid.SetColSize(0, 100)
        self.grid.SetColSize(1, 80)
        self.grid.SetColSize(2, 200)

        # Set minimum row height
        self.grid.SetDefaultRowSize(25)

        # Setup editors
        self.setup_grid_editors()

        main_sizer.Add(self.grid, 1, wx.EXPAND | wx.ALL, 5)

        # Add/remove buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        add_btn = wx.Button(self, label="Add Rule", size=(80, 30))
        remove_btn = wx.Button(self, label="Remove Rule", size=(80, 30))

        add_btn.Bind(wx.EVT_BUTTON, self.on_add_rule)
        remove_btn.Bind(wx.EVT_BUTTON, self.on_remove_rule)

        btn_sizer.Add(add_btn, 0, wx.ALL, 5)
        btn_sizer.Add(remove_btn, 0, wx.ALL, 5)

        main_sizer.Add(btn_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        self.SetSizer(main_sizer)

    def setup_grid_editors(self):
        """Setup choice editors for grid cells"""
        # Apply editors to columns
        for row in range(self.grid.GetNumberRows()):
            self.grid.SetCellEditor(row, 0, wx.grid.GridCellChoiceEditor(
                FLUX_CODES))
            self.grid.SetCellEditor(row, 1, wx.grid.GridCellChoiceEditor(
                ['i', 'd']))

    def on_add_rule(self, event):
        """Add a new rule row"""
        if self.grid.GetNumberRows() < 10:  # Limit number of rows
            current_rows = self.grid.GetNumberRows()
            self.grid.AppendRows(1)
            self.setup_row_editors(current_rows)

    def on_remove_rule(self, event):
        """Remove selected rule row"""
        selected_rows = self.grid.GetSelectedRows()
        if selected_rows:
            for row in sorted(selected_rows, reverse=True):
                if self.grid.GetNumberRows() > 1:
                    self.grid.DeleteRows(row, 1)
        elif self.grid.GetNumberRows() > 1:
            self.grid.DeleteRows(self.grid.GetNumberRows() - 1, 1)

    def setup_row_editors(self, row):
        """Setup editors for a specific row"""
        self.grid.SetCellEditor(row, 0,
                                wx.grid.GridCellChoiceEditor(FLUX_CODES))
        self.grid.SetCellEditor(row, 1,
                                wx.grid.GridCellChoiceEditor(['i', 'd']))

    def set_rules(self, rules_str):
        """Parse and set inter-rules from string"""
        if isinstance(rules_str, list):
            rules = rules_str.copy()
        else:
            if not rules_str.strip():
                # empty string - empty list
                rules = []
            else:
                # Parse rules - handle different formats
                rules = [x.strip() for x in rules_str.split()]
                if not rules:
                    rules = []

        # Clear existing rules
        current_rows = self.grid.GetNumberRows()
        if current_rows > 0:
            self.grid.DeleteRows(0, current_rows)

        # Parse rules - handle different formats
        rule_count = 0

        for rule in rules:
            if len(rule) >= 4 and rule_count < 10:  # Minimum length for valid rule and limit
                self.grid.AppendRows(1)
                row = self.grid.GetNumberRows() - 1
                self.setup_row_editors(row)

                # Parse rule format: target_flux + action + condition_fluxes
                # Examples: "h_0itau", "e_0itau", "fc2ie_0"

                # Try different parsing approaches
                target = ''
                action = ''
                conditions = ''

                # Method 1: Look for known flux codes at start
                for flux_code in FLUX_CODES:
                    if rule.startswith(flux_code):
                        target = flux_code
                        remaining = rule[len(flux_code):]
                        if remaining and remaining[0] in ['i', 'd']:
                            action = remaining[0]
                            conditions = remaining[1:]
                        break

                # Method 2: If method 1 didn't work, try standard 3-char format
                if not target and len(rule) >= 4:
                    target = rule[:3]
                    if rule[3] in ['i', 'd']:
                        action = rule[3]
                        conditions = rule[4:]

                # Set values
                if target in FLUX_CODES:
                    self.grid.SetCellValue(row, 0, target)
                else:
                    # Try to match partial names
                    for flux_code in FLUX_CODES:
                        if target.lower() in flux_code.lower():
                            self.grid.SetCellValue(row, 0, flux_code)
                            break
                    else:
                        self.grid.SetCellValue(row, 0, target)

                if action in ['i', 'd']:
                    self.grid.SetCellValue(row, 1, action)

                if conditions:
                    # Parse condition fluxes (groups of 3 characters or known flux codes)
                    condition_list = []
                    remaining_conditions = conditions

                    while remaining_conditions:
                        found_flux = False
                        # Try to match known flux codes first
                        for flux_code in FLUX_CODES:
                            if remaining_conditions.startswith(flux_code):
                                condition_list.append(flux_code)
                                remaining_conditions = remaining_conditions[
                                                       len(flux_code):]
                                found_flux = True
                                break

                        # If no flux code matched, try 3-character groups
                        if not found_flux:
                            if len(remaining_conditions) >= 3:
                                condition_list.append(
                                    remaining_conditions[:3])
                                remaining_conditions = remaining_conditions[
                                                       3:]
                            else:
                                # Add remaining characters as-is
                                if remaining_conditions:
                                    condition_list.append(
                                        remaining_conditions)
                                break

                    self.grid.SetCellValue(row, 2,
                                           ' '.join(condition_list))

                rule_count += 1

        # Ensure we have at least one empty row for new entries
        if self.grid.GetNumberRows() == 0:
            self.grid.AppendRows(1)
            self.setup_row_editors(0)

    def get_rules(self):
        """Generate inter-rules string from grid"""
        rules = []

        for row in range(self.grid.GetNumberRows()):
            target = self.grid.GetCellValue(row, 0)
            action = self.grid.GetCellValue(row, 1)
            conditions = self.grid.GetCellValue(row, 2)

            if target and action and conditions:
                # Combine conditions (remove spaces)
                condition_codes = ''.join(conditions.split())
                rule = f"{target}{action}{condition_codes}"
                rules.append(rule)

        return ' '.join(rules)

# Additional page classes for completeness

class TimePage(ConfigPageBase):
    """Time selection page"""

    def __init__(self, parent, top):
        super().__init__(parent, top)
        self.init_ui()

    def init_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Time range
        time_sizer = self.add_section(main_sizer, "Processing Time Range")
        self.add_text_field(time_sizer, "", "DateBegin")
        self.add_text_field(time_sizer, "", "DateEnd")

        # Intervals
        interval_sizer = self.add_section(main_sizer,
                                          "Processing Intervals")
        self.add_text_field(interval_sizer, "", "AvgInterval")
        self.add_text_field(interval_sizer, "", "PlfitInterval")

        self.SetSizer(main_sizer)

    def load_config(self, config):
        for key, control in self.controls.items():
            value = config.pull(key, '')
            control.SetValue(str(value))

    def save_config(self, config):
        for key, control in self.controls.items():
            config.push(key, control.GetValue())


class SitePage(ConfigPageBase):
    """Site information page"""

    def __init__(self, parent, top):
        super().__init__(parent, top)
        self.init_ui()

    def init_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Location
        location_sizer = self.add_section(main_sizer, "Site Location")
        self.add_text_field(location_sizer, "", "InstLatLon",
                            expected_type='coordinate')
        self.add_text_field(location_sizer, "", "Displacement")

        # Source area
        source_sizer = self.add_section(main_sizer, "Source Area")
        self.add_path_field(source_sizer, "", "SourceArea")

        # Excluded sectors
        sector_sizer = self.add_section(main_sizer,
                                        "Excluded Wind Sectors")
        self.sector_panel = ExcludedSectorPanel(self)
        sector_sizer.Add(self.sector_panel, 1, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(main_sizer)

    def add_path_field(self, parent_sizer, label, key, default='',
                       tooltip=''):
        """Add a file path field with browse button"""
        field_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Get label and tooltip from defaults if not provided
        if not label and key in defaults:
            label = defaults[key].get('short', key)
        if not tooltip and key in defaults:
            comment = defaults[key].get('comment', '')
            tooltip = f"{key} - {comment}" if comment else key

        # Get default value from defaults if not provided
        if not default and key in defaults:
            default = defaults[key].get('value', '')

        label_ctrl = wx.StaticText(self, label=label, size=(150, -1))
        text_ctrl = wx.TextCtrl(self, value=default, size=(200, -1))
        browse_btn = wx.Button(self, label="Browse...", size=(80, 30))

        if tooltip:
            text_ctrl.SetToolTip(tooltip)

        browse_btn.Bind(wx.EVT_BUTTON,
                        lambda evt: self.on_browse_file(text_ctrl))

        field_sizer.Add(label_ctrl, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL,
                        5)
        field_sizer.Add(text_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        field_sizer.Add(browse_btn, 0, wx.ALL, 5)

        parent_sizer.Add(field_sizer, 0, wx.EXPAND)
        self.controls[key] = text_ctrl
        return text_ctrl

    def on_browse_file(self, text_ctrl):
        """Browse for file path"""
        with wx.FileDialog(self, "Choose file") as dialog:
            if dialog.ShowModal() == wx.ID_OK:
                text_ctrl.SetValue(dialog.GetPath())

    def load_config(self, config):
        for key, control in self.controls.items():
            if key == 'InstLatLon':
                value = config.pull(key, kind='float', na=[])
                control.SetValue(' '.join([str(x) for x in value]))
            else:
                value = config.pull(key, '')
                control.SetValue(str(value))

        # Load excluded sectors
        if hasattr(self, 'sector_panel'):
            sectors = config.pull('ExcludeSector', kind='float', na=[])
            self.sector_panel.set_sectors(sectors)

    def save_config(self, config):
        for key, control in self.controls.items():
            if key == 'InstLatLon':
                try:
                    value = [float(x)
                             for x in control.GetValue().strip().split()]
                except (ValueError,TypeError):
                    value = []
            else:
                value = control.GetValue()
            config.push(key, value)

        # Save excluded sectors
        if hasattr(self, 'sector_panel'):
            sectors = self.sector_panel.get_sectors()
            if sectors:
                config.push('ExcludeSector', sectors)


class ExcludedSectorPanel(wx.Panel):
    """Panel for editing excluded wind sectors"""

    def __init__(self, parent):
        super().__init__(parent)
        self.sectors = []
        self.init_ui()

    def init_ui(self):
        sizer = wx.BoxSizer(wx.VERTICAL)

        label = wx.StaticText(self,
                              label="Excluded Wind Direction Sectors (degrees from North):")
        sizer.Add(label, 0, wx.ALL, 5)

        # List control for sectors
        self.sector_list = wx.ListCtrl(self,
                                       style=wx.LC_REPORT | wx.LC_SINGLE_SEL,
                                       size=(300, 150))
        self.sector_list.AppendColumn("Start", width=100)
        self.sector_list.AppendColumn("End", width=100)

        sizer.Add(self.sector_list, 1, wx.EXPAND | wx.ALL, 5)

        # Input fields for new sector
        input_sizer = wx.BoxSizer(wx.HORIZONTAL)

        input_sizer.Add(wx.StaticText(self, label="Start:"), 0,
                        wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.start_ctrl = wx.SpinCtrl(self, min=0, max=360, initial=0,
                                      size=(80, -1))
        input_sizer.Add(self.start_ctrl, 0, wx.ALL, 5)

        input_sizer.Add(wx.StaticText(self, label="End:"), 0,
                        wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.end_ctrl = wx.SpinCtrl(self, min=0, max=360, initial=0,
                                    size=(80, -1))
        input_sizer.Add(self.end_ctrl, 0, wx.ALL, 5)

        add_btn = wx.Button(self, label="Add", size=(60, 30))
        remove_btn = wx.Button(self, label="Remove", size=(60, 30))

        add_btn.Bind(wx.EVT_BUTTON, self.on_add_sector)
        remove_btn.Bind(wx.EVT_BUTTON, self.on_remove_sector)

        input_sizer.Add(add_btn, 0, wx.ALL, 5)
        input_sizer.Add(remove_btn, 0, wx.ALL, 5)

        sizer.Add(input_sizer, 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(sizer)

    def on_add_sector(self, event):
        """Add a new excluded sector"""
        start = self.start_ctrl.GetValue()
        end = self.end_ctrl.GetValue()

        if start != end:  # Avoid zero-width sectors
            index = self.sector_list.InsertItem(
                self.sector_list.GetItemCount(), str(start))
            self.sector_list.SetItem(index, 1, str(end))
            self.sectors.append((start, end))

    def on_remove_sector(self, event):
        """Remove selected sector"""
        selected = self.sector_list.GetFirstSelected()
        if selected >= 0:
            self.sector_list.DeleteItem(selected)
            if selected < len(self.sectors):
                del self.sectors[selected]

    def set_sectors(self, sectors):
        """Set excluded sectors from configuration"""
        self.sectors = []
        self.sector_list.DeleteAllItems()

        for sector in sectors:
            if isinstance(sector, str) and ' ' in sector:
                parts = sector.split()
                if len(parts) >= 2:
                    try:
                        start = int(parts[0])
                        end = int(parts[1])
                        index = self.sector_list.InsertItem(
                            self.sector_list.GetItemCount(), str(start))
                        self.sector_list.SetItem(index, 1, str(end))
                        self.sectors.append((start, end))
                    except ValueError:
                        pass

    def get_sectors(self):
        """Get excluded sectors for configuration"""
        return [f"{start} {end}" for start, end in self.sectors]


class DevicesPage(ConfigPageBase):
    """Device calibration page with notebook tabs for different device types"""

    def __init__(self, parent, top):
        super().__init__(parent, top)
        self.device_panels = {}
        self.init_ui()

    def init_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Create notebook for device types
        self.notebook = wx.Notebook(self)

        # Device configuration tabs organized by type
        device_tabs = [
            ('SonCal', 'Sonic Anemometer', 'Sonic'),
            ('CoupCal', 'Fast Thermometer', 'Thermo'),
            ('HygCal', 'Hygrometer', 'Hygro'),
            ('Co2Cal', 'CO₂ Sensor', 'Hygro')
            # CO2 sensors are typically also hygro type
        ]

        for prefix, title, device_type in device_tabs:
            # Create panel for this device type
            panel = DevicePanel(self.notebook, prefix, title, device_type)
            self.notebook.AddPage(panel, title)
            self.device_panels[prefix] = panel

        main_sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(main_sizer)

    def load_config(self, config):
        for prefix, panel in self.device_panels.items():
            panel.load_config(config)

    def save_config(self, config):
        for prefix, panel in self.device_panels.items():
            panel.save_config(config)


class DevicePanel(wx.Panel):
    """Panel for configuring a single device with type filtering and QQExt support"""

    def __init__(self, parent, prefix, title, device_type_filter):
        super().__init__(parent)
        self.prefix = prefix
        self.title = title
        self.device_type_filter = device_type_filter
        if self.device_type_filter == 'Sonic':
            self.max_extended = 11
        else:
            self.max_extended = 5
        self.controls = {}
        self.ext_controls = {}
        self.init_ui()

    def validate_text_field(self, control):
        """Validate text field and set background color accordingly"""
        if not hasattr(control, 'config_key'):
            return

        value = control.GetValue().strip()
        config_key = control.config_key
        is_valid = True

        # Get expected type from defaults or control attribute
        if hasattr(control, 'expected_type'):
            expected_type = control.expected_type
        elif config_key in defaults:
            expected_type = defaults[config_key].get('type', 'str')
        else:
            expected_type = 'str'

        # Allow empty values for most types
        if value == '':
            # Check if this parameter has a default or is required
            if config_key in defaults:
                default_value = str(defaults[config_key].get('value', ''))
                # If default is empty, empty input is valid
                is_valid = (default_value == '')
            else:
                is_valid = True
        else:
            # Validate based on expected type
            if expected_type == 'int':
                try:
                    # Allow float representations that are integers
                    float_val = float(value)
                    int_val = int(float_val)
                    is_valid = (float_val == int_val)
                except (ValueError, OverflowError):
                    is_valid = False
            elif expected_type == 'float':
                try:
                    float(value)
                    is_valid = True
                except (ValueError, OverflowError):
                    is_valid = False
            elif expected_type == 'bool':
                try:
                    str_to_bool(value)
                    is_valid = True
                except (ValueError, TypeError):
                    is_valid = False
            elif expected_type == 'str':
                # Strings are always valid
                is_valid = True
            else:
                # Unknown type, assume valid
                is_valid = True

        # Set background color based on validation
        if is_valid:
            control.SetBackgroundColour(
                wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
        else:
            control.SetBackgroundColour(
                wx.Colour(255, 200, 200))  # Light red

        control.Refresh()

    def on_text_change(self, event):
        """Handle text change events for validation"""
        control = event.GetEventObject()
        self.validate_text_field(control)
        event.Skip()

    def init_ui(self):
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Device type selection - filtered by device type
        type_sizer = wx.BoxSizer(wx.HORIZONTAL)
        type_sizer.Add(wx.StaticText(self, label="Device Type:"), 0,
                       wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        # Filter device types based on the device type filter
        filtered_types = []
        filtered_codes = []
        for code, info in APPARATUS_TYPES.items():
            if info['type'] == self.device_type_filter:
                filtered_types.append(f"{code}: {info['desc']}")
                filtered_codes.append(code)



        self.type_choice = wx.Choice(self, choices=filtered_types,
                                     size=(300, -1))
        self.type_choice.Bind(wx.EVT_CHOICE, self.on_type_change)
        self.filtered_codes = filtered_codes  # Store for lookup

        type_sizer.Add(self.type_choice, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(type_sizer, 0, wx.EXPAND)
        self.controls[f'{self.prefix}.QQType'] = self.type_choice

        # Position coordinates
        pos_box = wx.StaticBox(self, label="Position (m)")
        pos_sizer = wx.StaticBoxSizer(pos_box, wx.HORIZONTAL)

        for coord in ['X', 'Y', 'Z']:
            pos_sizer.Add(wx.StaticText(self, label=f"{coord}:"), 0,
                          wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
            ctrl = ValidatedTextCtrl(self, size=(80, -1))
            # Set expected type and validation
            ctrl.expected_type = 'float'
            ctrl.config_key = f'{self.prefix}.QQ{coord}'
            ctrl.Bind(wx.EVT_TEXT, self.on_text_change)
            ctrl.Bind(wx.EVT_KILL_FOCUS, self.on_text_change)
            pos_sizer.Add(ctrl, 0, wx.ALL, 5)
            self.controls[f'{self.prefix}.QQ{coord}'] = ctrl

        sizer.Add(pos_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # Calibration parameters
        cal_box = wx.StaticBox(self, label="Calibration")
        cal_sizer = wx.StaticBoxSizer(cal_box, wx.VERTICAL)

        cal_grid = wx.FlexGridSizer(cols=4, hgap=5, vgap=5)

        cal_params = [
            ('Gain:', 'QQGain', '1.0', 'float'),
            ('Offset:', 'QQOffset', '0.0', 'float'),
            ('Order:', 'QQOrder', '1', 'int'),
            ('Function:', 'QQFunc', '1', 'int'),
        ]

        for label, param, default, expected_type in cal_params:
            cal_grid.Add(wx.StaticText(self, label=label), 0,
                         wx.ALIGN_CENTER_VERTICAL)
            ctrl = ValidatedTextCtrl(self, value=default, size=(80, -1))
            ctrl.expected_type = expected_type
            ctrl.config_key = f'{self.prefix}.{param}'
            ctrl.Bind(wx.EVT_TEXT, self.on_text_change)
            ctrl.Bind(wx.EVT_KILL_FOCUS, self.on_text_change)
            cal_grid.Add(ctrl, 0, wx.EXPAND)
            self.controls[f'{self.prefix}.{param}'] = ctrl

        cal_sizer.Add(cal_grid, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(cal_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # QQExt parameters section (initially hidden)
        self.ext_box = wx.StaticBox(self, label="Extended Parameters")
        self.ext_sizer = wx.StaticBoxSizer(self.ext_box, wx.VERTICAL)
        self.ext_grid = wx.FlexGridSizer(cols=4, hgap=5, vgap=5)

        # Create QQExt controls for potential use
        for i in range(3, self.max_extended + 1):  # QQExt3 through 5 / 11
            label_text = f"QQExt{i}:"
            label_ctrl = wx.StaticText(self, label=label_text)
            ctrl = ValidatedTextCtrl(self, value='0.0', size=(80, -1))
            ctrl.expected_type = 'float'
            ctrl.config_key = f'{self.prefix}.QQExt{i}'
            ctrl.Bind(wx.EVT_TEXT, self.on_text_change)
            ctrl.Bind(wx.EVT_KILL_FOCUS, self.on_text_change)

            # Initially hide all ext controls
            label_ctrl.Show()
            label_ctrl.Disable()
            ctrl.Show()
            ctrl.SetBackgroundColour(
                wx.SystemSettings.GetColour(wx.SYS_COLOUR_INACTIVECAPTION))
            ctrl.Disable()

            self.ext_grid.Add(label_ctrl, 0, wx.ALIGN_CENTER_VERTICAL)
            self.ext_grid.Add(ctrl, 0, wx.EXPAND)

            self.ext_controls[i] = (label_ctrl, ctrl)
            self.controls[f'{self.prefix}.QQExt{i}'] = ctrl

        self.ext_sizer.Add(self.ext_grid, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.ext_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # Initially hide the entire ext section
        self.ext_sizer.ShowItems(False)

        # Perform initial validation for all text controls
        for control in self.controls.values():
            if isinstance(control, ValidatedTextCtrl):
                self.validate_text_field(control)

        self.SetSizer(sizer)

    def on_type_change(self, event):
        """Handle device type change - show/hide QQExt parameters"""
        selection = self.type_choice.GetSelection()
        if 0 <= selection < len(self.filtered_codes):
            device_code = self.filtered_codes[selection]
            device_info = APPARATUS_TYPES.get(device_code, {})

            # Hide all ext controls first
            for i, (label_ctrl, ctrl) in self.ext_controls.items():
                label_ctrl.Hide()
                ctrl.Hide()

            # Show ext section and relevant controls if device has ext parameters
            ext_info = device_info.get('ext', None)
            if ext_info:
                self.ext_sizer.ShowItems(True)

                # Show only the ext controls that are defined for this device
                for ext_index in self.ext_controls.keys():
                    label_ctrl, ctrl = self.ext_controls[ext_index]
                    if ext_index in ext_info:
                        label_ctrl, ctrl = self.ext_controls[ext_index]
                        # label_ctrl.Show()
                        # ctrl.Show()
                        label_ctrl.Enable()
                        ctrl.Enable()
                        ctrl.SetBackgroundColour(
                            wx.SystemSettings.GetColour(
                                wx.SYS_COLOUR_BACKGROUND))
                        # Set default value from apparatus type
                        default_value = str(ext_info[ext_index])
                        ctrl.SetValue(default_value)
                    else:
                        ctrl.SetValue('')
                        label_ctrl.Disable()
                        ctrl.SetBackgroundColour(
                            wx.SystemSettings.GetColour(
                                wx.SYS_COLOUR_INACTIVECAPTION))
                        ctrl.Disable()


            else:
                # Hide the entire ext section
                self.ext_sizer.ShowItems(False)

            # Refresh layout
            self.Layout()

    def load_config(self, config):
        """Load device configuration"""
        for key, control in self.controls.items():
            value = config.pull(key, '')
            if isinstance(control, wx.Choice) and key.endswith('.QQType'):
                try:
                    device_type = int(value) if value else 0
                    # Find the device type in our filtered list
                    if device_type in self.filtered_codes:
                        selection_index = self.filtered_codes.index(
                            device_type)
                        control.SetSelection(selection_index)
                        # Trigger type change to show appropriate QQExt fields
                        self.on_type_change(None)
                except (ValueError, IndexError):
                    control.SetSelection(0)
            elif isinstance(control, ValidatedTextCtrl):
                control.SetValue(str(value))

    def save_config(self, config):
        """Save device configuration"""
        for key, control in self.controls.items():
            if isinstance(control, wx.Choice) and key.endswith('.QQType'):
                selection = control.GetSelection()
                if 0 <= selection < len(self.filtered_codes):
                    device_code = self.filtered_codes[selection]
                    config.push(key, str(device_code))
                else:
                    config.push(key, "0")  # Default to "Not present"
            elif isinstance(control, ValidatedTextCtrl):
                # Only save QQExt values if they are visible (device supports them)
                if key.endswith(tuple(f'.QQExt{i}' for i in range(3, 21))):
                    # Check if this ext parameter is visible
                    ext_num = int(key.split('QQExt')[1])
                    if ext_num in self.ext_controls:
                        label_ctrl, ctrl = self.ext_controls[ext_num]
                        if ctrl.IsShown():
                            config.push(key, control.GetValue())
                        # Don't save hidden QQExt parameters
                else:
                    # Save all other parameters normally
                    config.push(key, control.GetValue())


class FormatPage(ConfigPageBase):
    """Data format configuration page with column/name radio button selection"""

    def __init__(self, parent, top):
        super().__init__(parent, top)
        self.use_names = False  # False = use column numbers, True = use column names
        self.original_config = {}  # Store original config for revert
        self.field_edited = False  # Track if any field has been edited
        self.field_panels = {}  # Store panels for each field pair
        self.init_ui()

    def init_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Control panel with radio buttons and back button
        control_panel = wx.Panel(self)
        control_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Input mode selection with radio buttons
        mode_box = wx.StaticBox(control_panel, label="Input Mode")
        mode_sizer = wx.StaticBoxSizer(mode_box, wx.HORIZONTAL)

        self.column_radio = wx.RadioButton(control_panel,
                                           label="Use Column Numbers",
                                           style=wx.RB_GROUP)
        self.name_radio = wx.RadioButton(control_panel,
                                         label="Use Column Names")

        # Set initial selection
        self.column_radio.SetValue(True)
        self.name_radio.SetValue(False)

        # Bind events
        self.column_radio.Bind(wx.EVT_RADIOBUTTON, self.on_mode_change)
        self.name_radio.Bind(wx.EVT_RADIOBUTTON, self.on_mode_change)

        mode_sizer.Add(self.column_radio, 0, wx.ALL, 5)
        mode_sizer.Add(self.name_radio, 0, wx.ALL, 5)

        # Back button (initially hidden)
        self.back_button = wx.Button(control_panel,
                                     label="Back",
                                     size=(80, 30))
        self.back_button.Bind(wx.EVT_BUTTON, self.on_back)
        self.back_button.Hide()

        control_sizer.Add(mode_sizer, 0, wx.ALL, 5)
        control_sizer.AddStretchSpacer()
        control_sizer.Add(self.back_button, 0, wx.ALL, 5)

        control_panel.SetSizer(control_sizer)
        main_sizer.Add(control_panel, 0, wx.EXPAND | wx.ALL, 5)

        # Fast data format
        fast_sizer = self.add_section(main_sizer,
                                      "Fast Data Column Mapping")

        self.fast_vars = [
            ('fastfmt.U_col', 'fastfmt.U_nam'),
            ('fastfmt.V_col', 'fastfmt.V_nam'),
            ('fastfmt.W_col', 'fastfmt.W_nam'),
            ('fastfmt.Tsonic_col', 'fastfmt.Tsonic_nam'),
            ('fastfmt.Tcouple_col', 'fastfmt.Tcouple_nam'),
            ('fastfmt.Humidity_col', 'fastfmt.Humidity_nam'),
            ('fastfmt.CO2_col', 'fastfmt.CO2_nam'),
            ('fastfmt.Press_col', 'fastfmt.Press_nam'),
            ('fastfmt.diag_col', 'fastfmt.diag_nam'),
            ('fastfmt.agc_col', 'fastfmt.agc_nam'),
        ]

        self.fast_controls = {}
        for col_key, nam_key in self.fast_vars:
            # Create a panel for each field pair
            field_panel = wx.Panel(self)
            field_sizer = wx.BoxSizer(wx.VERTICAL)

            # Get label from defaults
            label = defaults.get(col_key, {}).get('short',
                                                  col_key.split('.')[-1])

            # Create both column and name field panels
            col_panel = self.create_field_panel(field_panel, label,
                                                col_key, 'int')
            nam_panel = self.create_field_panel(field_panel, label,
                                                nam_key, 'str')

            # Add panels to field sizer
            field_sizer.Add(col_panel, 0, wx.EXPAND)
            field_sizer.Add(nam_panel, 0, wx.EXPAND)

            # Initially hide name panel
            nam_panel.Hide()

            field_panel.SetSizer(field_sizer)
            fast_sizer.Add(field_panel, 0, wx.EXPAND | wx.ALL, 2)

            # Store references
            self.field_panels[col_key] = col_panel
            self.field_panels[nam_key] = nam_panel

        # Slow data format
        slow_sizer = self.add_section(main_sizer,
                                      "Slow Data Column Mapping")

        self.slow_vars = [
            ('slowfmt.Tref_col', 'slowfmt.Tref_nam'),
            ('slowfmt.RelHum_col', 'slowfmt.RelHum_nam'),
            ('slowfmt.Pref_col', 'slowfmt.Pref_nam'),
        ]

        self.slow_controls = {}
        for col_key, nam_key in self.slow_vars:
            # Create a panel for each field pair
            field_panel = wx.Panel(self)
            field_sizer = wx.BoxSizer(wx.VERTICAL)

            # Get label from defaults
            label = defaults.get(col_key, {}).get('short',
                                                  col_key.split('.')[-1])

            # Create both column and name field panels
            col_panel = self.create_field_panel(field_panel, label,
                                                col_key, 'int')
            nam_panel = self.create_field_panel(field_panel, label,
                                                nam_key, 'str')

            # Add panels to field sizer
            field_sizer.Add(col_panel, 0, wx.EXPAND)
            field_sizer.Add(nam_panel, 0, wx.EXPAND)

            # Initially hide name panel
            nam_panel.Hide()

            field_panel.SetSizer(field_sizer)
            slow_sizer.Add(field_panel, 0, wx.EXPAND | wx.ALL, 2)

            # Store references
            self.field_panels[col_key] = col_panel
            self.field_panels[nam_key] = nam_panel

        self.SetSizer(main_sizer)

    def create_field_panel(self, parent, label, key, expected_type):
        """Create a panel containing a single field with label and text control"""
        panel = wx.Panel(parent)
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Create label
        label_ctrl = wx.StaticText(panel, label=label, size=(150, -1))

        # Create text control
        text_ctrl = ValidatedTextCtrl(panel, size=(200, -1))
        text_ctrl.expected_type = expected_type
        text_ctrl.config_key = key

        # Bind events
        text_ctrl.Bind(wx.EVT_TEXT, self.on_field_edited)
        text_ctrl.Bind(wx.EVT_KILL_FOCUS, self.on_text_change)

        # Add tooltip if available
        if key in defaults:
            comment = defaults[key].get('comment', '')
            tooltip = f"{key} - {comment}" if comment else key
            text_ctrl.SetToolTip(tooltip)

        # Add to sizer
        sizer.Add(label_ctrl, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        sizer.Add(text_ctrl, 1, wx.EXPAND | wx.ALL, 5)

        panel.SetSizer(sizer)

        # Store control reference
        self.controls[key] = text_ctrl

        return panel

    def on_text_change(self, event):
        """Handle text change events for validation"""
        control = event.GetEventObject()
        self.validate_text_field(control)
        event.Skip()

    def validate_text_field(self, control):
        """Validate text field and set background color accordingly"""
        if not hasattr(control, 'config_key'):
            return

        value = control.GetValue().strip()
        config_key = control.config_key
        is_valid = True

        # Get expected type
        if hasattr(control, 'expected_type'):
            expected_type = control.expected_type
        else:
            expected_type = 'str'

        # Allow empty values for most types
        if value == '':
            is_valid = True
        else:
            # Validate based on expected type
            if expected_type == 'int':
                try:
                    int(value)
                    is_valid = True
                except (ValueError, OverflowError):
                    is_valid = False
            elif expected_type == 'float':
                try:
                    float(value)
                    is_valid = True
                except (ValueError, OverflowError):
                    is_valid = False
            elif expected_type == 'str':
                is_valid = True

        # Set background color based on validation
        if is_valid:
            control.SetBackgroundColour(
                wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
        else:
            control.SetBackgroundColour(
                wx.Colour(255, 200, 200))  # Light red

        control.Refresh()

    def on_mode_change(self, event):
        """Handle radio button mode change"""
        if self.field_edited:
            # Prevent switch if fields have been edited
            # Restore previous selection
            self.column_radio.SetValue(not self.use_names)
            self.name_radio.SetValue(self.use_names)
            wx.MessageBox(
                "Cannot switch modes while fields are edited. Use 'Back' to revert changes first.",
                "Fields Modified", wx.OK | wx.ICON_WARNING)
            return

        self.use_names = self.name_radio.GetValue()
        self.update_display_mode()
        # Save current state as the new "original" state
        self.save_current_state()

    def on_field_edited(self, event):
        """Handle field editing - disable radio buttons and show back button"""
        if not self.field_edited:
            self.field_edited = True
            self.column_radio.Enable(False)
            self.name_radio.Enable(False)
            self.back_button.Show()
            self.GetParent().Layout()  # Refresh layout to show back button
        event.Skip()

    def on_back(self, event):
        """Revert to original state"""
        self.revert_to_original()
        self.field_edited = False
        self.column_radio.Enable(True)
        self.name_radio.Enable(True)
        self.back_button.Hide()
        self.GetParent().Layout()

    def update_display_mode(self):
        """Update which controls are visible based on current mode"""
        all_vars = self.fast_vars + self.slow_vars

        for col_key, nam_key in all_vars:
            col_panel = self.field_panels[col_key]
            nam_panel = self.field_panels[nam_key]

            if self.use_names:
                # Show name panels, hide column panels
                col_panel.Hide()
                nam_panel.Show()
            else:
                # Show column panels, hide name panels
                col_panel.Show()
                nam_panel.Hide()

        self.Layout()

    def save_current_state(self):
        """Save current control values as the reference point for revert"""
        self.original_config = {}
        for key, control in self.controls.items():
            if isinstance(control, wx.TextCtrl):
                self.original_config[key] = control.GetValue()

    def revert_to_original(self):
        """Revert all controls to their original state"""
        for key, control in self.controls.items():
            if isinstance(control,
                          wx.TextCtrl) and key in self.original_config:
                control.SetValue(self.original_config[key])

    def load_config(self, config):
        """Load configuration values"""
        for key, control in self.controls.items():
            value = config.pull(key, '0' if key.endswith('_col') else '')
            control.SetValue(str(value))

        # Save this as the original state
        self.save_current_state()
        self.field_edited = False
        self.column_radio.Enable(True)
        self.name_radio.Enable(True)
        self.back_button.Hide()

    def save_config(self, config):
        """Save configuration values, erasing non-visible settings"""
        all_vars = self.fast_vars + self.slow_vars

        for col_key, nam_key in all_vars:
            if self.use_names:
                # Save name values, erase column values
                config.push(nam_key, self.controls[nam_key].GetValue())
                config.push(col_key, "")  # Erase column setting
            else:
                # Save column values, erase name values
                config.push(col_key, self.controls[col_key].GetValue())
                config.push(nam_key, "")  # Erase name setting


class ProcessingPage(ConfigPageBase):
    """Processing settings page"""

    def __init__(self, parent, top):
        super().__init__(parent, top)
        self.init_ui()

    def init_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Basic processing parameters
        basic_sizer = self.add_section(main_sizer, "Basic Parameters")
        self.add_text_field(basic_sizer, "", "Par.FREQ")

        # Corrections and methods
        corrections_sizer = self.add_section(main_sizer, "Corrections and Methods")

        bool_keys = [
            ('Par.DoIterate', True),
            ('Par.DoSonic', True),
            ('Par.DoWebb', True),
            ('Par.DoFreq', True),
            ('Par.DoO2', True),
            ('Par.DoYaw', True),
            ('Par.DoPitch', False),
            ('Par.DoPF', True),
            ('Par.DoDetrend', False),
        ]

        for key, default in bool_keys:
            self.add_bool_field(corrections_sizer, "", key, default)

        # Limits and thresholds
        limits_sizer = self.add_section(main_sizer, "Limits and Thresholds")

        limit_keys = [
            'Par.MaxIter',
            'Par.PitchLim',
            'Par.RollLim',
            'Par.LLimit',
            'Par.ULimit',
            'Par.PFValid',
        ]

        for key in limit_keys:
            self.add_text_field(limits_sizer, "", key)

        self.SetSizer(main_sizer)

    def load_config(self, config):
        for key, control in self.controls.items():
            value = config.pull(key, '')
            if isinstance(control, wx.CheckBox):
                # Convert string to boolean
                bool_val = str(value).lower() in ['true', 't', '1', 'yes',
                                                  'y', '.true.']
                control.SetValue(bool_val)
            elif isinstance(control, wx.TextCtrl):
                control.SetValue(str(value))

    def save_config(self, config):
        for key, control in self.controls.items():
            if isinstance(control, wx.CheckBox):
                config.push(key, 'T' if control.GetValue() else 'F')
            elif isinstance(control, wx.TextCtrl):
                config.push(key, control.GetValue())


class QCPrePage(ConfigPageBase):
    """Quality control preprocessing page"""

    def __init__(self, parent, top):
        super().__init__(parent, top)
        self.init_ui()

    def init_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Instrument flags
        flags_sizer = self.add_section(main_sizer, "Instrument Flags")
        self.add_text_field(flags_sizer, "", "qcconf.csatmask")
        self.add_text_field(flags_sizer, "", "qcconf.irgamask")
        self.add_text_field(flags_sizer, "", "qcconf.agclimit")

        # Spike detection
        spikes_sizer = self.add_section(main_sizer,
                                        "Spike Detection (Vickers & Mahrt)")
        spike_keys = [
            'qcconf.L1',
            'qcconf.spth',
            'qcconf.spin',
            'qcconf.spco',
            'qcconf.spcr',
        ]

        for key in spike_keys:
            self.add_text_field(spikes_sizer, "", key)

        # Absolute limits
        limits_sizer = self.add_section(main_sizer, "Absolute Limits")
        limit_keys = [
            'qcconf.limu',
            'qcconf.limw',
            'qcconf.limtl',
            'qcconf.limth',
            'qcconf.limql',
            'qcconf.limqh',
            'qcconf.limcl',
            'qcconf.limch',
        ]

        for key in limit_keys:
            self.add_text_field(limits_sizer, "", key)

        # Higher moments
        moments_sizer = self.add_section(main_sizer, "Higher Moments")
        moment_keys = [
            'qcconf.maxskew_1',
            'qcconf.maxskew_2',
            'qcconf.minkurt_1',
            'qcconf.maxkurt_1',
            'qcconf.minkurt_2',
            'qcconf.maxkurt_2',
        ]

        for key in moment_keys:
            self.add_text_field(moments_sizer, "", key)

        # MAD spikes
        mad_sizer = self.add_section(main_sizer, "MAD Spike Detection")
        self.add_text_field(mad_sizer, "", "qcconf.madth")
        self.add_text_field(mad_sizer, "", "qcconf.madcr")

        # Change rate spikes
        change_sizer = self.add_section(main_sizer, "Change Rate Limits")
        change_keys = [
            'qcconf.chr_u',
            'qcconf.chr_w',
            'qcconf.chr_t',
            'qcconf.chrh2o',
            'qcconf.chrco2',
            'qcconf.chrcr',
        ]

        for key in change_keys:
            self.add_text_field(change_sizer, "", key)

        self.SetSizer(main_sizer)

    def load_config(self, config):
        for key, control in self.controls.items():
            value = config.pull(key, '')
            control.SetValue(str(value))

    def save_config(self, config):
        for key, control in self.controls.items():
            config.push(key, control.GetValue())


class QCPostPage(ConfigPageBase):
    """Quality control postprocessing page"""

    def __init__(self, parent, top):
        super().__init__(parent, top)
        self.init_ui()

    def init_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Mean vertical wind
        wind_sizer = self.add_section(main_sizer, "Mean Vertical Wind")
        self.add_text_field(wind_sizer, "", "qcconf.wlimit1")
        self.add_text_field(wind_sizer, "", "qcconf.wlimit2")

        # Integrated turbulence characteristics
        itc_sizer = self.add_section(main_sizer,
                                     "Integrated Turbulence Characteristics")
        itc_keys = [
            'qcconf.itclim1',
            'qcconf.itclim2',
            'qcconf.itchmin',
        ]

        for key in itc_keys:
            self.add_text_field(itc_sizer, "", key)

        # Footprint model
        footprint_sizer = self.add_section(main_sizer, "Footprint Model")
        self.add_text_field(footprint_sizer, "", "qcconf.minfoot")

        # Excessive error
        error_sizer = self.add_section(main_sizer,
                                       "Excessive Error Limits")
        error_keys = [
            'qcconf.Herrmin',
            'qcconf.Herrfac',
            'qcconf.Eerrmin',
            'qcconf.Eerrfac',
            'qcconf.Cerrmin',
            'qcconf.Cerrfac',
            'qcconf.terrmin',
            'qcconf.terrfac',
        ]

        for key in error_keys:
            self.add_text_field(error_sizer, "", key)

        # Stationarity tests
        stat_sizer = self.add_section(main_sizer, "Stationarity Tests")
        stat_keys = [
            'qcconf.fwsub',
            'qcconf.fwlim1',
            'qcconf.fwlim2',
            'qcconf.cotlimit',
            'qcconf.vstlim',
        ]

        for key in stat_keys:
            self.add_text_field(stat_sizer, "", key)

        # Turbulent fraction
        turb_sizer = self.add_section(main_sizer, "Turbulent Fraction")
        turb_keys = [
            'qcconf.Lf',
            'qcconf.ftmin1',
            'qcconf.ftmin2',
        ]

        for key in turb_keys:
            self.add_text_field(turb_sizer, "", key)

        # Surviving values
        surv_sizer = self.add_section(main_sizer, "Data Survival")
        surv_keys = [
            'qcconf.msurv1',
            'qcconf.msurv2',
        ]

        for key in surv_keys:
            self.add_text_field(surv_sizer, "", key)

        self.SetSizer(main_sizer)

    def load_config(self, config):
        for key, control in self.controls.items():
            value = config.pull(key, '')
            control.SetValue(str(value))

    def save_config(self, config):
        for key, control in self.controls.items():
            config.push(key, control.GetValue())


# Integration function to add the dialog to the existing ecmain.py

def show_configuration_dialog(parent, config=None):
    """
    Show the configuration dialog and return the modified configuration

    Args:
        parent: Parent window
        config: Current configuration dictionary

    Returns:
        tuple: (modified_config, was_modified)
    """
    dialog = ConfigurationDialog(parent, config)

    try:
        if dialog.ShowModal() == wx.ID_OK:
            return dialog.config, dialog.modified
        else:
            return config, False
    finally:
        dialog.Destroy()


# Integration functions for adding to existing ecmain.py

def add_config_dialog_to_main_window():
    """
    Integration code to add configuration dialog to existing Run_Window class.
    This should be added to the Run_Window class in ecmain.py
    """

    def OnConfigureAdvanced(self, event):
        """Open advanced configuration dialog"""
        self.statusbar.PushStatusText('OnConfigureAdvanced')

        if self.project is None:
            wx.MessageBox(
                "No project loaded. Please create or open a project first.",
                "No Project", wx.OK | wx.ICON_WARNING)
            return

        # Convert project config to dictionary format expected by dialog
        configuration = deepcopy(self.project.conf)

        # Show configuration dialog
        new_config, was_modified = show_configuration_dialog(self,
                                                             configuration)

        if was_modified:
            # Update project configuration
            self.project.conf = deepcopy(new_config)

            self.project.changed = True
            self.project.store()
            self.Update()

            wx.MessageBox("Configuration updated successfully.",
                          "Configuration Saved",
                          wx.OK | wx.ICON_INFORMATION)

        self.statusbar.PopStatusText()

    # Return the method to be added to the class
    return OnConfigureAdvanced


def integrate_config_dialog(run_window_class):
    """
    Add the advanced configuration dialog to the Run_Window class

    Usage:
    In ecmain.py, after the Run_Window class definition:
    integrate_config_dialog(Run_Window)
    """

    # Add the method to the class
    run_window_class.OnConfigureAdvanced = add_config_dialog_to_main_window()

    # Modify the __init__ method to add the menu item
    original_init = run_window_class.__init__

    def enhanced_init(self, *args, **kwargs):
        # Call original __init__
        original_init(self, *args, **kwargs)

        # Add advanced configuration menu item
        self.m_advanced = self.m_conf.Append(
            wx.ID_ANY, "&Advanced...", "Advanced configuration dialog.")
        self.Bind(wx.EVT_MENU, self.OnConfigureAdvanced, self.m_advanced)

        # Enable/disable based on project state
        self.m_advanced.Enable(self.project is not None)

    # Modify the Update method to enable/disable the menu item
    original_update = run_window_class.Update

    def enhanced_update(self):
        # Call original Update
        original_update(self)

        # Update menu item state
        if hasattr(self, 'm_advanced'):
            self.m_advanced.Enable(self.project is not None)

    # Replace methods
    run_window_class.__init__ = enhanced_init
    run_window_class.Update = enhanced_update


# Validation helper functions

def validate_numeric_range(value, min_val=None, max_val=None,
                           param_name="Parameter"):
    """Validate that a value is numeric and within range"""
    try:
        num_val = float(value)
        if min_val is not None and num_val < min_val:
            return f"{param_name} must be >= {min_val}"
        if max_val is not None and num_val > max_val:
            return f"{param_name} must be <= {max_val}"
        return None
    except (ValueError, TypeError):
        return f"{param_name} must be a valid number"


def validate_path_exists(path, param_name="Path"):
    """Validate that a path exists"""
    if path and not os.path.exists(path):
        return f"{param_name} does not exist: {path}"
    return None


def validate_date_format(date_str, param_name="Date"):
    """Validate date format YYYY/MM/DD-HH:MM:SS"""
    if not date_str:
        return None  # Empty is allowed

    pattern = r'^\d{4}/\d{2}/\d{2}-\d{2}:\d{2}:\d{2}$'
    if not re.match(pattern, date_str):
        return f"{param_name} must be in format YYYY/MM/DD-HH:MM:SS"

    # Additional validation could check if date is valid
    try:
        from datetime import datetime
        # Try to parse the date to ensure it's valid
        datetime.strptime(date_str, '%Y/%m/%d-%H:%M:%S')
        return None
    except ValueError:
        return f"{param_name} contains invalid date/time values"


def validate_coordinate(coord_str, coord_type="Coordinate"):
    """Validate coordinate values"""
    try:
        coord = float(coord_str)
        if coord_type.lower() == "latitude" and (
                coord < -90 or coord > 90):
            return "Latitude must be between -90 and 90 degrees"
        elif coord_type.lower() == "longitude" and (
                coord < -180 or coord > 180):
            return "Longitude must be between -180 and 180 degrees"
        return None
    except (ValueError, TypeError):
        return f"{coord_type} must be a valid number"
