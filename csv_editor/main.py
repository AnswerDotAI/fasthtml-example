from fasthtml.common import *

db = database(':memory:')
tbl = None
hdrs = (Style('''
button,input { margin: 0 1rem; }
[role="group"] { border: 1px solid #ccc; }
'''), )
app, rt = fast_app(live=True, hdrs=hdrs)

@rt("/")
async def get():
    return Titled("CSV Uploader",
        Group(
            Input(type="file", name="csv_file", accept=".csv"),
            Button("Upload", hx_post="/upload", hx_target="#results",
                   hx_encoding="multipart/form-data", hx_include='previous input'),
            A('Download', href='/download', type="button")
        ),
        Div(id="results"))

def render_row(row):
    vals = [Td(Input(value=v, name=k)) for k,v in row.items()]
    vals.append(Td(Group(Button('delete', hx_get=remove.rt(id=row['id'])),
                   Button('update', hx_post='/update', hx_include="closest tr"))))
    return Tr(*vals, hx_target='closest tr', hx_swap='outerHTML')

@rt
async def download():
    csv_data = [",".join(map(str, tbl.columns_dict))]
    csv_data += [",".join(map(str, row.values())) for row in tbl()]
    headers = {'Content-Disposition': 'attachment; filename="data.csv"'}
    return Response("\n".join(csv_data), media_type="text/csv", headers=headers)

@rt('/update')
def post(d:dict): return render_row(tbl.update(d))

@rt
def remove(id:int): tbl.delete(id)

@rt("/upload")
async def post(csv_file: UploadFile):
    global tbl
    if not csv_file.filename.endswith('.csv'): return "Please upload a CSV file"
    tbl = db.import_file('test', await csv_file.read(), pk='id')
    header = Tr(*map(Th, tbl.columns_dict))
    vals = [render_row(row) for row in tbl()]
    return Table(Thead(header), Tbody(*vals))

serve()
