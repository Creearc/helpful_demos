from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
import base64
import os


def load_img(path, img_name):
    try:
        encoded_image = base64.b64encode(open('{}{}'.format(path, img_name), 'rb').read()).decode()
        return 'data:image/{};base64,{}'.format(img_name.split('.')[-1], encoded_image)
    except:
        return ''
    

last_path = os.popen("ls -lt ~/yolov5/runs/train/").read().split('\n')[1].split()[-1]

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dcc.Input(id='input-1', type='text', value='runs/train/{}/'.format(last_path)),
    html.Button(id='submit-button-state', n_clicks=0, children='Submit'),
    html.Div(id='output-state'),
    
])


@app.callback(Output('output-state', 'children'),
              Input('submit-button-state', 'n_clicks'),
              State('input-1', 'value'))
def update_output(n_clicks, input1):
    path = '{}{}'.format(input1, '/' if input1[-1] != '/' else '')
    return html.Div([
      html.Img(src=load_img(path, 'labels.jpg'), width=600),
      html.Img(src=load_img(path, 'labels_correlogram.jpg'), width=600),

      html.Br(),
      
      html.Img(src=load_img(path, 'train_batch0.jpg'), width=600),
      html.Img(src=load_img(path, 'train_batch1.jpg'), width=600),
      html.Img(src=load_img(path, 'train_batch2.jpg'), width=600),

      html.Br(),
      
      html.Img(src=load_img(path, 'val_batch0_labels.jpg'), width=600),
      html.Img(src=load_img(path, 'val_batch0_pred.jpg'), width=600),
      html.Img(src=load_img(path, 'val_batch1_labels.jpg'), width=600),
      html.Img(src=load_img(path, 'val_batch1_pred.jpg'), width=600),
      html.Img(src=load_img(path, 'val_batch2_labels.jpg'), width=600),
      html.Img(src=load_img(path, 'val_batch2_pred.jpg'), width=600),

      html.Br(),

      html.Img(src=load_img(path, 'F1_curve.png'), width=600),
      html.Img(src=load_img(path, 'P_curve.png'), width=600),
      html.Img(src=load_img(path, 'R_curve.png'), width=600),
      html.Img(src=load_img(path, 'PR_curve.png'), width=600),

      html.Br(),

      html.Img(src=load_img(path, 'results.png'), width=600),
      html.Img(src=load_img(path, 'confusion_matrix.png'), width=600),
      
      ])


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, debug=True)


