'''
Created on 24.12.2015

@author: michi
'''

from gi.repository import Gtk, Gdk
import math

class FormulaCanvas(Gtk.Misc):
    
    def __init__(self,func=None,xmin=-1.0,xmax=1.0,ymin=-1.0,ymax=1.0,**props):
        Gtk.Misc.__init__(self,**props)

        self.func = func
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.press_position = None
        
        self.tick_length = 5
        self.label_distance = 25
        self.label_font_size = 10
        self.label_font = "Consolas"
        
        self.add_events(Gdk.EventMask.BUTTON1_MOTION_MASK)
        self.add_events(Gdk.EventMask.SCROLL_MASK)
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK)
        
        self.connect("button-release-event", self.on_button_release)
        self.connect("button-press-event", self.on_button_press)
        self.connect("scroll-event", self.on_scroll)
        self.connect("motion-notify-event", self.on_mouse_move)

    def _scale_to_world_x(self,alloc,di):
        return di/(alloc.width-1)*(self.xmax-self.xmin)
    
    def _scale_to_world_y(self,alloc,dj):
        return dj/(alloc.height-1)*(self.ymin-self.ymax)

    def _scale_to_world(self,alloc,di,dj):
        return (self._scale_to_world_x(alloc, di),self._scale_to_world_y(alloc,dj))

    def _to_world_x(self,alloc,i):
        return self.xmin+i/(alloc.width-1)*(self.xmax-self.xmin)
    
    def _to_world_y(self,alloc,j):
        return self.ymax-j/(alloc.height-1)*(self.ymax-self.ymin)

    def _to_world(self,alloc,i,j):
        return (self._to_world_x(alloc, i),self._to_world_y(alloc, j))

    def _scale_to_screen_x(self,alloc,dx):
        return (alloc.width-1)*dx.real/(self.xmax-self.xmin)
    
    def _scale_to_screen_y(self,alloc,dy):
        return (alloc.height-1)*dy.real/(self.ymin-self.ymax)
    
    def _scale_to_screen(self,alloc,dx,dy):
        return (self._scale_to_screen_x(alloc,dx),
                self._scale_to_screen_y(alloc,dy))

    def _to_screen_x(self,alloc,x):
        return (alloc.width-1)*(x.real-self.xmin)/(self.xmax-self.xmin)
        
    def _to_screen_y(self,alloc,y):
        return (alloc.height-1)*(self.ymax-y.real)/(self.ymax-self.ymin)

    def _to_screen(self,alloc,x,y):
        return (self._to_screen_x(alloc,x),self._to_screen_y(alloc,y))

    def on_button_release(self,target,event):
        
        self.press_position = None
        
    def on_button_press(self,target,event):
        
        #print("on_button_press(%r,%r,%r)"%(self,target,event))
        
        self.press_position = (event.x,event.y,self.xmin,self.ymin,self.xmax,self.ymax)
        
    def on_scroll(self,target,event):
        
        #print("on_scroll(%d,%d,%s,%lf,%lf)"%(event.x,event.y,event.direction,event.delta_x,event.delta_y))
        
        alloc = self.get_allocation()
        
        xc,yc = self._to_world(alloc,event.x,event.y)
        
        fac = 1.1 if event.direction == Gdk.ScrollDirection.DOWN else 1/1.1
        
        self.xmin = xc - (xc-self.xmin) * fac
        self.xmax = xc + (self.xmax-xc) * fac
        self.ymin = yc - (yc-self.ymin) * fac
        self.ymax = yc + (self.ymax-yc) * fac
        self.queue_draw()
    
    def on_mouse_move(self,target,event):
        
        #print("on_mouse_move(%r,%r,%r)"%(self,target,event))
        
        if self.press_position is None:
            return
        
        alloc = self.get_allocation()
        
        dx,dy = self._scale_to_world(alloc,event.x-self.press_position[0],event.y-self.press_position[1])
        
        self.xmin = self.press_position[2]-dx
        self.ymin = self.press_position[3]-dy
        self.xmax = self.press_position[4]-dx
        self.ymax = self.press_position[5]-dy
        
        self.queue_draw()
    
    def _get_axis_range(self,vmin,vmax,screen_size):
        
        fac = (vmax-vmin)/(screen_size-1)
        
        distance = self.label_distance * fac
        
        log_distance = math.log10(distance)
        
        floor_log_distance = math.floor(log_distance)
        
        d_log_distance = log_distance - floor_log_distance
        
        if d_log_distance == 0.0:
            delta = 10.0 ** floor_log_distance
            
        elif d_log_distance <= math.log10(2.0):
            delta = 2 * 10.0 ** floor_log_distance
            
        elif d_log_distance <= math.log10(5.0):
            delta = 5 * 10.0 ** floor_log_distance
        
        else:
            delta = 10.0 ** (floor_log_distance+1)
        
        return (range(math.ceil(vmin/delta),math.floor(vmax/delta)+1),delta)
    
    def _get_x_axis_range(self,alloc):
        return self._get_axis_range(self.xmin,self.xmax,alloc.width)
    
    def _get_y_axis_range(self,alloc):
        return self._get_axis_range(self.ymin,self.ymax,alloc.height)
    
    
    def _draw_label(self,cr,i,j,d,direction,value):
        
        value_s = "%.6g"%value
        
        # x_bearing, y_bearing, width, height, x_advance, y_advance
        extents = cr.text_extents(value_s)
        
        if direction == Gtk.DirectionType.RIGHT:
            xp = i+d
            yp = j + 0.5 * extents[3]
            
        elif direction == Gtk.DirectionType.LEFT:
            xp = i-d-extents[2]
            yp = j + 0.5 * extents[3]
            
        elif direction == Gtk.DirectionType.UP:
            xp = i-0.5*extents[2]
            yp = j - d
        
        elif direction == Gtk.DirectionType.DOWN:
            xp = i-0.5*extents[2]
            yp = j + d + extents[3]
        
        else:
            raise AssertionError("Unsupported direction %r"%direction)
        
        cr.move_to(xp,yp)
        cr.show_text(value_s)
        
        
    def _draw_x_axis(self,cr,alloc,j,direction):
        
        ixr,delta = self._get_x_axis_range(alloc)
        
        dj = self.tick_length
        
        if direction == Gtk.DirectionType.UP:
            dj *= -1.0
        
        for ix in ixr:
        
            x = ix * delta
            i = self._to_screen_x(alloc,x)
            cr.move_to(i,j)
            cr.rel_line_to(0,dj)
            cr.stroke()
            self._draw_label(cr,i,j,self.tick_length,direction,x)
        
    def _draw_y_axis(self,cr,alloc,i,direction):
        
        iyr,delta = self._get_y_axis_range(alloc)
        
        di = self.tick_length
        
        if direction == Gtk.DirectionType.LEFT:
            di *= -1.0
        
        for iy in iyr:
            
            y = iy * delta
            j = self._to_screen_y(alloc,y)
            cr.move_to(i,j)
            cr.rel_line_to(di,0)
            cr.stroke()
            self._draw_label(cr,i,j,self.tick_length,direction,y)
        
        
    def do_draw(self,cr):
        
        if self.func == None:
            return
        
        alloc = self.get_allocation()
                
        cr.save()
        try:
        
            #matrix = cairo.Matrix(alloc.width/(self.xmax-self.xmin),0,0,alloc.hight/(self.ymin-self.ymax),  # @UndefinedVariable
            #                      self.xmin*alloc.width/(self.xmin-self.xmax),
            #                      self.ymax*alloc.width/(self.ymax-self.ymin))
            #cr.transform (matrix)
            
            cr.set_source_rgb(1.0,1.0,1.0)
            cr.rectangle(0,0,alloc.width,alloc.height)
            cr.fill()
            
            cr.set_source_rgb(0.0,0.0,0.0)

            cr.set_line_width(1.0)
            self._draw_x_axis(cr,alloc,0,Gtk.DirectionType.DOWN)
            self._draw_x_axis(cr,alloc,alloc.height-1,Gtk.DirectionType.UP)
            self._draw_y_axis(cr,alloc,0,Gtk.DirectionType.RIGHT)
            self._draw_y_axis(cr,alloc,alloc.width-1,Gtk.DirectionType.LEFT)
            
            cr.set_line_width(2.0)
            
            path_open = False

            for i in range(alloc.width):
                
                x = self._to_world_x(alloc,i)
                
                try:
                    y = self.func(x)
                except:
                    y = None
                
                if y == None or math.isnan(y.real) or math.isinf(y.real):
                    
                    if path_open:
                        cr.stroke()
                        path_open = False
                else:
                    
                    j = self._to_screen_y(alloc,y)
                    
                    if path_open:
                        cr.line_to(i,j)
                    else:
                        cr.move_to(i,j)
                        path_open = True
            
            if path_open:
                cr.stroke()
                
        finally:
            cr.restore()
