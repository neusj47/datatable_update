# 기간별 datatable 업데이트 함수
# 기간을 입력하여 데이터를 호출한다.
# 호출한 데이터를 datatable 형태로 입력한다.

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import numpy as np
import datetime
from datetime import date
import pandas_datareader.data as web

# TICKER를 입력합니다.
TICKER = ['AAPL']

start = date(2021, 1, 1)
end = datetime.datetime.now()

# 수익률, 거래량 데이터를 산출합니다.
dfs = web.DataReader(TICKER[0], 'yahoo', start, end)
dfs.reset_index(inplace=True)
dfs.set_index("Date", inplace=True)
dfs['Return'] = (dfs['Close'] / dfs['Close'].shift(1)) - 1
dfs['Return(cum)'] = (1 + dfs['Return']).cumprod()
dfs = dfs.dropna()
dfs.loc[:, 'TICKER'] = TICKER[0]
df = dfs

for i in range(1, len(TICKER)):
    start = date(2021, 1, 1)
    end = datetime.datetime.now()
    dfs = web.DataReader(TICKER[i], 'yahoo', start, end)
    dfs.reset_index(inplace=True)
    dfs.set_index("Date", inplace=True)
    dfs['Return'] = (dfs['Close'] / dfs['Close'].shift(1)) - 1
    dfs['Return(cum)'] = (1 + dfs['Return']).cumprod()
    dfs = dfs.dropna()
    dfs.loc[:, 'TICKER'] = TICKER[i]
    df = df.append(dfs)

# 데이터타입(Date)변환 문제로 csv 저장 후, 다시 불러옵니다. (파일 경로 설정 필요!!)
df = df.reset_index().rename(columns={"index": "id"})
df.to_csv('pricevolume.csv', index=False, encoding='cp949')
df = pd.read_csv('....../pricevolume.csv')

app = dash.Dash()

app.layout = html.Div(
    [
        dcc.DatePickerRange(
            id="my-date-picker-range",
            min_date_allowed=date(2021, 1, 1),
            start_date_placeholder_text='2021-01-01',
            end_date_placeholder_text='2021-01-11',
            display_format='YYYY-MM-DD',
        ),
        dash_table.DataTable(
            id="datatable-interactivity",
            columns=[
                {
                    "name": i,
                    "id": i,
                    "deletable": True,
                    "selectable": True,
                    "hideable": True,
                }
                if i == "iso_alpha3" or i == "year" or i == "id"
                else {"name": i, "id": i, "deletable": True, "selectable": True}
                for i in df.columns
            ],
            data=df.to_dict("records"),  # the contents of the table
            editable=True,  # allow editing of data inside all cells
            filter_action="native",  # allow filtering of data by user ('native') or not ('none')
            sort_action="native",  # enables data to be sorted per-column by user or not ('none')
            sort_mode="single",  # sort across 'multi' or 'single' columns
            column_selectable="multi",  # allow users to select 'multi' or 'single' columns
            row_selectable="multi",  # allow users to select 'multi' or 'single' rows
            row_deletable=True,  # choose if user can delete a row (True) or not (False)
            selected_columns=[],  # ids of columns that user selects
            selected_rows=[],  # indices of rows that user selects
            page_action="native",  # all data is passed to the table up-front or not ('none')
            page_current=0,  # page number that user is on
            page_size=800,  # number of rows visible per page
            style_cell={  # ensure adequate header width when text is shorter than cell's text
                "minWidth": 95,
                "maxWidth": 95,
                "width": 95,
            },
            style_cell_conditional=[  # align text columns to left. By default they are aligned to right
                {"if": {"column_id": c}, "textAlign": "left"}
                for c in ["country", "iso_alpha3"]
            ],
            style_data={  # overflow cells' content into multiple lines
                "whiteSpace": "normal",
                "height": "auto",
            },
        ),
    ]
)


def date_string_to_date(date_string):
    return pd.to_datetime(date_string, infer_datetime_format=True)


@app.callback(
    dash.dependencies.Output("datatable-interactivity", "data"),
    [
        dash.dependencies.Input("my-date-picker-range", "start_date"),
        dash.dependencies.Input("my-date-picker-range", "end_date"),
    ],
)
def update_data(start_date, end_date):
    data = df.to_dict("records")
    if start_date and end_date:
        mask = (date_string_to_date(df["Date"]) >= date_string_to_date(start_date)) & (
            date_string_to_date(df["Date"]) <= date_string_to_date(end_date))
        data = df.loc[mask].to_dict("records")
    return data



if __name__ == "__main__":
    app.run_server(debug=True)