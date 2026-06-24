import os

with open(r'c:\Projects\agenticai\found.txt', 'w') as f:
    for root, dirs, files in os.walk(r'c:\Projects'):
        for file in files:
            if 'primagoai-context' in file.lower() or file.endswith('.txt'):
                if 'primagoai-context.txt' == file.lower():
                    f.write(os.path.join(root, file) + '\n')
