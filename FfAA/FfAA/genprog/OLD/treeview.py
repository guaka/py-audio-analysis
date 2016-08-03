#! /usr/bin/env python

from wxPython.wx import *

import string

#---------------------------------------------------------------------------

class TestTreeCtrlPanel(wxPanel):
	def __init__(self, parent):
		# Use the WANTS_CHARS style so the panel doesn't eat the Return key.
		wxPanel.__init__(self, parent, -1, style=wxWANTS_CHARS)
		EVT_SIZE(self, self.OnSize)

		self.log = ""
		tID = wxNewId()

		self.tree = wxTreeCtrl(self, tID, wxDefaultPosition, wxDefaultSize,
							   wxTR_HAS_BUTTONS
							   | wxTR_EDIT_LABELS
							   #| wxTR_MULTIPLE
							   | wxTR_HIDE_ROOT
							   )

		isz = (16, 16)
		il = wxImageList(isz[0], isz[1])
		fldridx		= il.Add(wxArtProvider_GetBitmap(wxART_FOLDER,		wxART_OTHER, isz))
		fldropenidx = il.Add(wxArtProvider_GetBitmap(wxART_FILE_OPEN,	wxART_OTHER, isz))
		fileidx		= il.Add(wxArtProvider_GetBitmap(wxART_REPORT_VIEW, wxART_OTHER, isz))
		# smileidx	  = il.Add(images.getSmilesBitmap())

		self.tree.SetImageList(il)
		self.il = il

		# NOTE:	 For some reason tree items have to have a data object in
		#		 order to be sorted.  Since our compare just uses the labels
		#		 we don't need any real data, so we'll just use None below for
		#		 the item data.

		self.root = self.tree.AddRoot("The Root Item")
		self.tree.SetPyData(self.root, None)
		self.tree.SetItemImage(self.root, fldridx, wxTreeItemIcon_Normal)
		self.tree.SetItemImage(self.root, fldropenidx, wxTreeItemIcon_Expanded)

		self.tree.Expand(self.root)
		EVT_TREE_ITEM_EXPANDED	(self, tID, self.OnItemExpanded)
		EVT_TREE_ITEM_COLLAPSED (self, tID, self.OnItemCollapsed)
		EVT_TREE_SEL_CHANGED	(self, tID, self.OnSelChanged)
		EVT_TREE_ITEM_ACTIVATED (self, tID, self.OnActivate)

		EVT_RIGHT_DOWN(self.tree, self.OnRightClick)
		EVT_RIGHT_UP(self.tree, self.OnRightUp)

	def add_code(self, code):
		self.add_subtree(self.root, code)
		self.tree.Expand(self.root)

	def add_subtree(self, treeview_node, code_subtree):
		# print "add_subtree:", code_subtree
		node = self.tree.AppendItem(treeview_node, repr(code_subtree.complexity()) + " " + code_subtree.node_repr_collapsed())
		self.tree.SetPyData(node, code_subtree)
		for child in code_subtree.children:
			self.add_subtree(node, child)
		self.tree.Expand(node)

	def delete_tree(self):
		self.tree.DeleteChildren(self.root)

	def OnRightClick(self, event):
		pt = event.GetPosition();
		item, flags = self.tree.HitTest(pt)
		#self.log.WriteText("OnRightClick: %s, %s, %s\n" %
		#					(self.tree.GetItemText(item), type(item), item.__class__))
		self.tree.SelectItem(item)


	def OnRightUp(self, event):
		pt = event.GetPosition();
		item, flags = self.tree.HitTest(pt)
		#self.log.WriteText("OnRightUp: %s (manually starting label edit)\n"
		#					% self.tree.GetItemText(item))
		self.tree.EditLabel(item)


	def OnSize(self, event):
		w, h = self.GetClientSizeTuple()
		self.tree.SetDimensions(0, 0, w, h)


	def OnItemExpanded(self, event):
		item = event.GetItem()
		code = self.tree.GetPyData(item)
		self.tree.SetItemText(item, code.node_repr_expanded())
		#self.log.WriteText("OnItemExpanded: %s\n" % self.tree.GetItemText(item))

	def OnItemCollapsed(self, event):
		item = event.GetItem()
		code = self.tree.GetPyData(item)
		self.tree.SetItemText(item, code.node_repr_collapsed())
		#self.log.WriteText("OnItemCollapsed: %s\n" % self.tree.GetItemText(item))

	def OnSelChanged(self, event):
		self.item = event.GetItem()
		event.Skip()
		#self.log.WriteText("OnSelChanged: %s\n" % self.tree.GetItemText(self.item))
		#if wxPlatform == '__WXMSW__':
		#	pass
		#	 #self.log.WriteText("BoundingRect: %s\n" %
		#	 #					 self.tree.GetBoundingRect(self.item, True))
		#items = self.tree.GetSelections()
		#print map(self.tree.GetItemText, items)


	def OnActivate(self, evt):
		pass
		#self.log.WriteText("OnActivate: %s\n" % self.tree.GetItemText(self.item))

