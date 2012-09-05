About
=====

This is a Pyramid application that allows users to contribute keywords
for inclusion into the cloud.  Any users that are allowed via Pyramid's
auth policies will be able to contribute words, but only those considered
as part of the 'group:Administrators' principal will be able to manage
keywords and regenerate the word cloud.

*Note*: this application wasn't designed to be generic -- all the styles
and templates all effectively exist purely for integration into a
Diazo-based theme.  You're more than welcome to steal ideas or otherwise
develop the code to suit your own requirements.

Features
========

* Generate tag clouds using PyTagCloud
* Global permissions granted to Authenticated/Administrator users 
  using custom Root object
* Various keyword views -- add, manage, export

  * Templates to suit these, including macros and more
  * Custom management form

* Deform schemas for keywords add form

  * Use Bleach to clean incoming words of HTML

* Entered On date defaults to utcnow
* Fanstatic resources:

  * Custom CSS for application 
  * Serve fonts from our custom hosting
  * Utilise jcu.common static resources


