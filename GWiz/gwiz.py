#!/usr/bin/python

#!!!KL see module subprocess to run the external wizards. subprocess.Popen is the trick. See file:///Z:/PythonPopenSnippet.html

"""GWiz -- An GCode Wizard with a graphical user interface. Written by
K. Lerman"""

import sys, os
#import sys, time, traceback, types
import dircache

import Tkinter

t = Tkinter.Tk(); t.wm_withdraw()

BASE = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), ".."))
sys.path.insert(0, os.path.join(BASE, "lib", "python"))

import emc

import wx                  # This module uses the new wx namespace

import  wx.lib.scrolledpanel as scrolled
import wx.lib.buttons as buttons
from wx import EmptyIcon
from wx.lib.stattext import GenStaticText

# For debugging
##wx.Trap();
##print "wx.VERSION_STRING = %s (%s)" % (wx.VERSION_STRING, wx.USE_UNICODE and 'unicode' or 'ansi')
##print "pid:", os.getpid()
##raw_input("Press Enter...")

# read ini file stuff

home = os.getenv('HOME')

if len(sys.argv) <= 2 or sys.argv[1] != "-ini":
    emcrc = emc.ini(home + '/' + '.emcrc')
    inifilename = emcrc.find("PICKCONFIG", "LAST_CONFIG")

    inifile = emc.ini(inifilename)

    if inifilename == None:
        raise SystemExit, "-ini must be first argument or must pick config"
else:
    inifile = emc.ini(sys.argv[2])

program_directory = inifile.find("DISPLAY", "PROGRAM_PREFIX")
wizard_root = inifile.find("WIZARD", "WIZARD_ROOT")
if wizard_root is None:
  wizard_root = '/usr/share/gwiz/wizards'

print "program_directory:", program_directory
print "wizard root:", wizard_root

#buttonpath = 'buttons/'
#imagepath = 'bitmaps/'

buttonpath = '/usr/share/gwiz/images/'
imagepath = '/usr/share/gwiz/images/'

#------------------------------------------------------------------------
# ParamPanel: a scrolled panel for wizard parameters
#------------------------------------------------------------------------

class ParamPanel(scrolled.ScrolledPanel):
    def __init__(self, parent):
        self.parent = parent
        self.fgs1 = None
        scrolled.ScrolledPanel.__init__(self, parent, wx.ID_ANY)
        GWiz.ParamPanel = self

    def SetParams(self, directory):

        if not directory:
            return None

##         print 'directory:%s panel:%s' % (directory, self.panel)
        
        fullPath = directory + 'config'

        self.SetWindowStyle(wx.TAB_TRAVERSAL|wx.SUNKEN_BORDER)
        self.SetName('paramPanel')
        GWiz.panel = self
        self.fgs1 = wx.FlexGridSizer(cols=2, vgap=4, hgap=4)
            
        #print 'GWiz.panel', GWiz.panel
        self.DestroyChildren()
        self.SetupScrolling()
         
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self, 1, wx.EXPAND)

        vbox = wx.BoxSizer(wx.VERTICAL)

        vbox.Add(hbox, 0)
        self.SetSizer(vbox)

        ##1 is this needed 
        xline = "None"
        GWiz.gcodeComment = xline
        GWiz.titleText.SetLabel(xline)
        GWiz.widgetList = []
        GWiz.comboDict = {}
        GWiz.inverseComboDict = {}

        try:
            f = open(fullPath, 'r')
            self.ReadConfig(f)
            f.close()

        except IOError:
             print "Unable to read config:", fullPath
    
        self.SetSizer(self.fgs1)

        self.SetupScrolling()

        self.SetAutoLayout(1)
        self.SetupScrolling()

    def ReadConfig(self, f):
        firstDone = False
        for line in f:
            line = line.rstrip()

            #print "Read Line ==>", line, "<=="

            if not firstDone:
                firstDone = True
                GWiz.gcodeComment = line
         	#print "comment:", line
                GWiz.titleText.SetLabel(line)
                GWiz.widgetList = []
                GWiz.comboDict = {}
                GWiz.inverseComboDict = {}
            else:
                self.ReadConfigLine(line)

    def ReadConfigLine(self, line):

        utype = name = toolTip = vdefault = ''

        try:
            lineParts = line.split('|')
            utype = lineParts[0]
            name = lineParts[1]
            toolTip = lineParts[2]
            vdefault = lineParts[3]
        except:
            pass

        if name == '':
            #print "name is blank"
            return None

        if utype == '':
            return None

        label = GenStaticText(self, wx.ID_ANY, name+':')
	label.SetLabel(name+':')

        label.SetToolTipString(toolTip)

#	print "LabelText", label.GetLabel()

        #print 'lineParts:', "|", utype, "|",name, "|",vdefault, "|",toolTip

        if (utype == 'S') | (utype == 'U'):
            tc = wx.TextCtrl(self, wx.ID_ANY, vdefault, size=(50,-1))
            tc.Bind(wx.EVT_TEXT, GWiz.OnWidgetChanged)
            GWiz.widgetList = GWiz.widgetList + [tc]
            
        elif utype == 'L':

            # A way to save and retrieve the value
            
            comboList = lineParts[4::2]
            comboValueList = lineParts[3::2]
            comboDict = {}
            inverseComboDict = {}
            for i in range(len(comboList)):
                name = comboList[i]
                value = comboValueList[i]
                comboDict[name] = value
                inverseComboDict[value] = name
                #print "dict:", name, value
                
            tc = wx.ComboBox(self, wx.ID_ANY,
            #                 size=(75,-1),
                             size=(100,-1),
                             choices=comboList,
                             style=wx.CB_DROPDOWN | wx.CB_READONLY)

            tc.Bind(wx.EVT_TEXT, GWiz.OnWidgetChanged)
            # the default is zero

            tc.SetSelection(0)

            GWiz.comboDict[tc] = comboDict
            GWiz.inverseComboDict[tc] = inverseComboDict

            GWiz.widgetList = GWiz.widgetList + [tc]

        else:
            print "Illegal utype:%s" % utype
            return None
            
        tc.SetToolTipString(toolTip)

        self.fgs1.Add(label, flag=wx.ALIGN_RIGHT |
                wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=10)

        self.fgs1.Add(tc, flag=wx.RIGHT)

        if utype == 'S':
            pass
        elif utype == 'U':
