import sys
import os
import marshal
import time
import subprocess
import re
import base64
from datetime import datetime

GREY = '\033[90m'
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RESET = '\033[0m'

ASCII_ART = f"{RED}            _    _    _          \n  _ __ _  _| |_ (_)__| |___ _ _  \n | '_ \\ || | ' \\| / _` / -_) '_| \n | .__/\\_, |_||_|_\\__,_\\___|_|   \n |_|   |__/                      \n{RESET}"

def log_info(msg):
    print(f"{GREEN}[ + ]{GREY} {msg}{RESET}")

def log_error(msg):
    print(f"{RED}[ - ]{GREY} {msg}{RESET}")

def log_warn(msg):
    print(f"{YELLOW}[/!\\]{GREY} {msg}{RESET}")

def start_message():
    print(ASCII_ART)
    now = datetime.now().strftime("%H:%M:%S")
    print(f"{GREY}[ i ] pyhider started at @ {now}{RESET}")

def progress_bar(task="Processing", length=30, duration=2.0):
    print()
    print(f"{GREY}{task}.. ", end='', flush=True)
    start = time.time()
    while time.time() - start < duration:
        elapsed = time.time() - start
        percent = elapsed / duration
        filled = int(length * percent)
        bar = '=' * filled + ' ' * (length - filled)
        print(f"\r{GREY}{task}.. |{bar}| {int(percent*100)}% ", end='', flush=True)
        time.sleep(0.05)
    print(f"\r{GREY}{task}.. |{'='*length}| 100% {RESET}\n")

def print_help():
    print("""
pyhider 1.2

Options:
  --file, -f          File to compile or obfuscate
  --compile, -c       Compile a file (name or path)
  --ico=              Path or name of icon
  --name=             Name of the output .exe
  --obfuscate         Obfuscate python file using marshal
  --ascii             Display ASCII art
  --hideconsole       Remove console window on execution
  --hidewebhook       Obfuscate detected webhooks in the code
  --hideurl           Obfuscate detected URLs in the code
  --hidefunctions     Obfuscate all functions bodies in the code
  --debug             Show debug details
  --clear             Clean temporary files after compilation
  --version           Show version
  --help, -h          Show this help
""")

def parse_args(args):
    opts = dict()
    opts['file'] = None
    opts['compile'] = None
    opts['ico'] = None
    opts['name'] = None
    opts['obfuscate'] = False
    opts['ascii'] = False
    opts['hideconsole'] = False
    opts['hidewebhook'] = False
    opts['hideurl'] = False
    opts['hidefunctions'] = False
    opts['debug'] = False
    opts['clear'] = False
    opts['version'] = False
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == '-h' or arg == '--help':
            print_help()
            sys.exit(0)
        elif arg == '--file' or arg == '-f':
            if i + 1 < len(args):
                opts['file'] = args[i + 1]
                i += 1
        elif arg.startswith('--file='):
            opts['file'] = arg.split('=', 1)[1]
        elif arg == '--compile' or arg == '-c':
            if i + 1 < len(args):
                opts['compile'] = args[i + 1]
                i += 1
        elif arg.startswith('--compile='):
            opts['compile'] = arg.split('=', 1)[1]
        elif arg.startswith('--ico='):
            opts['ico'] = arg.split('=', 1)[1]
        elif arg.startswith('--name='):
            opts['name'] = arg.split('=', 1)[1]
        elif arg == '--obfuscate':
            opts['obfuscate'] = True
        elif arg == '--ascii':
            opts['ascii'] = True
        elif arg == '--hideconsole':
            opts['hideconsole'] = True
        elif arg == '--hidewebhook':
            opts['hidewebhook'] = True
        elif arg == '--hideurl':
            opts['hideurl'] = True
        elif arg == '--hidefunctions':
            opts['hidefunctions'] = True
        elif arg == '--debug':
            opts['debug'] = True
        elif arg == '--clear':
            opts['clear'] = True
        elif arg == '--version':
            opts['version'] = True
        i += 1
    return opts

