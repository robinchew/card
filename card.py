from reportlab.graphics.shapes import Rect
from reportlab.lib.colors import PCMYKColor, PCMYKColorSep
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import getFont,stringWidth,registerFont
from reportlab.graphics.charts.textlabels import _text2Path

from pdfrw import PdfReader
from pdfrw.buildxobj import pagexobj
from pdfrw.toreportlab import makerl

from svglib import svg2rlg
import qrcode
from qrcode.image.svg import SvgImage

registerFont(TTFont('OpenSans','/home/robin/.fonts/opensans/OpenSans-Regular-webfont.ttf'))
registerFont(TTFont('OpenSansBold','/home/robin/.fonts/opensans/OpenSans-Bold-webfont.ttf'))

PT_PER_MM = 360.0/127.0

blue = PCMYKColor(70, 0, 0, 100)
black = PCMYKColor(0, 0, 0, 100)
grey   = PCMYKColor( 0.0, 0.0, 0.0, 60 )

# PCMYKColorSep( 0.0, 100.0, 91.0, 0.0, spotName='PANTONE 485 CV',density=100) # what is this?

class Text(object):
    font = 'OpenSans'

    def __init__(self,text,font=None,colour=None,x=0,scale=None,width=None,):
        font = font if font else self.font
        self.font = font
        self.text = text

        if scale > 0:
            self.font_size = self.scale = scale
            self.width = stringWidth(text,font, scale)
        else:
            self.width = 40*PT_PER_MM
            str_width = stringWidth(text,font, 1000)
            self.font_size = self.scale = self.width/(str_width/1000)
        self.height = self.height_of(text) * self.scale

        self.colour = colour if colour else black
        self.x = x

    def height_of(self,s):
        x1,y1,x2,y2 = _text2Path(s,fontName=self.font,fontSize=1).getBounds()
        #print x1,y1,x2,y2,'-',y2+y1
        return y2 - 0.21 # 0.21 repesents the PT size difference between a capital and small letter 
        
    def __str__(self):
        return self.text

class Card(object):
    width = 86*PT_PER_MM
    height = 54*PT_PER_MM
    text_list = None
    font = 'Helvetica'
    text_spacing = 6
    contact_spacing = 9
    def __init__(self):
        self.ctx = Canvas('card.pdf', (86*PT_PER_MM,54*PT_PER_MM))
        self.text_list = []
        self.sub_text_list = []
        self.contacts = []
        
    def text(self,text):
        self.text_list.append(text)

    def sub_text(self,text):
        self.sub_text_list.append(text)

    @property
    def total_text_height(self):
        return sum(text.height for text in self.text_list) + (len(self.text_list)-1) * self.text_spacing

    def draw(self):
        ctx = self.ctx
        box_h = self.total_text_height

        for i,text in enumerate(self.text_list):
            extra_h = self.text_spacing if i >= 1 else 0
            ctx.setFillColor(text.colour)
            ctx.setFont(text.font,text.font_size)
            ctx.drawString(text.x,box_h-text.height-extra_h,str(text))
            box_h = box_h-text.height-extra_h

    def add_contact(self,text,pdf_filename):
        self.contacts.append((text,pdf_filename))

    @property
    def total_contact_height(self):
        return sum( text.height for contact,p in self.contacts) + (len(self.contacts)-1)*self.contact_spacing

    def draw_contacts(self):
        ctx = self.ctx

        ctx.saveState()
        for i,l in enumerate(self.contacts):
            text = l[0]
            pdf_filename = l[1]

            spacing = self.contact_spacing if i > 0 else 0
            ctx.translate(0,-(spacing+text.height))

            ctx = self.ctx
            ctx.setFillColor(text.colour)
            ctx.setFont(text.font,text.font_size)

            w = 17
            if '@' in str(text):
                # Draw character by character
                # in order to control colours
                ctx.setFillColor(black)
                for c in str(text):
                    if c == '@':
                        ctx.setFillColor(text.colour)
                    ctx.drawString(w,0,c)
                    w += stringWidth(c,text.font,text.scale)
            else:
                ctx.drawString(w,0,str(text))

            pdf = PdfReader(pdf_filename).pages[0]
            pdf = pagexobj(pdf)

            ctx.saveState()
            ctx.translate((12-pdf.w)/2,-(pdf.h-text.height)/2+1)
            ctx.doForm(makerl(ctx,pdf))
            ctx.restoreState()

        ctx.restoreState()

    def move_texts(self,x):
        for text in self.text_list:
            text.x = x

    def move(self,x,y):
        self.ctx.translate(x,y)

    def save(self):
        self.ctx.save()

###################
# NAME / POSITION #
###################

card = Card()
card.text(Text('Robin Chew','OpenSansBold',scale=6*PT_PER_MM))
card.text(Text('Software Engineer',colour=grey,scale=6*PT_PER_MM))
#card.sub_text(Text('robin@obsi.com.au',colour=grey,scale=3*PT_PER_MM))
#card.sub_text(Text('0403 048 754',colour=grey,scale=3*PT_PER_MM))

card.ctx.saveState()
#left_margin = card.width/2-card.text_list[0].width/2
left_margin = 10 * PT_PER_MM 
card.move(left_margin,card.height/2-card.total_text_height/2)
card.draw()
card.ctx.restoreState()

########
# LOGO #
########

card.ctx.saveState()
h = card.height/2+card.total_text_height/2
card.move(card.width-82-10*PT_PER_MM, h+((card.height-h-22.6)/2))
logo = PdfReader('logo.pdf').pages[0]
logo = pagexobj(logo)
card.ctx.doForm(makerl(card.ctx,logo))
card.ctx.restoreState()

#################
# EMAIL & PHONE #
#################

text = Text('robin@obsi.com.au',colour=grey,scale=3.5*PT_PER_MM)
card.add_contact(text,'email.pdf')

text = Text('04 0304 8574',colour=grey,scale=3.5*PT_PER_MM)
card.add_contact(text,'phone.pdf')


#card.ctx.saveState()
#card.move(left_margin,card.total_contact_height)
card.ctx.translate(left_margin,((card.height-card.total_text_height)/2-card.total_contact_height)/2+card.total_contact_height)
card.draw_contacts()

#card.ctx.restoreState()

########
# SAVE #
########

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
