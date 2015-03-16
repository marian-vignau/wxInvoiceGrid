# -*- coding: utf-8 -*-
"""
-------------------------------------------------------------------------------
 Name:       InvoiceGrid
 Purpose:    Easy to do invoice grid


 Author:      mvignau

 Created:     05/11/2014
 Copyright:   (c) mvignau 2014
 Licence:     <your licence>
-------------------------------------------------------------------------------"""
#!/usr/bin/env python

import  wx
import  wx.grid as  gridlib
import locale



class DataType(object):
    '''    Base type, no meant to be used directly. Provide some defaults
    '''
    def __init__(self, *args, **kargs):
        self.args = args
        self.kargs = kargs

    def renderer(self):
        return gridlib.GridCellStringRenderer()
    def editor(self):
        return gridlib.GridCellTextEditor()
    def fromStr(self, value):
        return value
    def toStr(self,value):
        return value


class ReadOnlyType(DataType):
    def editor(self):
        return None

class NumberType(DataType):
    def renderer(self):
        return gridlib.GridCellNumberRenderer()
    def editor(self):
        return gridlib.GridCellNumberEditor(*self.args)
    def fromStr(self, value):
        try:
            return int(value)
        except ValueError:
            return 0
    def toStr(self,value):
        if value != 0:
            return locale.str(value)
        else:
            return u''

class FloatType(DataType):
    def renderer(self):
        return gridlib.GridCellFloatRenderer(*self.args)
    def editor(self):
        return gridlib.GridCellFloatEditor(*self.args)
    def fromStr(self, value):
        try:
            return locale.atof(value)
        except ValueError:
            return 0
    def toStr(self,value):
        if value != 0:
            return locale.str(value)
        else:
            return u''

class BoolType(DataType):
    def renderer(self):
        return gridlib.GridCellBoolRenderer()
    def editor(self):
        return gridlib.GridCellBoolEditor()
    def fromStr(self, value):
        if value == u'1':
            return True
        else:
            return False
    def toStr(self,value):
        if value:
            return u'1'
        else:
            return u''

class TextType(DataType):
    def renderer(self):
        return gridlib.GridCellAutoWrapStringRenderer()
    def editor(self):
        return gridlib.GridCellTextEditor()

class ListType(DataType):
    def __init__(self,*args):
        DataType.__init__(self, *args)
        self.values=[x[0] for x in self.args[0]]
        self.keys=[x[1] for x in self.args[0]]

    def editor(self):
        return gridlib.GridCellChoiceEditor(self.values)

    def fromStr(self, value):
        try:
            idx=self.values.index(value)
            return self.keys[idx]
        except ValueError:
            return None

    def toStr(self, value):
        try:
            idx=self.keys.index(value)
            return self.values[idx]
        except ValueError:
            return ''

class ImageRenderer(gridlib.PyGridCellRenderer):
    def __init__(self, bitmap):
        """ This just places an image
        """
        gridlib.PyGridCellRenderer.__init__(self)
        #self.table = table
        self.bitmap = bitmap
        self.colSize = None
        self.rowSize = None

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        image = wx.MemoryDC()
        image.SelectObject(self.bitmap)

        # clear the background
        dc.SetBackgroundMode(wx.SOLID)

        if isSelected:
            dc.SetBrush(wx.Brush(wx.BLUE, wx.SOLID))
            dc.SetPen(wx.Pen(wx.BLUE, 1, wx.SOLID))
        else:
            dc.SetBrush(wx.Brush(wx.WHITE, wx.SOLID))
            dc.SetPen(wx.Pen(wx.WHITE, 1, wx.SOLID))
        dc.DrawRectangleRect(rect)


        # copy the image but only to the size of the grid cell
        width, height = self.bitmap.GetWidth(), self.bitmap.GetHeight()

        if width > rect.width-2:
            width = rect.width-2

        if height > rect.height-2:
            height = rect.height-2

        dc.Blit(rect.x+1, rect.y+1, width, height,
                image,
                0, 0, wx.COPY, True)

class ButtonType(DataType):
    def renderer(self):
        return ImageRenderer(self.args[0])

    def editor(self):
        return None

    def fromStr(self, value):
        pass

    def toStr(self, value):
        pass

class ColumnDfn(object):
    """To define columns, if size is None, this is an autosize column"""
    def __init__(self,title, field, size=None, _type=DataType(), readonly=False):
        self.label = title
        self.field = field
        self.size = size
        self.type = _type
        self.readonly = readonly

