#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ##############################################################
#  program ecpet
#
#  a wrapper to run eddy-covariance processing by ec-pack/ec-frame
#
#  (C) 2017 Clemens Druee, Umweltmeteorologie, Universitaet Trier
#
# ##############################################################

import logging
from . import eclogger

# improved logging # ------------------------------------------------------
eclogger.setup_custom_logging()

logging.basicConfig(
    level=logging.NORMAL,
    format="%(levelname)7s: %(module)8s: %(message)s",
#    datefmt="%Y-%m-%d %H:%M:%S"
)

import argparse
import os
import sys
from time import sleep


from numpy.version import version as ver_np
from pandas import __version__ as ver_pd
from scipy import __version__ as ver_scipy
try:
    from matplotlib import __version__ as ver_mpl
except ImportError:
    ver_mpl = None
try:
    from wv import __version__ as ver_wx
except ImportError:
    ver_wx = None

#
# import modules using improved logging # ---------------------------------
#
from ._version import __release__ as version
from ._version import __copyright__ as copyright_string
from . import ecconfig
from . import ecdb
from . import ecengine
from . import ecutils as ec

#
#  optional : GUI framework
#
try:
    import wx
    import wx.lib.mixins.listctrl as listmix
    import wx.lib.scrolledpanel as scrolled
    from .ec_config_wizard import integrate_config_wizard
    from .ec_config_dialog import integrate_config_dialog
    have_wx = True

except ImportError:
    have_wx = False
    wx = listmix = scrolled = None

#
#  optional : inter-thread communication
#
try:
    from pubsub import pub
    from pubsub import __version__ as ver_pub
    from threading import Thread, Event
    have_com = True

except ImportError:
    pub = ver_pub = Thread = Event = None
    have_com = False

#
# setup logger
#
logger = logging.getLogger(__name__)
# suppress annoying findfont debug messages
# https://stackoverflow.com/a/58393562
logging.getLogger('matplotlib.font_manager').setLevel(logging.WARNING)

#
# stages descriptions
#
r_labels = {'start': 'start over  ',
            'pre':  'preprocessor',
            'plan': 'planar fit  ',
            'flux': 'flux calc.  ',
            'post': 'postprocesor',
            'out':  'write output'}
gui_image = None
defaultconf = ecconfig.Config()

