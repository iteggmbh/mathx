'''
Created on 28.10.2015

@author: michi
'''

from mathx import ast
from mathx import formula
from mathx.gui import widgets
from gi.repository import Gtk
from copy import deepcopy

def extension(clazz):
    def inner_decorator(func):
        setattr(clazz,func.__name__,func)
        return func
    return inner_decorator

@extension(ast.AstBinaryOperator)
def fillTree(self,treeStore,iterv=None):
    iterv2 = treeStore.append(iterv,[self.op])
    self.lhs.fillTree(treeStore,iterv2)
    self.rhs.fillTree(treeStore,iterv2)

@extension(ast.AstConstant)
def fillTree(self,treeStore,iterv=None):  # @DuplicatedSignature
    treeStore.append(iterv,[str(self)])

@extension(ast.AstVariable)
def fillTree(self,treeStore,iterv=None):  # @DuplicatedSignature
    treeStore.append(iterv,[self.variable])

@extension(ast.AstNegation)
def fillTree(self,treeStore,iterv=None):  # @DuplicatedSignature
    iterv2 = treeStore.append(iterv,["-"])
    self.target.fillTree(treeStore,iterv2)

@extension(ast.AstFunctionCall)
def fillTree(self,treeStore,iterv=None):  # @DuplicatedSignature
    iterv2 = treeStore.append(iterv,[self.func])
    self.target.fillTree(treeStore,iterv2)

@extension(ast.AstRoot)
def fillTree(self,treeStore,iterv=None):  # @DuplicatedSignature
    iterv2 = treeStore.append(iterv,["root"])
    self.power.fillTree(treeStore,iterv2)
    self.target.fillTree(treeStore,iterv2)


def fillTree_from_searchPath(searchPath,treeStore,iterv=None):
    for i1,i2 in enumerate(searchPath):
        if type(i2)!=tuple:
            try:
                iterv2  # @UndefinedVariable
            except NameError:
                iterv2 = treeStore.append(iterv,[str(i2)])
            else:
                iterv2 = treeStore.append(iterv2,[str(i2)])
        else:
            for i in searchPath[i1]:
                fillTree_from_searchPath(i, treeStore, iterv2)

class AstWidget(Gtk.Grid):
    def __init__(self,astv,title="formula"):
        Gtk.Grid.__init__(self)
        
        self.formula_entry = Gtk.Entry(hexpand=True)
        self.formula_entry.connect("notify::text",self.formula_changed)
        self.attach(self.formula_entry,1,1,1,1)
        
        self.formula_label = Gtk.Label()
        self.attach(self.formula_label,2,1,1,1)
        
        self.scroll = Gtk.ScrolledWindow(hexpand=True,vexpand=True)
        
        treeStore = Gtk.TreeStore(str)
        self.treeView = Gtk.TreeView.new_with_model(treeStore)
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(title, renderer, text=0)
        self.treeView.append_column(column)
        self.scroll.add(self.treeView)
        self.attach(self.scroll,1,2,2,1)
