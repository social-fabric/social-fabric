#
#  Copyright (c) 2020 - Neptunium Inc.
#
#  SPDX-License-Identifier: Apache-2.0
#

class ConsoleProcessor:

    HIDDEN_LINE = 'Password:'

    @classmethod
    def _add_(cls, str_out, line):
        if not line.startswith('Password:'):
            str_out += line
        return str_out

    @classmethod
    def convert(cls, error_code, bytes_in):
        prev_line = ''
        cur_line = ''
        str_out = ''
        if error_code != 0:
            str_out = '<font color="red">ERROR: </font>'
        length = len(bytes_in)
        ix = 0
        while ix < length:
            char = chr(bytes_in[ix])
            if char == '\n':
                if cur_line:
                    str_out = cls._add_(str_out, prev_line)
                    prev_line = cur_line + '<br>'
                    cur_line = ''
            elif char == '\r':
                pass
            elif char == '\033': # Escape
                remaining_length = length - ix
                if remaining_length >= 1 and bytes_in[ix + 1] == 91: # ord('['):
                    if remaining_length >= 4:
                        # Move Up
                        if bytes_in[ix + 3] == 65: # ord('A'):
                            ix += 4
                            continue
                        # Move Down
                        elif bytes_in[ix + 3] == 66: # ord('B'):
                            ix += 4
                            if cur_line:
                                str_out = cls._add_(str_out, prev_line)
                                prev_line = cur_line + '<br>'
                                cur_line = ''
                            continue
                        # Erase Line
                        elif bytes_in[ix + 3] == 75: # ord('K'):
                            ix += 4
                            continue
                        # Reset
                        elif bytes_in[ix + 3] == 109: # ord('m'):
                            cur_line += '</font>'
                            ix += 4
                            continue
                    # Set Color
                    if remaining_length >= 5:
                        if bytes_in[ix + 4] == 109: # ord('m'):
                            color_code = bytes_in[ix + 2:ix + 4].decode()
                            color_name = 'black'  # By default black
                            if color_code == '31':
                                color_name = 'red'
                            elif color_code == '32':
                                color_name = 'green'
                            elif color_code == '33':
                                color_name = 'orange'  #'yellow'
                            elif color_code == '34':
                                color_name = 'blue'
                            elif color_code == '35':
                                color_name = 'magenta'
                            elif color_code == '36':
                                color_name = 'cyan'
                            elif color_code == '37':
                                color_name = 'lightgray'
                            elif color_code == '90':
                                color_name = 'darkgray'
                            elif color_code == '91':
                                color_name = 'lightred'
                            elif color_code == '92':
                                color_name = 'lightgreen'
                            elif color_code == '93':
                                color_name = 'lightyellow'
                            elif color_code == '94':
                                color_name = 'lightblue'
                            elif color_code == '95':
                                color_name = 'lightmagenta'
                            elif color_code == '96':
                                color_name = 'lightcyan'
                            elif color_code == '97':
                                color_name = 'white'

                            cur_line += '<font color="' + color_name + '">'
                            ix += 5
                            continue
            else:
                cur_line += char
            ix += 1

        str_out = cls._add_(str_out, prev_line)
        if cur_line:
            str_out = cls._add_(str_out, cur_line)
        return str_out


if __name__ == '__main__':
    #example = 'Creating network "net_example.com" with the default driver\nCreating ca.example.com ...\n\033[1A\033[2K\nCreating ca.example.com ... \033[32mdone\033[0m\n\033[1B'
    #example = b'Stopping ca.example.com ... \r\n\x1b[1A\x1b[2K\rStopping ca.example.com ... \x1b[32mdone\x1b[0m\r\x1b[1BRemoving ca.example.com ... \r\n\x1b[1A\x1b[2K\rRemoving ca.example.com ... \x1b[32mdone\x1b[0m\r\x1b[1BRemoving network net_example.com\n'
    example = b'Stopping couchdb.peer1.org1.example.com ... \r\nStopping couchdb.peer0.org1.example.com ... \r\nStopping ca.org1.example.com            ... \r\nStopping ca.example.com                 ... \r\n\x1b[3A\x1b[2K\rStopping couchdb.peer0.org1.example.com ... \x1b[32mdone\x1b[0m\r\x1b[3B\x1b[4A\x1b[2K\rStopping couchdb.peer1.org1.example.com ... \x1b[32mdone\x1b[0m\r\x1b[4B\x1b[1A\x1b[2K\rStopping ca.example.com                 ... \x1b[32mdone\x1b[0m\r\x1b[1B\x1b[2A\x1b[2K\rStopping ca.org1.example.com            ... \x1b[32mdone\x1b[0m\r\x1b[2BRemoving couchdb.peer1.org1.example.com ... \r\nRemoving peer1.org1.example.com         ... \r\nRemoving peer0.org1.example.com         ... \r\nRemoving couchdb.peer0.org1.example.com ... \r\nRemoving ca.org1.example.com            ... \r\nRemoving orderer.example.com            ... \r\nRemoving ca.example.com                 ... \r\n\x1b[2A\x1b[2K\rRemoving orderer.example.com            ... \x1b[32mdone\x1b[0m\r\x1b[2B\x1b[6A\x1b[2K\rRemoving peer1.org1.example.com         ... \x1b[32mdone\x1b[0m\r\x1b[6B\x1b[4A\x1b[2K\rRemoving couchdb.peer0.org1.example.com ... \x1b[32mdone\x1b[0m\r\x1b[4B\x1b[7A\x1b[2K\rRemoving couchdb.peer1.org1.example.com ... \x1b[32mdone\x1b[0m\r\x1b[7B\x1b[1A\x1b[2K\rRemoving ca.example.com                 ... \x1b[32mdone\x1b[0m\r\x1b[1B\x1b[3A\x1b[2K\rRemoving ca.org1.example.com            ... \x1b[32mdone\x1b[0m\r\x1b[3B\x1b[5A\x1b[2K\rRemoving peer0.org1.example.com         ... \x1b[32mdone\x1b[0m\r\x1b[5BRemoving network net_example.com\n'
    #with open('/home/frobert/Projets/SocialFabric/social_fabric/log/deploy-20200521-155640.log', 'rb') as f:
    #    example = f.read()
    result = ConsoleProcessor.convert(0, example)
    print(result.encode())
    print(result)
