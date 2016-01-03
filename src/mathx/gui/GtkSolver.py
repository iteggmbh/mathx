'''
Created on 20.12.2015

@author: michi
'''

from gi.repository import Gtk, Gdk
from mathx import solver, formula
from mathx.gui.AstTree import ast  # @UnusedImport
import os

class Window(Gtk.Window):
    def __init__(self,g=None):
        
        self.fullscreen_bool = False
        
        cssProvider = Gtk.CssProvider()
        filename = os.path.dirname(__file__)
        filename = os.path.join(filename,"redgreen.css")
        cssProvider.load_from_path(filename)
        screen = Gdk.Screen.get_default()
        styleContext = Gtk.StyleContext()
        styleContext.add_provider_for_screen(screen, cssProvider,
                                             Gtk.STYLE_PROVIDER_PRIORITY_USER)
        
        if g is not None:
            self.gleichungslöser = solver.Solver(g)
        else:
            self.gleichungslöser = None
        
        Gtk.Window.__init__(self,title="solver")
        
        self.connect("key-press-event", self.on_key_press)
        
        self.grid = Gtk.Grid()
        
        self.lhs_Entry = Gtk.Entry(hexpand=True)
        if self.gleichungslöser is not None:
            self.lhs_Entry.set_text(str(self.gleichungslöser.lhs))
        self.lhs_Entry.connect("notify::text",self.on_gleichung_changed)
        self.grid.attach(self.lhs_Entry,1,1,1,1)
        self.lhs_ScrolledWindow = Gtk.ScrolledWindow(hexpand=True,vexpand=True)
        self.lhs_TreeView = Gtk.TreeView()
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("lhs", renderer, text=0)
        self.lhs_TreeView.append_column(column)
        self.lhs_ScrolledWindow.add(self.lhs_TreeView)
        self.grid.attach(self.lhs_ScrolledWindow,1,2,1,1)
        
        self.separator = Gtk.Label(label=" = ")
        self.grid.attach(self.separator,2,1,1,2)
        
        self.rhs_Entry = Gtk.Entry(hexpand=True)
        
        if self.gleichungslöser is not None:
            self.rhs_Entry.set_text(str(self.gleichungslöser.rhs))
        self.rhs_Entry.connect("notify::text",self.on_gleichung_changed)
        self.grid.attach(self.rhs_Entry,3,1,1,1)
        self.rhs_ScrolledWindow = Gtk.ScrolledWindow(hexpand=True,vexpand=True)
        self.rhs_TreeView = Gtk.TreeView()
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("rhs", renderer, text=0)
        self.rhs_TreeView.append_column(column)
        self.rhs_ScrolledWindow.add(self.rhs_TreeView)
        self.grid.attach(self.rhs_ScrolledWindow,3,2,1,1)
        
        self.varsgrid = Gtk.Grid()
        self.grid.attach(self.varsgrid,1,3,3,1)
        
        self.add(self.grid)
        
        self.fillTree()
    def on_key_press(self,target,event):
        mod = Gtk.accelerator_get_label(event.keyval, event.state)
        if mod=="F11":
            if self.fullscreen_bool:
                self.unfullscreen()
            else:
                self.fullscreen()
            self.fullscreen_bool = not self.fullscreen_bool
    def on_gleichung_changed(self,target,param):
        try:
            lhs = formula.Parser(self.lhs_Entry.get_text()).parseAst()
            
        except:
            self.lhs_Entry.get_style_context().add_class("red")
            lhs = self.gleichungslöser.lhs
        else:
            try:
                self.lhs_Entry.get_style_context().remove_class("red")
                #self.rhs_Entry.get_style_context().remove_class("red")
            except:
                pass
        try:
            rhs = formula.Parser(self.rhs_Entry.get_text()).parseAst()
            
        except:
            self.rhs_Entry.get_style_context().add_class("red")
            rhs = self.gleichungslöser.rhs
        else:
            try:
                #self.lhs_Entry.get_style_context().remove_class("red")
                self.rhs_Entry.get_style_context().remove_class("red")
            except:
                pass
            
        self.gleichungslöser = solver.AstSolver(lhs, rhs)
        self.fillTree()
        self.grid.remove(self.varsgrid)
        self.varsgrid = Gtk.Grid()
        vvars = self.gleichungslöser.evaluate()
        for (i,(var,value)) in enumerate(vvars.items()):
            self.varsgrid.attach(Gtk.Label(label="%s=%s"%(var,value)),1,i+1,1,1)
        self.grid.attach(self.varsgrid,1,3,3,1)
        self.show_all()
    def fillTree(self):
        if self.gleichungslöser is not None:
            treeStore = Gtk.TreeStore(str)
            self.gleichungslöser.lhs.fillTree(treeStore)
            self.lhs_TreeView.set_model(treeStore)
            self.lhs_TreeView.expand_all()
            treeStore = Gtk.TreeStore(str)
            self.gleichungslöser.rhs.fillTree(treeStore)
            self.rhs_TreeView.set_model(treeStore)
            self.rhs_TreeView.expand_all()
            self.show_all()
if __name__ == '__main__':
    win = Window("1=1")
    win.connect("destroy",Gtk.main_quit)
    win.show_all()
    Gtk.main()
