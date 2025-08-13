#Spec file for building a mainline Linux kernel with a custom configuration.
#This file is for a personal or test build and is not a full-featured Fedora kernel spec.
#Author: Bhargavjit Bhuyan
#This spec has been corrected to use a more complete set of build dependencies
#and to fix a potential issue with unpacking the source tarball.
%global mainline_version 6
%global mainline_subversion 16
%global patchlevel 0
%global kernel_version %{mainline_version}.%{mainline_subversion}.%{patchlevel}
%global release_version 1

#Use macros for better portability and consistency
%global _kernel_name kernel-mainline-ath
%global _kernel_release_name %{kernel_version}-%{release_version}

Name: %{_kernel_name}
Version: %{kernel_version}
Release: %{release_version}%{?dist}
Summary: The Linux kernel (patched)
License: GPLv2 and others
Source0: https://git.kernel.org/pub/scm/linux/kernel/git/ath/ath.git/snapshot/ath.git-ath-next.tar.gz
Source1: kernel-x86_64-fedora.config

#Your patch fix1.patch is already included in the aspm patchset and is not needed.
#Patch0: fix1.patch
#A more complete list of essential BuildRequires for a core kernel and modules.
#T#he original list was missing several key packages.
BuildRequires: gcc
BuildRequires: make
BuildRequires: python3
BuildRequires: bc
BuildRequires: elfutils-libelf-devel
BuildRequires: ncurses-devel
BuildRequires: openssl-devel
BuildRequires: rpm-build
BuildRequires: bison
BuildRequires: flex
BuildRequires: libmnl-devel
BuildRequires: libcap-devel
BuildRequires: perl
BuildRequires: perl-devel
BuildRequires: perl-generators
BuildRequires: perl-Pod-Html
BuildRequires: pesign
BuildRequires: xmlto
BuildRequires: asciidoc
BuildRequires: libatomic
BuildRequires: pahole
BuildRequires: xz-devel

%description
This is a custom build of the Linux kernel from the 'ath' git tree, specifically
the 'ath-next' branch, intended for testing wireless drivers.

%prep

The Source0 tarball is named 'ath.git-ath-next.tar.gz' and unpacks to a directory
with a similar name. Using '%setup -q' without the '-n' flag is more robust
as it handles the directory name automatically.
%setup -q
cp %{SOURCE1} .config

%build

Use a standard build process for the kernel.
make %{?_smp_mflags}
make olddefconfig
make %{?_smp_mflags}

%install

Install the kernel and modules into the build root.
make INSTALL_MOD_PATH=%{buildroot} modules_install
make INSTALL_HDR_PATH=%{buildroot}/usr headers_install
make INSTALL_PATH=%{buildroot}/boot install

The following lines are used to clean up the build.
%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
/boot/vmlinuz-%{_kernel_release_name}
/boot/System.map-%{_kernel_release_name}
/boot/config-%{_kernel_release_name}
/boot/initramfs-%{_kernel_release_name}.img
/lib/modules/%{_kernel_release_name}/

%files headers
%defattr(-,root,root,-)
/usr/include/

%files devel
%defattr(-,root,root,-)
/usr/src/kernels/%{_kernel_release_name}/include/
/usr/src/kernels/%{_kernel_release_name}/scripts/
/usr/src/kernels/%{_kernel_release_name}/Module.symvers
/usr/src/kernels/%{_kernel_release_name}/.config
/usr/src/kernels/%{_kernel_release_name}/Makefile

%if 0%{?with_firmware}
%files firmware
%defattr(-,root,root,-)
/lib/firmware/
%endif

%autochangelog

#Tue Aug 12 2025 Bhargavjit Bhuyan example@example.com - 6.16.0-1

#Changed Source0 to the direct snapshot link for the ath-next branch.

#Updated BuildRequires to a more comprehensive list for a successful build.

#Fixed the '%prep' section to handle the source tarball directory correctly.
