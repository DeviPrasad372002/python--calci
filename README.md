<div align='center'>
    <h1>Calculator Tk</h1>
    <img src='./demo/demo.gif' title='Calculator demo' width='340px' />
</div>

## Motivation
The project aims to encourage programming beginners in Python to contribute to open source projects that go beyond the Terminal, making development more visual.

Therefore, Calculator Tk was created with basic mathematical functionalities and some intentional errors so that corrections and expansions of new features can be made by the target audience (Beginners).

## How to contribute
Follow the steps below:

1. Fork the [Calculator Tk](<https://github.com/matheusfelipeog/calculadora-tk.git>) project in the upper right corner of the screen;
2. Clone the project from your GitHub repository (`git clone https://github.com/YOUR_USERNAME/calculadora-tk.git`);
3. Create your branch to make your modification (`git checkout -b feature/modification_name`);
4. After making your modifications, make a `commit` (`git commit -m "Description of modification"`);
5. Push to your repository (`git push origin feature/modification_name`);
6. In your GitHub repository, create a `Pull Request` so that your modifications can be evaluated for merging into the main project.

## Contributors

| [<img src="https://avatars2.githubusercontent.com/u/25591464?s=115" /><br /><sub>@aguiarcandre</sub>](https://github.com/aguiarcandre) | [<img src="https://avatars2.githubusercontent.com/u/52337966?s=115" /><br /><sub>@carlos3g</sub>](https://github.com/carlos3g) | [<img src="https://avatars0.githubusercontent.com/u/67281981?s=115" /><br /><sub>@ericllma</sub>](https://github.com/ericllma) | [<img src="https://avatars0.githubusercontent.com/u/61357388?s=115" width="115px" height="115px" /><br /><sub>@sam-chami</sub>](https://github.com/sam-chami) | [<img src="https://avatars1.githubusercontent.com/u/64209523?s=115" /><br /><sub>@taisbferreira</sub>](https://github.com/taisbferreira) | [<img src="https://avatars.githubusercontent.com/u/85250817?v=4" width="115px" height="115px"/><br /><sub>@edilsonmatola</sub>](https://github.com/edilsonmatola) | 
|:-:|:-:|:-:|:-:|:-:|:-:|
| [<img src="https://avatars.githubusercontent.com/u/65002100?s=115" /><br /><sub>@maguzzz</sub>](https://github.com/maguzzz) | [<img src="https://avatars.githubusercontent.com/u/60383210?s=115" /><br /><sub>@vinayyak</sub>](https://github.com/vinayyak) |

## For ideas/Bugs
If you find any bug, create an `issue` describing the Bug found that needs to be resolved, providing step-by-step instructions to replicate it.

And if you have any idea for new functionality that can be implemented by other beginners, create an `issue` describing this idea. ;)

## Start
```
$ python main.py
```

or create your own file with the following script, and then follow the procedure above with the corresponding name:
```Python
# -*- coding: utf-8 -*-

# Builtin
import tkinter as tk

# Internal module
from app.calculadora import Calculadora

if __name__ == '__main__':
    master = tk.Tk()
    main = Calculadora(master)
    main.start()
```

## Guides
- Tkinter: [Documentation](https://docs.python.org/3/library/tkinter.html) - *There are several other guides shown right at the beginning of the page*
- Git and Github: [Tutorial on Tableless](https://tableless.com.br/tudo-que-voce-queria-saber-sobre-git-e-github-mas-tinha-vergonha-de-perguntar/) - *Reading*
- Git and Github: [Tutorial on Youtube](https://www.youtube.com/playlist?list=PLQCmSnNFVYnRdgxOC_ufH58NxlmM6VYd1) - *Video Tutorial*
- Pull Request on GitHub: [DigitalOcean Tutorial](https://www.digitalocean.com/community/tutorials/como-criar-um-pull-request-no-github-pt) - *Reading*