adEdit – Minimalist SDI Text Editor / Mini-IDE
===================================
This is a text-editor built for SDI (Single Document Interface) operations, 
made to be used with modern window-managers that allow for efficient management
of many SDI windows. 

Note: I have not yet figured out a final name for this editor.
      There is a ~80% chance that this will be renamed in the near future,
      I just have not figured out what I want to name it.
Candidates are:
* Sdiide (Single-Document-Interface Integrated-Development-Environment)
* qtedit (A small editor written in QT) 
* addiks-edit (It's an editor written for and by me)
* ???

## Implementation
This project is written in Python, using Pyside6/Qt6 as the UI framework.
Every open document runs in it's own process, communication between 
processes/documents is done using DBUS.

## Features
**Implemented** Features:
* Open/Edit/Save ASCII files
* Dynamic Window-Size based on file contents
* Open-only-Once: If you try to open the same file twice, 
  the first window is presented instead
* Line-Numbers
* Syntax-Highlighting
* Highlighting of selected words

Planned **Common** Features:
* Git Integration
* Line-Sorting / -Filtering
* Formatters / Prettyfiers (JSON / YAML / ...)
* Search & Replace

Planned **Uncommon** Features:
* Project-Indexing / -Autocompletion (Abstracted per Language)
* Step-Debugger implementation 
  (Abstracted per Protocol. f.e.: dbgp/X-Debug for PHP)
* Edit in multiple places at once (Multi-Cursor)
* In-Code Warnings (f.e.: Results of static analysis)

Features that will **never** be implemented:
* Document-Management using tabs
* Additional toolbars, statusbars or other clutter in the main editor window

## Why SDI?
Most (if not all) other IDE's are written as big bulky MDI (multi-document-
interface) applications that run in a single big window and do not interface 
well with the rest of the system (window-manager).

I think that using tabs for document management is a very bad and inefficient
workaround that was created sometime in the nineties (by mozilla, I believe)
to work around the horribly bad window-management capabilities of MS Windows.

On the regular I see my collegues have multiple browser windows open with
dozens of tabs in each window. There is not even enough space for each tab
in the tab-bar to render an icon for the tab.
Searching for a single web-page sometimes takes them **minutes** while I stand
behind them waiting for then to find the right document.
You have a super high-speed computer at your hands, why in the world do you
still have to search for your documents by hand?!
The reason why is that every single application implements it's own (MDI)
document-management (mostly using tabs).
If applications would defer their document-management to the window-manager,
there could be one central point where all documents could be managed/searched.

I belive in an SDI approach, where every document (textfile, image, terminal, 
website, ...) is displayed in it's own window and the window-manager
(KDE/GNOME/...) is responsible for managing all of these documents.
KDE is (to my knowledge) the only window-manager that actually allows for
an efficient management of many small windows. 
Ubuntu Unity was another example, but unfortunately that WM was discontinued.

How do **I** find my windows? Simple: hit the [Expose][1] key on my keyboard,
see all my open windows at once and then use the Fulltext-Search to go directly
to my desired window within seconds.

[1] https://en.wikipedia.org/wiki/Mission_Control_(macOS)

I have configured all my applications to be used in an SDI fashion and use
KDE as a window-manager to handle them all.

## Why not use or modify an existing editor?
This project is meant to replace my current go-to editor, which is gedit with a
lot of plugins (some written by me). GNOME moves in a direction that I don't 
like (f.e.: removing menus).
And instead of taking gedit, suppressing half of the functionality (tabs) and 
adding other functionality that gedit was never designed for, I decided to just
build my own minimalist editor.
I've also looked at kate (too overloaded with unwanted UI: tabs) and kwrite (no extension support).