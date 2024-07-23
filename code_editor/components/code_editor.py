from fasthtml.common import *
from .toolbar import Toolbar

editor_script = Script("""
let editor;
let completionTippy;
let currentCompletion = '';

function initEditor() {
    editor = ace.edit("editor");
    editor.setTheme("ace/theme/monokai");
    editor.session.setMode("ace/mode/javascript");
    editor.setOptions({
        fontSize: "14px",
        showPrintMargin: false,
        showGutter: true,
        highlightActiveLine: true,
        wrap: true
    });
    
    editor.setValue("// Your code here");
    
    window.addEventListener('resize', function() {
        editor.resize();
    });

    document.getElementById('language').addEventListener('change', function(e) {
        let mode = "ace/mode/" + e.target.value;
        editor.session.setMode(mode);
    });

    editor.session.on('change', function(delta) {
        if (delta.action === 'insert' && (delta.lines[0] === '.' || delta.lines[0] === ' ')) {
            showCompletionSuggestion();
        }
    });

    completionTippy = tippy(document.getElementById('editor'), {
        content: 'Loading...',
        trigger: 'manual',
        placement: 'top-start',
        arrow: true,
        interactive: true
    });

    // Override the default tab behavior
    editor.commands.addCommand({
        name: 'insertCompletion',
        bindKey: {win: 'Tab', mac: 'Tab'},
        exec: function(editor) {
            if (currentCompletion) {
                editor.insert(currentCompletion);
                currentCompletion = '';
                completionTippy.hide();
            } else {
                editor.indent();
            }
        }
    });
}

async function showCompletionSuggestion() {
    const cursorPosition = editor.getCursorPosition();
    const screenPosition = editor.renderer.textToScreenCoordinates(cursorPosition.row, cursorPosition.column);

    completionTippy.setContent('Loading...');
    completionTippy.setProps({
        getReferenceClientRect: () => ({
            width: 0,
            height: 0,
            top: screenPosition.pageY,
            bottom: screenPosition.pageY,
            left: screenPosition.pageX,
            right: screenPosition.pageX,
        })
    });
    completionTippy.show();

    try {
        const response = await fetch('/complete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                code: editor.getValue(),
                row: cursorPosition.row,
                column: cursorPosition.column
            }),
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        currentCompletion = data.completion;
        completionTippy.setContent(`${currentCompletion} (Press Tab to insert)`);
    } catch (error) {
        console.error('Error:', error);
        completionTippy.setContent('Error fetching completion');
        currentCompletion = '';
    }

    setTimeout(() => {
        if (currentCompletion) {
            completionTippy.hide();
            currentCompletion = '';
        }
    }, 5000);
}

document.addEventListener('DOMContentLoaded', initEditor);
""")

def CodeEditor():
    return (
        Div(
            Toolbar(),
            Div(
                Div(id="editor", cls="w-full h-full"),
                Script("""
                    me().on('contextmenu', ev => {
                        ev.preventDefault()
                        me('#context-menu').send('show', {x: ev.pageX, y: ev.pageY})
                    })
                """),
                cls="flex-grow w-full"
            ),
            cls="flex flex-col h-screen w-full"
        ),
        editor_script
    )