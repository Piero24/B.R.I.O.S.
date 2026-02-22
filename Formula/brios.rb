class Brios < Formula
  include Language::Python::Virtualenv

  desc "Bluetooth Reactive Intelligent Operator for Croissant Safety"
  homepage "https://github.com/Piero24/B.R.I.O.S"
  url "https://github.com/Piero24/B.R.I.O.S/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "c3bf3c30b78faf59bca1419e39ded080676d3416e1c4d9ab3c1a7a3f6cef9bca"
  license "MIT"

  depends_on "python@3.12"
  depends_on "rust" if OS.mac? # Bleak might need it for building on some platforms if wheels aren't used, but python@3.12 handles wheels.

  resource "bleak" do
    url "https://files.pythonhosted.org/packages/6a/c0/3aca655fa43b8ff5340d99fac4e67061f53f42f092fc847bdd0559d67846/bleak-0.21.1.tar.gz"
    sha256 "ec4a1a2772fb315b992cbaa1153070c7e26968a52b0e2727035f443a1af5c18f"
  end

  resource "pyobjc-core" do
    url "https://files.pythonhosted.org/packages/48/d9/a13566ce8914746557b9e8637a5abe1caae86ed202b0fb072029626b8bb1/pyobjc-core-9.2.tar.gz"
    sha256 "d734b9291fec91ff4e3ae38b9c6839debf02b79c07314476e87da8e90b2c68c3"
  end

  resource "pyobjc-framework-Cocoa" do
    url "https://files.pythonhosted.org/packages/38/91/c54fdffda6d7cfad67ff617f19001163658d50bc72376d1584e691cf4895/pyobjc-framework-Cocoa-9.2.tar.gz"
    sha256 "efd78080872d8c8de6c2b97e0e4eac99d6203a5d1637aa135d071d464eb2db53"
  end

  resource "pyobjc-framework-CoreBluetooth" do
    url "https://files.pythonhosted.org/packages/f1/7a/239d5b1ac63056bb3e754c1f189f3e17051f3d2c3368c339d15b34f2ac48/pyobjc-framework-CoreBluetooth-9.2.tar.gz"
    sha256 "cb2481b1dfe211ae9ce55f36537dc8155dbf0dc8ff26e0bc2e13f7afb0a291d1"
  end

  resource "pyobjc-framework-libdispatch" do
    url "https://files.pythonhosted.org/packages/f1/73/455a8b92d3fc5b47b22e8055b6df19be96b2aa13715676e70a9cb7ed00b2/pyobjc-framework-libdispatch-9.2.tar.gz"
    sha256 "542e7f7c2b041939db5ed6f3119c1d67d73ec14a996278b92485f8513039c168"
  end

  resource "python-dotenv" do
    url "https://files.pythonhosted.org/packages/31/06/1ef763af20d0572c032fa22882cfbfb005fba6e7300715a37840858c919e/python-dotenv-1.0.0.tar.gz"
    sha256 "a8df96034aae6d2d50a4ebe8216326c61c3eb64836776504fcca410e5937a3ba"
  end

  resource "pyobjc-framework-Quartz" do
    url "https://files.pythonhosted.org/packages/49/52/a56bbd76bba721f49fa07d34ac962414b95eb49a9b941fe4d3761f3e6934/pyobjc-framework-Quartz-9.2.tar.gz"
    sha256 "f586183b9b9ef7f165f0444a7b714ed965d79f6e92617caaf869150dcfd5a72b"
  end

  def install
    virtualenv_install_with_resources
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
    system "#{bin}/brios", "--version"
  end
end
