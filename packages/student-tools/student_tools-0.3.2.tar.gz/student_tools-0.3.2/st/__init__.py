#  ___                   ___           
# | __|_ _ _ _ ___ _ _  |   \ _____ __ 
# | _|| '_| '_/ _ \ '_| | |) / -_) V / 
# |___|_| |_| \___/_|   |___/\___|\_/  
#                                      

# Required Modules =+--

from collections import Counter
import re, sympy, pyfiglet, requests, packaging
from sympy import symbols, Eq, solve, sqrt
from packaging import version
from packaging.version import Version

# Define Module Version =+--

local_version = "0.3.2"

# Functions =+--

def credits():
  """
  Shows credits for student-tools.
  """

  check_v()
  print("# student-tools credits")
  print("|")
  print("| author: Error Dev")
  print("|")
  print("> all code and comments in this module/package are created by the author, Error Dev")
  print("> need to contact me? any bugs in this version? just do st.author() and tell me!")

def author():
  """
  Lists the author and his contact information.
  """

  check_v()
  print("# contact information")
  print("| name: Error Dev")
  print("> discord: @error_dev")
  print("> email: 3rr0r.d3v@gmail.com")

def info():
  """
  Shows a list of classes and functions to list the functions of each class. To see a FULL list of functions, use cmds().
  Also includes a key to help with function tooltips shown in the Python IDLE or other IDEs.
  """

  check_v()
  print("# to see a full list of functions, use cmd()")
  print()
  print("| class: english")
  print("> cmds: st.english.info()")
  print()
  print("| class: math")
  print("> cmds: st.math.info()")
  print()
  print("| class: util")
  print("> cmds: st.util.info()")
  print()
  print()
  print("# tooltip legend")
  print("|          (int): an integer variable 1 2 3")
  print("|       (string): any text (including numbers and symbols) as a string with quotes \"string\"")
  print("|         (list): a list of items [1, 2, a, b, c]")
  print("| (list strings): a list of strings [\"string\"]")

def cmds():
  """
  Shows a list of all the classes and their functions.
  """

  check_v()
  print("* variables with an * are NOT required. All variables without * are required!")
  print()
  print("| no class")
  print()
  print("| credits()")
  print("> func: shows credits for student-tools")
  print()
  print("| author()")
  print("> func: lists the author and his contact information")
  print()
  print("| info()")
  print("> func: shows a list of classes and functions to list the functions of each class")
  print()
  print("| cmds()")
  print("> func: shows a list of all the classes and their functions")
  print()
  print("| version()")
  print("> func: checks your current version and tells you if you need to update")
  print()
  print("| license()")
  print("> func: shows the full proprietary license for the student-tools package")
  print()
  print()
  print("| class: english")
  print()
  print("| extra_chars(word, terms)")
  print("> func: detects the term that cannot be made up of letters in the word")
  print("> word: the main word that makes up terms")
  print("> terms: list of terms in the question")
  print()
  print("| word_value(values, term)")
  print("> func: calculate the sum of all letters in term")
  print("> values: list of letters and their value in the form LETTER:VALUE")
  print("> term: the term to find the value of")
  print()
  print("| substitution(word, code, type, inpt)")
  print("> func: a substitution cipher")
  print("> word: the word/decoded version to map each letter to a symbol")
  print("> code: the code/encoded version that maps onto each letter of the word")
  print("> type: encode (0) or decode (1)")
  print("> inpt: list of words or codes to encode or decode")
  print()
  print()
  print("| class: math")
  print()
  print("| inverse(function)")
  print("> func: find the inverse function of any equation or function")
  print("> function: the function or equation to inverse")
  print()
  print()
  print("| class: util")
  print()
  print("| clean(x*)")
  print("> func: \"cleans\" the IDLE or console you are working with")
  print("> x*: an integer controlling how many lines of blank space to create")
  print(">     defaults to 100 if value is not given")
  print()
  print("| separator(x*)")
  print("> x*: the length of the separator")
  print(">     defaults to 70 if value is not given")

