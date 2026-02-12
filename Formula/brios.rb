class Brios < Formula
  include Language::Python::Virtualenv

  desc "Bluetooth Reactive Intelligent Operator for Croissant Safety"
  homepage "https://github.com/Piero24/Bleissant"
  url "https://github.com/Piero24/Bleissant/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "REPLACE_WITH_SHA256_OF_TARBALL"
  license "MIT"

  depends_on "python@3.12"
  # depends_on "rust" if Bleak needs it for compilation, but usually binary wheels are available or it's pure python + corebluetooth

  def install
    virtualenv_install_with_resources
  end

  service do
    run [opt_bin/"brios"]
    keep_alive true
    log_path var/"log/brios.log"
    error_log_path var/"log/brios.log"
  end

  test do
    system "#{bin}/brios", "--version"
  end
end
