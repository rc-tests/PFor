import argparse
import hashlib
import csv
import os
import datetime
import platform
import getpass
import ctypes


def get_script_dir():
    return os.path.dirname(os.path.abspath(__file__))


def generate_results_folder(root_dir):
    if not os.path.exists(root_dir):
        print(f"[!] Error: The directory '{root_dir}' does not exist or the volume is not accessible.")
        exit(1)

    dirname = os.path.basename(os.path.normpath(root_dir))
    if not dirname:
        try:
            label = ctypes.create_unicode_buffer(1024)
            ctypes.windll.kernel32.GetVolumeInformationW(root_dir, label, 1024, None, None, None, None, 0)
            dirname = label.value.replace(" ", "_")
        except:
            dirname = "UnknownVolume"
    else:
        dirname = dirname.replace(" ", "_")

    date_stamp = datetime.datetime.now().strftime("%Y%m%d")
    script_dir = get_script_dir()
    count = 1
    base_folder_name = f"PHash_{dirname}_{date_stamp}"
    folder_name = base_folder_name
    full_path = os.path.join(script_dir, folder_name)
    while os.path.exists(full_path):
        folder_name = f"{base_folder_name}({count})"
        full_path = os.path.join(script_dir, folder_name)
        count += 1

    return full_path


def calculate_file_hash(filepath):
    hash_func = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while True:
            chunk = f.read(4096)
            if not chunk:
                break
            hash_func.update(chunk)
    return hash_func.hexdigest()


def get_unique_csv_path(destination):
    base = os.path.join(destination, "HASH_Report")
    count = 1
    path = f"{base}.csv"
    while os.path.exists(path):
        path = f"{base}({count}).csv"
        count += 1
    return path


def create_csv_report(root_dir, destination, verbose):
    os.makedirs(destination, exist_ok=True)
    report_path = get_unique_csv_path(destination)

    with open(report_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['File Name', 'HASH Value ( SHA256)', 'Time'])

        for dirpath, _, filenames in os.walk(root_dir):
            for file in filenames:
                filepath = os.path.join(dirpath, file)
                try:
                    hash_val = calculate_file_hash(filepath)
                    hash_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    writer.writerow([filepath, hash_val, hash_time])
                    if verbose:
                        print(f"[+] Checking: {filepath}")
                except Exception as e:
                    print(f"[-] Error hashing {filepath}: {e}")

    return report_path


def calculate_dir_hash(csv_path):
    hashes = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for row in reader:
            hashes.append(row[1])
    combined = ''.join(hashes)
    dir_hash = hashlib.sha256(combined.encode()).hexdigest()
    return dir_hash


def save_dir_hash(dir_hash, destination, root_dir):
    timestamp = datetime.datetime.now().strftime("%H%M%S")
    dt_full = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    base_report_name = "InvestigationReport"
    count = 1
    report_file = f"{base_report_name}.txt"
    report_path = os.path.join(destination, report_file)
    while os.path.exists(report_path):
        report_file = f"{base_report_name}({count}).txt"
        report_path = os.path.join(destination, report_file)
        count += 1

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("Forensic Hash Report - PForHash Tool\n")
        f.write("="*60 + "\n")
        f.write(f"Report Generated At : {dt_full}\n")
        f.write(f"Generated By        : {getpass.getuser()}\n")
        f.write(f"Operating System    : {platform.system()} {platform.release()}\n")
        f.write(f"Target Directory    : {root_dir}\n")
        f.write(f"Hashing Algorithm   : SHA256\n")
        f.write("="*60 + "\n\n")

        f.write(f"Master Directory Hash (SHA256):\n{dir_hash}\n")
        f.write("\nNote: This master hash is derived from all file hashes within the selected directory and its subdirectories.\n")
        f.write("This value will change even if a single file within the structure changes.\n")

        f.write("\nThis report is generated with forensic integrity and intended for legal admissibility.\n")

    return report_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PForHash - Forensic Directory Hash Tool")
    parser.add_argument("-v", action='store_true', help="Verbose output")
    parser.add_argument("-r", "--root", required=True, help="Root directory to hash")

    args = parser.parse_args()

    result_folder = generate_results_folder(args.root)

    csv_path = create_csv_report(args.root, result_folder, args.v)
    if csv_path is None:
        exit(0)

    dir_hash = calculate_dir_hash(csv_path)
    print("\n[*] Master Directory Hash:", dir_hash)

    save_path = save_dir_hash(dir_hash, result_folder, args.root)
    print(f"[+] Investigation report saved at: {save_path}")
