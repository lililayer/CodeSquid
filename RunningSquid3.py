import os
import subprocess
import pathlib
import click
import random
import time

def PrintHorizontalLine(l='-', in_string = False):
    term_size = os.get_terminal_size()
    line = '\n'+f'\033[0;35m{l*term_size.columns}\033[0m'+'\n'
    if not in_string:
        print(line)
    return line
    
do_verbose = False
full_debug_mode = False

def InvoqueError(text="", _exit="Imediate"):
    _text = "\033[1;91m\tERROR : " + text+"\033[0m"
    print(_text)
    if _exit=="Imediate": exit()
    return _exit

def InvoqueWarning(text=""):
    _text = "\033[1;93m\tWARNING : " + text+"\033[0m"
    print(_text)
    
def Debug(text = "", onlyVerboseMode=True, color="0;36"):
    if onlyVerboseMode and not do_verbose:
        return
    else:
        _text = f"\033[{color}m\tDEBUG : " + text+"\033[0m"
        print(_text)
    return

def AskBoolean(message, expectedTrue = [], expectedFalse = []):
    _text = "\033[1;93m\tASKING : " + message+"\033[0m\t"
    inputs = input(_text)
    if inputs in expectedTrue:
        return True
    elif inputs in expectedFalse:
        return False
    else:
        InvoqueWarning("Wrong answer.")
        AskBoolean(message, expectedTrue, expectedFalse)

keywords = []
class KeyWord:
    def __init__(self, sqd, tag, sub_tag = ""):
        self.sqd = sqd;
        self.tag = tag;
        self.sub_tag = sub_tag
        keywords.append(self)
        return

KeyWord("/*", "open_coment")
KeyWord("*/", "close_coment")
KeyWord(" ", "separator")
KeyWord("\n", "separator")
KeyWord("|", "pipe")
KeyWord(",", "param_separator")
KeyWord(";", "endline")

separators = [' ',',','|',';','\n']

SystemCallGrammars = [
    ["Syscall", "endline"],
    ["Syscall", "pipe", "value", "endline"],
    ["Syscall", "pipe", "value", "param_separator", "value", "endline"],
    ["Syscall", "pipe", "value", "param_separator", "value", "param_separator", "value", "endline"],
    ["Syscall", "pipe", "value", "param_separator", "value", "param_separator", "value", "param_separator", "value", "endline"],
    ["Syscall", "pipe", "value", "param_separator", "value", "param_separator", "value", "param_separator", "value", "param_separator", "value", "endline"],
    ["Syscall", "pipe", "value", "param_separator", "value", "param_separator", "value", "param_separator", "value", "param_separator", "value", "param_separator", "value", "endline"]
]

grammars = [SystemCallGrammars]

def GetKeyword(keyword_stack):
    for keyword in keywords:
        if keyword_stack == keyword.sqd:
            return keyword
    return None

def GetTags(instruction_stack):
    tags = []
    for word in instruction_stack:
        keyword = GetKeyword(word)
        if keyword:
            tags.append(keyword.tag)
    return tags

def GetGrammar(instruction_stack, forceNoDebug=False):
    for grammar in grammars:
        tags = GetTags(instruction_stack)
        if tags in grammar:
            if not forceNoDebug:
                Debug("Instruction found :\n\033[3;34m" + str(tags) + '\033[0m', color='0;36');
            return tags
        else:
            InvoqueError("Grammar not found in " + str(instruction_stack) + " !")
            return None

def GetGrammarElementTypeCount(grammar, elementType):
    counter = 0
    for element in grammar:
        if element == elementType:
            counter += 1
    return counter

def CheckEndInstruction(instruction_stack):
    tags = GetGrammar(instruction_stack, True)
    if (tags != None):
        return True
    return False

