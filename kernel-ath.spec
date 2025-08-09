# This is a spec file for building a custom Linux kernel with a specific patch
# for ath10k WiFi driver testing. It has been corrected for COPR builds.
#
# Author: Gemini
# Date: 2025-08-09

# Disable the generation of debug packages.
%define debug_package %{nil}

# --- Preamble: Metadata and Versioning ---

%define full_commit 19272b37aa4f83ca52bdf9c16d5d81bdd1354494
%define short_commit 19272b37aa4f

# --- KERNEL VERSIONING ---
%define kernel_base_ver 6.16.0
%define kernel_extra_ver rc1
%define custom_id aspm_fix_1
%define kernel_localversion -%{custom_id}.g%{short_commit}
%define full_kernel_string %{kernel_base_ver}-%{kernel_extra_ver}%{kernel_localversion}

Name:           kernel-ath
Version:        %{kernel_base_ver}
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
git am -3 *.mbx


# --- %build: Compile the kernel ---
%build
echo "--- Configuring the kernel ---"
make defconfig

echo "Disabling CONFIG_LOCALVERSION_AUTO to control the final version string."
scripts/config --disable LOCALVERSION_AUTO
make olddefconfig

echo "--- Building kernel and modules with LOCALVERSION='%{kernel_localversion}' ---"
make %{?_smp_mflags} LOCALVERSION=%{kernel_localversion} bzImage modules

# --- %install: Install the compiled files ---
%install
echo "--- Installing kernel and modules to buildroot ---"
make INSTALL_MOD_PATH=%{buildroot} LOCALVERSION=%{kernel_localversion} modules_install

# Note: Removed the 'rm' commands for the symlinks as we will handle them in %files.

install -d %{buildroot}/boot
install -m 644 arch/x86/boot/bzImage %{buildroot}/boot/vmlinuz-%{full_kernel_string}
install -m 644 System.map %{buildroot}/boot/System.map-%{full_kernel_string}
install -m 644 .config %{buildroot}/boot/config-%{full_kernel_string}

# --- %post: Post-installation script ---
%post
echo "--- Running kernel-install to add the new kernel ---"
/sbin/kernel-install add %{full_kernel_string} /boot/vmlinuz-%{full_kernel_string}

# --- %postun: Post-uninstallation script ---
%postun
echo "--- Running kernel-install to remove the old kernel ---"
/sbin/kernel-install remove %{full_kernel_string}

# --- %files: List of files to be included in the RPM ---
%files
/boot/vmlinuz-%{full_kernel_string}
/boot/System.map-%{full_kernel_string}
/boot/config-%{full_kernel_string}

# --- FIX: Explicitly package the module directory contents ---
# This is a more robust method than a simple directory wildcard.
# 1. Claim the directory itself.
%dir /lib/modules/%{full_kernel_string}
# 2. Claim the 'kernel' subdirectory, which contains all the .ko modules.
/lib/modules/%{full_kernel_string}/kernel/
# 3. Claim all the module metadata files (modules.alias, modules.dep, etc.).
/lib/modules/%{full_kernel_string}/modules.*
# 4. Exclude the problematic symlinks. This prevents both the "unpackaged file"
#    error and the "absolute symlink" warning.
%exclude /lib/modules/%{full_kernel_string}/build
%exclude /lib/modules/%{full_kernel_string}/source


# --- %changelog: Record of changes to the spec file ---
%changelog
* Sun Aug 10 2025 Gemini <gemini@google.com> - 6.16.0-0.rc1.aspm_fix_1.g19272b37aa4f
- Fixed "Installed (but unpackaged) file(s) found" error.
- Rewrote %files section to be more explicit about module files.
- Used %exclude to ignore the problematic build/source symlinks.
* Sat Aug 10 2025 Gemini <gemini@google.com> - 6.16.0-0.rc1.aspm_fix_1.g19272b37aa4f
- Disabled debug package generation to fix "Empty %files" error.
- Removed absolute 'build' and 'source' symlinks in %install to fix warnings.
* Sat Aug 09 2025 Gemini <gemini@google.com> - 6.16.0-0.rc1.aspm_fix_1.g19272b37aa4f
- Corrected kernel versioning logic to prevent "Directory not found" error.
- Introduced a %full_kernel_string macro to ensure consistency.
- Added 'scripts/config --disable LOCALVERSION_AUTO' to make version predictable.
* Fri Aug 09 2024 Gemini <gemini@google.com> - 6.16.0-aspm_fix_1.19272b37aa4f
- Fixed "No such file or directory" error in %prep.
- Replaced host config copy with 'make defconfig'.
* Fri Aug 09 2024 Gemini <gemini@google.com> - 6.10.0-rc2.aspm_fix_1.19272b37
- Initial build with ASPM patch for ath10k/ath11k testing.






