'''
@name    PhpIntellisense
@package sublime_plugin
@author  Neil Opet

This Sublime Text 2 plugin will autocomplete the php
function arguments if you choose to do so.  It will also
display the arguments in the status bar of Sublime Text,
showing which arguments are required, optional, and passed
by reference.

Windows and Mac: use [CTRL] + [Space] within the function parenthesis
to autocomplete the method.
'''

import os
import re
import ctypes
import string
import sublime
import sublime_plugin

def is_php( view ):
	syntax, _ = os.path.splitext(os.path.basename(view.settings().get('syntax')))
	return (syntax == "PHP")

class PhpIntellisense(sublime_plugin.EventListener):  
    def on_load(self, view):  
    	if not is_php(view):
    		return None

class PhpIntellisenseCommand(sublime_plugin.TextCommand):
	def highlight(self, region):
		#int, list, str, str, int
		edit = self.view.begin_edit()
		self.view.add_regions('first_word', [sublime.Region(region[0], region[1])], 'first word')
		self.view.end_edit(edit)

	def run(self, edit):
		# if we're not running PHP, might as well just exit
		if not is_php(self.view):
			return None
		# get the function name
		pt = self.view.sel()[0].begin()
		fn = self.view.substr(self.view.word(pt - 1))
		# set the binary
		binary = "php.exe" if sublime.platform() == "windows" else "php"
		# format the exec string
		cmd = r'"%s" --rf %s' % (
			os.path.join(sublime.packages_path(), "PhpIntellisense", binary), 
			fn
		)
		output = os.popen(cmd, 'r').read()
		pattern     = re.compile("Parameter #[0-9] \[\s(.*)\s\]\n+")
		params = pattern.findall(output)
		strStatus = strInsert = ""
		optionalParams = []
		requiredParams = []
		for param in params:
			opt = param[0:10]
			if opt == "<optional>":
				optionalParams.append(param.replace("<optional> ", ""))
			elif opt == "<required>":
				requiredParams.append(param.replace("<required> ", ""))

		strStatus = fn + "( " + ", ".join(requiredParams) + ", [ " + ", ".join(optionalParams) + " ] )"
		strInsert = (", ".join(requiredParams + optionalParams)).replace("&", "")
		# display status text
		sublime.status_message(strStatus)
		# insert the autocomplete
		self.view.insert(edit, pt, strInsert)
		# set cursor to beginning of word
		self.view.sel().clear()
		self.view.sel().add(self.view.word(pt + 2))
	