##             print "Type U"
##             tc.SetValidator(wx.Validator("\\d{1,3}\\.\\d{0,4}"))
            pass
        elif utype == 'L':
            #print "Type L"
            pass
        else:
            print "Type unknown"
            pass # ignore the line

#----------------------------------------------------------------------


#---------------------------------------------------------------------------
# Editor pane:
#   has a single editor line
#   OK and Cancel boxes

class EditLine(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        # Make widgets

        GWiz.textArea = wx.ListBox(self, wx.ID_ANY, pos=wx.DefaultPosition,
                              size=wx.DefaultSize,
                              style=wx.LC_REPORT
                              | wx.BORDER_NONE | wx.LB_SINGLE | wx.LB_HSCROLL
                              | wx.LB_ALWAYS_SB)


        GWiz.textArea.Bind(wx.EVT_LISTBOX, GWiz.OnItemSelected)
        GWiz.textArea.Bind(wx.EVT_CHAR, GWiz.OnTextAreaChar)

        GWiz.currentItem = None
        GWiz.pasteBuffer = None

        GWiz.textLine = wx.TextCtrl(self, wx.ID_ANY, size=wx.DefaultSize)

        GWiz.textLine.Bind(wx.EVT_TEXT, GWiz.OnTextChanged)
        GWiz.textLine.Bind(wx.EVT_CHAR, GWiz.OnChar)

        GWiz.DisableBoth()

        # add to sizers for layout
        tbox = wx.BoxSizer(wx.VERTICAL)
        
        tbox.Add(GWiz.textArea, 1, wx.EXPAND)

        tbox.Add(GWiz.textLine, 0, wx.EXPAND)
        
        self.SetSizer(tbox)
        self.Fit()

#---------------------------------------------------------------------------


def opj(path):
    """Convert paths to the platform-specific separator"""
    s = apply(os.path.join, tuple(path.split('/')))
    # HACK: on Linux, a leading / gets lost...
    if path.startswith('/'):
        s = '/' + s
    return s


#---------------------------------------------------------------------------
class gWiz(wx.Frame):

    def __init__(self, parent, title):
#        wx.Frame.__init__(self, parent, wx.ID_ANY, title, size = (950, 720),
        wx.Frame.__init__(self, parent, wx.ID_ANY, title, size = (950, 760),
                          style=wx.DEFAULT_FRAME_STYLE |
                          wx.NO_FULL_REPAINT_ON_RESIZE)

        globals()["GWiz"] = self
        self.SetMinSize((640,480))

        self.paramPanel = None
        self.fileIsOpen = False
        self.openFileName = None

        self.displayingWidget = False
        self.editing = False
	self.editingMode = "insert" # None or "insert" or "edit"
	self.mode = None # or "text" or "wizard"

        self.convMode = "wiz" # wiz or conv (conversational)
        self.wizardsLoaded = False
        
        self.bitmap = None
        self.loaded = False
        self.cwd = os.getcwd()
        self.curOverview = ""
        self.shell = None

        bmp = wx.Bitmap(buttonpath + 'wizicon.png', wx.BITMAP_TYPE_PNG)
        icon = EmptyIcon()
        icon.CopyFromBitmap(bmp)
        self.SetIcon(icon)

	self.Bind(wx.EVT_CHAR, GWiz.OnCharToWindow)

        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        self.Bind(wx.EVT_ICONIZE, self.OnIconfiy)
        self.Bind(wx.EVT_MAXIMIZE, self.OnMaximize)

        self.Centre(wx.BOTH)
        self.CreateStatusBar(1, wx.ST_SIZEGRIP)

        splitter0 = wx.Panel(self, wx.ID_ANY)
        splitter0.SetName("splitter0")

        splitter = wx.SplitterWindow(splitter0, wx.ID_ANY,
                                     style=wx.CLIP_CHILDREN |
                                     wx.SP_LIVE_UPDATE | wx.SP_3D)

        splitter.SetName("splitter")

        self.splitter2 = wx.SplitterWindow(splitter, wx.ID_ANY,
                                      style=wx.CLIP_CHILDREN |
                                      wx.SP_LIVE_UPDATE | wx.SP_3D)
        self.splitter2.SetName("splitter2")


        # Prevent TreeCtrl from disp. all items after destruction when True
        self.dying = False

        # Make a File menu
        self.mainmenu = wx.MenuBar()
        menu = wx.Menu()

        self.MakeMenuItem(menu, '&New', 'Create a new file', self.OnNew)
        self.MakeMenuItem(menu, '&Open', 'Open a file', self.OnOpen)
        self.MakeMenuItem(menu, '&Save', 'Save the existing file', self.OnSave)
        self.MakeMenuItem(menu, 'Save &As',
                          'Save the file with a specified name', self.OnSaveAs)

        menu.AppendSeparator()

        self.MakeMenuItem(menu, '&Redirect Output',
                          'Redirect print statements to a window',
                          self.OnToggleRedirect)

        self.MakeMenuItem(menu, 'E&xit\tCtrl-Q',
                          'Get the heck outta here', self.OnFileExit)

        self.mainmenu.Append(menu, '&File')

        # Make an Edit menu
        menu = wx.Menu()

        self.MakeMenuItem(menu, 'Cut', 'Delete the selected line', self.OnCut)
        self.MakeMenuItem(menu, 'Paste',
                          'Paste a saved line on top of selection',
                          self.OnPaste)
        self.MakeMenuItem(menu, 'Copy', 'Copy the selected line', self.OnCopy)
        self.MakeMenuItem(menu, '&Save', 'Save the existing file', self.OnSave)

        menu.AppendSeparator()

        self.MakeMenuItem(menu, 'Insert Blank',
                          'Insert a blank line before the selection',
                          self.OnInsert)
        self.MakeMenuItem(menu, 'Insert Wizard',
                          'Insert a wizard before the selection',
                          self.OnInsertWizard)

        self.mainmenu.Append(menu, '&Edit')

        # Make a Help menu
        menu = wx.Menu()

#        shellItem = menu.Append(wx.ID_ANY, 'Open Py&Shell Window\tF5',
#          'An interactive interpreter window with the '
#                                'demo app and frame objects in the namespace')
#        inspToolItem = menu.Append(wx.ID_ANY, 'Open &Widget Inspector\tF6',
#                                'A tool that lets you browse the live '
#                                   'widgets and sizers in an application')
#        menu.AppendSeparator()
        helpItem = menu.Append(wx.ID_ANY, '&About GWiz',
                               'wxPython RULES!!!')
        wx.App.SetMacAboutMenuItemId(helpItem.GetId())

#        self.Bind(wx.EVT_MENU, self.OnOpenShellWindow, shellItem)
#        self.Bind(wx.EVT_MENU, self.OnOpenWidgetInspector, inspToolItem)
        self.Bind(wx.EVT_MENU, self.OnHelpAbout, helpItem)
        self.mainmenu.Append(menu, '&Help')
        self.SetMenuBar(self.mainmenu)

        # Create a Tool Bar
        self.toolBar = wx.Panel(splitter0, wx.ID_ANY)
        self.toolBar.SetName("toolBar")

        hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.MakeAllToolButtons(self.toolBar, hbox)

        
        self.toolBar.SetSizer(hbox)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.toolBar, 0, wx.EXPAND)
        vbox.Add((10,10))
        vbox.Add(splitter, 1, wx.EXPAND)

        splitter0.SetSizer(vbox)

        # !!!KL Why is this needed?
        vbox.Fit(splitter0)
        
        # Create a graphic panel
        # Create a wizard panel

        self.CreateWizard()

        # Create a TreeCtrl
        tID = wx.NewId()
        leftPanel = wx.Panel(self.splitter2)
        leftPanel.SetName("leftPanel")
        
        self.treeMap = {}
        self.owordMap = {}
        self.tree = wx.TreeCtrl(leftPanel, tID, style = wx.TR_DEFAULT_STYLE)
        self.RecreateTree()

        self.tree.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.OnItemExpanded, id=tID)
        self.tree.Bind(wx.EVT_TREE_ITEM_COLLAPSED,
                       self.OnItemCollapsed, id=tID)
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, id=tID)
        
