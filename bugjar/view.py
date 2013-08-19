"""A module containing a visual representation of the connection

This is the "View" of the MVC world.
"""
import os
from Tkinter import *
from tkFont import *
from ttk import *
import tkMessageBox

from bugjar.widgets import DebuggerCode, BreakpointView, StackView, InspectorView


class MainWindow(object):
    def __init__(self, root, debugger):
        '''
        -----------------------------------------------------
        | main button toolbar                               |
        -----------------------------------------------------
        |       < ma | in content area >      |             |
        |            |                        |             |
        | File list  | File name              | Inspector   |
        | (stack/    | Code area              |             |
        | breakpnts) |                        |             |
        |            |                        |             |
        |            |                        |             |
        -----------------------------------------------------
        |     status bar area                               |
        -----------------------------------------------------

        '''

        self.base_path = os.path.abspath(os.getcwd())
        self.base_path = os.path.normcase(self.base_path) + '/'

        self.debugger = debugger
        # Associate the debugger with this view.
        self.debugger.view = self

        # Root window
        self.root = root
        self.root.title('Bugjar')
        self.root.geometry('1024x768')

        # Prevent the menus from having the empty tearoff entry
        self.root.option_add('*tearOff', FALSE)
        # Catch the close button
        self.root.protocol("WM_DELETE_WINDOW", self.on_quit)
        # Catch the "quit" event.
        self.root.createcommand('exit', self.on_quit)

        # Setup the menu
        self._setup_menubar()

        # Set up the main content for the window.
        self._setup_button_toolbar()
        self._setup_main_content()
        self._setup_status_bar()

        # Now configure the weights for the root frame
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=0)
        self.root.rowconfigure(1, weight=1)
        self.root.rowconfigure(2, weight=0)

        debugger.start()

    ######################################################
    # Internal GUI layout methods.
    ######################################################

    def _setup_menubar(self):
        # Menubar
        self.menubar = Menu(self.root)

        # self.menu_Apple = Menu(self.menubar, name='Apple')
        # self.menubar.add_cascade(menu=self.menu_Apple)

        self.menu_file = Menu(self.menubar)
        self.menubar.add_cascade(menu=self.menu_file, label='File')

        self.menu_edit = Menu(self.menubar)
        self.menubar.add_cascade(menu=self.menu_edit, label='Edit')

        # self.menu_help = Menu(self.menubar, name='help')
        # self.menubar.add_cascade(menu=self.menu_help)

        # self.menu_Apple.add_command(label='Test', command=self.cmd_dummy)

        # self.menu_file.add_command(label='New', command=self.cmd_dummy, accelerator="Command-N")
        # self.menu_file.add_command(label='Open...', command=self.cmd_dummy)
        # self.menu_file.add_command(label='Close', command=self.cmd_dummy)

        # self.menu_edit.add_command(label='New', command=self.cmd_dummy)
        # self.menu_edit.add_command(label='Open...', command=self.cmd_dummy)
        # self.menu_edit.add_command(label='Close', command=self.cmd_dummy)

        # self.menu_help.add_command(label='Test', command=self.cmd_dummy)

        # last step - configure the menubar
        self.root['menu'] = self.menubar

    def _setup_button_toolbar(self):
        '''
        The button toolbar runs as a horizontal area at the top of the GUI.
        It is a persistent GUI component
        '''

        # Main toolbar
        self.toolbar = Frame(self.root)
        self.toolbar.grid(column=0, row=0, sticky=(W, E))

        # Buttons on the toolbar
        self.run_button = Button(self.toolbar, text='Run', command=self.cmd_run)
        self.run_button.grid(column=0, row=0)

        self.step_button = Button(self.toolbar, text='Step', command=self.cmd_step)
        self.step_button.grid(column=1, row=0)

        self.next_button = Button(self.toolbar, text='Next', command=self.cmd_next)
        self.next_button.grid(column=2, row=0)

        self.return_button = Button(self.toolbar, text='Return', command=self.cmd_return)
        self.return_button.grid(column=3, row=0)

        self.toolbar.columnconfigure(0, weight=0)
        self.toolbar.rowconfigure(0, weight=0)

    def _setup_main_content(self):
        '''
        Sets up the main content area. It is a persistent GUI component
        '''

        # Main content area
        self.content = PanedWindow(self.root, orient=HORIZONTAL)
        self.content.grid(column=0, row=1, sticky=(N, S, E, W))

        # Create subregions of the content
        self._setup_file_lists()
        self._setup_code_area()
        self._setup_inspector()

        # Set up weights for the left frame's content
        self.content.columnconfigure(0, weight=1)
        self.content.rowconfigure(0, weight=1)

        self.content.pane(0, weight=1)
        self.content.pane(1, weight=2)
        self.content.pane(2, weight=1)

    def _setup_file_lists(self):

        self.file_notebook = Notebook(self.content, padding=(0, 5, 0, 5))
        self.content.add(self.file_notebook)

        self._setup_stack_frame_list()
        self._setup_breakpoint_list()

    def _setup_stack_frame_list(self):
        self.stack_frame = Frame(self.content)
        self.stack_frame.grid(column=0, row=0, sticky=(N, S, E, W))
        self.file_notebook.add(self.stack_frame, text='Stack')

        self.stack = StackView(self.stack_frame)
        self.stack.grid(column=0, row=0, sticky=(N, S, E, W))

        # # The tree's vertical scrollbar
        self.stack_scrollbar = Scrollbar(self.stack_frame, orient=VERTICAL)
        self.stack_scrollbar.grid(column=1, row=0, sticky=(N, S))

        # # Tie the scrollbar to the text views, and the text views
        # # to each other.
        self.stack.config(yscrollcommand=self.stack_scrollbar.set)
        self.stack_scrollbar.config(command=self.stack.yview)

        # Setup weights for the "stack" tree
        self.stack_frame.columnconfigure(0, weight=1)
        self.stack_frame.columnconfigure(1, weight=0)
        self.stack_frame.rowconfigure(0, weight=1)

        # Handlers for GUI events
        self.stack.bind('<<TreeviewSelect>>', self.on_stack_frame_selected)

    def _setup_breakpoint_list(self):
        self.breakpoint_list_frame = Frame(self.content)
        self.breakpoint_list_frame.grid(column=0, row=0, sticky=(N, S, E, W))
        self.file_notebook.add(self.breakpoint_list_frame, text='Breakpoints')

        self.breakpoint_list = BreakpointView(self.breakpoint_list_frame)
        self.breakpoint_list.grid(column=0, row=0, sticky=(N, S, E, W))

        # The tree's vertical scrollbar
        self.breakpoint_list_scrollbar = Scrollbar(self.breakpoint_list_frame, orient=VERTICAL)
        self.breakpoint_list_scrollbar.grid(column=1, row=0, sticky=(N, S))

        # Tie the scrollbar to the text views, and the text views
        # to each other.
        self.breakpoint_list.config(yscrollcommand=self.breakpoint_list_scrollbar.set)
        self.breakpoint_list_scrollbar.config(command=self.breakpoint_list.yview)

        # Setup weights for the "breakpoint list" tree
        self.breakpoint_list_frame.columnconfigure(0, weight=1)
        self.breakpoint_list_frame.columnconfigure(1, weight=0)
        self.breakpoint_list_frame.rowconfigure(0, weight=1)

        # Handlers for GUI events
        self.breakpoint_list.tag_bind('breakpoint', '<Double-Button-1>', self.on_breakpoint_double_clicked)
        self.breakpoint_list.tag_bind('breakpoint', '<<TreeviewSelect>>', self.on_breakpoint_selected)

    def _setup_code_area(self):
        self.code_frame = Frame(self.content)
        self.code_frame.grid(column=1, row=0, sticky=(N, S, E, W))

        # Label for current file
        self.current_file = StringVar()
        self.current_file_label = Label(self.code_frame, textvariable=self.current_file)
        self.current_file_label.grid(column=0, row=0, sticky=(W, E))

        # Code display area
        self.code = DebuggerCode(self.code_frame, debugger=self.debugger)
        self.code.grid(column=0, row=1, sticky=(N, S, E, W))

        # Set up weights for the code frame's content
        self.code_frame.columnconfigure(0, weight=1)
        self.code_frame.rowconfigure(0, weight=0)
        self.code_frame.rowconfigure(1, weight=1)

        self.content.add(self.code_frame)

    def _setup_inspector(self):
        self.inspector_frame = Frame(self.content)
        self.inspector_frame.grid(column=2, row=0, sticky=(N, S, E, W))

        self.inspector = InspectorView(self.inspector_frame)
        self.inspector.grid(column=0, row=0, sticky=(N, S, E, W))

        # The tree's vertical scrollbar
        self.inspector_scrollbar = Scrollbar(self.inspector_frame, orient=VERTICAL)
        self.inspector_scrollbar.grid(column=1, row=0, sticky=(N, S))

        # Tie the scrollbar to the text views, and the text views
        # to each other.
        self.inspector.config(yscrollcommand=self.inspector_scrollbar.set)
        self.inspector_scrollbar.config(command=self.inspector.yview)

        # Setup weights for the "breakpoint list" tree
        self.inspector_frame.columnconfigure(0, weight=1)
        self.inspector_frame.columnconfigure(1, weight=0)
        self.inspector_frame.rowconfigure(0, weight=1)

        self.content.add(self.inspector_frame)

    def _setup_status_bar(self):
        # Status bar
        self.statusbar = Frame(self.root)
        self.statusbar.grid(column=0, row=2, sticky=(W, E))

        # Current status
        self.run_status = StringVar()
        self.run_status_label = Label(self.statusbar, textvariable=self.run_status)
        self.run_status_label.grid(column=0, row=0, sticky=(W, E))
        self.run_status.set('Not running')

        # Main window resize handle
        self.grip = Sizegrip(self.statusbar)
        self.grip.grid(column=1, row=0, sticky=(S, E))

        # Set up weights for status bar frame
        self.statusbar.columnconfigure(0, weight=1)
        self.statusbar.columnconfigure(1, weight=0)
        self.statusbar.rowconfigure(0, weight=0)

    ######################################################
    # Utility methods for controlling content
    ######################################################

    def show_file(self, filename, line=None, breakpoints=None):
        """Show the content of the nominated file.

        If specified, line is the current line number to highlight. If the
        line isn't currently visible, the window will be scrolled until it is.

        breakpoints is a list of line numbers that have current breakpoints.

        If refresh is true, the file will be reloaded and redrawn.
        """
        # Set the filename label for the current file
        if filename.startswith(self.base_path):
            self.current_file.set(filename[len(self.base_path):])
        else:
            self.current_file.set(filename)

        # Update the code view; this means changing the displayed file
        # if necessary, and updating the current line.
        if filename != self.code.filename:
            self.code.filename = filename
            for bp in self.debugger.breakpoints(filename).values():
                if bp.enabled:
                    self.code.enable_breakpoint(bp.line)
                else:
                    self.code.disable_breakpoint(bp.line)

        self.code.line = line

    ######################################################
    # TK Main loop
    ######################################################

    def mainloop(self):
        self.root.mainloop()

    ######################################################
    # TK Command handlers
    ######################################################

    def on_quit(self):
        "Quit the debugger"
        self.debugger.stop()
        self.root.quit()

    def cmd_run(self):
        ""
        self.debugger.do_run()

    def cmd_step(self):
        self.debugger.do_step()

    def cmd_next(self):
        self.debugger.do_next()

    def cmd_return(self):
        self.debugger.do_return()

    ######################################################
    # Handlers for GUI actions
    ######################################################

    def on_stack_frame_selected(self, event):
        "When a stack frame is selected, highlight the file and line"
        _, index = event.widget.selection()[0].split(':')
        line, frame = self.debugger.stack[int(index)]
        self.show_file(filename=frame['filename'], line=line)

    def on_breakpoint_selected(self, event):
        "When a breakpoint on the tree has been selected, show the breakpoint"
        parts = event.widget.focus().split(':')
        bp = self.debugger.breakpoint((parts[0], int(parts[1])))
        self.show_file(filename=bp.filename, line=bp.line)

    def on_breakpoint_double_clicked(self, event):
        "When a breakpoint on the tree is double clicked, toggle it's status"
        parts = event.widget.focus().split(':')
        bp = self.debugger.breakpoint((parts[0], int(parts[1])))
        if bp.enabled:
            self.debugger.disable_breakpoint(bp)
        else:
            self.debugger.enable_breakpoint(bp)

    ######################################################
    # Handlers for debugger responses
    ######################################################

    def on_stack(self, stack):
        "A report of a new stack"
        # Update the stack list
        self.stack.update_stack(stack)

        if len(stack) > 0:
            # Update the display of the current file
            line = stack[-1][0]
            filename = stack[-1][1]['filename']
            self.show_file(filename=filename, line=line)

            # Select the current stack frame in the frame list
            self.stack.selection_set('frame:%s' % (len(stack) - 1))
        else:
            # No current frame (probably end of execution),
            # so clear the current line marker
            self.code.line = None

    def on_line(self, filename, line):
        "A single line of code has been executed"
        self.run_status.set('Line (%s:%s)' % (filename, line))

    def on_call(self, args):
        "A callable has been invoked"
        self.run_status.set('Call: %s' % args)

    def on_return(self, retval):
        "A callable has returned"
        self.run_status.set('Return: %s' % retval)

    def on_exception(self, **kwargs):
        "An exception has been raised"
        print "EXCEPTION FOUND"
        print kwargs
        self.run_status.set('Exception')

    def on_restart(self):
        "The code has finished running, and will start again"
        self.run_status.set('Not running')
        tkMessageBox.showinfo(message='Program has finished, and will restart.')

    def on_info(self, message):
        "The debugger needs to inform the user of something"
        tkMessageBox.showinfo(message=message)

    def on_warning(self, message):
        "The debugger needs to warn the user of something"
        tkMessageBox.showwarning(message=message)

    def on_error(self, message):
        "The debugger needs to report an error"
        tkMessageBox.showerror(message=message)

    def on_breakpoint_enable(self, bp):
        "A breakpoint has been enabled in the debugger"
        # If the breakpoint is in the currently displayed file, updated
        # the display of the breakpoint.
        if bp.filename == self.code.filename:
            self.code.enable_breakpoint(bp.line, temporary=bp.temporary)

        # ... then update the display of the breakpoint on the tree
        self.breakpoint_list.update_breakpoint(bp)

    def on_breakpoint_disable(self, bp):
        "A breakpoint has been disabled in the debugger"
        # If the breakpoint is in the currently displayed file, updated
        # the display of the breakpoint.
        if bp.filename == self.code.filename:
            self.code.disable_breakpoint(bp.line)

        # ... then update the display of the breakpoint on the tree
        self.breakpoint_list.update_breakpoint(bp)

    def on_breakpoint_ignore(self, bp, count):
        "A breakpoint has been ignored by the debugger"
        # If the breakpoint is in the currently displayed file, updated
        # the display of the breakpoint.
        if bp.filename == self.code.filename:
            self.code.ignore_breakpoint(bp.line)

        # ... then update the display of the breakpoint on the tree
        self.breakpoint_list.update_breakpoint(bp)

    def on_breakpoint_clear(self, bp):
        "A breakpoint has been cleared in the debugger"
        # If the breakpoint is in the currently displayed file, updated
        # the display of the breakpoint.
        if bp.filename == self.code.filename:
            self.code.clear_breakpoint(bp.line)

        # ... then update the display of the breakpoint on the tree
        self.breakpoint_list.update_breakpoint(bp)
