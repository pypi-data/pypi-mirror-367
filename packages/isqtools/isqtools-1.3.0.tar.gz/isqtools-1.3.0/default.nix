{
  lib,
  buildPythonPackage,
  # build-system
  hatchling,
  # dependencies
  numpy,
  requests,
  autograd,
  # gitignore
  gitignoreSource,
  # docs
  sphinxHook,
  sphinx,
  myst-parser,
  furo,
  sphinx-copybutton,
  sphinx-autodoc-typehints,
  nbsphinx,
  ipykernel,
  pandoc,
  ...
}:
buildPythonPackage rec {
  pname = "isqtools";
  version = "1.3.0";
  src = gitignoreSource ./.;

  pyproject = true;

  outputs = [
    "out"
    "doc"
  ];

  build-system = [ hatchling ];
  dependencies = [
    numpy
    autograd
    requests
  ];

  nativeBuildInputs = [
    sphinxHook
    sphinx
    myst-parser
    furo
    sphinx-copybutton
    sphinx-autodoc-typehints
    nbsphinx
    ipykernel
    pandoc
  ];
  buildInputs = [ ];

  doCheck = false;

  meta = { };
}
