# Running Python in the Browser with WebAssembly

A code editor that runs Python in the browser using Pyodide, CodeMirror and WebAssembly.

## Want to learn how to build this?

Check out the [post](https://testdriven.io/blog/python-webassembly/).

## Want to use this project?

1. Clone the repo:

   `git clone https://github.com/amirtds/python_editor_wasm`
1. Create a virtual environment and Install the dependencies:

    ```bash
    cd python_editor_wasm
    python3.10 -m venv env
    source env/bin/activate
    pip install -r requirements.txt
    ```

1. Run the flask app:

   `flask run`

1. Navigate to [http://127.0.0.1:5000/](http://127.0.0.1:5000/)