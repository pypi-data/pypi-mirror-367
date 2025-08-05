============
Zebra-0.1.0
============

Usage:

::

    from zebra import Zebra

    z = Zebra( [queue] )
      Constructor with optional printer queue

    z.getqueues()
      Return a list containing available printer queues

    z.setqueue( queue )
      Set the printer queue

    z.setup( direct_thermal=None, label_height=None, label_width=None )
      Set up the label printer using EPL2. Parameters are not set if they are None.
      Not necessary if using AutoSense (hold feed button while powering on)
        direct_thermal - True if using direct thermal labels
        label_height   - tuple (label height, label gap) in dots
        label_width    - in dots

    z.reset_default()
      Resets the printer to factory settings using EPL2

    z.reset()
      Resets the printer using EPL2 - equivalent of switching off/on

    z.autosense()
      Run AutoSense by sending an EPL2 command
      Get the printer to detect label and gap length and set the sensor levels 

    z.print_config_label()
      Send an EPL2 command to print label(s) with current config settings

    z.store_graphic( name, filename )
      Store a 1 bit .PCX file on the label printer using EPL2
        name     - name to be used on printer
        filename - local filename

    z.print_graphic( x, y, width, length, data, qty )
        Print a label from 1 bit data, using EPL2
          x,y    - top left coordinates of the image, in dots
          width  - width of image, in dots.  Must be a multiple of 8.
          length - length of image, in dots
          data   - raw graphical data, in bytes
          qty    - number of labels to print

    z.output( commands )
      Output raw commands to the printer

    z.print_config_label()
      Print label(s) containing the current printer configuration using EPL2

Note:

If you are on a Linux or MacOSX machine using CUPS, you may need to set up a
printer queue using the admin panel at http://localhost:631
