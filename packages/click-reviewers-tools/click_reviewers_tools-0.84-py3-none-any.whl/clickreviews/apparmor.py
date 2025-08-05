#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; version 3 of the License.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

APPARMOR_POLICIES = {
    "ubuntu": {
        "1.0": {
            "templates": {
                "common": [
                    "default",
                    "ubuntu-sdk",
                    "ubuntu-webapp"
                ],
                "reserved": [
                    "unconfined"
                ]
            },
            "policy_groups": {
                "common": [
                    "audio",
                    "camera",
                    "connectivity",
                    "content_exchange",
                    "content_exchange_source",
                    "keep-display-on",
                    "location",
                    "microphone",
                    "networking",
                    "sensors",
                    "usermetrics",
                    "video"
                ],
                "reserved": [
                    "accounts",
                    "calendar",
                    "contacts",
                    "friends",
                    "history",
                    "music_files",
                    "music_files_read",
                    "picture_files",
                    "picture_files_read",
                    "video_files",
                    "video_files_read"
                ]
            }
        },
        "1.1": {
            "templates": {
                "common": [
                    "default",
                    "ubuntu-sdk",
                    "ubuntu-webapp"
                ],
                "reserved": [
                    "unconfined"
                ]
            },
            "policy_groups": {
                "common": [
                    "audio",
                    "camera",
                    "connectivity",
                    "content_exchange",
                    "content_exchange_source",
                    "keep-display-on",
                    "location",
                    "microphone",
                    "networking",
                    "sensors",
                    "usermetrics",
                    "video",
                    "webview"
                ],
                "reserved": [
                    "accounts",
                    "calendar",
                    "contacts",
                    "debug",
                    "friends",
                    "history",
                    "music_files",
                    "music_files_read",
                    "picture_files",
                    "picture_files_read",
                    "video_files",
                    "video_files_read"
                ]
            }
        },
        "1.2": {
            "templates": {
                "common": [
                    "default",
                    "ubuntu-account-plugin",
                    "ubuntu-push-helper",
                    "ubuntu-scope-network",
                    "ubuntu-sdk",
                    "ubuntu-webapp"
                ],
                "reserved": [
                    "unconfined"
                ]
            },
            "policy_groups": {
                "common": [
                    "accounts",
                    "audio",
                    "camera",
                    "connectivity",
                    "content_exchange",
                    "content_exchange_source",
                    "keep-display-on",
                    "location",
                    "microphone",
                    "networking",
                    "push-notification-client",
                    "sensors",
                    "usermetrics",
                    "video",
                    "webview"
                ],
                "reserved": [
                    "calendar",
                    "contacts",
                    "debug",
                    "history",
                    "music_files",
                    "music_files_read",
                    "picture_files",
                    "picture_files_read",
                    "video_files",
                    "video_files_read"
                ]
            }
        },
        "1.3": {
            "templates": {
                "common": [
                    "default",
                    "ubuntu-account-plugin",
                    "ubuntu-push-helper",
                    "ubuntu-scope-network",
                    "ubuntu-sdk",
                    "ubuntu-webapp"
                ],
                "reserved": [
                    "unconfined"
                ]
            },
            "policy_groups": {
                "common": [
                    "accounts",
                    "audio",
                    "camera",
                    "connectivity",
                    "content_exchange",
                    "content_exchange_source",
                    "in-app-purchases",
                    "keep-display-on",
                    "location",
                    "microphone",
                    "networking",
                    "push-notification-client",
                    "sensors",
                    "usermetrics",
                    "video",
                    "webview"
                ],
                "reserved": [
                    "bluetooth",
                    "calendar",
                    "contacts",
                    "debug",
                    "history",
                    "music_files",
                    "music_files_read",
                    "picture_files",
                    "picture_files_read",
                    "video_files",
                    "video_files_read"
                ]
            }
        },
        "15.10": {
            "templates": {
                "common": [
                    "default",
                    "ubuntu-account-plugin",
                    "ubuntu-push-helper",
                    "ubuntu-scope-network",
                    "ubuntu-sdk",
                    "ubuntu-webapp"
                ],
                "reserved": [
                    "unconfined"
                ]
            },
            "policy_groups": {
                "common": [
                    "accounts",
                    "audio",
                    "camera",
                    "connectivity",
                    "content_exchange",
                    "content_exchange_source",
                    "in-app-purchases",
                    "keep-display-on",
                    "location",
                    "microphone",
                    "networking",
                    "push-notification-client",
                    "sensors",
                    "usermetrics",
                    "video",
                    "webview"
                ],
                "reserved": [
                    "bluetooth",
                    "calendar",
                    "contacts",
                    "debug",
                    "history",
                    "music_files",
                    "music_files_read",
                    "picture_files",
                    "picture_files_read",
                    "video_files",
                    "video_files_read"
                ]
            }
        },
        "16.04": {
            "templates": {
                "common": [
                    "default",
                    "ubuntu-account-plugin",
                    "ubuntu-push-helper",
                    "ubuntu-scope-network",
                    "ubuntu-sdk",
                    "ubuntu-webapp"
                ],
                "reserved": [
                    "unconfined"
                ]
            },
            "policy_groups": {
                "common": [
                    "accounts",
                    "audio",
                    "camera",
                    "connectivity",
                    "content_exchange",
                    "content_exchange_source",
                    "fm_radio",
                    "in-app-purchases",
                    "keep-display-on",
                    "location",
                    "microphone",
                    "networking",
                    "push-notification-client",
                    "sensors",
                    "usermetrics",
                    "video",
                    "webview",
                    "nfc"
                ],
                "reserved": [
                    "bluetooth",
                    "calendar",
                    "contacts",
                    "debug",
                    "history",
                    "music_files",
                    "music_files_read",
                    "picture_files",
                    "picture_files_read",
                    "video_files",
                    "video_files_read"
                ]
            }
        },
        "20.04": {
            "templates": {
                "common": [
                    "default",
                    "ubuntu-account-plugin",
                    "ubuntu-push-helper",
                    "ubuntu-sdk",
                    "ubuntu-webapp"
                ],
                "reserved": [
                    "unconfined"
                ]
            },
            "policy_groups": {
                "common": [
                    "accounts",
                    "audio",
                    "camera",
                    "connectivity",
                    "content_exchange",
                    "content_exchange_source",
                    "fm_radio",
                    "keep-display-on",
                    "location",
                    "microphone",
                    "networking",
                    "push-notification-client",
                    "sensors",
                    "usermetrics",
                    "video",
                    "webview",
                    "nfc"
                ],
                "reserved": [
                    "bluetooth",
                    "calendar",
                    "contacts",
                    "debug",
                    "history",
                    "music_files",
                    "music_files_read",
                    "picture_files",
                    "picture_files_read",
                    "video_files",
                    "video_files_read"
                ]
            }
        },
        "2404.1": {
            "templates": {
                "common": [
                    "default",
                    "ubuntu-account-plugin",
                    "ubuntu-push-helper",
                    "ubuntu-sdk",
                    "ubuntu-webapp"
                ],
                "reserved": [
                    "unconfined"
                ]
            },
            "policy_groups": {
                "common": [
                    "accounts",
                    "audio",
                    "camera",
                    "connectivity",
                    "content_exchange",
                    "content_exchange_source",
                    "fm_radio",
                    "keep-display-on",
                    "location",
                    "microphone",
                    "networking",
                    "push-notification-client",
                    "sensors",
                    "usermetrics",
                    "video",
                    "webview",
                    "nfc"
                ],
                "reserved": [
                    "bluetooth",
                    "calendar",
                    "contacts",
                    "debug",
                    "history",
                    "music_files",
                    "music_files_read",
                    "picture_files",
                    "picture_files_read",
                    "video_files",
                    "video_files_read"
                ]
            }
        },
        "9999.0": {
            "templates": {
                "common": [
                    "default",
                    "ubuntu-account-plugin",
                    "ubuntu-push-helper",
                    "ubuntu-sdk",
                    "ubuntu-webapp"
                ],
                "reserved": [
                    "unconfined"
                ]
            },
            "policy_groups": {
                "common": [
                    "accounts",
                    "audio",
                    "camera",
                    "connectivity",
                    "content_exchange",
                    "content_exchange_source",
                    "fm_radio",
                    "keep-display-on",
                    "location",
                    "microphone",
                    "networking",
                    "push-notification-client",
                    "sensors",
                    "usermetrics",
                    "video",
                    "webview",
                    "nfc"
                ],
                "reserved": [
                    "bluetooth",
                    "calendar",
                    "contacts",
                    "debug",
                    "history",
                    "music_files",
                    "music_files_read",
                    "picture_files",
                    "picture_files_read",
                    "video_files",
                    "video_files_read"
                ]
            }
        }
    },
    "ubuntu-snappy": {
        "1.3": {
            "templates": {
                "common": [
                    "default"
                ],
                "reserved": [
                    "unconfined"
                ]
            },
            "policy_groups": {
                "common": [
                    "networking",
                    "network-service",
                    "network-client"
                ],
                "reserved": []
            }
        }
    },
    "ubuntu-core": {
        "15.04": {
            "templates": {
                "common": [
                    "default"
                ],
                "reserved": [
                    "unconfined"
                ]
            },
            "policy_groups": {
                "common": [
                    "network-client",
                    "network-service",
                    "networking"
                ],
                "reserved": [
                    "bluez_client",
                    "docker_client",
                    "network-admin",
                    "network-firewall",
                    "network-status",
                    "snapd"
                ]
            }
        },
        "15.10": {
            "templates": {
                "common": [
                    "default"
                ],
                "reserved": [
                    "unconfined"
                ]
            },
            "policy_groups": {
                "common": [
                    "network-client",
                    "network-service",
                    "networking"
                ],
                "reserved": [
                    "bluez_client",
                    "docker_client",
                    "network-admin",
                    "network-firewall",
                    "network-status",
                    "snapd"
                ]
            }
        },
        "16.04": {
            "templates": {
                "common": [
                    "default"
                ],
                "reserved": []
            },
            "policy_groups": {
                "common": [
                    "bluetooth-control",
                    "bluez",
                    "bool-file",
                    "browser-support",
                    "camera",
                    "content",
                    "cups-control",
                    "docker",
                    "docker-support",
                    "firewall-control",
                    "fuse-support",
                    "fwupd",
                    "gpio",
                    "gsettings",
                    "hardware-observe",
                    "hidraw",
                    "home",
                    "kernel-module-control",
                    "libvirt",
                    "locale-control",
                    "location-control",
                    "location-observe",
                    "log-observe",
                    "lxd-support",
                    "mir",
                    "modem-manager",
                    "mount-observe",
                    "mpris",
                    "network",
                    "network-bind",
                    "network-control",
                    "network-manager",
                    "network-observe",
                    "network-setup-observe",
                    "opengl",
                    "optical-drive",
                    "ppp",
                    "process-control",
                    "pulseaudio",
                    "removable-media",
                    "screen-inhibit-control",
                    "serial-port",
                    "snapd-control",
                    "system-observe",
                    "system-trace",
                    "time-control",
                    "timeserver-control",
                    "timezone-control",
                    "tpm",
                    "udisks2",
                    "upower-observe",
                    "unity7",
                    "x11"
                ],
                "reserved": []
            }
        }
    }
}
