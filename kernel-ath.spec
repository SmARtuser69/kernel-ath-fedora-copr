# Spec file for building a mainline Linux kernel with all standard Fedora packages.
# This file uses the kernel's default configuration, suitable for personal builds
# or testing where a custom config isn't required.
#
# Author: Bhargavjit Bhuyan
#

%define mainline_version 6
%define mainline_subversion 16
%define kernel_version %{mainline_version}.%{mainline_subversion}
%define patchlevel 0
%define release_version 1

# Use macros for better portability and consistency
%global _kernel_name kernel-mainline-ath
%global _kernel_release_name %{version}-%{release}
%global _kernel_arch_dir arch/%{_arch_dir}
%global _modname %{_kernel_release_name}

Name:           %{_kernel_name}
Version:        %{kernel_version}
Release:        %{release_version}.%{patchlevel}%{?dist}
Summary:        The Linux kernel (mainline)
License:        GPLv2
URL:            https://www.kernel.org/
Source0:        https://cdn.kernel.org/pub/linux/kernel/v%{mainline_version}.x/linux-%{kernel_version}.tar.xz
Source1:        010-ath-patch.patch
Patch0:         %{SOURCE1}

BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  perl
BuildRequires:  python3
BuildRequires:  bc
BuildRequires:  elfutils-libelf-devel
BuildRequires:  ncurses-devel
BuildRequires:  openssl-devel
BuildRequires:  rpm-build
BuildRequires:  bison
BuildRequires:  flex
BuildRequires:  rsync
BuildRequires:  python3-devel
BuildRequires:  openssl-devel
BuildRequires:  grubby
BuildRequires:  kmod
BuildRequires:  xz
BuildRequires:  zlib-devel
BuildRequires:  libcap-devel
BuildRequires:  glibc-devel
BuildRequires:  python3-pyelftools
BuildRequires:  elfutils-devel
BuildRequires:  newt-devel

ExclusiveArch:  x86_64

%description
The Linux kernel, the core of the Linux operating system. This package
contains the mainline kernel, compiled with a default configuration and a custom patch.

# Kernel headers subpackage
%package headers
Summary:        Header files for the Linux kernel
BuildArch:      noarch
Provides:       kernel-headers = %{version}-%{release}
%description headers
This package provides the kernel header files. These header files are used by
glibc to build user-space applications.

# Kernel devel subpackage
%package devel
Summary:        Development files for the Linux kernel
Requires:       kernel-headers = %{version}-%{release}
%description devel
This package provides the development files needed to build external kernel
modules.

# Kernel debug subpackage
%package debug
Summary:        The Linux kernel with debug symbols
Requires:       %{_kernel_name} = %{version}-%{release}
%description debug
This package contains the debug version of the Linux kernel, with extra symbols
and debug information to aid in kernel debugging.

# Kernel debuginfo subpackage
%package debuginfo
Summary:        Debug symbols for the Linux kernel
BuildArch:      noarch
Requires:       %{_kernel_name} = %{version}-%{release}
%description debuginfo
This package provides debug symbols for the Linux kernel and its modules.

# Firmware subpackage
%package firmware
Summary:        Firmware files for the Linux kernel
BuildArch:      noarch
%description firmware
This package contains the firmware binary blobs required by the Linux kernel.

# Documentation subpackage
%package doc
Summary:        Documentation for the Linux kernel
BuildArch:      noarch
%description doc
This package contains the documentation for the Linux kernel.

# Tools subpackage
%package tools
Summary:        Tools for the Linux kernel
%description tools
This package contains user-space tools for interacting with the Linux kernel,
such as perf, cpupower, and turbostat.

# Tools devel subpackage
%package tools-devel
Summary:        Development files for the Linux kernel tools
Requires:       %{_kernel_name}-tools = %{version}-%{release}
%description tools-devel
This package provides the development files (headers, libraries) needed to
build applications that use the kernel tools.

%prep
%setup -q -n linux-%{kernel_version}
%patch0 -p1

%build
# Use the default configuration
make defconfig

