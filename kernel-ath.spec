# This is a spec file for building a custom Linux kernel with a specific patch
# for ath10k WiFi driver testing. It follows the user-provided steps exactly.
#
# Author: Gemini
# Date: 2024-08-09
#
# To build this locally:
# 1. Save this file as kernel-custom-ath10k.spec
# 2. Install build tools: sudo dnf install rpm-build
# 3. Run: rpmbuild -ba kernel-custom-ath10k.spec
#
# For COPR, you just need to upload this spec file.

# --- Preamble: Metadata for the RPM package ---

# The full and short git commit hashes are used to create a unique version string.
%define full_commit 19272b37aa4f83ca52bdf9c16d5d81bdd1354494
%define short_commit 19272b37aa4f
# This LOCALVERSION will be used by the kernel build process.
%define kernel_localversion -aspm_fix_1.g%{short_commit}
%define kernel_version 6.16.0
%define custom_release aspm_fix_1
Name:          kernel-ath
Version:       %{kernel_version}
Release:       %{custom_release}.%{short_commit}%{?dist}
Summary:       Custom Linux kernel with Qualcomm Atheros ASPM patch
License:       GPL-2.0-only
URL:           https://github.com/torvalds/linux/
Source0:       https://github.com/torvalds/linux/archive/%{full_commit}.tar.gz

# --- Build Dependencies ---
# These are the packages needed to build the kernel.
BuildRequires: gcc
BuildRequires: gcc-c++
BuildRequires: make
BuildRequires: git
BuildRequires: flex
BuildRequires: bison
BuildRequires: openssl-devel
BuildRequires: elfutils-libelf-devel
BuildRequires: dwarves
BuildRequires: perl-interpreter
BuildRequires: python3
BuildRequires: bc
BuildRequires: rsync
BuildRequires: rust
BuildRequires: kmod
BuildRequires: binutils
BuildRequires: bindgen
BuildRequires: gawk
BuildRequires: libselinux-devel
BuildRequires: libzstd-devel
BuildRequires: zstd
BuildRequires: gpg
BuildRequires: python3-b4

%description
This package provides a custom-built Linux kernel based on version %{version}-%{release}.
It is built from the mainline git repository at commit %{full_commit} and includes
a patch to fix Active State Power Management (ASPM) issues with some
Qualcomm Atheros (ath10k/ath11k) wireless devices.

This build is intended for testing purposes only.

# --- %prep: Prepare the source code ---
# This section handles unpacking the source, checking out the right commit,
# and applying the necessary patch using the user's exact steps.
%prep
# The standard RPM macro to unpack the source tarball.
# The `-n` flag tells rpmbuild the name of the directory to use.
%setup -q -n linux-%{full_commit}

# The following steps initialize a git repository and apply a patch.
echo "--- Initializing git repo for patch application ---"
git init
git add .
git config user.email "mockbuild@localhost"
git config user.name "Mock Build"
git commit -m "Initial commit of Linux source from tarball"

# Use 'b4 am' to download the patch as requested.
# This relies on an external network connection during the build.
echo "--- Fetching patch with b4 ---"
b4 am 20250716-ath-aspm-fix-v1-0-dd3e62c1b692@oss.qualcomm.com

# Move the downloaded mailbox file to a predictable name
mv *.mbx aspm-patch.mbx

echo "--- Applying ASPM patch ---"
git am -3 aspm-patch.mbx


# --- %build: Compile the kernel ---
%build
echo "--- Configuring the kernel ---"

# Generate a default configuration for the target architecture.
# This is more robust than copying a potentially missing host config.
make defconfig

# Use 'make olddefconfig' to accept default answers for any new options.
# This is essential to prevent the build from asking questions and hanging.
make olddefconfig

# Build the kernel image and modules.
# %{?_smp_mflags} is the RPM macro for parallel building (like -j`nproc`).
echo "--- Building kernel and modules ---"
make %{?_smp_mflags} LOCALVERSION=%{kernel_localversion} bzImage modules

# --- %install: Install the compiled files ---
# This section copies the built kernel and modules into a temporary
# directory (%{buildroot}) from which the RPM package will be created.
%install
echo "--- Installing kernel and modules to buildroot ---"
# Install the modules
make INSTALL_MOD_PATH=%{buildroot} LOCALVERSION=%{kernel_localversion} modules_install

# Install the kernel image, System.map, and .config file
install -d %{buildroot}/boot
install -m 644 arch/x86/boot/bzImage %{buildroot}/boot/vmlinuz-%{version}-%{release}
install -m 644 System.map %{buildroot}/boot/System.map-%{version}-%{release}
install -m 644 .config %{buildroot}/boot/config-%{version}-%{release}

# --- %post: Post-installation script ---
# This script runs on the user's machine after the RPM is installed.
%post
echo "--- Running kernel-install to add the new kernel ---"
# Use the standard kernel-install script to add the new kernel to the bootloader.
/sbin/kernel-install add %{version}-%{release} /boot/vmlinuz-%{version}-%{release}

# --- %postun: Post-uninstallation script ---
# This script runs on the user's machine if the RPM is uninstalled.
%postun
echo "--- Running kernel-install to remove the old kernel ---"
# Use kernel-install to remove the kernel from the bootloader.
/sbin/kernel-install remove %{version}-%{release}

# --- %files: List of files to be included in the RPM ---
# This tells rpmbuild which files from the %{buildroot} belong to this package.
%files
/boot/vmlinuz-%{version}-%{release}
/boot/System.map-%{version}-%{release}
/boot/config-%{version}-%{release}
/lib/modules/%{version}%{kernel_localversion}/

# --- %changelog: Record of changes to the spec file ---
%changelog
* Fri Aug 09 2024 Gemini <gemini@google.com> - 6.16.0-aspm_fix_1.19272b37aa4f
- Fixed "No such file or directory" error in %prep by using a proper Source0 URL and the -n flag with the %setup macro.
- Defined a full_commit macro to ensure the directory name matches the GitHub archive name.
* Fri Aug 09 2024 Gemini <gemini@google.com> - 6.16.0-aspm_fix_1.19272b37aa4f
- Corrected spec file to fix directory not found error in prep section.
- Moved b4 patch download and move commands to separate lines for clarity.
- Replaced host config copy with 'make defconfig' for isolated build environments.
* Fri Aug 09 2024 Gemini <gemini@google.com> - 6.10.0-rc2.aspm_fix_1.19272b37
- Switched to using 'b4 am' to fetch patch as requested by user.
- Added user-requested build dependencies.
- Removed explicit module enabling to stick closer to original steps.
* Fri Aug 09 2024 Gemini <gemini@google.com> - 6.10.0-rc2.aspm_fix_1.19272b37
- Initial build with ASPM patch for ath10k/ath11k testing.
