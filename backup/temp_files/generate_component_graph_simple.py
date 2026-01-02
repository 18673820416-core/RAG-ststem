# @self-expose: {"id": "generate_component_graph_simple", "name": "简化版组件知识图谱生成器", "type": "tool", "version": "1.0.0", "needs": {"deps": ["json"], "resources": ["self_exposures.json"]}, "provides": {"capabilities": ["组件知识图谱生成", "D3.js可视化", "依赖关系分析", "交互式图谱展示"]}}
import json

# 读取自我声明数据
def load_self_exposures():
    with open('self_exposures.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# 生成组件知识图谱
def generate_component_graph():
    exposures = load_self_exposures()
    
    # 构建节点和边
    nodes = []
    edges = []
    
    # 先创建所有节点
    for item in exposures:
        node = {
            'id': item['id'],
            'name': item['name'],
            'type': item['type'],
            'version': item['version'],
            'capabilities': item['provides']['capabilities']
        }
        nodes.append(node)
    
    # 创建边（依赖关系）
    for item in exposures:
        source_id = item['id']
        if 'deps' in item['needs']:
            for dep in item['needs']['deps']:
                dep_name = dep.split('.')[-1]
                for node in nodes:
                    if node['id'] == dep_name:
                        edges.append({
                            'source': source_id,
                            'target': node['id']
                        })
                        break
    
    return nodes, edges

# 生成HTML可视化 - 使用更简单的方式
def generate_html_visualization(nodes, edges):
    # 转换为JSON字符串
    nodes_json = json.dumps(nodes, ensure_ascii=False)
    edges_json = json.dumps(edges, ensure_ascii=False)
    
    # 简单的HTML模板，避免复杂的字符串拼接问题
    html_template = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>组件知识图谱</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5; }
        .container { display: flex; height: 100vh; }
        .sidebar { width: 300px; background-color: #fff; border-right: 1px solid #ddd; padding: 20px; overflow-y: auto; }
        .graph-container { flex: 1; position: relative; }
        #graph { width: 100%; height: 100%; }
        .node { cursor: pointer; }
        .node circle { stroke: #fff; stroke-width: 2px; }
        .node text { font-size: 12px; text-anchor: middle; pointer-events: none; }
        .link { stroke: #999; stroke-opacity: 0.6; stroke-width: 1.5px; }
        .node-type-api { fill: #1f77b4; }
        .node-type-service { fill: #2ca02c; }
        .node-type-component { fill: #ff7f0e; }
        .node-type-tool { fill: #9467bd; }
        .info-panel { background-color: #fff; padding: 15px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .info-panel h3 { margin-top: 0; color: #333; }
        .info-panel p { margin: 5px 0; font-size: 14px; }
        .capabilities { margin-top: 10px; }
        .capability { display: inline-block; background-color: #e8f4f8; color: #1f77b4; padding: 3px 8px; border-radius: 12px; font-size: 12px; margin: 2px; }
        .legend { margin-top: 20px; padding-top: 10px; border-top: 1px solid #ddd; }
        .legend-item { display: flex; align-items: center; margin: 5px 0; }
        .legend-color { width: 15px; height: 15px; border-radius: 50%; margin-right: 8px; }
        .legend-text { font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <h2>组件知识图谱</h2>
            <div class="info-panel">
                <h3>组件信息</h3>
                <p id="node-name">点击节点查看详情</p>
                <p id="node-type"></p>
                <p id="node-version"></p>
                <div class="capabilities" id="node-capabilities"></div>
            </div>
            <div class="legend">
                <h3>图例</h3>
                <div class="legend-item"><div class="legend-color" style="background-color: #1f77b4;"></div><div class="legend-text">API</div></div>
                <div class="legend-item"><div class="legend-color" style="background-color: #2ca02c;"></div><div class="legend-text">Service</div></div>
                <div class="legend-item"><div class="legend-color" style="background-color: #ff7f0e;"></div><div class="legend-text">Component</div></div>
                <div class="legend-item"><div class="legend-color" style="background-color: #9467bd;"></div><div class="legend-text">Tool</div></div>
            </div>
        </div>
        <div class="graph-container">
            <svg id="graph"></svg>
        </div>
    </div>

    <script>
        // 组件数据
        const nodes = DATA_NODES;
        const links = DATA_EDGES;
        
        // 设置SVG尺寸
        const svg = d3.select("#graph");
        const width = svg.node().clientWidth;
        const height = svg.node().clientHeight;
        
        // 创建力导向图模拟
        const simulation = d3.forceSimulation(nodes)
            .force("link", d3.forceLink(links).id(d => d.id).distance(100))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collision", d3.forceCollide().radius(30));
        
        // 创建箭头标记
        svg.append("defs").selectAll("marker")
            .data(["arrow"])
            .enter().append("marker")
            .attr("id", d => d)
            .attr("viewBox", "0 -5 10 10")
            .attr("refX", 25)
            .attr("refY", 0)
            .attr("markerWidth", 6)
            .attr("markerHeight", 6)
            .attr("orient", "auto")
            .append("path")
            .attr("d", "M0,-5L10,0L0,5")
            .attr("fill", "#999");
        
        // 创建连线
        const link = svg.append("g")
            .selectAll("line")
            .data(links)
            .enter().append("line")
            .attr("class", "link")
            .attr("marker-end", "url(#arrow)");
        
        // 创建节点组
        const node = svg.append("g")
            .selectAll(".node")
            .data(nodes)
            .enter().append("g")
            .attr("class", "node")
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));
        
        // 添加节点圆圈
        node.append("circle")
            .attr("r", 20)
            .attr("class", d => `node-type-${d.type}`);
        
        // 添加节点标签
        node.append("text")
            .attr("dy", 35)
            .text(d => d.name);
        
        // 节点点击事件
        node.on("click", function(event, d) {
            d3.select("#node-name").text(d.name);
            d3.select("#node-type").text(`类型: ${d.type}`);
            d3.select("#node-version").text(`版本: ${d.version}`);
            
            const capabilitiesDiv = d3.select("#node-capabilities");
            capabilitiesDiv.selectAll(".capability").remove();
            
            d.capabilities.forEach(cap => {
                capabilitiesDiv.append("div")
                    .attr("class", "capability")
                    .text(cap);
            });
        });
        
        // 更新模拟
        simulation.on("tick", () => {
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);
            
            node
                .attr("transform", d => `translate(${d.x},${d.y})`);
        });
        
        // 拖拽函数
        function dragstarted(event, d) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }
        
        function dragged(event, d) {
            d.fx = event.x;
            d.fy = event.y;
        }
        
        function dragended(event, d) {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }
        
        // 窗口大小调整
        window.addEventListener("resize", function() {
            const newWidth = svg.node().clientWidth;
            const newHeight = svg.node().clientHeight;
            
            simulation.force("center", d3.forceCenter(newWidth / 2, newHeight / 2));
            simulation.alpha(0.3).restart();
        });
    </script>
</body>
</html>
'''
    
    # 替换数据占位符
    html_content = html_template.replace('DATA_NODES', nodes_json).replace('DATA_EDGES', edges_json)
    
    # 写入文件
    with open('component_knowledge_graph.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

# 主函数
def main():
    nodes, edges = generate_component_graph()
    generate_html_visualization(nodes, edges)
    print("组件知识图谱已生成: component_knowledge_graph.html")

if __name__ == "__main__":
    main()