class Window(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self,title="formula")
        
        self.hb = Gtk.HeaderBar(title=self.get_title())
        self.hb.set_show_close_button(True)
        self.set_titlebar(self.hb)
        
        self.menu1 = Gtk.Menu()
        d = {"Simplify":self.simplify_clicked,
             "count":self.count_clicked,
             "SearchPath":self.searchPath_clicked}
        for i in sorted(d.keys()):
            item = Gtk.MenuItem(label=i)
            self.menu1.append(item)
            item.connect("activate",d[i])
        self.menu1.show_all()
        self.menubutton = Gtk.MenuButton(popup=self.menu1)
        self.hb.pack_end(self.menubutton)
        
        #self.paned = Gtk.Paned(Gtk.Orientation.VERTICAL)
        self.paned = Gtk.Paned()
        
        self.grid = Gtk.Grid()
        self.formula_entry = Gtk.Entry(hexpand=True)
        self.formula_entry.connect("notify::text",self.formula_changed)
        self.grid.attach(self.formula_entry,1,1,1,1)
        
        self.formula_label = Gtk.Label()
        self.grid.attach(self.formula_label,2,1,1,1)
        
        self.scroll = Gtk.ScrolledWindow(hexpand=True,vexpand=True)
        
        treeStore = Gtk.TreeStore(str)
        self.treeView = Gtk.TreeView.new_with_model(treeStore.filter_new())
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("formula", renderer, text=0)
        self.treeView.append_column(column)
        self.scroll.add(self.treeView)
        self.grid.attach(self.scroll,1,2,2,1)
        
        self.paned.add1(self.grid)
        
        self.formulacanvas = widgets.FormulaCanvas(hexpand=True,vexpand=True)
        self.paned.add2(self.formulacanvas)
        
        self.vars = {}
        self.var_to_entries = {}
        self.entries_to_var = {}
        self.varsgrid = Gtk.Grid()
        
        self.add(self.paned)
    def searchPath_clicked(self,event):
        fp = formula.Parser(self.formula_entry.get_text())
        win3 = searchPathwindow(fp.parseAst())
        win3.connect("destroy",Gtk.main_quit)
        win3.show_all()
        Gtk.main()
    def _show(self,node):
        self._show_tree(node)
        self._show_canvas(node)
    def _show_canvas(self,node):
        
        if len(self.vars)==1:
            var = list(self.vars.keys())[0]
            self.formulacanvas.func = lambda x:(node.evaluate({var:x}))
            self.formulacanvas.queue_draw()
        
    def _show_tree(self,node):
        treeStore = Gtk.TreeStore(str)
        node.fillTree(treeStore)
        self.treeView.set_model(treeStore)
        self.show_all()
        self.treeView.expand_all()

    def simplify_clicked(self,event):
        parser = formula.Parser(self.formula_entry.get_text())
        try:
            node = parser.parseAst()
        except:
            return
        
        node = node.simplify()
        self.formula_entry.set_text(str(node))
        self._show(node)
    def count_clicked(self,event):
        fp = formula.Parser(self.formula_entry.get_text())
        win2 = countwindow(fp.parseAst())
        win2.connect("destroy",Gtk.main_quit)
        win2.show_all()
        Gtk.main()
        
    def formula_changed(self,target,param):
        parser = formula.Parser(self.formula_entry.get_text())
        try:
            node = parser.parseAst()
        except:
            return
        
        old_vars = deepcopy(self.vars)
        self.vars.clear()
        node.findVars(self.vars)
        
        self.grid.remove(self.varsgrid)
        self.varsgrid = Gtk.Grid()
        l = list(self.vars.keys())
        self.var_to_entries = dict(zip(l,[Gtk.Entry(hexpand=True) for i in l]))
        self.entries_to_var.clear()
        for i,(var,entry) in enumerate(self.var_to_entries.items()):
            self.varsgrid.attach(Gtk.Label(var+":"),1,i,1,1)
            self.entries_to_var[entry] = var
            if var in old_vars and (old_vars[var] is not None):
                entry.set_text(str(old_vars[var]))
            entry.connect("notify::text",self.var_changed,node)
            self.varsgrid.attach(entry,2,i,1,1)
        self.grid.attach(self.varsgrid,1,3,2,1)
        
        if len(self.vars)==0:
            f = node.evaluate()
            if isinstance(f, (float,int)):
                if f%1!=0:
                    self.formula_label.set_label("=%s"%f)
                else:
                    self.formula_label.set_label("=%s"%int(f))
            else:
                self.formula_label.set_label("=%s"%f)
        
        self._show(node)
        
        
    def var_changed(self,target,param,node):
        fopa = formula.Parser(target.get_text())
        try:
            i = fopa.evaluate()
        except:
            pass
        else:
            self.vars[self.entries_to_var[target]] = i
        if list(self.vars.values()).count(None)==0:
            f = node.evaluate(self.vars)
            if isinstance(f, (float,int)):
                if f%1!=0:
                    self.formula_label.set_label("=%s"%f)
                else:
                    self.formula_label.set_label("=%s"%int(f))
            else:
                self.formula_label.set_label("=%s"%f)
