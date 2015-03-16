import os
from wx.tools.img2py import img2py

print os.curdir
file_name="catalog.py"
f=open(file_name,"w")
f.write('from wx.lib.embeddedimage import PyEmbeddedImage\n\n')
for name in os.listdir(os.curdir):
    if name.endswith(".PNG"):
        print name
        nom=name.split('.')[0]
        print nom
        img2py(name,file_name, imgName=nom, catalog=True, append=True)