# ----------------------------------------------------------------
#
# graphical interface  using wxpython
#
if have_wx:
    #
    # ----------------------------------------------------------------

    class Project(object):
        def __init__(self, name=None):
            self.conf = ecconfig.Config()
            self.stage = None
            self.changed = bool()
            self.file = None
            if name is not None:
                self.load(name)

        def load(self, name):
            ecdb.dbfile = name
            self.conf = ecdb.conf_from_db()
            logger.insane('loaded config: %s' % str(self.conf._values))
            self.changed = False
            tables = ecdb.list_tables()
            logger.insane(tables)
            if 'out:files' in tables:
                self.stage = 'out'
            elif 'post:intervals' in tables:
                self.stage = 'post'
            elif 'flux:intervals' in tables:
                self.stage = 'flux'
            elif 'plan:intervals' in tables:
                self.stage = 'plan'
            elif 'pre:intervals' in tables:
                self.stage = 'pre'
            else:
                self.stage = 'start'
            logger.insane(self.stage)
            self.file = os.path.abspath(name)

        def store(self):
            ecdb.conf_to_db(self.conf.to_dict())
            self.changed = False

    class ProgressBox(wx.Dialog):

        def __init__(self):
            wx.Dialog.__init__(self, None, title="Progress")

            self._closing = False  # Flag to prevent multiple close attempts

            self.info = wx.StaticText(self, wx.ID_ANY,
                                      label="Running stage:        ",
                                      style=wx.ALIGN_CENTRE_HORIZONTAL | wx.ST_NO_AUTORESIZE)
            self.stage = wx.Gauge(self, range=len(ec.stages))
            self.number = wx.StaticText(self, wx.ID_ANY,
                                        label="completed:       ",
                                        style=wx.ALIGN_CENTRE_HORIZONTAL | wx.ST_NO_AUTORESIZE)
            self.progress = wx.Gauge(self, range=100)
            self.percent = 0.
            self.progress.SetValue(int(self.percent))

            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.AddStretchSpacer()
            sizer.Add(self.info, 0, wx.EXPAND)
            sizer.AddSpacer(10)
            sizer.Add(self.stage, 0, wx.EXPAND)
            sizer.AddSpacer(20)
            sizer.Add(self.number, 0, wx.EXPAND)
            sizer.AddSpacer(10)
            sizer.Add(self.progress, 0, wx.EXPAND)
            sizer.AddSpacer(10)
            self.SetSizer(sizer)
            sizer.Layout()

            # Bind close event
            self.Bind(wx.EVT_CLOSE, self.OnClose)

            # create a pubsub receiver
            pub.subscribe(self.noProgress,  "pulse")
            pub.subscribe(self.setProgress, "progress")
            pub.subscribe(self.incProgress, "increment")
            pub.subscribe(self.setStage,    "stage")
            pub.subscribe(self.Done,        "done")

        def OnClose(self, event):
            """Handle close event safely"""
            if not self._closing:
                self._closing = True
                self.unsubscribe_all()
                event.Skip()  # Allow default close handling

        def unsubscribe_all(self):
            """Safely unsubscribe from all pubsub messages"""
            try:
                pub.unsubscribe(self.noProgress, "pulse")
                pub.unsubscribe(self.setProgress, "progress")
                pub.unsubscribe(self.incProgress, "increment")
                pub.unsubscribe(self.setStage, "stage")
                pub.unsubscribe(self.Done, "done")
            except Exception as e:
                logger.debug(f"Error unsubscribing from pubsub: {e}")

        def noProgress(self):
            if self._closing:
                return
            logger.insane('ProgressBox.Pulse')
            wx.CallAfter(self._safe_pulse)

        def _safe_pulse(self):
            if not self._closing and not self.IsBeingDeleted():
                self.progress.Pulse()
                wx.YieldIfNeeded()

        def setProgress(self, msg):
            if self._closing:
                return
            logger.insane('ProgressBox.SetProgress')
            try:
                percent = float(msg)
            except:
                percent = 0.
            wx.CallAfter(self._safe_set_progress, percent)

        def _safe_set_progress(self, percent):
            if self._closing or self.IsBeingDeleted():
                return

            if percent > 100.:
                percent = 100.
            if percent < 0.:
                percent = 0.

            self.percent = percent
            self.number.SetLabel(
                "completed: {:5.1f}%".format(self.percent))
            self.progress.SetValue(int(self.percent))
            wx.YieldIfNeeded()

        def incProgress(self, msg):
            if self._closing:
                return
            logger.insane('ProgressBox.incProgress')
            try:
                inc = float(msg)
            except:
                inc = 0
            wx.CallAfter(self._safe_inc_progress, inc)

        def _safe_inc_progress(self, inc):
            if self._closing or self.IsBeingDeleted():
                return

            self.percent += inc
            logger.insane(str(self))
            logger.debug(
                'percent: {:5.2f}% ( + {:.2f}% )'.format(self.percent, inc))
            if self.percent > 100.:
                self.percent = 100.
            if self.percent < 0.:
                self.percent = 0.
            self.number.SetLabel("completed: {:5.1f}%".format(self.percent))
            self.progress.SetValue(int(self.percent))
            wx.YieldIfNeeded()

        def setStage(self, msg):
            if self._closing:
                return
            logger.insane('ProgressBox.SetStage')
            wx.CallAfter(self._safe_set_stage, msg)

        def _safe_set_stage(self, msg):
            if self._closing or self.IsBeingDeleted():
                return

            if msg in ec.stages:
                sn = r_labels[msg]
                st = ec.stages.index(msg)
                per = 0.
            elif msg in range(len(ec.stages)):
                sn = r_labels[ec.stages[msg]]
                st = msg
                per = 0.
            else:
                sn = ''
                st = 0
                per = 0.
            self.info.SetLabel("Running stage: {:s}".format(sn))
            self.stage.SetValue(st)
            self.percent = per
            self.number.SetLabel("completed: {:5.1f}%".format(self.percent))
            self.progress.SetValue(int(self.percent))
            wx.YieldIfNeeded()

        def Done(self):
            if self._closing:
                return
            logger.insane('ProgressBox.Done')
            # Use CallAfter to safely close from main thread
            wx.CallAfter(self._safe_done)

        def _safe_done(self):
            if not self._closing and not self.IsBeingDeleted():
                self._closing = True
                self.unsubscribe_all()
                try:
                    self.EndModal(wx.ID_OK)  # Close modal dialog properly
                except Exception as e:
                    logger.debug(f"Error ending modal: {e}")
                    # Fallback to destroy if EndModal fails
                    try:
                        self.Destroy()
                    except Exception as e2:
                        logger.debug(f"Error destroying dialog: {e2}")