class searchPathwindow(Gtk.Window):
    def __init__(self,node):
        print(str(node))
        self.node=node
        
        Gtk.Window.__init__(self,title="searchPath",resizable=False)
        
        self.grid = Gtk.Grid()
        
        self.astentry = Gtk.Entry()
        self.grid.attach(self.astentry,1,1,1,1)
        
        self.okbutton = Gtk.Button(label="searchPath")
        self.okbutton.connect("clicked",self.okbutton_clicked)
        self.grid.attach(self.okbutton,1,2,1,1)
        
        self.add(self.grid)
    def okbutton_clicked(self,event):
        #print(self.astentry.get_text())
        p = formula.Parser(formula=self.astentry.get_text())
        print(type(p.formula),p.formula,dir(p.formula),sep="\n")
        ast = p.parseAst()
        searchPath = self.node.searchPath(ast)
        self.destroy()
        mywin = Gtk.Window()
        treeStore = Gtk.TreeStore(str)
        fillTree_from_searchPath(searchPath, treeStore)
        treeView = Gtk.TreeView.new_with_model(treeStore)
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("searchPath", renderer, text=0)
        treeView.append_column(column)
        mywin.add(treeView)
        mywin.connect("destroy",Gtk.main_quit)
        mywin.show_all()
        Gtk.main()
        
class countwindow(Gtk.Window):
    def __init__(self,node):
        self.node = node
        self.filter = ast.AstBinaryOperator
        
        Gtk.Window.__init__(self,title="count",resizable=False)
        
        self.grid = Gtk.Grid()
        
        self.radioOperator = Gtk.CheckButton("Operator",active=True)
        self.radioConstant = Gtk.CheckButton("Constant",active=False)
        self.radioFunctionCall = Gtk.CheckButton("FunctionCall",active=False)
        self.radioNegation = Gtk.CheckButton("Negation",active=False)
        self.radioVariable = Gtk.CheckButton("Variable",active=False)
        
        self.radios = [self.radioOperator,self.radioConstant,self.radioFunctionCall,self.radioNegation,self.radioVariable]
        
        self.grid.attach(self.radioOperator,1,1,1,1)
        self.grid.attach(self.radioConstant,1,2,1,1)
        self.grid.attach(self.radioFunctionCall,1,3,1,1)
        self.grid.attach(self.radioNegation,1,4,1,1)
        self.grid.attach(self.radioVariable,1,5,1,1)
        
        self.radioOperator.connect("toggled",self.radio_toggled,ast.AstBinaryOperator)
        self.radioConstant.connect("toggled",self.radio_toggled,ast.AstConstant)
        self.radioFunctionCall.connect("toggled",self.radio_toggled,ast.AstFunctionCall)
        self.radioNegation.connect("toggled",self.radio_toggled,ast.AstNegation)
        self.radioVariable.connect("toggled",self.radio_toggled,ast.AstVariable)
        
        self.ok_button = Gtk.Button(label="count")
        self.ok_button.connect("clicked",self.on_ok_button_clicked)
        self.grid.attach(self.ok_button,1,6,1,1)
        
        self.add(self.grid)
    def radio_toggled(self,target,ast):
        if target.get_active():
            self.filter = ast
            for i in self.radios:
                if i!=target:
                    i.set_active(False)
        else:
            if not (self.radioOperator.get_active()) and not(self.radioConstant.get_active()) and not(self.radioFunctionCall.get_active()) and not(self.radioNegation.get_active()) and not(self.radioVariable.get_active()):
                target.set_active(True)
        
    def on_ok_button_clicked(self,event):
        self.destroy()
        print(self.node.count(self.filter))
        
if __name__ == '__main__':
    win = Window()
    win.connect("destroy",Gtk.main_quit)
    win.show_all()
    Gtk.main()
    