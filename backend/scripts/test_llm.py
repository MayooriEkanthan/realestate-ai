import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from services.llm import ask

print(ask("Say hello in one short sentence."))
