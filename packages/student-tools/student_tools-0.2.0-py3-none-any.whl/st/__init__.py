from collections import Counter
import re, sympy, pyfiglet
from sympy import symbols, Eq, solve, sqrt

def info():
  """
  Shows a list of classes and functions to list the functions of each class. To see a FULL list of functions, use cmds().
  Also includes a key to help with function tooltips shown in the Python IDLE or other IDEs.
  """

  print("| class: english")
  print("> cmds: st.english.info()")
  print()
  print("| class: math")
  print("> cmds: st.math.info()")
  print()
  print("| class: util")
  print("> cmds: st.util.info()")

def cmds():
  print("* variables with an * are NOT required. All variables without * are required!")
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
  print("| inverse(word, terms)")
  print("> func: detects the term that cannot be made up of letters in the word")
  print("> word: the main word that makes up terms")
  print("> terms: list of terms in the question")
  print()
  print()
  print("| class: util")
  print()
  print("| clean(x*)")
  print("> func: \"cleans\" the IDLE or console you are working with")
  print("> x*: an integer controlling how many lines of blank space to create")
  print(">     defaults to 100 if value is not given")

class english:
  @staticmethod

  def info():
    """
    List of functions in class 'english' with their descriptions and variable definitions.
    """
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

    print("* variables with an * are NOT required. All variables without * are required!")
    print()
    print("| inverse(word, terms)")
    print("> func: detects the term that cannot be made up of letters in the word")
    print("> word: the main word that makes up terms")
    print("> terms: list of terms in the question")
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

    print("* variables with an * are NOT required. All variables without * are required!")
    print()
    print("| clean(x*)")
    print("> func: \"cleans\" the IDLE or console you are working with")
    print("> x*: an integer controlling how many lines of blank space to create")
    print(">     defaults to 100 if value is not given")
    print()
    print("| word_art()")
    print("> func: initiates a custom ASCII art utility to turn words into ascii art")

  def clean(x=None):
    """
    "Cleans" the IDLE or console you are working with. Work with a clean slate!
    ‎
    x*: (int) an integer controlling how many lines of blank space to create
    x*: defaults to 100 if value is not given
    """
    if x is None:
      for i in range(0, 100):
        print(" " * i)
    else:
      for i in range(0, x):
        print(" " * i)

  def word_art():
    while True:
      def art(text, style='standard'):
        """
        Prints the given text in ASCII art using the specified style/font.
        ‎
        text: the text you want to turn into word art
        style: the style you want the word art to be in
        """
        try:
          result = pyfiglet.figlet_format(text, font=style)
          print(result)
        except Exception as e:
          print(f"Error: {e}. Make sure the style '{style}' is listed in arts().")

      def arts():
        """
        Returns a list of all available ASCII art styles/fonts.
        """
        fonts = sorted(pyfiglet.FigletFont.getFonts())
        for i, font in enumerate(fonts, 1):
          print(f"{i}. {font}")

      def arthelp():
        """
        Prints information on how to use the art, arts, and arthelp functions.
        """
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
