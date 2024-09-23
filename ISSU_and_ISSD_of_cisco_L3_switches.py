def upgradeDowngrade(self, testscript, testbed, hdl, image):
    '''This function upgrades/downgrades the device
       call: upgradeDowngrade(self, testscript, dutToTest_obj, downgrade_image)
    '''
    image_name = image.split('/')
    image_name = image_name[len(image_name)-1]
    log.info('Checking if {0} image is present in box or not'.format(image_name))
    cmd = 'dir | grep {0}'.format(image_name)
    try:
        cmd_out = hdl.execute(cmd)
    except Exception:
        log.error(traceback.format_exc())
        self.errored('error executing command %s' % cmd)    
    if re.search(r"(\b{0}\b)".format(image_name),cmd_out):
        log.info('Image {0} is present in the box'.format(image_name))
    else:
        log.info('Copy image {0} to the box'.format(image_name))
        tftp_password = testbed.servers.tftp.password
        tftp_username = testbed.servers.tftp.username
        response = Dialog([
        [r'.*Warning: There is already a file existing with this name. Do you want to overwrite \(y/n\)\?\[n\] '
         , lambda spawn: spawn.sendline('y'), None, True, False],
        [r'.*Warning: There is already a file existing with this name. Do you want to.*'
         , lambda spawn: spawn.sendline('y'), None, True, False],
        [r'.*login\:', lambda spawn: spawn.sendline(tftp_username), None,
         True, False],
        [r'.*password\:', lambda spawn: spawn.sendline(tftp_password),
         None, True, False],
        [r'Do you wish to proceed anyway\?\s+\(y/n\)\s+\[n\]',
         lambda spawn: spawn.sendline('y'), None, True, False],
        [r'.*Enter vrf \(If no input\, current vrf \'default\' is considered\)\:'
         , lambda spawn: spawn.sendline('management'), None, True,
         False],
        ])
        copy = copy_image(self, testbed, hdl, image, response)
        if copy == 0:
            log.error('Copy image {0} failed...please debug'.format(image_name))
            testscript.parameters['fail_flag'] = 1
            self.failed()
        else:
            log.info('Copy image {0} success'.format(image_name))

    cmd = 'show version'
    try:
        cmd_out = hdl.execute(cmd)
    except Exception:
        log.error(traceback.format_exc())
        self.errored('error executing command %s' % cmd)
    if re.search(r"(\b{0}\b)".format(image_name),cmd_out):
        log.info('DUT is already running with {0} image'.format(image_name))
    else:
        log.info('Downgrading/Upgrading DUT to {0} image...'.format(image_name))
        cmd = 'install all nxos bootflash:{0} non-interruptive'.format(image_name)
        try:
            hdl.execute(cmd, timeout = 1200, prompt_recovery=True)
        except Exception:
            log.error(traceback.format_exc())
            self.errored('error executing command %s' % cmd)
        time.sleep(360)
        disconnect_connect_device(hdl)
        cmd = 'show version'
        try:
            cmd_out = hdl.execute(cmd)
        except Exception:
            log.error(traceback.format_exc())
            self.errored('error executing command %s' % cmd)    
        if re.search(r"(\b{0}\b)".format(image_name),cmd_out):
            log.info('Successfully downgraded/upgraded to {0}'.format(image_name))
        else:
            log.error('Failed to downgrade/upgrade to {0}'.format(image_name))
            testscript.parameters['fail_flag'] = 1
            self.failed()
