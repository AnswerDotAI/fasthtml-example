from fasthtml.common import *

def Toolbar():
    return Div(
        Select(
            Option("JavaScript", value="javascript"),
            Option("Python", value="python"),
            Option("HTML", value="html"),
            Option("CSS", value="css"),
            id="language",
            cls="mr-2 p-2 border rounded"
        ),
        Button("Run", id="run", cls="mr-2 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"),
        Button("Save", id="save", cls="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"),
        cls="bg-gray-200 p-4 shadow-md flex items-center w-full"
    )