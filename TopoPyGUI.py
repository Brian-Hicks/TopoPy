#!/usr/bin/env python3
#-*- coding: utf-8 -*-

# TopoPy GUI
#
# A Python-based topographic drawings software.
# This software is released under the Apache 2.0 License.
#
# Author: Johan Barthelemy
# Date: December 2015
# Version: 7

# TODO: if only 2 data point (x and y), then just draw a line, it is a part of a building (thicker line, colored?)
#       quite easy to do: try to read first the z coordinate, then if it is a letter, draw the convex hull of the (filled in black or dotted)
#       see http://stackoverflow.com/questions/21727199/python-convex-hull-with-scipy-spatial-delaunay-how-to-eleminate-points-inside-t
#       http://scipy.github.io/devdocs/generated/scipy.spatial.ConvexHull.html
# todo: print button directly in the interface, see http://stackoverflow.com/questions/12723818/print-to-standard-printer-from-python
#       and http://stackoverflow.com/questions/2316368/how-do-i-print-to-the-oss-default-printer-in-python-3-cross-platform
#       and http://timgolden.me.uk/python/win32_how_do_i/print.html
#       maybe need to switch to Qt ??? see http://www.blog.pythonlibrary.org/2013/04/16/pyside-standard-dialogs-and-message-boxes/
#                                      and http://stackoverflow.com/questions/18999602/error-printing-image-in-pyqt

## Import section
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as ml
import csv
import tkinter.messagebox
import tkinter as tk
import platform
from scipy.interpolate import griddata
from scipy.spatial import ConvexHull
from tkinter.filedialog import askopenfilename, asksaveasfilename
from matplotlib.patches import Polygon

## check if a given string represent a float
def isFloat(s):
    try: 
        float(s)
        return True
    except ValueError:
        return False

## a range function for float
def frange(x, y, jump):
    if (x < y) and (jump > 0):
        while x < y:
            yield x
            x += jump
    elif (x > y) and (jump < 0):
        while x > y:
            yield x
            x += jump
    else:
        return None