def TryGetKeyWord(c, keyword_stack, instruction_stack, instructions):
    keyword = GetKeyword(keyword_stack)
    if keyword != None:
        if keyword.tag != "separator":
            instruction_stack.append(keyword_stack)
        if keyword.tag == "endline":
            if CheckEndInstruction(instruction_stack):
                instructions.append(instruction_stack)
                Debug("Grammar found for " + str(instruction_stack))
                instruction_stack = []
            else:
                InvoqueError("Bad grammar for " + keyword_stack + ".")
        keyword_stack = ""
    elif c in separators:
        keyword = KeyWord(keyword_stack, "value")
        instruction_stack.append(keyword_stack)
        keyword_stack = ""
    return [keyword_stack, instruction_stack, instructions]

def ParseInstructions(script):
    global separators
    instructions = []
    instruction_stack = []
    keyword_stack = ""
    inString = False
    for c in script:
        if c == '"':
            inString = not inString
            if inString:
                tgkw = TryGetKeyWord(c, keyword_stack, instruction_stack, instructions)
                keyword_stack = tgkw[0]
                instruction_stack = tgkw[1]
                instructions = tgkw[2]
        if not inString:
            if keyword_stack == '\n':
                keyword_stack = ""
            if c in separators:
                tgkw = TryGetKeyWord(c, keyword_stack, instruction_stack, instructions)
                keyword_stack = tgkw[0]
                instruction_stack = tgkw[1]
                instructions = tgkw[2]
        keyword_stack += c
    return instructions
            
def ParseComents(script):
    global_stack = ""
    last = ""
    comenting = False
    for c in script:
        if last == '/' and c == '*':
            comenting = True
            global_stack = global_stack[:-1]
        elif last == '*' and c == '/':
            comenting = False
        elif not comenting:
            global_stack += c
        last = c
    return global_stack


#implemented_functions = ['\n\nglobal itohex\nitohex:\n\tpush edi\n\tmov edi, [esp+8]\n\tmov eax, [esp+12]\n\t\n\tmov ecx, 8\n.digit_loop:\n\trol eax, 4\n\tmov edx, eax\n\tand edx, 0x0f\n\t\n\tmovzx edx, byte [hex_lut + edx]\n\tmov [edi], dl\n\tinc edi\n\t\n\tdec ecx\n\tjnz .digit_loop\n\t\n\tpop edi\n\tret\n'] # transformer un int en char *
#implemented_functions.append() # print eax (qui est un int, donc il faut d'abord appeler itohex (voir au dessus))

#rodata_section = ['\n\nsection .rodata\n\thex_lut db "0123456789abcdef"']

data_section = ['\nsection .data\n']
#data_section.append('\n\trv db 0x0\n')
data_element_id = 0

def StoreString(sqdvalue):
    global data_element_id
    data_element_id += 1
    
    the_string_value = sqdvalue + ',0xa,0x0'
    the_string_name  = "string"+str(data_element_id)
    data_section.append("\n\t" + the_string_name + " db " + the_string_value)
    #the_length_name  = "strlen"+str(data_element_id)
    #data_section.append("\n\t" + the_length_name + " equ $ - " + the_string_name)
    return the_string_name

