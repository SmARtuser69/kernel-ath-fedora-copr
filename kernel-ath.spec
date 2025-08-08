%define kernel_version 6.16.0
%define custom_repo_url https://example.com/linux-%{kernel_version}.tar.xz

Name:           kernel-ath
Version:        6.16.0
Release:        1.fc42%{?dist}
Summary:        The Linux Kernel %{kernel_version}

License:        GPLv2
URL:            https://www.kernel.org/
Source0:        https://git.kernel.org/pub/scm/linux/kernel/git/ath/ath.git

BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  perl
BuildRequires:  bc
BuildRequires:  elfutils-libelf-devel
BuildRequires:  openssl-devel
BuildRequires:  rpm-build
BuildRequires:  bison
BuildRequires:  flex
BuildRequires:  rsync

ExclusiveArch:  x86_64

Provides:       kernel = %{version}-%{release}
Provides:       kernel-x86_64 = %{version}-%{release}

%description
The Linux kernel, the core of the GNU/Linux operating system. This is a
custom build of version %{kernel_version}.

%prep
%setup -q -n linux-%{kernel_version}
git clone --depth=1 --branch ath-next https://git.kernel.org/pub/scm/linux/kernel/git/ath/ath.git linux-ath-next
cd linux-ath-next

%build
# Generate the default configuration for x86_64
make defconfig

# Build the kernel
make -j$(nproc)

%install
rm -rf %{buildroot}
make install INSTALL_PATH=%{buildroot}/boot

# Install kernel modules
make modules_install INSTALL_MOD_PATH=%{buildroot}

# Remove unnecessary files
rm -f %{buildroot}/boot/System.map-%{version}

%files
/boot/vmlinuz-%{version}
/boot/initramfs-%{version}.img
/lib/modules/%{version}/

%changelog
* Fri Aug 08 2025 Bhargavjit Bhuyan <bhargavjitbhuyan123@gmail.com> - 6.16.0-1
- Initial build of kernel 6.16.0 for Fedora 42.
