# Spec file for building a mainline Linux kernel with a custom configuration.
# This file is for a personal or test build and is not a full-featured Fedora kernel spec.
#
# Author: Bhargavjit Bhuyan
#
# Note: This spec file has been simplified to remove non-essential
# build dependencies for a basic test build.

%global mainline_version 6
%global mainline_subversion 16
%global patchlevel 0
%global kernel_version %{mainline_version}.%{mainline_subversion}.%{patchlevel}
%global release_version 1

# Use macros for better portability and consistency
%global _kernel_name kernel-mainline-ath
%global _kernel_release_name %{version}-%{release}

Name:           %{_kernel_name}
Version:        %{kernel_version}
Release:        %{release_version}%{?dist}
Summary:        The Linux kernel (patched)
License:        GPLv2 and others
#Source0:        https://github.com/torvalds/linux/archive/refs/tags/v6.16.tar.gz
Source0: kernel-x86_64-fedora.config

# Minimized list of essential BuildRequires for a core kernel and modules.
BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  python3
BuildRequires:  bc
BuildRequires:  elfutils-libelf-devel
BuildRequires:  ncurses-devel
BuildRequires:  openssl-devel
BuildRequires:  rpm-build
BuildRequires:  bison
BuildRequires:  flex
BuildRequires:  python3-devel
BuildRequires:
