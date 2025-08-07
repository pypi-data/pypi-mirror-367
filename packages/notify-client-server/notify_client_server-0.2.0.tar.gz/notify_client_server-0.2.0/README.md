* website: <https://arrizza.com/python-notify-client-server.html>
* installation: see <https://arrizza.com/setup-common.html>

## Summary

This project shows a client and server for notifications.

I have several PCs that are on my home network (a couple of Ubuntu, a Mac laptop and a Win11 laptop).
These have backup scripts but those jobs are independent.
To see if any of them ran or failed, I had to manually check the logs and files.
That was a pain.

To fix it, a central server is needed and each of the PCs send a notification when a job passes or fails.
Then using a browser I can see what happened at 2:00AM when the backup jobs ran.

## Server

The server is started by running ```./do_server```.

It assumes that there is a directory "webhost" for a sqlite database to be created there.

Note that the server can be started as an Ubuntu service.
See src/notify_client_server/template_notify_server.service for a starting point for your
service.

Copy that template to ```./webhost/notify_server.service```

Configure it by changing the values in braces ```{ }```.
Currently, these are:

* ```User={svc_user_name}``` : the userid the service should run under
* ```Group={svc_group_name}```: the groupid the service should run under
* ```WorkingDirectory={svc_working_dir}``` : the working directory.
  Use the notify-client-server git repo directory
* ```ExecStart={svc_do_server_path}``` : the path to the ./do_server script.
  Normally this is the svc_working_dir above with ```/do_server```
* use absolute full paths

For example:

```text
<snip>
[Service]
User=my_userid
Group=my_userid
WorkingDirectory=/home/my_userid/projects/notify-client-server
ExecStart=/home/my_userid/projects/notify-client-server/do_server
<snip>
```

## Configuration

See src/notify_client_server/template_cfg.json for configuration.

The configuration json is in three sections.

* ```is_local```: if true, uses value from ```local_mode```, otherwise uses values from ```remote_mode```

#### local_mode

This section is used when your server is running on this local (Ubuntu) machine

* ```is_debug```: is used for the flask server to be automatically restarted when it detects a change.
  Very handy during development!
* ```server_hostname```: the hostname of your local PC
* ```server_port```: the URL port to use. Currently 5004
* ```server_ip```: you can use 127.0.0.1 or 0.0.0.0
* ```server_url```: defaults to the current hostname and port
* ```server_sudo_pwd_path```: holds your root pwd. Since the Ubuntu service is installed via root
  you'll to provide it. Currently, webhost/pf_pwd holds that. The "pf_" indicates it is a personal file
  and the .gitignore does not commit it.
* ```svc_name``` : the name of the service file. Currently notify_server.service
* ```svc_user_name```: the userid to run the service under
* ```svc_group_name```: the groupid to run the service under
* ```svc_working_dir```: the location of the local notify-client-server directory
* ```svc_do_server_path```: the location of the do_server script

* ```clients```: the list of clients to use for ```do_admin push```

#### remote_mode

These are the same as the values above, except for the remote server.

#### pc_info

Holds client information as needed by ```do_admin push```

```pc hostname```: e.g. "pc1" to identify the hostname used by ssh to connect to that client

Each PC entry has to have the following fields:

* ```user_name```: the userid used by ssh to connect to that client
* ```working_dir```: the location of the notify-client-server directory
* any additional fields required for do_admin e.g. jad_dir (see example below)

## Admin

To install and interact with the server, you can use ```do_admin```

That script assumes you have fully installed the notify-client-server:

```text
./do_subm_update full
./do_install

ls -al webhost
-rw-r--r--  1 my_userid my_userid 8282 May  1 20:33 notify_server.db   <= will be created when the server is started
-rw-rw-r--  1 my_userid my_userid 3080 May  4 14:45 notify-server.json
-rw-rw-r--  1 my_userid my_userid  346 May  4 14:45 notify_server.service

./do_server
# fix any warnings, issues, etc.
# note this expects the configuration to be correctly set up, see above
```

* ```./do_admin install``` : installs the Ubuntu service using the notify_server.service
* ```./do_admin restart``` : starts or restarts the service
* ```./do_admin status``` : shows the service's current status
* ```./do_admin journal``` : shows the service log for any warnings etc.
* ```./do_admin stop``` : stops the service
* ```./do_admin uninstall ``` : removes the service from Ubuntu services

* ```./do_admin push ``` : sends the .cfg file to all of your clients
* ```./do_admin test ``` : checks you can connect to your clients and run multiple commands.

#### To add or replace a command

* create a class that inherits from AdminBase
* add any new or override commands to self.fn_map()
* implement the functions as needed
* add fields to notify_server.json as needed