def encode_ascii_obf(s):
    return ''.join(f'\\x{ord(c):02x}' for c in s)

def decode_ascii_obf_code():
    return """
def _decode_obf_ascii(s):
    b = bytes(int(s[i:i+2],16) for i in range(2,len(s),4))
    import base64
    return base64.b64decode(b).decode()
"""

def hide_webhooks(source):
    pattern = r'https?://(?:canary\.|ptb\.)?discord(?:app)?\.com/api/webhooks/[0-9]+/[A-Za-z0-9_-]+'
    matches = re.findall(pattern, source)
    if not matches:
        return source, 0
    for w in matches:
        b64 = base64.b64encode(w.encode()).decode()
        obf = encode_ascii_obf(b64)
        decoder_func = decode_ascii_obf_code()
        replacement = f'(_decode_obf_ascii("{obf}"))'
        source = source.replace(w, replacement)
    if decoder_func not in source:
        source = decoder_func + '\n' + source
    return source, len(matches)

def hide_urls(source):
    url_pattern = r'https?://[^\s\'"\\]+'
    matches = re.findall(url_pattern, source)
    if not matches:
        return source, 0
    for u in matches:
        b64 = base64.b64encode(u.encode()).decode()
        obf = encode_ascii_obf(b64)
        decoder_func = decode_ascii_obf_code()
        replacement = f'(_decode_obf_ascii("{obf}"))'
        source = source.replace(u, replacement)
    if decoder_func not in source:
        source = decoder_func + '\n' + source
    return source, len(matches)

def hide_functions(source, debug):
    func_pattern = r'(^def\s+[\w_]+\s*\([^)]*\):\s*(?:\n[ \t]+.+)+)'
    functions = re.findall(func_pattern, source, re.MULTILINE)
    if not functions:
        return source, 0
    decoder_func = """
import base64
def _decode_func(b64code):
    code = base64.b64decode(b64code).decode()
    exec(code, globals())
"""
    obf_funcs = []
    for func in functions:
        header_line = func.split('\n')[0]
        body = '\n'.join(func.split('\n')[1:])
        indent = ' ' * 4
        b64_body = base64.b64encode(body.encode()).decode()
        fname = header_line.split('def ')[1].split('(')[0].strip()
        repl = f'{header_line}\n{indent}code_b64 = "{b64_body}"\n{indent}_decode_func(code_b64)\n'
        source = source.replace(func, repl)
    if decoder_func not in source:
        source = decoder_func + '\n' + source
    if debug:
        log_info(f'Obfuscated {len(functions)} function(s)')
    return source, len(functions)

def obfuscate_source(path, opts):
    if not os.path.isfile(path):
        log_error('File ' + path + ' not found')
        return None
    with open(path, 'r', encoding='utf-8') as f:
        source = f.read()
    if opts['debug']:
        log_info('Read source from ' + path + ' (' + str(len(source)) + ' bytes)')
    replaced = 0
    if opts['hidewebhook']:
        source, c = hide_webhooks(source)
        replaced += c
        if opts['debug']:
            log_info(f'Obfuscated {c} webhook(s)')
    if opts['hideurl']:
        source, c = hide_urls(source)
        replaced += c
        if opts['debug']:
            log_info(f'Obfuscated {c} url(s)')
    if opts['hidefunctions']:
        source, c = hide_functions(source, opts['debug'])
        replaced += c
    if opts['obfuscate']:
        try:
            code_obj = compile(source, path, 'exec')
            marshalled = marshal.dumps(code_obj)
            script = f'import marshal\ncode = marshal.loads({marshalled!r})\nexec(code)\n'
            if opts['hideconsole']:
                prelude = '\nimport os\nif os.name=="nt":\n import ctypes\n whnd=ctypes.windll.kernel32.GetConsoleWindow()\n if whnd!=0:\n  ctypes.windll.user32.ShowWindow(whnd,0)\n  ctypes.windll.kernel32.CloseHandle(whnd)\n'
                script = prelude + script
            return script
        except Exception as e:
            log_error('Obfuscation error: '+str(e))
            sys.exit(1)
    return source

