Trasker is a task tracking application that is aiming to simplify tasks by centralizing the location for the tasks, it's notes, and documents relating to the task. It also aims to bring an Agile approach to all by similfying terminologies like Epics, Sprints, Bugs, to common terms like Project, Work Week, Road Blocks. It will integrate a board view to easily manage the tasks and move them from one status to another. 

This application was prototyped in Python with a local server running PostgreSQL. The conversion to Django and Docker is still underway so there are reminances of the protoyped code. The file structure for the prototype is as follows:

Prototyped image can be seen below running on Linux using Tkinter:

![Image](https://trasker.app/assets/app_screenshot.png)

- Trasker
  - Trasker
    - trasker_gui/ # contains py view files that build out the gui.
      - supporting_view/ # contains py files that support building tkinter views from the trasker_gui folder.
    - trasker_cli.py
    - trasker_db_psql.py
    - trasker_gui.py
    - trasker_psql.py

 
The project files that will remain after conversion are:
- Trasker
  - Trasker
    - init.py
    - asgi.py
    - settings.py
    - urls.py
  - trasker_app (and all files contained)
  - .env (will need to populate as it is added to the gitignore)
  - docker-compose.yaml
  - Dockerfile
  - manage.py
  - requirements.txt

