# TopoPy GUI
#
# A Python-based topographic drawings software.
# This software is released under the Apache 2.0 License.
#
# Author: Johan Barthelemy
# Date: June 2015
# Version: 1

## Import section

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as ml
import csv
import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
import tkinter.messagebox
import os

class AppTopoGui(tk.Frame):
    
    # Constructor
    def __init__(self, parent):
        
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.parent.title('TopoPy')
        self.parent.iconbitmap('application_edit.ico') # put that line in the constructor
        
        self.listx  = []     # list of ids 
        self.listy  = []     # list containing the x coordinates of the points
        self.listz  = []     # list containing the y coordinates of the points
        self.listid = []     # list containing the z coordinates of the points
        
        #self.scale     = 200 # desired scale when saving the file
        #self.nx        = 500 # number of interpolated points (x)
        #self.ny        = 500 # number of interpolated points (y)
        #self.extension = 2   # spaces between borders and figure (in meters)
        #self.delta_l   = 20  # difference in meters between 2 contour lines
        #self.size_ids  = 7   # font size of the points labels
        
        self.initialize_gui()

    # Initialize the interface
    def initialize_gui(self):
    
        # layout manager
        self.grid()
        
        # ... creation load button
        loadButton = tk.Button(self, text="Load data", command=self.load_file)
        loadButton.grid(column=0, row=0, columnspan=4, sticky='E'+'W')
        
        # ... creation draw button
        drawButton = tk.Button(self, text="Draw map", command=self.draw_map)
        drawButton.grid(column=0, row=1, columnspan=4, sticky='E'+'W')
                
        # ... creation bouton sauvegarde
        saveButton = tk.Button(self, text="Save", command=self.save_map)
        saveButton.grid(column=0,row=2,columnspan=4,sticky='E'+'W')        
        
        # ... create label for scale
        scaleLabel = tk.Label(self, text="Scale: 1/", anchor="center")
        scaleLabel.grid(column=0, row=3, sticky='E')
        
        # ... create entry for scale
        self.scaleEntryVariable = tk.IntVar()
        self.scaleEntry = tk.Entry(self, textvariable=self.scaleEntryVariable)
        self.scaleEntry.grid(column=1, row=3, columnspan=3,sticky='E'+'W')
        self.scaleEntryVariable.set("200")
        
        # ... create label for image dpi
        dpiLabel = tk.Label(self, text="Resolution (dpi):")
        dpiLabel.grid(column=0, row=4, sticky='E')
        
        # ... creating the radio buttons for selecting the image dpi
        self.dpiVar = tk.IntVar()
        tk.Radiobutton(self, text="100", padx = 20, variable=self.dpiVar, value=100).grid(column=1,row=4)
        tk.Radiobutton(self, text="150", padx = 20, variable=self.dpiVar, value=150).grid(column=2,row=4)
        tk.Radiobutton(self, text="300", padx = 20, variable=self.dpiVar, value=300).grid(column=3,row=4)
        self.dpiVar.set(150)
        
        # ... creation label plot ids
        plotIdsLabel = tk.Label(self, text="Show points id:")
        plotIdsLabel.grid(column=0, row=5, sticky='E')
        
        # ... creating the radio buttons for showing/hiding points id
        self.plotId = tk.IntVar()
        tk.Radiobutton(self, text="Yes", padx = 20, variable=self.plotId, value=1).grid(column=1,row=5)
        tk.Radiobutton(self, text="No",  padx = 20, variable=self.plotId, value=0).grid(column=2,row=5)
        
        # ... create label for font size
        fontLabel = tk.Label(self, text="Font size:", anchor="center")
        fontLabel.grid(column=0, row=6, sticky='E')
        
        # ... create entry for font size
        self.fontEntryVariable = tk.IntVar()
        self.fontEntry = tk.Entry(self, textvariable=self.fontEntryVariable)
        self.fontEntry.grid(column=1, row=6, columnspan=3,sticky='E'+'W')
        self.fontEntryVariable.set("10")

        # ... create label for delta_l
        delta_lLabel = tk.Label(self, text="Altimetric difference between 2 contour lines (meters):", anchor="center")
        delta_lLabel.grid(column=0, row=7, sticky='E')
        
        # ... create entry for delta_l
        self.delta_lEntryVariable = tk.IntVar()
        self.delta_lEntry = tk.Entry(self, textvariable=self.delta_lEntryVariable)
        self.delta_lEntry.grid(column=1, row=7, columnspan=3,sticky='E'+'W')
        self.delta_lEntryVariable.set("20")

        # ... create label for extension
        extensionLabel = tk.Label(self, text="Minimum distance between the borders and the contour lines (meters):", anchor="center")
        extensionLabel.grid(column=0, row=8, sticky='E')
        
        # ... create entry for extension
        self.extensionEntryVariable = tk.IntVar()
        self.extensionEntry = tk.Entry(self, textvariable=self.extensionEntryVariable)
        self.extensionEntry.grid(column=1, row=8, columnspan=3,sticky='E'+'W')
        self.extensionEntryVariable.set("2")

        # ... create label for nx x ny
        nxnyLabel = tk.Label(self, text="Dimension of the interpolation grid:", anchor="center")
        nxnyLabel.grid(column=0, row=9, sticky='E')
        nxny2Label = tk.Label(self, text=" x ", anchor="center")
        nxny2Label.grid(column=2, row=9, sticky='E'+'W')
        
        # ... create entry for nx
        self.nxEntryVariable = tk.IntVar()
        self.nxEntry = tk.Entry(self, textvariable=self.nxEntryVariable)
        self.nxEntry.grid(column=1, row=9, columnspan=1,sticky='E'+'W')
        self.nxEntryVariable.set("500")
        
        # ... create entry for ny
        self.nyEntryVariable = tk.IntVar()
        self.nyEntry = tk.Entry(self, textvariable=self.nyEntryVariable)
        self.nyEntry.grid(column=3, row=9, columnspan=1,sticky='E'+'W')
        self.nyEntryVariable.set("500")
        
        # ... creation bouton quit
        quitButton = tk.Button(self, text="Quit",command=self.quit_app)
        quitButton.grid(column=0,row=10,columnspan=4,sticky='E'+'W')
                
        # empeche de redimensionner verticalement
        self.parent.resizable(False, False)
        
        # fixe les dim de l'interface (empeche redimensionnement automatique
        # si trop long texte dans le label
        self.update() # rafraichit l interface pour etre certain que tout est affiche
        self.parent.geometry(self.parent.geometry()) # fixe l interface
        
        # initialise le focus sur le champ de texte et texte deja selectionne
        self.scaleEntry.focus_set()
        self.scaleEntry.selection_range(0, tk.END)
       
    def quit_app(self):
        
        plt.close('all')
        top=self.winfo_toplevel()
        top.quit()
        self.parent.destroy()
    
    def clear_data(self):
        
        self.listid.clear()
        self.listx.clear()
        self.listy.clear()
        self.listz.clear()
    
    def load_file(self):
        
        # getting input file name and path
        self.csvfilename = askopenfilename();
        print(self.csvfilename)
        
        # resetting data
        self.clear_data()
        
        # reading file
        with open(self.csvfilename,'r') as csvfile:
            filereader = csv.reader(csvfile, delimiter = "\t",quotechar = " " )
            for row in filereader:
                try:
                    self.listid.append(str(row[0]))
                    self.listx.append(float(row[1]))
                    self.listy.append(float(row[2]))
                    self.listz.append(float(row[3]))
                except:
                    self.clear_data()
                    print('Error while reading input file... maybe something wrong with it?')
                    tk.messagebox.showerror(parent=self, title='Error while reading input file', message = 'Maybe something is wrong with the input file?')
                    return None
            
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
        except:
            print('Error while reading the parameters given by the user!')
            tk.messagebox.showerror(parent=self, title='Check parameterts', message = 'Is something wrong with the parameters (text instead of integer?)')
            return None
        
        ## plotting data

        xmin = min(self.listx)
        ymin = min(self.listy)
        xmax = max(self.listx)
        ymax = max(self.listy)
       
        # creating a new figure
        plt.figure()

        # interpolation
        xi = np.linspace(xmin, xmax, nx)
        yi = np.linspace(ymin, ymax, ny)
        zi = ml.griddata(self.listx, self.listy, self.listz, xi, yi)
        
        # plotting of the result
        C = plt.contour(xi, yi, zi, delta_l, linewidths = 0.5, colors = 'k')
        plt.pcolormesh(xi, yi, zi, cmap = plt.get_cmap('rainbow'))
        plt.clabel(C, inline=1, fontsize=fnt_size);
             
        # legend
        plt.colorbar()
        
        # plotting the data points
        plt.scatter(self.listx, self.listy, marker = 'o', c = 'b', s = 5, zorder = 10)
        
        # plot axis settings
        plt.axis('equal')
        self.xlim_min = xmin - extension
        self.xlim_max = xmax + extension
        self.ylim_min = ymin - extension
        self.ylim_max = ymax + extension
        plt.xlim(self.xlim_min, self.xlim_max)
        plt.ylim(self.ylim_min, self.ylim_max)
        
        # plotting points id if requested
        if self.plotId.get() == 1:
            labels = ['PN {0}'.format(i) for i in self.listid]
            for label, x, y in zip(labels, self.listx, self.listy):
                plt.annotate(label, xy = (x, y), xytext = (-1, 1), textcoords = 'offset points', ha = 'right', va = 'bottom', size = fnt_size)
        
        # showinf the final figure
        plt.show()

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
        scale_x = width / lenght_axis_x
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

# Main function        
def main():
    root = tk.Tk()
    AppTopoGui(root)
    root.mainloop()
    plt.close('all')
    
if __name__ == '__main__':
    main()  