##        if "gtk2" in wx.PlatformInfo:
##            self.ovr.SetStandardFonts()

        self.Bind(wx.EVT_ACTIVATE, self.OnActivate)
        wx.GetApp().Bind(wx.EVT_ACTIVATE_APP, self.OnAppActivate)

        # add the windows to the splitter and split it.

        self.splitter2.SplitVertically(leftPanel, self.wizardPanel, 220)

        leftBox = wx.BoxSizer(wx.VERTICAL)
        leftBox.Add(self.tree, 1, wx.EXPAND)
        leftPanel.SetSizer(leftBox)

        self.editLine = EditLine(splitter)
        splitter.SplitHorizontally(self.splitter2, self.editLine, -160)

        splitter.SetMinimumPaneSize(60)
        self.splitter2.SetMinimumPaneSize(120)

        # select initial items
        self.tree.SelectItem(self.root)

        self.SetFileChanged(False)

        # Load 'Main' module
        self.loaded = True

        #!!!KL the following was for the original Demo
        #!!!KL in the future add args to specify a file to open
        #!!!KL and the line to position at
        # select some other initial module?
##         if len(sys.argv) > 1:
##             arg = sys.argv[1]
##             if arg.endswith('.py'):
##                 arg = arg[:-3]
##             selectedDemo = self.treeMap.get(arg, None)
##             if selectedDemo:
##                 self.tree.SelectItem(selectedDemo)
##                 self.tree.EnsureVisible(selectedDemo)
        #self.Fit() -- is this useful or needed


    def SetFileChanged(self, val):
	GWiz.fileHasChanged = val
	if val:
	    GWiz.saveButton.Enable()
	else:
	    GWiz.saveButton.Disable()

    def ToolButtonData(self):

         return ((None,'', buttonpath+'/exit.png', 'Exit', self.OnExit),
                (None,'', buttonpath+'new.png', 'New', self.OnNew),
                (None,'', buttonpath+'open.png', 'Open', self.OnOpen),
                ('saveButton','', buttonpath+'save.png', 'Save', self.OnSave),
                (None,'', buttonpath+'cut.png', 'Cut', self.OnCut),
                (None,'', buttonpath+'copy.png', 'Copy', self.OnCopy),
                (None,'', buttonpath+'paste.png', 'Paste',
                 self.OnPaste),
                (None,'', buttonpath+'insertblank.png', 'Insert Blank',
                 self.OnInsert),
                (None,'', buttonpath+'insertwiz.png', 'Insert Wizard',
                 self.OnInsertWizard),
                ('upButton','', buttonpath+'up.png', 'Up',
                 self.OnUp),
                ('downButton','', buttonpath+'down.png',
                 'Down', self.OnDown),
                (None,'', None, None, None),

                ('convButton', 'Toggle' , buttonpath+'conversational.png',
                 'Conversational Mode', self.OnConv),
                (None,'', None, None, None),

                ('acceptButton', '', buttonpath+'accept.png',
                 'Accept Changes', self.OnAccept),
                ('rejectButton', '', buttonpath+'reject.png',
                 'Cancel Changes', self.OnReject),


                ('editButton', 'Toggle', buttonpath+'edit.png',
                 'Edit the current line', self.OnEdit),

                (None,'', buttonpath+'default.png', 'Set Defaults',
                 self.OnWizardDefault))

        
    def MakeAllToolButtons(self, bar, hbox):
        for eachButton, eachType, eachImage, eachTip, eachHandler in \
                self.ToolButtonData():
            button = self.MakeToolButton(bar, wx.ID_ANY, eachType, eachImage,
                                        hbox, eachTip, eachHandler)
            #!!!KL a hack. Is there a neat way to assign an out of
            #!!!KL scope variable
            if eachButton:
                self.__dict__[eachButton] = button

    def MakeToolButton(self, bar, id, type, pngFile, hbox, tip, handler):
        if pngFile == None:
            hbox.Add((10,10), 1, wx.EXPAND)
            return None
        bmp = wx.Bitmap(pngFile, wx.BITMAP_TYPE_PNG)
        if type == 'Toggle':
            button = buttons.GenBitmapToggleButton(bar, id, bmp)
        else:
            button = wx.BitmapButton(bar, id, bmp)
        button.SetToolTipString(tip)
        button.Bind(wx.EVT_BUTTON, handler)
        hbox.Add(button, 0, wx.EXPAND)
        hbox.Add((10,10))
        return button

    def MakeMenuItem(self, menu, label, tip, handler):
        item = menu.Append(wx.ID_ANY, label, tip)
        self.Bind(wx.EVT_MENU, handler, item)

    def OnExit(self, event):
        self.Close()

    def AskSaveFileIfNecessary(self):

        #!!!KL should ask if want to save current contents of text area
        #!!!KL there may be contents even if no file
        #!!!KL or should we disallow editing without at least a 'New'?
        if self.fileIsOpen and self.fileHasChanged:
            # Bring up a warning dialog
            dialog = wx.MessageDialog(self, "A file is currently open.\n"
                                      "Do you want to save your changes?",
                                      "Warning!",
                                      wx.CANCEL |
                                      wx.YES_NO | wx.ICON_WARNING)
            hit = dialog.ShowModal()
            if hit == wx.ID_YES:
                self.SaveOpenFile()
                self.DiscardOpenFile()
                self.fileIsOpen = False

            if hit == wx.ID_NO:
                self.DiscardOpenFile()
                self.fileIsOpen = False

            if hit == wx.ID_CANCEL:
                pass

            dialog.Destroy()
            
    def OnOpen(self, event):

        self.AskSaveFileIfNecessary()

        # get the name of the file to open
        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultDir=os.getcwd(),
            defaultFile="",
            wildcard='*.wiz',
            style=wx.OPEN | wx.CHANGE_DIR)

        if dlg.ShowModal() == wx.ID_OK:
            f = dlg.GetPaths()

            print "file:", f[0], ':'

            print "new path:", os.getcwd(),':'
            self.ReadGcodeFile(f[0])

        dlg.Destroy()
        self.fileIsOpen = True
	GWiz.SetFileChanged(False)

        # give focus to the text area
        GWiz.textArea.SetFocus()

    def OnWizardDefault(self, event):
        pass

    def OnConv(self, evt):
        if GWiz.convMode == "conv":
	    GWiz.convButton.SetValue(False)
	    GWiz.convMode = "wiz"
        else:
            GWiz.convButton.SetValue(True)
            GWiz.convMode = "conv"
            if GWiz.wizardsLoaded == False:
                GWiz.wizardsLoaded = True
                #!!!KL need to put in a real file name...
                filename = wizard_root+"/Conversational\ Mode.wiz"
                print "file name:%s:" % filename
                t.tk.call("send", "axis", "open_file_name", filename)
            
        evt.Skip()
	return

        
    def OnEdit(self, evt):

	if self.currentItem == None:
	    print "OnEdit currentItem is None value:",GWiz.editButton.GetValue()
	    GWiz.textLine.SetFocus()
	    return

	if GWiz.editingMode == "edit":
	    GWiz.editButton.SetValue(False)
	    GWiz.editingMode = "insert"
	    print "editing mode set to insert"
	    GWiz.textLine.SetFocus()
	    evt.Skip()
	    return

	GWiz.editingMode = "edit"
        GWiz.editButton.SetValue(True)
        print "editing mode set to edit"
        line = GWiz.textArea.GetString(self.currentItem)
	wiz = Wizard.FindWizardForLine(line)

	if wiz:
	    # a wizard
	    GWiz.SetWizard(wiz)
	    GWiz.mode = 'wizard'
	    GWiz.UngenerateGcode(line)
	else:
	    # a text line
            GWiz.textLine.SetValue(line)
	    GWiz.mode = 'text'

        GWiz.textLine.SetFocus()
        evt.Skip()

    def OnUp(self, event):

        GWiz.textArea.SetFocus()
        if (self.currentItem == None) or (self.currentItem == 0):
            return None

        text = GWiz.textArea.GetString(self.currentItem)
        previous = GWiz.textArea.GetString(self.currentItem-1)
        GWiz.textArea.SetString(self.currentItem, previous)
        GWiz.textArea.SetString(self.currentItem-1, text)

        self.currentItem = self.currentItem-1
        GWiz.textArea.SetSelection(self.currentItem)
        GWiz.textArea.EnsureVisible(self.currentItem)
	GWiz.SetFileChanged(True)

    def OnDown(self, event):

        GWiz.textArea.SetFocus()

        if (self.currentItem == None) or \
            (self.currentItem >= GWiz.textArea.GetCount()-1):
            return None

        text = GWiz.textArea.GetString(self.currentItem)
        next = GWiz.textArea.GetString(self.currentItem+1)
        GWiz.textArea.SetString(self.currentItem, next)
        GWiz.textArea.SetString(self.currentItem+1, text)

        self.currentItem = self.currentItem+1
        GWiz.textArea.SetSelection(self.currentItem)
        GWiz.textArea.EnsureVisible(self.currentItem)
	GWiz.SetFileChanged(True)

    def OnInsertStringItem(self, event):
        GWiz.textArea.InsertStringItem(self.currentItem, "(blank line)")

    def SaveOpenFile(self):
        print "SaveOpenFile"
        pass

    def DiscardOpenFile(self):
        print "DiscardOpenFile"
        self.fileIsOpen = False

        GWiz.textArea.ClearAll()
        GWiz.textArea.InsertColumn(0, "Line")
        GWiz.textLine.Clear()

    def OnNew(self, event):
        pass

    def OnSave(self, event):
	#!!!KL need to update change info
        if self.fileHasChanged:
            if self.openFileName == None:
                self.OnSaveAs(event)
            else:
                self.WriteGcodeFile(self.openFileName)
            
        self.SetFileChanged(False)

    def OnSaveAs(self, event):
        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultDir=os.getcwd(),
            defaultFile="",
            wildcard='*.wiz',
            style=wx.SAVE | wx.CHANGE_DIR)

        if dlg.ShowModal() == wx.ID_OK:
            f = dlg.GetPaths()

            print "file:", f[0], ':'

            print "new path:", os.getcwd(),':'
            self.openFileName = f[0]+".wiz"
            self.WriteGcodeFile(self.openFileName)

    def WriteGcodeFile(self, fileName):
        # open the file
        try:
            f = open(fileName, 'w')
            self.openFileName = fileName
        except:
            self.ErrorOpeningFile(fileName)
            return None

	GWiz.SetFileChanged(False)
        for i in range(GWiz.textArea.GetCount()):
            text = GWiz.textArea.GetString(i)
            f.write(text + '\n')

        f.close()
            

    def EndEdit(self):
        GWiz.upButton.Enable()
        GWiz.downButton.Enable()
        GWiz.DisableBoth()
        GWiz.textArea.Enable()
	GWiz.paramPanel.Enable()
	GWiz.textLine.Enable()
	GWiz.mode = None
	GWiz.editingMode = "insert"
        GWiz.editButton.SetValue(False)
	GWiz.tree.Enable()

    def DisableBoth(self):
        GWiz.rejectButton.Disable()
        GWiz.acceptButton.Disable()
	GWiz.editButton.Enable()

    def EnableBoth(self):
        GWiz.rejectButton.Enable()
        GWiz.acceptButton.Enable()
        #!!!KL do not set edit mode -- only set manually
	#GWiz.editButton.Disable()

    def OnAccept(self, evt):
	if GWiz.mode == 'wizard':
	    line = GWiz.GenerateGcode()
	    print "OnAccept: Mode was wizard:", line,":"
	else:
            line = GWiz.textLine.GetLineText(0)
	    GWiz.textLine.Clear()
