# CodeSquid
System call syntaxing

## USAGE
```bash
python3 RunningSquid3.py -p path/to/the/script.sqd --verbose
python3 RunningSquid3.py --help
```

## CODESQUID
syntaxie :
``` squid
syscall | arg1, arg2, arg3; /*comment*/
```
currently working on implement asm and systemcall_id injection to counter the lacks :
```
============================
eax | sqd name | description
============================
1   | emerge   | exit
2   | mitose   | fork
3   | observe  | read
4   | ink      | write
5   | open     | open
6   | close    | close
8   | create   | create
23  | setuid   | setuid
24  | getuid   | getuid
```
