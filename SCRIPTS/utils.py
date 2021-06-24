import plotly.graph_objects as go


def figure_scatter(dict_plot, title, xlabel, ylabel):
    
    figure = go.Figure()
    count= 0
    for plot in dict_plot:
        figure.add_trace(go.Scattergl(x = plot['x'],
                                    y=  plot['y'],
                                    mode= plot['mode'],
                                    name= plot['label'],))
    figure.update_layout(title=go.layout.Title(text=title ))
    figure.update_xaxes(title_text=xlabel)
    figure.update_yaxes(title_text=ylabel)
    return figure

def figure_bar(dict_plot, title, xlabel, ylabel):
    
    figure = go.Figure()
    count= 0
    for plot in dict_plot:
        figure.add_trace(go.Bar(x = plot['x'],
                                y=  plot['y'],
                                name= plot['label'],))
    figure.update_layout(barmode='stack')
    figure.update_layout(title=go.layout.Title(text=title ))
    figure.update_xaxes(title_text=xlabel)
    figure.update_yaxes(title_text=ylabel)
    return figure
