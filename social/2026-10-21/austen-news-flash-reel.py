"""Storm Austen news-flash Reel: 1080x1920, 13 s, 30 fps, from the news-flash card's own parts."""
import subprocess, math, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
S='/tmp/claude-0/-home-claude/41e73692-fe8f-5040-940a-5ba17b9f7b41/scratchpad'
F=S+'/fonts/node_modules/@fontsource/'
BSD='/home/claude/bog-standard/brand/fonts/'
W,H,FPS,DUR=1080,1920,30,13.0
N=int(DUR*FPS)
INK=(34,40,31); TEAL=(36,92,96); ORANGE=(232,96,34); PAPER=(231,223,198); BROWN=(110,72,48); SOFT=(70,74,60)
big=lambda s: ImageFont.truetype(BSD+'bsd900.ttf',s); big8=lambda s: ImageFont.truetype(BSD+'bsd800.ttf',s)
mono=lambda s: ImageFont.truetype(BSD+'plexmono600.ttf',s)
cav=lambda s: ImageFont.truetype(F+'caveat/files/caveat-latin-700-normal.woff2',s)
plexb=lambda s: ImageFont.truetype(F+'ibm-plex-sans/files/ibm-plex-sans-latin-500-normal.woff2',s)
plex=lambda s: ImageFont.truetype(F+'ibm-plex-sans/files/ibm-plex-sans-latin-400-normal.woff2',s)

def ease(t): t=max(0.0,min(1.0,t)); return t*t*(3-2*t)
def seg(t,a,b): return ease((t-a)/(b-a))
def win(t,a,b,f=0.25):
    if t<a or t>b: return 0.0
    return min(1.0,(t-a)/f,(b-t)/f)

# paper with grid, as the cards
BG=Image.new('RGB',(W,H),PAPER); d=ImageDraw.Draw(BG)
for x in range(0,W,30): d.line([(x,0),(x,H)],fill=(222,213,186))
for y in range(0,H,30): d.line([(0,y),(W,y)],fill=(222,213,186))

# logo from the house cards
src=Image.open('/home/claude/bog-standard-weekly/social/2026-10-15/07-explainer.png').convert('RGBA').crop((40,36,430,170))
la=np.asarray(src).copy(); dist=np.abs(la[...,:3].astype(int)-np.array(PAPER)).sum(-1)
la[...,3]=np.clip((dist-40)*4,0,255).astype(np.uint8)
LOGO=Image.fromarray(la).resize((585,201),Image.LANCZOS)

def put(layer, xy, txt, fnt, fill, alpha=1.0, scale=1.0, anchor='la'):
    if alpha<=0: return
    bb=fnt.getbbox(txt, anchor=anchor if anchor!='mm' else None)
    tmp=Image.new('RGBA',(int(fnt.getlength(txt))+40, int(fnt.size*1.5)+40),(0,0,0,0))
    ImageDraw.Draw(tmp).text((20,20),txt,font=fnt,fill=fill+(255,))
    box=tmp.getbbox()
    if box: tmp=tmp.crop(box)
    if scale!=1.0: tmp=tmp.resize((max(1,int(tmp.width*scale)),max(1,int(tmp.height*scale))),Image.BICUBIC)
    if alpha<1: tmp.putalpha(tmp.getchannel('A').point(lambda v:int(v*alpha)))
    x,y=xy
    if anchor=='mm': x,y=int(x-tmp.width/2),int(y-tmp.height/2)
    elif anchor=='rm': x,y=int(x-tmp.width),int(y-tmp.height/2)
    elif anchor=='lm': y=int(y-tmp.height/2)
    layer.alpha_composite(tmp,(int(x),int(y)))

TICK='STORM AUSTEN  ·  STORM WATCH IS ON  ·  WED 21 OCT, 18:40  ·  '
TF=mono(34); TU=TF.getlength(TICK)
TSPEED=2*TU/DUR   # two whole units over the reel, so the last frame matches the first
SMALL=[
 'A discharge report is not by itself proof of a permit breach.',
 '\u201cDuring Storm Austen\u201d is a window of time, not a cause: overflows',
 'are allowed to operate in heavy rain. Our record of the nine English',
 'companies\u2019 live feeds (Stream / Water UK), 18:40 UK, Wed 21 Oct 2026.',
 'Provisional. England only; Scottish Water separate. Hours, not volume.',
]

