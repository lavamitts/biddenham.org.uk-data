# On this day ...

This folder contains the SCSS and CSS files used to customise the On this day function.

## How to use

From this folder, run this script:

To generate an uncompressed version of the CSS (for testing) which watches as changes are made:

`sass --watch ./scss/_otd.scss:./css/otd.css --no-source-map --style=expanded`

As a one-off CSS generation script, run this:

`sass ./scss/_otd.scss ./css/otd.css --no-source-map --style=expanded`

## Installation

This uses the Dart Sass command-line interface (CLI), which is part of the sass npm package.

To install this globally:

`npm install -g sass`