#	    GWiz.textLine.SetValue("line was cleared")
	     
	    print "OnAccept: Mode was NOT wizard:", line,":"
	    GWiz.textLine.SetFocus()

        if GWiz.editingMode == "insert":
	    print "editingMode is insert"
            if GWiz.currentItem == None:
	        GWiz.currentItem = 0
	    else:
                GWiz.currentItem += 1
            GWiz.textArea.InsertItems((line,), GWiz.currentItem)
            GWiz.textArea.Select(GWiz.currentItem)
	    pass
	elif GWiz.editingMode == "edit":
	    print "editingMode is edit"
            if GWiz.currentItem == None:
	        GWiz.currentItem = 0
            GWiz.textArea.SetString(GWiz.currentItem, line)
	    pass

        GWiz.textArea.SetFirstItem(GWiz.currentItem)
	GWiz.textArea.SetSelection(GWiz.currentItem)
	GWiz.SetFileChanged(True)
        GWiz.EndEdit()

        if GWiz.convMode == "conv":
            #print "send_mdi_command:%s:" % line
            t.tk.call("send", "axis", ("send_mdi_command", line))

    def OnReject(self, evt):
	""" If inserting restore the current wizard to its default and
	    the text to blank. If editing, restore the current wizard to
	    its default and the text to the current line. """
	#!!!KL
	if GWiz.mode == 'wizard':
	    print "Mode was wizard"
            #!!!KL must restore the wizard line
	    # if inserting, restore from default
	    # if editing, restore from line being edited

	    if GWiz.currentItem is None:
	        GWiz.EndEdit()
		return

            line = GWiz.textArea.GetString(GWiz.currentItem)
            wiz = Wizard.FindWizardForLine(line)
	    if GWiz.editingMode == "insert":
                #  restore from default
		#!!!KL need to figure out how
		#GWiz.SetWizard(GWiz.currentWizard)
		GWiz.UngenerateGcode(GWiz.defaultWizardGcodeLine)
	    elif GWiz.editingMode == "edit":
		GWiz.UngenerateGcode(line)
	    else:
	        pass
	else:
            GWiz.textLine.Clear()
	    print "OnReject: Mode was NOT wizard"
	    GWiz.textLine.SetFocus()
        GWiz.EndEdit()

    def CreateWizard(self):

        self.wizardPanel = wx.Panel(self.splitter2, wx.ID_ANY)
        self.wizardPanel.SetName("wizardPanel");

        self.graphicPanel = wx.Panel(self.wizardPanel, wx.ID_ANY)
        self.graphicPanel.SetName("graphicPanel");

        self.titleText = GenStaticText(self.wizardPanel, wx.ID_ANY, 'None')
        self.titleText.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.NORMAL))
        self.titleText.SetBackgroundColour("Yellow")

        self.paramPanel = ParamPanel(self.wizardPanel)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.graphicPanel, 5, wx.EXPAND)
