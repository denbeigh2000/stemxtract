{
  description = "A small webapp to extract stems from songs";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    systems.url = "github:nix-systems/default";
  };

  outputs = { self, nixpkgs, flake-utils, systems }:
    let
      inherit (flake-utils.lib) eachSystem;
    in
    eachSystem (import systems) (system:
      let
        pkgs = import nixpkgs { inherit system; };
        inherit (pkgs) mkShell;
      in
      {

        devShells.default = mkShell {
          packages = with pkgs; [ python311 yarn nodejs_21 ];
        };
      });
}
