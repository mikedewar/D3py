d3py_template = """<html>
<head>
	<script type="text/javascript" src="http://mbostock.github.com/d3/d3.js"></script>
	<script type="text/javascript" src="http://localhost:{{ port }}/{{ name }}/{{ name }}.js"></script>
	<link type="text/css" rel="stylesheet" href="http://localhost:{{ port }}/{{ name }}/{{ name }}.css">
</head>

<body>
	<div id="chart"></div>
	<script>
		d3.json("http://localhost:{{ port }}/{{ name }}/{{ name }}.json", draw);
	</script>
</body>

</html>"""
