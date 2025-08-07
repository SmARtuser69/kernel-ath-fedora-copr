#
# This is a spec file for building a custom Linux kernel from the ath.git tree.
# It is simplified for a single architecture (x86_64) and a single flavor.
# For a production-grade kernel, it's highly recommended to start from the
# official Fedora kernel spec file and adapt it.
#

# --- Git Source Configuration ---
# Define the git commit hash you want to build.
# Using a specific commit ensures a reproducible build.
# Replace 'master' or use a specific commit hash from the ath-next branch for a more recent version.
%global githash master

# --- Preamble ---
# The Name must be unique to avoid conflicts with the official Fedora kernel.
Name:           kernel-ath
# The Version should match the base version in the kernel's Makefile.
# You may need to inspect the Makefile in the git repo to get the correct version.
# Example: If Makefile has VERSION = 6, PATCHLEVEL = 9, SUBLEVEL = 0, then Version is 6.9.0
Version:        6.16.0
# The Release string makes this RPM unique. It includes the git hash and Fedora version.
Release:        1.ath%{githash}.fc42
Summary:        The Linux kernel from the ath.git development tree.
License:        GPL-2.0-only
URL:            https://git.kernel.org/pub/scm/linux/kernel/git/ath/ath.git/
ExclusiveArch:  x86_64

# The Source0 URL points to a snapshot tarball of the specified git commit.
# This is generally more reliable for builders like COPR than cloning the repo directly.
Source0:        https://git.kernel.org/pub/scm/linux/kernel/git/ath/ath.git
# Source1 is the kernel configuration file. You MUST provide this file.
# You can get a good starting config from the official Fedora kernel source RPM:
# 1. dnf download --source kernel
# 2. rpm2cpio kernel-<version>.src.rpm | cpio -iv ./kernel-x86_64.config
# 3. Rename the extracted file and place it in the same directory as this spec file.
Source1:        kernel-x86_64-fedora.config

# --- Build Dependencies ---
# These are the packages required to build the kernel. This list is based on
# the standard Fedora kernel dependencies and should be sufficient for COPR.
BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  bison
BuildRequires:  flex
BuildRequires:  elfutils-libelf-devel
BuildRequires:  openssl-devel
BuildRequires:  rpm-build
BuildRequires:  perl
BuildRequires:  python3
BuildRequires:  bc
BuildRequires:  kmod
BuildRequires:  rsync
BuildRequires:  zstd

# The main package does not require anything special, as the system tools
# (like grubby, dracut) will handle the kernel installation.

%description
This package provides the Linux kernel and modules built from the wireless
development tree (ath.git) maintained by Kalle Valo.

This build is intended for testing and development purposes.

%prep
# The %setup macro unpacks the source tarball (Source0).
# The -n option specifies the directory name inside the tarball.
# The snapshot service creates a directory based on the project name and commit hash.
%setup -q -n %{name}-%{version}-ath-%{githash}

%build
# 1. Copy the pre-prepared kernel config file into the source tree as .config.
cp %{SOURCE1} ./.config

# 2. Run 'make olddefconfig' to update the .config file with any new options
#    available in this kernel source version, using the default values.
make olddefconfig

# 3. Build the kernel.
#    - LOCALVERSION is a critical parameter. It appends our unique release string
#      to the kernel version, resulting in a version like '6.10.0-1.ath...'.
#      This ensures our kernel's modules are installed in a unique directory
#      and do not conflict with the stock Fedora kernel.
#    - %{?_smp_mflags} is a standard RPM macro to enable parallel builds (e.g., make -j16).
make %{?_smp_mflags} LOCALVERSION=-%{release} bzImage modules

%install
# The %install section places the compiled files into the build root,
# which is a temporary directory structure that mirrors the final filesystem.

# 1. Install the kernel modules.
#    - INSTALL_MOD_PATH points to the build root.
#    - The LOCALVERSION must match the one used during the %build stage.
make INSTALL_MOD_PATH=%{buildroot} LOCALVERSION=-%{release} modules_install

# 2. Create the /boot directory in the build root.
mkdir -p %{buildroot}/boot

# 3. Copy the kernel image (bzImage) to the /boot directory, renaming it
#    to the standard vmlinuz-<version>-<release> format.
cp arch/x86/boot/bzImage %{buildroot}/boot/vmlinuz-%{version}-%{release}.%{_arch}

# 4. Copy the System.map and the final .config file to /boot for debugging
#    and reference purposes.
cp System.map %{buildroot}/boot/System.map-%{version}-%{release}.%{_arch}
cp .config %{buildroot}/boot/config-%{version}-%{release}.%{_arch}

# 5. (Optional but Recommended) Remove debugging info from modules to reduce size.
find %{buildroot} -type f -name '*.ko' | xargs strip --strip-debug

%files
# This section lists all the files that will be included in the final RPM package.
# Using the full version-release string ensures the file paths are correct.
/boot/vmlinuz-%{version}-%{release}.%{_arch}
/boot/System.map-%{version}-%{release}.%{_arch}
/boot/config-%{version}-%{release}.%{_arch}
/lib/modules/%{version}-%{release}.%{_arch}/

%changelog
* Thu Aug 07 2025 Your Name <you@example.com> - 6.10.0-1
- Initial build from ath.git tree for Fedora 42.
