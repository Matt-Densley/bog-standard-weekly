import sys
from PIL import Image, ImageDraw, ImageFont
S='/tmp/claude-0/-home-claude/41e73692-fe8f-5040-940a-5ba17b9f7b41/scratchpad'
F=S+'/fonts/node_modules/@fontsource/'
BS='/home/claude/bog-standard/brand/fonts/bsd900.ttf'
src=Image.open('/home/claude/bog-standard-weekly/social/2026-10-15/07-explainer.png').convert('RGB')
W,H=src.size
img=src.copy()
d=ImageDraw.Draw(img)
bg=src.getpixel((540,1110))
# clear everything below the header, keep the paper grid by copying an empty band
band=src.crop((0,1060,W,1140))
for y in range(180,H,80): img.paste(band,(0,y))
ink=(34,40,31); teal=(36,92,96); brown=(110,72,48); orange=(232,96,34)
big=lambda s: ImageFont.truetype(BS,s)
cav=lambda s: ImageFont.truetype(F+'caveat/files/caveat-latin-600-normal.woff2',s)
plex=lambda s: ImageFont.truetype(F+'ibm-plex-sans/files/ibm-plex-sans-latin-400-normal.woff2',s)
x=48
d.text((x,195),'STORM',font=big(190),fill=ink)
d.text((x,370),'AUSTEN',font=big(190),fill=teal)
d.text((x,575),'Due late Thursday into Friday.',font=cav(52),fill=ink)
d.text((x,635),'Here’s what to watch on the map.',font=cav(52),fill=ink)
rows=[('heavy rain','fills the older "combined" sewers'),
      ('storm overflows','are allowed to open when they can’t keep up'),
      ('every monitor','reporting a discharge shows on our map, live')]
y=750
for i,(a,b) in enumerate(rows):
    d.ellipse((x,y+12,x+40,y+52),outline=ink,width=3)
    d.text((x+20,y+32),str(i+1),font=big(30),fill=ink,anchor='mm')
    d.text((x+60,y),a,font=cav(50),fill=teal if i<2 else brown)
    w=d.textlength(a,font=cav(50))
    d.text((x+60+w+18,y+6),b,font=cav(42),fill=ink)
    y+=92
d.line((x,y+52,x+44,y+52),fill=orange,width=4); d.line((x+30,y+40,x+44,y+52),fill=orange,width=4); d.line((x+30,y+64,x+44,y+52),fill=orange,width=4)
d.text((x+60,y+20),'departures may be busy. Check yours.',font=cav(46),fill=orange)
d.text((x,1150),'BOGSTANDARD.UK/STORMS/AUSTEN',font=big(62),fill=ink)
small=('“During Storm Austen” means a window of time, not a cause. Figures will be what the '
       'monitors of nine water companies in England report, every ten minutes: provisional, hours not '
       'volume, and not by themselves proof of a permit breach. Scottish Water shown separately.')
# wrap
words=small.split(); line=''; ly=1232
for wd in words:
    t=(line+' '+wd).strip()
    if d.textlength(t,font=plex(22))>W-2*x: d.text((x,ly),line,font=plex(22),fill=ink); ly+=30; line=wd
    else: line=t
d.text((x,ly),line,font=plex(22),fill=ink)
img.save(S+'/austen/austen-t0.png')
print(img.size, ly)
