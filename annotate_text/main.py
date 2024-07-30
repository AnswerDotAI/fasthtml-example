from fasthtml.common import *
import json

# Set up the app, including daisyui and tailwind for the chat component
tlink = Script(src="https://cdn.tailwindcss.com"),
dlink = Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css")
app, rt, texts_db, Texts = fast_app('texts.db',hdrs=(tlink, dlink, picolink, MarkdownJS(), HighlightJS()), live=True, id=int, messages=list, feedback=bool, notes=str, pk='id')

LONG_TEXT = """Vertical Rhythm refers to the visual pattern formed by the blocks of type or lines of type on a web page as users scan down its content. This rhythm can be influenced by various elements such as headings, list items, block quotes, images, and more. Achieving good Vertical Rhythm is crucial as it ensures that the elements on your page are in harmony, making the content more readable and scannable for your visitors.
The Importance of Proper Line-Height and Visual Hierarchy
Two fundamental aspects of Vertical Rhythm that require close attention are line-height between elements and overall visual hierarchy on the page. Appropriate line-height proportions contribute to an engaging design, though it may demand an involved design exercise. Similarly, visual hierarchy ensures that the most important elements, such as primary images and text, are visually prominent, while less important ones are smaller and placed lower down the page.
The Evolution of Vertical Rhythm in Web Design


Vertical Rhythm has long been a concern for print designers, but it's come much later into the concerns of website or screen based visual design. With the increasing need to build responsive websites using grid layouts to accommodate various screen widths, mastering Vertical Rhythm is now more critical than ever. It has become a key aspect of both visual design and technical implementation, ensuring an optimal user experience across different devices.
Examples of Websites with Excellent Vertical Rhythm
To better understand the impact of Vertical Rhythm, let's take a closer look at some websites that have excelled in its implementation:
                """
title = 'Fastgenerated text annotation tool with FastHTML (and Tailwind)'


def render(message):
    return Div(
        P(message['content']),
        cls="mt-2 w-full text-sm text-gray-5000 overflow-y-auto whitespace-pre-wrap max-h-[calc(100vh-24rem)]"
    )