#        hbox.Add((10,10))
#        hbox.Add(self.paramPanel, 1, wx.EXPAND)
        hbox.Add(self.paramPanel, 2, wx.EXPAND)

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
#        hbox2.Add((32,32))
        hbox2.Add(self.titleText, 0, wx.EXPAND)
        vbox = wx.BoxSizer(wx.VERTICAL)

        vbox.Add(hbox2, 0, wx.EXPAND)
        vbox.Add(hbox, 1, wx.EXPAND)

        self.wizardPanel.SetSizer(vbox)

    def ErrorOpeningFile(self, fileName):

        dialog = wx.MessageDialog(self,
                                  "The file open operation on:%s failed.\n"
                                      "Do you want to exit?" % fileName,
                                      "Warning!",
                                      wx.YES_NO | wx.ICON_WARNING)
        hit = dialog.ShowModal()
        if hit == wx.ID_YES:
                self.Close()

    def ReadGcodeFile(self, fileName):
        """ Read a G Code file and display it in the list. """

        try:
            f = open(fileName, 'r')
            self.openFileName = fileName
        except:
            self.ErrorOpeningFile(fileName)
            return None

        for line in f:
            line = line.rstrip()
            GWiz.textArea.Append(line)
        f.close()

    def OnCopy(self, event):
        if self.currentItem:
            self.pasteBuffer = GWiz.textArea.GetString(self.currentItem)
    
    def OnPaste(self, event):
        if self.currentItem:
            GWiz.SetFileChanged(True)
            GWiz.textArea.SetString(self.currentItem, self.pasteBuffer)

    def OnCut(self, event):
        if self.currentItem != None:
            self.pasteBuffer = GWiz.textArea.GetString(self.currentItem)
            GWiz.textArea.Delete(self.currentItem)
        else:
            return None

        count = GWiz.textArea.GetCount()

        if self.currentItem > count - 1:
            self.currentItem = count - 1

        if count == 0:
            self.currentItem = None
            GWiz.textLine.SetLabel("")
        else:
            GWiz.textArea.Select(self.currentItem)

        GWiz.SetFileChanged(True)

    def OnInsert(self, event):
        if not self.currentItem:
            self.currentItem = 0
	else:
	    self.currentItem += 1

        GWiz.textArea.InsertItems(("(blank line)",),self.currentItem)
        GWiz.textArea.Select(self.currentItem)
        GWiz.SetFileChanged(True)

    def OnInsertWizard(self, event):
        if self.editing:
            return None

        if not self.displayingWidget:
	    print "OnInsertWizard returning None"
            return None

        if self.currentItem == None:
            self.currentItem = 0
	else:
            self.currentItem += 1

        line = self.GenerateGcode()
	print "currentItem:", self.currentItem, "generated code:",line,":"
        GWiz.textArea.InsertItems((line,), self.currentItem)
        GWiz.textArea.Select(self.currentItem)

        GWiz.textArea.SetFirstItem(self.currentItem)
        GWiz.SetFileChanged(True)

    def GenerateGcode(self):
        """ Generate a line of gcode from the current widgets in panel. """

        gcode = GWiz.currentGcode + " CALL " '(' + GWiz.gcodeComment + ')'
        for widget in GWiz.widgetList:
            if widget.GetClassName() == "wxComboBox":
                comboDict = GWiz.comboDict[widget]
                value = widget.GetValue()
                if value == '':
                    value = '0'
                else:
                    value = comboDict[value]
                    
                gcode += " [" + value + "]"      
            else:
                gcode += " [" + widget.GetValue() + "]"
        return gcode

    def GetGcodeArgs(self, line):

        # parts each have beginning of a param
        parts = line.split('[')

        # skip the first part
        for part in parts[1:]:
            arg = part.split(']')[0]
            yield arg
    
    def UngenerateGcode(self, line):
        """ Given a line, load the widgets in the panel from the code """
        widgets = GWiz.widgetList
        for arg in self.GetGcodeArgs(line):
            widget = widgets[0]
            widgets = widgets[1:]
            if widget.GetClassName() == 'wxComboBox':
                inverseComboDict = GWiz.inverseComboDict[widget]
                label = inverseComboDict[arg]
                widget.SetValue(label)
            else:
                widget.SetValue(arg)

    def FindOword(self, line):
        """ Given a line return None or a lower case oword """
        
        line = line.lower()
        #!!!KL must check that line is not empty
        if not line or (line[0] != 'o' and line[0] != 'O'):
            return None

        if line[1] == '<':
            # named o-word
            # if missing '>' will return the whole line -- but that's OK
            lineParts = line.split('>')
            # make return begin with a lower case 'o'
            ret = lineParts[0] + '>'
        else:
            # the line with just the end (after the oword)
            lineEnd = line[1:].lstrip('0123456789')

            ret = line[:-len(lineEnd)]
                       
        print "FindOword returning |%s|" % ret
        return ret

    def GetWizItem(self, line):

	#print 'entered GetWizItem'
        # get rid of leading and trailing blanks
        line = line.strip().rstrip()

        if len(line) == 0:
            return None

        oword = Wizard.FindOword(line)

        if oword == None:
            return None
        else:
            try:
                item = self.owordMap[oword]
                return item
            except KeyError:
                return None

    
    def HandleSelection(self, item):
        self.currentItem = item
        self.savedLine = GWiz.textArea.GetString(self.currentItem)

        line = GWiz.textArea.GetString(self.currentItem)
	wiz = Wizard.FindWizardForLine(line)

        if wiz:
	    print "HandleSelection: line is a wizard:", line, ":"
            # the line is a wizard
	    GWiz.SetWizard(wiz)
            GWiz.UngenerateGcode(line)
            #GWiz.textLine.SetValue( "Select EDIT to edit this "
            #                       "line in the Wizard")
	    #GWiz.textLine.SetFocus()
	    GWiz.textLine.Clear()
	    GWiz.EndEdit()
        else:
	    print "OnItemSelected: line is NOT a wizard:", line, ":"

            # the line is not a wizard
            GWiz.textLine.SetValue(line)

            # disable accept and reject
            GWiz.DisableBoth()

            # was disabled in OnTextChanged
            self.upButton.Enable()
            self.downButton.Enable()
            GWiz.tree.Enable()
            GWiz.paramPanel.Enable()

            GWiz.textArea.Enable()
            GWiz.textArea.SetFocus()

    def OnItemSelected(self, event):
        """ Invoked when a line in the text area is selected. There
        are two cases: line is wizard and line is not wizard """

	print 'entered OnItemSelected'

	self.HandleSelection(event.GetSelection())
        event.Skip()

    def OnCharToWindow(self, event):
	keyInt = event.GetKeyCode()
	escape = 27
	enter = 0xd
	cursorUp = 0x13d
	cursorDown = 0x13f
	print "OnCharToWindow: key:0x%x:" % keyInt

        event.Skip()

    def OnTextAreaChar(self, event):
	keyInt = event.GetKeyCode()
	escape = 27
	enter = 0xd
	cursorUp = 0x13d
	cursorDown = 0x13f
	print "OnTextAreaChar: key:0x%x:" % keyInt

	if keyInt == cursorUp and GWiz.currentItem > 0:
	    GWiz.currentItem = GWiz.currentItem - 1
	elif keyInt == cursorDown and GWiz.currentItem < \
	    GWiz.textArea.GetCount()-1:
	    GWiz.currentItem = GWiz.currentItem + 1

        GWiz.textArea.Select(GWiz.currentItem)
	self.HandleSelection(GWiz.currentItem)
	GWiz.textArea.SetFocus()

        event.Skip()

    def OnChar(self, event):
	#key = chr(event.GetKeyCode())
	keyInt = event.GetKeyCode()
	escape = 27
	enter = 0xd
	cursorUp = 0x13d
	cursorDown = 0x13f
	#print "key:0x%x:" % keyInt, key, ":"
	print "key:0x%x:" % keyInt
        if keyInt == enter:
	    GWiz.OnAccept(event)
	elif keyInt == escape:
	    GWiz.OnReject(event)
	elif keyInt == cursorUp or keyInt == cursorDown:
	    GWiz.OnTextAreaChar(event)

        event.Skip()

    def OnTextChanged(self, event):
        # called whenever there is a change -- includes
        # changes caused by program
   
        self.upButton.Disable()
        self.downButton.Disable()
        self.EnableBoth()
        #GWiz.textArea.SetItemBackgroundColour(GWiz.currentItem, '#ff0000')
        GWiz.textArea.Disable()
	GWiz.mode = 'text'
	GWiz.paramPanel.Disable()
	GWiz.tree.Disable()
        event.Skip()

    def OnWidgetChanged(self, event):
        # called whenever there is a change -- includes
        # changes caused by program
   
        self.upButton.Disable()
        self.downButton.Disable()
        self.EnableBoth()
        GWiz.textArea.Disable()
	GWiz.mode = 'wizard'
	GWiz.textLine.Disable()
	GWiz.tree.Disable()

    #---------------------------------------------
    def TraverseTree(self, parent, dirName):
        """ Recursively traverses the directory tree adding the item to
            the tree and adding it to the dictionary for lookup """

        try:
            direct = dircache.listdir(dirName)
            dircache.annotate(dirName, direct)
            #print "direct OK", dirName, direct

        except IOError:
            #print "direct NG", dirName
            return ''

        # read the wizard

        wizard = Wizard.FromDirectory(dirName)
        oword = wizard.Oword()
        item = wizard.Name()

        if self.root == None:
            self.root = self.tree.AddRoot(item)
            child = self.root

        else:
            child = self.tree.AppendItem(parent, item)

        self.tree.SetItemPyData(child, wizard)

        # associate the item in the tree with the name
        # so that selecting the item can be converted to the proper directory
        self.treeMap[item] = (oword, dirName)

        # coerce oword to be lower case
        owordlc = oword.lower() # use all lower case
        # child is a treeItemId
        self.owordMap[owordlc] = child

        # now traverse the children one at a time

        # for each child that is a directory
        for d in direct[:]:
            if d[-1] == '/':
                self.TraverseTree(child, dirName + d)
                self.tree.Expand(child)
        
    #---------------------------------------------
    def RecreateTree(self):
        self.tree.DeleteAllItems() 

        self.root = None

        self.TraverseTree(self.root, wizard_root+"/")

        Wizard.DumpAll()
        self.tree.Expand(self.root)
    
    def WriteText(self, text):
        if text[-1:] == '\n':
            text = text[:-1]
        #wx.LogMessage(text)

    def write(self, txt):
        self.WriteText(txt)

    #---------------------------------------------
    def OnItemExpanded(self, event):
        #item = event.GetItem()
        #wx.LogMessage("OnItemExpanded: %s" % self.tree.GetItemText(item))
        event.Skip()

    #---------------------------------------------
    def OnItemCollapsed(self, event):
        #item = event.GetItem()
        #wx.LogMessage("OnItemCollapsed: %s" % self.tree.GetItemText(item))
        event.Skip()

    #---------------------------------------------
