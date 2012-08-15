# Software License Agreement (BSD License)
#
# Copyright (c) 2012, Dorian Scholz
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the name of Willow Garage, Inc. nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import roslib
roslib.load_manifest('rqt_py_console')

import qt_gui.qt_binding_helper # @UnusedImport
from rqt_gui_py.plugin import Plugin
from py_console_widget import PyConsoleWidget
from qt_gui_py_common.simple_settings_dialog import SimpleSettingsDialog

try:
    from spyder_console_widget import SpyderConsoleWidget
    _has_spyderlib = True
except ImportError:
    _has_spyderlib = False
        
class PyConsole(Plugin):
    """
    Plugin providing an interactive Python console
    """
    def __init__(self, context):
        super(PyConsole, self).__init__(context)
        self.setObjectName('PyConsole')
        
        self._context = context
        self._widget = None
        self._use_spyderlib = _has_spyderlib
            
    def _update_console_widget(self):
        old_widget = self._widget
                
        if _has_spyderlib and self._use_spyderlib:
            self._widget = SpyderConsoleWidget(self._context)
            self._widget.setWindowTitle('SpyderConsole')
        else:
            self._widget = PyConsoleWidget(self._context)
            self._widget.setWindowTitle('PyConsole')
        
        if old_widget is not None:
            self._context.remove_widget(old_widget)
        self._context.add_widget(self._widget)

    def save_settings(self, plugin_settings, instance_settings):
        instance_settings.set_value('use_spyderlib', self._use_spyderlib)

    def restore_settings(self, plugin_settings, instance_settings):
        self._use_spyderlib = _has_spyderlib and bool(instance_settings.value('use_spyderlib', True))
        self._update_console_widget()

    def trigger_configuration(self):
        options=[
            {'title': 'SpyderConsole', 'description': 'Advanced Python console with tab-completion (needs spyderlib to be installed).', 'enabled': _has_spyderlib},
            {'title': 'PyConsole', 'description': 'Simple Python console.'},
        ]
        dialog = SimpleSettingsDialog(title='PyConsole Options')
        dialog.add_exclusive_option_group(title='Console Type', options=options, selected_index=int(not self._use_spyderlib))
        console_type = dialog.get_settings()[0]
        new_use_spyderlib = {0: True, 1: False}.get(console_type['selected_index'], self._use_spyderlib)
        if self._use_spyderlib != new_use_spyderlib:
            self._use_spyderlib = new_use_spyderlib
            self._update_console_widget()
        
    def shutdown_plugin(self):
        if self._widget is not None and hasattr(self._widget, 'shutdown'):
            self._widget.shutdown()
    