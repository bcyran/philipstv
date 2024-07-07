{
  description = "A Nix-flake-based Python development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = nixpkgs.legacyPackages.${system};
    in
      with pkgs; {
        devShells.default = pkgs.mkShell {
          venvDir = ".venv";
          packages = with pkgs;
            [
              python312
              poetry
              pyright
            ]
            ++ (with pkgs.python312Packages; [
              pip
              venvShellHook
            ]);
        };
      });
}