##     def OnTreeLeftDown(self, event):
##         # reset the overview text if the tree item is clicked on again
##         pt = event.GetPosition();
##         item, flags = self.tree.HitTest(pt)
##         #print "OnTreeLeftDown - item:", item

##         # seems to give PREVIOUS selection
##         # makes sense because the event hasn't been processed here yet
##         selected = self.tree.GetSelection()
##         selectedText = self.tree.GetItemText(selected)

##         #print "OnTreeLeftDown - selectedText:", selectedText
##         if selected:
##             treeItemList = self.treeMap.get(selectedText)
##             if treeItemList:
##                 treeItem = treeItemList[1]
##             else:
##                 treeItem = None
##             #print "treeItem:", treeItem

##         event.Skip()


    def DisplayWizard(self, directory):

        if not directory:
            self.displayingWidget = False
            return None

        fullPath = directory + 'screen.png'
##         print "DisplayWizard", fullPath
        if self.bitmap:
            self.bitmap.Destroy()
            self.bitmap = None

        GWiz.titleText.SetLabel("")

        try:
            # Display the Graphic
	    f = open(opj(fullPath), "r")
	    if f:
	        f.close()

            # read the image -- this generates on on screen
	    # error if no file
            png = wx.Image(opj(fullPath),
                           wx.BITMAP_TYPE_PNG)

	  
            # this is how to scale an image
            finishWidth = 400.0
            finishHeight = 300.0
            aspectRatio = finishWidth * 1.0 / finishHeight
            imageAspectRatio = png.GetWidth() * 1.0 / png.GetHeight()

            if imageAspectRatio > aspectRatio:
                factor = png.GetWidth()/finishWidth
                pass
            else:
                factor = png.GetHeight()/finishHeight
                pass

            png2 = png.Scale(png.GetWidth()/factor, png.GetHeight()/factor)

            # now convert it to a bitmap
            png3 = wx.BitmapFromImage(png2)

            if self.bitmap:
                self.bitmap.Destroy()

            self.bitmap = wx.StaticBitmap(self.graphicPanel, wx.ID_ANY, png3,
                                          (0, 0),
                            (png3.GetWidth(), png3.GetHeight()))

            self.displayingWidget = True            
            

        except IOError:
            print "DisplayWizard -- NG", fullPath
            self.displayingWidget = False
	    #return None

        # Display the Panel or blank
        # !!!KL need to create the new panel here

        self.paramPanel.SetParams(directory)
