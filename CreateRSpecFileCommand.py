import sublime
import sublime_plugin
import re, inspect, os

class CreateRspecFileCommand(sublime_plugin.WindowCommand):
  def run(self):
    path  = self.window.active_view().file_name()
    utils = RspecUtils(path)

    if utils.is_spec():
      for possilble_path in utils.implementation_candidates():
        if os.path.isfile(possilble_path):
          self.window.open_file(possilble_path)
          break
    else:
      spec_path = utils.to_spec_path()
      if not os.path.isfile(spec_path):
        if not sublime.ok_cancel_dialog("Create new file"): return True
        if not os.path.isdir(utils.spec_folder()): os.makedirs(utils.spec_folder())
        open(spec_path, 'a').write(utils.spec_template())
      self.window.open_file(spec_path)

    self.window.active_view().run_command('reveal_in_side_bar')


import os
from string import Template


class CodeParser():
  REGEX = re.compile(r"""
    def[ ]+
      \ *?
    (?P<name>[\w\.\=\_\?\!\<\>\[\]]+)
  """, re.VERBOSE | re.MULTILINE | re.UNICODE)


  def __init__(self, path):
    self.path = path

  def methods(self):
    private = self.__code().find("private")
    matched = self.REGEX.finditer(self.__code()[:private])
    method_names = [group for match in matched for group in match.groups()]
    if method_names.count("initialize") > 0: method_names.remove("initialize")
    return method_names

  def __code(self):
    return open(self.path, 'r').read()


class RspecUtils():
  TEMPLATE = Template(
'''# frozen_string_literal: true

require '${helper_path}'
${implementation_path}
${prefix}describe ${classname} do
${body}
end
''')

  DESCRIBE_TEMPLATE = Template(
'''\
  describe "#${methodname}" do
    it "" do
    end
  end'''
)

  def __init__(self, path):
    self.path = path

  def classname(self):
    start_position = self.path.index(self.__keyfolder()) + len(self.__keyfolder())
    inner_path     = self.path[start_position:].split(os.path.sep)[2:]
    return '::'.join(map(self.__conver_to_class, inner_path))

  def to_spec_path(self):
    return self.path.replace(self.__keyfolder(), 'spec').replace('.rb', '_spec.rb')

  def spec_template(self):
    methods = CodeParser(self.path).methods()
    body = "\n\n".join([self.DESCRIBE_TEMPLATE.substitute(methodname=method) for method in methods])

    if self.__is_rails():
      helper_path = "rails_helper"
      prefix = ""
      implementation_path = ""
    else:
      helper_path = "spec_helper"
      prefix = "RSpec."
      implementation_path = self.__require_implementation()

    return self.TEMPLATE.substitute(
      classname=self.classname(),
      body=body,
      prefix=prefix,
      helper_path=helper_path,
      implementation_path=implementation_path
    )

  def implementation_candidates(self):
    return [
      self.path.replace('spec/', 'app/').replace('_spec.rb', '.rb'),
      self.path.replace('spec/', 'lib/').replace('_spec.rb', '.rb'),
    ]

  def spec_folder(self):
    return  os.path.sep.join(self.path.replace(self.__keyfolder(), 'spec').split(os.path.sep)[:-1])

  def is_spec(self):
    return 'spec/' in self.path

  def __require_implementation(self):
    return "require './" + self.__to_implementation_path() + "'\n"

  def __to_implementation_path(self):
    start_position = self.path.index(self.__keyfolder())
    return self.path[start_position:].replace('.rb', '')

  def __is_rails(self):
    return 'app/' in self.path

  def __keyfolder(self):
    return 'app' if self.__is_rails() else 'lib'

  def __conver_to_class(self, part):
    return self.__underscore_to_camelcase(part.replace('.rb', ''))

  def __underscore_to_camelcase(self, text):
    return ''.join(word.title() for i, word in enumerate(text.split('_')))

