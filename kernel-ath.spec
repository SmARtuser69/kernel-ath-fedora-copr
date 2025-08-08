#
# spec file for a generic Linux kernel package for Fedora
#
# Name:        linux-ath
# Summary:     The Linux kernel (generic build)
#

%global kernver 6.9.9
%global relver 1

Name:          linux-ath
Version:       %{kernver}
Release:       %{relver}.copr.%{?dist}
Summary:       The Linux kernel (generic config build)
License:       GPL-2.0-only
URL:           https://www.kernel.org/
Source0:       https://git.kernel.org/pub/scm/linux/kernel/git/ath/ath.git/snapshot/ath-next.tar.gz

# We are using the default kernel config provided by the source.
# You can generate this with 'make defconfig' for your architecture.
# We no longer need to provide a separate config file.

# This kernel is only configured for x86_64
ExclusiveArch: x86_64

# We don't want debug packages for the kernel, they are massive and not
# useful for most users.
%global debug_package %{nil}

# Build dependencies required to compile the kernel and run the install scripts.
# These should be readily available in the standard Fedora COPR build roots.
BuildRequires: gcc
BuildRequires: make
BuildRequires: bison
BuildRequires: flex
BuildRequires: openssl-devel
BuildRequires: elfutils-libelf-devel
BuildRequires: bc
BuildRequires: ncurses-devel
BuildRequires: rpm-build
BuildRequires: perl
BuildRequires: python3
BuildRequires: rsync
BuildRequires: kernel-install-core
BuildRequires: fedora-packager

%description
The Linux kernel, the core of the operating system. This package contains a (generic) build of the Linux kernel + ath driver patches, without Fedora-specific patches.
It is intended for testing and development purposes.

%prep
# Unpack the kernel source code tarball. The -q option makes it quiet.
%setup -q -n ath-next

%build
# The kernel build process is driven by 'make'.
#
# 'make defconfig' generates a default configuration file for the architecture.
# The ath-next repository will have a default config in arch/x86/configs.
make defconfig

# 'make olddefconfig' updates the .config file to be compatible with this
# exact kernel version, answering any new questions with their default values.
# This ensures the build doesn't stop to ask interactive questions.
make olddefconfig

# Set a custom version string. This will be visible in 'uname -r'.
# For example: 6.9.9-1.copr.fc42.x86_64
# We get the base version from the Makefile and append our release info.
KV_EXTRA="-%{release}.%{_arch}"
sed -i "s/^EXTRAVERSION =.*/EXTRAVERSION = ${KV_EXTRA}/" Makefile

# Compile the kernel.
# We use %{_smp_mflags} which is a standard RPM macro that expands to -j<number_of_cores>
# to parallelize the build and make it much faster.
make %{?_smp_mflags}

%install
# This section installs the compiled kernel and modules into a temporary
# directory (%{buildroot}) from which the final RPM package will be created.

# Install kernel modules
# INSTALL_MOD_PATH points to our buildroot.
make INSTALL_MOD_PATH=%{buildroot} modules_install

# Create the /boot directory in the buildroot
install -d %{buildroot}/boot

# Install the compressed kernel image (vmlinuz)
# The final name will be something like: vmlinuz-6.9.9-1.copr.fc42.x86_64
install -m 644 arch/x86/boot/bzImage %{buildroot}/boot/vmlinuz-%{version}%{?KV_EXTRA}

# Install the System.map file (used for debugging kernel panics)
install -m 644 System.map %{buildroot}/boot/System.map-%{version}%{?KV_EXTRA}

# Install the .config file used for the build, for reference and building external modules
install -m 644 .config %{buildroot}/boot/config-%{version}%{?KV_EXTRA}

%files
# This section lists all the files that will be included in the final RPM package.
# Using the macros helps ensure the paths are correct.
/boot/vmlinuz-%{version}%{?KV_EXTRA}
/boot/System.map-%{version}%{?KV_EXTRA}
/boot/config-%{version}%{?KV_EXTRA}
/lib/modules/%{version}%{?KV_EXTRA}/

%post
# This scriptlet runs *after* the package is installed on the user's system.
# It uses the 'kernel-install' command to do all the heavy lifting:
# 1. Generates an initramfs using dracut.
# 2. Adds a new entry to the bootloader configuration (GRUB2).
echo "Running kernel-install script for %{version}%{?KV_EXTRA}..."
/usr/bin/kernel-install add %{version}%{?KV_EXTRA} /boot/vmlinuz-%{version}%{?KV_EXTRA}

%postun
# This scriptlet runs *after* the package is uninstalled.
# It cleans up by removing the initramfs and bootloader entry for the kernel
# being removed.
if [ $1 -eq 0 ] ; then
    echo "Running kernel-install remove for %{version}%{?KV_EXTRA}..."
    /usr/bin/kernel-install remove %{version}%{?KV_EXTRA}
fi

%changelog
* Fri Aug 08 2025 Your Name <your@email.com> - 6.9.9-1.copr
- Initial generic kernel spec for Fedora COPR.