#        print "Finished SetParams", directory
#	self.paramPanel.Enable()
#	self.paramPanel.Raise()
#	self.paramPanel.Refresh()
#	self.paramPanel.Show()
#	self.paramPanel.Update()

    def SetWizard(self, wiz):
	GWiz.currentWiz = wiz
        directory = wiz.Directory()
        GWiz.currentGcode = wiz.Oword()
        self.currentWizard = directory
        self.DisplayWizard(directory)
	self.defaultWizardGcodeLine = self.GenerateGcode()
            

    #---------------------------------------------
    def OnSelChanged(self, event):
        """ Changed selection in Wizard Tree """

        item = event.GetItem()

        wiz = self.tree.GetItemPyData(item)

        # Need a way to update display only if wiz changes
        # SetWiz returns True if wiz is not previous wiz
        if  Wizard.SetWiz(wiz):
            self.SetWizard(wiz)

        event.Skip()
        
    #---------------------------------------------

    # Menu methods
    def OnFileExit(self, *event):
        self.Close()

    def OnToggleRedirect(self, event):
        ap = wx.GetApp()
        if event.Checked():
            ap.RedirectStdio()
            print "Print statements and other standard "
            "output will now be directed to this window."
        else:
            ap.RestoreStdio()
            print "Print statements and other standard "
            "output will now be sent to the usual location."
 
    def OnHelpAbout(self, event):
        from About import MyAboutBox
        if Wizard.Wiz() == None:
            html = Wizard.NoHelp()
        else:
            html = Wizard.Wiz().About()

        about = MyAboutBox(self, html)
        about.ShowModal()
        about.Destroy()

    def OnOpenShellWindow(self, evt):
        return None

    def OnOpenWidgetInspector(self, evt):
        # Activate the widget inspector that was mixed in with the
        # app, see MyApp and MyApp.OnInit below.
        wx.GetApp().ShowInspectionTool()

        
    #---------------------------------------------
    def OnCloseWindow(self, event):
        self.dying = True
        self.mainmenu = None
        self.Destroy()

    #---------------------------------------------
    def OnIconfiy(self, evt):
        #wx.LogMessage("OnIconfiy: %s" % evt.Iconized())
        evt.Skip()

    #---------------------------------------------
    def OnMaximize(self, evt):
        #wx.LogMessage("OnMaximize")
        evt.Skip()

    #---------------------------------------------
    def OnActivate(self, evt):
        #wx.LogMessage("OnActivate: %s" % evt.GetActive())
        evt.Skip()

    #---------------------------------------------
    def OnAppActivate(self, evt):
        #wx.LogMessage("OnAppActivate: %s" % evt.GetActive())
        evt.Skip()

