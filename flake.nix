{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    systems.url = "github:nix-systems/default";
  };

  outputs = {
    nixpkgs,
    systems,
    ...
  }: let
    forEachSystem = nixpkgs.lib.genAttrs (import systems);
  in {
    devShells =
      forEachSystem
      (system: let
        pkgs = nixpkgs.legacyPackages.${system};

        sharedLibs = with pkgs; [
          stdenv.cc.cc
          libxcrypt
          file
        ];
      in {
        default = pkgs.mkShell {
          packages = with pkgs; [
            python3
            uv
            pyright
          ];

          NIX_LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath sharedLibs;
          LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath sharedLibs;
          TOX_TESTENV_PASSENV = "NIX_LD_LIBRARY_PATH";

          shellHook = ''
            if [[ ! -d ".venv" ]]; then
              echo "No virtual environment found, creating..."
              uv venv --python ${pkgs.python3}/bin/python3 --prompt "$(basename $PWD)" .venv
            fi
            source .venv/bin/activate

            uv sync --all-extras
            echo "Virtual environment ready!"
          '';
        };
      });
  };
}
