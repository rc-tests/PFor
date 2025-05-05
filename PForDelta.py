import argparse
import os
import csv
import datetime
import hashlib
import getpass


def get_logged_in_user():
    try:
        return getpass.getuser()
    except Exception:
        return "NA"


def calculate_sha256(file_path):
    hash_func = hashlib.sha256()
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(4096)
            if not chunk:
                break
            hash_func.update(chunk)
    return hash_func.hexdigest()


def load_previous_hashes(csv_path):
    hashes = {}
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            hashes[row['File Name']] = row['HASH Value ( SHA256)']
    return hashes


def traverse_directory(root_path, verbose):
    current_files = {}
    for dirpath, _, filenames in os.walk(root_path):
        for fname in filenames:
            full_path = os.path.join(dirpath, fname)
            try:
                if verbose:
                    try:
                        print(f"[*] Checking: {full_path}")
                    except UnicodeEncodeError:
                        print(f"[*] Checking: {full_path.encode('utf-8', errors='ignore').decode('utf-8')}")
                file_hash = calculate_sha256(full_path)
                current_files[full_path] = file_hash
            except Exception as e:
                if verbose:
                    print(f"[!] Failed to hash: {full_path} ({e})")
    return current_files


def compare_hashes(previous_hashes, current_hashes):
    deleted = []
    added = []
    changed = []
    renamed_or_moved = []

    prev_paths = set(previous_hashes.keys())
    curr_paths = set(current_hashes.keys())

    for path in prev_paths - curr_paths:
        deleted.append(path)

    for path in curr_paths - prev_paths:
        added.append(path)

    for path in prev_paths & curr_paths:
        if previous_hashes[path] != current_hashes[path]:
            changed.append(path)

    prev_hash_map = {v: k for k, v in previous_hashes.items()}
    added_copy = added[:]
    for path in added_copy:
        h = current_hashes[path]
        if h in prev_hash_map:
            renamed_or_moved.append((prev_hash_map[h], path))
            added.remove(path)
            if prev_hash_map[h] in deleted:
                deleted.remove(prev_hash_map[h])

    return deleted, added, changed, renamed_or_moved


def save_report(deleted, added, changed, renamed_or_moved, dest_folder):
    timestamp = datetime.datetime.now().strftime("%H%M")
    report_path = os.path.join(dest_folder, f"InvestigationReport{timestamp}.txt")
    with open(report_path, "w", encoding='utf-8') as f:
        f.write(f"Name: {get_logged_in_user()}\n")
        f.write(f"DateTime: {datetime.datetime.now()}\n\n")
        if deleted:
            f.write("Deleted files:\n")
            for path in deleted:
                f.write(f"{path}\n")
            f.write("\n")
        if added:
            f.write("Added files:\n")
            for path in added:
                f.write(f"{path}\n")
            f.write("\n")
        if changed:
            f.write("Modified files (hash changed):\n")
            for path in changed:
                f.write(f"{path}\n")
            f.write("\n")
        if renamed_or_moved:
            f.write("Renamed or Moved files:\n")
            for old_path, new_path in renamed_or_moved:
                f.write(f"{old_path} -> {new_path}\n")
            f.write("\n")
        if not (deleted or added or changed or renamed_or_moved):
            f.write("No changes to files or folders inside the directory.\n")
    return report_path


def main():
    parser = argparse.ArgumentParser(description="PForDelta - Detect file additions, deletions, renames, moves, copies, or modifications")
    parser.add_argument("-v", action="store_true", help="Verbose output")
    parser.add_argument("-e", required=True, help="Path to folder containing HASH_Report.csv")
    parser.add_argument("-r", "--root", required=True, help="Directory to scan")
    args = parser.parse_args()

    hash_report_path = os.path.join(args.e, "HASH_Report.csv")
    if not os.path.exists(hash_report_path):
        print("[!] HASH_Report.csv not found in specified folder")
        return

    previous_hashes = load_previous_hashes(hash_report_path)
    current_hashes = traverse_directory(args.root, args.v)

    deleted, added, changed, renamed_or_moved = compare_hashes(previous_hashes, current_hashes)

    if deleted or added or changed or renamed_or_moved:
        report_path = save_report(deleted, added, changed, renamed_or_moved, args.e)
        print(f"[*] Investigation report saved at: {report_path}")
    else:
        print("[*] No changes to files or folders inside the directory.")


if __name__ == "__main__":
    main()