def version():
    """
    Checks the current version and tells if there is a newer version.
    Also warns if the current version does not match any student-tools version available on PyPI.
    Warns if the current version is yanked.
    """

    check_v()
    try:
        response = requests.get("https://pypi.org/pypi/student-tools/json", timeout=7)
        response.raise_for_status()
        data = response.json()
        latest_version = data["info"]["version"]
        all_versions = data["releases"].keys()

        # Check if local_version is in available versions
        if local_version not in all_versions:
            print(f"| It seems like your current installed version ({local_version}) does not match any available versions!")
            print("> You could be using a fake version of student-tools, which could contain dangerous data or malware!")
            print("> Please delete this version, and install a real version with the following command!")
            print("> pip install student-tools")

        else:
            # Check if local_version is yanked
            release_files = data["releases"][local_version]
            is_yanked = any(file_info.get("yanked", False) for file_info in release_files)
            
            if is_yanked:
                print(f"| You are currently using a yanked version! Please update to the latest proper version, {latest_version} using:")
                print(f"> pip install student-tools=={latest_version}")
            elif Version(local_version) < Version(latest_version):
                print(f"| A newer version is available! Please update to {latest_version} using:")
                print(f"> pip install student-tools=={latest_version}")
            else:
                print(f"| You are using the latest version, {local_version}.")

    except Exception as e:
        print("| Could not connect to PyPI to check the latest version.")
        print(f"> Please report this error to the author(): {e}")
        print("> Please also manually check if there is a new version, which may fix this bug.")

def license():
    """
    Shows the full proprietary license for the student-tools package.
    """

    print("student-tools Proprietary License")
    print()
    print("Copyright (c) Error Dev")
    print()
    print("All rights reserved.")
    print()
    print("License")
    print()
    print('This license governs the use, reproduction, modification, and distribution of the software package "student-tools" (hereinafter "the Software"), created and owned by Error Dev.')
    print()
    print("1. Grant of License")
    print()
    print("Error Dev hereby grants you a personal, non-exclusive, non-transferable, and limited license to use the Software strictly for your own personal or internal use.")
    print()
    print("2. Restrictions")
    print()
    print("You are NOT permitted to:")
    print(" - Copy, modify, distribute, sell, lease, sublicense, or otherwise transfer the Software or any derivative works to any third party without the prior written consent of Error Dev.")
    print(" - Remove, obscure, or alter any copyright notices, trademarks, or other proprietary rights notices contained in the Software.")
    print(" - Use the Software in any manner that could harm, disable, overburden, or impair the Software or interfere with any other party's use and enjoyment of the Software.")
    print(" - Use the Software for any unlawful purposes.")
    print()
    print("3. Attribution")
    print()
    print("If you are granted permission by Error Dev to redistribute or modify the Software, you must provide prominent attribution to Error Dev, including all of the following:")
    print()
    print(" - Retain the original copyright notice.")
    print(" - Include the following attribution statement in any distributions or derivative works:")
    print()
    print('   > "This product includes software developed by Error Dev (https://devicals.github.io/)."')
    print()
    print(" - Clearly state if your distribution is a remix, modified version, or derivative work of the original Software.")
    print()
    print("   For example, include a notice such as:")
    print()
    print('   > "This is a modified version of the original software developed by Error Dev."')
    print()
    print("4. Ownership")
    print()
    print("The Software is licensed, not sold. Error Dev retains all rights, title, and interest in and to the Software, including all copyrights, patents, trade secrets, trademarks, and other intellectual property rights.")
    print()
    print("5. No Warranty")
    print()
    print("The Software is provided “as is,” without warranty of any kind, express or implied. Error Dev disclaims all warranties, including but not limited to merchantability, fitness for a particular purpose, and non-infringement.")
    print()
    print("6. Limitation of Liability")
    print()
    print("Error Dev shall not be liable for any damages arising out of the use or inability to use the Software, even if advised of the possibility of such damages.")
    print()
    print("7. Termination")
    print()
    print("This license is effective until terminated. It will terminate automatically without notice from Error Dev if you fail to comply with any term(s). Upon termination, you must destroy all copies of the Software.")
    print()
    print("8. Governing Law")
    print()
    print("This License shall be governed by the laws of your jurisdiction without regard to conflict of law principles.")

# Classes (& More Functions) =+--