class NamedFieldsGrid(gridlib.Grid):
    """This is the main class, to fast use of a grid"""
    def __init__(self, parent):
        gridlib.Grid.__init__(self, parent,  wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
        #'color defaults and styels'
        self.colours={'selected': wx.YELLOW, 'error': wx.RED}
        self.oddRow = gridlib.GridCellAttr()
        self.oddRow.SetBackgroundColour(wx.Colour( 235, 255, 215 ))
        self.evenRow = gridlib.GridCellAttr()
        self.evenRow.SetBackgroundColour(wx.Colour(255, 255, 255))
        #init rows(number of grid initial rows),
        self._initialRows=10
        self._columnData=[] # (list of definition of columns)
        self.fields = {}  # dict of fields. Used on class RowData
        self.totalsize = 0 #sum of size of columns with fixed sizes
        self.autosize = [] #list of columns with variable sizes
        self.hotkeys = False
        self.custom_clicks = {}
        self.rowdata = RowData(self)

    def __getitem__(self, item):
        'return a dict-like object if has some data, else return None'
        if item >= self.GetNumberRows() or item < 0:
            raise KeyError('Row out of boundaries',item)
        else:
            self.rowdata.row = item
            if self.rowdata.isEmpty():
                return False
            else:
                return self.rowdata

    def __setitem__(self, item, value):
        'accepts a dict object a use it to update values on the grid'
        if item >= self.GetNumberRows() or item < 0:
            raise KeyError('Row out of boundaries', item)
        else:
            self.rowdata.row = item
            for item, v in value.items():
                self.rowdata[item] = v

    def __delitem__(self, item):
        if isinstance(item, slice):
            for i in range(*item.indices(self.__len__())):
                self.__delitem__(i)
        else:
            if item >= self.GetNumberRows() or item < 0:
                raise KeyError('Row out of boundaries',item)
            else:
                self.rowdata.row = item
                if not self.rowdata.isEmpty():
                    for col in range(self.GetNumberCols()):
                        self.SetCellValue(item, col, '')

    def curRow(self):
        'returns a handler of current selected row'
        self.rowdata.row = self.GetGridCursorRow()
        return self.rowdata

    def appendRow(self, value):
        'put data on the next empty row'
        empty_row = -1
        for row in range(self.GetNumberRows()):
            self.rowdata.row = row
            if self.rowdata.isEmpty():
                empty_row = row
                break
        if empty_row == -1:
            empty_row = self.CreateNewRow()
        if empty_row >= 0:
            self.rowdata.row = empty_row
            for key,v in value.items():
                self.rowdata[key]=v
        return empty_row

    @property
    def oddColor(self):
        return self.oddRow.GetBackgroundColour()
    @oddColor.setter
    def oddColor(self, color):
        self.oddRow.SetBackgroundColour(color)
    @property
    def evenColor(self):
        return self.evenRow.GetBackgroundColour()
    @evenColor.setter
    def evenColor(self, color):
        self.evenRow.SetBackgroundColour(color)
    @property
    def selectedColor(self):
        return self.colours['selected']
    @selectedColor.setter
    def selectedColor(self, color):
        self.colours['selected']=color
    @property
    def errorColor(self):
        return self.colours['error']
    @errorColor.setter
    def errorColor(self, color):
        self.colours['error']=color
    @property
    def validatorFunc(self):
        'Callback function to validate a row'
        if hasattr(self,'_validator_fn'):
            return self._validator_fn
        else:
            return None

    @validatorFunc.setter
    def validatorFunc(self,function):
        self._validator_fn = function

    def appendCol(self, data):
        'to define the structure of the data. Can be used only when doing initial format'
        if isinstance(data, list):
            for col in data:
                self.appendCol(col)
        elif isinstance(data, ColumnDfn):
            self._columnData.append(data)
        else:
            col = ColumnDfn()
            col.label = data[0]
            col.field = data[1]
            col.size = data[2]
            col.type = data[3]
            self._columnData.append(col)

    def create(self):
        'create and format all the grid, bind all the events'
        for idx, col in enumerate(self._columnData):
            self.fields[col.field] = (idx, col)
            if col.size:
                self.totalsize += col.size
            else:
                self.autosize.append(idx)
        self.CreateGrid(self._initialRows, len(self._columnData))
        self.height_row = int(self.GetRowSize(1)*1.25)  #25% more on row heights
        self.SetRowLabelSize(0)  #don't use row labels
        self.SetSelectionMode(gridlib.Grid.SelectRows)  #select the whole row

        for col, item in enumerate(self._columnData):
            self.SetColLabelValue(col, item.label)
            if item.size:
                self.SetColSize(col, item.size)
        for row in range(self._initialRows):
            self.FormatRows(row)  #assign even-odd colours, renderers and editors
        if len(self.autosize):
            self.Bind( wx.EVT_SIZE, self.OnSize ) #to autosize columns
        self.Bind(gridlib.EVT_GRID_CELL_LEFT_DCLICK, self.OnLeftDClick) #to use only single click, not double
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)  #to process enter key
        if hasattr(self, '_validator_fn'):
            self._lastValidatedRow = -1  #initial validated row
            self._errorData = None  #initial value of error coords
            self.Bind(gridlib.EVT_GRID_SELECT_CELL, self.ValidateRow) #perform validation when move cursor
            self.Bind(wx.EVT_IDLE, self.MoveToCellError) #move cursor and color row
        else:
            self.Bind(gridlib.EVT_GRID_SELECT_CELL, self.IluminateRow) #paint selected row
            #self.Bind(gridlib.EVT_GRID_CELL_CHANGE, self.OnCellChange)
        if self.custom_clicks:
            self.Bind(gridlib.EVT_GRID_CELL_LEFT_CLICK, self.OnCellLeftClick)
        self.ForceRefresh()

    def FormatRows(self, row):
        'set all the format options, height, colors, renderers, editors'
        self.SetRowSize(row, self.height_row)
        self.SetRowLabelValue(row, '')
        for col,item in enumerate(self._columnData):
            self.SetCellRenderer(row, col, item.type.renderer())
            if item.type.editor() and item.readonly is False:
                self.SetCellEditor(row, col, item.type.editor())
            else:
                self.SetReadOnly(row, col, True)
        if row%2 == 1:
            self.SetRowAttr(row, self.oddRow)
        else:
            self.SetRowAttr(row, self.evenRow)

    def IluminateRow(self,evt):
        'use this ONLY when there are no validation'
        self.SelectRow(evt.GetRow())
        self.SetSelectionBackground(self.colours['selected'])
        self.SetSelectionForeground(wx.BLACK)

    # I do this because I don't like the default behaviour of not starting the
    # cell editor on double clicks, but only a second click.
    def OnLeftDClick(self, evt):
        if self.CanEnableCellControl():
            self.EnableCellEditControl()

    def OnCellLeftClick(self, evt):
        if evt.GetCol() in self.custom_clicks.keys():
            self.rowdata.row = evt.GetRow()
            self.custom_clicks[evt.GetCol()](self.rowdata)
        else:
            evt.Skip()

    def OnSize(self,event):
        'recalculate proportional with on resizable columns'
        width=self.GetSize()[0]-self.GetRowLabelSize()-self.totalsize
        for col in self.autosize:
            self.SetColSize(col,width/len(self.autosize))

    def OnKeyDown(self, evt):
        """process hotkey if they are configured
        to process ENTER key to move to next cell or to create new rows"""
        if self.hotkeys:
            function = self.hotkeys.onChar(evt.GetKeyCode(), self.GetGridCursorCol())
            if function:
                self.rowdata.row=self.GetGridCursorRow()
                function(self.rowdata)
                return

        if evt.GetKeyCode() != wx.WXK_RETURN:
            evt.Skip()
            return
        if evt.ControlDown():   # the edit control needs this key
            evt.Skip()
            return
        self.DisableCellEditControl()
        success = self.MoveCursorRight(evt.ShiftDown())
        if not success:
            newRow = self.GetGridCursorRow() + 1
            if newRow < self.GetTable().GetNumberRows():
                self.SetGridCursor(newRow, 0)
                self.MakeCellVisible(newRow, 0)
            else:
                self.CreateNewRow()
            #here I create a new row

    def CreateNewRow(self):
        newRow = self.GetTable().GetNumberRows()
        success = self.GetTable().AppendRows(1)
        if success:
            self.ForceRefresh()
            self.FormatRows(newRow)
            self.SetGridCursor(newRow, 0)
            self.MakeCellVisible(newRow, 0)
            return newRow
        return None

    def ValidateRow(self,evt):
        'call external callback function to evaluate validation'
        row, msg = evt.GetRow(), None
        if self._lastValidatedRow >= 0 and row != self._lastValidatedRow:
            self.rowdata.row = self._lastValidatedRow
            if not self.rowdata.isEmpty():
                field, msg = self._validator_fn(self.rowdata)
                if not msg is None:
                    col = 0
                    if field:
                        col = self.fields[field][0]
                    self._errorData = (self._lastValidatedRow, col)
        if msg is None:
            self._lastValidatedRow = row
            self.SelectRow(row)
            self.SetSelectionBackground(self.colours['selected'])
            self.SetSelectionForeground(wx.BLACK)
            evt.Skip()
            return False
        return True

    def MoveToCellError(self, evt):
        'to move cursor and paint the whole row on error'
        if not self._errorData is None:
            row, col = self._errorData
            self.DisableCellEditControl()
            self.SetGridCursor(self._lastValidatedRow,col)
            self.MakeCellVisible(self._lastValidatedRow,col)
            self.SelectRow(self._lastValidatedRow)
            self.SetSelectionBackground(self.colours['error'])
            self._errorData = None
            return True
        return False

    def __repr__(self):
        'return a nice string repr to all of the grid data'
        my_list=[]
        for row in range(self.GetNumberRows()):
            self.rowdata.row = row
            if self.rowdata.isEmpty():
                my_list.append('%02d) %r'%(row, self.rowdata))
        return '\n'.join(my_list)

    def __iter__(self):
        for row in range(self.__len__()):
            yield self.__getitem__(row)

    def __len__(self):
        for q in range(self.GetNumberRows()-1, 0, -1):
            self.rowdata.row = q
            if self.rowdata.isEmpty():
                return q+1
        return 0



