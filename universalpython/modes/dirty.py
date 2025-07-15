
def run (args, code):
    
  import yaml
  language_dict = yaml.load(open(args["dictionary"]), Loader=yaml.SafeLoader)

  reserved = language_dict.get("reserved")

  compiled_code = code
#   compiled_code = ur_pyfile.read()

  if args["keep_only"]:
      print ("Compiling", args["file"][0], "...")

  for key, value in reserved.items():
      compiled_code = compiled_code.replace(key, value)

  if args["keep"] or args["keep_only"]:
      eng_pyfile = open("compiled.en.py", "wt")

  if args["keep"] or args["keep_only"]:
      eng_pyfile.write(compiled_code)
      eng_pyfile.close()

  if args["keep_only"] is False:
      exec(compiled_code)