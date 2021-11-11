# yman
yman is a python script used for saving/restoring yakuake sessions (currently running commands, working directories, environment variables, tab titles)

NOTE: unless disabled when building, yakuake will display a warning about running commands from DBus once per a system session (per login).

## Installation
```
pip install yman
```

To use autocomplete (supported in bash/zsh) add this line to your zshrc/bashrc:
```
eval "$(_YMAN_COMPLETE=bash_source yman)"
```
(keep `bash_source` for both bash and zsh)

## Usage
```
» yman
Usage: yman [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  list     List saved sessions
  remove   Remove saved sessions
  restore  Restore saved sessions
  store    Store the currently running sessions
```

Saving a session:
```
» yman store sessionName
Storing current session as sessionName (skipping current terminal: yes)
Successfully stored current session as sessionName
```

Restoring a session:
```
» yman restore sessionName
Restoring session sessionName
```

Listing saved sessions:
```
» yman list
Saved sessions:
- sessionName
- demo
```

Removing a saved session:
```
» yman remove sessionName
Are you sure you want to remove session sessionName? [y/N]: y
```
