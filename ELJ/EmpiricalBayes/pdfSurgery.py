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
        page = inputpdf.getPage(i)
        if i != 0:
            page.trimBox.lowerLeft = (0, 425)
            page.trimBox.upperRight = (675, 1225)
            page.cropBox.lowerLeft = (0, 450)
            page.cropBox.upperRight = (650, 1200)
        output.addPage(page)
        pdfName = os.path.join("ForUpload","McAuliffe"+pages[i]+".pdf")
        with open(pdfName, "wb") as outputStream:
            output.write(outputStream)
        if i != 0:
            os.system("pdftops -eps "+pdfName)
            os.remove(pdfName)
    else:
        mainOutput.addPage(inputpdf.getPage(i))


with open(os.path.join("ForUpload","manuscript.pdf"), "wb") as outputStream:
    mainOutput.write(outputStream)
