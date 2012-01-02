
Read It's HTTP API
==================

.. http:get:: /login

   Retrieves a standard login form that will drive the Open ID login
   process.

.. http:post:: /login

   Processes a login request.

   :form openid: Open ID URL to authenticate with.

.. http:get:: /logout

   Logs out of the system.

   *Read It* doesn't store session information anywhere outside of the
   encrypted cookie so you don't have to worry about "not logging out".
   The log out functionality removes the cached information from the
   session cookie.

   :status 303: and then redirects to :http:get:`/login`

