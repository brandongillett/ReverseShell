<p align="center">
  <a href="" rel="noopener">
</p>

<h1 align="center">Reverse Shell</h1>

<div align="center">

</div>

---

<p align="center"> (Education purpose only) This is a project that I personally found interesting to demonstrate use of sockets, threading, and subprocesses in python. Disclamer this project is in the very early stages of being developed most of the code written was written with intent be be released at a production level further down the line (especiall client scripts).
    <br> 
Inspiration/Credit : <a href="https://github.com/malwaredllc/byob">BYOB (Build Your Own Botnet)</a>
</p>

## 📝 Table of Contents
- [About](#about)
- [Getting Started](#getting_started)
- [Deployment](#deployment)
- [Usage](#usage)
- [Built Using](#built_using)
- [TODO](../TODO.md)
- [Contributing](../CONTRIBUTING.md)
- [Authors](#authors)
- [Acknowledgments](#acknowledgement)

## 🧐 About <a name = "about"></a>
The purpose of this project is to help junior developers understand sockets in a fun way that they could have possibly learned in cyber security classes(such as i did). The use of threading and subprocesses is something that is demonstrated here as well which makes this a great introduction to cyber security/operating systems for many developers looking to get educated in these fields. Also with many features for the host such as informations on existing clients also demonstrates the use of databases in SQLite.
## 🏁 Getting Started <a name = "getting_started"></a>
All you will need to get started is an updated versaion of python3 and Ubuntu/Kali Linux.

Installing python3 (linux)

```
sudo apt update

sudo apt install python3
```

### Prerequisites
None at the moment. (As newer versions get released requirements.txt might be in place).

### Installing
After downloading the repository to get this running you do not need much as for the client script is currently hard coded and will be implemented for users to create custom scripts.  
Just run the rshell.py with python3 with admin priveledges.

```
sudo python3 rshell.py
```

From here the host side is all setup, we just need to run the client.py on the clients computer.

```
sudo python3 client.py
```


## 🎈 Usage <a name="usage"></a>
Once you have the host system setup (VPS or Local) and the client is connected, you are now able to reverse shell using the commands created.

To find the commands:

```
help [optional command]
```


## 🚀 Deployment <a name = "deployment"></a>
If you want to install this on a VPS it will be the same as described above just make sure you have the correct ports open and change the IP address in the settings found at the top of the rshell.py script.

## ⛏️ Built Using <a name = "built_using"></a>
- [Python3](https://www.python.org/) - Language
- [Sqlite](https://www.sqlite.org/) - Database
- [VueJs](https://www.kali.org/) - Operating System

## ✍️ Authors <a name = "authors"></a>
- [@brandongillett](https://github.com/brandongillett)

## 🎉 Acknowledgements <a name = "acknowledgement"></a>
- [@byob](https://github.com/malwaredllc/byob) - much credit to this repo and @malwaredllc for the inspiration behind this project
- [@The-Documentation-Compendium](https://github.com/kylelobo/The-Documentation-Compendium) - Documentation behind the README
