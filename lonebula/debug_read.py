import os

def read_file(path):
    print(f"--- Reading {path} ---")
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='latin-1') as f:
                print(f.read())
        except Exception as e:
            print(f"Error reading file: {e}")
    else:
        print("File not found.")
    print("--- End of file ---")

read_file(r'data\record_user_a.stream')
read_file(r'data\record_user_b.stream')
