# htmx-kanban

This project provides a simple Kanban board built with Flask, SQLModel, HTMX, and _hyperscript.
The purpose of this project is to perform stress testing with the browser with varying numbers of cards.
The cards themselves are stored in a sqlite database that gets created when starting the server.

This project is intended to explore the ideas of HTMX.
It is not intended to be used as anything other than a local demo.
I cut a lot of corners just to make this small and easy to work with.

## Developing
You must have `uv` installed (e.g., `brew install uv`).
First create a venv (`uv venv .venv`) and load the virtual environment in your shell (`source .venv/bin/activate`).
You can then run the application using `flask --app main.py --debug run`.
The application will be accessible at http://127.0.0.1:5000.
Running in debug mode ensures the templates are reloaded every time `render_template` is called, and the `--debug` flag will restart the server when the Python code changes.

If you want to seed the database with cards, you can run `uv run add_tasks.py <NUMBER>`.
The cards will be evenly distributed among the board columns.
The default number of cards is 500.

I have tested up to 25000 cards. 
In that scenario, the server remained fast (<20ms response time), but the browser had difficulty making the changes.
I assume this was due to the size of the DOM.

## Walkthrough
The server in this project is a Flask application that uses SQLModel.
The only SQLModel is `Task`, which gets stored in a local sqlite database.

The `Board` and `BoardColumn` classes are only ever used in memory in the index endpoint.
They exist to structure the cards from the database.

Since this is an HTMX application, all the endpoints return HTML (the default format supported by Flask).

The root route fetches all the tasks from the database and creates the Kanban board displayed on the page.
The other routes support create a new task or moving a task to a different column, and both of these return an HTML fragment that describes the update that should be applied to the board.

The HTML includes some _hyperscript scripts to add a bit of interactivity for drag-and-drop using the [HTML Drag and Drop API](https://developer.mozilla.org/en-US/docs/Web/API/HTML_Drag_and_Drop_API).

The board itself handles the `drag` event, and the individual cards are `draggable`.
The columns are drop targets because they halt the propagation of the dragover and dragenter events.
They also handle the drop event, and call the server via an `htmx.ajax` call.


## Gotchas
### hx-swap and interactivity
You cannot swap out content that has interactivity defined on it (e.g., via hyperscript) and expect that the interactivity will work after the swap. 
At least not by default.

This project works around this by ensure that there is no interactivity defined on the cards themselves, and only swapping those out.
You cannot swap out an entire column because you would lose the dragover, dragenter, and drop event handlers.

### currentTarget vs target
I learned that in the drop event handler on the columns, I needed to use `currentTarget` rather than `target` to get the id of the column.
This is because the `target` is the element that was dropped on, but the event will bubble up if that element is not a drop target.
On the event, the `target` will always be the element on which the event was initiated, but the `currentTarget` will be the element that is handling the event.



