#!/usr/bin/env python
#
# Copyright (C) 2015 ycmd contributors.
#
# This file is part of ycmd.
#
# ycmd is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ycmd is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ycmd.  If not, see <http://www.gnu.org/licenses/>.

from hamcrest import assert_that
from nose.tools import eq_
from python_handlers_test import Python_Handlers_test
import os.path


class Python_Subcommands_test( Python_Handlers_test ):

  def GoTo_Variation_ZeroBasedLineAndColumn_test( self ):
    tests = [
          {
            'command_arguments': [ 'GoToDefinition' ],
            'response': {
              'filepath': os.path.abspath( '/foo.py' ),
              'line_num': 2,
              'column_num': 5
            }
          },
          {
            'command_arguments': [ 'GoToDeclaration' ],
            'response': {
              'filepath': os.path.abspath( '/foo.py' ),
              'line_num': 7,
              'column_num': 1
            }
          }
      ]
    for test in tests:
      yield self._Run_GoTo_Variation_ZeroBasedLineAndColumn, test


  def _Run_GoTo_Variation_ZeroBasedLineAndColumn( self, test ):
    # Example taken directly from jedi docs
    # http://jedi.jedidjah.ch/en/latest/docs/plugin-api.html#examples
    contents = """
def my_func():
  print 'called'

alias = my_func
my_list = [1, None, alias]
inception = my_list[2]

inception()
"""

    goto_data = self._BuildRequest(
        completer_target = 'filetype_default',
        command_arguments = test[ 'command_arguments' ],
        line_num = 9,
        contents = contents,
        filetype = 'python',
        filepath = '/foo.py'
    )

    eq_( test[ 'response' ],
         self._app.post_json( '/run_completer_command', goto_data ).json )


  def GoToDefinition_NotFound_test( self ):
    filepath = self._PathToTestFile( 'goto_file5.py' )
    goto_data = self._BuildRequest( command_arguments = [ 'GoToDefinition' ],
                                    line_num = 4,
                                    contents = open( filepath ).read(),
                                    filetype = 'python',
                                    filepath = filepath )

    response = self._app.post_json( '/run_completer_command',
                                    goto_data,
                                    expect_errors = True  ).json
    assert_that( response,
                 self._ErrorMatcher( RuntimeError, "Can\'t jump to definition." ) )


  def GoTo_test( self ):
    # Tests taken from https://github.com/Valloric/YouCompleteMe/issues/1236
    tests = [
        {
          'request': { 'filename': 'goto_file1.py', 'line_num': 2 },
          'response': {
              'filepath': self._PathToTestFile( 'goto_file3.py' ),
              'line_num': 1,
              'column_num': 5
          }
        },
        {
          'request': { 'filename': 'goto_file4.py', 'line_num': 2 },
          'response': {
              'filepath': self._PathToTestFile( 'goto_file4.py' ),
              'line_num': 1,
              'column_num': 18
          }
        }
    ]
    for test in tests:
      yield self._Run_GoTo, test


  def _Run_GoTo( self, test ):
    filepath = self._PathToTestFile( test[ 'request' ][ 'filename' ] )
    goto_data = self._BuildRequest( completer_target = 'filetype_default',
                                    command_arguments = [ 'GoTo' ],
                                    line_num = test[ 'request' ][ 'line_num' ],
                                    contents = open( filepath ).read(),
                                    filetype = 'python',
                                    filepath = filepath )

    eq_( test[ 'response' ],
         self._app.post_json( '/run_completer_command', goto_data ).json )


  def GetDoc_Method_test( self ):
    # Testcase1
    filepath = self._PathToTestFile( 'GetDoc.py' )
    contents = open( filepath ).read()

    event_data = self._BuildRequest( filepath = filepath,
                                     filetype = 'python',
                                     line_num = 17,
                                     column_num = 9,
                                     contents = contents,
                                     command_arguments = [ 'GetDoc' ],
                                     completer_target = 'filetype_default' )

    response = self._app.post_json( '/run_completer_command', event_data ).json

    eq_( response, {
      'detailed_info': '_ModuleMethod()\n\n'
                       'Module method docs\n'
                       'Are dedented, like you might expect',
    } )


  def GetDoc_Class_test( self ):
    # Testcase1
    filepath = self._PathToTestFile( 'GetDoc.py' )
    contents = open( filepath ).read()

    event_data = self._BuildRequest( filepath = filepath,
                                     filetype = 'python',
                                     line_num = 19,
                                     column_num = 2,
                                     contents = contents,
                                     command_arguments = [ 'GetDoc' ],
                                     completer_target = 'filetype_default' )

    response = self._app.post_json( '/run_completer_command', event_data ).json

    eq_( response, {
      'detailed_info': 'Class Documentation',
    } )