## AppTopoGui class - main class of the application
class AppTopoGui(tk.Frame):
    
    ## Constructor
    def __init__(self, parent):
        
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.parent.title('TopoPy')
        if platform.system() == 'Windows':
            self.parent.iconbitmap('application_edit.ico')
        
        self.listx  = []            # list of ids 
        self.listy  = []            # list containing the x coordinates of the points
        self.listz  = []            # list containing the y coordinates of the points
        self.listid = []            # list containing the z coordinates of the points
        
        self.bat  = dict()          # dict containing the list of the buildings points
        
        self.read_settings()        # reading the settings        
        self.read_trad()            # reading the traductions
        self.initialize_menu()      # initialize the menu interface
        self.load_trad_gui()        # settings the labels accordingly to the selected language
        self.initialize_gui()       # drawing the gui
        
    
    ## Reading the settings in the file settings.ini    
    def read_settings(self):
        
        self.settings = dict()      # dictionnary containing the settings
        
        try:
            with open('settings.ini','r') as csvfile:
                filereader = csv.reader(csvfile, delimiter = "=",quotechar = " " )
                for row in filereader:
                    self.settings[row[0]] = row[1]
        except IOError:
            print('Error: Could not open the file settings.ini!')
            tk.messagebox.showerror(parent=self, title='Error: could not read settings', message = 'Could not find settings.ini!')
            return None
            
        for s, v in self.settings.items():
            print('INFO: settings.ini:', s,'=', v)
        
        if 'lang' not in self.settings:
            print('Warning: no language defined in the configuration file! Selecting english as default.')
            self.settings['lang'] = 'en'
    
    ## Saving settings in the file settings.ini
    def saving_settings(self):
        
        print('INFO: Saving settings')
        
        try:
            with open('settings.ini','w') as file:
                for k, v in self.settings.items():
                    file.write(k + '=' + v + '\n')
        except IOError:
            print('Error: Could not write the settings in settings.ini!')
            tk.messagebox.showerror(parent=self, title='Error: could not save settings', message = 'Could not save the settings in settings.ini!')
            return None
            
    ## Load the traductions stores then in a dict trad[item][lang] = value
    def read_trad(self):
       
        self.traductions = dict()   # dictionnary containing the traductions
        
        # reading the traductions in a file
        try:
            with open('trad.txt', encoding = "ISO-8859-1") as csvfile:
                filereader = csv.reader(csvfile, delimiter = ";",quotechar = " ")                
                
                for row in filereader:
                    self.traductions[row[0]] = dict()
                    self.traductions[row[0]]['en'] = row[1]
                    self.traductions[row[0]]['fr'] = row[2]
        
        except IOError:
            print('Error: ould not open the file trad.txt');
            tk.messagebox.showerror(parent = self, title = 'Error: could not load the traductions', message = 'Could not either find trad.txt or file incomplete!')
            self.quit_app();
        
        # gui langage
        self.lang_choice = tk.StringVar()
        self.lang_choice.set(self.settings['lang'])
        
        # defining the labels of the interface
        self.loadButtonLabelTxt   = tk.StringVar()
        self.scaleLabelTxt        = tk.StringVar()
        self.dpiLabelTxt          = tk.StringVar()
        self.plotIdsLabelTxt      = tk.StringVar()
        self.yesLabelTxt          = tk.StringVar()
        self.noLabelTxt           = tk.StringVar()
        self.fontLabelTxt         = tk.StringVar()
        self.base_lLabelTxt       = tk.StringVar()
        self.delta_lLabelTxt      = tk.StringVar()
        self.extensionLabelTxt    = tk.StringVar()
        self.nxnyLabelTxt         = tk.StringVar()
        self.interpMethodLabelTxt = tk.StringVar()
        self.linearLabelTxt       = tk.StringVar()
        self.cubicLabelTxt        = tk.StringVar()
        self.drawButtonLabelTxt   = tk.StringVar()
        self.saveButtonLabelTxt   = tk.StringVar()
        self.quitButtonLabelTxt   = tk.StringVar()
        self.languageTxt          = tk.StringVar()

    ## loading the desired langage and updating the gui accordingly
    def load_trad_gui(self, *argv):
        
        # getting the current langage
        lang = self.lang_choice.get()
        print('INFO: Loading gui traduction - selected language:', lang)
        
        # setting the values
        self.loadButtonLabelTxt.set(self.traductions['load'][lang])
        self.scaleLabelTxt.set(self.traductions['scale'][lang])
        self.dpiLabelTxt.set(self.traductions['dpi'][lang])
        self.plotIdsLabelTxt.set(self.traductions['plotIds'][lang])
        self.yesLabelTxt.set(self.traductions['yes'][lang])
        self.noLabelTxt.set(self.traductions['no'][lang])
        self.fontLabelTxt.set(self.traductions['font'][lang])
        self.base_lLabelTxt.set(self.traductions['base_l'][lang])
        self.delta_lLabelTxt.set(self.traductions['delta_l'][lang])
        self.extensionLabelTxt.set(self.traductions['extension'][lang])
        self.nxnyLabelTxt.set(self.traductions['nxny'][lang])
        self.interpMethodLabelTxt.set(self.traductions['interpMethod'][lang])
        self.linearLabelTxt.set(self.traductions['linear'][lang])
        self.cubicLabelTxt.set(self.traductions['cubic'][lang])
        self.drawButtonLabelTxt.set(self.traductions['drawButton'][lang])
        self.saveButtonLabelTxt.set(self.traductions['saveButton'][lang])
        self.quitButtonLabelTxt.set(self.traductions['quitButton'][lang])
        self.languageTxt.set(self.traductions['language'][lang])
        
        self.menu.entryconfig(1, label = self.languageTxt.get())
        self.filemenu.entryconfig(3, label = self.quitButtonLabelTxt.get())
        
        # refresh the interface
        self.update()
        
        # saving settings
        self.settings['lang'] = lang
        self.saving_settings()
    
    def initialize_menu(self):
        
        # ... creating menu
        self.menu     = tk.Menu(self.parent)
        self.filemenu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label= self.languageTxt.get(), menu=self.filemenu)
        self.filemenu.add_radiobutton(label="English",  command = self.load_trad_gui, var = self.lang_choice, value = 'en')
        self.filemenu.add_radiobutton(label="Français", command = self.load_trad_gui, var = self.lang_choice, value = 'fr')
        self.filemenu.add_separator()
        self.filemenu.add_command(label=self.quitButtonLabelTxt.get(), command=self.quit_app)
        
        self.parent.config(menu=self.menu)
        
    ## Initialize the interface
    def initialize_gui(self):

        # layout manager
        self.grid()
        
        # ... creation load button
        self.loadButton = tk.Button(self, textvariable=self.loadButtonLabelTxt, command=self.load_file)
        self.loadButton.grid(column=0, row=0, columnspan=4, sticky='E'+'W')
                
        # ... create label for scale
        scaleLabel = tk.Label(self, textvariable=self.scaleLabelTxt, anchor="center")
        scaleLabel.grid(column=0, row=1, sticky='E')
        
        # ... create entry for scale
        self.scaleEntryVariable = tk.IntVar()
        self.scaleEntry = tk.Entry(self, textvariable=self.scaleEntryVariable)
        self.scaleEntry.grid(column=1, row=1, columnspan=3,sticky='E'+'W')
        self.scaleEntryVariable.set("200")
        
        # ... create label for image dpi
        dpiLabel = tk.Label(self, textvariable=self.dpiLabelTxt)
        dpiLabel.grid(column=0, row=2, sticky='E')
        
        # ... creating the radio buttons for selecting the image dpi
        self.dpiVar = tk.IntVar()
        tk.Radiobutton(self, text="150", padx = 20, variable=self.dpiVar, value=150).grid(column=1,row=2)
        tk.Radiobutton(self, text="300", padx = 20, variable=self.dpiVar, value=300).grid(column=2,row=2)
        tk.Radiobutton(self, text="600", padx = 20, variable=self.dpiVar, value=600).grid(column=3,row=2)
        self.dpiVar.set(600)
        
        # ... creation label plot ids
        plotIdsLabel = tk.Label(self, textvariable=self.plotIdsLabelTxt)
        plotIdsLabel.grid(column=0, row=3, sticky='E')
        
        # ... creating the radio buttons for showing/hiding points id
        self.plotId = tk.IntVar()
        tk.Radiobutton(self, textvariable=self.yesLabelTxt, padx = 20, variable=self.plotId, value=1).grid(column=1,row=3)
        tk.Radiobutton(self, textvariable=self.noLabelTxt,  padx = 20, variable=self.plotId, value=0).grid(column=2,row=3)
        
        # ... create label for font size
        fontLabel = tk.Label(self, textvariable=self.fontLabelTxt, anchor="center")
        fontLabel.grid(column=0, row=4, sticky='E')
        
        # ... create entry for font size
        self.fontEntryVariable = tk.IntVar()
        self.fontEntry = tk.Entry(self, textvariable=self.fontEntryVariable)
        self.fontEntry.grid(column=1, row=4, columnspan=3,sticky='E'+'W')
        self.fontEntryVariable.set("10")

        # ... create label for base contour line
        base_lLabel = tk.Label(self, textvariable=self.base_lLabelTxt, anchor="center")
        base_lLabel.grid(column=0, row=5, sticky='E')
        
        # ... create entry for base contour line
        self.base_lEntryVariable = tk.IntVar()
        self.base_lEntry = tk.Entry(self, textvariable=self.base_lEntryVariable)
        self.base_lEntry.grid(column=1, row=5, columnspan=3,sticky='E'+'W')
        self.base_lEntryVariable.set("100")

        # ... create label for delta_l
        delta_lLabel = tk.Label(self, textvariable=self.delta_lLabelTxt, anchor="center")
        delta_lLabel.grid(column=0, row=6, sticky='E')
        
        # ... create entry for delta_l
        self.delta_lEntryVariable = tk.DoubleVar()
        self.delta_lEntry = tk.Entry(self, textvariable=self.delta_lEntryVariable)
        self.delta_lEntry.grid(column=1, row=6, columnspan=3,sticky='E'+'W')
        self.delta_lEntryVariable.set("0.50")
        
        # ... create label for extension
        extensionLabel = tk.Label(self, textvariable=self.extensionLabelTxt, anchor="center")
        extensionLabel.grid(column=0, row=7, sticky='E')
        
        # ... create entry for extension
        self.extensionEntryVariable = tk.IntVar()
        self.extensionEntry = tk.Entry(self, textvariable=self.extensionEntryVariable)
        self.extensionEntry.grid(column=1, row=7, columnspan=3,sticky='E'+'W')
        self.extensionEntryVariable.set("2")

        # ... create label for nx x ny
        nxnyLabel = tk.Label(self, textvariable=self.nxnyLabelTxt, anchor="center")
        nxnyLabel.grid(column=0, row=8, sticky='E')
        nxny2Label = tk.Label(self, text=" x ", anchor="center")
        nxny2Label.grid(column=2, row=8, sticky='E'+'W')
        
        # ... create entry for nx
        self.nxEntryVariable = tk.IntVar()
        self.nxEntry = tk.Entry(self, textvariable=self.nxEntryVariable)
        self.nxEntry.grid(column=1, row=8, columnspan=1,sticky='E'+'W')
        self.nxEntryVariable.set("500")
        
        # ... create entry for ny
        self.nyEntryVariable = tk.IntVar()
        self.nyEntry = tk.Entry(self, textvariable=self.nyEntryVariable)
        self.nyEntry.grid(column=3, row=8, columnspan=1,sticky='E'+'W')
        self.nyEntryVariable.set("500")
        
        # ... creating the label for the interpolation method
        interpMethodLabel = tk.Label(self, textvariable=self.interpMethodLabelTxt, anchor="center")
        interpMethodLabel.grid(column=0, row=9, sticky='E')
        
        # ... creating the radio buttons for selecting the interpolation method
        self.interpMethodVar = tk.StringVar()
        tk.Radiobutton(self, textvariable=self.linearLabelTxt, padx = 20, variable=self.interpMethodVar, value="linear").grid(column=1,row=9)
        tk.Radiobutton(self, textvariable=self.cubicLabelTxt,  padx = 20, variable=self.interpMethodVar, value="cubic" ).grid(column=2,row=9)
        self.interpMethodVar.set("cubic")
        
        # ... creation draw button
        drawButton = tk.Button(self, textvariable=self.drawButtonLabelTxt, command=self.draw_map)
        drawButton.grid(column=0, row=10, columnspan=4, sticky='E'+'W')
                
        # ... creation save button
        saveButton = tk.Button(self, textvariable=self.saveButtonLabelTxt, command=self.save_map)
        saveButton.grid(column=0,row=11,columnspan=4,sticky='E'+'W')        
        
        # ... creation bouton quit
        quitButton = tk.Button(self, textvariable=self.quitButtonLabelTxt,command=self.quit_app)
        quitButton.grid(column=0,row=12,columnspan=4,sticky='E'+'W')
                
        # prevent resizing of the interface
        self.parent.resizable(False, False)
        
        # force the interface to be redraw (be certain that everything is there)
        self.update()
               
        # set the focus on the scale input field and already select the text
        self.scaleEntry.focus_set()
        self.scaleEntry.selection_range(0, tk.END)
       
    ## quitting the app
    def quit_app(self):
  
        plt.close('all')
        top=self.winfo_toplevel()
        top.quit()
        self.parent.destroy()
    
    ## clearing the data
    def clear_data(self):
        
        self.listid.clear()
        self.listx.clear()
        self.listy.clear()
        self.listz.clear()
        self.bat.clear()
    
    ## loading a map
    def load_file(self):
        
        # getting input file name and path
        self.csvfilename = askopenfilename();
        if(self.csvfilename == ''):
            return None
        
        print(self.csvfilename)
        
        # resetting data
        self.clear_data()
        
        # reading file
        with open(self.csvfilename,'r') as csvfile:
            filereader = csv.reader(csvfile, delimiter = "\t",quotechar = " ")
            for row in filereader:
                try:
                    if isFloat(row[3]):
                        self.listid.append(str(row[0]))
                        self.listx.append(float(row[1]))
                        self.listy.append(float(row[2]))
                        self.listz.append(float(row[3]))
                    else:
                        print("Reading a batiment point!")                        
                        if row[3] not in self.bat:
                            self.bat[row[3]] = list()
                        self.bat[row[3]].append( [float(row[1]), float(row[2])] )
                    
                except:
                    self.clear_data()
                    print('Error while reading input file... maybe something wrong with it?')
                    tk.messagebox.showerror(parent=self, title='Error while reading input file', message = 'Maybe something is wrong with the input file?')
                    return None
    
    ## drawing the current map
    def draw_map(self):
        
        if not self.listid:
            print("No data loaded!")
            tk.messagebox.showinfo(parent=self, title='No data loaded!', message='You must load some data before drawing a map!')
            return None
        
        # checking user input
        try:
            fnt_size  = self.fontEntryVariable.get()
            extension = self.extensionEntryVariable.get()
            nx        = self.nxEntryVariable.get()
            ny        = self.nyEntryVariable.get()
            delta_l   = self.delta_lEntryVariable.get()
            base_l    = self.base_lEntryVariable.get()
        except:
            print('Error while reading the parameters given by the user!')
            tk.messagebox.showerror(parent=self, title='Check parameterts', message = 'Is something wrong with the parameters (text instead of integer?)')
            return None
        
        ## plotting data

        xmin = min(self.listx)
        ymin = min(self.listy)
        xmax = max(self.listx)
        ymax = max(self.listy)
        zmin = min(self.listz)
        zmax = max(self.listz)
       
        # creating a new figure
        plt.figure()

        # interpolation
        xi = np.linspace(xmin, xmax, nx)
        yi = np.linspace(ymin, ymax, ny)
        X,Y = np.meshgrid(xi,yi)        
        zi = griddata((self.listx, self.listy), self.listz, (X, Y), method=self.interpMethodVar.get())        
        
        # determining the location of the contour lines        
        lev_low = list(frange(base_l,zmin,-delta_l))
        lev_up  = list(frange(base_l+delta_l,zmax,delta_l))
        
        # plotting of the result
        C = plt.contour(xi, yi, zi, lev_low + lev_up, linewidths = 0.5, colors = 'k')
        plt.imshow(zi, extent=(xmin,xmax,ymin,ymax), origin='lower')
        plt.clabel(C, inline=1, fontsize=fnt_size);
             
        # legend
        plt.colorbar()
        
        # plotting the data points
        plt.scatter(self.listx, self.listy, marker = 'o', c = 'b', s = 5, zorder = 10)
        
        # plotting the building by determining their convex hull
        for b, list_coord in self.bat.items():
            print("INFO: plotting building", b)
            hull = ConvexHull(np.asarray(list_coord))
            list_coord_hull = list()
                
            for v in hull.vertices:
                list_coord_hull.append(list_coord[v])
                            
            ax = plt.subplot()
            ax.add_patch(Polygon(list_coord_hull, closed = True, fill= False, hatch='///'))
                                       
        # plot axis settings
        plt.axis('equal')
        self.xlim_min = xmin - extension
        self.xlim_max = xmax + extension
        self.ylim_min = ymin - extension
        self.ylim_max = ymax + extension
        plt.xlim(self.xlim_min, self.xlim_max)
        plt.ylim(self.ylim_min, self.ylim_max)

        # x label
        scale = self.scaleEntryVariable.get()
        plt.xlabel('Scale: 1/' + str(scale))
        
        # plotting points id if requested
        if self.plotId.get() == 1:
            labels = ['PN {0}'.format(i) for i in self.listid]
            for label, x, y in zip(labels, self.listx, self.listy):
                plt.annotate(label, xy = (x, y), xytext = (-1, 1), textcoords = 'offset points', ha = 'right', va = 'bottom', size = fnt_size)
        
        # showinf the final figure
        plt.show()

    ## Saving the map in memory
    def save_map(self):
        
        ## checking if a map is stored in memory
        
        if len(plt.get_fignums()) == 0:
            tk.messagebox.showinfo(parent=self, title='No map to save!', message='You must draw a map before saving it!')
            return None

        ## checking user input
        
        try:
            scale = self.scaleEntryVariable.get()
        except:
            print('Error while reading the scale parameter given by the user!')
            tk.messagebox.showerror(parent=self, title='Check scale', message = 'Maybe something is wrong with the scale (text instead of integer)?')
            return None

        ## determining output file name
        
        options = {}
        options['filetypes'] = [('png files', '.png')]
        options['initialfile'] = 'map.png'
        save_filename = asksaveasfilename(**options) 
        if not save_filename:
            print('No filename given... abort saving!')
            return None
        else:
            print(save_filename)
        
        ## determing the resulting scale

        # preparing the plot
        fig = plt.gcf()
        ax  = plt.gca()
        
        # get axis physical dimensions in inches
        bbox = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())

        # convert to cm
        width  = bbox.width * 2.54
        height = bbox.height * 2.54
        
        # convert axis range to cm
        lenght_axis_x = (self.xlim_max - self.xlim_min) * 100.0
        lenght_axis_y = (self.ylim_max - self.ylim_min) * 100.0
        
        # determine the current scale
        scale_x = width  / lenght_axis_x
        scale_y = height / lenght_axis_y
        print('initial scale x =', scale_x)
        print('initial scale y =', scale_y)

        # computing desired length and width
        width_target  = (1 / scale) * lenght_axis_x  
        height_target = (1 / scale) * lenght_axis_y
        
        # ratio between target and current dimension
        ratio_width  = width_target / width
        ratio_length = height_target / height
        print('ratio_width  = ', ratio_width)
        print('ratio_length = ',  ratio_length)

        # setting the final size of the scaled figure
        size_x = fig.get_size_inches()[0]
        size_y = fig.get_size_inches()[1]
        fig.set_size_inches(size_x * ratio_width, size_y * ratio_length)
        
        ## saving the scaled figure
        
        fig.savefig(save_filename, dpi=self.dpiVar.get())
        plt.close()
        self.draw_map()

## Main function        
def main():
    root = tk.Tk()
    app = AppTopoGui(root)
    root.mainloop()
    plt.close('all')
    
if __name__ == '__main__':
    main()  