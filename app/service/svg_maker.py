import requests
from lxml import etree
import math
from fastapi_cache.decorator import cache
from app.core.singleton import Singleton
from loguru import logger

class SVGMaker(metaclass=Singleton):
    
    @cache(expire=3600)
    async def get_base_svg(self, lang):
        logger.debug(f'Getting base svg for {lang}')
        lang = lang.lower().replace('#', 'sharp').replace('+', 'plus')
        response = requests.get(f'https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/{lang}/{lang}-original.svg')
        response.raise_for_status()
        logger.debug(f'Got base svg for {lang} {response.text[:30]}')
        return response.text
    
    def make_mask_svg(self, w, h):
        len=max(w,h)
        #make new xml
        mask = etree.Element('mask')
        mask.set('id', 'reveal-mask')
        circle = etree.SubElement(mask, 'circle')
        r = math.sqrt(math.pow(len / 2, 2) * 2) / 2 # diagonal length divided by 2
        circle.set('r', str(r))
        circle.set('cx', str(w / 2)) # center x
        circle.set('cy', str(h / 2)) # center y
        circle.set('fill', 'transparent')
        circle.set('stroke', 'white')
        circle.set('stroke-width', str(r*2)) # for full circle
        circle.set('transform', f'rotate(-90) translate(-{len})') # transition start from top

        animate =  etree.SubElement(circle, 'animate')
        animate.set('attributeName', 'stroke-dasharray')
        animate.set('begin', '0s')
        animate.set('dur', '1s')
        animate.set('fill', 'freeze')
        animate.set('keySplines', '0.5 0 0 1')
        animate.set('values', f'0,20000;{2*math.pi*r},20000') # from zero to circumference
        animate.set('calcMode', 'spline')
        
        return mask

    async def make_clock_wipe_transition(self, lang):
        raw_base_svg = await self.get_base_svg(lang)
        base_svg = etree.fromstring(raw_base_svg)
        
        x, y, w, h = base_svg.get('viewBox').split(' ')
        g_element = etree.Element("g", mask="url(#reveal-mask)")
        for child in base_svg.iterchildren():
            g_element.append(child)
            pass
        
        for child in list(base_svg):
            base_svg.remove(child)
        base_svg.append(g_element)

        mask_svg = self.make_mask_svg(int(w), int(h))
        base_svg.append(mask_svg)
        return etree.tostring(base_svg, pretty_print=True, encoding='unicode')

if __name__ == '__main__':
    maker = SVGMaker()
    result = maker.make_clock_wipe_transition('python')
    with open('file.svg', 'w') as f:
        f.write(result)
