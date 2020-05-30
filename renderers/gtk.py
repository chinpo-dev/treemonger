import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
#import cairo

from .colormap_rgb import colormap
from constants import (text_size,
                       text_offset_x,
                       text_offset_y,
                       )


#class Demo1:
#    def __init__(self, master):
#        self.master = master
#        self.frame = tk.Frame(self.master)
#        self.button1 = tk.Button(self.frame, text='null', width=25, command=self.new_window)
#        self.button1.pack()
#        self.frame.pack()
#
#    def new_window(self):
#        pass

class TreemongerApp(object):
    def __init__(self, master, width, height, title, tree, compute_func):
        self.master = master
        self.tree = tree
        self.compute_func = compute_func
        self.width = width
        self.height = height

        #screen_width = master.winfo_screenwidth()
        #screen_height = master.winfo_screenheight()
        #x = (screen_width / 2) - (width / 2)  # default window x position (centered)
        #y = (screen_height / 2) - (height / 2)  # default window y position (centered)
        #master.geometry('%dx%d+%d+%d' % (width, height, x, y))
        master.set_title(title)

        self.darea = Gtk.DrawingArea()
        self.darea.connect("draw", self.render)
        #self.cr = self.darea.get_property("window").cairo_create()

        master.add(self.darea)
        master.show_all()
        #self.root_rect = self.cr.rectangle(0, 0, 0, 0, width=1,
        #                                   fill="white", outline='black')
        #self.canv.bind("<Configure>", self.on_resize)
        #self.canv.bind("<Button-1>", self.on_click1)

    #def shape_text(self, extents, dx, dy):

    def render(self, widget, cr, width=None, height=None):
        #width = width or self.width
        #height = height or self.height
        width = widget.get_allocated_width()
        height = widget.get_allocated_height()
        #cr.set_operator(cairo.OPERATOR_CLEAR)
        #cr.paint()
        #cr.set_operator(cairo.OPERATOR_OVER)
        #cr.set_source_rgb(1, 1, 0)
        #cr.rectangle(0, 0, width, height)
        #cr.fill()
        print('rendering %dx%d' % (width, height))
        self.rects = self.compute_func(self.tree, [0, width], [0, height])
        for rect in self.rects:
            x = rect['x']
            y = rect['y']
            dx = rect['dx']
            dy = rect['dy']
            d = rect['depth']
            d = d % len(colormap)
            cs = colormap[d]

            cr.save()
            cr.rectangle(x, y, dx, dy)
            cr.set_source_rgb(0, 0, 0)
            cr.stroke()
            cr.rectangle(x, y, dx, dy)
            cr.set_source_rgb(cs[0][0], cs[0][1], cs[0][2])
            cr.fill()
            cr.rectangle(x, y, dx, dy)
            cr.clip()
            # self.canv.create_line(x, y+dy, x, y, x+dx, y, fill=cs[1])
            # self.canv.create_line(x, y+dy, x+dx, y+dy, x+dx, y, fill=cs[2])

            extents = cr.text_extents(rect['text'])
            if rect['type'] == 'directory':
                text_x = x + text_offset_x
                text_y = y + extents.height
            elif rect['type'] == 'file':
                #self.shape_text(cr.text_extents(rect['text']), dx, dy)
                if extents.width > dx:
                    text_x = x
                else:
                    text_x = x + dx / 2 - extents.width/2
                text_y = y + dy / 2
            cr.move_to(text_x, text_y)
            cr.set_source_rgb(0, 0, 0)
       	    #cr.select_font_face("Helvetica");
            #cr.set_font_size(text_size)
            cr.show_text(rect['text'])
            cr.restore()


    def on_click1(self, ev):
        print('left clicked: (%d, %d), (%d, %d)' %
              (ev.x, ev.y, ev.x_root, ev.y_root))

    def on_resize(self, ev):
        print('resized: %d %d' % (ev.width, ev.height))
        #widget.get_window().invalidate_rect(widget.get_allocation(), False)
        # self.canv.coords(self.root_rect, 1, 1, ev.width - 2, ev.height - 2)
        #self.render(ev.width, ev.height)


def render_class(tree, compute_func, width, height, title):
    """
    similar to render_class, but accepts the original tree rather than the computed rectangles
    this allows recalculation on resize etc
    """
    root = Gtk.Window()
    app = TreemongerApp(root, width, height, title, tree, compute_func)
    #app.render()
    Gtk.main()

def on_resize(ev):
    # canv.coords(line,0,0,ev.width,ev.height)

    print('resized: %d %d' % (ev.width, ev.height))

    # canv.coords(rect1, 1, 1, ev.width - 2, ev.height - 2)
    # render(t, canv, [3, ev.width - 4], [3, ev.height - 4])


def init(title, width, height):
    root = tk.Tk()

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width / 2) - (width / 2)  # default window x position (centered)
    y = (screen_height / 2) - (height / 2)  # default window y position (centered)
    root.geometry('%dx%d+%d+%d' % (width, height, x, y))

    root.title(title)

    # not sure if w and h do anything here
    # canv = tk.Canvas(root, width=w, height=h, bg='black')
    canv = tk.Canvas(root, bg='black')
    # canv = Canvas(root, bg = 'black')
    canv.pack(expand=True, fill=tk.BOTH)  # ?
    # canv.grid(row=0, column=0, columnspan=3);
    rect1 = canv.create_rectangle(
        0, 0, 0, 0, width=1, fill="white", outline='black')
    canv.bind("<Configure>", on_resize)
    # canv.bind("<Button-1>", on_click1)
    # canv.bind("<Button-2>", on_click2)
    # canv.bind("<Button-3>", on_click3)
    # canv.bind("<Button-4>", on_click4)
    # canv.bind("<Button-5>", on_click5)
    # root.bind("<KeyPress>", on_keydown)
    # root.bind("<KeyRelease>", on_keyup)

    return root, canv


def render_function(rects, width, height, title):
    # title = reverse_path(abspath(treepath))
    root, canv = init(title, width, height)
    print('%d rects' % len(rects))
    for rect in rects:
        x = rect['x']
        y = rect['y']
        dx = rect['dx']
        dy = rect['dy']
        d = rect['depth']
        d = d % len(colormap)
        cs = colormap[d]

        canv.create_rectangle(x, y, x+dx, y+dy, width=1, fill=cs[0], outline='black')
        canv.create_line(x, y+dy, x, y, x+dx, y, fill=cs[1])
        canv.create_line(x, y+dy, x+dx, y+dy, x+dx, y, fill=cs[2])

        if rect['type'] == 'directory':
            text_x = x + text_offset_x 
            text_y = y + text_offset_y
        elif rect['type'] == 'file':
            text_x = x + dx / 2
            text_y = y + dy / 2

        canv.create_text(text_x, text_y, text=rect['text'], fill="black",
                         anchor=tk.NW, font=("Helvectica", text_size))

    root.mainloop()
