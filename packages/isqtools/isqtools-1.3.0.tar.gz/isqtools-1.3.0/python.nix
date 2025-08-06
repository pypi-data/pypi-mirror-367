{
  pkgs,
  pythonVersion,
  gitignoreSource,
  ...
}:
let
  pythonEnv = pkgs.${pythonVersion}.override {
    packageOverrides = self: super: {
      isqtools = self.callPackage ./. { inherit gitignoreSource; };
      openfermion = self.callPackage ./pkgs/openfermion.nix { };
    };
  };
in
pythonEnv