class RowData(dict):
    """a dict-like class to easy access of data. dataitems return a real dict,
    __getitem__ return data from row, __getattr__ return data as an attribute"""
    def __init__(self, my_Grid):
        self._grid = my_Grid
        self.row = 0 #from which row can be get and set all the data
        self.initialised = True #to access dict items as class properties

    def update(self, data):
        for key, value in data.items():
            self.__setitem__(key, value)

    def dataitems (self):
        """creates a dict to put all the data in the correspondent format
        self.m_grid1[row+1]=self.m_grid1[row].dataitems()"""
        data = {}
        for (col,item) in self._grid.fields.values():
            data[item.field] = item.type.fromStr(self._grid.GetCellValue(self.row, col))
        return data

    def __len__(self):
        return len(self._grid.fields)

    def __getitem__(self, key):
        'get items from self.row row and key field'
        col, item = self._grid.fields[key]
        value = self._grid.GetCellValue(self.row, col)
        return item.type.fromStr(value)

    def __setitem__(self, key, value):
        'set items on self.row row and key field'
        col, item = self._grid.fields[key]
        formatted = item.type.toStr(value)
        self._grid.SetCellValue(self.row, col, formatted)

    def __repr__(self):
        'return a string representing the data'
        return repr(self.dataitems())

    def __getattr__(self, item):
        """Maps values to attributes.
        Only called if there *isn't* an attribute with this name
        """
        try:
            return self.__getitem__(item)
        except KeyError:
            raise AttributeError(item)

    def __setattr__(self, item, value):
        """Maps attributes to values.
        Only if we are initialised
        """
        if not self.__dict__.has_key('initialised'):  # this test allows attributes to be set in the __init__ method
            return dict.__setattr__(self, item, value)
        elif self.__dict__.has_key(item):       # any normal attributes are handled normally
            dict.__setattr__(self, item, value)
        else:
            self.__setitem__(item, value)

    def isEmpty(self):
        for col in range(self.__len__()):
            if self._grid.GetCellValue(self.row,col).strip():
                return False
        return True

class HotKeys(object):
    """when some of the hot key in the dict is used,
    returns the function, else return false"""
    def __init__(self, data_dict):
        self.keys={}
        for key, value in data_dict.items():
            if isinstance(value, tuple):
                self.keys[key] = value
            else:
                self.keys[key] = ('all', value)

    def onChar(self, key, col):
        try:
            pair=self.keys[key]
            if pair[0] == 'all' or pair[0] == col:
                return pair[1]
        except KeyError:
            pass
        return False