systemcalls = []
_syscallID = 0
class SystemCall:
    def __init__(self, base,
                    RAX=int(), RDI=str(), RSI=str(), RDX=str(), R10=str(), R8=str(), R9=str(), 
                    EAX=int(), EBX=str(), ECX=str(), EDX=str(), ESI=str(), EDI=str(), EBP=str()
                ):
        self.base = base
        self.RAX    =   RAX;        self.EAX    =   EAX
        self.RDI    =   RDI;        self.EBX    =   EBX
        self.RSI    =   RSI;        self.ECX    =   ECX
        self.RDX    =   RDX;        self.EDX    =   EDX
        self.R10    =   R10;        self.ESI    =   ESI
        self.R8     =   R8;         self.EDI    =   EDI
        self.R9     =   R9;         self.EBP    =   EBP
        systemcalls.append(self)
        KeyWord(base, "Syscall", "function"+str(RAX+EAX))
        return
    
    def GetVia(self):
        if self.EAX != 0:
            return 32
        if self.RAX != 0:
            return 64
        return None

    def GetAssembler(self, parameters):
        asm = "\n"
        if self.GetVia() == 64: 
            asm += "\n\tmov rax, " + str(self.RAX)
            register_id = 0
            for parameter in parameters:
                final_param = parameter
                inString = (parameter[len(parameter)-1] == '"')
                if inString:
                    final_param = StoreString(parameter)
                    
                if (register_id == 0): asm += "\n\tmov rdi, " + final_param # /!\ need verrify if the parameter types are correct !
                if (register_id == 1): asm += "\n\tmov rsi, " + final_param # types are stored in RSI, RDX etc...
                if (register_id == 2): asm += "\n\tmov rdx, " + final_param
                if (register_id == 3): asm += "\n\tmov r10, " + final_param # /!\ not sure it's in the right order
                if (register_id == 4): asm += "\n\tmov r8, " + final_param
                if (register_id == 5): asm += "\n\tmov r9, " + final_param
                register_id += 1
        if self.GetVia() == 32: 
            asm += "\n\tmov eax, " + str(self.EAX)
            register_id = 0
            for parameter in parameters:
                final_param = parameter
                inString = (parameter[len(parameter)-1] == '"')
                if inString:
                    final_param = StoreString(parameter)
                if (register_id == 0): asm += "\n\tmov ebx, " + final_param  # /!\ need verrify if the parameter types are correct !
                if (register_id == 1): asm += "\n\tmov ecx, " + final_param  # types are stored in RSI, RDX etc...
                if (register_id == 2): asm += "\n\tmov edx, " + final_param 
                if (register_id == 3): asm += "\n\tmov esi, " + final_param  # /!\ not sure it's in the right order
                if (register_id == 4): asm += "\n\tmov edi, " + final_param 
                if (register_id == 5): asm += "\n\tmov ebp, " + final_param 
                register_id += 1
        asm += '\n\tint 0x80\n'
        global full_debug_mode
        if (full_debug_mode):
            asm += '\n\t; [FULL DEBUG MOD] ;\n\tmov ebx, eax\n\tmov eax, 0xFFFFFFFF\n\tint 0x80\n' # for strace
        #asm += f'\n\tmov ecx, eax\n\tmov [rv], ecx\n\tmov eax, 4\n\tmov ebx, 1\n\tmov ecx, [rv]\n\tmov edx, 1\n\tint 0x80\n\n\n'
        #asm += '\n\tcall itohex\n\n' # appeler la fonction qui print eax
        #asm += '\n\tmov ecx, eax\n\tmov [rv], ecx\n\tmov eax, 4\n\tmov ebx, 1\n\tmov ecx, [rv]\n\tmov edx, 1\n\tint 0x80\n\n\n'
        return asm
        
######################################
### DEFINE SYSTEM CALLS TRADS HERE ###
######################################

SystemCall("getuid", EAX=24) # sys_getuid
SystemCall("setuid", EAX=23, EBX="int") # sys_setuid
SystemCall("create", EAX=8, EBX="string", ECX="int") # sys_creat
SystemCall("close", EAX=6, EBX="int") # sys_close
SystemCall("open", EAX=5, EBX="string", ECX="int", EDX="int") # sys_open
SystemCall("ink", EAX=4, EBX="int", ECX="string", EDX="int") # sys_write : std, string, string_length
SystemCall("observe", EAX=3, EBX="int", ECX="string", EDX="int") # sys_read
SystemCall("mitose", EAX=2, EBX="struct_pt_reg") # sys_fork
SystemCall("emerge", EAX=1, EBX="int") # sys_exit : exit_code

def GetSystemCallByBase(base):
    for s in systemcalls:
        if s.base == base:
            return s
    InvoqueError("Bad systemcall name.")
    return None

def GetSyscallValueCountFromInstruction(instruction, grammar):
    value_count = GetGrammarElementTypeCount(grammar, "value")
    Debug("Parameter count : " + str(value_count), color="2;36")
    values = []
    i = 0
    for tag in grammar:
        word = instruction[i]
        if tag == "value":
            values.append(word)
        i += 1
    if len(values) != value_count:
        InvoqueError("Wrong parameter(s) grammar.")
        return None
            
    return values

