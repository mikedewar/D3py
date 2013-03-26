import logging

from StringIO import StringIO
import time
import json
import os

from jinja2 import Template # well-known templating module

from css import CSS
import javascript as JS

class Figure(object):
    """
    Maintains in internal representation of d3 geometries. This implies
    an understanding of css,html and javascript. 
    """
    def __init__(self, name, width, height, font, logging, template, **kwargs):

        # store data
        self.name = '_'.join(name.split())
        d3py_path = os.path.abspath(os.path.dirname(__file__))
        self.filemap = {
            "static" + os.sep + "d3.js":{
                "fd":open(d3py_path + os.sep + "d3.js","r"), 
                "timestamp":time.time()
            },
        }

        self.logging = logging

        # initialise strings
        self.js = JS.JavaScript()
        self.margins = {
            "top": 10, 
            "right": 20, 
            "bottom": 25, 
            "left": 60, 
            "height":height, 
            "width":width
        }
        
        # we use bostock's scheme http://bl.ocks.org/1624660
        self.css = CSS()

        self.html = template or "".join(open(
            d3py_path + os.sep + 'd3py_template.html').readlines())
        self.js_geoms = JS.JavaScript()
        self.css_geoms = CSS()
        self.geoms = []
        # misc arguments - these go into the css!
        self.font = font
        self.args = {
            "width": width - self.margins["left"] - self.margins["right"],
            "height": height - self.margins["top"] - self.margins["bottom"],
            "font-family": "'%s'; sans-serif"%self.font
        }
        kwargs = dict([(k[0].replace('_','-'), k[1]) for k in kwargs.items()])
        self.args.update(kwargs)

    def _build(self):
        logging.debug('building chart')
        self._build_js()
        self._build_css()
        self._build_geoms()

    def update(self):
        logging.debug('updating chart')
        self._build()
        self.save()

    def save(self):
        """
        Saving the chart. We need to wait to save the html because 
        we do not know how this will be displayed or deployed. The
        assoicated displayable will provide the remaining information
        when it calls renderHtml() 
        """
        logging.debug('saving chart')
        self._save_data()
        self._save_css()
        self._save_js()

    def _clanup(self):
        """
        What is the intent of this stub? see  https://github.com/mikedewar/d3py/issues/62
        """
        raise NotImplementedError

    def _set_data(self):
        self.update()

    def _add_geom(self, geom):
        self.geoms.append(geom)
        self.save()
    
    def _build_css(self):
        #._build up the basic css
        chart = {}
        chart.update(self.args)
        self.css["#chart"] = chart

    def _build_geoms(self):
        self.js_geoms = JS.JavaScript()
        self.css_geoms = CSS()
        for geom in self.geoms:
            self.js_geoms.merge(geom._build_js())
            self.css_geoms += geom._build_css()

    def __add__(self, geom):
        self._add_geom(geom)

    def __iadd__(self, geom):
        self._add_geom(geom)
        return self

    def _data_to_json(self):
        raise NotImplementedError
        
    def _build_js(self):
        draw = JS.Function("draw", ("data",))
        draw += "var margin = %s;"%json.dumps(self.margins).replace('""','')
        draw += "    width = %s - margin.left - margin.right"%self.margins["width"]
        draw += "    height = %s - margin.top - margin.bottom;"%self.margins["height"]
        # this approach to laying out the graph is from Bostock: http://bl.ocks.org/1624660
        draw += "var g = " + JS.Selection("d3").select("'#chart'") \
            .append("'svg'") \
            .attr("'width'", 'width + margin.left + margin.right + 25') \
            .attr("'height'", 'height + margin.top + margin.bottom + 25') \
            .append("'g'") \
            .attr("'transform'", "'translate(' + margin.left + ',' + margin.top + ')'")

        self.js = JS.JavaScript() + draw + JS.Function("init")

    def _save_data(self,directory=None):
        """
        save a json representation of the figure's data frame
        
        Parameters
        ==========
        directory : str
            specify a directory to store the data in (optional)
        """
        # write data
        filename = "%s.json"%self.name
        self.filemap[filename] = {"fd":StringIO(self._data_to_json()),
                "timestamp":time.time()}

    def _save_css(self):
        # write css
        filename = "%s.css"%self.name
        css = "%s\n%s"%(self.css, self.css_geoms)
        self.filemap[filename] = {"fd":StringIO(css),
                "timestamp":time.time()}

    def _save_js(self):
        # write javascript
        final_js = JS.JavaScript()
        final_js.merge(self.js)
        final_js.merge(self.js_geoms)

        filename = "%s.js"%self.name
        js = "%s"%final_js
        self.filemap[filename] = {"fd":StringIO(js),
                "timestamp":time.time()}

    def renderHtml(self, a_host, a_port):
        """
        Bind a var in the html template code with that value provided. 
        Implies all related variables defined. 
        Implies all related variables defined. 
        """
        self.html_filename = "%s.html"%self.name
        template = Template(self.html)
        self.filemap[self.html_filename] = {
            "fd":StringIO(template.render(name=self.name, host=a_host, port=a_port)),
            "timestamp":time.time()
        }

