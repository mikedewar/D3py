import logging

import json
import os
from StringIO import StringIO
import time

import displayable
import deployable

from jinja2 import Template # well-known templating module

from css import CSS
import javascript as JS

class Figure(object):
    """
    Maintains in internal representation of d3 geometries. This implies
    an understanding of css,html and javascript. 
    """
    def __init__(self, name, width, height, font, 
        logging, template, server, deploy, **kwargs):

        # store data
        self.name = '_'.join(name.split())
        d3py_path = os.path.abspath(os.path.dirname(__file__))
        self.filemap = {
            os.path.join("static", "d3.js"):{
                "fd":open(os.path.join(d3py_path,"d3.js"),"r"), 
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
            os.path.join(d3py_path, 'd3py_template.html')).readlines())
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
    
        self._server = server 
        self._deploy = deploy


    def __enter__(self):
        """
        It is important that the Figure support the python's with statement. 
        At the moment, the heavy lifting is done by the displayable module. 
        This stub is required, so that, the callee can use the 'with' 
        syntax directly. 
        """
        if self._server is None: 
            self._server = displayable.displayable.default_displayable(self)
            if hasattr(self._server,'__enter__'):
                self._server.__enter__() 

        if self._deploy is None:
            self._deploy = deployable.deployable.default_deployable(self)
            if hasattr(self._deploy,'__enter__'):
                self._deploy.__enter__()
        
        # assertion: All variables used by the html template are 
        #  known. Write the html based on the template. 
        self._save_html(self._server.host, self._server.port)
        return self
    

    def __exit__(self, ex_type, ex_value, ex_tb):
        """
        This snub is required, so that, the callee can use the with directly.
        """
        self._server.__exit__(ex_type, ex_value, ex_tb)
        return false 

    def ion(self):
        """
        Turns interactive mode on ala pylab
        """
        self._server.ion()

    def ioff(self):
        """
        Turns interactive mode off
        """
        self._server.ioff()

    def show(self):
        self.update()
        self.save()
        self._server.show()

    def deploy(self):
        self.update()
        self.save()
        self._deploy.save()

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
        Saving the chart. _save_html() is not called here. It relies
        on an html template. Since all values are available during construction, __init__() calls _save_hmtl() once. 
        """
        logging.debug('saving chart')
        self._save_data()
        self._save_css()
        self._save_js()

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

    def _save_html(self, a_host, a_port):
        """
        Bind a var in the html template code with that value provided. 
        Implies all related variables defined. 
        """
        self.html_filename = "%s.html"%self.name
        template = Template(self.html)
        self.filemap[self.html_filename] = {
            "fd":StringIO(template.render(name=self.name, host=a_host, port=a_port)),
            "timestamp":time.time()
        }

