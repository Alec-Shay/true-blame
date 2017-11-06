### Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [IntelliJ Setup](#intellij)

## Prerequisites
Python must be installed to run the script.

## Installation
Clone this repository : 
`git@github.com/alec-shay/true-blame.git`

Add this section to .bash_aliases (or the equivalent on whichever shell you're using) which calls the script.  Ensure /path/to/clone/location is modified to be wherever you've cloned the repository.

```bash
TB_PATH=/path/to/clone/location

tb() {
        ${TB_PATH}/tb $@
}
```

Additionally hook the function tb() to your build / ant-all / gw workflow to always have the hash of your bundle.

<a name="intellij" />
## IntelliJ Setup

1. After cloning the `true-blame` repository, in IntelliJ, navigate to `File` -> `Settings`.
2. Add a new external tool under `Tools` -> `External Tools`.

![External Tools screenshot](https://github.com/Alec-Shay/true-blame/blob/doc/img/IntelliJExternalToolSetup.png)

3. Add a name (i.e., "true blame") and ensure "Open console" is checked under `Options`
4. Under `Show in`, uncheck all options except `Editor menu`.
5. Set the following under `Tool settings`:
   - For Program: py
   - For Parameters: (full path to true-blame.py (in `src`)) $FileRelativePath$ $LineNumber$ -s $SelectedText$
   - Working directory: $ProjectFileDir$
6. Optionally, create another External Tool to add an option to perform in reverse, adding one more to the parameters: -r

Now you can run True Blame from IntelliJ by using the right-click context menu for selected text!