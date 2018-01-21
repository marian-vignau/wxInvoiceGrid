# -*- coding: utf-8 -*-
"""
-------------------------------------------------------------------------------
 Name:       InvoiceGrid
 Purpose:    demo to show howto do a easy invoice grid


 Author:      mvignau

 Created:     05/11/2014
 Copyright:   (c) mvignau 2015

-------------------------------------------------------------------------------"""
#!/usr/bin/env python

import  wx
import locale
import InvoiceGrid as grid

from wx.lib.embeddedimage import PyEmbeddedImage
LUPA = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAACgAAAAaCAIAAABKLomcAAAAAXNSR0IArs4c6QAAAARnQU1B"
    "AACxjwv8YQUAAAAgY0hSTQAAeiYAAICEAAD6AAAAgOgAAHUwAADqYAAAOpgAABdwnLpRPAAA"
    "ASVJREFUSEvtlkEOgjAQRedWJHIUFoZruIFwCFeEK7AkcYNLlyy4jw4dqGVoC61NXWjTGKy0"
    "r//PTCvAF9szepvFInccHtF6WZZ/MHNbTbuAgbBZTci70mgkCN4IRgD+JjNd0mnC52wbmKiq"
    "YnrWg7tLqkQlLVrcXHOeh+ir2vVgclhLNbIFOK+V1esM18GRW5EAJFUXDbxIFOCsOa54a7Ic"
    "0bi9slrBTLo5FT23We0BXlktJW6jYALjjlghyU1g4C3JpQcP1xyA5ddOOTHRSKUJ+MkraiPr"
    "nVNLlu1nNb3BDpCF2gNMfRc8Dm11ciwnddH1Td2LOjawXS4359sJqUHYzmARggBsHzBj+53b"
    "nmBia1LscJj9wX5C5awfB6P8mO2L/+XhBaACxPk/69/aAAAAAElFTkSuQmCC")

class MyFrame1 ( wx.Frame ):

    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size(800,600 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )

        bSizer1 = wx.BoxSizer( wx.VERTICAL )
        #definition = myGrid(Columns)

        self.m_grid1 = grid.NamedFieldsGrid(self)

        bSizer1.Add( self.m_grid1, 1, wx.ALL|wx.EXPAND, 5 )

        self.m_button1 = wx.Button( self, wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer1.Add( self.m_button1, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )

        self.m_textCtrl1 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer1.Add( self.m_textCtrl1, 0, wx.ALL|wx.EXPAND, 5 )


        self.SetSizer( bSizer1 )
        self.Layout()

        self.Centre( wx.BOTH )
        self.m_button1.Bind(wx.EVT_BUTTON,self.ShowData)

    def ShowData(self,evt):
        row=self.m_grid1.GetGridCursorRow()
        if not self.m_grid1[row]:
            self.m_textCtrl1.SetValue('row %d is empty'%row)
        else:
            self.m_textCtrl1.SetValue(repr(self.m_grid1[row]))
            self.m_grid1[row+1]=self.m_grid1[row].dataitems()
        #print repr(self.m_grid1)
        print len(self.m_grid1)
        total=0.0
        for row_data in self.m_grid1:
            if row_data:
                total_prod=row_data.price*row_data.quantity
                row_data.total=total_prod
                total+=row_data.total
                print row_data.row, row_data
        data={'code': u'', 'quantity': 45, 'selected': False, 'price': 2.0, 'description': u'e', 'total': 90.0, 'units': None}
        e1=self.m_grid1.appendRow(data)
        #del self.m_grid1[:]

        #self.m_grid1.SetRowData(row+1, data)

    def OnCode(self, row_data):
        dlg = wx.SingleChoiceDialog(
                self, 'Test Single Choice', 'The Caption',
                ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight'],
                wx.CHOICEDLG_STYLE
                )

        if dlg.ShowModal() == wx.ID_OK:
            #self.log.WriteText('You selected: %s\n' % dlg.GetStringSelection())
            row_data.code=dlg.GetStringSelection()
        dlg.Destroy()

    def __del__( self ):
        pass
#---------------------------------------------------------------------------
def ValidateRow(row_data):
    field,msg=None, None
    if not row_data.description:
        field,msg='description',u'You must enter a description'
    elif row_data.quantity<=0:
        field,msg='quantity','Must enter a quantity'
    elif row_data.price<=0:
        field,msg='price','Must enter a price'
    if not msg is None:
        dlg = wx.MessageDialog(None, msg,
                               'Error validating the row',
                               wx.OK | wx.ICON_ERROR
                               #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                               )
        dlg.ShowModal()
        dlg.Destroy()
    else:
        row_data.total=row_data.price*row_data.quantity
    return field,msg

def ShowMe(rowdata):
    print 'Showme', rowdata


if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame1(None)

    editor=grid.ReadOnlyType()
    editor.onEdit = ShowMe
    Columns=[grid.ColumnDfn(u'Edi', 'edi', 40, grid.ButtonType(LUPA.GetBitmap())),
        grid.ColumnDfn(u'Code', 'code', 100, editor),
        grid.ColumnDfn(u'Description', 'description',None, grid.TextType()),
        grid.ColumnDfn(u'Quantity', 'quantity', 120,grid.NumberType(1,10000)),
        grid.ColumnDfn(u'Unit', 'units', 80,grid.ListType([('b.', 0),('kg', 1),('mt', 2)])),
        grid.ColumnDfn(u'Price', 'price', 150, grid.FloatType(6,2)),
        grid.ColumnDfn(u'Sel.', 'selected', 50, grid.BoolType()),
        grid.ColumnDfn(u'Total','total',150, grid.FloatType(6,2),readonly=True)
        ]

    import sys

    frame.m_grid1.appendCol(Columns)
    frame.m_grid1.hotkeys = grid.HotKeys({wx.WXK_F3: ShowMe, wx.WXK_RETURN: (0, ShowMe)})
    frame.m_grid1.custom_clicks = {0: ShowMe,1:frame.OnCode}
    frame.m_grid1.validatorFunc = ValidateRow
    frame.m_grid1.create()
    frame.Show(True)
    app.MainLoop()
