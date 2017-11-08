### Contents
- [Parameters](#parameters)
- [Installation](#installation)
- [IntelliJ](#intellijsetup)
    - [Setup](#intellijsetup)
    - [Usage](#intellijusage)
- [Alias](#aliassetup)
	- [Setup](#aliassetup)
	- [Usage](#aliasusage)

## Parameters

- `-s <string>` : specify a specific substring of the desired line to search on
   - not using `-s` will use the whole line by default (without leading/trailing whitespace)

- `-r <start-commit> <end-commit>` : search in reverse
   - start-commit and end-commit are assumed HEAD by default


## Installation
1. Install Python 3

2. Clone this repository : 
`git@github.com/alec-shay/true-blame.git`

<a name="intellijsetup" />

## IntelliJ 

#### Setup

1. After cloning the `true-blame` repository, in IntelliJ, navigate to `File` -> `Settings`.
2. Add a new external tool under `Tools` -> `External Tools`.

![External Tools screenshot](https://github.com/Alec-Shay/true-blame/blob/master/img/IntelliJExternalToolSetup.png)

3. Add a name (i.e., "true blame") and ensure "Open console" is checked under `Options`
4. Under `Show in`, uncheck all options except `Editor menu`.
5. Set the following under `Tool settings`:
   - Program: py
   - Parameters: /path/to/true-blame.py $FileRelativePath$ $LineNumber$ -s "$SelectedText$"
   - Working directory: $ProjectFileDir$
6. Optionally, add a shortcut by going to Keymap -> External Tools and right-clicking True Blame.

Now you can run True Blame from IntelliJ by using the right-click context menu for selected text!

<a name="intellijusage" />

#### Usage

Select the desired text and right-click, then under External Tools click True Blame.

![Right-click context screenshot](https://github.com/Alec-Shay/true-blame/blob/master/img/SampleIntelliJUse.png)


- **Warning: IntelliJ `$SelectedText$` removes quotation marks.**  

To allow for more flexible parameters (including selected text with quotes), create another External Tool with the following Parameters:
   - /path/to/true-blame.py $FileRelativePath$ $LineNumber$ $Prompt$

The following example uses $Prompt$ to use additional parameters and escape quotes.  We pass in a substring (`-s`) with escaped quotes (`"SCOPE_ID_GROUP_PREFIX = \"Group_\""`) and the True Blame reverse (`-r`) starting hash (`23b974b`).
   
![Right-click prompt screenshot](https://github.com/Alec-Shay/true-blame/blob/master/img/SampleIntelliJPrompt.png)
   

<a name="aliassetup" />

## Alias

#### Setup

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

<a name="aliasusage" />

#### Usage

```tb path/to/file/filename.extension line_number arguments```