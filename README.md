[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-24ddc0f5d75046c5622901739e7c5dd533143b0c8e959d652212380cedb1ea36.svg)](https://classroom.github.com/a/BsFdJ6lI)
<a name="readme-top"></a>
[![Open in Codespaces](https://classroom.github.com/assets/launch-codespace-f4981d0f882b2a3f0472912d15f9806d57e124e0fc890972558857b51b24a6f9.svg)](https://classroom.github.com/open-in-codespaces?assignment_repo_id=10162029)

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/uol-feps-soc-comp2913-2223s2-classroom/project-squad30">
    <img src="vertex/app/static/images/logo.jpeg" alt="Logo" width="80" height="80">
  </a>

<h3 align="center">The Vertex Sports Centre Management System</h3>
  
  <p align="center">
    A comprehensive sports centre management system in Python and Flask.
    <br />
    <a href="https://github.com/uol-feps-soc-comp2913-2223s2-classroom/project-squad30"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/uol-feps-soc-comp2913-2223s2-classroom/project-squad30/issues">Report Bug</a>
    ·
    <a href="https://github.com/uol-feps-soc-comp2913-2223s2-classroom/project-squad30/issues">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Issues</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details><br>



<!-- ABOUT THE PROJECT -->
## About The Project

Design, development and testing of a sports centre management system in Python using Flask, developed for the COMP2913 Software Engineering Principles Group Project.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

* [![Python][Python.com]][Python-url]
* [![Flask][Flask.com]][Flask-url]
* [![Bootstrap][Bootstrap.com]][Bootstrap-url]
* [![HTML5][HTML5.com]][HTML5-url]
* [![CSS3][CSS3.com]][CSS3-url]
* [![GitHub Actions][Actions.com]][Actions-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple steps:
*Note*: Windows steps assume that you're using PowerShell from within the [Windows Terminal](https://apps.microsoft.com/store/detail/windows-terminal/9N0DX20HK701?hl=en-gb&gl=gb&rtc=1) app.

## Cloning the repository

```bash
> git clone https://github.com/uol-feps-soc-comp2913-2223s2-classroom/project-squad30.git
```

## Setting up the repository to run the application

**You should only need to do this once (the first time you clone) with proper git usage.**

1. Create your virtual environment in the project-squad30 directory. As long as the environment is called "env", it won't be uploaded to version control (see the gitignore file).
```bash
> python3 -m venv env # "env" is the name of the environment
# or
> python -m venv env
```

2. Activate your virtual environment. 
```bash
# Windows
> ./env/Scripts/activate
# Linux/Mac [?]
> source ./env/bin/activate

# When you want to deactivate later
> deactivate
```

3. Install project requirements.
```bash
> pip3 install -r requirements.txt
# or
> pip install -r requirements.txt
```

4. Set environment variables.

```bash
# Windows (powershell)
> $env:SECRET_KEY='secretkeygoeshere-see-teams'
> $env:TOKEN_SALT='emailsaltgoeshere-see-teams'
> $env:EMAIL_PASSWORD='emailpasswordgoeshere-see-teams'
> $env:FLASK_DEBUG=1 # if you want to run the app in debug mode
> $env:PUBLISHABLE_KEY='publishablekeygoeshere-see-teams'
> $env:SECRET_STRIPE_KEY='secretstripekeygoeshere-see-teams'
# Linux/mac
# Look up how to make environment variables persist to prevent having to re-do this step every time you open a new terminal.
> export SECRET_KEY='secretkeygoeshere-see-teams'
> export TOKEN_SALT='emailsaltgoeshere-see-teams'
> export EMAIL_PASSWORD='emailpasswordgoeshere-see-teams'
> export FLASK_DEBUG=1
> export PUBLISHABLE_KEY='publishablekeygoeshere-see-teams'
> export SECRET_STRIPE_KEY='secretstripekeygoeshere-see-teams'
```

5. Run pytest. This will initialise some caches and the database for you.

```bash
> python3 -m pytest -v
# or 
> python -m pytest -v
```

6. The project should be ready to run.
Check by running it.

```bash
> cd vertex
> flask run
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ISSUES -->
## Issues

See the [open issues](https://github.com/uol-feps-soc-comp2913-2223s2-classroom/project-squad30/issues) for a full list of backlog, known issues, their priorities and assignees.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

### Squad 30

* Divyashri Ravichandran - [@DivyashriRavichandran](https://github.com/DivyashriRavichandran) - sc21dr@leeds.ac.uk
* Theo Addis - [@27theo](https://github.com/27theo) - sc21tcda@leeds.ac.uk
* Kavya Pothapragada - [@sc21k2p](https://github.com/sc21k2p) - sc21k2p@leeds.ac.uk
* Vindhyaa Saravanan - [@Vindhyaa-Saravanan](https://github.com/Vindhyaa-Saravanan) - sc21vs@leeds.ac.uk
* Aidan Nash - [@aidann21](https://github.com/aidann21) - sc21an@leeds.ac.uk
* Ilham Abdullayev - [@sc20ia](https://github.com/sc20ia) - sc20ia@leeds.ac.uk


### Project Links:

* [Project Repository](https://github.com/uol-feps-soc-comp2913-2223s2-classroom/project-squad30)
* [Project Wiki](https://github.com/uol-feps-soc-comp2913-2223s2-classroom/project-squad30/wiki)

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[Bootstrap.com]: https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white
[Bootstrap-url]: https://getbootstrap.com
[JQuery.com]: https://img.shields.io/badge/jQuery-0769AD?style=for-the-badge&logo=jquery&logoColor=white
[JQuery-url]: https://jquery.com 
[Flask.com]: https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white
[Flask-url]: https://flask.palletsprojects.com/en/2.2.x/
[Python.com]: https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54
[Python-url]: https://python.org
[Actions.com]: https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white
[Actions-url]: https://docs.github.com/en/actions
[CSS3.com]: https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white
[CSS3-url]: https://www.w3.org/Style/CSS/Overview.en.html
[HTML5.com]: https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white
[HTML5-url]: https://www.w3.org/html/