def frame(t):
    img=BG.copy().convert('RGBA'); L=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(L)
    # header bar + live dot (pulses)
    d.rectangle((0,0,W,230),fill=INK+(255,))
    pr=27+5*math.sin(t*2*math.pi/1.3*2)   # period 0.65 s -> 20 pulses in 13 s, loops
    d.ellipse((70-pr,115-pr,70+pr,115+pr),fill=ORANGE+(255,))
    put(L,(120,115),'NEWS FLASH',big(150),PAPER,anchor='lm',scale=1.0)
    # ticker
    d.rectangle((0,230,W,310),fill=TEAL+(255,))
    off=(t*TSPEED)%TU
    x=-off
    while x<W:
        d.text((x,270),TICK,font=TF,fill=PAPER+(255,),anchor='lm'); x+=TU
    # the number: on from frame 0, a little punch every loop start
    punch=1+0.06*math.exp(-t*8)*math.sin(t*30) if t<1 else 1.0
    put(L,(W//2,555),'157',big(450),INK,anchor='mm',scale=punch)
    for i,line in enumerate(['storm overflow monitors in England','reporting a discharge at 18:40,','during Storm Austen’s window.']):
        put(L,(W//2,815+i*58),line,plexb(46),INK,anchor='mm')
    # gauge: 0 .. 400, storm watch at 150, storm at 400; fills to 157 from 2.4 s
    ga=win(t,2.3,11.6,0.3)
    if ga>0:
        x0,x1,y0=90,990,1050; sc=lambda v: x0+(x1-x0)*v/400
        a=int(255*ga)
        d.rectangle((x0,y0,x1,y0+70),outline=INK+(a,),width=4)
        fill=157*seg(t,2.5,3.6)
        d.rectangle((x0+4,y0+4,max(x0+4,sc(fill)),y0+66),fill=(TEAL if fill<150 else ORANGE)+(a,))
        for v,lab in ((150,'storm watch 150'),(400,'storm 400')):
            xv=sc(v); d.line((xv,y0-18,xv,y0+88),fill=INK+(a,),width=5)
        put(L,(sc(150),y0+125),'storm watch: 150',cav(44),INK,alpha=ga,anchor='mm')
        put(L,(x1,y0+125),'storm: 400',cav(44),INK,alpha=ga,anchor='rm')
        put(L,(sc(fill),y0-45),f'{int(round(fill))}',big8(52),INK,alpha=ga*seg(t,2.5,2.8),anchor='mm')
    put(L,(W//2,1255),'Past our “storm watch” line.',cav(76),ORANGE,alpha=win(t,3.8,11.6,0.25),
        scale=1+0.25*math.exp(-max(0,t-3.8)*9)*math.cos(max(0,t-3.8)*18) if t>=3.8 else 1, anchor='mm')
    put(L,(W//2,1335),'The 18:40 departures board: busy.',cav(62),TEAL,alpha=win(t,5.2,11.6,0.25),anchor='mm')
    # small print, throughout
    for i,line in enumerate(SMALL):
        put(L,(W//2,1400+i*34),line,plex(27),SOFT,anchor='mm')
    img.alpha_composite(L)
    # end card
    ca=win(t,7.6,12.4,0.45)
    if ca>0:
        img.alpha_composite(Image.new('RGBA',(W,H),PAPER+(int(252*ca),)))
        C=Image.new('RGBA',(W,H),(0,0,0,0))
        lg=LOGO.copy(); lg.putalpha(lg.getchannel('A').point(lambda v:int(v*ca)))
        C.alpha_composite(lg,((W-lg.width)//2,430))
        put(C,(W//2,780),'More rain is forecast.',cav(90),INK,alpha=win(t,7.9,12.4,0.3),anchor='mm')
        put(C,(W//2,880),'Is the overflow near you on the board?',cav(66),TEAL,alpha=win(t,8.3,12.4,0.3),anchor='mm')
        ua=win(t,8.7,12.4,0.3)
        put(C,(W//2,1050),'BOGSTANDARD.UK',big(130),INK,alpha=ua,anchor='mm')
        put(C,(W//2,1180),'/STORMS/AUSTEN',big(130),TEAL,alpha=ua,anchor='mm')
        put(C,(W//2,1320),'live count + rain forecast for your area',plexb(40),SOFT,alpha=win(t,9.1,12.4,0.3),anchor='mm')
        img.alpha_composite(C)
        # keep the small print legible over the veil
        P=Image.new('RGBA',(W,H),(0,0,0,0))
        for i,line in enumerate(SMALL): put(P,(W//2,1400+i*34),line,plex(27),SOFT,alpha=ca,anchor='mm')
        img.alpha_composite(P)
    return img.convert('RGB')

if __name__=='__main__':
    out=sys.argv[1]
    if len(sys.argv)>2:
        for ts in sys.argv[2:]: frame(float(ts)).save(f'{S}/reel/still_{ts}.png')
        sys.exit()
    cmd=['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
         '-f','lavfi','-i','anullsrc=r=44100:cl=stereo','-shortest','-c:v','libx264','-preset','medium','-crf','18',
         '-pix_fmt','yuv420p','-profile:v','high','-movflags','+faststart','-c:a','aac','-b:a','128k',out]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    for i in range(N): p.stdin.write(frame(i/FPS).tobytes())
    p.stdin.close(); p.wait(); print('done',p.returncode)
