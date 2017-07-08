from pyPdf import PdfFileWriter, PdfFileReader
import os

inputpdf = PdfFileReader(open("EmpiricalBayes_forUpload.pdf", "rb"))

pages = {}
pages[0] = "TitlePage" 
fig = 1
for i in range(19,40):
    pages[i] = "Figure"+str(fig)
    fig +=1

tab = 1
for i in range(41,44):
    pages[i] = "Table"+str(tab)
    tab +=1

mainOutput = PdfFileWriter()
for i in xrange(inputpdf.numPages):
    if i in pages.keys():
        output = PdfFileWriter()
        output.addPage(inputpdf.getPage(i))
        with open(os.path.join("ForUpload",pages[i]+".pdf"), "wb") as outputStream:
            output.write(outputStream)
    else:
        mainOutput.addPage(inputpdf.getPage(i))


with open(os.path.join("ForUpload","manuscript.pdf"), "wb") as outputStream:
    mainOutput.write(outputStream)