def output_path_for(original, ext, name, hideconsole):
    base_dir = 'hider'
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    base_name = name if name else os.path.splitext(os.path.basename(original))[0]
    if hideconsole and ext == '.py':
        ext = '.pyw'
    return os.path.join(base_dir, base_name + ext)

def run_pyinstaller(source_path, output_name, ico, hideconsole, debug):
    import shutil
    import tempfile
    tmpdir = tempfile.mkdtemp()
    dest = os.path.join(tmpdir, os.path.basename(source_path))
    shutil.copy(source_path, dest)
    cmd = ['pyinstaller', '--onefile', dest]
    if hideconsole:
        cmd.append('--noconsole')
    if ico:
        cmd.append(f'--icon={ico}')
    if debug:
        log_info('Running: ' + ' '.join(cmd))
    result = subprocess.run(cmd, capture_output=not debug)
    if result.returncode != 0:
        log_error('PyInstaller failed')
        return False
    dist_path = os.path.join(tmpdir, 'dist', output_name + ('.exe' if os.name == 'nt' else ''))
    final_path = os.path.join('hider', output_name + ('.exe' if os.name == 'nt' else ''))
    if not os.path.exists('hider'):
        os.mkdir('hider')
    shutil.move(dist_path, final_path)
    if debug:
        log_info(f'Moved compiled file to {final_path}')
    shutil.rmtree(tmpdir)
    return True

def clear_temp_files(debug):
    import glob
    temp_folder = os.path.join(os.getcwd(), 'build')
    dist_folder = os.path.join(os.getcwd(), 'dist')
    spec_files = glob.glob('*.spec')
    for folder in [temp_folder, dist_folder]:
        if os.path.exists(folder):
            try:
                for root, dirs, files in os.walk(folder, topdown=False):
                    for name in files:
                        os.remove(os.path.join(root, name))
                    for name in dirs:
                        os.rmdir(os.path.join(root, name))
                os.rmdir(folder)
                if debug:
                    log_info(f'Removed folder {folder}')
            except Exception as e:
                log_warn(f'Could not remove folder {folder}: {e}')
    for f in spec_files:
        try:
            os.remove(f)
            if debug:
                log_info(f'Removed file {f}')
        except Exception as e:
            log_warn(f'Could not remove file {f}: {e}')

def main():
    opts = parse_args(sys.argv[1:])
    if opts['version']:
        print('PyHider 1.4')
        sys.exit(0)
    if opts['ascii']:
        print(ASCII_ART)
        sys.exit(0)
    if not opts['file'] and not opts['compile']:
        print_help()
        sys.exit(0)
    if not opts['debug']:
        start_message()
    file_to_process = opts['file'] if opts['file'] else opts['compile']
    compiled_name = opts['name']
    output_file = None
    success = True
    source = obfuscate_source(file_to_process, opts)
    ext = '.pyw' if opts['hideconsole'] and not opts['compile'] else '.py'
    output_file = output_path_for(file_to_process, ext, compiled_name, opts['hideconsole'])
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(source)
    log_info(f'Generated embedded script at {output_file}')
    if opts['compile']:
        if not opts['debug']:
            progress_bar("Compiling", duration=3)
        compiled_name = opts['name'] if opts['name'] else os.path.splitext(os.path.basename(opts['compile']))[0]
        if opts['debug']:
            log_info(f'Launching pyinstaller for {opts["compile"]}')
        success = run_pyinstaller(output_file, compiled_name, opts['ico'], opts['hideconsole'], opts['debug'])
    if opts['clear']:
        clear_temp_files(opts['debug'])
    if not success:
        sys.exit(1)
    sys.exit(0)

if __name__ == '__main__':
    main()
