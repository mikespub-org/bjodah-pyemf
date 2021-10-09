from .constants import *
from .field import *
from .record import _EMR_UNKNOWN

_type_map = {}


def register(klass):
    """Register META with id."""
    _type_map[klass.emr_id] = klass
    return klass


class META_UNKNOWN(_EMR_UNKNOWN):
    emr_id = 0x7FFF

    def __init__(self):
        _EMR_UNKNOWN.__init__(self)

    def readHdr(self, already_read):
        (count, func) = struct.unpack("<IH", already_read)
        return func, count * 2

    def writeHdr(self, fh):
        fh.write(struct.pack("<IH", self.nSize // 2, self.iType))

    def hdrLen(self):
        return 6

    def verifySize(self, before, calcSize):
        return


class META_COLOR(META_UNKNOWN):
    typedef = [("I", "crColor", 0)]

    def __init__(self, color=0):
        META_UNKNOWN.__init__(self)
        self.crColor = color


class META_HAS_HANDLE(META_UNKNOWN):
    def __init__(self, dc=None, handle=0):
        META_UNKNOWN.__init__(self)
        self.handle = handle

    def hasHandle(self):
        return True


class META_HANDLE(META_UNKNOWN):
    typedef = [("H", "handle")]

    def __init__(self, dc=None, handle=0):
        META_UNKNOWN.__init__(self)
        self.handle = handle


class META_SETMODE(META_UNKNOWN):
    typedef = [("H", "iMode", 0), ("H", "iReserved", 0)]

    def __init__(self, mode, first, last):
        META_UNKNOWN.__init__(self)
        if mode < first or mode > last:
            self.error = 1
        else:
            self.iMode = mode


class META_CREATEOBJECT(META_HAS_HANDLE):
    def __init__(self, dc=None, handle=0):
        META_HAS_HANDLE.__init__(self, dc, handle)

    def isCreateObject(self):
        return True

    def setHandle(self, handle):
        self.handle = handle


class META_PLACEABLE(META_UNKNOWN):
    """The META_PLACEABLE record is the first record in a placeable
    WMF metafile, which is an extension to the WMF metafile format."""

    typedef = [
        ("I", "nKey", 0x9AC6CDD7),
        ("H", "hWmf", 0x0000),
        (Points(num=2, fmt="H"), "rclBounds"),
        ("H", "sInch", 0),
        ("I", "nReserved", 0),
        ("H", "sChecksum", 0),
    ]

    def __init__(self):
        META_UNKNOWN.__init__(self)
        self.szlDevice = [0, 0]
        self.szlMicrometers = [0, 0]
        self.szlMillimeters = [0, 0]

    def setBounds(self, dc, scaleheader=False):
        self.rclBounds = [
            [dc.bounds_left, dc.bounds_top],
            [dc.bounds_right, dc.bounds_bottom],
        ]
        self.rclFrame = [
            [dc.frame_left, dc.frame_top],
            [dc.frame_right, dc.frame_bottom],
        ]

        print(self)

    def writeHdr(self, fh):
        return

    def hdrLen(self):
        return 0


class META_HEADER(META_UNKNOWN):
    """The META_HEADER record is the first record in a standard (nonplaceable)
    WMF metafile."""

    typedef = [
        ("H", "sType", 0),
        ("H", "sHeaderSize", 9),
        ("H", "sVersion", 0),
        ("H", "sSizeLow", 0),
        ("H", "sSizeHigh", 0),
        ("H", "sNumberOfObjects", 0),
        ("I", "nMaxRecord", 0),
        ("H", "sNumberOfMembers", 0),
    ]

    def __init__(self):
        META_UNKNOWN.__init__(self)

    def writeHdr(self, fh):
        return

    def hdrLen(self):
        return 0


@register
class META_EOF(META_UNKNOWN):
    emr_id = 0x0000

    def isEOF(self):
        return True


# MetafileType
MEMORYMETAFILE = 0x0001
DISKMETAFILE = 0x0002


@register
class META_REALIZEPALETTE(META_UNKNOWN):
    emr_id = 0x0035


@register
class META_SETPALENTRIES(META_UNKNOWN):
    emr_id = 0x0037


@register
class META_SETBKMODE(META_SETMODE):
    emr_id = 0x0102

    def __init__(self, mode=OPAQUE):
        META_SETMODE.__init__(self, mode, TRANSPARENT, BKMODE_LAST)


@register
class META_SETMAPMODE(META_SETMODE):
    typedef = [("H", "iMapMode", 0)]

    emr_id = 0x0103

    def __init__(self, mode=MM_ANISOTROPIC):
        META_SETMODE.__init__(self, mode, MM_TEXT, MM_MAX)


@register
class META_SETROP2(META_UNKNOWN):
    emr_id = 0x0104


@register
class META_SETRELABS(META_UNKNOWN):
    emr_id = 0x0105


@register
class META_SETPOLYFILLMODE(META_SETMODE):
    emr_id = 0x0106

    def __init__(self, mode=ALTERNATE):
        META_SETMODE.__init__(self, mode, ALTERNATE, POLYFILL_LAST)


@register
class META_SETSTRETCHBLTMODE(META_UNKNOWN):
    emr_id = 0x0107


@register
class META_SETTEXTCHAREXTRA(META_UNKNOWN):
    emr_id = 0x0108


@register
class META_RESTOREDC(META_UNKNOWN):
    emr_id = 0x0127


@register
class META_RESIZEPALETTE(META_UNKNOWN):
    emr_id = 0x0139


@register
class META_DIBCREATEPATTERNBRUSH(META_UNKNOWN):
    emr_id = 0x0142


@register
class META_SETLAYOUT(META_UNKNOWN):
    emr_id = 0x0149


@register
class META_SETBKCOLOR(META_COLOR):
    emr_id = 0x0201


@register
class META_SETTEXTCOLOR(META_UNKNOWN):
    emr_id = 0x0209


@register
class META_OFFSETVIEWPORTORG(META_UNKNOWN):
    emr_id = 0x0211


@register
class META_LINETO(META_UNKNOWN):
    emr_id = 0x0213


@register
class META_MOVETO(META_UNKNOWN):
    emr_id = 0x0214


@register
class META_OFFSETCLIPRGN(META_UNKNOWN):
    emr_id = 0x0220


@register
class META_FILLREGION(META_UNKNOWN):
    emr_id = 0x0228


@register
class META_SETMAPPERFLAGS(META_UNKNOWN):
    emr_id = 0x0231


@register
class META_SELECTPALETTE(META_HANDLE):
    emr_id = 0x0234


@register
class META_POLYGON(META_UNKNOWN):
    emr_id = 0x0324


@register
class META_POLYLINE(META_UNKNOWN):
    emr_id = 0x0325

    typedef = [
        ("h", "sNumberOfPoints", 0),
        (Points(num="sNumberOfPoints", fmt="h"), "aPoints"),
    ]


@register
class META_SETTEXTJUSTIFICATION(META_UNKNOWN):
    emr_id = 0x020A


@register
class META_SETWINDOWORG(META_UNKNOWN):
    emr_id = 0x020B

    typedef = [
        ("H", "ptlOrigin_y"),
        ("H", "ptlOrigin_x"),
    ]

    def __init__(self, x=0, y=0):
        META_UNKNOWN.__init__(self)
        self.ptlOrigin_x = x
        self.ptlOrigin_y = y


@register
class META_SETWINDOWEXT(META_UNKNOWN):
    emr_id = 0x020C

    typedef = [
        ("H", "szlExtent_cy"),
        ("H", "szlExtent_cx"),
    ]

    def __init__(self, cx=0, cy=0):
        META_UNKNOWN.__init__(self)
        self.szlExtent_cx = cx
        self.szlExtent_cy = cy


@register
class META_SETVIEWPORTORG(META_UNKNOWN):
    emr_id = 0x020D


@register
class META_SETVIEWPORTEXT(META_UNKNOWN):
    emr_id = 0x020E


@register
class META_OFFSETWINDOWORG(META_UNKNOWN):
    emr_id = 0x020F


@register
class META_SCALEWINDOWEXT(META_UNKNOWN):
    emr_id = 0x0410


@register
class META_SCALEVIEWPORTEXT(META_UNKNOWN):
    emr_id = 0x0412


@register
class META_EXCLUDECLIPRECT(META_UNKNOWN):
    emr_id = 0x0415


@register
class META_INTERSECTCLIPRECT(META_UNKNOWN):
    emr_id = 0x0416


@register
class META_ELLIPSE(META_UNKNOWN):
    emr_id = 0x0418


@register
class META_FLOODFILL(META_UNKNOWN):
    emr_id = 0x0419


@register
class META_FRAMEREGION(META_UNKNOWN):
    emr_id = 0x0429


@register
class META_ANIMATEPALETTE(META_UNKNOWN):
    emr_id = 0x0436


@register
class META_TEXTOUT(META_UNKNOWN):
    emr_id = 0x0521


@register
class META_POLYPOLYGON(META_UNKNOWN):
    emr_id = 0x0538


@register
class META_EXTFLOODFILL(META_UNKNOWN):
    emr_id = 0x0548


@register
class META_RECTANGLE(META_UNKNOWN):
    emr_id = 0x041B


@register
class META_SETPIXEL(META_UNKNOWN):
    emr_id = 0x041F


@register
class META_ROUNDRECT(META_UNKNOWN):
    emr_id = 0x061C


@register
class META_PATBLT(META_UNKNOWN):
    emr_id = 0x061D


@register
class META_SAVEDC(META_UNKNOWN):
    emr_id = 0x001E


@register
class META_PIE(META_UNKNOWN):
    emr_id = 0x081A


@register
class META_STRETCHBLT(META_UNKNOWN):
    emr_id = 0x0B23


@register
class META_ESCAPE(META_UNKNOWN):
    emr_id = 0x0626


@register
class META_INVERTREGION(META_UNKNOWN):
    emr_id = 0x012A


@register
class META_PAINTREGION(META_UNKNOWN):
    emr_id = 0x012B


@register
class META_SELECTCLIPREGION(META_UNKNOWN):
    emr_id = 0x012C


@register
class META_SELECTOBJECT(META_HANDLE):
    emr_id = 0x012D


@register
class META_SETTEXTALIGN(META_UNKNOWN):
    emr_id = 0x012E


@register
class META_ARC(META_UNKNOWN):
    emr_id = 0x0817


@register
class META_CHORD(META_UNKNOWN):
    emr_id = 0x0830


@register
class META_BITBLT(META_UNKNOWN):
    emr_id = 0x0922


@register
class META_EXTTEXTOUT(META_UNKNOWN):
    emr_id = 0x0A32
    typedef = [
        ("h", "ptlReference_y", 0),
        ("h", "ptlReference_x", 0),
        ("h", "nChars", 0),
        ("H", "fwOpts", 0),
    ]

    # type descriptors of variable fields
    _rclBounds = Points(num=2, fmt="h")
    _string = EMFString(num="nChars", size=1, pad=2)
    _dx = List(num="nChars", fmt="h")

    def __init__(self, x=0, y=0, txt=""):
        META_UNKNOWN.__init__(self)
        self.ptlReference_x = x
        self.ptlReference_y = y
        self.string = txt
        self.nChars = len(txt) if txt is not None else 0
        self.charsize = 1
        self.rclBounds = [[0, 0], [-1, -1]]
        self.dx = []

    def _write(self, fh, fmt, name, value):
        output = fmt.pack(self, name, value)
        fh.write(output)

    def sizeExtra(self):
        fh = BytesIO()
        if self.fwOpts & (ETO_OPAQUE | ETO_CLIPPED):
            fmt = self.__class__._rclBounds
            self._write(fh, fmt, "rclBounds", self.rclBounds)
        if self.nChars > 0:
            fmt = self.__class__._string
            self._write(fh, fmt, "string", self.string)
        if self.fwOpts & (ETO_GLYPH_INDEX | ETO_PDY):
            fmt = self.__class__._dx
            old_nChars = self.nChars
            try:
                self.nChars = len(self.dx)
                self._write(fh, fmt, "dx", self.dx)
            finally:
                self.nChars = old_nChars
        self.unhandleddata = fh.getvalue()
        return super().sizeExtra()

    def unserializeExtra(self, data):
        super().unserializeExtra(data)
        ptr = 0
        if self.fwOpts & (ETO_OPAQUE | ETO_CLIPPED):
            fmt = self.__class__._rclBounds
            obj = self
            name = "rclBounds"
            (value, size) = fmt.unpack(obj, name, data, ptr)
            self.rclBounds = value
            ptr += size
        if self.nChars > 0:
            fmt = self.__class__._string
            (value, size) = fmt.unpack(self, "string", data, ptr)
            self.string = value
            ptr += size
        if self.fwOpts & (ETO_GLYPH_INDEX | ETO_PDY):
            fmt = self.__class__._dx
            # don't rely on nChars but compute it using the actual dx byte count
            old_nChars = self.nChars
            try:
                self.nChars = (len(data) - ptr) // 2
                (value, size) = fmt.unpack(self, "dx", data, ptr)
            finally:
                self.nChars = old_nChars
            self.dx = value
            ptr += size


@register
class META_SETDIBTODEV(META_UNKNOWN):
    emr_id = 0x0D33


@register
class META_DIBBITBLT(META_UNKNOWN):
    emr_id = 0x0940


@register
class META_DIBSTRETCHBLT(META_UNKNOWN):
    emr_id = 0x0B41


@register
class META_STRETCHDIB(META_UNKNOWN):
    emr_id = 0x0F43

    typedef = [
        ("I", "dwRop"),
        ("H", "iUsageSrc"),
        ("H", "cySrc"),
        ("H", "cxSrc"),
        ("H", "ySrc"),
        ("H", "xSrc"),
        ("H", "cyDest"),
        ("H", "cxDest"),
        ("H", "yDest"),
        ("H", "xDest"),
    ]

    def __init__(self):
        META_UNKNOWN.__init__(self)

    def unserializeExtra(self, data):
        # self.write_bitmap("test.bmp", data)
        super().unserializeExtra(data)

    def write_bitmap(self, file_name, data):
        bmp_header_len = 14
        dib_header_len = struct.unpack("<I", data[:4])
        with open(file_name, "wb") as f:
            f.write("BM" + struct.pack("<I", bmp_header_len + len(data)))
            f.write("\0\0\0\0")
            f.write(struct.pack("<I", bmp_header_len + dib_header_len[0]))
            f.write(data)


@register
class META_DELETEOBJECT(META_HANDLE):
    emr_id = 0x01F0

    def isDeleteObject(self):
        return True


@register
class META_CREATEPALETTE(META_CREATEOBJECT):
    emr_id = 0x00F7


@register
class META_CREATEPATTERNBRUSH(META_UNKNOWN):
    emr_id = 0x01F9


@register
class META_CREATEPENINDIRECT(META_CREATEOBJECT):
    emr_id = 0x02FA

    typedef = [
        ("H", "lopn_style"),
        (Points(num=1, fmt="H"), "lopn_width"),
        ("I", "lopn_color"),
    ]

    def __init__(self, style=PS_SOLID, width=1, color=0):
        META_CREATEOBJECT.__init__(self)
        self.lopn_style = style
        self.lopn_width = width
        self.lopn_color = color


@register
class META_CREATEFONTINDIRECT(META_CREATEOBJECT):
    emr_id = 0x02FB
    typedef = [
        ("h", "lfHeight"),
        ("h", "lfWidth"),
        ("h", "lfEscapement"),
        ("h", "lfOrientation"),
        ("h", "lfWeight"),
        ("B", "lfItalic"),
        ("B", "lfUnderline"),
        ("B", "lfStrikeOut"),
        ("B", "lfCharSet"),
        ("B", "lfOutPrecision"),
        ("B", "lfClipPrecision"),
        ("B", "lfQuality"),
        ("B", "lfPitchAndFamily"),
        (CString(num=32), "lfFaceName"),
    ]

    def __init__(
        self,
        height=0,
        width=0,
        escapement=0,
        orientation=0,
        weight=FW_NORMAL,
        italic=0,
        underline=0,
        strike_out=0,
        charset=ANSI_CHARSET,
        out_precision=OUT_DEFAULT_PRECIS,
        clip_precision=CLIP_DEFAULT_PRECIS,
        quality=DEFAULT_QUALITY,
        pitch_family=DEFAULT_PITCH | FF_DONTCARE,
        name="Times New Roman",
    ):
        META_CREATEOBJECT.__init__(self)
        self.lfHeight = height
        self.lfWidth = width
        self.lfEscapement = escapement
        self.lfOrientation = orientation
        self.lfWeight = weight
        self.lfItalic = italic
        self.lfUnderline = underline
        self.lfStrikeOut = strike_out
        self.lfCharSet = charset
        self.lfOutPrecision = out_precision
        self.lfClipPrecision = clip_precision
        self.lfQuality = quality
        self.lfPitchAndFamily = pitch_family

        # truncate or pad to exactly 32 characters
        name = name.split("\0")[0]
        nameLen = len(name)
        if nameLen > 31:
            name = name[0:31]
        name += "\0" * (32 - nameLen)
        self.lfFaceName = name
        # print("lfFaceName=%r" % self.lfFaceName)

    def hasHandle(self):
        return True


@register
class META_CREATEBRUSHINDIRECT(META_CREATEOBJECT):
    emr_id = 0x02FC

    typedef = [
        ("H", "lbStyle"),
        ("I", "lbColor"),
        ("H", "lbHatch"),
    ]


@register
class META_CREATEREGION(META_UNKNOWN):
    emr_id = 0x06FF
