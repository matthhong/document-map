export default function define(runtime, observer) {
  const main = runtime.module();
  const fileAttachments = new Map([["clusters.json",new URL("./files/b5558669e7064c862ea2f8997668d553cfea8f88b7e72bd406038fdd7102a35239609819a25afbb52b2cba55f2305eca7e4badec22d6f11190dcc0a80e7b66c7",import.meta.url)],["hexes.wkt.csv",new URL("./files/32da1d02624dbaf28329583a45c5b4779ab8c5066d2ae4acbbd0bad832c87941e2178c060209b983b5a36195911511b588cd7374a4fd6886360c504482e0f4de",import.meta.url)]]);
  main.builtin("FileAttachment", runtime.fileAttachments(name => fileAttachments.get(name)));
  main.variable(observer()).define(["md"], function(md){return(
md`# Document Clusters`
)});
  main.variable(observer("svg")).define("svg", ["d3","DOM","data","gosper"], function(d3,DOM,data,gosper)
{
    let width = 960
    let height = 500
    
    const svg = d3.select(DOM.svg(width, height))
        
    const vis = svg.append('g')
        .attr('transform', 'translate(540,10)')

    let seq = []
    for (const [k, v] of Object.entries(data)) {
        seq.push(...v.map(el => ([el, k])))
    }

    let coords = gosper

    function new_hex(c, e) {
      let x = 2*(c.x + c.z/2.0)
      let y = 2*c.z
      
      return {
          type: 'Feature',
          geometry: {
              type: 'Polygon',
              coordinates: [[
                  [x, y+2],
                  [x+1, y+1],
                  [x+1, y],
                  [x, y-1],
                  [x-1, y],
                  [x-1, y+1],
                  [x, y+2]
              ]]
          },
          properties: {
              'class': e
          }
      }
    }
        
    let hexes = {
        type: 'FeatureCollection',
        features: seq.map((e,i) => new_hex(coords[i], e[1]))
    }
    
    let radius = 5
    let dx = radius * 2 * Math.sin(Math.PI / 3)
    let dy = radius * 1.5
    
    let path_generator = d3.geoPath()
        .projection(d3.geoTransform({
            point: function(x,y) {this.stream.point(x * dx / 2, -(y - (2 - (y & 1)) / 3) * dy / 2)
        }}))
        
    let colorify = d3.scaleOrdinal()
        .domain(['A','B','C','D'])
        .range(["#8dd3c7","#ffffb3","#bebada","#fb8072"])
        
    vis.selectAll('.hex')
        .data(hexes.features)
      .enter().append('path')
        .attr('class', 'hex')
        .attr('d', path_generator)
        .attr('fill', (d) => colorify(d.properties['class']))
        .attr('stroke', (d) => colorify(d.properties['class']))

    return svg.node()
}
);
  main.variable(observer("data")).define("data", ["FileAttachment"], function(FileAttachment){return(
FileAttachment("clusters.json").json()
)});
  main.variable(observer("gosper")).define("gosper", ["d3","FileAttachment"], async function(d3,FileAttachment){return(
d3.csvParseRows(await FileAttachment("hexes.wkt.csv").text(), (d, i) => {
  return {
    x: parseInt(d[0]), // convert first colum column to Date
    y: parseInt(d[1]),
    z: parseInt(d[2])// convert fourth column to number
  }}
)
)});
  return main;
}