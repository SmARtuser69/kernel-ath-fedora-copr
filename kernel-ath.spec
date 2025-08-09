# This is a spec file for building a custom Linux kernel with a specific patch
# for ath10k WiFi driver testing. It has been corrected for COPR builds.
#
# Author: Gemini
# Date: 2025-08-09
#
# To build this locally:
# 1. Save this file as kernel-custom-ath10k.spec
# 2. Install build tools: sudo dnf install rpm-build rpmdevtools
# 3. Run: rpmbuild -ba kernel-custom-ath10k.spec
#
# For COPR, you just need to upload this spec file.

# --- FIX: Disable the generation of debug packages ---
# This prevents the "Empty %files file" error which is fatal in COPR.
%define debug_package %{nil}

# --- Preamble: Metadata and Corrected Versioning ---

%define full_commit 19272b37aa4f83ca52bdf9c16d5d81bdd1354494
%define short_commit 19272b37aa4f

# --- KERNEL VERSIONING ---
# Define all version components separately for clarity and correctness.

# The base version number. RPM 'Version' tag cannot contain hyphens.
%define kernel_base_ver 6.16.0
# The extra version from the kernel's Makefile for this specific commit.
%define kernel_extra_ver rc1
# Our custom identifier for the patch/build.
%define custom_id aspm_fix_1
# This is the string that will be passed to the kernel build as LOCALVERSION.
# The leading '-' is required by the kernel's build system.
%define kernel_localversion -%{custom_id}.g%{short_commit}

# This macro defines the *final, predictable kernel release string* that will be generated.
# It combines the base version, extra version, and our local version.
# This is the single source of truth for all paths and scripts.
# Example: 6.16.0-rc1-aspm_fix_1.g19272b37aa4f
%define full_kernel_string %{kernel_base_ver}-%{kernel_extra_ver}%{kernel_localversion}

Name:           kernel-ath
Version:        %{kernel_base_ver}
# The Release tag is structured to be sortable and informative, reflecting the build details.
Release:        0.%{kernel_extra_ver}.%{custom_id}.g%{short_commit}%{?dist}
Summary:        Custom Linux kernel with Qualcomm Atheros ASPM patch
License:        GPL-2.0-only
URL:            https://github.com/torvalds/linux/
Source0:        https://github.com/torvalds/linux/archive/%{full_commit}.tar.gz

# --- Build Dependencies ---
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
BuildRequires: rust-packaging
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
This package provides a custom-built Linux kernel based on git commit %{short_commit}.
It includes a patch to fix Active State Power Management (ASPM) issues with some
Qualcomm Atheros (ath10k/ath11k) wireless devices.

This build is intended for testing purposes only. The final kernel release string is %{full_kernel_string}.

# --- %prep: Prepare the source code ---
%prep
%setup -q -n linux-%{full_commit}

echo "--- Initializing git repo for patch application ---"
git init -b main
git add .
git config user.email "mockbuild@localhost"
git config user.name "Mock Build"
git commit -m "Initial commit of Linux source from tarball"

echo "--- Fetching patch with b4 ---"
b4 am 20250716-ath-aspm-fix-v1-0-dd3e62c1b692@oss.qualcomm.com

echo "--- Applying ASPM patch ---"
# Apply the patch from the downloaded mailbox file. Using a wildcard is fine as b4 creates a unique name.
git am -3 *.mbx


# --- %build: Compile the kernel ---
%build
echo "--- Configuring the kernel ---"

make defconfig

# Disable automatic version suffixing to control the final version string.
echo "Disabling CONFIG_LOCALVERSION_AUTO to control the final version string."
scripts/config --disable LOCALVERSION_AUTO

# Run 'make olddefconfig' again to ensure the configuration is consistent.
make olddefconfig

echo "--- Building kernel and modules with LOCALVERSION='%{kernel_localversion}' ---"
# We pass our custom localversion to the make command.
make %{?_smp_mflags} LOCALVERSION=%{kernel_localversion} bzImage modules

# --- %install: Install the compiled files ---
%install
echo "--- Installing kernel and modules to buildroot ---"
make INSTALL_MOD_PATH=%{buildroot} LOCALVERSION=%{kernel_localversion} modules_install

# --- FIX:
