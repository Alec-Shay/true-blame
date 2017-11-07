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
   - For Parameters: (full path to true-blame.py (in `src`)) $FileRelativePath$ $LineNumber$ -s "$SelectedText$"
   - Working directory: $ProjectFileDir$
6. Optionally, create another External Tool to add an option to perform in reverse, adding one more to the parameters: -r

Now you can run True Blame from IntelliJ by using the right-click context menu for selected text!

### Tip: You can add your own shortcuts for the tools you created for True Blame by going to Keymap -> External Tools to find them, and right-clicking them

### **Warning:** if the selected text in IntelliJ contains quotation marks, then IntelliJ will automatically remove these before passing them as a parameter. If you must use a substring containing quotation marks with True Blame, then you may need to create yet another External Tool option and replace the $SelectedText$ parameter with a "$Prompt$" parameter. This will open a prompt where you can wrap the desired substring in quotes and escape the quotation marks yourself, with less limitations (but be sure to still keep the cursor on the appropriate line!).