#---------------------------------------------------------------------------

class RunDemoApp(wxApp):
	def __init__(self, population = None):
		wxApp.__init__(self, 0) ##wxPlatform == "__WXMAC__")
		self.population = population

	def OnInit(self):
		wxInitAllImageHandlers()
		wxLog_SetActiveTarget(wxLogStderr())

		#wxFrame.__init__(self, parent, id, title,
		#				 wxPoint(0, 0), wxSize(360, 100))

		frame = wxFrame(None, -1, "Tree test",
						pos = wxPoint(0, 0),
						size = wxSize(800, 300),
						style = wxNO_FULL_REPAINT_ON_RESIZE | wxDEFAULT_FRAME_STYLE)
		frame.CreateStatusBar()
		menuBar = wxMenuBar()

		menuFile = wxMenu()
		menuFile.Append(102, "&Next\tAlt-N", "Next generation")
		menuBar.Append(menuFile, "&File")
		EVT_MENU(self, 102, self.NextGeneration)

		menuFile.Append(101, "E&xit\tAlt-X", "Exit demo")
		EVT_MENU(self, 101, self.OnButton)
		
		menuHelp = wxMenu()
		menuHelp.Append(103, "&About\tAlt-A", "About")
		menuBar.Append(menuHelp, "&Help")
		EVT_MENU(self, 103, self.OnMenuAbout)

		frame.SetMenuBar(menuBar)
		frame.Show(True)
		EVT_CLOSE(frame, self.OnCloseFrame)

		win = TestTreeCtrlPanel(frame)
		self.win = win
		
		# a window will be returned if the demo does not create
		# its own top-level window
		if win:
			# so set the frame to a good size for showing stuff
			# frame.SetSize((900, 600))
			win.SetFocus()
			self.window = win

		else:
			# otherwise the demo made its own frame, so just put a
			# button in this one
			if hasattr(frame, 'otherWin'):
				b = wxButton(frame, -1, " Exit ")
				frame.SetSize((200, 100))
				EVT_BUTTON(frame, b.GetId(), self.OnButton)
			else:
				# It was probably a dialog or something that is already
				# gone, so we're done.
				frame.Destroy()
				return True

		self.SetTopWindow(frame)
		self.frame = frame

		#wxLog_SetActiveTarget(wxLogStderr())
		#wxLog_SetTraceMask(wxTraceMessages)
		return True

	def NextGeneration(self, evt):
		self.population.nextGeneration()
		self.win.delete_tree()
		self.ShowPopulation()

	def ShowPopulation(self):
		for code in self.population:
			self.win.add_code(code)

	def OnButton(self, evt):
		self.frame.Close(True)

	def OnMenuAbout(self, event):
		dlg = wxMessageDialog(self.frame,
							  'Genetic Algorithm To Find ISA Structures and (not yet) Transformations\n\n' + \
							  'written in Python, using wxPython\n' + \
							  'by Kasper.Souren@ircam.fr',
							  'GATFIST',
							  wxOK | wxICON_INFORMATION)
                              #wxYES_NO | wxNO_DEFAULT | wxCANCEL | wxICON_INFORMATION)
		dlg.ShowModal()
		dlg.Destroy()

	def OnCloseFrame(self, evt):
		#if hasattr(self, "window") and hasattr(self.window, "ShutdownDemo"):
		#	 self.window.ShutdownDemo()
		evt.Skip()


def view_population(population):
	app = RunDemoApp(population)
	app.ShowPopulation()
	#for code in population:
	#	print code
	#	app.win.add_code(code)
	#app.win.delete_population()
	app.MainLoop()


if __name__ == '__main__':
	app = RunDemoApp()
	app.MainLoop()