```python
import sys

from notify_client_server.admin_base import AdminBase
from notify_client_server.cfg import cfg
from notify_client_server.os_specific import OsSpecific


# -------------------
## run a command for the local PC or for a remote PC
class App(AdminBase):
    # -------------------
    ## run a command
    #
    # @param cmd  the command to run
    # @return None
    def run(self, cmd):
        # add sample of new command: test
        self.fn_map['pull'] = self.do_pull
        self.fn_map['push'] = self.do_push_cfg  # override builtin push()

        self.run_command(cmd)

    # -------------------
    ## do a git pull in all jad directories
    #
    # @return None
    def do_pull(self):
        lines = [
            'hostname -s',
            'pwd',
            'cd {jad_dir}', <== 
            'pwd',
            'git pull',  # get latest repo version
        ]
        self.run_on_all_pcs('pull', lines, skip_local=False)

    # -------------------
    ## push files to remote PCs
    #
    # @return None
    def do_push_cfg(self):
        # <snip> set rsync opts here
        pc_list = self._get_pc_list()
        for pc in pc_list:
            if pc == OsSpecific.hostname:
                # skip the sender PC
                continue

            path = '{pc}:{jad_dir}/webhost'
            path = cfg.translate_for(pc, path)
            cmd = f'rsync {opts} webhost/ {path}/'
            print(f' --> pushing to {pc}')
            OsSpecific.run_cmd(cmd, print_cb=self._print_cb)
```

## Client(s)

The clients are kicked off using ```./doit```.
See sample/app.py to see how a notification is sent.

It also shows how to send a "ping". This can be used to ensure communication is working
before sending a notification.

## Run

Running ```./do_server```, as typical output:

```text
==== do_server: starting...
     gen: constants_version.py rc=0
16:24:21.076 ==== on 2025/05/04 
00:00:00.000 ==== server.main host=0.0.0.0, port=5004, debug=True
 * Serving Flask app 'server'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5004
 * Running on http://10.0.0.17:5004
Press CTRL+C to quit
 * Restarting with stat
16:24:21.155 ==== on 2025/05/04 
00:00:00.000 ==== server.main host=0.0.0.0, port=5004, debug=True
 * Debugger is active!
 * Debugger PIN: 926-003-063
```

Then open a browser to: http://localhost:5004/. There should be no notifications.

Run ```./doiit```

```text
(venv)$ ./doit
OK   set_env: rc=0
OK   doit: out_dir: /home/myuserid/projects/notify-client-server/out
==== doit: starting...
16:26:29.954 INFO on 2025/05/04 
00:00:00.000 INFO App.init
00:00:00.000 INFO App.run
00:00:00.002 DBG  ping successful      POST 200 http://john26:5004
00:00:00.007 DBG  notify successful    POST 200 http://john26:5004
     doit: run_it rc=0
     doit: overall rc=0
```

The server should output some logging:

```text
127.0.0.1 - - [04/May/2025 16:25:38] "GET / HTTP/1.1" 200 -
127.0.0.1 - - [04/May/2025 16:25:38] "GET /favicon.ico HTTP/1.1" 404 -
127.0.0.1 - - [04/May/2025 16:26:29] "POST /ping HTTP/1.1" 200 -
127.0.0.1 - - [04/May/2025 16:26:29] "POST /notify HTTP/1.1" 200 -
127.0.0.1 - - [04/May/2025 16:27:26] "GET / HTTP/1.1" 200 -
```

Refresh the browser page. There should be a sample notification:

```text
Notifications
        date                 source event         status	description
Delete  2025/05/04 16:26:29	 john26	backup_nas x	ok	    running good 17
Pings: 1
```

The "Pings" should be 1. Run ```doit``` again and it should bump to 2, etc.

Click the Delete buttons to remove the notification on that row.

## crontab

I have a python script that backs up the PC it's on to a NAS and
at the end of that process it sends a notifications to notify_server:

```python
def _notify(self, status, desc):
  tag = self._tag      <== indicates some information where the backup occurred e.g. crontab
  if len(sys.argv) > 1:
      tag = f'{self._tag} {sys.argv[1]}'  <== add info from the command line
  self._client.notify(tag, status, desc) 
```

The status is "ok", "fail" or "warn" depending on what happened during the backup:

```python
status = 'ok'
if self._backups_warn > 0:      <== keeps track of any warnings logged
    status = 'warn'
if self._backups_failed > 0:    <== keeps track of any errors logged
    status = 'err'
```

The desc variable contains some useful info:

```text
00:00:08 overallrc=0; done:0 warns:0 failed:0; needs commit: True;"
   ^-- time to complete the backup HH:MM:SS
           ^-- overall return code
                        ^-- number of directories backed up
                               ^-- number of warnings
                                      ^-- number of errors
                                                ^-- state of git the repo I use for this kind of maintenance  
```

crontab entry looks like this:

```text
45  02  *   *   *     cd /jad; test_notify/doit "crontab" > /jad/test_notify/test.log
      ^-- runs every day at 2:45AM
                        ^-- enters my maintenance repo
                                     ^-- runs the backup and indicates its from a crontab entry instead of manual
                                                                ^-- saves the full log

```
