# Rspecer

## Description

Every time when I create new class I need to write tests for it. After many weeks
of repeating sequence "copy file path, mkdir, touch" this plugin was created.

This Sublime Text 2/3 plugin can be used to generate rspec file for current module.
To generate file you can use default command "Create Rspec file for current module.".
This command will generate full directories tree according to your file but using
directory spec instead of app (for Rails apps) or lib (for Sinatra apps).

You can use RSpec plugin (https://github.com/SublimeText/RSpec) to automaticly
open file after creating.
