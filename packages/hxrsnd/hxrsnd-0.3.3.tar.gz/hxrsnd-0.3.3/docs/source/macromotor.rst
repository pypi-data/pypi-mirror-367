===========
Macromotors
===========


Base Class
==========

All of the macromotors inherit fromt the ``MacroBase`` class, which implements
the high level interface for each of the macromotors.

.. autosummary::

    ~hxrsnd.macromotor.MacroBase


Base Delay Class
================

All delay macromotors inherit from this abstract class.

.. autosummary::

    ~hxrsnd.macromotor.DelayTowerMacro


System Delay
============

Macromotor ``snd.Delay`` that controls the system delay by manipulating the
following motors:

- ``snd.t1.L``
- ``snd.t4.L``

.. autosummary::

    ~hxrsnd.macromotor.DelayMacro


Delay Energy
============

Macromotor ``snd.E1`` that controls the delay branch energy by manipulating the
following motors:

- ``snd.t1.tth``
- ``snd.t1.th1``
- ``snd.t1.th2``
- ``snd.t4.tth``
- ``snd.t4.th1``
- ``snd.t4.th2``

.. autosummary::

    ~hxrsnd.macromotor.Energy1Macro


Delay Energy Channel Cut
========================

Macromotor ``snd.E1_cc`` that controls the delay branch energy by manipulating
the following motors:

- ``snd.t1.tth``
- ``snd.t4.tth``

.. autosummary::

    ~hxrsnd.macromotor.Energy1CCMacro


Channel Cut Energy
==================

Macromotor ``snd.E2`` that controls the channel cut branch energy by
manipulating the following motors:

- ``snd.t2.th``
- ``snd.t3.th``

.. autosummary::

    ~hxrsnd.macromotor.Energy2Macro
