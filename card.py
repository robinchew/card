from reportlab.graphics.shapes import Rect
from reportlab.lib.colors import PCMYKColor, PCMYKColorSep
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase.pdfmetrics import getFont,stringWidth,registerFont
from reportlab.graphics.charts.textlabels import _text2Path

#registerFont()

PT_PER_MM = 360.0/127.0

black = PCMYKColor(0, 0, 0, 100)
blue  = PCMYKColor(91.0,  43.0,  0.0, 0.0)
red   = PCMYKColorSep( 0.0, 100.0, 91.0, 0.0, spotName='PANTONE 485 CV',density=100)
red2   = PCMYKColor( 0.0, 100.0, 91.0, 0.0, knockout=0) #knockout does nothing?

class Text(object):
    font = 'Helvetica'

    def height_of(self,s):
        x1,y1,x2,y2 = _text2Path(s,fontName=self.font,fontSize=1).getBounds()
        #print 'xyxy',x1,y1,x2,y2
        return (y2+y1/5)+0.3
        
    def __init__(self,text,font=None):
        font = font if font else self.font
        self.font = font
        box_w = 40*PT_PER_MM
        self.text = text
        self.width = stringWidth(text,font, 1000)
        self.font_size = self.scale = box_w/(self.width/1000)
        self.height = self.height_of(text) * self.scale

    def __str__(self):
        return self.text

class Card(object):
    width = 86*PT_PER_MM
    height = 54*PT_PER_MM
    text_list = None
    font = 'Helvetica'
    def __init__(self):
        self.ctx = Canvas('test.pdf', (86*PT_PER_MM,54*PT_PER_MM))
        self.text_list = []
        
    def text(self,text,font=None):
        text = Text(text,font)
        self.text_list.append(text)

        #print text_w,'/',text_w,'=',scale

    def draw(self):
        ctx = self.ctx
        box_h = self.height
        for text in self.text_list:
            ctx.setFillColor(black)
            ctx.setFont(text.font,text.font_size)
            ctx.drawString(0,box_h-text.height,str(text))
            box_h -= text.height

    def move(self,x,y):
        self.ctx.translate(x,y)

    def save(self):
        self.ctx.save()

card = Card()
card.text('Paul Cartwright','Helvetica-Bold')
card.text('Software Engineer')
card.text('paul@obsi.com.au')
card.text('0403 048 754')

total_text_h = sum(text.height for text in card.text_list)

card.move(card.width/2-20*PT_PER_MM,-(card.height/2-total_text_h/2))
print card.width/2-20*PT_PER_MM,-(card.height/2-total_text_h/2)
print 'th',total_text_h
card.draw()
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
