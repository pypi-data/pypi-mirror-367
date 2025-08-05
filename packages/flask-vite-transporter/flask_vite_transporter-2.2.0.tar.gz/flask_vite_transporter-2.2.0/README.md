# flask-vite-transporter 🚚

Transport Vite apps to Flask (or Quart)

```bash
pip install flask-vite-transporter
```

<!-- TOC -->
* [flask-vite-transporter 🚚](#flask-vite-transporter-)
  * [How it works](#how-it-works)
    * [The pyproject.toml file](#the-pyprojecttoml-file)
    * [List the Vite apps](#list-the-vite-apps)
    * [Compiling the Vite apps](#compiling-the-vite-apps)
    * [Transporting the Vite apps](#transporting-the-vite-apps)
    * [What happens](#what-happens)
    * [Modes (--mode)](#modes---mode)
    * [Only (--only)](#only---only)
  * [Working with vite-transporter using Flask / Quart](#working-with-vite-transporter-using-flask--quart)
    * [The context processors](#the-context-processors)
    * [Flask Example](#flask-example)
    * [Quart Example](#quart-example)
    * [CORS](#cors)
    * [Update the Static URL Path](#update-the-static-url-path)
  * [Running the demos](#running-the-demos)
  * [Things to note](#things-to-note)
<!-- TOC -->

## How it works

### The pyproject.toml file

The pyproject.toml file is used to store what Vite apps are available.

`pyproject.toml`:

```toml
[tool.flask_vite_transporter]
npm_exec = "npm"
npx_exec = "npx"
serve_app = "app_flask"
vite_app.frontend = "frontend"
```

The compiling of the Vite apps requires the `npx` and `npm` be
available. You can use absolute paths here.

`npm_exec` is used to run `npm install` if your Vite app does not
have the `node_modules` folder.

`npx` is used to run the Vite app build command.

`serve_app` is the Flask or Quart app package that will serve the Vite
compiled files. For now this extension only works with the app package setup:

```text
app_flask/
├── static
├── templates
└── __init__.py
```

`vite_app.<reference>` is vite_app.'reference in the flask app' = 'relative
folder of the vite app'

You can send over multiple Vite apps to the serving app, and they will be
accessible within template files using the reference value.

See [Working with vite-transporter using Flask / Quart](#working-with-vite-transporter-using-flask--quart)
for more information about how to use references.

```toml
[tool.flask_vite_transporter]
npm_exec = "npm"
npx_exec = "npx"
serve_app = "app_flask"
vite_app.customer_portal = "frontends/customer"
vite_app.admin_portal = "frontends/admin"
```

### List the Vite apps

You can see what apps can be compiled by running:

```bash
vt list
```

It will show: `<reference>: <vite app source> => <serve app location>`

### Compiling the Vite apps

```bash
vt pack
```

This will create a
`dist` folder in each Vite app directory with the compiled files.

### Transporting the Vite apps

```bash
vt transport
```

This will move the compiled files to the serving app.

You can also run the `pack` and `transport` commands together:

```bash
vt pack transport
```

### What happens

The Vite apps are compiled into a `dist` folder, the files contained
in this folder are then moved to a folder called `vite` in the serving app.

Any js file that is compiled that contains an asset reference will
replace `assets/` with `/--vite--/{reference}`.

This requires that all assets in the Vite app stay in the
`assets` folder, and are imported in the
frontend project in a way that the Vite compile stage can find them.

### Modes (--mode)

The Vite apps can be compiled in different modes by using the `-m` or `--mode`
flag:

```bash
vt pack -m development
# or
vt pack -m your-named-mode
```

An example of `pack` and `transport` together:

```bash
vt pack -m dev transport
# or
vt pack transport -mode dev
```

These mode values are accessible via `import.meta.env.MODE` in the Vite app.

See [Vite: Env Variables and Modes](https://vite.dev/guide/env-and-mode) to
find out more about Vite modes.

### Only (--only)

If you have multiple frontends and only want to pack and transport one you
can use the `-o` or `--only` flag to do that.

Here's an example:

```toml
[tool.flask_vite_transporter]
npm_exec = "npm"
npx_exec = "npx"
serve_app = "app_flask"
vite_app.customer_portal = "frontends/customer"
vite_app.admin_portal = "frontends/admin"
```

`vt pack transport --only admin_portal`

## Working with vite-transporter using Flask / Quart

flask-vite-transporter creates a couple of Flask / Quart context processors
that match the Vite apps to a Flask / Quart template.

### The context processors

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    {{ vt_head('frontend') }}
    <title>Test</title>
</head>
<body>
{{ vt_body() }}
</body>
</html>
```

```
vt_head(
    reference: str  # The name of the reference used.
)
```

```
vt_body(
    root_id: str = "root",  # The id of the root element
    noscript_message: str = "You need to enable JavaScript to run this app.",
)
```

### Flask Example

```python
from flask import Flask, render_template

from flask_vite_transporter import ViteTransporter


def create_app():
    app = Flask(__name__)
    ViteTransporter(app)

    @app.route("/")
    def index():
        return render_template("index.html")

    return app
```

### Quart Example

```python
from quart import Quart, render_template

from flask_vite_transporter.quart import QuartViteTransporter


def create_app():
    app = Quart(__name__)
    QuartViteTransporter(app)

    @app.route("/")
    async def index():
        return await render_template("index.html")

    return app
```

### CORS

Setting:

```python
ViteTransporter(app, cors_allowed_hosts=["http://127.0.0.1:5003"])
```

This is to allow the Vite app to communicate with the app.

### Update the Static URL Path

```python
ViteTransporter(
  app, 
  cors_allowed_hosts=["http://127.0.0.1:5003"],
  static_url_path="/nested/system/--vite--"
)
```

```bash
vt pack transport -sup /nested/system/--vite--
```

This is used if you're using nested systems.

**Note:** It's recommended to remove this in production.

## Running the demos

We will be using a package call
`pyqwe` to run commands from the pyproject file.
Installing the development requirements will install `pyqwe`:

```bash
pip install -r requirements/tests.txt
```

Use `pyqwe` to install the local version of flask-vite-transporter:

```bash
pyqwe install
```

The `serve_app` under `tool.flask_vite_transporter` is currently set to use
the Flask demo app.

```bash
pyqwe flask_plus_vite
```

You should be able to visit the Flask app and the Vite app from the link in
the terminal. Change something in the Vite app, save, then in a separate
terminal run:

```bash
vt pack transport
```

The Vite app will be compiled, and the files will be moved to the Flask app.
Visiting the Flask app from the link in the terminal should show the changes.

## Things to note

When including credentials in fetch requests in the vite app.
You must visit the serve app first to set the credentials.

For example, if the serve app is running on `http://127.0.0.1:5001`,
you must visit this address first.

This won't be needed in production, as it's expected that the Vite
app will be served from the same domain.
