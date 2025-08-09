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

# The git commit hash is used to create a unique version string.
%define short_commit 19272b37aa4f83ca52bdf9c16d5d81bdd1354494
%define kernel_version 6.16.0
%define custom_release aspm_fix_1
Name:          kernel-ath
Version:       %{kernel_version}
Release:       %{custom_release}.%{short_commit}%{?dist}
Summary:       Custom Linux kernel with Qualcomm Atheros ASPM patch
License:       GPL-2.0-only
URL:           https://github.com/torvalds/linux/
Source0:       https://github.com/torvalds/linux/archive/%{short_commit}.tar.gz

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
It is built from the mainline git repository at commit %{short_commit} and includes
a patch to fix Active State Power Management (ASPM) issues with some
Qualcomm Atheros (ath10k/ath11k) wireless devices.

This build is intended for testing purposes only.

# --- %prep: Prepare the source code ---
# This section handles unpacking the source, checking out the right commit,
# and applying the necessary patch using the user's exact steps.
%prep
# The standard RPM macro to unpack the source tarball.
# This automatically changes the current directory to the source tree.
%setup -q -n linux-%{short_commit}

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
make %{?_smp_mflags} bzImage modules

# --- %install: Install the compiled files ---
# This section copies the built kernel and modules into a temporary
# directory (%{buildroot}) from which the RPM package will be created.
%install
echo "--- Installing kernel and modules to buildroot ---"
