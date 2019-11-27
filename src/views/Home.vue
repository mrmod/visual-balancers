<template>
  <div class="home">
    <svg></svg>
    <div v-if="error" class="error">
      {{ error }}
    </div>
  </div>
</template>

<script>
import * as d3 from 'd3'
import {sankey as d3Sankey, sankeyLinkHorizontal as d3SankeyLinkHorizontal} from 'd3-sankey'
import {json as d3JSON} from 'd3-request'
import { stringify } from 'querystring'
import axios from 'axios'

export default {
  name: 'home',
  components: {
  },
  data() {
    return {
      error: null,
    }
  },
  mounted() {
    const svg = d3.select('svg')
    svg.style('width', '80vw').style('height', '80vh').style('background', '#CCCCCC')

    const nodes = [
      {name: 'node0'},
      {name: 'node1'},
    ]
    const links = [
      {source: 0, target: 1, value: 100},
    ]
    const graph = {nodes, links}
    let width = window.innerWidth * 0.8
    let height = window.innerHeight * 0.8

  var formatNumber = d3.format(",.0f"),
      format = function(d) { return formatNumber(d) + " TWh"; },
      color = d3.scaleOrdinal(d3.schemeCategory10);

  var sankey = d3Sankey()
      .nodeWidth(15)
      .nodePadding(10)
      .extent([[0, 0], [width, height]]);

  var link = svg.append("g")
      .attr("class", "links")
      .attr("fill", "none")
      .attr("stroke", "#000")
      .attr("stroke-opacity", 0.2)
    .selectAll("path");

  var node = svg.append("g")
      .attr("class", "nodes")
      .attr("font-family", "sans-serif")
      .attr("font-size", 10)
    .selectAll("g");
    axios.get('/graph')
    .then(r => {
      // Copy paste from Sankey example for D3 v4
      // D3-style graph
      let graph = r.data;
      sankey(graph);

      link = link
        .data(graph.links)
        .enter().append("path")
          .attr("d", d3SankeyLinkHorizontal())
          .attr("stroke-width", function(d) { return Math.max(1, d.width); });

      link.append("title")
          .text(function(d) { return d.source.name + " → " + d.target.name + "\n" + format(d.value); })
          

      node = node
        .data(graph.nodes)
        .enter().append("g");

      node.append("rect")
          .attr("x", function(d) { return d.x0; })
          .attr("y", function(d) { return d.y0; })
          .attr("height", function(d) { return d.y1 - d.y0; })
          .attr("width", function(d) { return d.x1 - d.x0; })
          .attr("fill", function(d) { return color(d.name.replace(/ .*/, "")); })
          .attr("stroke", "#000");

      node.append("text")
          .attr("x", function(d) { return d.x0 - 6; })
          .attr("y", function(d) { return (d.y1 + d.y0) / 2; })
          .attr("dy", "0.35em")
          .attr("text-anchor", "end")
          .text(function(d) { return d.name; })
        .filter(function(d) { return d.x0 < width / 2; })
          .attr("x", function(d) { return d.x1 + 6; })
          .attr("text-anchor", "start")
          

      node.append("title")
          .text(function(d) { return d.name + "\n" + format(d.value); })
    })
    .catch(error => `<h1>Error: {error}</h1><p>Check your authorization tokens and network connection</p>`)
  }
}
</script>

<style scoped>
.error h1 {
  font-weight: bold;
  font-size: 1.3em;
  color: red;
}
</style>