This tool is split in 2 parts, PForHash and PForDelta.

1. PForHash hashes every single file in your target folder(could be a disk partition but w Python speeds so...)and subfolders using SHA256, spits out a clean CSV with hashes and timestamps of files.
a)  Also saves a "Master Hash" but I basically added that for funsies.
b)  Both files saved in new Folder named PHash_[FolderName]_[datetime].
c)  csv is called hash report
d)  txt is called investigation report
e)  That master txt file also has details like the date, username and directory name.
f)  In case you have it in a portable storage, you will know which computer you took that case from and when.

2. PForDelta can be called at a later date to check for the following:

🆕 Added

❌ Deleted

✏️ Modified

📁 Moved or Renamed(only if moved in a subfolder)

📎 Copied (kinda sorta, just like moved)

