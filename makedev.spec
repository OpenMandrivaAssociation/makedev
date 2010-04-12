# synced with rh-3.3.1-1

%define devrootdir /lib/root-mirror
%define dev_lock /var/lock/subsys/dev
%define makedev_lock /var/lock/subsys/makedev

Summary:	A program used for creating the device files in /dev
Name:		makedev
Version:	4.4
Release:	%mkrel 9
Group:		System/Kernel and hardware
License:	GPL
URL:		http://cvs.mandriva.com/cgi-bin/cvsweb.cgi/soft/makedev/
Source:		%{name}-%{version}.tar.bz2
Requires(pre):	/usr/sbin/groupadd, /usr/sbin/useradd, sed, coreutils, mktemp
Requires:	bash, perl-base
Provides:	dev, MAKEDEV
Obsoletes:	dev, MAKEDEV
BuildArch:	noarch
BuildRoot:	%{_tmppath}/%{name}-%{version}-buildroot
# coreutils => /bin/mkdir

%description
This package contains the makedev program, which makes it easier to create
and maintain the files in the /dev directory.  /dev directory files
correspond to a particular device supported by Linux (serial or printer
ports, scanners, sound cards, tape drives, CD-ROM drives, hard drives,
etc.) and interface with the drivers in the kernel.

The makedev package is a basic part of your Mandriva Linux system and it needs
to be installed.

#The Mandriva Linux operating system uses file system entries to represent
#devices (CD-ROMs, floppy drives, etc.) attached to the machine. All of
#these entries are in the /dev tree (although they don't have to be).
#This package contains the most commonly used /dev entries.

%prep
%setup -q

%build
# Generate the config scripts
%make

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

mkdir -p %{buildroot}%{devrootdir}
%makeinstall_std

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%post
/usr/sbin/useradd -c "virtual console memory owner" -u 69 \
  -s /sbin/nologin -r -d /dev vcsa 2> /dev/null || :

#- when devfs or udev are used, upgrade and install can be done easily :)
if [ -e /dev/.devfsd ] || [ -e /dev/.udev.tdb ] || [ -d /dev/.udevdb/ ]; then
	[ -d %{devrootdir} ] || mkdir %{devrootdir}
	mount --bind / %{devrootdir}
	DEV_DIR=%{devrootdir}/dev
     
     [ -L $DEV_DIR/snd ] && rm -f $DEV_DIR/snd
	mkdir -p $DEV_DIR/{pts,shm}
	/sbin/makedev $DEV_DIR

	# race 
	while [ ! -c $DEV_DIR/null ]; do
		rm -f $DEV_DIR/null
		mknod -m 0666 $DEV_DIR/null c 1 3
		chown root.root $DEV_DIR/null
	done

	umount -f %{devrootdir} 2> /dev/null
#- case when makedev is being installed, not upgraded
else
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


%triggerpostun -- dev

if [ ! -e /dev/.devfsd -a ! -e /dev/.udev.tdb -a ! -d /dev/.udevdb/ ]; then
	#- when upgrading from old dev pkg to makedev pkg, this can't be done in %%post
	#- doing the same when upgrading from new dev pkg
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
%defattr(644,root,root,755)
%doc COPYING devices.txt README
%{_mandir}/*/*
%attr(755,root,root) /sbin/%{name}
%dir %{_sysconfdir}/makedev.d/
%config(noreplace) %{_sysconfdir}/makedev.d/*
%dir /dev
%dir %{devrootdir}


