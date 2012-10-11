from reportlab.graphics.shapes import Rect
from reportlab.lib.colors import PCMYKColor, PCMYKColorSep
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import getFont,stringWidth,registerFont
from reportlab.graphics.charts.textlabels import _text2Path

from svglib import svg2rlg
import qrcode
from qrcode.image.svg import SvgImage

registerFont(TTFont('OpenSans','/home/robin/.fonts/opensans/OpenSans-Regular-webfont.ttf'))
registerFont(TTFont('OpenSansBold','/home/robin/.fonts/opensans/OpenSans-Bold-webfont.ttf'))

PT_PER_MM = 360.0/127.0

black = PCMYKColor(0, 0, 0, 100)
grey   = PCMYKColor( 0.0, 0.0, 0.0, 70 )

# PCMYKColorSep( 0.0, 100.0, 91.0, 0.0, spotName='PANTONE 485 CV',density=100) # what is this?

class Text(object):
    font = 'OpenSans'

    def __init__(self,text,font=None,colour=None,x=0):
        font = font if font else self.font
        self.font = font
        self.width = 40*PT_PER_MM
        self.text = text
        str_width = stringWidth(text,font, 1000)
        self.font_size = self.scale = self.width/(str_width/1000)
        self.height = self.height_of(text) * self.scale
        self.colour = colour if colour else black
        self.x = x

    def height_of(self,s):
        x1,y1,x2,y2 = _text2Path(s,fontName=self.font,fontSize=1).getBounds()
        return (y2+y1/5)+0.3
        
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
        
    def text(self,text):
        self.text_list.append(text)

    @property
    def total_text_height(self):
        return sum(text.height for text in self.text_list)

    def draw(self):
        ctx = self.ctx
        box_h = self.total_text_height

        for text in self.text_list:
            ctx.setFillColor(text.colour)
            ctx.setFont(text.font,text.font_size)
            ctx.drawString(text.x,box_h-text.height,str(text))
            box_h -= text.height

    def move_texts(self,x):
        for text in self.text_list:
            text.x = x

    def move(self,x,y):
        self.ctx.translate(x,y)

    def save(self):
        self.ctx.save()

card = Card()
card.text(Text('Paul Cartwright','OpenSansBold'))
card.text(Text('Software Engineer'))
card.text(Text('paul@obsi.com.au',colour=grey))
card.text(Text('0403 048 754',colour=grey))
url_name = 'ploy'

qr = qrcode.QRCode(border=0)
qr.add_data('http://obsi.com.au/%s/' % url_name)
qr.make(fit=True)
img = qr.make_image(image_factory=SvgImage)
img.save('qr.svg')

qr_width = 25*PT_PER_MM
qr_scale = card.total_text_height/qr_width
qr_width = qr_width * qr_scale
card.move_texts(qr_width+2*PT_PER_MM)
drawing = svg2rlg('qr.svg')

card.move(card.width/2-(qr_width+2*PT_PER_MM+card.text_list[0].width)/2,card.height/2-card.total_text_height/2)
card.draw()
card.ctx.scale(qr_scale,qr_scale)
drawing.drawOn(card.ctx,0,0)

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
