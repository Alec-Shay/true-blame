### Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [IntelliJ Setup](#intellij)

## Prerequisites
Python 3 must be installed to run the script.

## Installation
Clone this repository : 
`git@github.com/alec-shay/true-blame.git`

<a name="intellij" />

## IntelliJ Setup

1. After cloning the `true-blame` repository, in IntelliJ, navigate to `File` -> `Settings`.
2. Add a new external tool under `Tools` -> `External Tools`.

![External Tools screenshot](https://github.com/Alec-Shay/true-blame/blob/master/img/IntelliJExternalToolSetup.png)

3. Add a name (i.e., "true blame") and ensure "Open console" is checked under `Options`
4. Under `Show in`, uncheck all options except `Editor menu`.
5. Set the following under `Tool settings`:
   - For Program: py
   - For Parameters: /path/to/true-blame.py $FileRelativePath$ $LineNumber$ -s "$SelectedText$"
   - Working directory: $ProjectFileDir$
6. Optionally, add a shortcut by going to Keymap -> External Tools and right-clicking True Blame.

Now you can run True Blame from IntelliJ by using the right-click context menu for selected text!

- **Warning: IntelliJ removes quotation marks.**  For selected text with quotes (`message.getString("className")`) replace the External Tool's `"$SelectedText$"` parameter with `"$Prompt$"`.  Use the program as before except input the desired substring with quotes escaped (`message.getString(\"className\")`.

## Alias Setup
Add this section to .bash_aliases (or the equivalent on whichever shell you're using) which calls the script.  Ensure /path/to/clone/location is modified to be wherever you've cloned the repository.

```bash
TB_PATH=/path/to/clone/location

tb() {
        ${TB_PATH}/tb $@
}
```

To run, type `tb` and enter the file name, line number, and substring when promopted.  
```
Filename: modules/apps/web-experience/asset/asset-publisher-web/src/main/java/com/liferay/asset/publisher/web/util/AssetPublisherUtil.java
Line Number: 157
Substring (default: exact line): rootPortletId
```