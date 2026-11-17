"""Draw English schematic diagrams from shared SVG/PNG geometry; no measurements."""
from pathlib import Path
from html import escape
import math
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/figures'
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

class Diagram:
    def __init__(self, title, subtitle):
        self.image = Image.new('RGB', (1600, 940), '#ffffff')
        self.draw = ImageDraw.Draw(self.image)
        self.svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="940" viewBox="0 0 1600 940">', '<rect width="1600" height="940" fill="white"/>']
        self.text(40, 25, title, 34, True)
        self.text(40, 80, subtitle, 21)
    def text(self, x, y, value, size=22, bold=False, color='#182b43'):
        self.draw.text((x, y), value, font=ImageFont.truetype(BOLD if bold else FONT, size), fill=color)
        self.svg.append(f'<text x="{x}" y="{y+size}" font-family="DejaVu Sans, sans-serif" font-size="{size}" font-weight="{"bold" if bold else "normal"}" fill="{color}">{escape(value)}</text>')
    def panel(self, x,y,w,h,title):
        self.draw.rounded_rectangle((x,y,x+w,y+h),radius=12,fill='#f3f6fa',outline='#a5b6cb',width=2)
        self.svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="#f3f6fa" stroke="#a5b6cb" stroke-width="2"/>')
        self.text(x+16,y+12,title,24,True)
    def box(self,x,y,w,h,lines,color='#e5f0fd'):
        self.draw.rounded_rectangle((x,y,x+w,y+h),radius=9,fill=color,outline='#45658b',width=2)
        self.svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="{color}" stroke="#45658b" stroke-width="2"/>')
        top=y+(h-len(lines)*29)/2-3
        for n,line in enumerate(lines):
            size=22
            while size>16 and self.draw.textlength(line,font=ImageFont.truetype(BOLD if n==0 else FONT,size))>w-30:
                size-=1
            self.text(x+15,top+n*29,line,size,n==0)
    def arrow(self,points,dashed=False,color='#436080'):
        for a,b in zip(points,points[1:]):
            if dashed:
                dx=b[0]-a[0];dy=b[1]-a[1];length=math.hypot(dx,dy)
                for start in range(0,int(length),17):
                    end=min(length,start+10)
                    if length:self.draw.line((a[0]+dx*start/length,a[1]+dy*start/length,a[0]+dx*end/length,a[1]+dy*end/length),fill=color,width=3)
            else:self.draw.line((a,b),fill=color,width=3)
        a,b=points[-2:];angle=math.atan2(b[1]-a[1],b[0]-a[0]);tri=[b,(b[0]-12*math.cos(angle-.45),b[1]-12*math.sin(angle-.45)),(b[0]-12*math.cos(angle+.45),b[1]-12*math.sin(angle+.45))]
        self.draw.polygon(tri,fill=color)
        coords=' '.join(f'{x},{y}' for x,y in points); dash=' stroke-dasharray="10 7"' if dashed else ''
        self.svg.append(f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="3"{dash}/><polygon points="'+ ' '.join(f'{x},{y}' for x,y in tri)+f'" fill="{color}"/>')
    def save(self,name):
        OUT.mkdir(parents=True,exist_ok=True)
        self.image.save(OUT/(name+'.png'))
        (OUT/(name+'.svg')).write_text('\n'.join(self.svg+['</svg>'])+'\n')


def main():
    d=Diagram('MiniCPM-o 4.5: conceptual model components','A model example, not a universal Omni architecture or a measured timeline')
    for y,label in [(150,'Text'),(275,'Images'),(400,'Audio')]:d.box(40,y,210,76,[label])
    d.box(40,530,210,90,['Video','Timed frames/audio'])
    d.box(330,150,330,76,['Tokenizer + embeddings'])
    d.box(330,275,330,90,['SigLip2 vision encoder','Resampler / projection'])
    d.box(330,400,330,110,['Whisper-medium encoder','Features / projection','Pooling'])
    d.box(780,255,340,210,['Thinker','Qwen3-8B backbone','Prefill: input positions','Decode: next tokens'])
    d.box(1250,280,300,110,['Text output','Detokenization'])
    for y in [188,320,455]:d.arrow([(250,y),(330,y)])
    for y in [188,320,455]:d.arrow([(660,y),(720,y),(720,350),(780,350)])
    d.arrow([(1120,335),(1250,335)])
    d.arrow([(250,552),(290,552),(290,335),(330,335)],True)
    d.arrow([(250,595),(305,595),(305,470),(330,470)],True)
    d.box(470,670,300,110,['Talker','Speech codec tokens'])
    d.box(860,670,300,110,['Flow','Acoustic features'])
    d.box(1250,670,300,110,['HiFT','Waveform output'])
    d.arrow([(950,465),(950,580),(620,580),(620,670)],True)
    d.text(650,585,'Speech conditioning',20)
    d.arrow([(770,725),(860,725)],True);d.arrow([(1160,725),(1250,725)],True)
    d.box(40,685,320,90,['Optional reference','Voice conditioning'], '#f5ecdb')
    d.arrow([(360,730),(410,730),(410,820),(1005,820),(1005,780)],True)
    d.text(860,845,'Flow + HiFT = Code2Wav stage',21)
    d.text(40,885,'Dashed routes depend on the task and output mode. Real-time sessions add incremental state and scheduling.',20)
    d.save('model-components')
    d=Diagram('SGLang Omni: example process and device placement','One shared GPU; logical stages are grouped into OS processes')
    d.panel(30,130,1530,120,'Coordinator process | CPU')
    d.box(60,180,360,55,['HTTP admission / routing'])
    d.box(1120,180,410,55,['Response serialization'])
    d.panel(30,300,1040,425,'Pipeline process | CPU threads + GPU 0')
    d.box(60,385,280,100,['Preprocessing','Media + prompt | CPU'])
    d.box(400,385,290,100,['Audio encoder','Features to embeddings','GPU 0'])
    d.box(750,385,290,125,['Thinker','Prefill / decode','GPU 0'])
    d.box(400,565,290,100,['Image encoder','Optional vision | GPU 0'],'#f5ecdb')
    d.box(750,585,290,80,['Text detokenization','CPU'])
    d.panel(1110,300,450,425,'Speech process | same GPU 0')
    d.box(1140,385,390,90,['Talker','Codec generation | GPU 0'],'#f5ecdb')
    d.box(1140,560,390,105,['Code2Wav','Flow + HiFT | GPU 0'],'#f5ecdb')
    d.arrow([(200,235),(200,275),(15,275),(15,435),(60,435)])
    d.arrow([(340,435),(400,435)]);d.arrow([(690,435),(750,435)])
    d.arrow([(895,510),(895,585)])
    d.arrow([(1040,625),(1090,625),(1090,205),(1120,205)])
    d.arrow([(200,485),(200,615),(400,615)],True)
    d.arrow([(690,615),(720,615),(720,470),(750,470)],True)
    d.arrow([(1040,430),(1140,430)],True)
    d.arrow([(1335,475),(1335,560)],True)
    d.arrow([(1530,610),(1580,610),(1580,205),(1530,205)],True)
    d.text(40,775,'Solid: audio transcription to text. Dashed: task-dependent image and speech branches.',23)
    d.text(40,820,'A batch groups model work; it is not the same as client concurrency or a separate process.',22)
    d.text(40,865,'This configuration diagram reports no durations, GPU utilization, or bottleneck conclusions.',22)
    d.save('system-path')


if __name__ == '__main__':
    main()