# ----------------------------------------------------------------------


    class EditableListCtrl(wx.ListCtrl, listmix.TextEditMixin, listmix.ColumnSorterMixin):
        '''
        TextEditMixin allows any column to be edited.
        '''

        def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,
                     size=wx.DefaultSize, style=0):
            """Constructor"""

            wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
            listmix.TextEditMixin.__init__(self)
            self.curCol = None
            self.curRow = None
            self.Bind(wx.EVT_SCROLLWIN, self.OnScroll)

        def OpenEditor(self, col, row):
            """allow only editing of column #2 (Values)"""
            logger.insane('CLICK column {:d}, row {:d}'.format(col, row))
            if col != 3:
                logger.insane(
                    'column {:d}, row {:d} not editable'.format(col, row))
                return

            # original code follows here

            # give the derived class a chance to Allow/Veto this edit.
            evt = wx.ListEvent(
                wx.wxEVT_COMMAND_LIST_BEGIN_LABEL_EDIT, self.GetId())
            evt.Index = row
            evt.Column = col
            item = self.GetItem(row, col)
            evt.Item.SetId(item.GetId())
            evt.Item.SetColumn(item.GetColumn())
            evt.Item.SetData(item.GetData())
            evt.Item.SetText(item.GetText())
            ret = self.GetEventHandler().ProcessEvent(evt)
            if ret and not evt.IsAllowed():
                return   # user code doesn't allow the edit.

            if self.GetColumn(col).Align != self.col_style:
                self.make_editor(self.GetColumn(col).Align)

            editor = self.editor
            # original code  causes GTK warning and no editor is shown
            # this is the hack:
            rect = wx.Rect()
            self.GetSubItemRect(row, col, rect)
            editor.SetSize(rect)
            # end hack

            editor.SetValue(self.GetItem(row, col).GetText())
            editor.Show()
            editor.Raise()
            editor.SetSelection(-1, -1)
            editor.SetFocus()

            self.curRow = row
            self.curCol = col

        def OnScroll(self, event):
            ''' lock scrolling during editing. '''
            if hasattr(self, 'editor') and self.editor.Shown is True:
                pass
            else:
                event.Skip()


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------


    class Run_Window(wx.Frame):
        ''' EC-PeT main mindow. '''
        #
        #

        def __init__(self, parent, id=-1, title=wx.EmptyString,
                     pos=wx.DefaultPosition, size=(640, 480),
                     style=wx.DEFAULT_FRAME_STYLE, name=wx.FrameNameStr,
                     opts=None):
            wx.Frame.__init__(self, None, id, title, pos, size, style, name)
            # - - - - - - - - - - -
            # define window elements
            #
            # Menu bar
            #
            if opts is None:
                opts = {}
            self.menuBar = wx.MenuBar()
            self.m_file = wx.Menu()
            self.m_new = self.m_file.Append(
                wx.ID_ANY, "&New Project", "Create new project.")
            self.Bind(wx.EVT_MENU, self.OnNew, self.m_new)
            self.m_open = self.m_file.Append(
                wx.ID_ANY, "&Open Project", "Open existing project.")
            self.Bind(wx.EVT_MENU, self.OnOpen, self.m_open)
            self.m_close = self.m_file.Append(
                wx.ID_ANY, "&Close Project", "Close current project.")
            self.Bind(wx.EVT_MENU, self.OnClose, self.m_close)
            self.m_exit = self.m_file.Append(
                wx.ID_ANY, "E&xit\tAlt-X", "Close window and exit program.")
            self.Bind(wx.EVT_MENU, self.OnExit, self.m_exit)
            self.menuBar.Append(self.m_file, "&File")
            self.m_conf = wx.Menu()
            self.m_import = self.m_conf.Append(
                wx.ID_ANY, "&Import", "Import a configuration file.")
            self.Bind(wx.EVT_MENU, self.OnImport, self.m_import)
            self.m_export_mini = self.m_conf.Append(
                wx.ID_ANY, "&Export minimal", "Export minimal configuration to file.")
            self.Bind(wx.EVT_MENU, self.OnExportMini, self.m_export_mini)
            self.m_export_full = self.m_conf.Append(
                wx.ID_ANY, "&Export full", "Export full configuration to file.")
            self.Bind(wx.EVT_MENU, self.OnExportFull, self.m_export_full)
            self.menuBar.Append(self.m_conf, "&Config")
            self.m_about = wx.Menu()
            self.m_status = self.m_about.Append(
                wx.ID_ANY, "&Status", "Program status and environment.")
            self.Bind(wx.EVT_MENU, self.OnStatus, self.m_status)
            self.menuBar.Append(self.m_about, "&About")
            self.SetMenuBar(self.menuBar)
            #
            # status bar
            #
            self.statusbar = self.CreateStatusBar(2)
            #
            # main content
            #
            sizer = wx.BoxSizer(wx.HORIZONTAL)
            box = wx.BoxSizer(wx.VERTICAL)

            logo = wx.Bitmap(os.path.join(imagepath, 'gui-image_text.png'),
                             wx.BITMAP_TYPE_PNG)
            self.pic = wx.StaticBitmap(self, wx.ID_ANY, logo)

            sizer.Add(self.pic, 0, wx.ALL, 5)

            self.conlist = EditableListCtrl(self, wx.ID_ANY,
                                            style=wx.LC_REPORT,
                                            size=(640, 400))
            self.conlist.InsertColumn(0, 'Group')
            self.conlist.InsertColumn(1, 'Token')
            self.conlist.InsertColumn(2, '*')
            self.conlist.InsertColumn(3, 'Value')
            self.conlist.SetColumnWidth(0, 80)
            self.conlist.SetColumnWidth(1, 80)
            self.conlist.SetColumnWidth(2, 15)
            self.conlist.SetColumnWidth(3, 465)
            self.conlist.Bind(wx.EVT_LIST_END_LABEL_EDIT, self.OnEndEdit)
            self.conlist.Bind(wx.EVT_LIST_COL_CLICK, self.OnColClick)

            box.Add(self.conlist, 0, wx.EXPAND | wx.ALL, 5)

            self.progress = wx.Gauge(self, wx.ID_ANY,
                                     size=(640, 20),
                                     style=wx.GA_HORIZONTAL,
                                     range=100)
            box.Add(self.progress, 0, wx.EXPAND | wx.ALL, 5)

            szr_buttons = wx.BoxSizer(wx.HORIZONTAL)

            self.radio = wx.RadioBox(self, wx.ID_ANY, choices=[
                                     r_labels[x] for x in ec.stages])
            szr_buttons.Add(self.radio, flag=wx.ALIGN_CENTRE_VERTICAL)

            szr_buttons.AddStretchSpacer()
            self.btn_start = wx.Button(self, wx.ID_ANY, label="START")
            self.Bind(wx.EVT_BUTTON, self.OnRun, self.btn_start)
            szr_buttons.Add(self.btn_start, flag=wx.ALIGN_CENTRE_VERTICAL)

            box.Add(szr_buttons, 0, wx.EXPAND | wx.ALL, 5)

            sizer.Add(box, 0, wx.ALL, 5)
            self.SetAutoLayout(True)
            self.SetSizer(sizer)
            self.Fit()

            self.Layout()

            # startup
            self.options = opts
            if 'project' in self.options and self.options['project'] is not None:
                self.project = Project(self.options['project'])
            else:
                self.project = None

            self.sortby = [2, 1]

            self.Update()

        # ---------------
        # object methods
        #
        def Update(self):
            logger.debug('current dir: {:s}'.format(os.getcwd()))
            if self.project is None:
                #
                # disable controls
                self.m_close.Enabled = False
                self.m_import.Enabled = False
                self.m_export_mini.Enabled = False
                self.m_export_full.Enabled = False
                #
                # empty status bar
                self.statusbar.SetStatusText('no project', 1)
                #
                # empty process completeness
                self.progress.SetValue(0)
                #
                # empty config display
                self.conlist.DeleteAllItems()
                self.sortby = [2, 1]
                #
                # disable start options
                for i in range(len(ec.stages)):
                    self.radio.EnableItem(i, False)
                self.radio.Enabled = False
                self.btn_start.Enabled = False
            else:
                #
                # enable controls
                self.m_close.Enabled = True
                self.m_import.Enabled = True
                self.m_export_mini.Enabled = True
                self.m_export_full.Enabled = True
                #
                # show name in status bar
                self.statusbar.SetStatusText(
                    os.path.basename(self.project.file), 1)
                #
                # display config
                self.DisplayConfig()
                #
                # show process completeness
                perc = int(self.progress.GetRange()*(float(ec.stages.index(self.project.stage))
                                                     / float(len(ec.stages)-1)))
                logger.insane('percentage: {:d} ({:d}/{:d})'.format(
                    perc, ec.stages.index(self.project.stage), len(ec.stages)-1))
                self.progress.SetValue(perc)
                #
                # enable start options
                self.radio.Enabled = True
                for i in range(len(ec.stages)):
                    if ec.stages.index(self.project.stage) >= i-1:
                        self.radio.EnableItem(i, True)
                    else:
                        self.radio.EnableItem(i, False)
                self.btn_start.Enabled = True
            wx.YieldIfNeeded()

        def ImSure(self):
            if self.project is not None and self.project.changed:
                if wx.MessageBox("Current content has not been saved! Proceed?", "Please confirm",
                                 wx.ICON_QUESTION | wx.YES_NO, self) == wx.NO:
                    return False
                else:
                    return True
            else:
                return True

        def DisplayConfig(self):
            row = 0
            sortarray = []
            for k in self.project.conf.tokens:
                v = self.project.conf.pull(k, kind='raw').strip()
                if '.' in k:
                    group, token = k.split('.', 1)  # get characters before '.'
                else:
                    group = ''              # sort blank at one end
                    token = k
                if self.project.conf.is_default(k):
                    isdefault = 1
                else:
                    isdefault = 0
                sortarray.append((group, token, isdefault, v))
            for by in self.sortby:
                # by is 1-based, negative means reversed sort
                sortarray = sorted(
                    sortarray, key=lambda x: x[abs(by)-1], reverse=(by < 0))
            # (re) fill listctrl
            self.conlist.DeleteAllItems()
            for k in sortarray:
                g, t, d, v = k
                if d == 1:
                    self.conlist.Append((g, t, '', v))
                    self.conlist.SetItemTextColour(
                        row, wx.TheColourDatabase.Find('GREY'))
                else:
                    self.conlist.Append((g, t, '*', v))
                    self.conlist.SetItemTextColour(
                        row, wx.TheColourDatabase.Find('BLACK'))
                row += 1

        def OnColClick(self, event):
            # Get the column clicked (values in array are 1-based to have a meaningful sign)
            col = event.GetColumn() + 1
            # reverse sort order if column is clicked again
            if abs(col) == abs(self.sortby[-1]):
                self.sortby[-1] = -self.sortby[-1]
            else:
                self.sortby.append(col)
            # limit length of array
            if len(self.sortby) > 4:
                self.sortby = self.sortby[-4:]
            self.Update()

        def OnEndEdit(self, event):
            row_id = event.GetIndex()  # Get the current row
