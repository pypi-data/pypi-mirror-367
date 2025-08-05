import sys

try:
    import graphviz
except ImportError:
    print("Warning: 'graphviz' library not found. Visualization will not be available.", file=sys.stderr)
    graphviz = None

def visualize_acn_key(key: dict, filename: str, view: bool = True):
    if not graphviz:
        print("Cannot generate visualization because 'graphviz' is not installed.", file=sys.stderr)
        return
    architecture = key.get("architecture")
    if not architecture:
        print("Error: Key does not contain 'architecture' information.", file=sys.stderr)
        return
    
    f_width = architecture[1]
    num_rounds = architecture[2]
    
    dot = graphviz.Digraph('ACN_F_Function', comment='ACN Feistel F-Function')
    dot.attr(rankdir='LR', splines='line', nodesep='0.8', ranksep='2', labelloc='t', label=f'F-Function Structure ({num_rounds} Rounds Total)')
    dot.attr('node', shape='circle', style='bold', label='', width='0.5')
    dot.attr('edge', arrowhead='none')

    with dot.subgraph(name=f'cluster_f') as c:
        c.attr(style='rounded', color='lightgrey', label=f'Input to F ({f_width} chunks)')
        input_nodes = [f'F_In_{i}' for i in range(f_width)]
        for node_id in input_nodes:
            c.node(node_id)
            
    with dot.subgraph(name=f'cluster_neurons') as c:
        c.attr(style='invis')
        neuron_nodes = [f'F_Neuron_{i}' for i in range(f_width)]
        # این حلقه تصحیح شده است
        for i, node_id in enumerate(neuron_nodes):
            c.node(node_id, shape='box', label=f'N_{i}')

    with dot.subgraph(name=f'cluster_out') as c:
        c.attr(style='rounded', color='lightgrey', label=f'Output from F ({f_width} chunks)')
        output_nodes = [f'F_Out_{i}' for i in range(f_width)]
        for node_id in output_nodes:
            c.node(node_id)
            
    for i in range(f_width):
        dot.edge(input_nodes[i], neuron_nodes[i])
        dot.edge(neuron_nodes[i], output_nodes[i])

    for i in range(1, f_width):
        dot.edge(neuron_nodes[i-1], neuron_nodes[i], style='dashed', constraint='false')

    try:
        dot.render(filename, format='png', view=view, cleanup=True)
        print(f"✅ F-function visualization saved as '{filename}.png'")
    except Exception as e:
        print(f"An error occurred during visualization: {e}", file=sys.stderr)