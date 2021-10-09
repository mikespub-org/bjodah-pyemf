#!/usr/bin/env python

import pyemf

width = 8
height = 6
dpi = 300
pointstopixels = dpi / 72.0

emf = pyemf.EMF(width, height, dpi, verbose=False)
brush = emf.CreateHatchBrush(pyemf.HS_CROSS, (0x7F, 0x00, 0xFF))
emf.SelectObject(brush)
dashed = emf.CreatePen(pyemf.PS_DASH, 1, (0x00, 0x80, 0x80))
emf.SelectObject(dashed)

x = 100
y = 100
size = 300
emf.Arc(x, y, x + size, y + size, x, y, x, y + size)
print("after Arc")

x += size
y += size
emf.Chord(x, y, x + size, y + size, x, y, x, y + size)
print("after Chord")

x += size
y += size
emf.Pie(x, y, x + size, y + size, x, y, x, y + size)

x += size
emf.Pie(x, y, x + size, y + size, x, y + (int(size / 2)), x, y + (int(size / 2)))
print("after Pie")


ret = emf.save("test-arc-chord-pie.emf")
print("save returns %s" % str(ret))
