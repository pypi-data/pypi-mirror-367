{
  lib,
  buildPythonPackage,
  fetchPypi,
  # build-system
  setuptools,
  #dep
  cirq-core,
  deprecation,
  h5py,
  networkx,
  numpy,
  requests,
  scipy,
  sympy,
  ...
}:
buildPythonPackage rec {
  pname = "openfermion";
  version = "1.7.1";
  format = "setuptools";

  src = fetchPypi {
    inherit pname version;
    hash = "sha256-cX9Llpof0d8k8RvUYrSF0xfyV73ZHO8yztI9J2zIP3A=";
  };

  build-system = [ setuptools ];

  patches = [
    ./remove_raise_1.7.1.patch
  ];

  dependencies = [
    cirq-core
    deprecation
    h5py
    networkx
    numpy
    requests
    scipy
    sympy
  ];

  nativeBuildInputs = [ ];
  buildInputs = [ ];

  doCheck = false;

  meta = { };
}
