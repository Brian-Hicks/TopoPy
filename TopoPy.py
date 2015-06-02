## imports

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as ml
import csv
import tkinter
from tkinter.filedialog import askopenfilename
import os

## parameters

plot_ids  = True       # True pour afficher les noms des points; False pour les cacher
size_ids  = 7          # Taille de la police des identifiants des points
precision = 150        # Resolution de l'image finale (100, 150, 300)
delta_l   = 20         # Difference de niveau entre 2 courbes
scale     = 1 / 200    # Echelle desiree
extension = 2          # Ajuste la bordure blanche entre le dessin et les axes (metres)

## reading data

listx  = []
listy  = []
listz  = []
listid = []

root = tkinter.Tk()
csvfilename = askopenfilename()
root.withdraw()

with open(csvfilename,'r') as csvfile:
    filereader = csv.reader(csvfile, delimiter = "\t",quotechar = " " )
    for row in filereader:
        listid.append(str(row[0]))
        listx.append(float(row[1]))
        listy.append(float(row[2]))
        listz.append(float(row[3])) 
        
xmin = min(listx)
ymin = min(listy)
xmax = max(listx)
ymax = max(listy)

nx = 500
ny = 500

## plotting data

xi = np.linspace(xmin, xmax, nx)
yi = np.linspace(ymin, ymax, ny)
zi = ml.griddata(listx, listy, listz, xi, yi)

C = plt.contour(xi, yi, zi, delta_l, linewidths = 0.5, colors = 'k')
plt.pcolormesh(xi, yi, zi, cmap = plt.get_cmap('rainbow'))
plt.clabel(C, inline=1, fontsize=10)

plt.colorbar() 
plt.scatter(listx, listy, marker = 'o', c = 'b', s = 5, zorder = 10)
plt.axis('equal')

plt.xlim(xmin - extension, xmax + extension)
plt.ylim(ymin - extension, ymax + extension)

###
xlim_min = xmin - extension
xlim_max = xmax + extension
ylim_min = ymin - extension
ylim_max = ymax + extension
###


if plot_ids == True:
    labels = ['PN {0}'.format(i) for i in listid]
    for label, x, y in zip(labels, listx, listy):
        plt.annotate(label, xy = (x, y), xytext = (-1, 1), textcoords = 'offset points', ha = 'right', va = 'bottom', size = size_ids)

# plotting the figure
plt.show()

## determing the resulting scale

fig = plt.gcf()
ax  = plt.gca()

# get axis physical dimensions in inches
bbox = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())

# convert to cm
width  = bbox.width * 2.54
height = bbox.height * 2.54

# convert axis range to cm
lenght_axis_x = (xlim_max - xlim_min) * 100.0
lenght_axis_y = (ylim_max - ylim_min) * 100.0

# determine the current scale
scale_x = width / lenght_axis_x
scale_y = height / lenght_axis_y
print('initial scale x =', scale_x)
print('initial scale y =', scale_y)

# computing desired length and width
width_target  = scale * lenght_axis_x  
height_target = scale * lenght_axis_y

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

cur_dir = os.path.dirname(csvfilename)
save_filename = cur_dir + '/epreuve_scaled.png'
fig.savefig(save_filename, dpi=precision)