#      col_id = event.GetColumn () #Get the current column
            new_data = event.GetLabel()  # Get the changed data

            # construct key of changed value
            g = self.conlist.GetItem(row_id, 0).GetText()
            t = self.conlist.GetItem(row_id, 1).GetText()
            if g != '':
                key = '.'.join((g, t))
            else:
                key = t
            old_data = self.project.conf.pull(key)
            self.project.conf.push(key, new_data)
            logger.debug('config value "%s" changed from "%s" to "%s"' % (
                key, old_data, new_data))
            self.project.store()
            self.Update()

        def OnExit(self, event):
            if self.ImSure():
                self.Destroy()

        def OnStatus(self, event):
            self.statusbar.PushStatusText('Status')
            ver = {}
            ver['python'] = sys.version.split()[0]
            ver['numpy'] = ver_np
            ver['pandas'] = ver_pd
            ver['scipy'] = ver_scipy
            ver['wxPython'] = wx.__version__
            ver['pubsub'] = ver_pub if ver_pub else 'not available'
            ver['matplotlib'] = ver_mpl if ver_mpl else 'not available'

            message = ('EC-PeT -- ' +
                       'elaboratio concursuum perturbationum Treverensis *)\n' +
                       'Release: ' + version +'\n' +
                       copyright_string + '\n' +
                       '\n' +
                       'Versions:\n'
                       )
            for k, v in ver.items():
                message += f'{k}: {v}\n'
            msg = wx.MessageDialog(self,
                                   message,
                                   style=wx.OK | wx.ICON_INFORMATION | wx.CENTRE
                                   )
            msg.ShowModal()
            self.statusbar.PopStatusText()

        def OnNew(self, event):
            self.statusbar.PushStatusText('OnNew')
            if self.ImSure():
                # ask the user what new file to open
                wildcard = 'EC-PeT project (.ecp)|*.ecp|SQLite3 files (.sqlite)|*.sqlite'
                with wx.FileDialog(self, "Open project file",
                                   wildcard=wildcard,
                                   style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

                    if fileDialog.ShowModal() == wx.ID_CANCEL:
                        return     # the user changed their mind

                    # file chosen by the user
                    pathname = fileDialog.GetPath()

                    # every second element from wildcard string is an extension
                    ext = wildcard.replace('*', '').split('|')[1::2]
                    # get the extension chosen by user
                    iext = fileDialog.GetFilterIndex()
                    # make sure pathname ends with a proper extension:
                    if not pathname.endswith(ext[iext]):
                        pathname = pathname+ext[iext]

                os.chdir(os.path.dirname(pathname))
                self.project = Project()
                ecdb.dbfile = pathname
                self.project.file = pathname
                self.project.conf = ecconfig.Config()
                logger.insane(
                    'new project filename: {:s}'.format(self.project.file))
                self.project.changed = False
                self.project.stage = 'start'
                self.Update()
            self.statusbar.PopStatusText()

        def OnOpen(self, event):
            self.statusbar.PushStatusText('OnOpen')
            if self.ImSure():
                # ask the user what new file to open
                wildcard = 'EC-PeT project (.ecp)|*.ecp|SQLite3 files (.sqlite)|*.sqlite|All files|*'
                with wx.FileDialog(self, "Open project file", wildcard=wildcard,
                                   style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

                    if fileDialog.ShowModal() == wx.ID_CANCEL:
                        return     # the user changed their mind

                    # if project is loaded, unload it first
                    self.project = None
                    self.Update()

                    # Proceed loading the file chosen by the user
                    pathname = fileDialog.GetPath()
                    try:
                        self.project = Project(pathname)
                    except IOError:
                        wx.LogError("Cannot open file '%s'." % pathname)
                    else:
                        os.chdir(os.path.dirname(pathname))
                        self.Update()
            self.statusbar.PopStatusText()

        def OnClose(self, event):
            self.statusbar.PushStatusText('OnClose')
            if self.ImSure():
                if self.project is not None:
                    self.project = None
                self.Update()
            self.statusbar.PopStatusText()

        def OnImport(self, event):
            self.statusbar.PushStatusText('OnImport')
            if self.ImSure():
                # ask the user what new file to open
                with wx.FileDialog(self, "Open config file", wildcard="config files (*.conf)|*.conf|All files|*",
                                   style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

                    if fileDialog.ShowModal() == wx.ID_CANCEL:
                        return     # the user changed their mind

                    # Proceed loading the file chosen by the user
                    pathname = fileDialog.GetPath()
                    try:
                        arglist = ecconfig.read_file(pathname)
                    except IOError:
                        wx.LogError("Cannot open file '%s'." % pathname)
                    else:
                        self.project.conf = ecconfig.complete(arglist)
                        self.project.store()
                self.Update()
            self.statusbar.PopStatusText()

        def Export(self, event, full):
            # ask the user what new file to open
            with wx.FileDialog(self, "Save config file", wildcard="config files (*.conf)|*.conf",
                               style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

                if fileDialog.ShowModal() == wx.ID_CANCEL:
                    return     # the user changed their mind

                # Proceed loading the file chosen by the user
                pathname = fileDialog.GetPath()
                if not pathname.endswith('.conf'):
                    pathname = pathname + '.conf'
                reduced = self.project.conf.to_dict(reduced=not full)
                try:
                    ecconfig.write_file(pathname, reduced)
                except IOError:
                    wx.LogError("Cannot write file '%s'." % pathname)
            self.Update()

        def OnExportMini(self, event):
            self.statusbar.PushStatusText('OnExportMini')
            self.Export(event, full=False)
            self.statusbar.PopStatusText()

        def OnExportFull(self, event):
            self.statusbar.PushStatusText('OnExportFull')
            self.Export(event, full=True)
            self.statusbar.PopStatusText()

        def OnRun(self, event):
            startat = self.radio.GetSelection()
            logger.debug('running stage'+ec.stages[startat])
            with wx.MessageDialog(self, '(Re)Starting processing at stage: ' +
                                  ' {:s} '.format(
                                      r_labels[ec.stages[startat]]),
                                  style=wx.ICON_QUESTION | wx.OK | wx.CANCEL) as dlg:
                yesno = dlg.ShowModal() == wx.ID_OK

            wx.YieldIfNeeded()

            if yesno:
                if have_com:
                    # Create progress dialog
                    progress_dlg = ProgressBox()

                    # Create and start worker thread
                    thread = Thread(target=ecengine.process, kwargs=dict(
                        conf=self.project.conf, startat=startat))
                    thread.daemon = True  # Make sure thread dies when main program exits
                    thread.start()

                    try:
                        # Show modal dialog - this blocks until dialog is closed
                        progress_dlg.ShowModal()
                    except Exception as e:
                        logger.error(f"Error during progress dialog: {e}")
                    finally:
                        # Ensure dialog is properly destroyed
                        if progress_dlg and not progress_dlg.IsBeingDeleted():
                            try:
                                progress_dlg.Destroy()
                            except Exception as e:
                                logger.debug(
                                    f"Error destroying progress dialog: {e}")

                        # Wait for thread to complete
                        if thread.is_alive():
                            logger.debug(
                                "Waiting for processing thread to complete...")
                            thread.join(timeout=5.0)  # Wait max 5 seconds
                            if thread.is_alive():
                                logger.warning(
                                    "Processing thread did not complete in time")

                    wx.YieldIfNeeded()
                else:
                    # No GUI progress - run directly
                    ecengine.process(self.project.conf, startat)

            self.Update()
    integrate_config_wizard(Run_Window)

    integrate_config_dialog(Run_Window)


# end "if have_wx" -------------------------------------------

# ----------------------------------------------------------------
#


def graphical_interface(options):

    global imagepath
    imagepath = ecconfig.find_imagepath()
    global gui_image
    gui_image = os.path.join(imagepath, 'gui-image_text.png')

    app = wx.App(False)
    top = Run_Window(None, title='EC-PeT - Main window', opts=options)
    top.Show()
    app.MainLoop()
    app.Destroy()
    return

# ----------------------------------------------------------------
#
# switch user interface
#


def commandline_interface():

    #  all_values=['AvgInterval','ConfName','DateBegin','DateEnd',
    #            'RawDir','RawFastData','RawSlowData',
    #            'OutDir','PlfitInterval']
    options = {'command': None,
               'project': None,
               'config': None
               }

    # read command line
    parser = argparse.ArgumentParser(
        description=f'EC-PeT -- elaboratio concursuum perturbationum '
                    f'Treverensis *)\n'
                    f'Release: {version}\n' + copyright_string,
        epilog='*)= eddy-covariance software from Trier',
        formatter_class=argparse.RawTextHelpFormatter)
    subparsers = parser.add_subparsers(dest='run_command')
    parser_g = subparsers.add_parser(
        'gui',
        help='start graphic user interface (GUI)')
    parser_r = subparsers.add_parser(
        'run',
        help='use existing configuration, create new project and run it')
    parser_u = subparsers.add_parser(
        'update',
        help='use existing configuration, alter it according to the '
             'command-line options, create new project and run it')
    parser_m = subparsers.add_parser(
        'make',
        help='generate a new default configuration file '
             '(including the command-line options)')

    for i in [parser_r]:
        i.add_argument('-r', '--restart',
                       dest='stage', metavar='STAGE',
                       choices=ec.stages, nargs=1, default='start',
                       help='restart at processing stage ["start"]')
        what_r = i.add_mutually_exclusive_group()

    for i in [parser_u, parser_m, what_r]:
        i.add_argument('-c', '--config',
                       dest='config', nargs=1,
                       help='name of the configuration file ' +
                       '[%s]' % defaultconf.pull('ConfName'),
                       metavar='FILE')

    for i in [parser_g, parser_u, what_r]:
        i.add_argument('-p', '--project', nargs=1,
                       default=None,
                       help='name of the project (file) ',
                       metavar='PROJECT')

    for i in [parser_u, parser_m]:
        i.add_argument('-a', '--AvgInterval',
                       dest='avgstring', nargs=1,
                       help='duration for the averaging interval in '
                            'seconds [%s]' % defaultconf.pull(
                           'AvgInterval'),
                       metavar='SECONDS')
        i.add_argument('-b', '--DateBegin',
                       dest='DateBegin', nargs=1,
                       help='start time of fist averaging interval',
                       metavar='TIMESTAMNP')
        i.add_argument('-e', '--DateEnd',
                       dest='DateEnd', nargs=1,
                       help='end time of fist averaging interval',
                       metavar='TIMESTAMNP')
        i.add_argument('-d', '--RawDir',
                       dest='RawDir', nargs=1,
                       help='directory containing the data to process. ' +
                            'all names specified under -f or -s are relative ' +
                            'to this directory ' +
                            '[%s]' % defaultconf.pull('RawDir'),
                       metavar='DIR')
        i.add_argument('-f', '--RawFastData',
                       dest='RawFastData', nargs='+',
                       help='fast (high frequency) data files: given as' +
                       'one or more filenames, wildcard pattern, or ' +
                            'a sub-directory of RawDir (for all files within)' +
                            '[%s]' % defaultconf.pull('RawFastData'),
                       metavar='FILE')
        i.add_argument('-s', '--RawSlowData',
                       dest='RawSlowData', nargs="+",
                       help='fast (high frequency) data files: given as '
                            'one or more filenames, wildcard pattern, or '
                            'a sub-directory of RawDir '
                            '(for all files within) '
                            '[%s]' % defaultconf.pull('RawSlowData'),
                       metavar='FILE')
        i.add_argument('-o', '--OutDir',
                       dest='OutDir', nargs=1,
                       help='directory where to store the output '
                       '[%s]' % defaultconf.pull('OutDir'),
                       metavar='DIR')
        i.add_argument('-i', '--PlfitInterval',
                       dest='plfitstring', nargs=1,
                       help='duration for the averaging interval in days'
                       '[%s]' % defaultconf.pull('PlfitInterval'),
                       metavar='DAYS')

    varg = parser.add_mutually_exclusive_group()
    varg.add_argument('-v', '--verbose',
                      dest='verbose', 
                      action='store_const',
                      const=logging.INFO,
                      default=logging.NORMAL,
                      help='increase output verbosity')
    varg.add_argument('--debug',
                      dest='verbose', 
                      action='store_const',
                      const=logging.DEBUG,
                      help='decrease output verbosity')
    varg.add_argument('--debug-insane',
                      dest='verbose', 
                      action='store_const',
                      const=logging.INSANE,
                      help='decrease output verbosity')
    varg.add_argument('-q', '--quiet',
                      dest='verbose',
                      action='store_const',
                      const=logging.ERROR,
                      help='decrease output verbosity')

    parser.add_argument('--version', action='version',
                        version=f'ecpet version: {version}\n'
                                f'libraries:\n'
                                f'      numpy: {ver_np}\n'
                                f'      pandas: {ver_pd}\n'
                                f'      scipy: {ver_scipy}\n'
                                f'      matplotlib: {ver_mpl}\n'
                                f'      wxPython: {ver_wx}\n')

    # parse
    arglist = vars(parser.parse_args())

    # convert length1-1 lists into strings
    for a in arglist:
        if isinstance(arglist[a], list):
            if len(arglist[a]) == 1:
                arglist[a] = arglist[a][0]

    # collect the conf values among the arguments
    values = {k: v for k, v in arglist.items()
              if k in defaultconf.tokens}

    if arglist['verbose'] in [logging.CRITICAL, logging.ERROR,
                              logging.WARNING, logging.NORMAL,
                              logging.INFO, logging.DEBUG, logging.INSANE]:
        logging.root.setLevel(arglist['verbose'])
    logger.normal('logging level: {:s}'.format(
        logging.getLevelName(logging.root.getEffectiveLevel())))

    # set command
    if arglist['run_command'] is not None:
        options['command'] = arglist['run_command']
    else:
        options['command'] = 'gui'
    # set project file
    if 'project' in arglist and arglist['project'] is not None:
        options['project'] = arglist['project']
    # set config file
    if 'config' in arglist and arglist['config'] is not None:
        options['config'] = arglist['config']
    # set starting stage
    if 'stage' in arglist and arglist['stage'] is not None:
        options['stage'] = arglist['stage']

    # convert averaging string into seconds
    if 'avgstring' in values and values['avgstring'] is not None:
        logger.debug('got averaging string "%s"' % values['avgstring'])
        values['AvgInterval'] = ec.string_to_interval(values['avgstring'])
        logger.debug('convert to AvgInterval=%is' % values['AvgInterval'])
        del(values['avgstring'])
    else:
        values['AvgInterval'] = None

    # convert planarfit interval string into seconds
    if 'plfitstring' in values and values['plfitstring'] is not None:
        logger.debug('got planar-fit interval string "%s"' %
                      values['plfitstring'])
        values['PlfitInterval'] = ec.string_to_interval(
            values['plfitstring'])
        logger.debug('converted to PlfitInterval=%is' %
                      values['PlfitInterval'])
        del(values['plfitstring'])
    else:
        values['PlfitInterval'] = None

    # make sure only set values are there
    for k, v in list(values.items()):
        if v is None:
            del values[k]
            logger.insane('values: %s deleted' % k)
        else:
            logger.debug('values: %s = %s' % (k, v))

    return values, options

# ----------------------------------------------------------------
#
# run in text mode
#

def processing_console(values, options):
    logger.debug('values: %s' % values)
    logger.debug('options: %s' % options)
    if options['command'] == 'make':
        conf = ecconfig.Config(values)
        ecconfig.write(defaultconf, conf, full=True)
    elif options['command'] == 'update':
        if options['project'] is not None:
            ecdb.dbfile = options['project']
        oldconf = ecconfig.complete(
            ecconfig.read_file(options['ConfName']))
        conf = ecconfig.apply(oldconf, values)
        ecconfig.write(defaultconf, conf, full=True)
        startat = None
    elif options['command'] == 'run':
        if options['config'] is not None and options['project'] is not None:
            if not os.path.exists(options['ConfName']):
                logger.fatal('config file %s not found!' %
                              options['ConfName'])
                sys.exit(2)
            if os.path.exists(options['project']):
                logger.error('project file %s already exists. '
                             'please rename or remove '
                             '%s' % options['project'])
                sys.exit(1)
            conf = ecconfig.complete(ecconfig.read_file(options['config']))
            ecdb.dbfile = options['project']
        elif options['config'] is not None and options['project'] is None:
            if not os.path.exists(options['config']):
                logger.fatal('config file %s '
                             'not found!' % options['config'])
                sys.exit(2)
            conf = ecconfig.complete(ecconfig.read_file(options['config']))
            base = os.path.splitext(os.path.basename(options['config']))[0]
            ecdb.dbfile = base + '.ecp'
        elif options['config'] is None and options['project'] is not None:
            if not os.path.exists(options['project']):
                logger.fatal('project file %s not found!' %
                              options['project'])
                sys.exit(2)
            ecdb.dbfile = options['project']
            conf = ecdb.conf_from_db()
        else:
            logger.critical('either a config file (-c) or a project (-p) '
                             'must be specified!')
            sys.exit(2)
        #
        if options['stage'] is not None:
            startat = ec.stages.index(options['stage'])
        else:
            startat = 0

        ecdb.conf_to_db(conf)

        if have_com and sys.stdout.isatty():
            logger.debug('initiaslizing progress indicator')

            def getstage(msg):
                global stage_progress, stage_name
                stage_progress = 0
                stage_name = msg

            def getprogress(msg):
                global stage_progress
                stage_progress = msg

            def getincrement(msg):
                global stage_progress
                stage_progress += msg

            pub.subscribe(getprogress, "progress")
            pub.subscribe(getincrement, "increment")
            pub.subscribe(getstage, "stage")

            logger.debug('progress indicator started')

            def task(event):
                global stage_progress, stage_name
                stage_progress = 0
                stage_name = ""
                # execute a task in a loop
                while True:
                    # block for a moment
                    sleep(2)
                    # check for stop
                    if event.is_set():
                        break
                    # refresh progress bar
                    logger.normal('============ STAGE: %5s '
                                   % stage_name
                                   + ' PROGRESS: %5.1f%% ============)'
                                   % stage_progress)

            # create the event
            event = Event()
            # create and configure a new thread
            thread = Thread(target=task, args=(event,))
            # start the new thread
            logger.debug('progress thread starting')
            thread.start()

            indicator = True
        else:
            indicator = False

        ecengine.process(conf, startat)

        if indicator:
            logger.debug('progress thread stopping')
            event.set()
            thread.join()

    else:
        raise ValueError('unknown command "%s"' % options['command'])

# ----------------------------------------------------------------
#
# switch user interface
#


def user_interface():

    # check number of command line arguments (  1 = only command given )
    if len(sys.argv) > 1:
        # if command line arguments are present, get them
        values, options = commandline_interface()
    else:
        values = {}
        options = {}
        if not have_wx:
            # quit if no graphic environment is available
            logger.critical('only command-line interface availabe.')
            logger.critical('Run '+__file__+' -h for help')
            sys.exit(1)
        else:
            options = {'command': 'gui',
                       'project': None,
                       'stage': None}

    logger.debug(f"selected command: {options['command']}")
    # create a complete config with all the user settings
    if options['command'] == 'gui':
        if 'project' in values.keys():
            options['project'] = values['project']
        graphical_interface(options)
    else:
        processing_console(values, options)
    logger.normal('finished successfully')


# ----------------------------------------------------------------
#
# main call
#
if __name__ == "__main__":
    user_interface()
