#!/usr/bin/python

import subprocess
import os
import json

EXT4_FS = "ext4"

def _get_volume(volume):
    return ["--volume", volume]

class VolumeManager:
    def __init__(self, binary, mount_root):
        self.base_cmdline = [binary]
	self.mount_root = mount_root

    def start_server(self, pidfile, cmdline):
        start_cmdline = ["start-stop-daemon", "-S", "-b", "-m", "-p", pidfile,
			"--exec"] + self.base_cmdline + ["--"] + cmdline
        subprocess.check_call(start_cmdline)

    def stop_server(self, pidfile):
        stop_cmdline = ["start-stop-daemon", "-K", "-p", pidfile, "-x"] + self.base_cmdline
        return subprocess.call(stop_cmdline)

    def check_server(self, pidfile):
        check_cmdline = ["start-stop-daemon", "-T", "-p", pidfile]
        return subprocess.call(check_cmdline)

    def server_info(self):
	return subprocess.check_output(self.base_cmdline + ["info"])

    def create_volume(self, size = "", name = "", backup_url = ""):
        cmd = ["volume", "create"]
        if size != "":
            cmd = cmd + ["--size", size]
        if name != "":
            cmd = cmd + ["--name", name]
        if backup_url != "":
            cmd = cmd + ["--backup-url", backup_url]
        data = subprocess.check_output(self.base_cmdline + cmd)
        volume = json.loads(data)
        if name != "":
            assert volume["Name"] == name
        return volume["UUID"]

    def delete_volume(self, volume):
        subprocess.check_call(self.base_cmdline + ["volume", "delete",
            ] + _get_volume(volume))

    def mount_volume(self, volume):
        volume_mount_dir = os.path.join(self.mount_root, volume)
        if not os.path.exists(volume_mount_dir):
    	    os.makedirs(volume_mount_dir)
        assert os.path.exists(volume_mount_dir)
        cmdline = self.base_cmdline + ["volume", "mount",
    		"--mountpoint", volume_mount_dir] + _get_volume(volume)

	subprocess.check_call(cmdline)
        return volume_mount_dir

    def mount_volume_auto(self, volume):
        cmdline = self.base_cmdline + ["volume", "mount"] + _get_volume(volume)

	data = subprocess.check_output(cmdline)
        volume = json.loads(data)
        return volume["MountPoint"]

    def umount_volume(self, volume):
        subprocess.check_call(self.base_cmdline + ["volume", "umount",
            ] + _get_volume(volume))

    def list_volumes(self):
    	data = subprocess.check_output(self.base_cmdline + ["volume", "list"])
        volumes = json.loads(data)
        return volumes["Volumes"]

    def inspect_volume(self, volume):
        cmd = ["volume", "inspect", "--volume", volume]
    	data = subprocess.check_output(self.base_cmdline + cmd)

        return json.loads(data)

    def create_snapshot(self, volume, snapshot_name = ""):
        cmd = ["snapshot", "create"] + _get_volume(volume)
        if snapshot_name != "":
                cmd += ["--name", snapshot_name]
        data = subprocess.check_output(self.base_cmdline + cmd)
        snapshot = json.loads(data)
        return snapshot["UUID"]

    def delete_snapshot(self, snapshot):
        subprocess.check_call(self.base_cmdline + ["snapshot", "delete",
	        "--snapshot", snapshot])

    def inspect_snapshot(self, snapshot):
        output = subprocess.check_output(self.base_cmdline + ["snapshot", "inspect",
	        "--snapshot", snapshot])
        snapshot = json.loads(output)
        return snapshot

    def create_backup(self, snapshot_uuid, dest_url):
        data = subprocess.check_output(self.base_cmdline + ["backup", "create",
		"--snapshot", snapshot_uuid,
		"--dest-url", dest_url])
        backup = json.loads(data)
        return backup["URL"]

    def delete_backup(self, backup_url):
	subprocess.check_call(self.base_cmdline + ["backup", "delete",
		"--backup-url", backup_url])

    def list_backup(self, dest_url, volume_uuid = ""):
        cmd = ["backup", "list",
		"--dest-url", dest_url]
        if volume_uuid != "":
		cmd += ["--volume-uuid", volume_uuid]
	data = subprocess.check_output(self.base_cmdline + cmd)
        backups = json.loads(data)
        return backups["Backups"]

    def inspect_backup(self, backup_url):
	data = subprocess.check_output(self.base_cmdline + ["backup",
                "inspect",
		"--backup-url", backup_url])
        backups = json.loads(data)
        return backups["Backups"]
