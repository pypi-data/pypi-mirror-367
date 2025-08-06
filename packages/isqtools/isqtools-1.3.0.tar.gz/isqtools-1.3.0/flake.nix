{
  description = "isqtools";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-parts = {
      url = "github:hercules-ci/flake-parts";
      inputs.nixpkgs-lib.follows = "nixpkgs";
    };
    git-hooks = {
      url = "github:cachix/git-hooks.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    treefmt-nix = {
      url = "github:numtide/treefmt-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    gitignore = {
      url = "github:hercules-ci/gitignore.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    inputs@{ flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      imports = [
        inputs.git-hooks.flakeModule
        inputs.treefmt-nix.flakeModule
      ];
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "aarch64-darwin"
        "x86_64-darwin"
      ];
      perSystem =
        {
          config,
          self',
          inputs',
          pkgs,
          system,
          lib,
          ...
        }:
        let
          mkPythonEnv =
            pythonVersion:
            (import ./python.nix {
              inherit pkgs pythonVersion;
              inherit (inputs.gitignore.lib) gitignoreSource;
            });
          pyVersions = [
            "python3"
            "python310"
            "python311"
            "python312"
            "python313"
            "python314"
          ];
        in
        {

          legacyPackages = lib.genAttrs pyVersions (v: mkPythonEnv v);

          packages = {
            default = self'.legacyPackages.python3.pkgs.isqtools;
          }
          // builtins.listToAttrs (
            lib.forEach pyVersions (v: {
              name = "isqtools_${v}";
              value = self'.legacyPackages.${v}.pkgs.isqtools;
            })
          );

          devShells.default = pkgs.mkShell {
            inputsFrom = [
              config.pre-commit.devShell
              config.treefmt.build.devShell
            ];
            packages = [
              (self'.legacyPackages.python3.withPackages (
                p: with p; [
                  isqtools
                  openfermion

                  hatchling
                  autograd
                  requests
                  pytest
                  pytest-cov
                  pyscf
                  matplotlib
                  torch
                  torchvision
                  scikit-learn

                  sphinx
                  myst-parser
                  sphinx-autodoc-typehints
                  sphinx-copybutton
                  furo
                  nbsphinx
                  jupyter

                  build
                  twine
                ]
              ))
            ]
            ++ (with pkgs; [
              pandoc
              nbqa
              isort
              black
            ]);

            shellHook = ''
              export PATH="$HOME/opt/isqc/isqc-0.2.5:$PATH"
            '';
          };

          pre-commit = {
            check.enable = true;
            settings.hooks = {
              nixfmt-rfc-style.enable = true;
              ruff-format.enable = true;
              shfmt = {
                enable = true;
                args = [
                  "-i"
                  "2"
                ];
              };
              taplo.enable = true;
              prettier = {
                enable = true;
                excludes = [ "flake.lock" ];
              };
            };
          };

          treefmt = {
            projectRootFile = "flake.nix";
            programs = {
              nixfmt.enable = true;
              shfmt.enable = true;
              taplo.enable = true;
              ruff-format.enable = true;
              prettier.enable = true;
              just.enable = true;
            };
            settings.global = {
              excludes = [ ];
            };
          };
        };
      flake = { };
    };
}