class english:
  @staticmethod

  def info():
    """
    List of functions in class 'english' with their descriptions and variable definitions.
    """

    check_v()
    print("* variables with an * are NOT required. All variables without * are required!")
    print()
    print("| extra_chars(word, terms)")
    print("> func: detects the term that cannot be made up of letters in the word")
    print("> word: the main word that makes up terms")
    print("> terms: list of terms in the question")
    print()
    print("| word_value(values, term)")
    print("> func: calculate the sum of all letters in term")
    print("> values: list of letters and their value in the form LETTER:VALUE")
    print("> term: the term to find the value of")
    print()
    print("| substitution(word, code, type, inpt)")
    print("> func: a substitution cipher")
    print("> word: the word/decoded version to map each letter to a symbol")
    print("> code: the code/encoded version that maps onto each letter of the word")
    print("> type: encode (0) or decode (1)")
    print("> inpt: list of words or codes to encode or decode")

  def extra_chars(word, terms):
    """
    Detects the term that cannot be made up of letters in the word.
    ‎
    word: (string) the main word that makes up terms
    terms: (list strings) list of terms in the question
    """

    check_v()
    word_count = Counter(word)
    for term in terms:
      term_count = Counter(term)
      if any(term_count[char] > word_count.get(char, 0) for char in term_count):
        print(term)

  def word_value(values, term):
    """
    Calculate the sum of all letters in term.
    ‎
    values: (list strings) list of letters and their value in the form LETTER:VALUE
    term: (string) the term to find the value of
    """
    
    check_v()
    letter_values = {}
    for item in values:
        letter, value = item.split(":")
        letter = letter.strip().lower()
        value = int(value.strip())
        letter_values[letter] = value

    term_lower = term.lower()
    total = sum(letter_values.get(char, 0) for char in term_lower)
    print(f"{term}: {total}")

  def substitution(word, code, type, inpt):
    """
    word: (string) the word/decoded version to map each letter to a symbol
    code: (string) the code/encoded version that maps onto each letter of the word
    type: (int) encode (0) or decode (1)
    inpt: (list strings) list of words or codes to encode or decode
    """

    check_v()
    if len(word) != len(code):
        raise ValueError("word and code must be the same length")

    encode_map = {w: c for w, c in zip(word, code)}
    decode_map = {c: w for w, c in zip(word, code)}

    output = []
    if type == 0:  # encode
        for item in inpt:
            encoded = ''.join(encode_map.get(ch, ch) for ch in item)
            output.append(f"{item}: {encoded}")
    elif type == 1:  # decode
        for item in inpt:
            decoded = ''.join(decode_map.get(ch, ch) for ch in item)
            output.append(f"{item}: {decoded}")
    else:
        raise ValueError("type must be 0 (encode) or 1 (decode)")
    return output

class math:
  @staticmethod
  def info():
    """
    List of functions in class 'math' with their descriptions and variable definitions.
    """

    check_v()
    print("* variables with an * are NOT required. All variables without * are required!")
    print()
    print("| inverse(function)")
    print("> func: find the inverse function of any equation or function")
    print("> function: the function or equation to inverse")
    print()
    print("| fib()")
    print("> func: fibonacci series up to n")
    print("> n: an integer defining the max for the series")

  def inverse(function):
    """
    Find the inverse function of any equation or function.
    (Equations must start with y = )
    ‎
    function: The function or equation to inverse.
    """

    check_v()
    expr = function.replace('^', '**')
    expr = re.sub(r'cbrt\(([^)]+)\)', r'(\1)**(1/3)', expr)
    
    match = re.match(r'\s*([a-zA-Z_][a-zA-Z0-9_]*)\(x\)\s*=\s*(.+)', expr)
    if match:
      funcname, rhs = match.groups()
      x = symbols('x')
      y = symbols(funcname)
      lhs = y
    else:
      match2 = re.match(r'\s*y\s*=\s*(.+)', expr)
      if not match2:
          print("Input must be of the form 'f(x) = ...' or 'y = ...'")
          return
      funcname = 'f'
      rhs = match2.group(1)
      x = symbols('x')
      y = symbols('y')
      lhs = y

    rhs_sym = sympy.sympify(rhs, locals={'sqrt': sqrt})
    equation = Eq(lhs, rhs_sym)
    sol = solve(equation, x)
    if not sol:
      print("Could not find inverse.")
      return
    inv = sol[0]

    inv_str = str(inv)
    inv_str = inv_str.replace('**(1/2)', '^0.5')
    inv_str = inv_str.replace('**(1/3)', '^0.3333333333')
    inv_str = re.sub(r'\*\*([0-9]+)', r'^\1', inv_str)
    inv_str = re.sub(r'\b%s\b' % re.escape(funcname), 'x', inv_str)

    print(f"{funcname}\u207B\u00B9(x) = {inv_str}")

  def fib(n):
    """
    Fibonacci series up to n.
    ‎
    n: (int) an integer defining the max for the series
    """

    check_v()
    a, b = 0, 1
    while a < n:
        print(a, end=' ')
        a, b = b, a+b
    print()

