<div align='center'>
    <h1>Calculadora Tk</h1>
    <img src='./demo/demo.gif' title='Calculator demo' width='340px' />
</div>

## Motivation

This project aims to encourage Python beginners to contribute to open source projects that go beyond the Terminal, so that development becomes more visual and engaging.

With that in mind, the Tk Calculator was created with basic mathematical functions and some intentional bugs, so that corrections and feature expansions can be implemented by the target audience (beginners).

## How to Contribute

Follow the steps below:

1. Fork the project [Calculadora Tk](https://github.com/matheusfelipeog/calculadora-tk.git) using the button at the top right;
2. Clone the project from your repository (`git clone https://github.com/YOUR_USERNAME/calculadora-tk.git`);
3. Create a new branch for your modification (`git checkout -b feature/your_feature_name`);
4. After making your changes, make a commit (`git commit -m "Description of the modification"`);
5. Push the changes to your repository (`git push origin feature/your_feature_name`);
6. On your GitHub repository, create a Pull Request so your changes can be reviewed and merged into the main project.

## Contributors

| [<img src="https://avatars2.githubusercontent.com/u/25591464?s=115" /><br /><sub>@aguiarcandre</sub>](https://github.com/aguiarcandre) | [<img src="https://avatars2.githubusercontent.com/u/52337966?s=115" /><br /><sub>@carlos3g</sub>](https://github.com/carlos3g) | [<img src="https://avatars0.githubusercontent.com/u/67281981?s=115" /><br /><sub>@ericllma</sub>](https://github.com/ericllma) | [<img src="https://avatars0.githubusercontent.com/u/61357388?s=115" width="115px" height="115px" /><br /><sub>@sam-chami</sub>](https://github.com/sam-chami) | [<img src="https://avatars1.githubusercontent.com/u/64209523?s=115" /><br /><sub>@taisbferreira</sub>](https://github.com/taisbferreira) | [<img src="https://avatars.githubusercontent.com/u/85250817?v=4" width="115px" height="115px"/><br /><sub>@edilsonmatola</sub>](https://github.com/edilsonmatola) |
| :------------------------------------------------------------------------------------------------------------------------------------: | :----------------------------------------------------------------------------------------------------------------------------: | :----------------------------------------------------------------------------------------------------------------------------: | :-----------------------------------------------------------------------------------------------------------------------------------------------------------: | :--------------------------------------------------------------------------------------------------------------------------------------: | :---------------------------------------------------------------------------------------------------------------------------------------------------------------: |
|      [<img src="https://avatars.githubusercontent.com/u/65002100?s=115" /><br /><sub>@maguzzz</sub>](https://github.com/maguzzz)       | [<img src="https://avatars.githubusercontent.com/u/60383210?s=115" /><br /><sub>@vinayyak</sub>](https://github.com/vinayyak)  |

## Ideas / Bugs

If you find a bug, open an `issue` describing the problem and providing steps to reproduce it.

If you have an idea for a new feature that could be implemented by beginners, feel free to open an `issue` describing it. 😉

## Start

$ python main.py

Or create your own file using the following script, then follow the contribution steps above with your chosen filename:

```python
# -*- coding: utf-8 -*-

# Built-in
import tkinter as tk

# Internal module
from app.calculadora import Calculadora

if __name__ == '__main__':
    master = tk.Tk()
    main = Calculadora(master)
    main.start()

Guides
Tkinter: Documentation – There are many other guides shown at the top of the page.

Git and GitHub: Tableless Tutorial – Reading

Git and GitHub: YouTube Playlist – Video lesson

Pull Request on GitHub: DigitalOcean Tutorial – Reading

---
```