def GetSystemCallFromInstructionAndCheckValuesFromGrammar(instruction, grammar):
    # GET syscall
    syscall = GetSystemCallByBase(instruction[0])
    if syscall == None: return None
    Debug("RAX : " + str(syscall.RAX) + " \t EAX : " + str(syscall.EAX), color="2;36")
    # GET values
    values = GetSyscallValueCountFromInstruction(instruction, grammar)
    Debug("Values : " + str(values), color="2;36")
    return [syscall, values]

def CompileInstruction(instruction):
    grammar = GetGrammar(instruction)
    if grammar != None:
        syscall_and_check = GetSystemCallFromInstructionAndCheckValuesFromGrammar(instruction, grammar)
        syscall = syscall_and_check[0]
        values = syscall_and_check[1]
        if syscall != None:
            
            asm = syscall.GetAssembler(parameters = values);
            
            return asm
        return None
    return None
    
def CompileInstructions(instructions):
    compiledInstructions = []
    for instruction in instructions:
        compiledInstructions.append(CompileInstruction(instruction))
    return compiledInstructions

@click.command()
@click.option('--sqdman/--no-sqdman', default=False, help='Show the SQD manual and exit. Default is \'no-sqdman\'')
@click.option('--verbose/--no-verbose', default=False, help='Verbose compilation. Default is \'no-verbose\'.')
@click.option('--fdm/--no-fdm', default=False, help='Trigger Full Debug Mode : simulate a syscall error -1 after every systemcalls in the compiled asm code, in order to echo EAX returned values with strace. Default is \'no-fdm\'.')
@click.option('--program', '-p', default="", help='Program\'s path to execute. Ex : \'RunningSquid3.py -p /path/to/the/script/the_script.sqd\'')
@click.option('--container', '-c', default="./Container", help='Folder choosen to put compiled scripts in.')
def main(program, container, verbose, sqdman, fdm):
    if sqdman:
        with open("./Resources/sqdman.txt", 'r') as file:
            manual = file.read()
            print(manual)
        exit()
    
    ### AVOID PARAMETTER'S ERROR ###
    
    if program == '': InvoqueError("No program to compile.");
    if os.path.exists(program) == False: InvoqueError(str(program) + " does not exists.");
    if pathlib.Path(program).suffix != ".sqd": InvoqueError("This is not a RunningSquid (.sqd) program !");
    
    # print the cool title
    try:
        with open("./Resources/title.txt", 'r') as file:
                title = file.read()
                print("\033[1;35m"+title+"\033[0m")
    except Exception as e:
        InvoqueWarning("Can't show the cool title :(" + str(e))
    
    ### LETSGO
    
    global do_verbose
    do_verbose = verbose
    global full_debug_mode 
    full_debug_mode = fdm
    if os.path.exists(program) == False: InvoqueError("This file doesn't exists : " + str(program));
    if pathlib.Path(program).suffix != ".sqd": InvoqueError("This file is not a RuningSquid script.");
    
    try:
        with open(program, 'r') as file:
            _script_ = file.read()
        Debug("the file has been opened successfully.", color='1;36')
    except:
        InvoqueError("Failed to read the script.")
    
    PrintHorizontalLine()
    
    _script_ = ParseComents(_script_);
    #Debug("Parsed coments : \n" + PrintHorizontalLine('-', True) + str(_script_) + PrintHorizontalLine('-', True))
    instructions = ParseInstructions(_script_)
    Debug("Parsed keywords : \n\033[3;34m" + str(instructions) + '\033[0m');
    PrintHorizontalLine()
    compiledInstructions = CompileInstructions(instructions)
    PrintHorizontalLine()
    ### SECTION TEXT
    script = "section .text\n\tglobal _start\n\n_start:";
    for compiledInstruction in compiledInstructions:
        script += compiledInstruction
    ### IMPLEMENTED FUNCTIONS
    #for imp_f in implemented_functions:
    #    script += imp_f
    ### SECTION DATA
    for dataline in data_section:
        script += dataline
        
    # secure shell from buffer overflows : #### !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    #
    
    ### SECTION RODATA
    #for rodataline in rodata_section:
    #    script += rodataline
    Debug("Compiled script : [\33[0m\n\033[3;34m\n" + script + '[\33[0m', color='1;36')
    
    #######################################################################################################################
    
    PrintHorizontalLine()
    ### PUT INTO AN ASSEMBLY FILE ###
    _file_session_id_ = str(random.randrange(100000000000, 999999999999))
    
    Debug("Creating an assembly file...")
    asm_file_name = f"{container}/RUNNING_SQUID_X86_64_Assembly_{_file_session_id_}.asm"
    Debug("File name : " + asm_file_name)
    try:
        with open(asm_file_name, 'x') as f:
            f.write("")
    except Exception as e:
        InvoqueError(e);
        exit()
    
    try:
        Debug("Wrinting datas...")
        with open(asm_file_name, 'w') as f:
            f.write(script)

        with open(asm_file_name, 'r') as f:
            freaden = f.read()
            if freaden != script:
                InvoqueWarning("The contents of the x86-64 assembly file created is different from the script generated (use --verbose too see more).")
                if (verbose):
                    PrintHorizontalLine()
                    InvoqueWarning(freaden)
                    PrintHorizontalLine()
    except:
        InvoqueError("Failed to write in the file !")
        exit()
    
    
    ### COMPILE ASSEMBLY FILE ###
    
    CompileSuccessfull = False
    while not CompileSuccessfull:
        Debug("Compiling assembly file...")
        binary_file_name = f"{container}/RUNNING_SQUID_X86_64_Binary_{_file_session_id_}.o"
        nasm_command = subprocess.Popen(["nasm", "-f", "elf64", asm_file_name, "-o", binary_file_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = nasm_command.communicate()
        decoded_stdout = stdout.decode()
        decoded_stderr = stderr.decode()
        if decoded_stdout != "":
            Debug("NASM STD-OUT : " + decoded_stdout)
        if decoded_stderr != "":
            InvoqueError("NASM STD-ERR : " + decoded_stderr, _exit='no')
            CompileSuccessfull = False    
                    
            if AskBoolean(
                "Do you want to manualy modify the compiled code (Assembler x86_64) ? (y/n) ",
                expectedTrue = ['y', 'yes'],
                expectedFalse = ['n', 'no']
            ):
                Debug("Opening nano...")
                os.system('nano -- ' + asm_file_name)
                Debug("... closed nano.")
                
            else:
                Debug("Exiting...")
                exit()
            
            if AskBoolean(
                "Show saved code ? (y/n) ",
                expectedTrue = ['y', 'yes'],
                expectedFalse = ['n', 'no']
            ):
                with open(asm_file_name, 'r') as f:
                    freaden = f.read()
                    PrintHorizontalLine()
                    Debug("Assembly x86_64 script : [\33[0m\n\033[2;34m" + freaden + '[\33[0m', color='1;36')
                PrintHorizontalLine()
            
        else:
            CompileSuccessfull = True
        
    
    
    ### SET EXECUTABLE
    
    executable_file_name = f"{container}/RUNNING_SQUID_X86_64_Executable_{_file_session_id_}"
    Debug("Set file as executable...")
    try:
        os.system("ld -o " + executable_file_name + " " + binary_file_name)
    except:
        InvoqueError(9)
    
    ### EXECUTE ###
    Debug("Ready to execute !", color='1;36')
    PrintHorizontalLine()
    #Debug("Launching gnome...")
    #os.system('gnome-terminal -- ./'+executable_file_name)
    
    if fdm:
        os.system('strace ' + './' + executable_file_name)
    else:
        os.system('./' + executable_file_name)

    PrintHorizontalLine()
    
if __name__ == '__main__':
    main()
