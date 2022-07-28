import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import networkx as nx
from pyvis.network import Network
import numpy as np

# Read dataset (CSV)

got_data = pd.read_csv('network_vec_small.csv', nrows = 10000)
got_dict = pd.read_csv('dict.csv', sep=",")
got_dict.index = range(1,61010)
title = got_dict['code']
desc = got_dict['desc']

# Set Group Color

from matplotlib import colors
nodes_color = got_dict['group'].tolist()

nodes_color_dict = {'CCS': 'red',
                    'Other lab': 'gold',
                    'ShortName': 'gold',
                    'LOINC': 'gold',
                    'PheCode': 'aqua',
                    'RXNORM': 'lime',
                    'PROC': 'violet',
                    'ACTI': 'violet',
                    'LIVB': 'violet',
                    'PHYS': 'violet',
                    'PHEN': 'violet',
                    'CHEM': 'violet',
                    'DISO': 'violet'}
nodes_color = [nodes_color_dict[i] if i in nodes_color_dict else i for i in nodes_color]
nodes_color = pd.Series(nodes_color, index = range(1,61010))


# Define list of selection options and sort alphabetically

idx = pd.concat([got_data['row'], got_data['col']])
idx = idx.drop_duplicates(keep='first')
code_list = title[idx].str.cat(desc[idx], sep=': ')
code_list = code_list.tolist()
code_list, idx = (list(t) for t in zip(*sorted(zip(code_list, idx))))


# Set header title
st.title('Network Graph Visualization')


# Implement multiselect dropdown menu for option selection (returns a list)
selected_codes = st.multiselect('Select code(s) to visualize', code_list)
selected_idx_idx = [code_list.index(i) for i in selected_codes]
selected_idx = [idx[i] for i in selected_idx_idx]

# Set info message on initial site load
if len(selected_codes) == 0:
    st.text('Choose at least 1 code to get started')

# Create network graph when user selects >= 1 item
else:

    # Initiate PyVis network object
    code_net = Network(height='465px', bgcolor='white', font_color='white')

    # Create networkx graph object from pandas dataframe
    df_select = got_data.loc[got_data['row'].isin(selected_idx) | \
                             got_data['col'].isin(selected_idx)]
    df_select = df_select.reset_index(drop=True)
    if len(df_select) == 0:
        st.text('Incorrect')
    else:
        st.text('Nedges ='+str(len(df_select)))
    sources = df_select['row']
    targets = df_select['col']
    weights = 1 - df_select['fdr']

    edge_data = zip(sources, targets, weights)

    for e in edge_data:
        src = e[0]
        dst = e[1]
        w = e[2]

        code_net.add_node(title[src]+': '+desc[src], title[src], 
                          title = title[src] + ':\n' + desc[src],
                          color = nodes_color[src])
        code_net.add_node(title[dst]+': '+desc[dst], title[dst], 
                          title = title[dst] + ':\n' + desc[dst],
                          color = nodes_color[dst])
        code_net.add_edge(title[src]+': '+desc[src], 
                          title[dst]+': '+desc[dst], 
                          value = w*0.5, 
                          color = {'color': 'whitesmoke', 'highlight': 'dimgrey'})

    neighbor_map = code_net.get_adj_list()

    # add neighbor data to node hover data
    for node in code_net.nodes:
        node['title'] += '\n Neighbors:\n' + '\n'.join(neighbor_map[node['id']])
        node['value'] = np.log(np.log(len(neighbor_map[node['id']])+5))
    
    st.text('Nnodes ='+str(len(code_net.nodes)))

    # Generate network with specific layout settings
    #code_net.repulsion(node_distance=420, central_gravity=0.33,
    #                   spring_length=110, spring_strength=0.10,
    #                   damping=0.95)
    #code_net.repulsion(node_distance=420, central_gravity=-22350,
    #                   spring_length=250, spring_strength=0.10,
    #                   damping=0.95)

    # Save and read graph as HTML file (on Streamlit Sharing)
    try:
        path = 'tmp'
        #code_net.save_graph(f'Desktop/research/Tianxi/PMI-inference/python_network/tmp/pyvis_graph.html')
        code_net.save_graph(f'{path}/pyvis_graph.html')
        HtmlFile = open(f'{path}/pyvis_graph.html','r',encoding='utf-8')

    # Save and read graph as HTML file (locally)
    except:
        path = 'html_files'
        #code_net.save_graph(f'Desktop/research/Tianxi/PMI-inference/python_network/html_files/pyvis_graph_0727.html')
        code_net.save_graph(f'{path}/pyvis_graph.html')
        HtmlFile = open(f'{path}/pyvis_graph.html','r',encoding='utf-8')

    #code_net.show_buttons(filter_ = ['physics'])
    #code_net.show('html_files/pyvis_graph.html')
    #HtmlFile = open(f'html_files/pyvis_graph.html', 'r', encoding='utf-8')

    # Load HTML file in HTML component for display on Streamlit page
    components.html(HtmlFile.read(), height=435)
