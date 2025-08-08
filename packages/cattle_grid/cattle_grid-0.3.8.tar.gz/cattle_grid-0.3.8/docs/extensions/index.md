# Extensions

!!! warning
    Still experimental

## Types of extensions

cattle_grid supports different types of extensions:

- Lookup extensions: Retrieves stuff
- Transform extensions: Takes data and harmonizes the format / adds information
- Processing extensions: When an activity is received or send, the extension does something
- API extensions: Provide something accessible via HTTP

Combining these types of extension is possible.

!!! info
    I might add a transform extension for outgoing messages. Similarly, a transform extension for messages just about to be send. This would allow one to do remote instance specific transformations.

### Types of subscriptions

Extensions can define new topics, and then perform an action when a message is received. These actions should be either to change the state of the extension, e.g. update its database, or send new messages. These messages should be send to existing topics. Extensions should not send to `incoming.#` (as it is reserved for messages received form the Fediverse), not should they send to `outgoing.#`, instead they should send to `send_message`, which will ensure proper distribution to `outgoing.#`.

However, extensions should subscribe to `outgoing.#` and `incoming.#` to process messages.

## Writing an extension

The basic implementation will be

```python
from cattle_grid.extensions import Extension

extension = Extension("some name", __name__)

...
```

By writing something as a cattle_grid extension, you can first through the lookup and transform method influence cattle_grid's behavior to e.g.

- serve archived activities (e.g. from a migrated account)
- add information to activities, e.g. label them

### Running extensions

In order to test extensions, one might want to run these using a separate
process. This can be achieved by running

```bash
python -m cattle_grid.extensions run your.extension.module
```

See [below](#python-m-cattle_gridextensions-run) for further details on
this command.

!!! warning
    This only works for processing and API extensions. Transformation
    and lookup extensions are called by cattle_grid directly.

We note here that the configuration will be loaded through
the same mechanism as cattle_grid does. This is in particular
relevant for accessing the database and the RabbitMQ router.

## Configuring extensions

Extensions are configured in `cattle_grid.toml` by adding an entry of the form

```toml
[[extensions]]

module_name = "your.extension"
config = { var = 1}

lookup_order = 2
```

The factory method in the python module `your.extension` will be called with the contents `config` as an argument.

::: mkdocs-click
    :module: cattle_grid.extensions.__main__
    :command: main
    :prog_name: python -m cattle_grid.extensions
    :depth: 1
    :list_subcommands: True
    :style: table