class util:
  @staticmethod

  def info():
    """
    List of functions in class 'util' with their descriptions and variable definitions.
    """

    check_v()
    print("* variables with an * are NOT required. All variables without * are required!")
    print()
    print("| clean(x*)")
    print("> func: \"cleans\" the IDLE or console you are working with")
    print("> x*: an integer controlling how many lines of blank space to create")
    print(">     defaults to 100 if value is not given")
    print()
    print("| word_art()")
    print("> func: initiates a custom ASCII art utility to turn words into ascii art")
    print()
    print("| separator(x*)")
    print("> x*: the length of the separator")
    print(">     defaults to 70 if value is not given")

  def clean(x=None):
    """
    "Cleans" the IDLE or console you are working with. Work with a clean slate!
    ‎
    x*: (int) an integer controlling how many lines of blank space to create
    x*: defaults to 100 if value is not given
    """

    check_v()
    if x is None:
      for i in range(0, 100):
        print(" " * i)
    else:
      for i in range(0, x):
        print(" " * i)

  def word_art():
    """
    Initiates a custom ASCII art utility to turn words into ascii art.
    """

    check_v()
    while True:
      def art(text, style='standard'):
        """
        Prints the given text in ASCII art using the specified style/font.
        ‎
        text: the text you want to turn into word art
        style: the style you want the word art to be in
        """

        check_v()
        try:
          result = pyfiglet.figlet_format(text, font=style)
          print(result)
        except Exception as e:
          print(f"Error: {e}. Make sure the style '{style}' is listed in arts().")

      def arts():
        """
        Returns a list of all available ASCII art styles/fonts.
        """

        check_v()
        fonts = sorted(pyfiglet.FigletFont.getFonts())
        for i, font in enumerate(fonts, 1):
          print(f"{i}. {font}")

      def arthelp():
        """
        Prints information on how to use the art, arts, and arthelp functions.
        """

        check_v()
        print("""
        ASCII Art Utility Functions:

        1. art(text, style):
          Prints the given text in the specified ASCII art style/font.
          Example: art("Hello World", "graffiti")

        2. arts():
          Lists all available ASCII art styles/fonts you can use.
          Example: print(arts())

        3. arthelp():
          Shows this help text.
          Example: arthelp()
        """)

      print()
      check_v()
      print("Welcome to ASCII Art Utility!")
      print()
      print("1. Help/Info")
      print("2. List Avaliable Styles")
      print("3. Make Word Art")
      print("x. Exit Program")
      print()
      user_input = input("Choose an option (1/2/3/x): ")
      print()
      if user_input == "1":
        arthelp()
      elif user_input == "2":
        arts()
      elif user_input == "3":
        unstylized = input("Enter the word(s) you want to stylize: ")
        art_style = input("Enter the style you want to use: ")
        print()
        art(unstylized, art_style)
      elif user_input == "x":
        break
      else:
        print(f"Invalid choice '{user_input}'. Please try again.")

  def separator(x=None):
    """
    Creates a separator.
    ‎
    x*: (int) the length of the separator
    x*: defaults to 70 if value is not given
    """

    check_v()
    if x is None:
        print("# " + "-"*70 + " #")
    else:
        print("# " + "-"*x + " #")

# Invisible Functions =+--

def check_v():
    """
    Checks the current version and shows a warning if there is a newer version.
    Also warns if the current version does not match any student-tools version available on PyPI.
    Warns if the current version is yanked.
    """

    try:
        response = requests.get("https://pypi.org/pypi/student-tools/json", timeout=7)
        response.raise_for_status()
        data = response.json()
        latest_version = data["info"]["version"]
        all_versions = data["releases"].keys()

        if local_version not in all_versions:
            print(f"| It seems like your current installed version ({local_version}) does not match any available versions!")
            print("> You could be using a fake version of student-tools, which could contain dangerous data or malware!")
            print("> Please delete this version, and install a real version with the following command!")
            print("> pip install student-tools")
            print()

        else:
            release_files = data["releases"][local_version]
            is_yanked = any(file_info.get("yanked", False) for file_info in release_files)
            
            if is_yanked:
                print(f"| You are currently using a yanked version! Please update to the latest proper version, {latest_version} using:")
                print(f"> pip install student-tools=={latest_version}")
                print()
            elif Version(local_version) < Version(latest_version):
                print(f"| A newer version is available! Please update to {latest_version} using:")
                print(f"> pip install student-tools=={latest_version}")
                print()

    except Exception as e:
        print("| Could not connect to PyPI to check the latest version.")
        print(f"> Please report this error to the author(): {e}")
        print("> Please also manually check if there is a new version, which may fix this bug.")
        print()

#  ___                   ___           
# | __|_ _ _ _ ___ _ _  |   \ _____ __ 
# | _|| '_| '_/ _ \ '_| | |) / -_) V / 
# |___|_| |_| \___/_|   |___/\___|\_/  
#                                      