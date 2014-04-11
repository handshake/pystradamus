Pystradamus
===========

Pystradamus is an evidence-based scheduling tool that mines Jira tickets to build probability curves for future work.


Installation
------------

To install via pip (the recommended method)...

.. code-block:: bash

    $ pip install git+https://github.com/Handshake/pystradamus

Now have pystradamus dump a generic config file into your home directory

.. code-block:: bash

    $ pystradamus config > ~/.pystradamus.cfg

Next, edit your specific Jira settings in the config we just
made. Pystradmus will use this configuration from then on. You can also
override the config to use at run time with the `-c` flag.

Usage
-----

Pystradamus works in two stages: Refresh and Predict. The refresh stage
pull historical data from your Jira instance for a particular usage. Example...

.. code-block:: bash

    $ pystradamus history -r joe

This will find all tickets that had an estimate in the past and build
a local sqlite3 database of these estimates as well the time spent
"in-progress" per ticket in Jira.

Predict mode is what projects the currently open and assigned tickets
for this user into the future. For example after having refreshed user
`joe` in the previous step we can now predict his currently open and
assigned workload like so...

.. code-block:: bash

    $ pystradamus history -p joe
    HS-3503 [0.05] Update storefront promo edit preview to match actual dash
        50% chance: 2014-04-11 19:19:59.466628
        95% chance: 2014-04-11 21:24:51.305642
    HS-3323 [0.1] Custom help page for buyers
        50% chance: 2014-04-13 01:10:35.751628
        95% chance: 2014-04-18 19:13:52.397642
    HS-3411 [0.1] Buyer "My Settings Page"
        50% chance: 2014-04-14 02:24:05.444628
        95% chance: 2014-04-25 17:02:53.489642
    HS-3295 [0.1] Storefront Order Screen Rework
        50% chance: 2014-04-15 03:37:35.137628
        95% chance: 2014-05-02 14:51:54.581642
    HS-3310 [0.05] Storefront explanation for multiple ship dates
        50% chance: 2014-04-15 04:15:35.758628
        95% chance: 2014-05-03 11:24:50.788642

What you've just been given is Joe's next 5 tickets, with their 50%
and 95% confidence fits to the calendar. The more history for a user
the better the predictive results.
