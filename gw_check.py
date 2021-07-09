from netmiko import ConnectHandler

gateway_list = [['SFO-CUBE-ASR-01', '172.18.142.17']]

output = open("output.html","a")

print >>output,"""<html>
<head>
<title>GATEWAY CHECK STATUS REPORT</title>
</head>
<body>"""

for i in range(len(gateway_list)) :
    gw_name = gateway_list[i][0]
    gw_ip = gateway_list[i][1]

    print("===========================================================================================")
    print("----------------------------------- CHECKING "+ gw_name +"-------------------------------------")
    print >> output,"<p>-------------------------------------------------------------------------------------------</p>"
    print >> output,"<p>%s</p>" % (gw_name)
    print >> output,"<p>-------------------------------------------------------------------------------------------</p>"

    cisco_gw = {
        'device_type': 'cisco_ios_telnet',
        'host':   gw_ip,
        'username': 'administrator',
        'password': 'lab',
        'secret': 'lab',
        'port' : 2006
    }

    try:
        net_connect = ConnectHandler(**cisco_gw)
    except Exception as Error:
        print('\033[1;31m'+"***** ERROR: Connection to the gateway failed due to the reason *****")
        Err= str(Error)
        print Err
        print("***** Skipping the checks *****"+'\033[m')
        print >> output,"""<p style="color:red">ERROR: Connection to the gateway failed due to the reason</p>"""
        print >> output,"""<p style="color:red">%s</p>""" % (Err)
    else:
        print('\033[1;32m'+"***** Successfully connected to the gateway *****"+'\033[m')
        
        print("------------------------------- CHECKING ADMIN PRIVILEGE ----------------------------------")
        if net_connect.check_enable_mode() is True: print('\033[1;32m'+"***** Already have admin privilege *****"+'\033[m')
        else:
            print('\033[1;31m'+"***** WARNING: Admin privilege not enabled... Enabling the admin privilege now *****"+'\033[m')
            net_connect.enable('enable')
            if net_connect.check_enable_mode() is True: print('\033[1;32m'+"***** Enabled the admin privilege *****"+'\033[m')

        print("-------------------------------------------------------------------------------------------")

        if 'GW1-HA1-1A' in gw_name or 'GW1-HA2-1A' in gw_name :
            print("--------------------------------- CHECKING IP STATUS --------------------------------------")
            cmd1=net_connect.send_command('show ip int brief')
            print(cmd1)
            print("-------------------------------------------------------------------------------------------")

        print("------------------------------- CHECKING MEMORY LEAKS -------------------------------------")
        cmd2=net_connect.send_command('show memory debug leaks summary')
        print(cmd2)
        length=len(cmd2.split('\n'))
        if 'GW1-9A' in gw_name:
            if length == 12:
                print('\033[1;32m'+"***** NO MEMORY LEAKS FOUND *****"+'\033[m')
                print >> output,"""<p style="color:green">NO MEMORY LEAKS FOUND</p>"""
            else:
                print('\033[1;31m'+"***** WARNING: MEMORY LEAKS FOUND *****"+'\033[m')
                print >> output,"""<p style="color:red">WARNING: MEMORY LEAKS FOUND</p>"""
        else:
            if length == 19:
                print('\033[1;32m'+"***** NO MEMORY LEAKS FOUND *****"+'\033[m')
                print >> output,"""<p style="color:green">NO MEMORY LEAKS FOUND</p>"""
            else:
                print('\033[1;31m'+"***** WARNING: MEMORY LEAKS FOUND *****"+'\033[m')
                print >> output,"""<p style="color:red">WARNING: MEMORY LEAKS FOUND</p>"""
        print("-------------------------------------------------------------------------------------------")

        print("------------------------------ CHECKING RTP CONNECTIONS -----------------------------------")
        cmd3= net_connect.send_command('show voip rtp connections')
        print(cmd3)
        if 'No active connections found' in cmd3:
            print('\033[1;32m'+"***** NO ACTIVE RTP CONNECTIONS FOUND *****"+'\033[m')
            print >> output,"""<p style="color:green">NO ACTIVE RTP CONNECTIONS FOUND</p>"""
        else:
            print('\033[1;31m'+"***** WARNING: STALE RTP CONNECTIONS FOUND *****"+'\033[m')
            print >> output,"""<p style="color:red">WARNING: STALE RTP CONNECTIONS FOUND</p>"""
        print("-------------------------------------------------------------------------------------------")

        print("------------------------------ CHECKING ACTIVE CALLS --------------------------------------")
        cmd4= net_connect.send_command('show call active voice compact')
        print(cmd4)
        if(len(cmd4) == 0):
            print('\033[1;32m'+"***** NO ACTIVE CALLS FOUND *****"+'\033[m')
            print >> output,"""<p style="color:green">NO ACTIVE CALLS FOUND</p>"""
        else:
            print('\033[1;31m'+"***** WARNING: HUNG CALLS FOUND *****"+'\033[m')
            print >> output,"""<p style="color:red">WARNING: HUNG CALLS FOUND</p>"""
        print("-------------------------------------------------------------------------------------------")

        print("------------------------------- CHECKING FPI CALLS ----------------------------------------")
        cmd5= net_connect.send_command('show voip fpi calls')
        print(cmd5)
        if 'GW1-9A' not in gw_name:
            if 'Number of Calls : 0' in cmd5:
                print('\033[1;32m'+"***** NO FPI CALLS FOUND *****"+'\033[m')
                print >> output,"""<p style="color:green">NO FPI CALLS FOUND</p>"""
            else:
                print('\033[1;31m'+"***** WARNING: HUNG FPI CALLS FOUND *****"+'\033[m')
                print >> output,"""<p style="color:red">WARNING: HUNG FPI CALLS FOUND</p>"""
        print("-------------------------------------------------------------------------------------------")

        print("----------------------------- FINISHED CHECKING "+ gw_name +"-----------------------------------")
        print("===========================================================================================")

print >>output,"</body></html>"
output.close()
exit
