class Brios < Formula
  include Language::Python::Virtualenv

  desc "Bluetooth Reactive Intelligent Operator for Croissant Safety"
  homepage "https://github.com/Piero24/B.R.I.O.S."
  url "https://github.com/Piero24/B.R.I.O.S./archive/refs/tags/v1.0.0.tar.gz"
  sha256 "d98733798e8d280ce5bda0ef18060ac31b563a4812cba32fc7fcf48fb637c469"
  license "MIT"

  depends_on "python@3.12"

  resource "bleak" do
    url "https://files.pythonhosted.org/packages/6a/c0/3aca655fa43b8ff5340d99fac4e67061f53f42f092fc847bdd0559d67846/bleak-0.21.1.tar.gz"
    sha256 "ec4a1a2772fb315b992cbaa1153070c7e26968a52b0e2727035f443a1af5c18f"
  end

  resource "pyobjc-core" do
    url "https://files.pythonhosted.org/packages/b8/b6/d5612eb40be4fd5ef88c259339e6313f46ba67577a95d86c3470b951fce0/pyobjc_core-12.1.tar.gz"
    sha256 "2bb3903f5387f72422145e1466b3ac3f7f0ef2e9960afa9bcd8961c5cbf8bd21"
  end

  resource "pyobjc-framework-Cocoa" do
    url "https://files.pythonhosted.org/packages/02/a3/16ca9a15e77c061a9250afbae2eae26f2e1579eb8ca9462ae2d2c71e1169/pyobjc_framework_cocoa-12.1.tar.gz"
    sha256 "5556c87db95711b985d5efdaaf01c917ddd41d148b1e52a0c66b1a2e2c5c1640"
  end

  resource "pyobjc-framework-CoreBluetooth" do
    url "https://files.pythonhosted.org/packages/4b/25/d21d6cb3fd249c2c2aa96ee54279f40876a0c93e7161b3304bf21cbd0bfe/pyobjc_framework_corebluetooth-12.1.tar.gz"
    sha256 "8060c1466d90bbb9100741a1091bb79975d9ba43911c9841599879fc45c2bbe0"
  end

  resource "pyobjc-framework-libdispatch" do
    url "https://files.pythonhosted.org/packages/26/e8/75b6b9b3c88b37723c237e5a7600384ea2d84874548671139db02e76652b/pyobjc_framework_libdispatch-12.1.tar.gz"
    sha256 "4035535b4fae1b5e976f3e0e38b6e3442ffea1b8aa178d0ca89faa9b8ecdea41"
  end

  resource "python-dotenv" do
    url "https://files.pythonhosted.org/packages/31/06/1ef763af20d0572c032fa22882cfbfb005fba6e7300715a37840858c919e/python-dotenv-1.0.0.tar.gz"
    sha256 "a8df96034aae6d2d50a4ebe8216326c61c3eb64836776504fcca410e5937a3ba"
  end

  def install
    virtualenv_install_with_resources
    pkgshare.install ".env.example"
  end

  service do
    run [opt_bin/"brios"]
    keep_alive true
    log_path var/"log/brios.log"
    error_log_path var/"log/brios.log"
    working_dir var
    environment_variables PATH: std_service_path_env
  end

  test do
    system bin/"brios", "--version"
  end
end
