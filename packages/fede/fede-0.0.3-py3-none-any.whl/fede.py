from colorama import init as colorama_init
from colorama import Fore
from colorama import Style

colorama_init()

cv = f"""
{Fore.GREEN}Hello world!{Style.RESET_ALL} 👋🏻️ 🌎

My name is Fede Calendino, I'm an Argentinian 🇦🇷  living in the UK 🇬🇧.

Creative and adaptable Software Engineer specialized in back-end development, 
with an analytical and a pragmatic approach to problem solving. 
Open-minded and quick to adapt in fast-paced and evolving environments.

Currently working as:

* Contractor Software Engineer at Book.io


✉️\tfede@calendino.com
💻\tgithub.com/fedecalendino
👤\tlinkedin.com/in/fedecalendino
"""

print(cv)
