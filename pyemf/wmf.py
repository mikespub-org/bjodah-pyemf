# An adaptation of the pyemf EMF code for handling WMF format files

# Copyright (C) 2005 Rob McMullen
# Copyright (C) 2016 Jeremy Sanders
# Copyright (C) 2017 6tudent

# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.

# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.

# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., 51 Franklin St, Fifth Floor,
# Boston, MA  02110-1301, USA.


from .constants import *
from .dc import _DC
from . import meta


class WMF:

    """
Reference page of the public API for WMF metafile creation.  See
L{pyemf} for an overview / mini tutorial.

@group Creating Metafiles: __init__, load, save
@group Drawing Parameters: GetStockObject, SelectObject, DeleteObject, CreatePen, CreateSolidBrush, CreateHatchBrush, SetBkColor, SetBkMode, SetPolyFillMode
@group Drawing Primitives: SetPixel, Polyline, PolyPolyline, Polygon, PolyPolygon, Rectangle, RoundRect, Ellipse, Arc, Chord, Pie, PolyBezier
@group Path Primatives: BeginPath, EndPath, MoveTo, LineTo, PolylineTo, ArcTo,
 PolyBezierTo, CloseFigure, FillPath, StrokePath, StrokeAndFillPath
@group Clipping: SelectClipPath
@group Text: CreateFont, SetTextAlign, SetTextColor, TextOut
@group Coordinate System Transformation: SaveDC, RestoreDC, SetWorldTransform, ModifyWorldTransform
@group **Experimental** -- Viewport Manipulation: SetMapMode, SetViewportOrgEx, GetViewportOrgEx, SetWindowOrgEx, GetWindowOrgEx, SetViewportExtEx, ScaleViewportExtEx, GetViewportExtEx, SetWindowExtEx, ScaleWindowExtEx, GetWindowExtEx

"""

    def __init__(self, width=6.0, height=4.0, density=300, units="in",
                 description="pyemf.sf.net", verbose=False):
        """
Create an EMF structure in memory.  The size of the resulting image is
specified in either inches or millimeters depending on the value of
L{units}.  Width and height are floating point values, but density
must be an integer because this becomes the basis for the coordinate
system in the image.  Density is the number of individually
addressible pixels per unit measurement (dots per inch or dots per
millimeter, depending on the units system) in the image.  A
consequence of this is that each pixel is specified by a pair of
integer coordinates.

@param width: width of EMF image in inches or millimeters
@param height: height of EMF image in inches or millimeters
@param density: dots (pixels) per unit measurement
@param units: string indicating the unit measurement, one of:
 - 'in'
 - 'mm'
@type width: float
@type height: float
@type density: int
@type units: string
@param description: optional string to specify a description of the image
@type description: string

"""
        self.filename = None
        self.dc = _DC(width, height, density, units)
        self.records = []

        # path recordkeeping
        self.pathstart = 0

        self.verbose = verbose

        # if True, scale the image using only the header, and not
        # using MapMode or SetWindow/SetViewport.
        self.scaleheader = True

        placehdr = meta.META_PLACEABLE()
        self._append(placehdr)
        hdr = meta.META_HEADER()
        self._append(hdr)

    def loadmem(self, membuf=None):
        """
Read an existing buffer from a string of bytes.  If any records exist
in the current object, they will be overwritten by the records from
this buffer.

@param membuf: buffer to load
@type membuf: string
@returns: True for success, False for failure.
@rtype: Boolean
        """
        fh = BytesIO(membuf)
        self._load(fh)

    def load(self, filename=None):
        """
Read an existing EMF file.  If any records exist in the current
object, they will be overwritten by the records from this file.

@param filename: filename to load
@type filename: string
@returns: True for success, False for failure.
@rtype: Boolean
        """
        if filename:
            self.filename = filename

        if self.filename:
            fh = open(self.filename, 'rb')
            self._load(fh)

    def _load(self, fh):
        self.records = []
        self._unserialize(fh)
        self.scaleheader = False
        # get DC from header record
        self.dc.getBounds(self.records[0])

    def _unserialize(self, fh):
        try:
            data = fh.read(22)
            count = len(data)
            e = meta.META_PLACEABLE()
            e.unserialize(fh, data, 1, count, 0)
            self.records.append(e)

            data = fh.read(18)
            count = len(data)
            e = meta.META_HEADER()
            e.unserialize(fh, data, 1, count, 0)
            self.records.append(e)

            objects = [None] * e.sNumberOfObjects

            dummy_rec = meta.META_UNKNOWN()

            while count > 0:
                hdr_len = dummy_rec.hdrLen()
                data = fh.read(hdr_len)
                count = len(data)
                if count >= hdr_len:
                    (sType, nSize) = dummy_rec.readHdr(data)
                    if self.verbose:
                        print("WMF:  sType=0x%04x nSize=%d" % (sType, nSize))

                    if sType in meta._type_map:
                        e = meta._type_map[sType]()
                    else:
                        e = meta.META_UNKNOWN()

                    e.unserialize(fh, data, sType, nSize)
                    self.records.append(e)

                    if e.isCreateObject():
                        handle = objects.index(None)
                        e.setHandle(handle)
                        objects[handle] = e
                        if self.verbose:
                            print("  handle=%d" % handle)

                    if e.isDeleteObject():
                        self.dc.removeObject(e.handle)
                        objects[e.handle] = None
                    elif e.hasHandle():
                        self.dc.addObject(e, e.handle)

                    if self.verbose:
                        print("Unserializing: ", end=' ')
                        print(e)
                elif count > 0 and self.verbose:
                    print("Discarded trailing bytes: %r" % data)

        except EOFError:
            pass

    def _append(self, e):
        """Append an EMR to the record list, unless the record has
        been flagged as having an error."""
        if not e.error:
            if self.verbose:
                print("Appending: ", end=' ')
                print(e)
            self.records.append(e)
            return 1
        return 0

    def _end(self):
        """
Append an EOF record and compute header information.  The header needs
to know the number of records, number of handles, bounds, and size of
the entire metafile before it can be written out, so we have to march
through all the records and gather info.
        """

        end = self.records[-1]
        if not end.isEOF():
            if self.verbose:
                print("adding EOF record")
            e = meta.META_EOF()
            self._append(e)
        header = self.records[0]
        header.setBounds(self.dc, self.scaleheader)
        header.nRecords = len(self.records)
        header.nHandles = len(self.dc.objects)
        size = 0
        for e in self.records:
            e.resize()
            size += e.nSize
            if self.verbose:
                print("size=%d total=%d" % (e.nSize, size))
        if self.verbose:
            print("total: %s bytes" % size)
        header.nBytes = size

    def save(self, filename=None):
        """
Write the EMF to disk.

@param filename: filename to write
@type filename: string
@returns: True for success, False for failure.
@rtype: Boolean
        """

        self._end()

        if filename:
            self.filename = filename

        if self.filename:
            try:
                fh = open(self.filename, "wb")
                self._update_header()
                self._serialize(fh)
                fh.close()
                return True
            except:
                raise
                return False
        return False

    def _update_header(self):
        file_len = 0
        max_rec_len = 0
        num_records = 0
        for e in self.records:
            rec_len = e.resize()
            max_rec_len = max(max_rec_len, rec_len)
            file_len += rec_len
            num_records += 1
        header = self.records[1]
        file_size = (file_len + 1) // 2
        header.sSizeLow = file_size % 65536
        header.sSizeHigh = file_size // 65536
        max_rec_size = (max_rec_len + 1) // 2
        header.nMaxRecord = max_rec_size

    def _serialize(self, fh):
        for e in self.records:
            if self.verbose:
                print(e)
            e.serialize(fh)

    def _create(self, width, height, dots_per_unit, units):
        pass

    def _getBounds(self, points):
        """Get the bounding rectangle for this list of 2-tuples."""
        left = points[0][0]
        right = left
        top = points[0][1]
        bottom = top
        for x, y in points[1:]:
            if x < left:
                left = x
            elif x > right:
                right = x
            if y < top:
                top = y
            elif y > bottom:
                bottom = y
        return ((left, top), (right, bottom))

    def _mergeBounds(self, bounds, itembounds):
        if itembounds:
            if itembounds[0][0] < bounds[0][0]:
                bounds[0][0] = itembounds[0][0]
            if itembounds[0][1] < bounds[0][1]:
                bounds[0][1] = itembounds[0][1]
            if itembounds[1][0] > bounds[1][0]:
                bounds[1][0] = itembounds[1][0]
            if itembounds[1][1] > bounds[1][1]:
                bounds[1][1] = itembounds[1][1]

    def _getPathBounds(self):
        """Get the bounding rectangle for the list of EMR records
        starting from the last saved path start to the current record."""
        # If there are no bounds supplied, default to the EMF standard
        # of ((0,0),(-1,-1)) which means that the bounds aren't
        # precomputed.
        bounds = [[0, 0], [-1, -1]]

        # find the first bounds
        for i in range(self.pathstart, len(self.records)):
            # print "FIXME: checking initial bounds on record %d" % i
            e = self.records[i]
            # print e
            # print "bounds=%s" % str(e.getBounds())
            objbounds = e.getBounds()
            if objbounds:
                # print "bounds=%s" % str(objbounds)
                # have to copy the object manually because we don't
                # want to overwrite the object's bounds
                bounds = [[objbounds[0][0], objbounds[0][1]],
                          [objbounds[1][0], objbounds[1][1]]]
                break

        # if there are more records with bounds, merge them
        for j in range(i, len(self.records)):
            # print "FIXME: checking bounds for more records: %d" % j
            e = self.records[j]
            # print e
            # print "bounds=%s" % str(e.getBounds())
            self._mergeBounds(bounds, e.getBounds())

        return bounds

    def _useShort(self, bounds):
        """Determine if we can use the shorter 16-bit EMR structures.
        If all the numbers can fit within 16 bit integers, return
        true.  The bounds 4-tuple is (left,top,right,bottom)."""

        SHRT_MIN = -32768
        SHRT_MAX = 32767
        if bounds[0][0] >= SHRT_MIN and bounds[0][1] >= SHRT_MIN and bounds[1][0] <= SHRT_MAX and bounds[1][1] <= SHRT_MAX:
            return True
        return False

    def _appendOptimize16(self, points, cls16, cls):
        bounds = self._getBounds(points)
        if self._useShort(bounds):
            e = cls16(points, bounds)
        else:
            e = cls(points, bounds)
        if not self._append(e):
            return 0
        return 1

    def _appendOptimizePoly16(self, polylist, cls16, cls):
        """polylist is a list of lists of points, where each inner
        list represents a single polygon or line.  The number of
        polygons is the size of the outer list."""
        points = []
        polycounts = []
        for polygon in polylist:
            count = 0
            for point in polygon:
                points.append(point)
                count += 1
            polycounts.append(count)

        bounds = self._getBounds(points)
        if self._useShort(bounds):
            e = cls16(points, polycounts, bounds)
        else:
            e = cls(points, polycounts, bounds)
        if not self._append(e):
            return 0
        return 1

    def _appendHandle(self, e):
        handle = self.dc.addObject(e)
        if not self._append(e):
            self.dc.popObject()
            return 0
        e.handle = handle
        return handle

    def removeRecord(self, i):
        del self.records[i]

    def SelectObject(self, handle):
        """
Make the given graphics object current.

@param handle: handle of graphics object to make current.

@return:
    the handle of the current graphics object which obj replaces.

@rtype: int
@type handle: int
        """
        return self._append(meta.META_SELECTOBJECT(self.dc, handle))

    def CreateFont(self, height, width=0, escapement=0, orientation=0, weight=FW_NORMAL, italic=0, underline=0, strike_out=0, charset=ANSI_CHARSET, out_precision=OUT_DEFAULT_PRECIS, clip_precision=CLIP_DEFAULT_PRECIS, quality=DEFAULT_QUALITY, pitch_family=DEFAULT_PITCH | FF_DONTCARE, name='Times New Roman'):
        """

Create a new font object. Presumably, when rendering the EMF the
system tries to find a reasonable approximation to all the requested
attributes.

@param height: specified one of two ways:
 - if height>0: locate the font using the specified height as the typical cell height
 - if height<0: use the absolute value of the height as the typical glyph height.
@param width: typical glyph width.  If zero, the typical aspect ratio of the font is used.
@param escapement: angle, in degrees*10, of rendered string rotation.  Note that escapement and orientation must be the same.
@param orientation: angle, in degrees*10, of rendered string rotation.  Note that escapement and orientation must be the same.
@param weight: weight has (at least) the following values:
 - FW_DONTCARE
 - FW_THIN
 - FW_EXTRALIGHT
 - FW_ULTRALIGHT
 - FW_LIGHT
 - FW_NORMAL
 - FW_REGULAR
 - FW_MEDIUM
 - FW_SEMIBOLD
 - FW_DEMIBOLD
 - FW_BOLD
 - FW_EXTRABOLD
 - FW_ULTRABOLD
 - FW_HEAVY
 - FW_BLACK
@param italic: non-zero means try to find an italic version of the face.
@param underline: non-zero means to underline the glyphs.
@param strike_out: non-zero means to strike-out the glyphs.
@param charset: select the character set from the following list:
 - ANSI_CHARSET
 - DEFAULT_CHARSET
 - SYMBOL_CHARSET
 - SHIFTJIS_CHARSET
 - HANGEUL_CHARSET
 - HANGUL_CHARSET
 - GB2312_CHARSET
 - CHINESEBIG5_CHARSET
 - GREEK_CHARSET
 - TURKISH_CHARSET
 - HEBREW_CHARSET
 - ARABIC_CHARSET
 - BALTIC_CHARSET
 - RUSSIAN_CHARSET
 - EE_CHARSET
 - EASTEUROPE_CHARSET
 - THAI_CHARSET
 - JOHAB_CHARSET
 - MAC_CHARSET
 - OEM_CHARSET
@param out_precision: the precision of the face may have on of the
following values:
 - OUT_DEFAULT_PRECIS
 - OUT_STRING_PRECIS
 - OUT_CHARACTER_PRECIS
 - OUT_STROKE_PRECIS
 - OUT_TT_PRECIS
 - OUT_DEVICE_PRECIS
 - OUT_RASTER_PRECIS
 - OUT_TT_ONLY_PRECIS
 - OUT_OUTLINE_PRECIS
@param clip_precision: the precision of glyph clipping may have one of the
following values:
 - CLIP_DEFAULT_PRECIS
 - CLIP_CHARACTER_PRECIS
 - CLIP_STROKE_PRECIS
 - CLIP_MASK
 - CLIP_LH_ANGLES
 - CLIP_TT_ALWAYS
 - CLIP_EMBEDDED
@param quality: (subjective) quality of the font. Choose from the following
values:
 - DEFAULT_QUALITY
 - DRAFT_QUALITY
 - PROOF_QUALITY
 - NONANTIALIASED_QUALITY
 - ANTIALIASED_QUALITY
@param pitch_family: the pitch and family of the font face if the named font can't be found. Combine the pitch and style using a binary or.
 - Pitch:
   - DEFAULT_PITCH
   - FIXED_PITCH
   - VARIABLE_PITCH
   - MONO_FONT
 - Style:
   - FF_DONTCARE
   - FF_ROMAN
   - FF_SWISS
   - FF_MODERN
   - FF_SCRIPT
   - FF_DECORATIVE
@param name: ASCII string containing the name of the font face.
@return: handle of font.
@rtype: int
@type height: int
@type width: int
@type escapement: int
@type orientation: int
@type weight: int
@type italic: int
@type underline: int
@type strike_out: int
@type charset: int
@type out_precision: int
@type clip_precision: int
@type quality: int
@type pitch_family: int
@type name: string

        """
        e = meta.META_CREATEFONTINDIRECT(height, width,
                                         escapement,
                                         orientation, weight,
                                         italic, underline,
                                         strike_out, charset,
                                         out_precision,
                                         clip_precision,
                                         quality, pitch_family,
                                         name)
        return self._appendHandle(e)

    def TextOut(self, x, y, text):
        """

Draw a string of text at the given position using the current FONT and
other text attributes.
@param x: x position of text.
@param y: y position of text.
@param text: ASCII text string to render.
@return: true of string successfully drawn.

@rtype: int
@type x: int
@type y: int
@type text: string

        """
        e = meta.META_EXTTEXTOUT(x, y, text)
        if not self._append(e):
            return 0
        return 1
