This tool is split in 2 parts, PForHash and PForDelta
PForHash hashes every single file in your target folder(could be a disk partition but w Python speeds so...)and subfolders using SHA256, spits out a clean CSV with hashes and timestamps of files. Also saves a "Master Hash" but I basically added that for funsies.
That master txt file also has details like the username and directory name.
In case you have it in a portable storage, you will know which computer you took that case from.

PForDelta can be called at a later date to check for the following:

🆕 Added

❌ Deleted

✏️ Modified

📁 Moved or Renamed(only if moved in a subfolder)

📎 Copied (kinda sorta, just like moved)

To Do:

User has to call for PForDelta and create a fresh hash map after the day's check manually. I can probably call PForHash as a library inside PForDelta and overwrite the previous hashmap and master hash file but I am trying to learn if there is a better way.

Learning PySide and PyQt to make it GUI (makes me pull my hair out)

Learning API integrations and how to host from clouds so we will see about that (in a 100years for sure)

Need to add a save as csv argument
