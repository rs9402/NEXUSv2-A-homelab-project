This folder includes all the scripts and data for my server control dashboard. The purpose of this web application is so that I can shut down
my server from any device on the local network. Due to this being a sensitive operation, I have employed the use of AI, namely Gemini, to help me with
the scripting of the auth service, as well as the general html. The auth service works by being unencrypting the database, reading it, and sending a
response depending on the input on the frontend. Since it is ran exclusively on localhost (therefore isolated from the rest of the network), it is more 
secure than if it were running on an exposed port. The 'shutdown' operation is carried out by triggering a simple powershell script.

My auth db and environment variables, as well as the easter egg in the web ui have been redacted for my privacy and security.