@rt("/")
def get():
    items = texts_db()
    # texts_db.insert(id="9", messages=json.dumps([{"role":"user","content":"can zig compile\/link to c++","num_tokens":7},{"role":"assistant","content":"Yes, Zig can compile and link to C++ code, allowing you to leverage existing C++ libraries or integrate C++ code within your Zig projects. Here\u2019s how you can do that:\n\n### 1. Using Zig to Call C++ Code\n\nTo call C++ code from Zig, you typically need to follow these steps:\n\n#### Step 1: Create C++ Code\n\nYou can create a simple C++ file, for example, `hello.cpp`:\n\n```cpp\n\/\/ hello.cpp\n#include <iostream>\n\nextern \"C\" {\n    void say_hello() {\n        std::cout << \"Hello from C++!\" << std::endl;\n    }\n}\n```\n\n- The `extern \"C\"` is used to prevent name mangling, allowing Zig to link correctly to C++ functions.\n\n#### Step 2: Create a Zig File\n\nNext, create a Zig file, for example, `main.zig`:\n\n```zig\nconst std = @import(\"std\");\n\nextern \"C\" {\n    fn say_hello();\n}\n\npub fn main() !void {\n    say_hello();\n}\n```\n\n#### Step 3: Compile and Link\n\nYou will need to compile both the C++ and Zig files together. The simplest way to do this is by using the Zig build system or directly using command-line tools.\n\n##### Using Command Line\n\nYou can compile and link them using the following commands:\n\n```bash\n# Compile the C++ code to an object file\ng++ -c hello.cpp -o hello.o\n\n# Compile the Zig code and link with the C++ object file\nzig build-exe main.zig hello.o --link-lib c++\n```\n\n- **Note**: The `--link-lib c++` flag tells Zig to link against the C++ standard library.\n\n### 2. Using Zig Build System\n\nYou can also use the Zig build system to simplify the process. Create a `build.zig` file:\n\n```zig\nconst Builder = @import(\"std\").build;\n\npub fn build(b: *Builder.Build) void {\n    const mode = b.standardReleaseOptions();\n    const exe = b.addExecutable(\"main\", \"main.zig\");\n    exe.linkLibC();\n    exe.linkLibCxx(); \/\/ Link against C++ standard library\n    exe.addObjectFile(\"hello.o\"); \/\/ Add the C++ object file\n\n    b.default_step.dependOn(&exe.step);\n}\n```\n\n### 3. Build the Project\n\nTo build your project, run:\n\n```bash\nzig build\n```\n\nThis command uses the `build.zig` file to compile the Zig and C++ code together, generating the executable.\n\n### 4. Running the Executable\n\nAfter building, you can run the executable:\n\n```bash\n.\/zig-out\/bin\/main\n```\n\nYou should see:\n\n```\nHello from C++!\n```\n\n### Important Notes\n\n- **C++ ABI Compatibility**: When linking C++ code with Zig, ensure that you are aware of the C++ ABI (Application Binary Interface) compatibility, especially if you are using C++ libraries.\n- **Linking C++ Libraries**: If you are linking against precompiled C++ libraries, you can specify them using `exe.linkLib(...)` in the `build.zig` file.\n- **Compiler Settings**: You may need to adjust compiler settings based on your development environment, including paths to headers or libraries.\n\n### Conclusion\n\nZig can effectively compile and link C++ code, allowing you to take advantage of both languages in your projects. By using the Zig build system or command-line tools, you can manage the integration smoothly.","num_tokens":732}]), feedback=None, notes='')
    index = 1 if id is null else id 
    # Card header
    card_header = Div(
        Div(
            Div(
                H3(f"Sample {items[0]} out of 12", cls="text-base font-semibold leading-6 text-gray-900"),
                P("User question to LLM goes here....", cls="mt-1 text-sm text-gray-500"),
                cls="ml-4 mt-4"
            ),
            Div(
                Button(
                    Span("←", cls="sr-only"),
                    Span("←", cls="h-5 w-5", aria_hidden="true"),
                    type="button",
                    cls="relative inline-flex items-center rounded-l-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
                ),
                Button(
                    Span("→", cls="sr-only"),
                    Span("→", cls="h-5 w-5", aria_hidden="true"),
                    type="button",
                    cls="relative -ml-px inline-flex items-center rounded-r-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
                ),
                cls="ml-4 mt-4 flex-shrink-0"
            ),
            cls="-ml-4 -mt-4 flex flex-wrap items-center justify-between sm:flex-nowrap"
        ),
        cls="border-b border-gray-200 bg-white px-4 py-5 sm:px-6"
    )
    
    # Card component
    card = Div(
        card_header,
        Div(
            Div(
                P(LONG_TEXT),
                id="main_text",
                cls="mt-2 w-full text-sm text-gray-500 overflow-y-auto whitespace-pre-wrap max-h-[calc(100vh-24rem)]"
            ),
            cls="px-4 py-5 sm:p-6 flex-grow overflow-hidden"
        ),
        cls="bg-white shadow sm:rounded-lg flex flex-col h-full"
    )
    
    # Wrapper div for collapse and buttons
    wrapper = Div(
        Div(
            # Input for additional notes
            Input(
                type="text",
                placeholder="Additional notes?",
                cls="flex-grow p-2 my-4 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-transparent"
            ),
            # Buttons
            Div(
                Button("Correct", cls="btn btn-outline btn-success mr-2 hover:text-white"),
                Button("Incorrect", cls="btn btn-outline btn-error hover:text-white"),
                cls="flex-shrink-0 ml-4"
            ),
            cls="flex items-center"
        ),
        cls="mt-4"
    )
    
    # Container for card and buttons
    content = Div(
        card,
        wrapper,
        cls="w-full max-w-2xl mx-auto flex flex-col h-[calc(100vh-8rem)]"
    )
    
    return Titled(title, Main(
        content,
        cls="container mx-auto mt-8 min-h-screen bg-gray-100 p-8 flex flex-col"
    ))


serve()