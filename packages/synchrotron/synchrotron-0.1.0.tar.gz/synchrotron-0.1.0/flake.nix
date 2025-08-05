{
  description = "Synchrotron - Graph-based live audio manipulation engine implemented in Python";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
  };

  outputs = inputs:
  let
    pkgs = inputs.nixpkgs.legacyPackages."x86_64-linux";
  in {
    devShells."x86_64-linux".default = import ./shell.nix { inherit pkgs; };
  };
}
