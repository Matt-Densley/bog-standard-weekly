from PIL import Image, ImageDraw, ImageFont
S='/tmp/claude-0/-home-claude/41e73692-fe8f-5040-940a-5ba17b9f7b41/scratchpad'
F=S+'/fonts/node_modules/@fontsource/'
BS='/home/claude/bog-standard/brand/fonts/bsd900.ttf'
BS8='/home/claude/bog-standard/brand/fonts/bsd800.ttf'
MONO='/home/claude/bog-standard/brand/fonts/plexmono600.ttf'
src=Image.open('/home/claude/bog-standard-weekly/social/2026-10-15/07-explainer.png').convert('RGB')
W,H=src.size
img=src.copy(); d=ImageDraw.Draw(img)
band=src.crop((0,1060,W,1140))
for y in range(0,H,80): img.paste(band,(0,y))
ink=(34,40,31); teal=(36,92,96); orange=(232,96,34); paper=(231,223,198)
big=lambda s: ImageFont.truetype(BS,s); big8=lambda s: ImageFont.truetype(BS8,s)
cav=lambda s: ImageFont.truetype(F+'caveat/files/caveat-latin-600-normal.woff2',s)
plex=lambda s: ImageFont.truetype(F+'ibm-plex-sans/files/ibm-plex-sans-latin-400-normal.woff2',s)
plexb=lambda s: ImageFont.truetype(F+'ibm-plex-sans/files/ibm-plex-sans-latin-500-normal.woff2',s)
mono=lambda s: ImageFont.truetype(MONO,s)
x=48
# top: ink bar "NEWS FLASH" with a live dot, like a departures board ticker
d.rectangle((0,0,W,150),fill=ink)
d.ellipse((x,52,x+46,98),fill=orange)
d.text((x+70,75),'NEWS FLASH',font=big(96),fill=paper,anchor='lm')
d.text((W-x,75),'BOG STANDARD',font=big8(44),fill=paper,anchor='rm')
# ticker strip
d.rectangle((0,150,W,206),fill=teal)
d.text((x,178),'STORM AUSTEN  ·  STORM WATCH IS ON  ·  WED 21 OCT, 18:40',font=mono(28),fill=paper,anchor='lm')
# the number
d.text((x,232),'157',font=big(330),fill=ink)
d.text((x,575),'storm overflow monitors in England',font=plexb(40),fill=ink)
d.text((x,625),'reporting a discharge at 18:40, the most',font=plexb(40),fill=ink)
d.text((x,675),'at once so far in Storm Austen’s window.',font=plexb(40),fill=ink)
d.text((600,330),'the 18:40',font=cav(64),fill=teal)
d.text((600,400),'departures board:',font=cav(64),fill=teal)
d.text((600,470),'busy.',font=cav(64),fill=teal)
d.text((x,738),'Past our “storm watch” line of 150.',font=cav(50),fill=orange)
# forecast block
d.line((x,815,W-x,815),fill=ink,width=3)
d.text((x,835),'RAIN FORECAST TO SUNDAY 01:00',font=big(54),fill=ink)
rows=[('South West Water',55.6),('Wessex Water',45.9),('Southern Water',36.7),('England (29 points)',31.3)]
top=55.6; y=905
for name,mm in rows:
    d.text((x,y),name,font=plexb(32),fill=ink)
    bx=x+330; bw=int((W-x-150-bx)*mm/top)
    d.rectangle((bx,y+8,bx+(W-x-150-bx),y+34),outline=ink,width=2)
    d.rectangle((bx,y+8,bx+bw,y+34),fill=teal if not name.startswith('England') else ink)
    d.text((W-x,y+21),f'{mm} mm',font=big8(38),fill=ink,anchor='rm')
    y+=58
d.text((x,y+4),'Met Office forecast at our fixed points, 17:00 run. Rain, not discharges.',font=plex(22),fill=ink)
d.text((x,1180),'BOGSTANDARD.UK/STORMS/AUSTEN',font=big(60),fill=ink)
small=('“During Storm Austen” means a window of time, not a cause. Storm overflows are allowed to operate in heavy rain. '
       'Live count from the nine English water companies’ feeds; provisional; a discharge report is not by itself proof of a permit breach.')
words=small.split(); line=''; ly=1256
for wd in words:
    t=(line+' '+wd).strip()
    if d.textlength(t,font=plex(22))>W-2*x: d.text((x,ly),line,font=plex(22),fill=ink); ly+=29; line=wd
    else: line=t
d.text((x,ly),line,font=plex(22),fill=ink)
img.save(S+'/austen/austen-flash.png'); print(ly)
