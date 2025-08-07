# codops/cli.py

import argparse
from run import run as run_command  # Importer start depuis start.py
from explain import explain as explain_command      # Importer stop depuis stop.py
from suggest import suggest as suggest_command 
from readme import generate as readme_command 
from doc_explain import docexp as docexp_command 
from doc_suggest import docsug as docsug_command 
from help import help as help_command

def main():
    parser = argparse.ArgumentParser(description='Codops CLI Tool')
    parser.add_argument('command', help='Command to execute')
    
    args = parser.parse_args()
    
    if args.command == 'run':
        run_command()  
    elif args.command == 'explain':
        explain_command()   
    elif args.command == 'suggest':
        suggest_command()
    elif args.command == 'help':
        help_command()
    elif args.command == 'readme':
        readme_command()
    elif args.command == 'docsug':
        docsug_command()
    elif args.command == 'docexp':
        docexp_command()
    else:
        print("Unknown command")

if __name__ == '__main__':
    main()