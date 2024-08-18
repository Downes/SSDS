# SSDS
Stephen's Simple Data Store

This is a test project with an app written in Python intended to be run on one server and a client writtern in Javascript intended to be run on any number of remote servers. 

SUPER-BASIC and NOT TO BE USED IN PRODUCTION

The Python App is written in Flask (with the help of ChatGPT). After registering and logging in, a user can use the Javascript application to create and store a set of name-value pairs to a simple database. This data is them available to any Javascript client using the right credentials.

On the client side, the user can create a number of name-value pairs, each identified with a key. The user can edit the values, sav to the app, or delete the name-value pair.

NOT A SECURE APP

The SQLite database used by the Flask App is not encrypted. Though the Javascript client connects with the App ising SSL, the name-value pairs are not otherwise encrypted in transit. Access to the database to logged-in users is enabled with an access code sent as a URL parameter to the Javascript app, whereupon it is stored as a cookie. Access codes are short-lived.


Why I Built This

I looked for a simple way I could save name-value pairs to a cloud database in order to access them later using a Javascript-based web page, and couldn't find anything. I intend to use this to write my demo Javascript-based web page, for which I have a specific purpose in mind. 

There's probably any number of uses for a service like this. Maybe this service exists elsewhere; if you know of one, please tell me.

If you find this project worthwhile and would like to contribute security features to it, please be my guest. I'd love to make it more secure.


Usage

I used Reclaim Cloud's Marketplace to create a Flask app. https://app.my.reclaim.cloud/ 

Create the app. It will have an address like 'https://env-1873872.ca.reclaim.cloud'. Or just use this address and don't worry at all about setting up the Flask App. If you do create the app, record the new address. Use WebSSH to install the dependencies listed in requirements.txt and upload the code in the app subdirectory of this repository into /var/www/webroot/ROOT using sftp, git or whatever. Register an account at 'https://env-1873872.ca.reclaim.cloud/register' (for whatever URL you are using). 

On a second server (any server that hosts web pages will do) place the web page flasker.html
If you used the 'https://env-1873872.ca.reclaim.cloud' Flask app you don't have to do anything; otherwise replace every instance of 'https://env-1873872.ca.reclaim.cloud' with the new URL of your Flask app. Then navigate to flasker.html on your second server. It will ask you to login, then function as described thereafter.

If you don't want to do any of this, just register an account at 'https://env-1873872.ca.reclaim.cloud/register' and then go to https://www.downes.ca/CList/flasker.html  


Updates

I'll probably make some changes. Things I have in mind:
- 'Register' link on the login page
- Method to select between more than one instances of the Flask App