#---------------------------------------------------------------------------
#---------------------------------------------------------------------------

class Wizard(object):
    """ A Wizard object supports reading the wizard from the directory and
    all manipulations of the files associated with the wizard. It can
    save defaults, load defaults, generate gcode, and read generated
    gcode. It is the model that represents a wizard.

    The Wizard class know how to find a wizard given the gcode it generated.
    """

    wizOwordDict = {}
    currentWizard = None

    def FindWizardForLine(cls, line):
	try:
            oword = cls.FindOword(line)
            if oword == None:
                return None
            wiz = cls.wizOwordDict[oword]

	except KeyError:
	    return None
	    
        return wiz

    FindWizardForLine = classmethod(FindWizardForLine)

    def Wiz(cls):
        return cls.currentWizard
    Wiz = classmethod(Wiz)

    def SetWiz(cls, wiz):
        """ Returns True if new wiz is different than previous wiz """

        oldWiz = cls.currentWizard
        cls.currentWizard = wiz
        return wiz != oldWiz
    SetWiz = classmethod(SetWiz)

    def AddAWizard(cls, wiz):
        cls.wizOwordDict[wiz.Oword()] = wiz
    AddAWizard = classmethod(AddAWizard)

    def DumpAll(cls):
        """ Dump the dictionary of Wizards. """
##         print 'wizOwordDict', cls.wizOwordDict
        pass
    DumpAll = classmethod(DumpAll)
        
    def Oword(self):
        return self.oword

    def NoHelp(cls):
        return 'No Help Info Available'
    NoHelp = classmethod(NoHelp)

    def About(self):
        try:
            f = open(self.directory + 'help', 'r')
            lines = f.read()
            f.close()
        except IOError:
            lines = 'No Help Info Available for %s' % self.name
        return lines

    def Name(self):
        return self.name

    def FindOword(cls, line):
        """ Given a line return None or a lower case oword """

        line = line.lower()
        if len(line) == 0 or line[0] != 'o':
            return None

        if line[1] == '<':
            # named o-word
            # if missing '>' will return the whole line -- but that's OK
            lineParts = line.split('>')
            # make return begin with a lower case 'o'
            ret = lineParts[0] + '>'

        else:
            # the line with just the end (after the oword)
	    # !!!KL this is wrong. Consider o#123 or o[#123+5]
	    # On the other hand, it doesn't matter because it will NOT
	    # match a wizard and that's all we care about.
            lineEnd = line[1:].lstrip('0123456789')

            ret = line[:-len(lineEnd)]
                       
##         print "FindOword returning |%s|" % ret

        return ret

    FindOword = classmethod(FindOword)

    def FromDirectory(cls, directory):

##         wiz = cls()
##         wiz.directory = directory
##         wiz.oword, wiz.name = wiz.ReadDescFile(directory)
##         cls.AddAWizard(wiz)
        self = cls()
        self.directory = directory
        self.oword, self.name = self.ReadDescFile(directory)
	self.oword = self.oword.lower()
        cls.AddAWizard(self)

        return self

    FromDirectory = classmethod(FromDirectory)

    def Directory(self):
        return self.directory

    def ReadDescFile(self, dirName):
        try:
            f = open(dirName + 'desc', 'r')

            # the file has a single line
            line = f.readline()
            line = line.rstrip()

            # pipe separator
            lineParts = line.split('|')

            f.close()

        except IOError: 
            lineParts =  ('o<none>', dirName)

        return lineParts
    

#---------------------------------------------------------------------------
#---------------------------------------------------------------------------

class MySplashScreen(wx.SplashScreen):
    def __init__(self):
        bmp = wx.Image(opj(imagepath + 'splash.png')).ConvertToBitmap()
        wx.SplashScreen.__init__(self, bmp,
                                 wx.SPLASH_CENTRE_ON_SCREEN |
                                    wx.SPLASH_TIMEOUT,
                                 5000, None, -1)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.fc = wx.FutureCall(2000, self.ShowMain)


    def OnClose(self, evt):
        # Make sure the default handler runs too so this window gets
        # destroyed
        evt.Skip()
        self.Hide()
        
        # if the timer is still running then go ahead and show the
        # main frame now
        if self.fc.IsRunning():
            self.fc.Stop()
            self.ShowMain()


    def ShowMain(self):
        frame = gWiz(None, "GWiz: (A G-Code Wizard Framework)")
        frame.Show()
        if self.fc.IsRunning():
            self.Raise()

        
#import wx.lib.mixins.inspection
#import wx.lib.mixins

#class MyApp(wx.App, wx.lib.mixins.inspection.InspectionMixin):
#    def OnInit(self):

class MyApp(wx.App):
    def OnInit(self):

        """
        Create and show the splash screen.  It will then create and show
        the main frame when it is time to do so.
        """

        wx.SystemOptions.SetOptionInt("mac.window-plain-transition", 1)

        # For debugging
        #self.SetAssertMode(wx.PYAPP_ASSERT_DIALOG)

        # Normally when using a SplashScreen you would create it, show
        # it and then continue on with the applicaiton's
        # initialization, finally creating and showing the main
        # application window(s).  In this case we have nothing else to
        # do so we'll delay showing the main frame until later (see
        # ShowMain above) so the users can see the SplashScreen effect.        
        splash = MySplashScreen()
        splash.Show()

        # Setup the InspectionMixin
        #self.Init()
        
        return True

#---------------------------------------------------------------------------


def main():
    global app
    app = MyApp(False)
    app.MainLoop()

#----------------------------------------------------------------------------

GWiz = None
app = None

if __name__ == '__main__':
    __name__ = 'GWiz'
    main()

#----------------------------------------------------------------------------
