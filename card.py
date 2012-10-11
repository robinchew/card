from reportlab.graphics.shapes import Rect
from reportlab.lib.colors import PCMYKColor, PCMYKColorSep
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase.pdfmetrics import getFont,stringWidth
from reportlab.graphics.charts.textlabels import _text2Path

PT_PER_MM = 360.0/127.0

black = PCMYKColor(0, 0, 0, 100)
blue  = PCMYKColor(91.0,  43.0,  0.0, 0.0)
red   = PCMYKColorSep( 0.0, 100.0, 91.0, 0.0, spotName='PANTONE 485 CV',density=100)
red2   = PCMYKColor( 0.0, 100.0, 91.0, 0.0, knockout=0) #knockout does nothing?

class Card(object):
    width = 86*PT_PER_MM
    height = 54*PT_PER_MM
    box_h = 0
    font = 'Helvetica'
    def __init__(self):
        self.ctx = Canvas('test.pdf', (86*PT_PER_MM,54*PT_PER_MM))
        self.box_h = self.height
        
    def height_of(self,s):
        x1,y1,x2,y2 = _text2Path(s,fontName=self.font,fontSize=1).getBounds()
        print 'xyxy',x1,y1,x2,y2
        return (y2+y1/5)+0.3
        
    def draw(self,text):
        ctx = self.ctx
        box_w = 40*PT_PER_MM
        text_w = stringWidth(text, self.font, 1000)
        scale = box_w/(text_w/1000)
        text_h = self.height_of(text) * scale

        #print text_w,'/',text_w,'=',scale

        ctx.setFillColor(black)
        ctx.setFont(self.font, scale)
        ctx.drawString(0,self.box_h-text_h,text)

        self.box_h -= text_h

    def save(self):
        self.ctx.save()

card = Card()
card.draw('Paul Cartwright')
card.draw('Software Engineer')
card.draw('paul@obsi.com.au')
card.draw('0403 048 754')
card.save()

"""
c.setFillOverprint(True)
c.setFillColor(blue)
c.rect(25,25,100,100, fill=True, stroke=False)
c.setFillColor(red)
c.rect(100,75,100,100, fill=True, stroke=False)
c.setFillColor(black)
c.drawString(225,180, 'overprint w. plain CMYKColor (does not work)')
c.setFillColor(blue)
c.rect(225,25,100,100, fill=True, stroke=False)
c.setFillColor(red2)
c.rect(300,75,100,100, fill=True, stroke=False)
c.save()
"""