# Compile the kernel
NPROCS=$(/usr/bin/getconf _NPROCESSORS_ONLN)
make -j${NPROCS}

# Build kernel tools
make -C tools -j${NPROCS}

%install
rm -rf %{buildroot}
make INSTALL_MOD_PATH=%{buildroot} modules_install
mkdir -p %{buildroot}/boot
cp -v %{_kernel_arch_dir}/boot/bzImage %{buildroot}/boot/vmlinuz-%{_kernel_release_name}
cp -v System.map %{buildroot}/boot/System.map-%{_kernel_release_name}
cp -v .config %{buildroot}/boot/config-%{_kernel_release_name}

# Install kernel headers and devel files
mkdir -p %{buildroot}/usr/src/kernels/%{_modname}
cp -a include %{buildroot}/usr/src/kernels/%{_modname}/
cp -a %{_kernel_arch_dir}/include %{buildroot}/usr/src/kernels/%{_modname}/
cp -a .config %{buildroot}/usr/src/kernels/%{_modname}/
cp -a Module.symvers %{buildroot}/usr/src/kernels/%{_modname}/
cp -a scripts %{buildroot}/usr/src/kernels/%{_modname}/
cp -a vmlinux %{buildroot}/usr/src/kernels/%{_modname}/

# Install firmware
mkdir -p %{buildroot}/lib/firmware
cp -a firmware/* %{buildroot}/lib/firmware/

# Install documentation
mkdir -p %{buildroot}/usr/share/doc/%{_kernel_name}-%{version}
cp -a Documentation/* %{buildroot}/usr/share/doc/%{_kernel_name}-%{version}/

# Install kernel tools and devel
make -C tools INSTALL_MOD_PATH=%{buildroot} DESTDIR=%{buildroot} install

# Generate debug symbols
mkdir -p %{buildroot}/usr/lib/debug/lib/modules/%{_modname}
objcopy --only-keep-debug vmlinux %{buildroot}/usr/lib/debug/lib/modules/%{_modname}/vmlinux.debug
strip -g vmlinux
objcopy --add-gnu-debuglink=%{buildroot}/usr/lib/debug/lib/modules/%{_modname}/vmlinux.debug vmlinux
find %{buildroot}/lib/modules/%{_modname} -name "*.ko" -exec objcopy --only-keep-debug {} {}.debug \;
find %{buildroot}/lib/modules/%{_modname} -name "*.ko" -exec strip -g {} \;

%post
# Use grubby to manage bootloader entries
grubby --add-kernel=/boot/vmlinuz-%{_kernel_release_name} \
       --title="Linux Kernel %{_kernel_release_name}" \
       --copy-default \
       --make-default

%preun
if [ $1 -eq 0 ]; then
   grubby --remove-kernel=/boot/vmlinuz-%{_kernel_release_name}
fi

%files
/boot/vmlinuz-%{_kernel_release_name}
/boot/System.map-%{_kernel_release_name}
/boot/config-%{_kernel_release_name}
/lib/modules/%{_modname}/

%files headers
/usr/src/kernels/%{_modname}/include/
/usr/src/kernels/%{_modname}/arch/x86/include/

%files devel
/usr/src/kernels/%{_modname}/.config
/usr/src/kernels/%{_modname}/Module.symvers
/usr/src/kernels/%{_modname}/scripts/
/usr/src/kernels/%{_modname}/vmlinux

%files debug
# The debug kernel itself
/boot/vmlinuz-%{_kernel_release_name}

%files debuginfo
# Debug symbols for the kernel and modules
/usr/lib/debug/lib/modules/%{_modname}/

%files firmware
/lib/firmware/

%files doc
/usr/share/doc/%{_kernel_name}-%{version}/

%files tools
# List the specific kernel tools to be installed
/usr/bin/perf
/usr/bin/cpupower
/usr/bin/turbostat

%files tools-devel
# List the specific development files for the tools
/usr/include/perf/

%changelog
* Sat Aug 09 2025 Bhargavjit Bhuyan <example@example.com> - 6.16.0-1
- Initial build of mainline kernel 6.16.0 for Fedora COPR.
