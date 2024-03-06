{
  description = "A basic flake with a shell";
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-23.11";
    flake-utils.url = "github:numtide/flake-utils";
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        lib = pkgs.lib;
        p2nix = poetry2nix.lib.mkPoetry2Nix { inherit pkgs; };

        source = pkgs.copyPathToStore (lib.cleanSource ./.);
        python_with_gunicorn = pkgs.python3.withPackages(ps: [ ps.gunicorn ]);
      in
      {
        packages = rec {
          myapp = p2nix.mkPoetryApplication {
            projectDir = self;
            overrides = p2nix.overrides.withDefaults (self: super: {
              paho-mqtt = super.paho-mqtt.overridePythonAttrs (old: {
                buildInputs = (old.buildInputs or []) ++ [ super.hatchling ];
              });
            });
          };
          default = self.packages.${system}.myapp;

          poetryenv = p2nix.mkPoetryEnv {
            projectDir = self;
            overrides = p2nix.overrides.withDefaults (self: super: {
              paho-mqtt = super.paho-mqtt.overridePythonAttrs (old: {
                buildInputs = (old.buildInputs or []) ++ [ super.hatchling ];
              });
            });
          };

          dockerImage = pkgs.dockerTools.buildLayeredImage {
            name = "cot_webserver_prod";
            tag = "latest";
            contents = [ source poetryenv pkgs.bash ];
            #config = {
            #  Cmd = [ "${pkgs.bash} -c ${poetryenv}/bin/gunicorn --workers=4 src.app:main" ];
            #};
          };
        };

        devShells.default = pkgs.mkShell {
          inputsFrom = [ self.packages.${system}.default ];
          packages = [ pkgs.poetry ];
        };
      });
}
