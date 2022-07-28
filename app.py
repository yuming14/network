import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import networkx as nx
from pyvis.network import Network
import numpy as np

#st.set_page_config(layout="wide")

# Set header title
st.title('Network Graph Visualization')

# Set Nrow
#N_rows = st.slider("Nrows of edges to read in: ", min_value=1, max_value=1000000)
N_rows = 1000000

# Read dataset (CSV)

#got_data = pd.read_csv('network_vec.csv', sep="\s+", nrows = N_rows)
got_data = pd.read_csv('network_vec_small.csv', sep=",", nrows = N_rows)
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

# Implement multiselect dropdown menu for option selection (returns a list)
selected_codes = st.multiselect('Select code(s) to visualize', code_list)
selected_idx_idx = [code_list.index(i) for i in selected_codes]
selected_idx = [idx[i] for i in selected_idx_idx]
st.write("Nselected = "+str(len(selected_idx)))

#target_fdr = st.slider("Target -log_10(Fdr)", min_value=0, max_value=50)
#st.write("target fdr =", 1/np.power(10, target_fdr))
N_edge_select = st.slider("top prop% edges", min_value=0.0, max_value=1.0)

# Set info message on initial site load
if len(selected_codes) == 0:
    st.text('Choose at least 1 code to get started')

# Create network graph when user selects >= 1 item
else:

    # Initiate PyVis network object
    code_net = Network(height='600px', bgcolor='#222222', font_color='white')

    # Create networkx graph object from pandas dataframe
    #tmp = []
    #for selected_idx_part in selected_idx:
      #tmp_part = [got_data['row'].tolist().index(selected_idx_part),
      #            got_data['col'].tolist().index(selected_idx_part)]
    #  tmp_part = [i for i,x in enumerate(got_data['row'].tolist()) if x == selected_idx_part ] + \
    #             [i for i,x in enumerate(got_data['col'].tolist()) if x == selected_idx_part ]
    #  tmp_part.sort()
    #  tmp_part = tmp_part[0:(max(int(len(tmp_part)*N_edge_select),1))]
    #  tmp = tmp + tmp_part
    #  df_select = got_data.loc[tmp]
    tmp = (got_data['row'].isin(selected_idx) | \
           got_data['col'].isin(selected_idx))
    df_select = got_data.loc[tmp]
    del tmp
    #del tmp_part
    df_select = df_select.reset_index(drop=True)
    #df_select = df_select.loc[0:max(int(len(df_select)*N_edge_select),1)]
    df_select = df_select.loc[0:int(len(df_select)*N_edge_select)]
    df_select = df_select.reset_index(drop=True)
    
    if len(df_select) == 0:
        st.text('Incorrect')
    sources = df_select['row']
    targets = df_select['col']
    weights = 1 - df_select['fdr']

    edge_data = zip(sources, targets, weights)

    for e in edge_data:
        src = e[0]
        dst = e[1]
        w = e[2]
        
        tmptitle = title[src] + ': ' + desc[src] + '<br>Neighbors:'
        for i in range(len(df_selec)):
          if df_select['row'][i+1] == src:
            tmpid = df_select['col'][i+1]
            tmptitle = '<br>' + tmptitle + title[tmpid] + ': ' + desc[tmpid]
          elif df_select['col'][i+1] == src:
            tmpid = df_select['row'][i+1]
            tmptitle = '<br>' + tmptitle + title[tmpid] + ': ' + desc[tmpid]
        
        code_net.add_node(title[src]+': '+desc[src], desc[src],
                          title = tmptitle, color = nodes_color[src])
        
        tmptitle = title[dst] + ': ' + desc[dst] + '<br>Neighbors:'
        for i in range(len(df_selec)):
          if df_select['row'][i+1] == dst:
            tmpid = df_select['col'][i+1]
            tmptitle = '<br>' + tmptitle + title[tmpid] + ': ' + desc[tmpid]
          elif df_select['col'][i+1] == dst:
            tmpid = df_select['row'][i+1]
            tmptitle = '<br>' + tmptitle + title[tmpid] + ': ' + desc[tmpid]
        
        code_net.add_node(title[dst]+': '+desc[dst], desc[dst],
                          title = tmptitle, color = nodes_color[dst])
        
        #code_net.add_node(title[src]+': '+desc[src], desc[src], 
        #                  title = title[src] + ': ' + desc[src],
        #                  color = nodes_color[src])
        #code_net.add_node(title[dst]+': '+desc[dst], desc[dst], 
        #                  title = title[dst] + ': ' + desc[dst],
        #                  color = nodes_color[dst])
        code_net.add_edge(title[src]+': '+desc[src], 
                          title[dst]+': '+desc[dst], 
                          value = w*0.5, 
                          color = {'color': 'dimgrey', 'highlight': 'whitesmoke'})

    #neighbor_map = code_net.get_adj_list()

    # add neighbor data to node hover data
    #for node in code_net.nodes:
    #    node['title'] += '<br> Neighbors:<br>' + '<br>'.join(neighbor_map[node['id']])
    #    node['value'] = np.log(np.log(len(neighbor_map[node['id']])+5))
    
    st.text('Nnodes = '+str(len(code_net.nodes))+'; Nedges = '+str(len(df_select)))

    # Generate network with specific layout settings
    #code_net.repulsion(node_distance=420, central_gravity=0.33,
    #                   spring_length=110, spring_strength=0.10,
    #                   damping=0.95)
    code_net.repulsion(node_distance=420, central_gravity=0.33,
                       spring_length=110, spring_strength=0.10,
                       damping=0.95)

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
    components.html(HtmlFile.read(), height=600, width=2000)
