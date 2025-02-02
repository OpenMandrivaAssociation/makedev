%define dev_lock /var/lock/subsys/dev
%define makedev_lock /var/lock/subsys/makedev

Summary:	A program used for creating the device files in /dev
Name:		makedev
Version:	4.4
Release:	22
Group:		System/Kernel and hardware
License:	GPLv2
Url:		https://cvs.mandriva.com/cgi-bin/cvsweb.cgi/soft/makedev/
Source0:	%{name}-%{version}.tar.bz2
BuildArch:	noarch
Requires(pre):	coreutils
Requires(pre):	udev
Requires(post):	perl(MDK::Common)
Requires(post):	shadow-utils
Requires(post):	sed
Requires(post):	util-linux
Requires:	bash
# (tpg) this got moved to udev
#Provides:	dev
#Provides:	MAKEDEV
# coreutils => /bin/mkdir

%description
This package contains the makedev program, which makes it easier to create
and maintain the files in the /dev directory.  /dev directory files
correspond to a particular device supported by Linux (serial or printer
ports, scanners, sound cards, tape drives, CD-ROM drives, hard drives,
etc.) and interface with the drivers in the kernel.

The makedev package is a basic part of your Mandriva Linux system and it needs
to be installed.

%prep
%setup -q

%build
%global optflags %{optflags} -Os
%setup_compile_flags

# Generate the config scripts
%make

%install
%makeinstall_std

%post
/usr/sbin/useradd -c "virtual console memory owner" -u 69 \
  -s /sbin/nologin -r -d /dev vcsa 2> /dev/null || :

# If /dev is a devtmpfs, we don't need to do anything
if ! df /dev | grep -q /dev$ || ! mount | grep -q ' /dev type devtmpfs '; then
	DEV_DIR=/dev
	mkdir -p $DEV_DIR/{pts,shm}
     [ -L $DEV_DIR/snd ] && rm -f $DEV_DIR/snd
	/sbin/makedev $DEV_DIR

	# race 
	while [ ! -c $DEV_DIR/null ]; do
		rm -f $DEV_DIR/null
		mknod -m 0666 $DEV_DIR/null c 1 3
		chown root.root $DEV_DIR/null
	done

	[ -x /sbin/pam_console_apply ] && /sbin/pam_console_apply &>/dev/null
fi
:

%files
%doc COPYING devices.txt README
%{_mandir}/*/*
%attr(755,root,root) /sbin/%{name}
%dir %{_sysconfdir}/makedev.d/
%config(noreplace) %{_sysconfdir}/makedev.d/*

