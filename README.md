# Event Ticket App

![GitHub all releases](https://img.shields.io/github/downloads/ademolaidowu/event-ticket-app/total)
![GitHub language count](https://img.shields.io/github/languages/count/ademolaidowu/event-ticket-app) 
![GitHub top language](https://img.shields.io/github/languages/top/ademolaidowu/event-ticket-app?color=yellow) 
![Bitbucket open issues](https://img.shields.io/bitbucket/issues/ademolaidowu/event-ticket-app)
![GitHub forks](https://img.shields.io/github/forks/ademolaidowu/event-ticket-app?style=social)
![GitHub Repo stars](https://img.shields.io/github/stars/ademolaidowu/event-ticket-app?style=social)

<table>
  <tr>
    <td><img src="img/tik1.png"/></td>
    <td><img src="img/tik2.png"/></td>
  </tr>
</table>
<br>

<br>
<p><b>An Event Management App API</b></p>
<br>


## ➡️ Description
This is an event management app api created using Django Rest Framework. The project is deployed on pythonanywhere - [Tikwey API](https://tikwey.pythonanywhere.com/api/endpoints)<br>
The database model structure was carefully mapped out in the db_model.drawio file.<br>
The main purpose of the app is to buy tickets online.<br>
This app development was halted due to change in stack and the entire app is being redeveloped using AWS Architecture and React JS.<br>
Check out ongoing Tikwey app website - [Tikwey](https://www.tikwey.com).<br>


## ➡️ Features
* Authentication features such as login, logout, register, change and reset password
* Wallet features for each users to deposit money and buy tickets or trade at events
* Purchase ticket features
* View all events available
* Create, update or delete your event when authenticated
<br><br>


## ➡️ Languages | Technologies
<table>
  <tr>
    <td>Programming Languages</td>
    <td>Python</td>
  </tr>
  <tr>
    <td>Backend</td>
    <td>Django, Django Rest Framework</td>
  </tr>
  <tr>
    <td>Frontend</td>
    <td>Swagger UI</td>
  </tr>
  <tr>
    <td>Database</td>
    <td>Sqlite3</td>
  </tr>
</table>
<br>


## ➡️ Installation
* Clone or download this repository
* Ensure python is installed on your system
* Create virtual environment in parent directory, run `python -m venv venv`
* Activate environment, for bash run `source venv/Scripts/activate`
* Install project packages, navigate to requirements folder and run `pip install -r local.txt`
* Migrate database models, run `python manage.py makemigrations`, then `python manage.py migrate`
* Finally start the app, run `python manage.py runserver`
<br>